from google.adk.artifacts import GcsArtifactService

# Specify the GCS bucket name
gcs_bucket_name_py = "your-gcs-bucket-for-adk-artifacts" # Replace with your bucket name

try:
    gcs_service_py = GcsArtifactService(bucket_name=gcs_bucket_name_py)
    print(f"Python GcsArtifactService initialized for bucket: {gcs_bucket_name_py}")
    # Ensure your environment has credentials to access this bucket.
    # e.g., via Application Default Credentials (ADC)

    # Then pass it to the Runner
    # runner = Runner(..., artifact_service=gcs_service_py)

except Exception as e:
    # Catch potential errors during GCS client initialization (e.g., auth issues)
    print(f"Error initializing Python GcsArtifactService: {e}")
    # Handle the error appropriately - maybe fall back to InMemory or raise