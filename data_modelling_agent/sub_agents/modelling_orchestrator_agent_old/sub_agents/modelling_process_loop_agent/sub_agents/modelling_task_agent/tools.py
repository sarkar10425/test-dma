from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from .const import config
import os
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

# from .agent import modelling_task_agent
# from .const import config, DDL_TASK, BQ_METADATA_TASK, BQ_LOGICAL_MODEL_TASK, BASE_MODEL_TASK, LDM_TASK, PDM_TASK
# import datetime
# from pathlib import Path
# from modelling_orchestrator_agent.utils import del_dir, save_artifacts
# from data_modelling_agent.sub_agents.reporting_agent.utils.commons import cleanup_metadata
# from data_modelling_agent.sub_agents.reporting_agent.tools import generate_report
from google import genai
import os


def user_feedback_sentiment_tool(
    # callback_context: CallbackContext,
    tool_context: ToolContext,
    # llm_response: LlmResponse
):
    print("Executing user_feedback_sentiment_tool()")
    current_state = tool_context.state
    events = tool_context._invocation_context.session.events
    user_search_google_phrases = [
        "i am good",
        "confirm",
        "save",
        "finalize",
        "finalise",
    ]
    # logic to check sentiment of users response
    for ev in events:
        if ev.content:
            if ev.content.role:
                if ev.content.role == "user":
                    for part in ev.content.parts:
                        for phrase in user_search_google_phrases:
                            if phrase in part.text:
                                # logic to get user sentiment
                                # TBA
                                client = genai.Client()
                                response = client.models.generate_content(
                                    model="gemini-2.5-flash",
                                    contents=f"""
                                            You are an intelligent assistant who can analyse user's text.
                                            You will be provided a user text
                                            If you find that the user is suggesting that they are satisfied by using any phrases from - {user_search_google_phrases}, then you **must** output 'True' as your output. You **must** not output anything else.
                                            If you find that the user is not suggesting by any means that they are satisfied, then you should output the **exact** User text
                                            User text:
                                            {part.text}
                                            """,
                                )
                                if (
                                    response.text == "True"
                                    or response.text == True
                                    or response.text == "true"
                                ):
                                    current_state["loop_exit_cue"] = True
                                    current_state["hitl_feedback"] = ""
                                else:
                                    current_state["loop_exit_cue"] = False
                                    current_state["hitl_feedback"] = part.text
    return


# async def call_modelling_agent(
#     question: str,
#     tool_context: ToolContext,
# ):
#     """Tool to call modeller_agent."""

#     #This will change to active persona in future. For now we are just performing all tasks
#     tasks = config["output_personas"]["all"]
#     folder_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#     Path(folder_name).mkdir()
#     tool_output = {}
#     for task in tasks:
#         tool_context.state["current_task"] = task
#         agent_tool = AgentTool(agent=modelling_task_agent)
#         modeller_agent_output = await agent_tool.run_async(
#             args={"request": question}, tool_context=tool_context
#         )
#         print(task,"\n", modeller_agent_output)
#         save_artifacts(task, modeller_agent_output, folder_name)
#         if task == DDL_TASK:
#             tool_context.state["ddl"] = modeller_agent_output
#         if task == BQ_METADATA_TASK:
#             tool_context.state["metadata"] = cleanup_metadata(modeller_agent_output)
#         if task == BQ_LOGICAL_MODEL_TASK:
#             tool_output["summary"] = modeller_agent_output
#         if task == BASE_MODEL_TASK:
#             tool_context.state["base_data_model"] = modeller_agent_output
#         if task == LDM_TASK:
#             tool_context.state["logical_data_model"] = modeller_agent_output
#         if task == PDM_TASK:
#             tool_context.state["physical_data_model"] = modeller_agent_output
#     tool_context.state["gcs_folder"] = folder_name
#     tool_output["gcs_folder"] = folder_name
#     tool_output["project_id"] = os.getenv("GOOGLE_CLOUD_PROJECT", default="deid-sandbox")
#     tool_context.state["project_id"] = os.getenv("GOOGLE_CLOUD_PROJECT", default="deid-sandbox")
#     del_dir(folder_name)
#     return tool_output
