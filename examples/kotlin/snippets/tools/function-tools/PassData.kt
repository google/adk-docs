package com.google.adk.kt.examples.tools

import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.tools.ToolContext

// --8<-- [start:pass_data]
class DataPassingService {
    /**
     * Stores a value in the temporary session state.
     */
    @Tool
    fun storeValue(
        context: ToolContext,
        @Param("The value to store.") value: String
    ): String {
        // Store data in the 'temp:' state.
        context.invocationContext.session.state["temp:my_key"] = value
        return "Value stored."
    }

    /**
     * Retrieves a value from the temporary session state.
     */
    @Tool
    fun retrieveValue(context: ToolContext): String {
        // Retrieve data from the 'temp:' state.
        val value = context.invocationContext.session.state["temp:my_key"] as? String
        return "Retrieved value: $value"
    }
}
// --8<-- [end:pass_data]
