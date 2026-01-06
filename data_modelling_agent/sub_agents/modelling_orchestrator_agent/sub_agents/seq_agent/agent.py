from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from ..modeller_agent.agent import modeller_agent
from ..modeller_loop_agent.agent import modelling_loop_agent


# modelling_agent = SequentialAgent(
#     name="ModellingAgent",
#     sub_agents=[
#         modeller_agent, # Run first to create initial model
#         modelling_loop_agent       # Then run the re-creation model with HITL in a loop until user is satisfied
#     ],
#     description="Creates an initial data model and then iteratively refines it with human-in-the-loop feedback.",
# )
