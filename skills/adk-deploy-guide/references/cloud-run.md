# Cloud Run Infrastructure

> **Assumes `/adk-scaffold` scaffolding.** For non-scaffolded projects, fetch `https://adk.dev/deploy/cloud-run/index.md`.

## Scaling & Resource Defaults

Agent Starter Pack scaffolds Cloud Run infrastructure in `deployment/terraform/service.tf`. Check that file for current resource limits, scaling configuration, concurrency, and session affinity settings.

Key settings to be aware of: `cpu_idle` (CPU allocation strategy), `min_instance_count` (cold start avoidance), `max_instance_request_concurrency` (concurrency per instance), and `session_affinity` (sticky routing).

## Dockerfile

Scaffolded projects include a `Dockerfile` using single-stage build with `uv` for dependency management. Check the project root `Dockerfile` for the exact configuration.

## FastAPI Endpoints

Available endpoints vary by project template. Check `app/fast_api_app.py` for the exact routes in your project.

## Session Types

| Type | Configuration | Use Case |
|------|--------------|----------|
| **In-memory** | Default (`session_service_uri = None`) | Local dev only; lost on instance restart |
| **Cloud SQL** | `--session-type cloud_sql` at scaffold time | Production persistent sessions (Postgres 15, IAM auth) |
| **Agent Engine** | `session_service_uri = agentengine://{resource_name}` | When using Agent Engine as session backend |

Cloud SQL session infrastructure (instance, database, Cloud SQL Unix socket volume mount) is configured in `deployment/terraform/service.tf`.

## Network & Ingress

Default ingress is `INGRESS_TRAFFIC_ALL` (public). To restrict, change the `ingress` setting in `service.tf` to `INGRESS_TRAFFIC_INTERNAL_ONLY` (VPC only) or `INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER` (internal + GCLB).

IAP is available via `make deploy IAP=true`, which adds Identity-Aware Proxy for Google identity authentication without code changes.

VPC connectors are not configured by default. Add them in custom Terraform if needed for private resource access (see `references/terraform-patterns.md`).
