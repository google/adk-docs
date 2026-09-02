import java.util.Map;
import java.util.Optional;

public static Map<String, Object> searchFlights(
    @Schema(description = "The destination city.", name = "destination")
    String destination,

    @Schema(description = "The desired departure date.", name = "departureDate")
    String departureDate,

    @Schema(description = "Number of flexible days for the search. Defaults to 0.", name = "flexibleDays")
    Optional<Integer> flexibleDays) {

    // ... function logic ...
    int days = flexibleDays.orElse(0);
    if (days > 0) {
        return Map.of("status", "success", "report", "Found flexible flights to " + destination + ".");
    }
    return Map.of("status", "success", "report", "Found flights to " + destination + " on " + departureDate + ".");
}