---
name: microservices-production
description: "Build and deploy enterprise-grade microservices architectures with production-ready patterns, comprehensive observability, advanced security, and operational excellence. Use when: (1) designing multi-service architectures (FastAPI, Go, Node.js), (2) deploying to Kubernetes/Docker/Serverless, (3) implementing observability (logs, metrics, traces), (4) building event-driven systems, (5) securing services with mTLS/RBAC, or (6) operating production microservices. Includes framework-specific implementations, deployment patterns, monitoring setup, service mesh integration, and SRE practices."
---

# Microservices Production Skill

Build professional, scalable, and reliable microservices architectures from design through operations.

## Quick Start: Microservice Decision Tree

**Step 1: Choose Framework**
- **FastAPI (Python)**: Type-safe async APIs, automatic OpenAPI docs, Pydantic validation
- **Go/Gin**: High performance, compiled, excellent concurrency
- **Node.js/Express**: JavaScript ecosystem, real-time capabilities

See `references/frameworks/` for complete patterns and examples.

**Step 2: Choose Deployment Target**
- **Kubernetes (Recommended)**: Production cloud-native, auto-scaling, self-healing
- **Docker Compose**: Local development and testing
- **Serverless**: Managed infrastructure, auto-scaling on demand

See `references/deployment/` for setup and configuration.

**Step 3: Plan Observability Stack**
- **Logging**: Structured logs, centralized aggregation (ELK, Loki)
- **Metrics**: Performance monitoring, alerting (Prometheus, CloudWatch)
- **Tracing**: Request flow visualization (Jaeger, DataDog)

See `references/observability/` for complete setup guides.

**Step 4: Implement Advanced Patterns** (as needed)
- **Service Mesh**: Traffic management, security, resilience (Istio)
- **Event-Driven**: Async communication, saga patterns (Kafka, Dapr)
- **Security**: Zero-trust, mTLS, RBAC, secrets management

See `references/advanced/` for detailed patterns.

## Core Microservices Principles

### 1. Domain-Driven Design
- Organize services around business domains (bounded contexts)
- Each service owns its data (no shared databases)
- Clear service boundaries = clear API contracts

### 2. API Design
- REST for synchronous, query-heavy operations
- gRPC for internal service-to-service (performance critical)
- Message queues for asynchronous, event-driven workflows
- Versioning strategy from day one

### 3. Resilience Patterns
- **Timeouts**: Always set; prevents cascading failures
- **Retries**: Exponential backoff with jitter
- **Circuit Breakers**: Fail fast when downstream is unhealthy
- **Bulkheads**: Isolate resources per service
- **Graceful Degradation**: Degrade functionality, not crash

### 4. Data Consistency
- **Strongly Consistent**: Single service or distributed transactions (rare)
- **Eventually Consistent**: Async messaging, event sourcing (preferred)
- **Saga Pattern**: Multi-step workflows with rollback logic

## Production Checklist

Before deploying to production, validate:

**Architecture**
- [ ] Service boundaries are clear (bounded contexts)
- [ ] Each service owns its data
- [ ] Asynchronous communication patterns for loose coupling
- [ ] API versioning strategy defined

**Implementation**
- [ ] Structured logging with correlation IDs
- [ ] Metrics and health checks on all services
- [ ] Graceful shutdown handlers (SIGTERM)
- [ ] Configuration via environment variables (12-factor app)
- [ ] Secret management (not in code or config files)

**Deployment**
- [ ] Container images building and running correctly
- [ ] Kubernetes manifests or docker-compose validated
- [ ] Resource requests/limits configured
- [ ] Health checks (liveness/readiness probes)
- [ ] Auto-scaling policies defined

**Observability**
- [ ] Structured logs flowing to centralized system
- [ ] Key metrics exposed and alerting configured
- [ ] Distributed tracing enabled end-to-end
- [ ] Dashboards for on-call visibility

