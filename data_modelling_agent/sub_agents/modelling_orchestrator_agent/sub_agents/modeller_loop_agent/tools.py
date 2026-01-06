import os
from google.genai import types
from typing import Optional
from google.adk.agents.llm_agent import Agent

# from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from typing import Optional

from google import genai
import os


def user_feedback_capture_tool(
    tool_context: ToolContext,
):
    print("Executing user_feedback_sentiment_tool()")
    current_state = tool_context.state
    events = tool_context._invocation_context.session.events
    print(f"events: {events}")
    try:
        for ev in events:
            if ev.content:
                if ev.content.role:
                    if ev.content.role == "user":
                        for part in ev.content.parts:
                            current_state["hitl_feedback"] = part.text
    except Exception as e:
        print(f"Error: {e}")
    return {}
