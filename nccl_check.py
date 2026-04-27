# nccl_check.py
import os
import torch
import torch.distributed as dist
import torch.multiprocessing as mp

def worker(rank, world_size):
    os.environ["MASTER_ADDR"] = "127.0.0.1"
    os.environ["MASTER_PORT"] = "29500"
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

    x = torch.ones(1, device=f"cuda:{rank}") * (rank + 1)
    dist.all_reduce(x, op=dist.ReduceOp.SUM)
    print(f"[rank {rank}] all_reduce 결과: {x.item()}  (기대값: {sum(range(1, world_size+1))})")

    dist.destroy_process_group()

if __name__ == "__main__":
    world_size = torch.cuda.device_count()
    mp.spawn(worker, args=(world_size,), nprocs=world_size)