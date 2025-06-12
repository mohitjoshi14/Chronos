# analysis_and_summary.py
import pandas as pd
import numpy as np
import json
import os
from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging
from src.utils import load_prompt_from_file, select_llm_model

load_dotenv()

logger = logging.getLogger(__name__)

# Helper to convert NumPy types to Python native types recursively
def convert_to_python_native(obj):
    numpy_scalar_types = (np.integer, np.floating)
    if isinstance(obj, numpy_scalar_types):
        return obj.item() # Convert NumPy scalar to Python int/float
    if isinstance(obj, dict):
        return {k: convert_to_python_native(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_to_python_native(elem) for elem in obj]
    return obj

def summarize_simulation_results_with_llm(
    problem_statement: str,
    simulation_results_df: pd.DataFrame,
    model_parameters: dict,
    stock_names: list,
    component_units: dict,
    time_unit: str,
    llm_for_simulation_analysis: dict = {'provider': 'google', 'model_name': 'gemini-2.0-flash', 'temperature': 0.5},
    verbose: bool = False
) -> str:
    """
    Uses an LLM (Gemini) to summarize the simulation results in natural language.
    Includes initial/final stock states, parameters, and their units for a more informed summary.
    """
    llm = select_llm_model(llm_for_simulation_analysis)

    summary_data = {}
    if not simulation_results_df.empty:
        # Extract initial and final stock values
        initial_full_state = simulation_results_df.iloc[0].to_dict()
        final_full_state = simulation_results_df.iloc[-1].to_dict()

        initial_stock_state = {name: initial_full_state[name] for name in stock_names if name in initial_full_state}
        final_stock_state = {name: final_full_state[name] for name in stock_names if name in final_full_state}

        # --- Display Initial and Final States (for console output) ---
        if verbose:
            print("\n--- Initial State of Stocks and Parameters ---")
        for stock_name, value in initial_stock_state.items():
            unit = component_units.get(stock_name, "units")
            if verbose:
                print(f"  {stock_name}: {value:.2f} {unit}")
        if verbose:
            print("\n--- Initial Parameters ---")
        for param_name, param_details in model_parameters.items():
            value = param_details['value'] if isinstance(param_details, dict) and 'value' in param_details else param_details
            unit = param_details['unit'] if isinstance(param_details, dict) and 'unit' in param_details else "dimensionless"
            if verbose:
                print(f"  {param_name}: {value} {unit}")
        if verbose:
            print("\n--- Final State of Stocks ---")
        for stock_name, value in final_stock_state.items():
            unit = component_units.get(stock_name, "units")
            if verbose:
                print(f"  {stock_name}: {value:.2f} {unit}")
        if verbose:
            print("----------------------------------------------")
        # --- End Display ---


        # Populate summary_data for LLM (ensuring native Python types and including units)
        llm_parameters_with_units = {
            name: {
                "value": convert_to_python_native(details['value']) if isinstance(details, dict) and 'value' in details else convert_to_python_native(details),
                "unit": details['unit'] if isinstance(details, dict) and 'unit' in details else "dimensionless"
            } for name, details in model_parameters.items()
        }

        llm_initial_stock_state = {
            name: {
                "value": convert_to_python_native(value),
                "unit": component_units.get(name, "units")
            } for name, value in initial_stock_state.items()
        }
        llm_final_stock_state = {
            name: {
                "value": convert_to_python_native(value),
                "unit": component_units.get(name, "units")
            } for name, value in final_stock_state.items()
        }

        summary_data["model_parameters"] = llm_parameters_with_units
        summary_data["initial_stock_state"] = llm_initial_stock_state
        summary_data["final_stock_state"] = llm_final_stock_state

        summary_data["problem_statement"] = problem_statement
        summary_data["simulation_duration"] = {
            "value": convert_to_python_native(simulation_results_df['time'].max()),
            "unit": time_unit
        }

        for col in simulation_results_df.columns:
            if col != 'time':
                col_unit = component_units.get(col, "unknown_unit")
                summary_data[f"{col}_min"] = {"value": convert_to_python_native(simulation_results_df[col].min()), "unit": col_unit}
                summary_data[f"{col}_max"] = {"value": convert_to_python_native(simulation_results_df[col].max()), "unit": col_unit}
                if simulation_results_df[col].iloc[0] < simulation_results_df[col].iloc[-1]:
                    summary_data[f"{col}_trend"] = "increased"
                elif simulation_results_df[col].iloc[0] > simulation_results_df[col].iloc[-1]:
                    summary_data[f"{col}_trend"] = "decreased"
                else:
                    summary_data[f"{col}_trend"] = "remained stable"
    else:
        summary_data = {
            "problem_statement": problem_statement,
            "message": "Simulation results DataFrame was empty."
        }


    # Load the prompt messages from the YAML file
    prompt_directory = 'prompts'
    if not os.path.exists(prompt_directory):
        raise FileNotFoundError(f"Prompt directory not found: {prompt_directory}")
    prompt_file = os.path.join(prompt_directory, 'sim_analysis_prompt.yaml')
    prompt_messages = load_prompt_from_file(prompt_file)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_messages["system_message"]),
            ("human", prompt_messages["human_message"])
        ]
    )

    chain = prompt_template | llm | StrOutputParser()

    if verbose:
        print("\nSummarizing simulation results with LLM...")
    try:
        response = chain.invoke({"problem_statement": problem_statement, "summary_data": json.dumps(summary_data, indent=2)})
        if verbose:
            print("\nLLM Summary Generated Successfully.")
        return response
    except Exception as e:
        logger.error(f"Error summarizing results with LLM: {e}")
        return "Failed to generate summary."

# For final meta-summary of multiple runs
def generate_final_summary_with_llm(problem_statement: str, 
                                    all_individual_summaries: list[dict],
                                    llm_for_summarization: dict = {'provider': 'google', 'model_name': 'gemini-2.0-flash', 'temperature': 0.7},
                                    verbose: bool = False) -> str:
    """
    Uses an LLM (Gemini) to synthesize a final summary from multiple individual simulation summaries.
    """
    llm = select_llm_model(llm_for_summarization)
    # llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7) # Higher temperature for more creative synthesis
    parser = StrOutputParser()

    # Create a string representation of all summaries for the LLM
    summaries_str = ""
    for i, summary in enumerate(all_individual_summaries):
        summaries_str += f"--- Scenario {i+1}: {summary.get('scenario_description', 'No description')}\n"
        summaries_str += f"{summary['summary_text']}\n\n" # Assuming 'summary_text' holds the individual LLM summary

    # Load the prompt messages from the YAML file
    prompt_directory = 'prompts'
    if not os.path.exists(prompt_directory):
        raise FileNotFoundError(f"Prompt directory not found: {prompt_directory}")    
    prompt_file = os.path.join(prompt_directory, 'final_sim_analysis_prompt.yaml')
    prompt_messages = load_prompt_from_file(prompt_file)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_messages["system_message"]),
            ("human", prompt_messages["human_message"])
        ]
    )

    chain = prompt_template | llm | parser

    if verbose:
        print("\nGenerating final comprehensive summary with LLM...")
    try:
        response = chain.invoke({"problem_statement": problem_statement, "summaries_str": summaries_str})
        if verbose:
            print("\nFinal LLM Summary Generated Successfully.")
        return response
    except Exception as e:
        logger.error(f"Error generating final summary with LLM: {e}")
        return "Failed to generate final summary."