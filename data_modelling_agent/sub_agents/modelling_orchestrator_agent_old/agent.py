# import os
# from google.genai import types
# from typing import Optional
# from google.adk.agents.callback_context import CallbackContext
# from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents import Agent

# from .sub_agents.modelling_process_loop_agent.agent import modelling_process_loop_agent
from .tools import set_current_task


# def fetch_user_intention(callback_context: CallbackContext, llm_request: LlmRequest)-> LlmResponse:
#     kind_of_activity = callback_context.state.get("KIND_OF_ACTIVITY", None)
#     print("inside 'fetch_user_intention'")
#     # return kind_of_activity
#     return LlmResponse(
#                     content=types.Content(
#                         role="model",
#                         parts=[types.Part(text=f"{kind_of_activity}")],
#                     )
#                 )


modelling_orchestrator_agent = Agent(
    name="modelling_orchestrator_agent",
    description="Responsible to orchestrate the data modelling process and generate the models",
    instruction="""
        You are an helpful assistant to orchestrate data modelling process and generate different models. 
        To generate models you need to strictly follow the following instructions-
        
        1. Your primary goal is to generate a data model for the user. To do this, you must call the 'set_current_task' tool.
        2. Once the 'set_current_task' tool provides you with an output, your task is complete.
        3. You MUST present the output from the tool directly to the user as the final answer. Do not add any extra text or formatting unless the tool output itself contains it.

        **Guardrails**
        - Do not call the 'set_current_task' tool more than once.
        - The final output of your execution should be the direct output of the 'set_current_task' tool.
        """,
    tools=[set_current_task],
)

# If {"KIND_OF_ACTIVITY"} is '1': This means that the user wants to start a new data modelling afresh. **Invoke 'set_current_task' tool imemdiately.**
#         ELSE when {"KIND_OF_ACTIVITY"} is '2': This means that the user wants to start where they left off earlier. **Invoke 'set_current_task' tool imemdiately.**

#         Along with the at last you must mention all artifacts are saved and available in:
#         project: {{tool_output["project_id"]}}
#         gcs folder: {{tool_output["gcs_folder"]}}

#         Above location information must me highlighted well enough to user and user must be asked to save project and gcs folder for future use.
