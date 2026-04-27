# NCCLTester

A small repository for smoke-testing NCCL distributed training on a single node with multiple NVIDIA GPUs. The included [nccl_check.py](nccl_check.py) spawns one PyTorch process per visible GPU, joins them into an NCCL `ProcessGroup`, runs an `all_reduce`, and prints whether the result matches the expected sum.

This README documents the current state of the repository, including the environment fixes that were needed before the test could even be attempted, and an open investigation into a hang seen during the first end-to-end run.

---

## Environment

| Component | Version |
|---|---|
| OS | Ubuntu 24.04 (Noble) inside a `--privileged` Docker container |
| GPUs | 2 x NVIDIA H200 NVL (143 GB each) |
| Driver | 580.126.09 (max CUDA 13.0) |
| CUDA toolkit | 13.0.96-1 (`cuda-cudart-13-0`) |
| PyTorch | 2.11.0+cu130 |
| PyTorch's bundled NCCL | 2.28.9 |
| System NCCL (`libnccl2`, `libnccl-dev`) | 2.28.9-1+cuda13.0 (held) |

The system NCCL was deliberately aligned with PyTorch's bundled NCCL so that any non-PyTorch consumers of `libnccl.so` see the same version PyTorch is already running with. PyTorch's `torch.distributed` continues to use its own bundled NCCL regardless of the system package.

---

## Files

| File | Purpose |
|---|---|
| [nccl_check.py](nccl_check.py) | Distributed all-reduce smoke test using PyTorch + NCCL. Spawns one worker per CUDA device. |
| [nccl_check_bash.sh](nccl_check_bash.sh) | Convenience launcher that sets `NCCL_DEBUG=INFO` and runs the test. |
| [CLAUDE.md](CLAUDE.md) | Project conventions for Claude Code sessions (rule priority, MIT code style, debug file management, ToDo workflow, linting, etc.). |
| [ToDo.md](ToDo.md) | Append-only task log. Each entry corresponds to a GitHub issue. |
| [ruff.toml](ruff.toml) | Linter config: `line-length = 80`, `indent-width = 4`. |
| [.claude/](.claude/) | Hook scripts and `settings.json` that automate the conventions in `CLAUDE.md`. |

---

## Progress so far

| # | Status | Title | Notes |
|---|---|---|---|
| [#1](https://github.com/coport-uni/NCCLTester/issues/1) | Closed | Fix APT "Conflicting values set for option Signed-By" for NVIDIA CUDA repo | Removed unsigned duplicate `cuda.list` from `/etc/apt/sources.list.d/`. APT could not read any sources before the fix, blocking all package installs. |
| [#2](https://github.com/coport-uni/NCCLTester/issues/2) | Closed | Upgrade `libnccl2` / `libnccl-dev` to `2.28.9-1+cuda13.0` | Aligned the system NCCL with PyTorch's bundled NCCL (also 2.28.9). System packages are pinned (`apt-mark hold`). |
| [#3](https://github.com/coport-uni/NCCLTester/issues/3) | Open | Debug `nccl_check.py` hang on 2x H200 NVL | First end-to-end run hangs with both worker Python processes pegged at 99% CPU and 100% GPU-Util, no stdout for 4+ minutes. Investigation paused; see "Known issue" below. |

---

## Known issue: `nccl_check.py` hangs

Running [nccl_check_bash.sh](nccl_check_bash.sh) (`NCCL_DEBUG=INFO python3 nccl_check.py`) reproduces the following pattern:

- Both worker Python processes (one per GPU) consume CPU at 99% and accumulate minutes of CPU time.
- `nvidia-smi` shows ~1 GB allocated and 100% GPU-Util on each card — the workers reach CUDA initialization.
- No stdout is produced for the duration of the run.
- The first attempt to capture output via `... | tee /tmp/nccl.log` produced an empty log, suggesting Python's stdout in the spawned workers is fully buffered. Even setting `PYTHONUNBUFFERED=1` and `NCCL_DEBUG_FILE=/tmp/nccl_%h.%p.log` did not produce per-process log files within the bounded run window.

Notably, this behaviour is independent of the system NCCL upgrade in #2 — PyTorch uses its own bundled NCCL.

The investigation is tracked in [#3](https://github.com/coport-uni/NCCLTester/issues/3) and will resume in a follow-up session. Likely directions:

- Run a non-distributed CUDA sanity check on each GPU first (`torch.cuda.is_available()`, simple kernel) to confirm CUDA itself is healthy.
- Consider container `--shm-size` (separate from `--privileged`); PyTorch `mp.spawn` uses shared memory for IPC.
- Try `NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1 NCCL_SOCKET_IFNAME=lo` to rule out IB/RoCE auto-detection or NIC-binding hangs.
- Switch the launcher from `mp.spawn` to `torchrun --nproc_per_node=2` to remove one layer of indirection.

---

## How to reproduce

```bash
# 1. Verify the apt sources fix is in place
ls /etc/apt/sources.list.d/
# expected: cuda-ubuntu2404-x86_64.list, ubuntu.sources  (no cuda.list)

# 2. Verify NCCL packages
dpkg -l | grep -E '^hi\s+(libnccl2|libnccl-dev)'
# expected: both at 2.28.9-1+cuda13.0, status hi

# 3. Run the smoke test
bash nccl_check_bash.sh
```

Expect it to hang as described under "Known issue" until #3 is resolved.

---

## Conventions

This repo follows the workflow defined in [CLAUDE.md](CLAUDE.md):

- Every task gets a [ToDo.md](ToDo.md) entry **and** a GitHub issue before work begins.
- Every commit references the issue it closes.
- Python is linted with `ruff` against [ruff.toml](ruff.toml) (80 columns, 4-space indent).
- Debug / exploratory scripts go under `claude_test/` (when present), not `tests/`.
- Hooks in [.claude/](.claude/) automate the parts of the convention that can be checked mechanically.
