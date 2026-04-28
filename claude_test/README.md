# claude_test/

Debug and exploratory scripts. Per [CLAUDE.md §3](../CLAUDE.md), this is
the scratch area for one-off diagnostics. Anything later promoted into
`tests/` must conform fully to the production conventions.

## Index

| File                       | Purpose                                                                 | What was learned                                                                                                              |
|----------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `check_cuda_p2p.py`        | Probe `torch.cuda.can_device_access_peer` between every GPU pair.       | GPU0 ↔ GPU1 reports `True` both ways. CUDA-level P2P over PCIe Gen5 x16 is permitted (no NVLink bridge installed).            |
| `check_nccl_devfix.py`     | Try `cuda.set_device` *before* `init_process_group` to dodge the P2P hang in `nccl_check.py`. | Did **not** fix it — `EXIT=124` (timeout) just like the original. The P2P/CUMEM hang sits deeper than rank-to-device ordering. |
| `logs/cuda_p2p.log`        | Output of `check_cuda_p2p.py`.                                          | -                                                                                                                             |
| `logs/nccl_init.log`       | Default `nccl_check.py` run with `NCCL_DEBUG=INIT,NET,P2P,SHM,GRAPH`.   | NCCL selects `P2P/CUMEM` for all 4 channels in each direction; init completes in ~0.8 s but `all_reduce` hangs (timeout 90 s). |
| `logs/nccl_p2p_disabled.log` | Same script with `NCCL_P2P_DISABLE=1`.                                | Falls back to `SHM/direct/direct`; `all_reduce` completes successfully, result = 3.0 (expected 3).                            |
| `logs/nccl_net_only.log`   | Same script with `NCCL_P2P_DISABLE=1 NCCL_SHM_DISABLE=1`.              | Falls back to `NET/Socket/0` over `eth0` (172.17.0.2); `all_reduce` completes successfully, result = 3.0.                     |
| `logs/nccl_devfix.log`     | Output of `check_nccl_devfix.py`.                                       | Confirms the `set_device`-first fix does not resolve the P2P hang.                                                            |
| `logs/diagnose_run.log`    | Stdout of `python3 nccl_diagnose.py --timeout 90` on this container.    | Verification artifact for issue #6: SHM and NET PASS, default and accelerate TIMEOUT under `P2P/CUMEM` (matches #5 findings). |
| `logs/diagnose_report.json`| `--report` JSON of the same run.                                        | Per-test status, exit code, transport, and a 20-line log tail. Useful for diffing across environments.                        |
