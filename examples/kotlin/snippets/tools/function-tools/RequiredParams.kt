package com.google.adk.kt.examples.tools

import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool

// --8<-- [start:required_params]
class WeatherService {
    /**
     * Retrieves the weather for a city in the specified unit.
     */
    @Tool
    fun getWeather(
        @Param("The city and state, e.g., San Francisco, CA") location: String,
        @Param("The temperature unit, either 'Celsius' or 'Fahrenheit'") unit: String,
    ): String {
        // ... function logic ...
        return "Weather for $location is sunny in $unit."
    }
}
// --8<-- [end:required_params]
