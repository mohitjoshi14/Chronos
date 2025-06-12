# orchestrator.py
import json
import copy
import datetime
import pandas as pd
import os # Make sure os module is imported
from dotenv import load_dotenv
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import components from their new modules
from src.simulation_core import System
from src.model_generation import generate_model_config_with_llm
from src.analysis_and_summary import summarize_simulation_results_with_llm, generate_final_summary_with_llm
from src.parameter_variation import generate_parameter_variations_with_llm
from src.generate_diagrams import generate_model_diagram

# Set up logging to file in logs directory
os.makedirs('logs', exist_ok=True)
# Create a unique error log file for each run
error_log_filename = os.path.join('logs', f"error_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=error_log_filename,
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(message)s'
)

load_dotenv() # Ensure env variables are loaded for all modules

def _run_simulation_and_summarize(scenario_description, current_model_config, problem_statement, llm_for_simulation_analysis, verbose):
    try:
        sim_system = System(current_model_config)
        end_time_value = current_model_config.get('simulation_settings', {}).get('end_time', {}).get('value', 100)
        time_unit = current_model_config.get('simulation_settings', {}).get('end_time', {}).get('unit', 'days')
        simulation_results = sim_system.run_simulation(end_time=end_time_value)
        if verbose:
            print(f"Simulation for '{scenario_description}' completed successfully.")
            print("### Raw Simulation Data (First 5 and Last 5 Rows):")
            if not simulation_results.empty:
                print(simulation_results.head().to_markdown(index=False))
                print("...")
                print(simulation_results.tail().to_markdown(index=False))
            else:
                print("No simulation data generated.\n")
        stock_names = [s['name'] for s in current_model_config.get('stocks', [])]
        individual_summary_text = summarize_simulation_results_with_llm(
            problem_statement,
            simulation_results,
            model_parameters=sim_system.parameters,
            stock_names=stock_names,
            component_units=sim_system.component_units,
            time_unit=time_unit,
            llm_for_simulation_analysis=llm_for_simulation_analysis,
            verbose=verbose
        )
        if verbose:
            print(f"\n--- AI Summary for Scenario: {scenario_description} ---")
            print(individual_summary_text)
            print("---------------------------------------------------\n")
            print("### AI Generated Summary:")
            print(individual_summary_text + "\n")
        return {
            "scenario_description": scenario_description,
            "summary_text": individual_summary_text,
            "simulation_results": simulation_results
        }
    except Exception as e:
        error_message = f"Error during simulation for '{scenario_description}': {e}"
        if verbose:
            print(f"Error encountered: {error_message}")
            print(f"### Simulation Error:")
            print(f"{error_message}\n")
        logging.error(error_message, exc_info=e)
        if isinstance(e, ValueError) and ("Error calculating" in str(e)):
            if verbose:
                print("Please review the generated model configuration, especially the formulas, for correctness.\n")
        return {
            "scenario_description": scenario_description,
            "summary_text": f"Simulation failed with error: {e}",
            "simulation_results": None
        }

