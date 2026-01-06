from google.adk.agents import LoopAgent, Agent, LlmAgent

# from ..modeller_agent.agent import modeller_agent
# from .checker_agent import exit_loop
import os
from google.genai import types
from google.adk.tools import ToolContext
from google.adk.models import LlmResponse

# from google.adk.agents.callback_context import CallbackContext
# from .tools import user_feedback_capture_tool
# # from ..modeller_agent.prompts import instructions_latest_loop


async def save_content(tool_context: ToolContext):
    print("@@@@@ saving now....")
    try:
        content = "I am ADK"
        report_artifact = types.Part()
        await tool_context.save_artifact(
            filename="content.txt", artifact=report_artifact
        )
    except Exception as e:
        print(f"Error: {e}")


root_agent = LlmAgent(
    name="HumanInTheLoopAgent",
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    instruction=f"""
    You are a helpful assistant, who saves output to artifact.

    output below line:
    "I am an ADK agent"

    Invoke  'save_content' tool now.
    """,
    tools=[save_content],
    output_key="agent_output",
    # after_agent_callback=save_content
)


# human_in_loop_agent = LlmAgent(
#     name="HumanInTheLoopAgent",
#     model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
#     include_contents="none",
#     # MODIFIED Instruction: More nuanced completion criteria, look for clear improvement paths.
#     instruction=f"""
#     You are a helpful assistant, who assists to colelct user feedback.

#     **Task:**
#     - Ask the user for their feedback on the generated data model - ```{{data_model}}```.
#     - *ALWAYS* invoke the 'user_feedback_capture_tool' tool as soon as you receive a user feedback.
#     - Do not output or ask anythin else to the user.
#     """,
#     description="Reviews the current draft, providing critique if clear improvements are needed, otherwise signals completion.",
#     tools=[user_feedback_capture_tool],
# )


# refiner_modeller_agent = LlmAgent(
#     name="RefinerModellerAgent",
#     model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
#     # Relies solely on state via placeholders
#     include_contents="none",
#     instruction=f"""You are an agent who can re-create a data model based on feedback.

#     **Current Data Model:**
#     {{data_model}}

#     **User feedback:**
#     {{hitl_feedback}}

#     **Task**
#     IF {{hitl_feedback}} *clearly states* that the user is satisfied with the current data model:
#     You MUST call the 'exit_loop' function. Do not output any text.

#     ELSE ({{hitl_feedback}} cotains actionable feedback):
#     Use the above two inputs and follow below instructions to *re-create* a data model based on user feedback:
#     {instructions_latest_loop}

#     Lastly, output your response.
#     """,
#     description="Refines the data model based on user feedback, or calls exit_loop if user indicates completion.",
#     tools=[exit_loop],
#     output_key="data_model",
# )

# modelling_loop_agent = LoopAgent(
#     name="modelling_process_loop_agent",
#     description="""Responsible for iteratively generating a data model until the user is satisfied""",
#     sub_agents=[human_in_loop_agent, refiner_modeller_agent],
#     max_iterations=2,
# )
