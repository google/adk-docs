// Example illustrating namespace difference (conceptual)

// Session-specific artifact filename
String sessionReportFilename = "summary.txt";

// User-specific artifact filename
String userConfigFilename = "user:settings.json"; // The "user:" prefix is key

// When saving 'summary.txt' via context.save_artifact,
// it's tied to the current app_name, user_id, and session_id.
// artifactService.saveArtifact(appName, userId, sessionId1, sessionReportFilename, someData);

// When saving 'user:settings.json' via context.save_artifact,
// the ArtifactService implementation should recognize the "user:" prefix
// and scope it to app_name and user_id, making it accessible across sessions for that user.
// artifactService.saveArtifact(appName, userId, sessionId1, userConfigFilename, someData);