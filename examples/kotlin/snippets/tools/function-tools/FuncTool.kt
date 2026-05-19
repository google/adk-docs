package com.google.adk.kt.examples.tools

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import kotlinx.coroutines.runBlocking

// --8<-- [start:full_example]
class StockService {
    /**
     * Retrieves the stock price for a given symbol.
     */
    @Tool
    fun getStockPrice(@Param("The stock symbol, e.g. GOOG") symbol: String): Map<String, Any> {
        // In a real app, you would call a stock price API here.
        return mapOf("symbol" to symbol, "price" to 123.45)
    }
}

fun main() = runBlocking {
    val stockService = StockService()
    
    val agent = LlmAgent(
        name = "stock_agent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction = Instruction("You are a helpful stock assistant."),
        // .generatedTools() is used to get the tools from the annotated class.
        tools = stockService.generatedTools()
    )
    
    // ... use the agent ...
}
// --8<-- [end:full_example]
