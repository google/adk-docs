// Within a tool implementation
async runAsync({ args, toolContext }: RunAsyncToolRequest) {
  const query = args['query'] as string;
  const response = await toolContext.searchMemory(query);
  // process response
  return {
    memories: response.memories.map(m => m.content.parts?.map(p => p.text).join(' ')).join('\n')
  };
}