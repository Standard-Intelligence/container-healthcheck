# Healthcheck

## Docker Build

```bash
docker buildx build --platform linux/amd64 -t ghcr.io/standard-intelligence/healthcheck:latest --push -f Dockerfile .
```

## Kubernetes Deployment

```bash
kubectl create configmap healthcheck-script --from-file=min.py && \
kubectl apply -f min.yaml && \
kubectl wait --for=condition=Ready pod -l job-name=healthcheck,batch.kubernetes.io/job-completion-index="0" --timeout=300s && \
kubectl logs -f -l job-name=healthcheck,batch.kubernetes.io/job-completion-index="0"
```