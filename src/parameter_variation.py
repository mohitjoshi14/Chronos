# parameter_variation.py
import json
import yaml
import os
import logging
from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field, ValidationError
from src.utils import load_prompt_from_file, select_llm_model

# Configure logging
os.makedirs('logs', exist_ok=True)

load_dotenv()

class ParameterVariation(BaseModel):
    scenario_description: str = Field(description="A brief, descriptive name or summary for this parameter variation scenario (e.g., 'Optimistic Productivity', 'High Investment Cost').")
    parameters: dict = Field(description="The dictionary of parameters for this specific variation. Only the 'value' of parameters should be changed, 'unit' must remain the same as the base model. Maintain the exact same parameter names as the base model.")

class ParameterVariationsOutput(BaseModel):
    variations: list[ParameterVariation] = Field(description="A list of distinct parameter variations for different scenarios.")

def generate_parameter_variations_with_llm(
    base_model_config: dict,
    num_variations: int,
    problem_statement: str,
    llm_for_generating_scenarios: dict = {'provider': 'google', 'model_name': 'gemini-2.0-flash', 'temperature': 0.5}
) -> list[ParameterVariation]: # Updated return type hint for clarity
    """
    Uses an LLM to generate multiple logical variations of model parameters.
    """
    llm = select_llm_model(llm_for_generating_scenarios)
    raw_json_parser = StrOutputParser()

    base_parameters = base_model_config.get('parameters', {})
    base_params_str = json.dumps(base_parameters, indent=2)

    example_json_output = json.dumps(
        ParameterVariationsOutput(
            variations=[
                ParameterVariation(
                    scenario_description='Example Scenario',
                    parameters={
                        'EXAMPLE_PARAM': {'value': 1.2, 'unit': 'ratio'}
                    }
                )
            ]
        ).model_dump(),
        indent=2
    )

    # Load the prompt messages from the YAML file
    prompt_directory = 'prompts'
    if not os.path.exists(prompt_directory):
        raise FileNotFoundError(f"Prompt directory not found: {prompt_directory}")
    prompt_file = os.path.join(prompt_directory, 'parameter_variation_prompt.yaml')
    prompt_messages = load_prompt_from_file(prompt_file)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_messages["system_message"]),
            ("human", prompt_messages["human_message"])
        ]
    )

    chain = prompt_template | llm | raw_json_parser

    print(f"\nGenerating {num_variations} parameter variations with LLM... This might take a moment.")
    raw_llm_output = ""
    try:
        raw_llm_output = chain.invoke({
            "problem_statement": problem_statement,
            "base_params_str": base_params_str,
            "num_variations": num_variations,
            "example_output_string": example_json_output
        })
        print("\nRaw LLM Output for Parameter Variations (for debugging):\n", raw_llm_output)

        json_start = raw_llm_output.find('{')
        json_end = raw_llm_output.rfind('}') + 1

        if json_start == -1 or json_end == -1:
            raise ValueError("No valid JSON object found in LLM output.")

        json_string = raw_llm_output[json_start:json_end]
        
        parsed_data = json.loads(json_string)

        validated_output = ParameterVariationsOutput.model_validate(parsed_data) # Changed .parse_obj() to .model_validate()
        
        print("\nParameter Variations Generated Successfully.")
        return validated_output.variations
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from LLM output: {e}")
        print(f"Problematic JSON string: {json_string[:500]}...")
        print("Raw LLM output causing error:\n", raw_llm_output)
        logging.error(f"Error decoding JSON from LLM output: {e}\nProblematic JSON string: {json_string[:500]}...\nRaw LLM output: {raw_llm_output}", exc_info=e)
        return []
    except ValidationError as e:
        print(f"Pydantic validation error for LLM output: {e}")
        print("Raw LLM output causing error:\n", raw_llm_output)
        logging.error(f"Pydantic validation error for LLM output: {e}\nRaw LLM output: {raw_llm_output}", exc_info=e)
        return []
    except ValueError as e:
        print(f"Content error in LLM output: {e}")
        print("Raw LLM output causing error:\n", raw_llm_output)
        logging.error(f"Content error in LLM output: {e}\nRaw LLM output: {raw_llm_output}", exc_info=e)
        return []
    except Exception as e:
        print(f"An unexpected error occurred during parameter variation generation: {e}")
        print("Raw LLM output causing error:\n", raw_llm_output)
        logging.error(f"Unexpected error during parameter variation generation: {e}\nRaw LLM output: {raw_llm_output}", exc_info=e)
        return []


if __name__ == "__main__":
    print("--- Testing Parameter Variation Module ---")

    dummy_base_model_config = {
        'parameters': {
            'BASE_PRICE': {'value': 1.0, 'unit': 'USD/unit'},
            'PRODUCTION_COST_PER_UNIT': {'value': 0.5, 'unit': 'USD/unit'},
            'INITIAL_DEMAND_FACTOR': {'value': 0.1, 'unit': 'units/customer/day'},
            'PRICE_SENSITIVITY': {'value': 0.5, 'unit': '1/USD'},
            'LOYALTY_IMPACT_ON_DEMAND': {'value': 0.2, 'unit': 'ratio'},
            'ADVERTISING_EFFECTIVENESS': {'value': 1e-05, 'unit': 'customers/USD'},
            'ADVERTISING_BUDGET_FRACTION': {'value': 0.1, 'unit': 'ratio'},
            'CUSTOMER_CHURN_RATE': {'value': 0.001, 'unit': '1/day'},
            'LOYALTY_REGAIN_RATE': {'value': 0.0001, 'unit': '1/day'},
            'PRODUCTION_CAPACITY': {'value': 1500000.0, 'unit': 'units/day'},
            'PRICE_INCREASE_MULTIPLIER': {'value': 2.0, 'unit': 'ratio'}
        }
    }
    
    test_num_variations = 3
    test_problem_statement = "What is the impact of Coca-Cola doubling their price?"

    variations = generate_parameter_variations_with_llm(
        dummy_base_model_config,
        test_num_variations,
        test_problem_statement
    )

    if variations:
        print("\n--- Generated Parameter Variations ---")
        for i, var in enumerate(variations):
            print(f"Scenario {i+1}: {var.scenario_description}") # Changed to dot notation
            print(json.dumps(var.parameters, indent=2)) # Changed to dot notation
            print("-" * 30)
    else:
        print("\nFailed to generate parameter variations.")