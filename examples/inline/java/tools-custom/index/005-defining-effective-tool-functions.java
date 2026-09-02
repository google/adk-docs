/**
 * Retrieves the current weather report for a specified city.
 *
 * @param city The city for which to retrieve the weather report.
 * @param toolContext The context for the tool.
 * @return A dictionary containing the weather information.
 */
public static Map<String, Object> getWeatherReport(String city, ToolContext toolContext) {
    Map<String, Object> response = new HashMap<>();
    if (city.toLowerCase(Locale.ROOT).equals("london")) {
        response.put("status", "success");
        response.put(
                "report",
                "The current weather in London is cloudy with a temperature of 18 degrees Celsius and a"
                        + " chance of rain.");
    } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
        response.put("status", "success");
        response.put("report", "The weather in Paris is sunny with a temperature of 25 degrees Celsius.");
    } else {
        response.put("status", "error");
        response.put("error_message", String.format("Weather information for '%s' is not available.", city));
    }
    return response;
}