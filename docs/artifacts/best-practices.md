## Best Practices

To use artifacts effectively and maintainably:

* **Choose the Right Service:** Use `InMemoryArtifactService` for rapid prototyping, testing, and scenarios where persistence isn't needed. Use `GcsArtifactService` (or implement your own `BaseArtifactService` for other backends) for production environments requiring data persistence and scalability.
* **Meaningful Filenames:** Use clear, descriptive filenames. Including relevant extensions (`.pdf`, `.png`, `.wav`) helps humans understand the content, even though the `mime_type` dictates programmatic handling. Establish conventions for temporary vs. persistent artifact names.
* **Specify Correct MIME Types:** Always provide an accurate `mime_type` when creating the `types.Part` for `save_artifact`. This is critical for applications or tools that later `load_artifact` to interpret the `bytes` data correctly. Use standard IANA MIME types where possible.
* **Understand Versioning:** Remember that `load_artifact()` without a specific `version` argument retrieves the *latest* version. If your logic depends on a specific historical version of an artifact, be sure to provide the integer version number when loading.
* **Use Namespacing (`user:`) Deliberately:** Only use the `"user:"` prefix for filenames when the data truly belongs to the user and should be accessible across all their sessions. For data specific to a single conversation or session, use regular filenames without the prefix.
* **Error Handling:**
    * Always check if an `artifact_service` is actually configured before calling context methods (`save_artifact`, `load_artifact`, `list_artifacts`) – they will raise a `ValueError` if the service is `None`.
    * Check the return value of `load_artifact`, as it will be `None` if the artifact or version doesn't exist. Don't assume it always returns a `Part`.
    * Be prepared to handle exceptions from the underlying storage service, especially with `GcsArtifactService` (e.g., `google.api_core.exceptions.Forbidden` for permission issues, `NotFound` if the bucket doesn't exist, network errors).
* **Size Considerations:** Artifacts are suitable for typical file sizes, but be mindful of potential costs and performance impacts with extremely large files, especially with cloud storage. `InMemoryArtifactService` can consume significant memory if storing many large artifacts. Evaluate if very large data might be better handled through direct GCS links or other specialized storage solutions rather than passing entire byte arrays in-memory.
* **Cleanup Strategy:** For persistent storage like `GcsArtifactService`, artifacts remain until explicitly deleted. If artifacts represent temporary data or have a limited lifespan, implement a strategy for cleanup. This might involve:
    * Using GCS lifecycle policies on the bucket.
    * Building specific tools or administrative functions that utilize the `artifact_service.delete_artifact` method (note: delete is *not* exposed via context objects for safety).
    * Carefully managing filenames to allow pattern-based deletion if needed.
