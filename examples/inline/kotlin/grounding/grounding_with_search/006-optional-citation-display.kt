events.collect { event ->
    if (event.isFinalResponse) {
        println(event.content?.parts?.firstOrNull()?.text)

        // Optional: Show source count
        val chunks = event.groundingMetadata?.groundingChunks
        if (!chunks.isNullOrEmpty()) {
            println("\nBased on ${chunks.size} documents")
        }
    }
}