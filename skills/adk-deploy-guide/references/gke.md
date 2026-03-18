# GKE Infrastructure

> **Assumes `/adk-scaffold` scaffolding.** For non-scaffolded projects, fetch `https://google.github.io/adk-docs/deploy/gke/index.md`.

## Deployment Architecture

GKE uses **container-based deployment** to a managed GKE Autopilot cluster. Your agent is packaged as a Docker container (same Dockerfile as Cloud Run), pushed to Artifact Registry, and deployed via Terraform-managed Kubernetes resources.

## Dockerfile

Scaffolded projects include a `Dockerfile` using single-stage build with `uv` for dependency management — same as Cloud Run. Check the project root `Dockerfile` for the exact configuration.

## Kubernetes Resources (Terraform-Managed)

All Kubernetes resources are managed by Terraform in `deployment/terraform/service.tf` (staging/prod) and `deployment/terraform/dev/service.tf` (dev). CI/CD pipelines only update the container image via `kubectl set image`.

| Resource | Purpose |
|----------|---------|
| **`kubernetes_deployment_v1`** | Pod spec, container config, resource requests/limits, startup/readiness/liveness probes, env vars, optional Cloud SQL proxy sidecar |
| **`kubernetes_service_v1`** | LoadBalancer service exposing port 8080 |
| **`kubernetes_horizontal_pod_autoscaler_v2`** | HorizontalPodAutoscaler (2-10 replicas, 70% CPU target) |
| **`kubernetes_pod_disruption_budget_v1`** | PodDisruptionBudget (minAvailable: 1) |
| **`kubernetes_service_account_v1`** | Kubernetes ServiceAccount for Workload Identity |
| **`kubernetes_namespace_v1`** | Namespace for the application |
| **`kubernetes_secret_v1`** | DB password secret (Cloud SQL only) |

## Terraform Infrastructure

GKE infrastructure is provisioned in `deployment/terraform/service.tf`. Check that file for current configuration.

Key differences from Cloud Run: Terraform provisions a full networking stack (VPC, subnet, Cloud NAT for private node internet access) and a GKE Autopilot cluster with private nodes. Cloud SQL (optional, when `session_type == "cloud_sql"`) uses a proxy sidecar in the pod rather than Cloud Run's Unix socket volume mount.

## Workload Identity

GKE uses Workload Identity to map Kubernetes service accounts to GCP service accounts. The Kubernetes SA in `deployment/terraform/service.tf` is bound to `app_sa` via an `iam.workloadIdentityUser` IAM binding in Terraform.

This lets pods authenticate as `app_sa` without service account keys — same security model as Cloud Run's service identity, but configured through Kubernetes.

## Session Types

| Type | Configuration | Use Case |
|------|--------------|----------|
| **In-memory** | Default (`session_service_uri = None`) | Local dev only; lost on pod restart |
| **Cloud SQL** | `--session-type cloud_sql` at scaffold time | Production persistent sessions (Cloud SQL proxy sidecar in pod) |
| **Agent Engine** | `session_service_uri = agentengine://{resource_name}` | When using Agent Engine as session backend |

Cloud SQL in GKE uses a **proxy sidecar container** in the pod (unlike Cloud Run which uses a Unix socket volume mount). The sidecar is configured in the `kubernetes_deployment_v1` Terraform resource.

## FastAPI Endpoints

Available endpoints vary by project template. Check `app/fast_api_app.py` for the exact routes in your project.

## Testing Your Deployed Agent

GKE LoadBalancer services are **public by default** — no auth header needed (unlike Cloud Run).

```bash
# Get the external IP
EXTERNAL_IP=$(kubectl get svc SERVICE_NAME -n NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_URL="http://$EXTERNAL_IP:8080"

# Test health endpoint
curl "$SERVICE_URL/"

# Create a session
curl -X POST "$SERVICE_URL/apps/app/users/test-user/sessions" \
  -H "Content-Type: application/json" \
  -d '{}'

# Send a message via SSE streaming
curl -X POST "$SERVICE_URL/run_sse" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "app",
    "user_id": "test-user",
    "session_id": "SESSION_ID",
    "new_message": {"role": "user", "parts": [{"text": "Hello!"}]}
  }'
```

## Network & Ingress

GKE LoadBalancer services are **public by default** (no authentication required). To restrict access:

- **Internal LoadBalancer** — Add the annotation `networking.gke.io/load-balancer-type: "Internal"` to the `kubernetes_service_v1` resource in Terraform to restrict access to VPC-internal clients only.
- **IAP (Identity-Aware Proxy)** — Requires switching from a LoadBalancer Service to a GKE Ingress with a BackendConfig. This is not supported via `make deploy IAP=true` (that flag is Cloud Run only). See the [GCP docs on IAP for GKE](https://cloud.google.com/iap/docs/enabling-kubernetes-howto) for setup.
- **Network policies** — Define Kubernetes NetworkPolicy resources to restrict pod-to-pod and external traffic within the cluster.
