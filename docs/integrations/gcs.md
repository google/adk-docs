---
catalog_title: Google Cloud Storage
catalog_description: Access and perform operations on Google Cloud Storage buckets and objects
catalog_icon: /integrations/assets/gcs.png
catalog_tags: ["data", "google"]
---

# Google Cloud Storage (GCS)

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.3.0</span>
</div>

The `GCSToolset` and `GCSAdminToolset` allow ADK agents to interact with
[Google Cloud Storage (GCS)](https://cloud.google.com/storage) to manage buckets
and read/write objects.

## Use cases

- **Object Management**: Read, download, create, upload, list, metadata check,
  and delete GCS objects.
- **Bucket Management**: List cloud storage buckets, create new buckets, change
  configurations, such as enabling versioning or uniform bucket-level access, and
  delete buckets.
- **Data Integration**: Use cloud storage objects dynamically as part of the
  agent's workflow, such as processing files and ingestion.

## Prerequisites

- **Enable the Google Cloud Storage API** in the target Google Cloud project.
- **IAM Permissions**: The authenticated principal (Application Default
  Credentials, service account, or user) must have the correct permissions,
  including `roles/storage.admin`, to perform GCS
  bucket and object operations.
- A Google Cloud Project ID configured.

## Authentication

The `GCSToolset` and `GCSAdminToolset` support several authentication mechanisms
via `GCSCredentialsConfig`:

### Application Default Credentials

Recommended for local development and deployment to Google Cloud, including
Agent Runtime, Cloud Run, and GKE.

```python
--8<-- "examples/inline/python/integrations/gcs/001-application-default-credentials.py"
```

### Service Account

Allows providing credentials from a service account file.

```python
--8<-- "examples/inline/python/integrations/gcs/002-service-account.py"
```

### External Access Token

For acting on behalf of an end-user, such as via an OAuth2 flow or an external
identity provider.

```python
--8<-- "examples/inline/python/integrations/gcs/003-external-access-token.py"
```

### External Auth Providers

For platforms like Gemini Enterprise where the token is managed externally by
the environment or platform.

```python
--8<-- "examples/inline/python/integrations/gcs/004-external-auth-providers.py"
```

### Interactive Auth (ADK Web)

For interactive sessions using `adk web` interface to trigger an OAuth 2.0
login flow.

```python
--8<-- "examples/inline/python/integrations/gcs/005-interactive-auth-adk-web.py"
```

## Use with agent

The following example shows how to configure credentials and instantiate the
storage toolset with write access enabled.

```python
--8<-- "examples/inline/python/integrations/gcs/006-use-with-agent.py"
```

## Available tools

The GCS integration split the capabilities into two main toolsets:

### GCS Storage Tools (`GCSToolset`)

Tool | Description
---- | -----------
`gcs_list_objects` | List object names in a GCS bucket. Supports optional prefix filtering and pagination.
`gcs_get_object_metadata` | Get metadata properties of a specific GCS object (blob).
`gcs_create_object` | Create a new object (blob) in a bucket from in-memory string data or a local file upload. Requires `Capabilities.READ_WRITE`.
`gcs_get_object_data` | Get content of a GCS object as a string, or download it directly to a local file.
`gcs_delete_objects` | Delete multiple GCS objects (blobs) from a bucket. Requires `Capabilities.READ_WRITE`.

### GCS Admin Tools (`GCSAdminToolset`)

Tool | Description
---- | -----------
`gcs_list_buckets` | List GCS bucket names in a Google Cloud project.
`gcs_get_bucket` | Get metadata information about a GCS bucket.
`gcs_create_bucket` | Create a new GCS bucket in a specific location. Requires `Capabilities.READ_WRITE`.
`gcs_update_bucket` | Update properties of a GCS bucket, such as versioning or uniform bucket-level access. Requires `Capabilities.READ_WRITE`.
`gcs_delete_bucket` | Delete a GCS bucket (bucket must be empty first). Requires `Capabilities.READ_WRITE`.

!!! note

    The tool names listed here are the ones exposed to the model (prefixed with `gcs_`).
    When using `tool_filter`, reference the unprefixed names such as `get_bucket`.

## Sample agents

For complete, ready-to-run examples of GCS-powered agents with detailed
authentication configurations, see:

- [GCS Storage Sample Agent](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/gcs)
- [GCS Admin Sample Agent](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/gcs_admin)

## Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [GitHub Repository](https://github.com/google/adk-python)
