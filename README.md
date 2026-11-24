# Kubernetes SRE Incident Response Lab

A hands-on Kubernetes project for practicing deployment, observability, autoscaling, access control, and incident troubleshooting.

## What you will build

- A Python REST API container image
- Kubernetes Namespace, Deployment, Service, ConfigMap, Secret example, ServiceAccount and RBAC
- Startup, readiness and liveness probes
- CPU/memory requests and limits
- Horizontal Pod Autoscaler (HPA)
- PodDisruptionBudget (PDB)
- NetworkPolicy example
- Prometheus/Grafana monitoring using `kube-prometheus-stack`
- Prometheus alert rules
- Failure-injection scripts and incident runbooks

This is a local training lab. Do not use the sample credentials or manifests as-is in production.

## Prerequisites

- Docker
- `kubectl`
- Minikube or Kind
- Helm 3
- `hey` (optional, for load testing) or use the included Python load generator

## Option A: Run with Minikube

```bash
minikube start --cpus=4 --memory=6g
minikube addons enable metrics-server
```

Build the image inside Minikube's Docker environment:

```bash
eval $(minikube docker-env)       # macOS/Linux shell
docker build -t sre-orders-api:1.0 ./app
```

For Windows PowerShell, use Minikube's image build command instead:

```powershell
minikube image build -t sre-orders-api:1.0 ./app
```

Apply the application resources:

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/
kubectl -n sre-lab get pods,svc,hpa,pdb
```

The `kubectl apply -f k8s/` command can also apply the namespace file; applying it twice is harmless.

Access the app:

```bash
kubectl -n sre-lab port-forward svc/orders-api 8080:80
```

In another terminal:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/ready
curl http://localhost:8080/api/orders
curl http://localhost:8080/metrics
```

## Option B: Run with Kind

```bash
kind create cluster --name sre-lab
docker build -t sre-orders-api:1.0 ./app
kind load docker-image sre-orders-api:1.0 --name sre-lab
kubectl apply -f k8s/
```

Install metrics-server for HPA (follow the official metrics-server instructions for your cluster). Then verify:

```bash
kubectl -n sre-lab get hpa
kubectl top pods -n sre-lab
```

## Install Prometheus and Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f monitoring/values.yaml
```

Apply the app ServiceMonitor and alert rules:

```bash
kubectl apply -f monitoring/servicemonitor.yaml
kubectl apply -f monitoring/prometheusrule.yaml
```

Port-forward Grafana:

```bash
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```

Get the generated Grafana admin password:

```bash
kubectl -n monitoring get secret monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d; echo
```

Username is `admin`. Open http://localhost:3000. Prometheus is usually available with:

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

## Failure and troubleshooting exercises

### 1. Simulate a bad rollout

```bash
kubectl -n sre-lab set image deployment/orders-api api=nginx:does-not-exist
kubectl -n sre-lab rollout status deployment/orders-api
kubectl -n sre-lab get pods
kubectl -n sre-lab describe pod <pod-name>
kubectl -n sre-lab rollout undo deployment/orders-api
```

Expected learning: ImagePullBackOff, rollout status, events, rollback.

### 2. Simulate a crashing application

```bash
kubectl -n sre-lab exec deploy/orders-api -- sh -c 'kill 1'
kubectl -n sre-lab get pods -w
kubectl -n sre-lab logs deploy/orders-api --previous
```

Expected learning: restart behavior, liveness probe, previous container logs.

### 3. Generate traffic and observe HPA

```bash
python scripts/load_test.py --url http://localhost:8080/api/orders --requests 1000 --concurrency 30
kubectl -n sre-lab get hpa -w
kubectl -n sre-lab get pods -w
```

HPA needs metrics-server and may take time to react. Resource thresholds depend on your machine.

### 4. Inspect resource usage

```bash
kubectl top nodes
kubectl top pods -n sre-lab
kubectl describe hpa -n sre-lab orders-api
```

### 5. Inspect service networking

```bash
kubectl -n sre-lab get svc,endpoints
kubectl -n sre-lab describe networkpolicy orders-api-default-deny
```

The included NetworkPolicy is intentionally restrictive and allows ingress to the API only from pods labelled `access: allowed` in the same namespace. Test it by launching a temporary client pod with and without that label.

## Core SRE concepts to explain

- **SLI:** measured service behavior, such as successful requests / total requests.
- **SLO:** target for an SLI, e.g. 99.5% successful requests over a rolling 30-day window.
- **Error budget:** permitted unreliability implied by the SLO.
- **Golden signals:** latency, traffic, errors, and saturation.
- **MTTD:** mean time to detect.
- **MTTR:** mean time to restore/recover.
- **RCA:** root cause analysis after service restoration.

## Useful commands

```bash
kubectl get all -n sre-lab
kubectl describe deployment orders-api -n sre-lab
kubectl logs -f deployment/orders-api -n sre-lab
kubectl logs deployment/orders-api -n sre-lab --previous
kubectl get events -n sre-lab --sort-by=.lastTimestamp
kubectl rollout history deployment/orders-api -n sre-lab
kubectl rollout undo deployment/orders-api -n sre-lab
kubectl auth can-i get pods --as=system:serviceaccount:sre-lab:orders-api -n sre-lab
```



## Cleanup

```bash
kubectl delete namespace sre-lab
helm uninstall monitoring -n monitoring
kubectl delete namespace monitoring
minikube delete
# or: kind delete cluster --name sre-lab
```

Author-Pradnya Gaikwad
