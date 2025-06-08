# Chronos - Simulation Tool
# This is a Gradio app that allows users to input a problem statement and run simulations using an LLM (Large Language Model) to analyze the problem and generate summaries of the results.
import gradio as gr
import glob
import os
from datetime import datetime
from src.orchestrator import run_analysis

# Number of variations (simulations) to generate for the problem statement
number_of_scenarios = 3

# LLM config to be used at various stages of the analysis
llm_config_1 = {
    'provider': 'google',  # Options: 'openai', 'google', 'anthropic'
    'model_name': 'gemini-2.0-flash',
    'temperature': 0.2 # suggest lower creativity (0.2) for generating system model and scenarios
}

llm_config_2 = {
    'provider': 'google',  # Options: 'openai', 'google', 'anthropic'
    'model_name': 'gemini-2.0-flash',
    'temperature': 0.4  # suggest higher creativity (0.5) for simulation analysis
}

llm_config_3 = {
    'provider': 'google',  # Options: 'openai', 'google', 'anthropic'
    'model_name': 'gemini-2.0-flash',
    'temperature': 0.5  # suggest higher creativity (0.7) for summarization
}

output_directory = 'analysis_results'

def analyze_problem(problem_description):
    final_summary = run_analysis(
        problem_statement=problem_description,
        num_variations=number_of_scenarios,
        llm_for_generating_system_model=llm_config_1,
        llm_for_generating_scenarios=llm_config_1,
        llm_for_simulation_analysis=llm_config_2,
        llm_for_summarization=llm_config_3,
        output_directory=output_directory
    )
    return final_summary

with gr.Blocks(title="Chronos - Simulation Tool") as demo:
    gr.HTML("""
    <style>
    #output_md_box {
        min-height: 180px;  /* Adjust as needed */
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 12px;
        background: #f9f9f9;
    }
    </style>
    """)
    gr.Markdown("# Chronos - Simulation Tool\nEnter a problem statement for which you want to run simulations.\n Example: What will be the impact of AI on software engineering jobs?")
    with gr.Row():
        problem_input = gr.Textbox(label="Enter Problem Description", lines=3)
    submit_btn = gr.Button("Submit", variant="primary")
    output_md = gr.Markdown(label="Analysis", value=" ", visible=True, elem_id="output_md_box")

    # First, show the "Processing..." message
    submit_btn.click(
        fn=lambda: "⏳ Processing... Please wait.",
        inputs=None,
        outputs=output_md,
        queue=False  # Immediate feedback, no queue
    )
    # Then, run the analysis and update the output
    submit_btn.click(
        fn=analyze_problem,
        inputs=problem_input,
        outputs=output_md,
        queue=True  # This can be True or omitted for default behavior
    )

if __name__ == "__main__":
    demo.launch()
