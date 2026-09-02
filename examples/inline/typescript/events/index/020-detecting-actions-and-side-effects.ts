export function handleStateChanges(event: Event) {
    if (event.actions && Object.keys(event.actions.stateDelta).length > 0) {
        console.log(`  State changes: ${JSON.stringify(event.actions.stateDelta)}`);
        // Update local UI or application state if necessary
    }
}