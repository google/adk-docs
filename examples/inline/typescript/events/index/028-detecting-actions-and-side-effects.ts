export function handleControlFlow(event: Event) {
    if (event.actions) {
        if (event.actions.transferToAgent) {
            console.log(`  Signal: Transfer to ${event.actions.transferToAgent}`);
        }
        if (event.actions.escalate) {
            console.log('  Signal: Escalate (terminate loop)');
        }
        if (event.actions.skipSummarization) {
            console.log('  Signal: Skip summarization for tool result');
        }
    }
}