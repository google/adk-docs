# Agent Instruction Anti-Patterns

When designing ADK agents, certain instruction patterns can lead to architectural problems, poor user experience, or system failures. This guide identifies common anti-patterns and provides better alternatives based on proven solutions.

## Overview

Agent instructions that work well in theory may fail in practice due to the stateless nature of LLM interactions, external system constraints, or user experience expectations. Understanding these anti-patterns helps you design more robust and maintainable agent architectures.

## Anti-Pattern 1: Autonomous Polling Instructions

### The Problem

**❌ Anti-Pattern:**
```python
agent = Agent(
    name="approval-agent",
    instruction="""
    After submitting the request for approval, poll the status every 30 seconds
    by calling check_approval_status() until you get a decision.
    Keep checking until approved or rejected.
    """
)
```

**Why This Fails:**
- LLMs are stateless request-response systems and cannot "wait" or "sleep"
- Each polling attempt requires a new inference, increasing costs by ~93%
- Creates poor user experience with manual "continue" clicks
- Violates architectural principles of asynchronous systems

### The Solution: Backend Blocking Poll Pattern

**✅ Correct Pattern:**
```python
async def request_approval_with_poll(proposal: str) -> dict:
    """
    Blocks and polls approval API internally until decision received.
    Returns final result to agent in single call.
    """
    # Create approval request
    ticket_id = await create_approval_ticket(proposal)

    # Poll internally with timeout
    max_polls = 60  # 30 minutes
    poll_interval = 30  # seconds

    for poll_count in range(max_polls):
        if poll_count > 0:
            await asyncio.sleep(poll_interval)

        status = await check_approval_status(ticket_id)
        if status != 'pending':
            return {'decision': status, 'ticket_id': ticket_id}

    return {'decision': 'timeout', 'ticket_id': ticket_id}

agent = Agent(
    name="approval-agent",
    instruction="""
    Call request_approval_with_poll(proposal). This tool will block and
    poll internally until a decision is received (may take several minutes).
    Do NOT implement manual polling loops.
    """,
    tools=[request_approval_with_poll]
)
```

**Benefits:**
- Single LLM inference instead of 15+ inferences
- Better user experience (actually waits vs. fake waiting)
- Proper separation of concerns (polling logic in backend)
- Standard pattern across frameworks (LangChain, AutoGen)

## Anti-Pattern 2: Frontend Responsibility Confusion

### The Problem

**❌ Anti-Pattern:**
```python
agent = Agent(
    instruction="""
    Ask the user to manually refresh the dashboard every few minutes
    to check if their request has been processed. Tell them to come
    back to this conversation when they see an update.
    """
)
```

**Why This Fails:**
- Breaks conversation flow and context
- Poor user experience requiring manual intervention
- Doesn't leverage available backend capabilities
- Makes agent appear less intelligent than it could be

### The Solution: Choose the Right Pattern

**✅ For Dashboard/External System Approvals:**
```python
# Backend handles the waiting
async def dashboard_approval_poll(request_data: dict) -> dict:
    """Polls dashboard API until approval decision available"""
    return await poll_with_timeout(dashboard_api, request_data, timeout_minutes=30)
```

**✅ For Real-time User Interaction:**
```python
# Use confirmation tools for immediate decisions
@tool
def request_user_confirmation(question: str) -> str:
    """Request immediate user confirmation via UI"""
    return request_confirmation(question)
```

**✅ For Long-running Operations:**
```python
# Use LongRunningFunctionTool pattern
@tool
def initiate_long_operation(params: dict) -> dict:
    """Start operation and return tracking info"""
    operation_id = start_background_process(params)
    return {"operation_id": operation_id, "status": "started"}
```

## Anti-Pattern 3: Instruction Overloading

### The Problem

**❌ Anti-Pattern:**
```python
agent = Agent(
    instruction="""
    You are a helpful assistant. When users ask for weather, use get_weather().
    When they ask for news, use get_news(). For stock prices, use get_stock().
    If they want to place an order, first check inventory with check_inventory(),
    then validate payment with validate_payment(), then if approved poll the
    payment processor every 5 seconds with check_payment_status() until complete,
    then create_order(), then send_confirmation(), then update_inventory().
    Remember to always be polite and if anything fails start over.
    """
)
```

**Why This Fails:**
- Mixing architectural instructions with behavioral instructions
- Embedding polling anti-patterns in complex workflows
- Too many responsibilities in single instruction
- Difficult to debug when things go wrong

