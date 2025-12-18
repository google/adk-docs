# Deployment Strategy Guide

Choosing the right deployment target for your ADK agents is critical for success. The ADK supports multiple deployment targets, ranging from fully managed serverless environments to custom containerized infrastructure.

This guide helps you choose the right path based on your specific needs.

## Decision Matrix

Use this matrix to quickly identify the best deployment target for your project.

| Feature | **Agent Engine** (Vertex AI) | **Cloud Run** (Serverless Container) | **GKE / Custom VM** |
| :--- | :--- | :--- | :--- |
| **Primary Use Case** | Pure agent logic, rapid prototyping, no-ops | Custom UIs, complex networking, specialized libraries | Enterprise compliance, existing K8s ecosystem |
| **Management Overhead** | **Low** (Fully Managed) | **Medium** (Container configuration) | **High** (Cluster management) |
| **State Management** | **Built-in** (Vertex AI Session Service) | **Ephemeral** (Requires external DB for persistence) | **External** (Requires external DB) |
| **Scaling** | Auto-scaling (Managed) | Auto-scaling (0 to N instances) | Manual or Cluster Autoscaling |
| **Networking** | Public API Endpoint | VPC connectivity, Custom Domains | Full VPC Control, Service Mesh |
| **Cost Model** | Pay-per-use (Token/Request) | Compute-based (vCPU/Memory/Time) | Instance-based (Always on) |

## Deployment Paths

### Path A: Vertex AI Agent Engine (Recommended for most)
**"I just want my agent to run."**

This is the managed service path. You write code, and Google runs it. It supports both the "Accelerated" (Agent Starter Pack) and "Standard" deployment workflows described in the [Agent Engine documentation](./agent-engine.md).

- **Pros**: No Dockerfile needed. No infrastructure config. Built-in conversation history via `VertexAiSessionService`.
- **Cons**: Restricted runtime environment (cannot install system-level packages like `apt-get`).
- **Command**: `adk deploy agent_engine`

### Path B: Cloud Run (Native Deployment)
**"I need a custom UI or specific libraries."**

This acts like "Vercel for Agents". The ADK handles the containerization, but you get a standard Cloud Run service.
- **Pros**: You can deploy a React frontend alongside your agent (`--with_ui`). You can install system dependencies (e.g., `poppler` for PDF parsing) by modifying the generated Dockerfile.
- **Cons**: Session state is **ephemeral** by default (stored in memory). If the container restarts or scales down, conversation history is lost unless you configure an external database (Redis/SQL).
- **Command**: `adk deploy cloud_run` (See [Cloud Run Guide](./cloud-run.md))

### Path C: Container / GKE
**"I have strict enterprise compliance requirements."**

You package the agent as a Docker container yourself and deploy it to your existing infrastructure.
- **Pros**: Complete control. Meets strict IT/Security policies.
- **Cons**: You own the build pipeline, security patching, and orchestration.
- **Guide**: See [GKE Guide](./gke.md)

## Common Deployment Gotchas

### Environment Variables
- **Agent Engine**: The `adk deploy agent_engine` command reads your local `.env` file at **deployment time** to configure the service.
    - *Tip*: If you exclude `.env` from version control (recommended), ensure you create one in your deployment environment (e.g., CI/CD pipeline) before running the deploy command.
- **Cloud Run**: Variables can be passed during deployment or updated later on the service.
    ```bash
    adk deploy cloud_run --service_name my-agent
    gcloud run services update my-agent --set-env-vars KEY=VALUE
    ```

### File Uploads
If your agent processes files (PDFs, Images):
- **Agent Engine**: Handles file storage automatically within the managed session context.
- **Cloud Run**: You must implement a mechanism to accept file uploads (e.g., multipart/form-data) and store them (e.g., in Google Cloud Storage) before passing the URI to the agent, as the container's filesystem is ephemeral.
