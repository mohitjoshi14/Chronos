from src.orchestrator import run_analysis

# Problem statement that you want to analyze
# problem_description = """What is the impact of Coca-Cola doubling their price?"""
# problem_description = """What is the impact of Trump trade tariffs on the World Economy?"""
# problem_description = """What is the impact of climate change on global food security?"""
# problem_description = """What is the impact of AI on job displacement?"""
problem_description = """
Core Question: How will the accelerating adoption of AI-powered automation and optimization technologies specifically within the Indian IT Services and Business Process Outsourcing (BPO) sector influence the net change in full-time equivalent (FTE) employment levels (considering both displacement and creation) for entry-level and mid-level roles over the period 2025-2040, and what are the most effective policy and industry-level interventions to achieve a stable or growing employment rate in this sector?

Key Areas of Interest/Dynamics to Explore:

AI Adoption Rate: Factors influencing the rate of AI adoption by IT and BPO companies (e.g., cost of AI, availability of skilled AI professionals, competitive pressure, regulatory environment).
Job Displacement Mechanisms:
Automation of repetitive tasks (e.g., data entry, customer support).
Efficiency gains leading to reduced need for human intervention.
Impact on specific job categories (e.g., IT support, call center agents, junior software developers).
Job Creation Mechanisms:
New roles created by AI (e.g., AI trainers, data scientists, AI ethicists, prompt engineers).
Increased demand for services due to AI-driven productivity and cost reductions.
Growth in complementary industries.
Workforce Transformation & Skill Gap:
Flow of workers between different skill levels/job types.
Effectiveness of re-skilling and up-skilling programs (e.g., government initiatives, corporate training, individual learning).
Time lags associated with skill acquisition.
Economic & Policy Environment:
Government policies (e.g., subsidies for training, unemployment benefits, labor laws, AI regulation).
Investment in R&D and AI infrastructure.
Overall economic growth in India.
Industry-level strategic decisions (e.g., reskilling investment, organizational restructuring).
Demand Dynamics:
How AI impacts the demand for IT and BPO services.
Potential for new service offerings enabled by AI.
Desired Outcomes from the Model (Quantifiable Outputs):

Projection of net FTE employment in the Indian IT/BPO sector (disaggregated by skill level/job type if feasible).
Projections of average wages for different skill segments.
Sensitivity of employment levels to different AI adoption rates.
Effectiveness (in terms of employment impact) of various policy interventions (e.g., x percent increase in re-skilling budget, y percent tax incentive for AI-driven job creation).
Identification of tipping points or critical thresholds in AI adoption."""

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
