// Conceptual Structure of an Event (Kotlin)
// data class Event(
//     val author: String,
//     val content: Content? = null,
//     val actions: EventActions = EventActions(),
//     val invocationId: String? = null,
//     val branch: String? = null,
//     val timestamp: Long = Clock.System.now().toEpochMilliseconds(),
//     val id: String = Uuid.random(),
//     val partial: Boolean = false,
//     val turnComplete: Boolean = false,
//     val longRunningToolIds: Set<String> = emptySet()
// )