# Runbook: Common Alerts

## HighErrorRate

**Severity**: Critical

**Symptoms**: Backend returning >5% 5xx errors.

**Steps**:
1. Check backend pod logs: `kubectl logs -l app=backend -n todo-app --tail=100`
2. Check database connectivity: `kubectl exec -it <backend-pod> -- python -c "import asyncpg; ..."`
3. Check Dapr sidecar logs: `kubectl logs <pod> -c daprd -n todo-app`
4. If DB issue, check Neon status page
5. If Dapr issue, restart Dapr sidecar: `kubectl rollout restart deployment/todo-app-backend -n todo-app`

## HighLatency

**Severity**: Warning

**Symptoms**: P95 latency >500ms on backend API.

**Steps**:
1. Check Jaeger for slow traces: port-forward to Jaeger UI (16686)
2. Check database query performance via pg_stat_statements
3. Check pod resource usage in Grafana
4. Scale backend if CPU-bound: `kubectl scale deployment/todo-app-backend --replicas=5 -n todo-app`

## PodCrashLooping

**Severity**: Critical

**Steps**:
1. Get pod events: `kubectl describe pod <pod-name> -n todo-app`
2. Check previous logs: `kubectl logs <pod-name> -n todo-app --previous`
3. Common causes: missing env vars, DB connection failure, OOM kill
4. If OOM: increase memory limits in values.yaml and redeploy

## PodNotReady

**Severity**: Warning

**Steps**:
1. Check readiness probe: `kubectl describe pod <pod-name> -n todo-app`
2. Check if health endpoint is responding
3. Check if dependencies (DB, Kafka) are available
4. Restart if stuck: `kubectl delete pod <pod-name> -n todo-app`
