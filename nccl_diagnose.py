"""Portable NCCL transport + Accelerate multi-GPU diagnostic.

Probes which NCCL transports (SHM, P2P, NET) work end-to-end and whether
HuggingFace Accelerate succeeds at multi-GPU all_reduce on the current
machine. Each path runs in its own subprocess with a bounded timeout so
a hang in one transport does not stall the rest of the diagnosis.

Usage:
    python3 nccl_diagnose.py [--timeout SECS] [--report PATH]

The internal worker modes are entered automatically by the spawned
subprocesses and should not be invoked by hand:
    python3 nccl_diagnose.py worker-torch
    python3 nccl_diagnose.py worker-accelerate

Required: PyTorch with NCCL backend.
Optional: huggingface accelerate. The accelerate test reports SKIPPED
if accelerate is not importable.
"""

import argparse
import glob
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Marker that workers print on success. The launcher counts how many
# times this marker appears in subprocess stdout to decide PASS/FAIL.
SUCCESS_MARKER = "DIAG_OK"

# Tolerance for floating-point equality of all_reduce output.
REDUCE_TOLERANCE = 1e-6

# One TCP port per test so back-to-back launches do not collide on
# TIME_WAIT in the kernel's loopback stack.
WORKER_PORT = {
    "default": "29500",
    "shm_only": "29501",
    "net_only": "29502",
    "accelerate": "29503",
}

# Patterns NCCL emits in NCCL_DEBUG=INFO logs to announce the chosen
# transport for each channel. Used to label test results.
TRANSPORT_PATTERNS = {
    "P2P/CUMEM": re.compile(r"via P2P/CUMEM"),
    "P2P/IPC": re.compile(r"via P2P/IPC"),
    "SHM/direct": re.compile(r"via SHM/"),
    "NET/Socket": re.compile(r"via NET/Socket"),
    "NET/IB": re.compile(r"via NET/IB"),
}


def static_probe():
    """Collect static facts about the host without invoking NCCL.

    Returns:
        dict with torch/NCCL versions, GPU listing, CUDA P2P matrix,
        /dev/shm size and mount options, NIC interfaces, and whether
        InfiniBand devices are exposed by the kernel.
    """
    info = {}
    try:
        import torch

        info["torch_version"] = torch.__version__
        info["cuda_available"] = bool(torch.cuda.is_available())
        info["device_count"] = int(torch.cuda.device_count())
        info["devices"] = [
            torch.cuda.get_device_name(i)
            for i in range(torch.cuda.device_count())
        ]
        if torch.cuda.is_available():
            info["nccl_version"] = ".".join(
                str(v) for v in torch.cuda.nccl.version()
            )
        else:
            info["nccl_version"] = None
        matrix = {}
        for i in range(torch.cuda.device_count()):
            row = {}
            for j in range(torch.cuda.device_count()):
                if i == j:
                    row[str(j)] = None
                else:
                    row[str(j)] = bool(torch.cuda.can_device_access_peer(i, j))
            matrix[str(i)] = row
        info["p2p_matrix"] = matrix
    except Exception as exc:
        info["torch_error"] = repr(exc)

    shm = Path("/dev/shm")
    if shm.exists():
        try:
            st = os.statvfs(shm)
            info["shm_total_gb"] = round(st.f_blocks * st.f_frsize / 1e9, 2)
            info["shm_free_gb"] = round(st.f_bavail * st.f_frsize / 1e9, 2)
        except OSError:
            pass
        try:
            with open("/proc/self/mounts") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 4 and parts[1] == "/dev/shm":
                        info["shm_mount_options"] = parts[3]
                        break
        except OSError:
            pass

    net_dir = Path("/sys/class/net")
    if net_dir.exists():
        info["net_interfaces"] = sorted(p.name for p in net_dir.iterdir())
    ib_dir = Path("/sys/class/infiniband")
    info["infiniband"] = ib_dir.exists() and any(ib_dir.iterdir())

    return info


def _torch_run(rank, world_size):
    """All_reduce worker body. Run inside torch.multiprocessing.spawn."""
    import torch
    import torch.distributed as dist

    torch.cuda.set_device(rank)
    os.environ.setdefault("MASTER_ADDR", "127.0.0.1")
    os.environ.setdefault("MASTER_PORT", "29500")
    dist.init_process_group(
        "nccl",
        rank=rank,
        world_size=world_size,
        device_id=torch.device(f"cuda:{rank}"),
    )
    x = torch.ones(1, device=f"cuda:{rank}") * (rank + 1)
    dist.all_reduce(x, op=dist.ReduceOp.SUM)
    expected = sum(range(1, world_size + 1))
    if abs(x.item() - expected) < REDUCE_TOLERANCE:
        print(f"{SUCCESS_MARKER} rank={rank} value={x.item()}")
    dist.destroy_process_group()


def torch_worker():
    """Entry point for the `worker-torch` subprocess mode."""
    import torch
    import torch.multiprocessing as mp

    n = torch.cuda.device_count()
    if n < 2:
        print(f"DIAG_SKIP need >= 2 GPUs, found {n}")
        return
    mp.spawn(_torch_run, args=(n,), nprocs=n)


