import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parallel import DistributedDataParallel as DDP

rank = int(os.environ['RANK'])
world_size = int(os.environ['WORLD_SIZE'])
local_rank = int(os.environ['LOCAL_RANK'])

print(f'Rank {rank}/{world_size}, Local rank {local_rank}')

torch.distributed.init_process_group(backend='nccl')

device = f'cuda:{local_rank}'
torch.cuda.set_device(device)
print(f'Initialized on device {device}')

test_tensor = torch.randn(10, device=device)
print(f'Mean before all_reduce: {test_tensor.mean().item()}')
torch.distributed.all_reduce(test_tensor)
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

print('Starting training...')
inputs = torch.randn(batch_size, input_dim, device=device)
targets = torch.randn(batch_size, input_dim, device=device)

for step in range(1000):
    optimizer.zero_grad()
    
    with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
        loss = F.mse_loss(model(inputs), targets)
    
    loss.backward()
    optimizer.step()
    
    if step % 10 == 0 and local_rank == 0:
        print(f'Step {step}, Loss: {loss.item():.4f}')

print('Training complete')
torch.distributed.destroy_process_group()
