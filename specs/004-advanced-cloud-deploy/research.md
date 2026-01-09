# Research: Phase V - Advanced Cloud Deployment

**Feature**: 004-advanced-cloud-deploy
**Date**: 2026-01-04
**Status**: Complete

## Research Areas

### 1. Dapr Integration with FastAPI

**Decision**: Use Dapr Python SDK with HTTP-based Dapr sidecar communication

**Rationale**:
- Dapr sidecar runs alongside each service, exposing HTTP/gRPC APIs on localhost:3500
- Python SDK provides typed wrappers but HTTP calls work without SDK dependency
- Pub/Sub via `POST http://localhost:3500/v1.0/publish/{pubsub-name}/{topic}`
- State management via `GET/POST http://localhost:3500/v1.0/state/{store-name}`
- Minimal code changes to existing FastAPI endpoints

**Alternatives Considered**:
- Direct Kafka client (aiokafka): More code, tighter coupling, no abstraction
- gRPC Dapr SDK: Higher performance but more complex setup
- Dapr Actors: Overkill for this use case

**Implementation Pattern**:
```python
import httpx

DAPR_HTTP_PORT = 3500

async def publish_event(topic: str, data: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/kafka-pubsub/{topic}",
            json=data
        )
```

---

### 2. Recurring Task Pattern Implementation

**Decision**: Use python-dateutil rrule for recurrence calculation + event-driven generation

**Rationale**:
- `rrule` is the standard for RFC 5545 (iCalendar) recurrence rules
- Supports daily, weekly, monthly, yearly patterns plus complex custom rules
- Well-tested library used by major calendar applications
- Event-driven: On task completion, publish event → Recurring Service creates next occurrence

**Alternatives Considered**:
- Cron expressions: Less intuitive for users, harder to represent "every 2nd Tuesday"
- Custom recurrence logic: Error-prone, reinventing the wheel
- Pre-generate all occurrences: Wasteful storage, hard to handle pattern changes

**Implementation Pattern**:
```python
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from datetime import datetime

def get_next_occurrence(pattern: RecurrencePattern, after: datetime) -> datetime:
    rule = rrule(
        freq=pattern.frequency,
        interval=pattern.interval,
        byweekday=pattern.day_of_week,
        dtstart=pattern.start_date,
        until=pattern.end_date
    )
    return rule.after(after)
```

---

### 3. Real-time Sync via WebSocket

**Decision**: Use Dapr Pub/Sub → WebSocket Service pattern with Server-Sent Events fallback

**Rationale**:
- Backend publishes to `task-updates` topic via Dapr
- Dedicated WebSocket service subscribes and broadcasts to connected clients
- SSE fallback for browsers with WebSocket issues
- Dapr handles message delivery guarantees

**Alternatives Considered**:
- Direct WebSocket from Backend: Couples real-time to main API, scaling issues
- Polling: Higher latency, more server load
- Firebase/Pusher: External dependency, cost at scale

**Implementation Pattern**:
```python
# WebSocket Service subscribes to Dapr
@app.post("/dapr/subscribe")
async def subscribe():
    return [{"pubsubname": "kafka-pubsub", "topic": "task-updates", "route": "/events/task-updates"}]

@app.post("/events/task-updates")
async def handle_task_update(event: CloudEvent):
    await broadcast_to_clients(event.data)
```

---

### 4. Full-Text Search Strategy

**Decision**: PostgreSQL full-text search with tsvector/tsquery

**Rationale**:
- Native PostgreSQL feature, no additional service
- Supports stemming, ranking, phrase matching
- GIN index for performance on 10,000+ tasks
- Neon PostgreSQL fully supports full-text search

**Alternatives Considered**:
- Elasticsearch: Overkill for current scale, additional infrastructure
- Algolia/Typesense: External service, cost
- LIKE queries: Poor performance, no ranking

