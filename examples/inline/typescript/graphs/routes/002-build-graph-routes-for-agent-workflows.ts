export const rootAgent = new Workflow({
  name: 'routing_workflow',
  edges: [
    ['START', processMessage, router],
    [
      router,
      {
        'output-1': response1,
        'output-2': response2,
        'output-3': response3,
      },
    ],
  ],
});