async def run_analysis(
        problem_statement: str,
        num_variations: int = 1,
        output_directory: str = "output",
        llm_for_generating_system_model: dict = {},
        llm_for_generating_scenarios: dict = {},
        llm_for_simulation_analysis: dict = {},
        llm_for_summarization: dict = {},
        verbose: bool = False
    ) -> tuple[str, str]:
    """
    Main function to orchestrate the entire process:
    1. Get problem statement from user.
    2. Generate base model config using LLM.
    3. Generate multiple parameter variations using another LLM.
    4. Run simulation for each variation.
    5. Summarize results for each variation using LLM.
    6. Generate a final comprehensive summary if multiple variations were run.
    """
    if verbose:
        print("--- System Dynamics Model Generation and Analysis ---")
    # Step 1: Get problem statement from user if not provided
    if problem_statement is None:
        if verbose:
            print("Problem statement cannot be empty. Exiting.")
        logging.error("Problem statement cannot be empty. Exiting.")
        return
    else:
        if verbose:
            print(f"Using provided problem statement: {problem_statement}")
        if num_variations < 1:
            if verbose:
                print("Number of variations must be at least 1. Setting to 1.")
            num_variations = 1

    os.makedirs(output_directory, exist_ok=True) # exist_ok=True prevents error if directory already exists
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Remove all file writing logic. Only print to console and keep data in memory.
    if verbose:
        print(f"# System Dynamics Model Analysis\n")
        print(f"**Problem Statement:** {problem_statement}\n")
        print(f"**Analysis Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"--- Number of Requested Scenarios: {num_variations} ---\n")

    # Step 2: AI generates base model configuration
    if verbose:
        print("\nGenerating base model configuration with LLM... This might take a moment.")
        print("## Base Model Configuration Generation\n")
        print("Generating base model configuration with LLM...\n")

    base_model_config = generate_model_config_with_llm(problem_statement, llm_for_generating_system_model, verbose=verbose)

    if base_model_config is None:
        if verbose:
            print("Failed to generate a valid base model configuration. Exiting.")
        logging.error("Failed to generate a valid base model configuration.")
        return

    base_model_diagram = generate_model_diagram(base_model_config)

    if verbose:
        print("Base Model Configuration Generated Successfully.")
        print("Base Model Configuration Generated Successfully.\n")
        print("### Base Model Configuration JSON:")
        print(json.dumps(base_model_config, indent=2))
        print("\n--- Base Model Configuration (JSON) ---\n", json.dumps(base_model_config, indent=2), "\n-------------------------------------------\n")

    all_scenarios_to_run = []
    all_scenarios_to_run.append({
        "scenario_description": "Base Case Scenario",
        "model_config": base_model_config
    })

    # Step 3: Generate multiple parameter variations if requested
    if num_variations > 1:
        if verbose:
            print("## Parameter Variation Generation\n")
            print("Generating additional parameter variations with LLM...")
            print(f"Requesting {num_variations - 1} additional parameter variations...\n")
        additional_variations = generate_parameter_variations_with_llm(
            base_model_config=base_model_config,
            num_variations=(num_variations - 1),
            problem_statement=problem_statement,
            llm_for_generating_scenarios=llm_for_generating_scenarios,
            verbose=verbose
        )

        if not additional_variations:
            if verbose:
                print("No additional parameter variations generated. Running only base case.")
            logging.error("No additional parameter variations generated by LLM.")
        else:
            if verbose:
                print(f"Successfully generated {len(additional_variations)} additional parameter variations.\n")
            for var in additional_variations:
                scenario_config = copy.deepcopy(base_model_config)
                scenario_config['parameters'] = var.parameters
                all_scenarios_to_run.append({
                    "scenario_description": var.scenario_description,
                    "model_config": scenario_config
                })

    if verbose:
        print(f"--- Running {len(all_scenarios_to_run)} Scenarios ---\n")
    all_individual_summaries = []
    all_simulation_results = []

    async def run_all_scenarios():
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            tasks = [
                loop.run_in_executor(
                    executor,
                    _run_simulation_and_summarize,
                    scenario['scenario_description'],
                    scenario['model_config'],
                    problem_statement,
                    llm_for_simulation_analysis,
                    verbose
                )
                for scenario in all_scenarios_to_run
            ]
            return await asyncio.gather(*tasks)

    scenario_results = await run_all_scenarios()
    for result in scenario_results:
        all_individual_summaries.append({
            "scenario_description": result["scenario_description"],
            "summary_text": result["summary_text"]
        })
        if result["simulation_results"] is not None:
            all_simulation_results.append({
                "scenario_description": result["scenario_description"],
                "simulation_results": result["simulation_results"]
            })
        if verbose:
            print("---\n") # Separator between scenarios

    # Step 6: Generate final comprehensive summary if multiple variations were run
    final_summary = ""
    if verbose:
        print("# Final Comprehensive Analysis Conclusion\n")
    if num_variations > 1 and len(all_individual_summaries) > 1: # Only run if more than one successful scenario
        final_summary = generate_final_summary_with_llm(
            problem_statement,
            all_individual_summaries,
            llm_for_summarization=llm_for_summarization,
            verbose=verbose
        )
        if verbose:
            print("\n--- Final Comprehensive AI Summary of All Scenarios ---")
            print(final_summary)
            print("-------------------------------------------------------\n")
            print(final_summary + "\n")
    elif num_variations == 1:
        if verbose:
            print("\nOnly one scenario was run. No comparative summary generated.")
            print("Only one scenario was run, so no comparative summary was generated. The summary for the base case is provided above.\n")
    else:
        if verbose:
            print("\nNo successful scenarios to compare. Skipping final summary.")
            print("No successful scenarios were completed for comparison. Skipping final summary generation.\n")

    return final_summary, base_model_diagram
