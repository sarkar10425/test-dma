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

"""Top level agent for Bigquery modelling  multi-agents.

-- It gets the prompt from the user and passes to the suitable agent.
"""
import os
import json
from datetime import date

from google.genai import types
from typing import Optional
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from .const import (
    KIND_OF_ACTIVITY_STATE_LBL,
    KIND_OF_ACTIVITY_ALLOWED_VALS,
    INITIALIZATION_INSTRUCTION_ACTIVITY,
    KIND_OF_ACTIVITY_PREVIOUS,
    KIND_OF_ACTIVITY_START_FRESH,
    INITIALIZATION_INSTRUCTION_PARAMS,
    INITIALIZATION_INSTRUCTION_ACTIVITY,
    SAMPLE_PROMPTS,
)
from .utils.commons import get_params_from_msg
from merlin.sub_agents.ddl_agent.utils.commons import get_ddl_from_gcs
from merlin.sub_agents.ddl_agent.utils.bq import cleanup_ddl
from merlin.sub_agents.synthetic_data_generator_agent.utils.commons import (
    get_metadata_from_gcs,
)
from .sub_agents import (
    search_agent,
    ddl_agent,
    synthetic_data_generator_agent,
    reporting_agent,
    dml_agent,
)

# from .sub_agents.metadata_agent.agent import sql_queries_agent
from .sub_agents.modelling_orchestrator_agent.agent import modelling_orchestrator_agent
from google.adk.agents.callback_context import CallbackContext

from .prompts import AGENT_INTRODUCTION, AGENT_INTRODUCTION_MINIFIED


def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:

    kind_of_activity = callback_context.state.get(KIND_OF_ACTIVITY_STATE_LBL, None)
    print("kind_of_activity", kind_of_activity)
    if kind_of_activity == KIND_OF_ACTIVITY_START_FRESH:
        return None
    else:
        # Inspect the last user message in the request contents
        last_user_message = ""
        if llm_request.contents and llm_request.contents[-1].role == "user":
            if llm_request.contents[-1].parts:
                last_user_message = llm_request.contents[-1].parts[0].text
        print("last_user_message", last_user_message)
        if kind_of_activity == None:
            if (
                last_user_message.lower().strip() == KIND_OF_ACTIVITY_START_FRESH
                or "fresh" in last_user_message.lower().strip()
            ):
                callback_context.state[KIND_OF_ACTIVITY_STATE_LBL] = (
                    KIND_OF_ACTIVITY_START_FRESH
                )
                return None
            elif (
                last_user_message.lower().strip() == KIND_OF_ACTIVITY_PREVIOUS
                or "prev" in last_user_message.lower().strip()
            ):
                callback_context.state[KIND_OF_ACTIVITY_STATE_LBL] = (
                    KIND_OF_ACTIVITY_PREVIOUS
                )
                project_id, dataset_id, gcs_folder = get_params_from_msg(
                    last_user_message
                )
                if (
                    project_id in [None, ""]
                    or dataset_id in [None, ""]
                    or gcs_folder in [None, ""]
                ):
                    return LlmResponse(
                        content=types.Content(
                            role="model",
                            parts=[types.Part(text=INITIALIZATION_INSTRUCTION_PARAMS)],
                        )
                    )
            else:
                return LlmResponse(
                    content=types.Content(
                        role="model",
                        parts=[
                            types.Part(
                                text=f"{AGENT_INTRODUCTION_MINIFIED}\n\n{INITIALIZATION_INSTRUCTION_ACTIVITY}"
                            )
                        ],
                    )
                )
        elif kind_of_activity == KIND_OF_ACTIVITY_PREVIOUS:
            project_id, dataset_id, gcs_folder = get_params_from_msg(last_user_message)
            callback_context.state["project_id"] = project_id
            callback_context.state["dataset_id"] = dataset_id
            callback_context.state["gcs_folder"] = gcs_folder
            callback_context.state["ddl"] = cleanup_ddl(
                get_ddl_from_gcs(gcs_folder), project_id, dataset_id
            )
            callback_context.state["metadata"] = get_metadata_from_gcs(gcs_folder)
            os.environ["BQ_DATA_PROJECT_ID"] = project_id
            os.environ["BQ_DATA_PROJECT_ID"] = project_id
            os.environ["BQ_COMPUTE_PROJECT_ID"] = project_id

            os.environ["BQ_DATASET_ID"] = dataset_id
        else:
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=INITIALIZATION_INSTRUCTION_ACTIVITY)],
                )
            )


date_today = date.today()


root_agent = Agent(
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    name="data_modelling_agent",
    description=AGENT_INTRODUCTION_MINIFIED,
    instruction=f"""You are a master orchestrator for a BigQuery Modelling Multi-Agent System. Your primary responsibility is to analyze the user's request and delegate it to the correct specialist agent based on the user's intent.
    **Agent Routing Guide:**
    *Primary agent:*
    - **`modelling_orchestrator_agent`**: Use it to start new data model creation process.
    - **`reporting_agent`**: Use for requests to create reports, charts and diagrams.

    *Secondary agents: To be used once `modelling_orchestrator_agent` has finished execution*
    - **`ddl_agent`**: Use it to **execute** DDLs for *newly generated data model* by `modelling_orchestrator_agent` agent.
    - **`synthetic_data_generator_agent`**: Use it to generate synthetic or sample data once new model tables are created on destination data warehouse.
    - **`dml_agent`**: Use it to execute SQL queries to calculate metrics and KPIs.

    
    **TASK:**
        You must follow these rules:
            1. When the User is asked on {INITIALIZATION_INSTRUCTION_ACTIVITY}.
            2. Then you must append these {SAMPLE_PROMPTS} sample prompts to the reponse of the user.
            3. If user replies with yes, invoke `modelling_orchestrator_agent` agent to start creating new data model

    **Strict Rules:**
    1.  You **MUST** delegate the task to exactly **ONE** agent.
    2.  You **MUST NOT** generate final answers yourself. Your main job is to route.
    3.  You **MUST NOT** ask user for any inputs.
    4.  If an agent returns an error, you must retry from beginning after sending clear message to user.
""",
    global_instruction=(
        f"""
        You are a BigQuery Modelling Multi Agent System.
        Todays date: {date_today}
        """
    ),
    sub_agents=[
        modelling_orchestrator_agent,
        ddl_agent,
        synthetic_data_generator_agent,
        reporting_agent,
        dml_agent,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
    before_model_callback=before_model_callback,
)