def accelerate_worker():
    """Entry point invoked by `accelerate launch` for one rank.

    Each rank reaches this function as its own freshly-spawned Python
    process, so unlike notebook_launcher (which forks) it is safe to
    touch CUDA from this point forward.
    """
    import torch
    from accelerate import Accelerator

    accelerator = Accelerator()
    rank = accelerator.process_index
    world = accelerator.num_processes
    device = accelerator.device
    x = torch.ones(1, device=device) * (rank + 1)
    reduced = accelerator.reduce(x, reduction="sum")
    expected = sum(range(1, world + 1))
    if abs(reduced.item() - expected) < REDUCE_TOLERANCE:
        print(f"{SUCCESS_MARKER} rank={rank} value={reduced.item()}")


def _parse_transport(log):
    """Return a comma-joined list of NCCL transport tags found in log."""
    found = [
        name for name, pat in TRANSPORT_PATTERNS.items() if pat.search(log)
    ]
    return ",".join(found) if found else "unknown"


def _classify(stdout, stderr, exit_code, timed_out):
    """Map (output, exit_code, timeout) into a status label.

    Return one of: PASS, FAIL, TIMEOUT, SKIPPED.
    """
    del stderr  # not consulted; subprocess output uses stdout markers
    if "DIAG_SKIP" in stdout:
        return "SKIPPED"
    ok_count = stdout.count(SUCCESS_MARKER)
    if timed_out:
        return "TIMEOUT"
    if exit_code == 0 and ok_count >= 2:
        return "PASS"
    return "FAIL"


def _run_subprocess(cmd, env, timeout):
    """Run `cmd` under `env` with a bounded timeout.

    Uses a fresh session so that on timeout we can SIGKILL the whole
    process group, including any grandchildren spawned by mp.spawn or
    `accelerate launch`. Output goes to tempfiles rather than pipes —
    if we used PIPE, grandchildren would inherit the parent's stdout
    fd and proc.communicate() would block on those open fds even after
    the immediate child is reaped.
    """
    started = time.time()
    timed_out = False
    out_buf = tempfile.TemporaryFile(mode="w+")
    err_buf = tempfile.TemporaryFile(mode="w+")
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=out_buf,
        stderr=err_buf,
        text=True,
        start_new_session=True,
    )
    try:
        exit_code = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            exit_code = proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            exit_code = -1
        timed_out = True
    elapsed = round(time.time() - started, 1)
    out_buf.seek(0)
    err_buf.seek(0)
    stdout = out_buf.read()
    stderr = err_buf.read()
    out_buf.close()
    err_buf.close()
    if timed_out and exit_code != -1:
        # `wait` succeeded after the kill — preserve the timeout label.
        exit_code = -1
    return stdout, stderr, exit_code, timed_out, elapsed


def _read_nccl_debug_files(prefix_dir):
    """Concatenate every NCCL debug file in `prefix_dir` (one per PID)."""
    chunks = []
    for path in sorted(glob.glob(str(Path(prefix_dir) / "nccl.*.log"))):
        try:
            chunks.append(Path(path).read_text(errors="replace"))
        except OSError:
            continue
    return "\n".join(chunks)


def _detect_device_count_via_subprocess():
    """Count CUDA devices in a throwaway subprocess.

    Calling torch.cuda.device_count() in our own process leaks a CUDA
    initialization that breaks fork-based launchers downstream, so we
    delegate to a child whose CUDA state we discard.
    """
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "import torch; print(torch.cuda.device_count())",
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    try:
        return int(probe.stdout.strip())
    except ValueError:
        return 0


def run_torch_test(mode, timeout):
    """Run the torch.distributed worker as a subprocess in `mode`.

    Args:
        mode: one of "default", "shm_only", "net_only".
        timeout: seconds before the subprocess group is killed.

    Returns:
        Result dict with mode, status, transport, elapsed_sec, log_tail.
    """
    log_dir = tempfile.mkdtemp(prefix=f"nccl_diag_{mode}_")
    env = os.environ.copy()
    env["NCCL_DEBUG"] = "INFO"
    env["NCCL_DEBUG_SUBSYS"] = "INIT,NET,P2P,SHM"
    env["NCCL_DEBUG_FILE"] = str(Path(log_dir) / "nccl.%p.log")
    env["MASTER_PORT"] = WORKER_PORT[mode]
    if mode == "shm_only":
        env["NCCL_P2P_DISABLE"] = "1"
    elif mode == "net_only":
        env["NCCL_P2P_DISABLE"] = "1"
        env["NCCL_SHM_DISABLE"] = "1"

    cmd = [sys.executable, str(Path(__file__).resolve()), "worker-torch"]
    stdout, stderr, exit_code, timed_out, elapsed = _run_subprocess(
        cmd, env, timeout
    )
    nccl_log = _read_nccl_debug_files(log_dir)
    shutil.rmtree(log_dir, ignore_errors=True)
    combined = stdout + stderr + nccl_log
    return {
        "mode": mode,
        "status": _classify(stdout, stderr, exit_code, timed_out),
        "transport": _parse_transport(combined),
        "elapsed_sec": elapsed,
        "exit_code": exit_code,
        "log_tail": combined.splitlines()[-20:],
    }


