// The @Schema annotation on the parameter provides the description.
public static Map<String, Object> getWeather(
    @Schema(description = "The city and state, e.g., San Francisco, CA", name = "location")
    String location,

    @Schema(description = "The temperature unit, either 'Celsius' or 'Fahrenheit'", name = "unit")
    String unit) {

    // ... function logic ...
    return Map.of("status", "success", "report", "Weather for " + location + " is sunny.");
}