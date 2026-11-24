# Runbook: ImagePullBackOff

## Symptoms
Pod is stuck in `ImagePullBackOff` or `ErrImagePull`; new ReplicaSet may not become ready.

## Investigation
```bash
kubectl get pods -n sre-lab
kubectl describe pod <pod-name> -n sre-lab
kubectl get events -n sre-lab --sort-by=.lastTimestamp
```

Check:
- Image name and tag spelling
- Whether image exists in local cluster or registry
- `imagePullPolicy`
- Registry credentials / imagePullSecrets (for private registries)
- Node network and registry availability

## Recovery in this lab
```bash
kubectl set image deployment/orders-api api=sre-orders-api:1.0 -n sre-lab
kubectl rollout status deployment/orders-api -n sre-lab
```

## Validate
```bash
kubectl get pods -n sre-lab
kubectl get endpoints orders-api -n sre-lab
curl http://localhost:8080/health
```
