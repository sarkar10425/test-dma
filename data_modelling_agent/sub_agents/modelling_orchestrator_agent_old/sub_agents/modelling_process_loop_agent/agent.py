from google.adk.agents import LoopAgent, Agent

# from .sub_agents.modelling_task_agent.agent import modelling_task_agent
from .sub_agents.modeller_agent.agent import modeller_agent
from .checker_agent import checker_agent_instance
import os

modelling_process_loop_agent = LoopAgent(
    name="modelling_process_loop_agent",
    description="""Responsible for iteratively generating a data model until the user is satisfied""",
    sub_agents=[modeller_agent, checker_agent_instance],
    max_iterations=2,
)
# modelling_process_agent = Agent(
#     name="modelling_process_loop_agent",
#     model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash"),
#     description="""Responsible to run the provided sub-agent""",
#     instruction = "You are helpful assistant to invoke 'modelling_task_agent' sub-agent.",
#     sub_agents = [
#         modelling_task_agent,
#         # checker_agent_instance
#         ]
# )
