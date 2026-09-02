for await (const event of this.someSubAgent.runAsync(ctx)) {
    // Optionally inspect or log the event
    yield event; // Pass the event up to the runner
}