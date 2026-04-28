"""Quick CUDA P2P probe between GPU pairs (no NCCL)."""

import torch

n = torch.cuda.device_count()
print(f"device_count={n}")
for i in range(n):
    print(f"  cuda:{i} = {torch.cuda.get_device_name(i)}")

print("can_device_access_peer matrix:")
for i in range(n):
    row = []
    for j in range(n):
        if i == j:
            row.append("  -  ")
        else:
            ok = torch.cuda.can_device_access_peer(i, j)
            row.append(" yes " if ok else " no  ")
    print(f"  from cuda:{i} -> {row}")
