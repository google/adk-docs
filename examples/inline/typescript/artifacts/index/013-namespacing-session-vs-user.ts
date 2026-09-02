// Example illustrating namespace difference (conceptual)

// Session-specific artifact filename
const sessionReportFilename = "summary.txt";

// User-specific artifact filename
const userConfigFilename = "user:settings.json";

// When saving 'summary.txt' via context.saveArtifact, it's tied to the current appName, userId, and sessionId.
// When saving 'user:settings.json' via context.saveArtifact, the ArtifactService implementation recognizes the "user:" prefix and scopes it to appName and userId, making it accessible across sessions for that user.