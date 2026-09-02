export function handleArtifactChanges(event: Event) {
    if (event.actions && Object.keys(event.actions.artifactDelta).length > 0) {
        console.log(`  Artifacts saved: ${JSON.stringify(event.actions.artifactDelta)}`);
        // UI might refresh an artifact list
    }
}