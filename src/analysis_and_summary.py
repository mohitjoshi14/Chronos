# analysis_and_summary.py
import pandas as pd
import numpy as np
import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

load_dotenv()

# Helper to convert NumPy types to Python native types recursively
def convert_to_python_native(obj):
    if isinstance(obj, (np.int64, np.int32, np.float64, np.float32)):
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
    time_unit: str
) -> str:
    """
    Uses an LLM (Gemini) to summarize the simulation results in natural language.
    Includes initial/final stock states, parameters, and their units for a more informed summary.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)

    summary_data = {}
    if not simulation_results_df.empty:
        # Extract initial and final stock values
        initial_full_state = simulation_results_df.iloc[0].to_dict()
        final_full_state = simulation_results_df.iloc[-1].to_dict()

        initial_stock_state = {name: initial_full_state[name] for name in stock_names if name in initial_full_state}
        final_stock_state = {name: final_full_state[name] for name in stock_names if name in final_full_state}

        # --- Display Initial and Final States (for console output) ---
        print("\n--- Initial State of Stocks and Parameters ---")
        for stock_name, value in initial_stock_state.items():
            unit = component_units.get(stock_name, "units")
            print(f"  {stock_name}: {value:.2f} {unit}")
        print("\n--- Initial Parameters ---")
        for param_name, param_details in model_parameters.items():
            value = param_details['value'] if isinstance(param_details, dict) and 'value' in param_details else param_details
            unit = param_details['unit'] if isinstance(param_details, dict) and 'unit' in param_details else "dimensionless"
            print(f"  {param_name}: {value} {unit}")

        print("\n--- Final State of Stocks ---")
        for stock_name, value in final_stock_state.items():
            unit = component_units.get(stock_name, "units")
            print(f"  {stock_name}: {value:.2f} {unit}")
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


    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are an expert system dynamics analyst. Analyze the provided simulation data and context. "
             "Summarize the key findings, trends, and impacts in clear, concise natural language. "
             "Crucially, **incorporate the units of measurement** for all values (stocks, parameters, flows, auxiliaries, time) when discussing them. "
             "Refer back to the original problem statement and explain how the simulation addresses it. "
             "Highlight the most significant changes and implications, particularly focusing on how stock levels (like capital and product inventories) change over time and how parameters influenced these changes. "
             "Consider initial states, final states, and overall trends. Focus on the core dynamics and value capture aspects."
             "Present the summary in well-structured paragraphs, using bullet points for key data points if appropriate."
            ),
            ("human",
             "Original Problem: {problem_statement}\n\n"
             "Simulation Data Summary (including initial and final stock states, parameters, and trends, all with units):\n{summary_data}\n\n"
             "Based on this, what are the key findings and implications?"
            )
        ]
    )

    chain = prompt_template | llm | StrOutputParser()

    print("\nSummarizing simulation results with LLM...")
    try:
        response = chain.invoke({"problem_statement": problem_statement, "summary_data": json.dumps(summary_data, indent=2)})
        print("\nLLM Summary Generated Successfully.")
        return response
    except Exception as e:
        logging.error(f"Error summarizing results with LLM: {e}")
        return "Failed to generate summary."

# NEW FUNCTION: For final meta-summary of multiple runs
def generate_final_summary_with_llm(problem_statement: str, all_individual_summaries: list[dict]) -> str:
    """
    Uses an LLM (Gemini) to synthesize a final summary from multiple individual simulation summaries.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7) # Higher temperature for more creative synthesis
    parser = StrOutputParser()

    # Create a string representation of all summaries for the LLM
    summaries_str = ""
    for i, summary in enumerate(all_individual_summaries):
        summaries_str += f"--- Scenario {i+1}: {summary.get('scenario_description', 'No description')}\n"
        summaries_str += f"{summary['summary_text']}\n\n" # Assuming 'summary_text' holds the individual LLM summary

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are an expert in comparative analysis of system dynamics simulations. "
             "Your task is to synthesize a comprehensive summary from multiple individual simulation summaries. "
             "Each individual summary represents a scenario based on different parameter assumptions. "
             "Analyze how varying initial conditions and parameters impacted the simulation outcomes. "
             "Compare and contrast the scenarios, highlighting the most significant changes in stock levels, "
             "trends of auxiliaries and flows, and overall implications. "
             "Focus on insights relevant to the original problem statement. "
             "Ensure you discuss the impact of the *specific parameter changes* for each scenario. "
             "Retain units for all values mentioned in the summary. "
             "Present the final summary in a well-structured report format with an introduction, "
             "a comparison of scenarios, and a conclusion with key takeaways."
            ),
            ("human",
             "Original Problem Statement: {problem_statement}\n\n"
             "Individual Simulation Summaries:\n{summaries_str}\n\n"
             "Please provide a final comprehensive summary and comparative analysis."
            )
        ]
    )

    chain = prompt_template | llm | parser

    print("\nGenerating final comprehensive summary with LLM...")
    try:
        response = chain.invoke({"problem_statement": problem_statement, "summaries_str": summaries_str})
        print("\nFinal LLM Summary Generated Successfully.")
        return response
    except Exception as e:
        logging.error(f"Error generating final summary with LLM: {e}")
        return "Failed to generate final summary."