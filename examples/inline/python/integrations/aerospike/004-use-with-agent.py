import asyncio

from adk_aerospike import AerospikeArtifactService
from google.genai import types

async def main() -> None:
    svc = AerospikeArtifactService.from_uri(
        "aerospike://localhost:3000/adk"
    )

    await svc.save_artifact(
        app_name="support_bot",
        user_id="alice",
        session_id="s-1",
        filename="report.pdf",
        artifact=types.Part(
            inline_data=types.Blob(
                mime_type="application/pdf", data=b"%PDF-1.4..."
            ),
        ),
    )

    latest = await svc.load_artifact(
        app_name="support_bot",
        user_id="alice",
        session_id="s-1",
        filename="report.pdf",
    )
    print(latest.inline_data.mime_type)

    svc.close()

asyncio.run(main())