**Implementation Pattern**:
```sql
-- Add search vector column
ALTER TABLE tasks ADD COLUMN search_vector tsvector;
CREATE INDEX tasks_search_idx ON tasks USING GIN(search_vector);

-- Update trigger
CREATE TRIGGER tasks_search_update BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);

-- Search query
SELECT * FROM tasks
WHERE search_vector @@ plainto_tsquery('english', 'project alpha')
ORDER BY ts_rank(search_vector, plainto_tsquery('english', 'project alpha')) DESC;
```

---

### 5. Email Notification Delivery

**Decision**: Use Resend or SendGrid with async processing via Dapr binding

**Rationale**:
- Both offer free tiers sufficient for development/testing
- Dapr output binding abstracts email provider
- Async processing prevents blocking main API
- Easy provider swap via Dapr component config

**Alternatives Considered**:
- SMTP direct: Requires mail server setup, deliverability issues
- AWS SES: Good but requires AWS account
- Mailgun: Similar to SendGrid, slightly less generous free tier

**Implementation Pattern**:
```yaml
# Dapr component for email binding
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: email-output
spec:
  type: bindings.smtp
  version: v1
  metadata:
    - name: host
      value: "smtp.resend.com"
    - name: port
      value: "587"
    - name: user
      secretKeyRef:
        name: email-secrets
        key: username
```

---

### 6. Kubernetes Deployment Best Practices

**Decision**: Helm charts with values overrides per environment

**Rationale**:
- Helm is the standard for K8s package management
- Single chart with environment-specific values (dev, staging, prod)
- Supports rollbacks, upgrades, templating
- Works across Minikube, DOKS, GKE, AKS

**Alternatives Considered**:
- Kustomize: Good but less feature-rich than Helm
- Plain YAML: No templating, repetitive
- Pulumi/CDK: Adds programming language dependency

**Implementation Pattern**:
```yaml
# values-production.yaml
replicaCount:
  backend: 3
  frontend: 2
  notification: 2
resources:
  backend:
    limits:
      cpu: 500m
      memory: 512Mi
ingress:
  enabled: true
  host: todo.example.com
```

---

### 7. CI/CD Pipeline Structure

**Decision**: GitHub Actions with reusable workflows and environment protection rules

**Rationale**:
- Native GitHub integration
- Free for public repos, generous minutes for private
- Environment protection rules for production gates
- Reusable workflows reduce duplication

**Alternatives Considered**:
- GitLab CI: Good but requires GitLab
- ArgoCD: GitOps approach, more complex setup
- Jenkins: Self-hosted overhead

**Implementation Pattern**:
```yaml
# .github/workflows/cd-production.yml
jobs:
  deploy:
    environment:
      name: production
      url: https://todo.example.com
    steps:
      - uses: azure/k8s-set-context@v3  # or DOKS/GKE equivalent
      - run: helm upgrade --install todo-app ./infra/helm/todo-app -f values-production.yaml
```

---

### 8. Monitoring Stack Selection

**Decision**: Prometheus + Grafana for metrics, Loki for logs, Jaeger for tracing

**Rationale**:
- All open-source, no licensing costs
- Dapr has built-in Prometheus metrics export
- Grafana provides unified dashboards
- Loki integrates with Grafana for logs
- Jaeger integrates with Dapr for distributed tracing

**Alternatives Considered**:
- Datadog: Excellent but expensive at scale
- Cloud-native (CloudWatch, Stackdriver): Vendor lock-in
- ELK Stack: Elasticsearch resource-heavy

**Implementation Pattern**:
```yaml
# Dapr configuration for metrics
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
spec:
  metric:
    enabled: true
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: http://jaeger-collector:9411/api/v2/spans
```

---

## Summary

All technical unknowns have been resolved:

| Area | Decision | Confidence |
|------|----------|------------|
| Dapr Integration | HTTP-based sidecar communication | High |
| Recurrence | python-dateutil rrule | High |
| Real-time Sync | Dapr Pub/Sub → WebSocket | High |
| Search | PostgreSQL full-text | High |
| Email | Resend/SendGrid via Dapr binding | High |
| K8s Deployment | Helm charts | High |
| CI/CD | GitHub Actions | High |
| Monitoring | Prometheus/Grafana/Loki/Jaeger | High |

**Ready for Phase 1: Data Model & Contracts**
