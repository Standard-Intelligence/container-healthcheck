import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parallel import DistributedDataParallel as DDP
import time

rank = int(os.environ['RANK'])
world_size = int(os.environ['WORLD_SIZE'])
local_rank = int(os.environ['LOCAL_RANK'])

print(f'Rank {rank}/{world_size}, Local rank {local_rank}')

torch.distributed.init_process_group(backend='nccl')

device = f'cuda:{local_rank}'
torch.cuda.set_device(device)

if rank == 0:
    print(f'Initialized on device {device}')

test_tensor = torch.randn(10, device=device)
if rank == 0:
    print(f'Mean before all_reduce: {test_tensor.mean().item()}')
torch.distributed.all_reduce(test_tensor)
if rank == 0:
    print(f'Mean after all_reduce: {test_tensor.mean().item()}')

input_dim = 32
model_dim = int(2**18)
batch_size = int(2**15)

model = nn.Sequential(
    nn.Linear(input_dim, model_dim, bias=False),
    nn.ReLU(),
    nn.Linear(model_dim, input_dim, bias=False)
)
model = model.to(device)
model = torch.compile(model)
model = DDP(model, device_ids=[local_rank])

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

if rank == 0:
    print('Starting training...')
inputs = torch.randn(batch_size, input_dim, device=device)
targets = torch.randn(batch_size, input_dim, device=device)

torch.cuda.synchronize()
start_time = time.perf_counter()
step_start = start_time

for step in range(1000):
    optimizer.zero_grad()
    
    with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
        loss = F.mse_loss(model(inputs), targets)
    
    loss.backward()
    optimizer.step()
    
    if step % 10 == 0 and step > 0:
        torch.cuda.synchronize()
        step_end = time.perf_counter()
        
        if rank == 0:
            time_per_step = (step_end - step_start) / 10
            samples_per_second = batch_size * world_size / time_per_step
            
            print(f'Step {step}, Loss: {loss.item():.4f}, '
                  f'Time/step: {time_per_step*1000:.1f}ms, '
                  f'Throughput: {samples_per_second:.0f} samples/s')
        
        step_start = step_end
    
torch.distributed.destroy_process_group()
