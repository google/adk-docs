# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.tools import ToolContext, FunctionTool
from google.genai import types
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import Session
import asyncio
from typing import cast


async def process_document(
    document_name: str, analysis_query: str, tool_context: ToolContext
) -> dict:
    """Analyzes a document using context from memory."""

    # 1. Load the artifact
    print(f"Tool: Attempting to load artifact: {document_name}")
    document_part = await tool_context.load_artifact(document_name)

    if not document_part:
        return {"status": "error", "message": f"Document '{document_name}' not found."}

    document_text = document_part.text  # Assuming it's text for simplicity
    print(f"Tool: Loaded document '{document_name}' ({len(document_text)} chars).")

    # 2. Search memory for related context
    print(f"Tool: Searching memory for context related to: '{analysis_query}'")
    memory_response = await tool_context.search_memory(
        f"Context for analyzing document about {analysis_query}"
    )
    memory_context = "\n".join(
        [
            m.content.parts[0].text
            for m in memory_response.memories
            if m.content and m.content.parts
        ]
    )
    
    # Simplified extraction
    print(f"Tool: Found memory context: {memory_context[:100]}...")

    # 3. Perform analysis (placeholder)
    analysis_result = f"Analysis of '{document_name}' regarding '{analysis_query}' using memory context: [Placeholder Analysis Result]"
    print("Tool: Performed analysis.")

    # 4. Save the analysis result as a new artifact
    analysis_part = types.Part.from_text(text=analysis_result)
    new_artifact_name = f"analysis_{document_name}"
    version = await tool_context.save_artifact(new_artifact_name, analysis_part)
    print(f"Tool: Saved analysis result as '{new_artifact_name}' version {version}.")

    return {
        "status": "success",
        "analysis_artifact": new_artifact_name,
        "version": version,
    }

async def read_report_and_create_part():
    """
    Reads content from report.txt, creates a Part using constructor,
    and saves it as an artifact.
    """
    # Read content from local report.txt file
    try:
        with open("report.txt", "r") as file:
            report_content = file.read()
            print(f"Successfully read report.txt ({len(report_content)} chars)")
    except FileNotFoundError:
        print("Error: report.txt file not found. Please create it first.")
        return None
    
    # Create a types.Part object using constructor
    report_part = types.Part(text=report_content)
    print("Created types.Part object using constructor: types.Part(text=content)")
    
    # Save it as an artifact
    artifact_service = InMemoryArtifactService()
    result = await artifact_service.save_artifact(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        filename="report.txt",
        artifact=report_part
    )
    
    print(f"Saved report content as artifact with version: {result}")
    return report_part

async def run_prompt(
      session: Session, 
      new_message: str,
      runner,
      user_id
    ) -> Session:
    content = types.Content(
        role='user', parts=[types.Part.from_text(text=new_message)]
    )
    print('** User says:', content.model_dump(exclude_none=True))
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        if not event.content or not event.content.parts:
            continue
        if event.content.parts[0].text:
            print(f'** {event.author}: {event.content.parts[0].text}')
        elif event.content.parts[0].function_call:
            print(
                f'** {event.author}: fc /'
                f' {event.content.parts[0].function_call.name} /'
                f' {event.content.parts[0].function_call.args}\n'
            )
        elif event.content.parts[0].function_response:
            print(
                f'** {event.author}: fr /'
                f' {event.content.parts[0].function_response.name} /'
                f' {event.content.parts[0].function_response.response}\n'
            )
        return cast(
            Session,
            await runner.session_service.get_session(
                app_name=runner.app_name, user_id=user_id, session_id=session.id
            ),
        )

doc_analysis_tool = FunctionTool(func=process_document)

# In an Agent:
# Assume artifact 'report.txt' was previously saved.
# Assume memory service is configured and has relevant past data.

APP_NAME="document_analyzes_app"
USER_ID="u_123"
SESSION_ID="s_123"
MODEL="gemini-2.0-flash"
user_question="can you help process report.txt, and analysis topic related google adk"

async def main():
    artifact_service = InMemoryArtifactService()


    report_part = await read_report_and_create_part()
    load_artifact_result = await artifact_service.save_artifact(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        filename="report.txt",
        artifact = report_part
        
    )


    memory_service=InMemoryMemoryService()
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID
    )
    content = types.Content(role='user', parts=[types.Part(text=user_question)])

    root_agent = LlmAgent(
        name="document_analyzes_agent",
        description="An agent that analyzes documents using context from memory",
        model=MODEL,
        tools=[doc_analysis_tool]
    )

    runner = Runner(
        agent=root_agent, 
        app_name=APP_NAME, 
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service
    )
    
    print(f'----Session to create memory: {session.id} ----------------------')
    session = await run_prompt(session, 'adk is opensource by google', runner, USER_ID)
    session = await run_prompt(session, 'Agent Development Kit (ADK) is a flexible and modular framework',runner,USER_ID)
    session = await run_prompt(session, 'We love ADK',runner,USER_ID)
    await memory_service.add_session_to_memory(
        session
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    ):
        print(event)

if __name__ == "__main__":
    asyncio.run(
        main()
    )