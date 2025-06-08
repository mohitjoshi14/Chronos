# model_generation.py
import json
import yaml
import os
import logging
from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from src.utils import load_prompt_from_file, select_llm_model
from typing import Optional

# Load environment variables (like GOOGLE_API_KEY)
load_dotenv()

# --- Pydantic Schemas for LLM Output ---

class StockDefinition(BaseModel):
    name: str = Field(description="Unique name of the stock. Use CamelCase. Examples: 'FarmerCapital', 'DistributorProductInventory'.")
    initial_value: float = Field(description="Initial numerical value of the stock.")
    unit: str = Field(description="Unit of measurement for the stock. E.g., 'USD', 'units', 'customers'.")

class ParameterDefinition(BaseModel):
    value: float = Field(description="Numerical value of the parameter.")
    unit: str = Field(description="Unit of measurement for the parameter. E.g., 'USD/unit', 'ratio', 'days'.")

class AuxiliaryDefinition(BaseModel):
    name: str = Field(description="Unique name of the auxiliary variable. Use CamelCase. Examples: 'EffectiveSellingPrice', 'DemandRate'.")
    formula: str = Field(description="Python expression as a string. Can reference stock names, other auxiliary names, or parameter names (using their 'value'). E.g., 'StockA * PARAM_B.value'.")
    unit: str = Field(description="Unit of measurement for the auxiliary. E.g., 'USD/unit', 'units/day', 'ratio'.")

class FlowDefinition(BaseModel):
    name: str = Field(description="Unique name of the flow. Use CamelCase. Examples: 'ProductProductionRate', 'CapitalTransferToDistributor'.")
    formula: str = Field(description="Python expression as a string. Can reference stock names, auxiliary names, or parameter names (using their 'value'). Must be non-negative, so use 'max(0, ...)' around the entire expression. E.g., 'max(0, ProductInventory * DemandFactor)'.")
    unit: str = Field(description="Unit of measurement for the flow. This should be 'stock_unit/time_unit'. E.g., 'units/day', 'USD/month'.")

class FlowConnection(BaseModel):
    flow_name: str = Field(description="Name of the flow.")
    stock_name: str = Field(description="Name of the stock.")
    direction: str = Field(description="Direction of flow, either 'inflow' or 'outflow'.")

class SimulationTimeSetting(BaseModel):
    value: float = Field(description="Value for the time setting.")
    unit: str = Field(description="Unit of measurement for the time setting. E.g., 'days', 'weeks', 'months', 'years'.")

class SimulationSettings(BaseModel):
    end_time: SimulationTimeSetting = Field(description="Total simulation duration.")
    dt: SimulationTimeSetting = Field(description="Time step size for the simulation.")

class ModelConfig(BaseModel):
    stocks: list[StockDefinition] = Field(description="List of stocks in the system. Ensure all key stakeholders (e.g., Company, Customer) have explicit stocks for their capital/money and relevant product/resource inventories. All must have a 'unit'.")
    parameters: dict[str, ParameterDefinition] = Field(description="Dictionary of parameters (constants) used in formulas. Each parameter must be a dictionary with 'value' and 'unit'.")
    auxiliaries: list[AuxiliaryDefinition] = Field(description="List of auxiliary variables (converters) in the system. These define decision rules, influencing factors like prices, bargaining power, market conditions, and calculated rates based on stocks or other auxiliaries. All must have a 'unit'.")
    flows: list[FlowDefinition] = Field(description="List of flows (rates of change) in the system. Flows represent the movement of resources (money, product, customers, etc.) between stocks. Ensure corresponding inflows and outflows for transfers between entities. All must have a 'unit'.")
    flow_connections: list[list[str]] = Field(description="List of flow connections. Each item is a list: [flow_name, stock_name, direction ('inflow' or 'outflow')].")
    simulation_settings: SimulationSettings = Field(description="Settings for the simulation run. 'end_time' and 'dt' must have a 'value' and 'unit'.")
    problem_description: str = Field(description="The original problem statement provided by the user.")


def generate_model_config_with_llm(problem_statement: str,
                                   llm_for_generating_system_model: dict) -> Optional[dict]:
    """
    Generates a model configuration using an LLM based on the provided problem statement.
    """
    llm = select_llm_model(llm_for_generating_system_model)
    parser = JsonOutputParser(pydantic_object=ModelConfig)

    # Load the prompt messages from the YAML file
    prompt_directory = 'prompts'
    if not os.path.exists(prompt_directory):
        raise FileNotFoundError(f"Prompt directory not found: {prompt_directory}")
    prompt_file = os.path.join(prompt_directory, 'model_generation_prompt.yaml')
    prompt_messages = load_prompt_from_file(prompt_file)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_messages["system_message"]),
            ("human", prompt_messages["human_message"])
        ]
    )

    chain = prompt_template | llm | parser

    print("Generating model configuration with LLM... This might take a moment.")
    try:
        response = chain.invoke({"problem_statement": problem_statement, "format_instructions": parser.get_format_instructions()})
        print("\nLLM Model Configuration Generated Successfully.")
        return response
    except Exception as e:
        logging.error(f"Error generating model config with LLM: {e}")
        print(f"Error generating model config with LLM. Check logs/error.log for details.")
        return None