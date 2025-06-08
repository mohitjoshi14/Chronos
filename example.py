from src.orchestrator import run_analysis

# Problem statement that you want to analyze
# problem_description = """What is the impact of Coca-Cola doubling their price?"""
# problem_description = """What is the impact of Trump trade tariffs on the World Economy?"""
# problem_description = """What is the impact of climate change on global food security?"""
problem_description = """What is the impact of AI on job displacement?"""

# Number of variations (simulations) to generate for the problem statement
number_of_scenarios = 5

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

# Output directory for the analysis results
output_directory = 'analysis_results'

# Run the analysis with the specified parameters
run_analysis(
    problem_statement=problem_description,
    num_variations=number_of_scenarios,
    llm_for_generating_system_model=llm_config_1,
    llm_for_generating_scenarios=llm_config_1,
    llm_for_simulation_analysis=llm_config_2,
    llm_for_summarization=llm_config_3,
    output_directory=output_directory
)
