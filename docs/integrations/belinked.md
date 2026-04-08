
---
catalog_title: BeLinked
catalog_description: AI-ready booking tools for BeTask services.
catalog_icon: /integrations/assets/belinked.png
---

# BeLinked Booking Tools for Google ADK

Belinked Booking Tools is a toolkit that enables Google ADK agents to perform end-to-end service booking through structured tool calls.

It provides ready-to-use functions for:
- Retrieving available branches
- Browsing services by branch
- Creating appointments with real-time availability

Designed for chat-based experiences, this integration allows AI agents to guide users through the full booking flow, from discovery to confirmation, while ensuring accurate and deterministic execution via backend APIs.

## Use cases

- **Use Case 1**: Chat-based appointment booking — Users can interact with an AI agent to discover available branches, explore services, and book appointments in real time without leaving the chat interface.
- **Use Case 2**: Guided service selection — The AI agent helps users choose suitable services based on their intent (e.g., hair treatment, spa, clinic), then completes the booking flow by checking availability and confirming the appointment.

## Prerequisites

- **Required accounts**:
  - A Betask account is required to access the booking system.
  - Users must register and create a shop to obtain a valid `shopId` via:
    https://shop-web.betaskthai.tech/

- **Required data**:
  - A valid `shopId` from the Betask platform
 

## Installation

```bash
pip install belinked-adk
```

## Use with agent

```python
from google.adk.agents import Agent

from belinked_adk.tools.browse_services import browse_services_tool
from belinked_adk.tools.book_appointment import book_appointment_tool
from belinked_adk.tools.get_branches import get_branches_tool
from belinked_adk.utils.date_parser import parse_human_date
from dotenv import load_dotenv
import os

load_dotenv()

BETASK_SHOP_ID = os.getenv("BETASK_SHOP_ID")
LINE_USER_ID = "user id"
LINE_DISPLAY_NAME = "user name"


def get_branches_wrapper():
    print("🔥 TOOL CALLED: get_branches_tool")
    return get_branches_tool(
        line_user_id=LINE_USER_ID,
        line_display_name=LINE_DISPLAY_NAME,
        shop_id=BETASK_SHOP_ID
    )


def browse_services_wrapper(branch_id):
    return browse_services_tool(
        line_user_id=LINE_USER_ID,
        line_display_name=LINE_DISPLAY_NAME,
        shop_id=BETASK_SHOP_ID,
        branch_id=branch_id
    )

def book_appointment_wrapper(
    service_keyword: str,
    date: str,
    time: str,
    remark: str = ""
):
    return book_appointment_tool(
        line_user_id=LINE_USER_ID,
        line_display_name=LINE_DISPLAY_NAME,
        shop_id=BETASK_SHOP_ID,
        service_keyword=service_keyword,
        date=date,
        time=time,
        remark=remark
    )

root_agent = Agent(
    model="gemini-2.5-flash",
    name="booking_agent",
    tools=[
        browse_services_wrapper,
        book_appointment_wrapper,
        get_branches_wrapper,
        parse_human_date
    ],
    instruction="""
You are a service booking assistant.

Your responsibilities:
- Help users book appointments
- Provide information about available services

Important rules:
- Do not assume or fabricate any information
- Always use tools when required data is missing
- Respond in the same language as the user (e.g., if the user speaks Thai, reply in Thai)

Workflow:

1. If the user asks about services but no branch is selected:
   → You MUST call get_branches_tool first
   → Then present the list of branches for the user to choose

2. If a branch is selected but no service is specified:
   → Use browse_services_tool

3. If date or time is missing:
   → Ask the user for the missing information

4. If all required information is available:
   → Use book_appointment_tool

Response format:

- When showing branches:
  "Available branches:\n- Branch A\n- Branch B"

- When showing services:
  "Available services:\n- ..."

- If information is incomplete:
  Ask the user for more details

- Always respond in a friendly and helpful tone to guide the user through the booking process
- Do NOT respond in JSON or any structured format
- Do NOT display code or tool calls in the response

Date handling rules:

- Users may provide dates in natural language, such as:
  - today
  - tomorrow
  - next Monday
  - วันนี้
  - พรุ่งนี้

- You MUST convert these into YYYY-MM-DD format by calling parse_human_date tool before calling any booking-related tool
"""
)

```

## Available tools

Tool | Description
---- | -----------
`get_branches_tool` | Get available branches for booking.
`browse_services_tool` | Get services available at a branch.
`book_appointment_tool` | Book an appointment with selected details.
`parse_human_date` | Convert natural language dates to YYYY-MM-DD.

## Resources

- [BeTask Website]([https://example.com/docs](https://shop-web.betaskthai.tech)