### The Solution: Separation of Concerns

**✅ Correct Pattern:**
```python
# Simple, focused agent instruction
checkout_agent = Agent(
    name="checkout-agent",
    instruction="Process customer orders by calling process_order() with item details.",
    tools=[process_order_workflow]
)

# Complex logic handled in tool
async def process_order_workflow(item_id: str, quantity: int) -> dict:
    """
    Handles complete order workflow with proper error handling.
    Includes inventory check, payment processing, order creation.
    """
    try:
        # Check inventory
        inventory = await check_inventory(item_id, quantity)
        if not inventory['available']:
            return {'status': 'failed', 'reason': 'insufficient inventory'}

        # Process payment (with internal polling if needed)
        payment_result = await process_payment_with_polling(amount)
        if payment_result['status'] != 'approved':
            return {'status': 'failed', 'reason': 'payment declined'}

        # Create order
        order = await create_order(item_id, quantity, payment_result['transaction_id'])

        return {'status': 'success', 'order_id': order['id']}

    except Exception as e:
        return {'status': 'error', 'reason': str(e)}
```

## Decision Matrix: When to Use Each Pattern

| Use Case | Pattern | Why |
|----------|---------|-----|
| **External dashboard approval** | Backend Blocking Poll | System can wait, user expects delay |
| **Real-time user confirmation** | Confirmation Tool | User is present, immediate response needed |
| **File processing/uploads** | LongRunningFunctionTool | Operation takes time, user may navigate away |
| **Multi-step workflows** | Workflow Tool | Complex logic better in code than instructions |
| **Simple tool calls** | Direct Tool | No polling or complex logic needed |

## Common Instruction Mistakes

### ❌ Mistake: Architectural Instructions in Behavior
```python
instruction="Be helpful. Always poll APIs every 30 seconds. Use try-catch for errors."
```

### ✅ Better: Behavioral Instructions Only
```python
instruction="You are a helpful customer service agent. Focus on resolving user issues efficiently."
```

### ❌ Mistake: Implementation Details in Instructions
```python
instruction="Call get_weather(), then parse JSON, then extract temperature field, then format as string."
```

### ✅ Better: Intent-Based Instructions
```python
instruction="Provide current weather information when requested."
# Implementation details in the tool function
```

### ❌ Mistake: Error Handling in Instructions
```python
instruction="If the API fails, retry 3 times, then ask user to try again later."
```

### ✅ Better: Error Handling in Code
```python
# Tool handles retries and error states
async def get_weather_with_retry(city: str) -> dict:
    for attempt in range(3):
        try:
            return await weather_api.get_weather(city)
        except Exception as e:
            if attempt == 2:  # Last attempt
                return {'error': 'Weather service temporarily unavailable'}
            await asyncio.sleep(1)
```

## Best Practices for Agent Instructions

### Do:
- Focus on **what** the agent should accomplish, not **how**
- Use **behavioral** guidance (tone, style, goals)
- Keep instructions **concise** and **clear**
- Handle complex logic in **tool implementations**
- Use appropriate patterns for **different interaction types**

### Don't:
- Include **polling** or **waiting** instructions
- Mix **architectural** concerns with **behavioral** guidance
- Embed **error handling** logic in instructions
- Create **overly complex** instruction sets
- Assume agents can maintain **state between calls**

## Related Documentation

- [Human-in-the-Loop Patterns](multi-agents.md#human-in-the-loop-pattern) - Existing synchronous approval patterns
- [Function Tools Guide](../tools-custom/function-tools.md) - LongRunningFunctionTool usage
- [Confirmation Tools](../tools-custom/confirmation.md) - Real-time user confirmation
- [Callback Patterns](../callbacks/design-patterns-and-best-practices.md) - Advanced lifecycle control

## GitHub Issues Addressed

This guide addresses several community-reported issues:

- [Issue #3607](https://github.com/google/adk-python/issues/3607) - Context detachment with HITL confirmations
- [Issue #3645](https://github.com/google/adk-python/issues/3645) - HITL TypeError in request confirmation
- [Issue #3184](https://github.com/google/adk-python/issues/3184) - Parent agents not pausing for sub-agent confirmations (resolved)

By following these patterns, you can avoid common pitfalls and build more robust, maintainable ADK agents that provide better user experiences.