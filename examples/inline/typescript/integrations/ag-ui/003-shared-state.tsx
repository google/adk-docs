const { state, setState } = useCoAgent<AgentState>({
  name: "my_agent",
  initialState: {
    proverbs: [
      "A journey of a thousand miles begins with a single step.",
    ],
  },
})