// Within a tool implementation
public Single<ToolOutput> execute(ToolContext context) {
  String query = ...; // get query from arguments
  return context.searchMemory(query)
      .map(response -> {
          // process response
          return new ToolOutput(response.memories().toString());
      });
}