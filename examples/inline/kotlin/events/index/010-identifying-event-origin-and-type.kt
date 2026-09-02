// Pseudocode: Basic event identification (Kotlin)
// runner.runAsync(...).collect { event ->
//     println("Event from: ${event.author}")
//
//     val content = event.content
//     if (content != null && content.parts.isNotEmpty()) {
//         if (event.functionCalls().isNotEmpty()) {
//             println("  Type: Tool Call Request")
//         } else if (event.functionResponses().isNotEmpty()) {
//             println("  Type: Tool Result")
//         } else if (content.parts[0].text != null) {
//             if (event.partial) {
//                 println("  Type: Streaming Text Chunk")
//             } else {
//                 println("  Type: Complete Text Message")
//             }
//         } else {
//             println("  Type: Other Content (e.g., code result)")
//         }
//     } else if (event.actions.stateDelta.isNotEmpty() || event.actions.artifactDelta.isNotEmpty()) {
//         println("  Type: State/Artifact Update")
//     } else {
//         println("  Type: Control Signal or Other")
//     }
// }