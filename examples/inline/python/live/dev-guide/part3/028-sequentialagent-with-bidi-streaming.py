# SequentialAgent automatically adds this tool to each sub-agent
def task_completed():
    """
    Signals that the agent has successfully completed the user's question
    or task.
    """
    return 'Task completion signaled.'