**Security**
- [ ] Service-to-service authentication (mTLS or JWT)
- [ ] Data encrypted in transit and at rest
- [ ] Network policies restricting traffic
- [ ] Secret rotation automated
- [ ] RBAC configured per environment

**Testing**
- [ ] Unit tests (business logic)
- [ ] Integration tests (against dependencies)
- [ ] Contract tests (API contracts between services)
- [ ] Load/chaos tests (resilience validation)

## Common Patterns & Gotchas

### Distributed Tracing Correlation
Always propagate trace IDs through requests:
```python
# FastAPI example
trace_id = request.headers.get("X-Trace-ID", str(uuid4()))
# Pass trace_id to downstream services
```

### Service Discovery
- **Kubernetes**: Use DNS, no client-side discovery
- **Docker Compose**: Service names resolve to IPs
- **External**: Use service discovery tool (Consul, Eureka)

### Secrets Management
- **Never** hardcode secrets in config files
- Use: Kubernetes Secrets, HashiCorp Vault, cloud provider secret manager
- Rotate regularly; audit access

### Database Per Service
- Each service has its own database (enforces isolation)
- No direct database access between services (use APIs)
- Data consistency handled via events/sagas

### Asynchronous Communication
- Use message queues for non-blocking operations
- Implement idempotency (same message processed 2x = same result)
- Handle dead-letter queues for failed messages

## Reference Files

- **Framework Guides**: `references/frameworks/` - FastAPI, Go, Node.js implementations
- **Deployment Guides**: `references/deployment/` - Kubernetes, Docker Compose, Serverless
- **Observability Guides**: `references/observability/` - Logging, metrics, tracing setup
- **Advanced Patterns**: `references/advanced/` - Service mesh, event-driven, security

## Scripts & Tools

- `scripts/bootstrap-k8s.py` - Generate Kubernetes manifests
- `scripts/generate-dockerfile.py` - Create production-optimized Dockerfiles
- `scripts/setup-monitoring.py` - Initialize monitoring stack
- `assets/templates/` - Service boilerplates (FastAPI, Go, Node.js)
- `assets/helm-charts/` - Helm charts for deployment

## Workflow: Build a Microservice from Scratch

1. **Design Phase**
   - Define service boundaries (domain-driven design)
   - Design API contracts (OpenAPI/gRPC specs)
   - Plan data consistency approach

2. **Implementation Phase**
   - Choose framework from `references/frameworks/`
   - Use boilerplate from `assets/templates/`
   - Implement health checks, structured logging, graceful shutdown

3. **Containerization Phase**
   - Use `scripts/generate-dockerfile.py` to create Dockerfile
   - Test container locally with Docker Compose

4. **Deployment Phase**
   - Choose deployment target from `references/deployment/`
   - Generate Kubernetes manifests with `scripts/bootstrap-k8s.py`
   - Configure resource limits, probes, scaling policies

5. **Observability Phase**
   - Add structured logging per `references/observability/logging.md`
   - Expose metrics per `references/observability/metrics.md`
   - Enable distributed tracing per `references/observability/tracing.md`

6. **Security Phase**
   - Implement service authentication (mTLS or JWT)
   - Configure network policies
   - Set up secret management

7. **Operations Phase**
   - Define SLOs and error budgets
   - Create runbooks for common issues
   - Set up alerting and on-call rotation

## Example: Building a 3-Service E-Commerce Platform

**Services:**
1. `product-catalog` - Product data and search (Go)
2. `order-service` - Order management and payment (FastAPI)
3. `notification-service` - Email/SMS notifications (Node.js)

**Workflow:**
1. Design service boundaries and API contracts
2. Implement each service using framework guides
3. Dockerize each service
4. Deploy to Kubernetes using bootstrap script
5. Set up centralized logging, metrics, tracing
6. Implement saga pattern for order workflow
7. Add Istio for traffic management and mTLS
8. Test with chaos engineering (kill pods, network delays)
9. Set up on-call alerting and runbooks

See reference files for detailed patterns and examples for each framework and deployment target.
