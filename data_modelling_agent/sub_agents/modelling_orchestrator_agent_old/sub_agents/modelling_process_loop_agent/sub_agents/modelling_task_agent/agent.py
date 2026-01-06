# import os
# from google.adk.agents import Agent
# # from google.adk.agents.callback_context import CallbackContext
# from .tools import user_feedback_sentiment_tool
# # from modelling_orchestrator_agent.sub_agents.modeller_agent.tools import call_modeller_agent
# # from ..modeller_agent.tools import call_modeller_agent
# from ..modeller_agent.agent import modeller_agent


# modelling_task_agent = Agent(
#     name="modelling_task_agent",
#     model="gemini-2.5-flash",
#    instruction=f"""
#    You are an intelligent assistant who invokes 'modeller_agent' sub-agent when user provides a feedback.
#    Use 'user_feedback_sentiment_tool' tool to analyze the user feedback and re-create data model by taking **both** {{hitl_feedback}} & {{data_model}} context variables as input.
#    """,
#    description="You are an assistant who re-creates a data model based on user's feedback",
#    output_key = "modeller_agent_output",
#    sub_agents = [modeller_agent],
#    tools = [user_feedback_sentiment_tool],
# #    before_agent_callback = call_modeller_agent
# )
