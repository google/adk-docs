package com.google.adk.kt.examples.tools

import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool

// --8<-- [start:optional_params]
class FlightService {
    /**
     * Searches for flights.
     */
    @Tool
    fun searchFlights(
        @Param("The destination city.") destination: String,
        @Param("The desired departure date.") departureDate: String,
        @Param("Number of flexible days for the search. Defaults to 0.") flexibleDays: Int? = 0,
    ): String {
        // ... function logic ...
        val days = flexibleDays ?: 0
        if (days > 0) {
            return "Found flexible flights to $destination."
        }
        return "Found flights to $destination on $departureDate."
    }
}
// --8<-- [end:optional_params]
