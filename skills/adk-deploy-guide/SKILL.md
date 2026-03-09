---
name: adk-deploy-guide
description: >
  MUST READ before deploying any ADK agent.
  ADK deployment guide — Agent Engine, Cloud Run, GKE, CI/CD pipelines,
  secrets, observability, and production workflows.
  Use when deploying agents to Google Cloud or troubleshooting deployments.
  Do NOT use for API code patterns (use adk-cheatsheet), evaluation
  (use adk-eval-guide), or project scaffolding (use adk-scaffold).
metadata:
  license: Apache-2.0
  author: Google
---

# ADK Deployment Guide

> **Scaffolded project?** Use the `make` commands throughout this guide — they wrap Terraform, Docker, and deployment into a tested pipeline.
>
> **No scaffold?** See [Quick Deploy](#quick-deploy-adk-cli) below, or the [ADK deployment docs](https://google.github.io/adk-docs/deploy/).
> For production infrastructure, scaffold with `/adk-scaffold`.

### Reference Files

For deeper details, consult these reference files in `references/`:

- **`cloud-run.md`** — Scaling defaults, Dockerfile, session types, networking
- **`agent-engine.md`** — deploy.py CLI, AdkApp pattern, Terraform resource, deployment metadata, CI/CD differences
- **`terraform-patterns.md`** — Custom infrastructure, IAM, state management, importing resources
- **`event-driven.md`** — Pub/Sub, Eventarc, BigQuery Remote Function triggers via custom `fast_api_app.py` endpoints

> **Observability:** See the **adk-observability-guide** skill for Cloud Trace, prompt-response logging, BigQuery Analytics, and third-party integrations.

---

## Deployment Target Decision Matrix

Choose the right deployment target based on your requirements:

| Criteria | Agent Engine | Cloud Run | GKE |
|----------|-------------|-----------|-----|
| **Languages** | Python | Python | Python (+ others via custom containers) |
| **Scaling** | Managed auto-scaling (configurable min/max, concurrency) | Fully configurable (min/max instances, concurrency, CPU allocation) | Full Kubernetes scaling (HPA, VPA, node auto-provisioning) |
| **Networking** | VPC-SC and PSC supported | Full VPC support, direct VPC egress, IAP, ingress rules | Full Kubernetes networking|
| **Session state** | Native `VertexAiSessionService` (persistent, managed) | In-memory (dev), Cloud SQL, or Agent Engine session backend | Custom (any Kubernetes-compatible store) |
| **Batch/event processing** | Not supported | `/invoke` endpoint for Pub/Sub, Eventarc, BigQuery | Custom (Kubernetes Jobs, Pub/Sub) |
| **Cost model** | vCPU-hours + memory-hours (not billed when idle) | Per-instance-second + min instance costs | Node pool costs (always-on or auto-provisioned) |
| **Setup complexity** | Lower (managed, purpose-built for agents) | Medium (Dockerfile, Terraform, networking) | Higher (Kubernetes expertise required) |
| **Best for** | Managed infrastructure, minimal ops | Custom infra, event-driven workloads | Full control, open models, GPU workloads |

**Ask the user** which deployment target fits their needs. Each is a valid production choice with different trade-offs.

---

## Quick Deploy (ADK CLI)

For projects without Agent Starter Pack scaffolding. No Makefile, Terraform, or Dockerfile required.

```bash
# Cloud Run
adk deploy cloud_run --project=PROJECT --region=REGION path/to/agent/

# Agent Engine
adk deploy agent_engine --project=PROJECT --region=REGION path/to/agent/

# GKE (requires existing cluster)
adk deploy gke --project=PROJECT --cluster_name=CLUSTER --region=REGION path/to/agent/
```

All commands support `--with_ui` to deploy the ADK dev UI. Cloud Run also accepts extra `gcloud` flags after `--` (e.g., `-- --no-allow-unauthenticated`).

See `adk deploy --help` or the [ADK deployment docs](https://google.github.io/adk-docs/deploy/) for full flag reference.

> For CI/CD, observability, or production infrastructure, scaffold with `/adk-scaffold` and use the sections below.

---

## Dev Environment Setup & Deploy (Scaffolded Projects)

### Setting Up Dev Infrastructure (Optional)

`make setup-dev-env` runs `terraform apply` in `deployment/terraform/dev/`. This provisions supporting infrastructure:
- Service accounts (`app_sa` for the agent, used for runtime permissions)
- Artifact Registry repository (for container images)
- IAM bindings (granting the app SA necessary roles)
- Telemetry resources (Cloud Logging bucket, BigQuery dataset)
- Any custom resources defined in `deployment/terraform/dev/`

This step is **optional** — `make deploy` works without it (Cloud Run creates the service on the fly via `gcloud run deploy --source .`). However, running it gives you proper service accounts, observability, and IAM setup.

```bash
make setup-dev-env
```

> **Note:** `make deploy` doesn't automatically use the Terraform-created `app_sa`. Pass `--service-account` explicitly or update the Makefile.

### Deploying

1. **Notify the human**: "Eval scores meet thresholds and tests pass. Ready to deploy to dev?"
2. **Wait for explicit approval**
3. Once approved: `make deploy`

**IMPORTANT**: Never run `make deploy` without explicit human approval.

---

## Production Deployment — CI/CD Pipeline

**Best for:** Production applications, teams requiring staging → production promotion.

**Prerequisites:**
1. Project must NOT be in a gitignored folder
2. User must provide staging and production GCP project IDs
3. GitHub repository name and owner

**Steps:**
1. If prototype, first add Terraform/CI-CD files using the Agent Starter Pack CLI (see `/adk-scaffold` for full options):
   ```bash
   uvx agent-starter-pack enhance . --cicd-runner github_actions -y -s
   ```

2. Ensure you're logged in to GitHub CLI:
   ```bash
   gh auth login  # (skip if already authenticated)
   ```

3. Run setup-cicd:
   ```bash
   uvx agent-starter-pack setup-cicd \
     --staging-project YOUR_STAGING_PROJECT \
     --prod-project YOUR_PROD_PROJECT \
     --repository-name YOUR_REPO_NAME \
     --repository-owner YOUR_GITHUB_USERNAME \
     --auto-approve \
     --create-repository
   ```

4. Push code to trigger deployments

#### Key `setup-cicd` Flags

| Flag | Description |
|------|-------------|
| `--staging-project` | GCP project ID for staging environment |
| `--prod-project` | GCP project ID for production environment |
| `--repository-name` / `--repository-owner` | GitHub repository name and owner |
| `--auto-approve` | Skip Terraform plan confirmation prompts |
| `--create-repository` | Create the GitHub repo if it doesn't exist |
| `--cicd-project` | Separate GCP project for CI/CD infrastructure. Defaults to prod project |
| `--local-state` | Store Terraform state locally instead of in GCS (see `references/terraform-patterns.md`) |

Run `uvx agent-starter-pack setup-cicd --help` for the full flag reference (Cloud Build options, dev project, region, etc.).

### Choosing a CI/CD Runner

| Runner | Pros | Cons |
|--------|------|------|
| **github_actions** (Default) | No PAT needed, uses `gh auth`, WIF-based, fully automated | Requires GitHub CLI authentication |
| **google_cloud_build** | Native GCP integration | Requires interactive browser authorization (or PAT + app installation ID for programmatic mode) |

### How Authentication Works (WIF)

Both runners use **Workload Identity Federation (WIF)** — GitHub/Cloud Build OIDC tokens are trusted by a GCP Workload Identity Pool, which grants `cicd_runner_sa` impersonation. No long-lived service account keys needed. Terraform in `setup-cicd` creates the pool, provider, and SA bindings automatically. If auth fails, re-run `terraform apply` in the CI/CD Terraform directory.

### CI/CD Pipeline Stages

The pipeline has three stages:

1. **CI (PR checks)** — Triggered on pull request. Runs unit and integration tests.
2. **Staging CD** — Triggered on merge to `main`. Builds container, deploys to staging, runs load tests.
   > **Path filter:** Staging CD uses `paths: ['app/**']` — it only triggers when files under `app/` change. The first push after `setup-cicd` won't trigger staging CD unless you modify something in `app/`. If nothing happens after pushing, this is why.
3. **Production CD** — Triggered after successful staging deploy via `workflow_run`. Might require **manual approval** before deploying to production.
   > **Approving:** Go to GitHub Actions → the production workflow run → click "Review deployments" → approve the pending `production` environment. This is GitHub's environment protection rules, not a custom mechanism.

**IMPORTANT**: `setup-cicd` creates infrastructure but doesn't deploy automatically. Terraform configures all required GitHub secrets and variables (WIF credentials, project IDs, service accounts). Push code to trigger the pipeline:

```bash
git add . && git commit -m "Initial agent implementation"
git push origin main
```

To approve production deployment:

```bash
# GitHub Actions: Approve via repository Actions tab (environment protection rules)

# Cloud Build: Find pending build and approve
gcloud builds list --project=PROD_PROJECT --region=REGION --filter="status=PENDING"
gcloud builds approve BUILD_ID --project=PROD_PROJECT
```

---

## Cloud Run Specifics

For detailed infrastructure configuration (scaling defaults, Dockerfile, FastAPI endpoints, session types, networking), see `references/cloud-run.md`. For ADK docs on Cloud Run deployment, fetch `https://google.github.io/adk-docs/deploy/cloud-run/index.md`.

---

## Agent Engine Specifics

Agent Engine is a managed Vertex AI service for deploying Python ADK agents. Uses source-based deployment (no Dockerfile) via `deploy.py` and the `AdkApp` class.

> **No `gcloud` CLI exists for Agent Engine.** Deploy via `deploy.py` or `adk deploy agent_engine`. Query via the Python `vertexai.Client` SDK.

Deployments can take 5-10 minutes. If `make deploy` times out, check if the engine was created and manually populate `deployment_metadata.json` with the engine resource ID (see reference for details).

For detailed infrastructure configuration (deploy.py flags, AdkApp pattern, Terraform resource, deployment metadata, session/artifact services, CI/CD differences), see `references/agent-engine.md`. For ADK docs on Agent Engine deployment, fetch `https://google.github.io/adk-docs/deploy/agent-engine/index.md`.

---

## Service Account Architecture

Scaffolded projects use two service accounts:

- **`app_sa`** (per environment) — Runtime identity for the deployed agent. Roles defined in `deployment/terraform/iam.tf`.
- **`cicd_runner_sa`** (CI/CD project) — CI/CD pipeline identity (GitHub Actions / Cloud Build). Lives in the CI/CD project (defaults to prod project), needs permissions in **both** staging and prod projects.

Check `deployment/terraform/iam.tf` for exact role bindings. Cross-project permissions (Cloud Run service agents, artifact registry access) are also configured there.

**Common 403 errors:**
- "Permission denied on Cloud Run" → `cicd_runner_sa` missing deployment role in the target project
- "Cannot act as service account" → Missing `iam.serviceAccountUser` binding on `app_sa`
- "Secret access denied" → `app_sa` missing `secretmanager.secretAccessor`
- "Artifact Registry read denied" → Cloud Run service agent missing read access in CI/CD project

---

## Secret Manager (for API Credentials)

Instead of passing sensitive keys as environment variables, use GCP Secret Manager.

```bash
# Create a secret
echo -n "YOUR_API_KEY" | gcloud secrets create MY_SECRET_NAME --data-file=-

# Update an existing secret
echo -n "NEW_API_KEY" | gcloud secrets versions add MY_SECRET_NAME --data-file=-
```

**Grant access:** For Cloud Run, grant `secretmanager.secretAccessor` to `app_sa`. For Agent Engine, grant it to the platform-managed SA (`service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com`).

**Pass secrets at deploy time (Agent Engine):**
```bash
make deploy SECRETS="API_KEY=my-api-key,DB_PASS=db-password:2"
```

Format: `ENV_VAR=SECRET_ID` or `ENV_VAR=SECRET_ID:VERSION` (defaults to latest). Access in code via `os.environ.get("API_KEY")`.

---

## Observability

See the **adk-observability-guide** skill for observability configuration (Cloud Trace, prompt-response logging, BigQuery Analytics, third-party integrations).

---

## Testing Your Deployed Agent

### Agent Engine Deployment

**Option 1: Testing Notebook**
```bash
jupyter notebook notebooks/adk_app_testing.ipynb
```

**Option 2: Python Script**
```python
import json
import vertexai

with open("deployment_metadata.json") as f:
    engine_id = json.load(f)["remote_agent_engine_id"]

client = vertexai.Client(location="us-central1")
agent = client.agent_engines.get(name=engine_id)

async for event in agent.async_stream_query(message="Hello!", user_id="test"):
    print(event)
```

**Option 3: Playground**
```bash
make playground
```

### Cloud Run Deployment

> **Auth required by default.** Cloud Run deploys with `--no-allow-unauthenticated`, so all requests need an `Authorization: Bearer` header with an identity token. Getting a 403? You're likely missing this header. To allow public access, redeploy with `--allow-unauthenticated`.

```bash
SERVICE_URL="https://SERVICE_NAME-PROJECT_NUMBER.REGION.run.app"
AUTH="Authorization: Bearer $(gcloud auth print-identity-token)"

# Test health endpoint
curl -H "$AUTH" "$SERVICE_URL/"

# Step 1: Create a session (required before sending messages)
curl -X POST "$SERVICE_URL/apps/app/users/test-user/sessions" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{}'
# → returns JSON with "id" — use this as SESSION_ID below

# Step 2: Send a message via SSE streaming
curl -X POST "$SERVICE_URL/run_sse" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{
    "app_name": "app",
    "user_id": "test-user",
    "session_id": "SESSION_ID",
    "new_message": {"role": "user", "parts": [{"text": "Hello!"}]}
  }'
```

> **Common mistake:** Using `{"message": "Hello!", "user_id": "...", "session_id": "..."}` returns `422 Field required`. The ADK HTTP server expects the `new_message` / `parts` schema shown above, and the session must already exist.

### Load Tests

```bash
make load-test
```

See `tests/load_test/README.md` for configuration, default settings, and CI/CD integration details.

---

## Deploying with a UI (IAP)

To expose your agent with a web UI protected by Google identity authentication:

```bash
# Deploy with IAP (built-in framework UI)
make deploy IAP=true

# Deploy with custom frontend on a different port
make deploy IAP=true PORT=5173
```

IAP (Identity-Aware Proxy) secures the Cloud Run service — only authorized Google accounts can access it. After deploying, grant user access via the [Cloud Console IAP settings](https://cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run#manage_user_or_group_access).

For Agent Engine with a custom frontend, use a **decoupled deployment** — deploy the frontend separately to Cloud Run or Cloud Storage, connecting to the Agent Engine backend API.

---

## Rollback & Recovery

The primary rollback mechanism is **git-based**: fix the issue, commit, and push to `main`. The CI/CD pipeline will automatically build and deploy the new version through staging → production.

For immediate Cloud Run rollback without a new commit, use revision traffic shifting:
```bash
gcloud run revisions list --service=SERVICE_NAME --region=REGION
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions=REVISION_NAME=100 --region=REGION
```

Agent Engine doesn't support revision-based rollback — fix and redeploy via `make deploy`.

---

## Custom Infrastructure (Terraform)

For custom infrastructure patterns (Pub/Sub, BigQuery, Eventarc, Cloud SQL, IAM), consult `references/terraform-patterns.md` for:
- Where to put custom Terraform files (dev vs CI/CD)
- Resource examples (Pub/Sub, BigQuery, Eventarc triggers)
- IAM bindings for custom resources
- Terraform state management (remote vs local, importing resources)
- Common infrastructure patterns

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Terraform state locked | `terraform force-unlock -force LOCK_ID` in deployment/terraform/ |
| GitHub Actions auth failed | Re-run `terraform apply` in CI/CD terraform dir; verify WIF pool/provider |
| Cloud Build authorization pending | Use `github_actions` runner instead |
| Resource already exists | `terraform import` (see `references/terraform-patterns.md`) |
| Agent Engine deploy timeout / hangs | Deployments take 5-10 min; check if engine was created (see Agent Engine Specifics) |
| Secret not available | Verify `secretAccessor` granted to `app_sa` (not the default compute SA) |
| 403 on deploy | Check `deployment/terraform/iam.tf` — `cicd_runner_sa` needs deployment + SA impersonation roles in the target project |
| 403 when testing Cloud Run | Default is `--no-allow-unauthenticated`; include `Authorization: Bearer $(gcloud auth print-identity-token)` header |
| Cold starts too slow | Set `min_instance_count > 0` in Cloud Run Terraform config |
| Cloud Run 503 errors | Check resource limits (memory/CPU), increase `max_instance_count`, or check container crash logs |
| 403 right after granting IAM role | IAM propagation is not instant — wait a couple of minutes before retrying. Don't keep re-granting the same role |
| Resource seems missing but Terraform created it | Run `terraform state list` to check what Terraform actually manages. Resources created via `null_resource` + `local-exec` (e.g., BQ linked datasets) won't appear in `gcloud` CLI output |
