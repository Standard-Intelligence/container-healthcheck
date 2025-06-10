# Healthcheck

## Docker Build

```bash
docker buildx build --platform linux/amd64 -t ghcr.io/{YOUR_GITHUB_NAME}/{YOUR_PACKAGE_NAME}:latest --push -f Dockerfile .
```

## Kubernetes Deployment

```bash
kubectl create configmap healthcheck-script --from-file=min.py && \
kubectl apply -f min.yaml && \
kubectl wait --for=condition=Ready pod -l job-name=healthcheck,batch.kubernetes.io/job-completion-index="0" --timeout=300s && \
kubectl logs -f -l job-name=healthcheck,batch.kubernetes.io/job-completion-index="0"
```

To run again, `kubectl delete configmap healthcheck-script && kubectl delete -f min.yaml`


## Expected Output

```bash
configmap/healthcheck-script created
service/healthcheck-svc created
job.batch/healthcheck created
pod/healthcheck-0-vpgvt condition met
+ sleep 10
+ torchrun --nnodes 2 --nproc_per_node 8 --rdzv-backend c10d --rdzv-endpoint healthcheck-0.healthcheck-svc:29500 /scripts/min.py
Rank 7/16, Local rank 7
Rank 0/16, Local rank 0
Rank 1/16, Local rank 1
Rank 5/16, Local rank 5
Rank 3/16, Local rank 3
Rank 6/16, Local rank 6
Rank 4/16, Local rank 4
Rank 2/16, Local rank 2
Initialized on device cuda:0
Mean before all_reduce: -0.24806562066078186
Mean after all_reduce: -0.6414656043052673
Starting training...
Step 10, Loss: 7.1843, Time/step: 657.6ms, Throughput: 797259 samples/s
Step 20, Loss: 2.6501, Time/step: 60.3ms, Throughput: 8690747 samples/s
Step 30, Loss: 1.1404, Time/step: 60.4ms, Throughput: 8684555 samples/s
Step 40, Loss: 1.1079, Time/step: 60.4ms, Throughput: 8685017 samples/s
Step 50, Loss: 1.0493, Time/step: 60.4ms, Throughput: 8682423 samples/s
Step 60, Loss: 1.0187, Time/step: 60.4ms, Throughput: 8686450 samples/s
Step 70, Loss: 1.0074, Time/step: 60.4ms, Throughput: 8686772 samples/s
Step 80, Loss: 1.0063, Time/step: 60.3ms, Throughput: 8688462 samples/s
Step 90, Loss: 1.0051, Time/step: 60.3ms, Throughput: 8689386 samples/s
Step 100, Loss: 1.0030, Time/step: 60.3ms, Throughput: 8687918 samples/s
Step 110, Loss: 1.0023, Time/step: 60.3ms, Throughput: 8693065 samples/s
Step 120, Loss: 1.0017, Time/step: 60.3ms, Throughput: 8688557 samples/s
Step 130, Loss: 1.0013, Time/step: 60.3ms, Throughput: 8690453 samples/s
Step 140, Loss: 1.0009, Time/step: 60.3ms, Throughput: 8689276 samples/s
Step 150, Loss: 1.0006, Time/step: 60.3ms, Throughput: 8690747 samples/s
Step 160, Loss: 1.0003, Time/step: 60.3ms, Throughput: 8690539 samples/s
Step 170, Loss: 1.0000, Time/step: 60.3ms, Throughput: 8689947 samples/s
...
```