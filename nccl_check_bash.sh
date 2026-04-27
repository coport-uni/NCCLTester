NCCL_DEBUG=INFO
echo 50000 51000 > /proc/sys/net/ipv4/ip_local_port_range
python3 nccl_check.py