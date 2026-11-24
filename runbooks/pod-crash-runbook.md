# Runbook: Pod Crash / Restart

1. Check current state and restart count:
   `kubectl get pods -n sre-lab`
2. Inspect events and probe failures:
   `kubectl describe pod <pod-name> -n sre-lab`
3. Read current and previous logs:
   `kubectl logs <pod-name> -n sre-lab`
   `kubectl logs <pod-name> -n sre-lab --previous`
4. Check resource pressure:
   `kubectl top pods -n sre-lab`
5. Check configuration and mounted secrets:
   `kubectl describe deployment orders-api -n sre-lab`
6. After remediation, verify rollout, readiness, service endpoints, and error rate.

Do not delete or restart production pods as a first response without understanding impact and following the team's incident process.
