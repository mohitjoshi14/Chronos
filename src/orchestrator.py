# sim.py (This is your main execution file now)
import json
import copy
import datetime
import pandas as pd
import os # Make sure os module is imported
from dotenv import load_dotenv
import logging

# Import components from their new modules
from src.simulation_core import System
from src.model_generation import generate_model_config_with_llm
from src.analysis_and_summary import summarize_simulation_results_with_llm, generate_final_summary_with_llm
from src.parameter_variation import generate_parameter_variations_with_llm

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

def run_analysis(
        problem_statement: str,
        num_variations: int = 1,
        output_directory: str = "output",
        llm_for_generating_system_model: dict = {},
        llm_for_generating_scenarios: dict = {},
        llm_for_simulation_analysis: dict = {},
        llm_for_summarization: dict = {}
    ):
    """
    Main function to orchestrate the entire process:
    1. Get problem statement from user.
    2. Generate base model config using LLM.
    3. (NEW) Generate multiple parameter variations using another LLM.
    4. Run simulation for each variation.
    5. Summarize results for each variation using LLM.
    6. (NEW) Generate a final comprehensive summary if multiple variations were run.
    """
    print("--- System Dynamics Model Generation and Analysis ---")
    # Step 1: Get problem statement from user if not provided
    if problem_statement is None:
            print("Problem statement cannot be empty. Exiting.")
            logging.error("Problem statement cannot be empty. Exiting.")
            return
    else:
        print(f"Using provided problem statement: {problem_statement}")


        if num_variations < 1:
            print("Number of variations must be at least 1. Setting to 1.")
            num_variations = 1

    # # Define the output directory
    # output_directory = "output"
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True) # exist_ok=True prevents error if directory already exists

    # Generate a timestamp for the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Construct the full path for the output file
    output_filename = os.path.join(output_directory, f"simulation_analysis_{timestamp}.md")
    output_final_filename = os.path.join(output_directory, f"final_analysis_{timestamp}.md")

    # Open the Markdown file to write all outputs
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(f"# System Dynamics Model Analysis\n\n")
        f.write(f"**Problem Statement:** {problem_statement}\n\n")
        f.write(f"**Analysis Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"--- Number of Requested Scenarios: {num_variations} ---\n\n")

        # Step 2: AI generates base model configuration
        print("\nGenerating base model configuration with LLM... This might take a moment.")
        f.write("## Base Model Configuration Generation\n\n")
        f.write("Generating base model configuration with LLM...\n\n")

        base_model_config = generate_model_config_with_llm(problem_statement, llm_for_generating_system_model)

        if base_model_config is None:
            print("Failed to generate a valid base model configuration. Exiting.")
            f.write("Failed to generate a valid base model configuration. Analysis stopped.\n")
            logging.error("Failed to generate a valid base model configuration.")
            return

        print("Base Model Configuration Generated Successfully.")
        f.write("Base Model Configuration Generated Successfully.\n\n")
        f.write("### Base Model Configuration JSON:\n")
        f.write("```json\n")
        f.write(json.dumps(base_model_config, indent=2))
        f.write("\n```\n\n")
        print("--- Base Model Configuration (JSON) ---\n", json.dumps(base_model_config, indent=2), "\n-------------------------------------------\n")

        all_scenarios_to_run = []
        # Add the base configuration as the first scenario
        all_scenarios_to_run.append({
            "scenario_description": "Base Case Scenario",
            "model_config": base_model_config
        })

        # Step 3: Generate multiple parameter variations if requested
        if num_variations > 1:
            f.write("## Parameter Variation Generation\n\n")
            print("Generating additional parameter variations with LLM...")
            f.write(f"Requesting {num_variations - 1} additional parameter variations...\n\n")
            
            additional_variations = generate_parameter_variations_with_llm(
                base_model_config=base_model_config,
                num_variations=(num_variations - 1),
                problem_statement=problem_statement,
                llm_for_generating_scenarios=llm_for_generating_scenarios
            )

            if not additional_variations:
                print("No additional parameter variations generated. Running only base case.")
                f.write("No additional parameter variations generated. Proceeding with base case only.\n\n")
                logging.error("No additional parameter variations generated by LLM.")
            else:
                f.write(f"Successfully generated {len(additional_variations)} additional parameter variations.\n\n")
                for var in additional_variations:
                    scenario_config = copy.deepcopy(base_model_config)
                    scenario_config['parameters'] = var.parameters
                    all_scenarios_to_run.append({
                        "scenario_description": var.scenario_description,
                        "model_config": scenario_config
                    })
        
        f.write(f"--- Running {len(all_scenarios_to_run)} Scenarios ---\n\n")
        all_individual_summaries = []
        all_simulation_results = []

        # Step 4 & 5: Run simulation and summarize results for each scenario
        for i, scenario in enumerate(all_scenarios_to_run):
            scenario_description = scenario['scenario_description']
            current_model_config = scenario['model_config']
            
            print(f"\n--- Running Simulation for Scenario {i+1}: {scenario_description} ---")
            f.write(f"## Scenario {i+1}: {scenario_description}\n\n")
            f.write("### Scenario Parameters:\n")
            f.write("```json\n")
            f.write(json.dumps(current_model_config.get('parameters', {}), indent=2))
            f.write("\n```\n\n")
            print(f"Scenario Parameters: {json.dumps(current_model_config.get('parameters', {}), indent=2)}")

            try:
                sim_system = System(current_model_config)
                
                end_time_value = current_model_config.get('simulation_settings', {}).get('end_time', {}).get('value', 100)
                time_unit = current_model_config.get('simulation_settings', {}).get('end_time', {}).get('unit', 'days')

                simulation_results = sim_system.run_simulation(end_time=end_time_value)
                all_simulation_results.append({
                    "scenario_description": scenario_description,
                    "simulation_results": simulation_results
                })
                print(f"Simulation for '{scenario_description}' completed successfully.")
                f.write("Simulation completed successfully.\n\n")

                f.write("### Raw Simulation Data (First 5 and Last 5 Rows):\n")
                if not simulation_results.empty:
                    f.write(simulation_results.head().to_markdown(index=False) + "\n")
                    f.write("...\n")
                    f.write(simulation_results.tail().to_markdown(index=False) + "\n\n")
                else:
                    f.write("No simulation data generated.\n\n")

                # Step 5: Summarize results for the current scenario
                stock_names = [s['name'] for s in current_model_config.get('stocks', [])]
                individual_summary_text = summarize_simulation_results_with_llm(
                    problem_statement,
                    simulation_results,
                    model_parameters=sim_system.parameters,
                    stock_names=stock_names,
                    component_units=sim_system.component_units,
                    time_unit=time_unit,
                    llm_for_simulation_analysis=llm_for_simulation_analysis
                )
                print(f"\n--- AI Summary for Scenario {i+1}: {scenario_description} ---")
                print(individual_summary_text)
                print("---------------------------------------------------\n")
                
                f.write("### AI Generated Summary:\n")
                f.write(individual_summary_text + "\n\n")
                
                all_individual_summaries.append({
                    "scenario_description": scenario_description,
                    "summary_text": individual_summary_text
                })

            except Exception as e:
                error_message = f"Error during simulation for '{scenario_description}': {e}"
                print(f"Error encountered: {error_message}")
                f.write(f"### Simulation Error:\n")
                f.write(f"```")
                f.write(f"{error_message}\n```)\n\n")
                logging.error(error_message, exc_info=e)
                if isinstance(e, ValueError) and ("Error calculating" in str(e)):
                    f.write("Please review the generated model configuration, especially the formulas, for correctness.\n\n")
                all_individual_summaries.append({
                    "scenario_description": scenario_description,
                    "summary_text": f"Simulation failed with error: {e}"
                })
            f.write("---\n\n") # Separator between scenarios

        # Step 6: Generate final comprehensive summary if multiple variations were run
    with open(output_final_filename, 'w', encoding='utf-8') as z:
        z.write("# Final Comprehensive Analysis Conclusion\n\n")
        if num_variations > 1 and len(all_individual_summaries) > 1: # Only run if more than one successful scenario
            final_summary = generate_final_summary_with_llm(
                problem_statement,
                all_individual_summaries,
                llm_for_summarization=llm_for_summarization
            )
            print("\n--- Final Comprehensive AI Summary of All Scenarios ---")
            print(final_summary)
            print("-------------------------------------------------------\n")
            z.write(final_summary + "\n\n")
        elif num_variations == 1:
            print("\nOnly one scenario was run. No comparative summary generated.")
            z.write("Only one scenario was run, so no comparative summary was generated. The summary for the base case is provided above.\n\n")
        else:
            print("\nNo successful scenarios to compare. Skipping final summary.")
            z.write("No successful scenarios were completed for comparison. Skipping final summary generation.\n\n")

    print(f"\nAnalysis complete. Detailed simulation results written to: {output_filename}")
    print(f"Final comprehensive analysis written to: {output_final_filename}")
