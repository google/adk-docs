"""A minimal example demonstrating ConditionalAgent.

This sample shows how to route user requests to different sub-agents based on a
predicate evaluated against the current `InvocationContext`.

• If the user asks to *roll* a die → `roll_agent` is triggered.
• Otherwise, the request is delegated to `prime_agent` for prime-number checks.
"""
from __future__ import annotations

import random
from typing import cast

from google.adk.agents.conditional_agent import ConditionalAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types

# -----------------------------------------------------------------------------
# Helper tool functions
# -----------------------------------------------------------------------------

def roll_die(sides: int) -> int:
    """Roll a die with a given number of *sides* and return the result."""
    return random.randint(1, sides)


def check_prime(nums: list[int]) -> str:
    """Return a formatted string indicating which numbers are prime."""
    primes = []
    for n in nums:
        n = int(n)
        if n <= 1:
            continue
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                break
        else:
            primes.append(n)
    return "No prime numbers found." if not primes else ", ".join(map(str, primes)) + " are prime numbers."

# -----------------------------------------------------------------------------
# Sub-agents definitions
# -----------------------------------------------------------------------------

roll_agent = LlmAgent(
    name="roll_agent",
    description="Handles rolling dice of different sizes.",
    model="gemini-2.0-flash",
    instruction=(
        """
        You are responsible for rolling dice based on the user's request.\n
        When asked to roll a die, call the `roll_die` tool with the number of
        sides. Do **not** decide the outcome yourself – always use the tool.
        """
    ),
    tools=[roll_die],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)

prime_agent = LlmAgent(
    name="prime_agent",
    description="Checks whether provided numbers are prime.",
    model="gemini-2.0-flash",
    instruction=(
        """
        You determine if numbers are prime.\n
        Whenever the user asks about prime numbers, call the `check_prime` tool
        with a list of integers and return its result. Never attempt to compute
        primes manually – always rely on the tool.
        """
    ),
    tools=[check_prime],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)

# -----------------------------------------------------------------------------
# Predicate used by the ConditionalAgent
# -----------------------------------------------------------------------------

def is_roll_request(ctx: InvocationContext) -> bool:
    """Return True if the last user message seems to be a *roll* request."""
    if not ctx.user_content or not ctx.user_content.parts:
        return False
    text = cast(str, getattr(ctx.user_content.parts[0], "text", "")).lower()
    return "roll" in text

# -----------------------------------------------------------------------------
# Root ConditionalAgent
# -----------------------------------------------------------------------------

root_agent = ConditionalAgent(
    name="simple_conditional_agent",
    description="Routes to roll or prime agent based on user's intent.",
    sub_agents=[roll_agent, prime_agent],
    condition=is_roll_request,
)
