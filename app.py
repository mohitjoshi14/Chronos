# Chronos - Simulation Tool
# This is a Gradio app that allows users to input a problem statement and run simulations using an LLM (Large Language Model) to analyze the problem and generate summaries of the results.
import gradio as gr
import glob
import os
from datetime import datetime
from src.orchestrator import run_analysis
from src.problem_statement_optimizer import optimize_problem_statement
import asyncio

# Number of variations (simulations) to generate for the problem statement
number_of_scenarios = 10

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

llm_config_4 = {
    'provider': 'google',  # Options: 'openai', 'google', 'anthropic'
    'model_name': 'gemini-2.0-flash',
    'temperature': 0.3  # Lower temperature for clarity in optimization
}

output_directory = 'analysis_results'

def analyze_problem(problem_description):
    final_summary, model_diagram = asyncio.run(run_analysis(
        problem_statement=problem_description,
        num_variations=number_of_scenarios,
        llm_for_generating_system_model=llm_config_1,
        llm_for_generating_scenarios=llm_config_1,
        llm_for_simulation_analysis=llm_config_2,
        llm_for_summarization=llm_config_3,
        output_directory=output_directory,
        verbose=True
    ))
    return final_summary, model_diagram

with gr.Blocks(title="Chronos - Simulation Tool") as demo:
    gr.HTML("""
    <style>
    .magic-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        background: #e0e7ff;
        color: #3b3b6d;
        border: 1px solid #b3b3e6;
        border-radius: 6px;
        padding: 6px 14px;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s;
    }
    .magic-btn:hover {
        background: #c7d2fe;
    }
    .magic-icon {
        font-size: 1.2em;
    }
    </style>
    """)
    gr.Markdown("# Chronos - Simulation Tool\nEnter a problem statement for which you want to run simulations.\n Example: What will be the impact of AI on software engineering jobs?")
    with gr.Row():
        problem_input = gr.Textbox(label="Enter Problem Description", lines=3)
        optimize_btn = gr.Button("\u2728 Optimize Problem Statement", elem_classes=["magic-btn"])  # Magic wand icon
    submit_btn = gr.Button("Submit", variant="primary")
    mermaid_md = gr.Markdown(label="Diagram Preview", value=" ", visible=True, elem_id="mermaid_md_box")
    output_md = gr.Markdown(label="Analysis", value=" ", visible=True, elem_id="output_md_box")
    

    # Optimize button logic: optimize input and update textbox in place
    def optimize_and_return(text):
        return optimize_problem_statement(text, llm_config_4)

    # Disable buttons while processing
    def set_buttons_state(disabled):
        return gr.update(interactive=not disabled), gr.update(interactive=not disabled)

    # When optimize starts, disable both buttons
    optimize_btn.click(
        fn=lambda: set_buttons_state(True),
        inputs=None,
        outputs=[optimize_btn, submit_btn],
        queue=False
    ).then(
        fn=optimize_and_return,
        inputs=problem_input,
        outputs=problem_input,
        queue=True
    ).then(
        fn=lambda: set_buttons_state(False),
        inputs=None,
        outputs=[optimize_btn, submit_btn],
        queue=False
    )

    # When submit starts, disable both buttons
    submit_btn.click(
        fn=lambda: set_buttons_state(True),
        inputs=None,
        outputs=[optimize_btn, submit_btn],
        queue=False
    # ).then(
    #     fn=lambda: "\u23F3 Processing... Please wait.",
    #     inputs=None,
    #     outputs=None,
    #     queue=False
    ).then(
        fn=analyze_problem,
        inputs=problem_input,
        outputs=[output_md, mermaid_md],
        queue=True
    ).then(
        fn=lambda: set_buttons_state(False),
        inputs=None,
        outputs=[optimize_btn, submit_btn],
        queue=False
    )
    
if __name__ == "__main__":
    demo.launch()