def run_accelerate_test(timeout):
    """Run the accelerate worker via `accelerate launch`.

    `accelerate launch` spawns each rank as its own Python interpreter
    (subprocess + exec, not fork), so initializing CUDA inside the rank
    is safe — unlike `notebook_launcher`, which forks.
    """
    if shutil.which("accelerate") is None:
        return {
            "mode": "accelerate",
            "status": "SKIPPED",
            "transport": "n/a",
            "elapsed_sec": 0.0,
            "exit_code": 0,
            "log_tail": ["accelerate CLI not installed"],
        }
    n = _detect_device_count_via_subprocess()
    if n < 2:
        return {
            "mode": "accelerate",
            "status": "SKIPPED",
            "transport": "n/a",
            "elapsed_sec": 0.0,
            "exit_code": 0,
            "log_tail": [f"need >= 2 GPUs, found {n}"],
        }
    log_dir = tempfile.mkdtemp(prefix="nccl_diag_accelerate_")
    env = os.environ.copy()
    env["NCCL_DEBUG"] = "INFO"
    env["NCCL_DEBUG_SUBSYS"] = "INIT,NET,P2P,SHM"
    env["NCCL_DEBUG_FILE"] = str(Path(log_dir) / "nccl.%p.log")

    cmd = [
        "accelerate",
        "launch",
        "--num_processes",
        str(n),
        "--num_machines",
        "1",
        "--main_process_port",
        WORKER_PORT["accelerate"],
        str(Path(__file__).resolve()),
        "worker-accelerate",
    ]
    stdout, stderr, exit_code, timed_out, elapsed = _run_subprocess(
        cmd, env, timeout
    )
    nccl_log = _read_nccl_debug_files(log_dir)
    shutil.rmtree(log_dir, ignore_errors=True)
    combined = stdout + stderr + nccl_log
    return {
        "mode": "accelerate",
        "status": _classify(stdout, stderr, exit_code, timed_out),
        "transport": _parse_transport(combined),
        "elapsed_sec": elapsed,
        "exit_code": exit_code,
        "log_tail": combined.splitlines()[-20:],
    }


def render_summary(static, results):
    """Build the human-readable stdout summary."""
    lines = []
    lines.append("=" * 72)
    lines.append("NCCL transport + Accelerate diagnosis")
    lines.append("=" * 72)
    lines.append("")
    lines.append("Environment:")
    lines.append(f"  torch                = {static.get('torch_version')}")
    lines.append(f"  NCCL                 = {static.get('nccl_version')}")
    lines.append(f"  GPU count            = {static.get('device_count')}")
    for idx, name in enumerate(static.get("devices") or []):
        lines.append(f"    [{idx}] {name}")
    lines.append(f"  /dev/shm total       = {static.get('shm_total_gb')} GB")
    lines.append(f"  /dev/shm mount opts  = {static.get('shm_mount_options')}")
    lines.append(f"  NIC interfaces       = {static.get('net_interfaces')}")
    lines.append(f"  InfiniBand present   = {static.get('infiniband')}")
    matrix = static.get("p2p_matrix") or {}
    if matrix:
        lines.append("  CUDA P2P matrix:")
        for src, row in matrix.items():
            cells = [
                f"{dst}={val}" for dst, val in row.items() if val is not None
            ]
            lines.append(f"    GPU {src} -> {{{', '.join(cells)}}}")
    lines.append("")
    lines.append("Transport tests:")
    header = f"  {'mode':<12} {'status':<10} {'transport':<28} {'time':>8}"
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))
    for r in results:
        lines.append(
            f"  {r['mode']:<12} {r['status']:<10} "
            f"{r['transport']:<28} {r['elapsed_sec']:>6}s"
        )
    lines.append("")
    return "\n".join(lines)


def run_full(timeout, report_path):
    """Top-level orchestrator: static probe + 4 subprocess tests."""
    static = static_probe()
    results = []
    if (static.get("device_count") or 0) >= 2:
        for mode in ("default", "shm_only", "net_only"):
            results.append(run_torch_test(mode, timeout))
        results.append(run_accelerate_test(timeout))
    summary = render_summary(static, results)
    print(summary)
    if report_path:
        Path(report_path).write_text(
            json.dumps(
                {"static": static, "results": results},
                indent=2,
                default=str,
            )
        )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="full",
        choices=["full", "worker-torch", "worker-accelerate"],
        help="entry mode (default: full)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=90,
        help="per-test timeout in seconds (default: 90)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="optional path to write a JSON report",
    )
    args = parser.parse_args()

    if args.mode == "worker-torch":
        torch_worker()
    elif args.mode == "worker-accelerate":
        accelerate_worker()
    else:
        run_full(args.timeout, args.report)


if __name__ == "__main__":
    main()
