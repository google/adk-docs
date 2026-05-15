package com.google.adk.kt.examples.artifacts

import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.models.GeminiModel
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.artifacts.InMemoryArtifactService
import com.google.adk.kt.artifacts.GcsArtifactService
import com.google.adk.kt.tools.ToolContext
import com.google.adk.kt.tools.LoadArtifactsTool
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Blob
import kotlinx.coroutines.runBlocking

// --8<-- [start:full_example]
// --8<-- [start:representation]
fun artifactRepresentationExample() {
    // Assume 'imageBytes' contains the binary data of a PNG image
    val imageBytes = byteArrayOf(0x89.toByte(), 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)

    val imageArtifact = Part(
        inlineData = Blob(
            mimeType = "image/png",
            data = imageBytes
        )
    )

    println("Artifact MIME Type: ${imageArtifact.inlineData?.mimeType}")
    println("Artifact Data (first 8 bytes): ${imageArtifact.inlineData?.data?.take(8)}")
}
// --8<-- [end:representation]

// --8<-- [start:configure_runner]
fun configureRunnerExample() {
    val myAgent = LlmAgent(name = "artifact_user_agent", model = GeminiModel("gemini-flash-latest"))
    val artifactService = InMemoryArtifactService()
    val sessionService = InMemorySessionService()

    val runner = InMemoryRunner(
        agent = myAgent,
        appName = "my_artifact_app",
        sessionService = sessionService,
        artifactService = artifactService
    )
}
// --8<-- [end:configure_runner]

// --8<-- [start:artifact_data]
fun artifactDataExample() {
    val pdfBytes = "%PDF-1.4...".toByteArray()
    val pdfMimeType = "application/pdf"

    val pdfArtifact = Part(
        inlineData = Blob(
            data = pdfBytes,
            mimeType = pdfMimeType
        )
    )

    println("Created Kotlin artifact with MIME type: ${pdfArtifact.inlineData?.mimeType}")
}
// --8<-- [end:artifact_data]

// --8<-- [start:namespacing]
fun namespacingExample() {
    // Session-specific artifact filename
    val sessionReportFilename = "summary.txt"

    // User-specific artifact filename
    val userConfigFilename = "user:settings.json"
}
// --8<-- [end:namespacing]

// --8<-- [start:interaction_save]
suspend fun saveGeneratedReport(context: ToolContext, reportBytes: ByteArray) {
    val reportArtifact = Part(
        inlineData = Blob(
            data = reportBytes,
            mimeType = "application/pdf"
        )
    )
    val filename = "generated_report.pdf"

    val service = context.invocationContext.artifactService
    if (service != null) {
        val version = service.saveArtifact(context.invocationContext.session.key, filename, reportArtifact)
        println("Successfully saved Kotlin artifact '$filename' as version $version.")
    } else {
        println("Artifact service not available.")
    }
}
// --8<-- [end:interaction_save]

// --8<-- [start:interaction_load]
suspend fun processLatestReport(context: ToolContext) {
    val filename = "generated_report.pdf"
    val reportArtifact = context.loadArtifact(filename)

    if (reportArtifact != null && reportArtifact.inlineData != null) {
        println("Successfully loaded latest Kotlin artifact '$filename'.")
        println("MIME Type: ${reportArtifact.inlineData?.mimeType}")
        val pdfBytes = reportArtifact.inlineData?.data
        println("Report size: ${pdfBytes?.size} bytes.")
    } else {
        println("Kotlin artifact '$filename' not found.")
    }
}
// --8<-- [end:interaction_load]

// --8<-- [start:load_artifacts_tool]
fun loadArtifactsToolExample() {
    val rootAgent = LlmAgent(
        name = "artifact_reader",
        model = GeminiModel("gemini-flash-latest"),
        instruction = Instruction(
            "Answer questions about available user files. " +
            "Call load_artifacts before answering when you need file contents."
        ),
        tools = listOf(LoadArtifactsTool())
    )
}
// --8<-- [end:load_artifacts_tool]

// --8<-- [start:listing_artifacts]
suspend fun listUserFiles(context: ToolContext): String {
    val availableFiles = context.listArtifacts()
    if (availableFiles.isEmpty()) {
        return "You have no saved artifacts."
    } else {
        val fileListStr = availableFiles.joinToString("\n") { "- $it" }
        return "Here are your available Kotlin artifacts:\n$fileListStr"
    }
}
// --8<-- [end:listing_artifacts]

// --8<-- [start:in_memory_service]
fun inMemoryServiceExample() {
    val inMemoryService = InMemoryArtifactService()
}
// --8<-- [end:in_memory_service]

// --8<-- [start:gcs_service]
fun gcsServiceExample() {
    val gcsBucketName = "your-gcs-bucket-for-adk-artifacts"
    try {
        // Initialize the GCS Storage client (usually uses Application Default Credentials)
        val storage = com.google.cloud.storage.StorageOptions.getDefaultInstance().service
        val gcsService = GcsArtifactService(bucketName = gcsBucketName, storageClient = storage)
        println("Kotlin GcsArtifactService initialized for bucket: $gcsBucketName")
    } catch (e: Exception) {
        println("Error initializing Kotlin GcsArtifactService: ${e.message}")
    }
}
// --8<-- [end:gcs_service]

fun main() = runBlocking {
    artifactRepresentationExample()
    artifactDataExample()
    inMemoryServiceExample()
    gcsServiceExample()
}
// --8<-- [end:full_example]
