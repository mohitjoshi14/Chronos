import os
import logging
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils import load_prompt_from_file, select_llm_model

# Load environment variables (like GOOGLE_API_KEY)
load_dotenv()

logger = logging.getLogger(__name__)


def optimize_problem_statement(problem_statement, llm_for_optimizing_problem_statement):
    """
    Optimizes the problem statement using an LLM to make it more suitable for model generation.
    """
    llm = select_llm_model(llm_for_optimizing_problem_statement)
    parser = StrOutputParser()
    if not problem_statement:
        logger.error("Problem statement cannot be empty.")
        raise ValueError("Problem statement cannot be empty.")

    # Load the prompt messages from the YAML file
    prompt_directory = 'prompts'
    if not os.path.exists(prompt_directory):
        logger.error(f"Prompt directory not found: {prompt_directory}")
        raise FileNotFoundError(f"Prompt directory not found: {prompt_directory}")
    prompt_file = os.path.join(prompt_directory, 'problem_statement_optimization_prompt.yaml')
    prompt_messages = load_prompt_from_file(prompt_file)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_messages["system_message"]),
            ("human", prompt_messages["human_message"])
        ]
    )

    chain = prompt_template | llm | parser

    try:
        optimized_config = chain.invoke({"problem_statement": problem_statement})
        return optimized_config
    except Exception as e:
        logger.error(f"Error during problem statement optimization: {e}")
        raise ValueError(f"Error during problem statement optimization: {e}")
    
if __name__ == "__main__":
    problem_statement = "How can we improve the employment rate in the tech industry?"
    llm_for_optimizing_problem_statement = {'provider': 'google', 'model_name': 'gemini-2.0-flash', 'temperature': 0.5}
    optimized_statement = optimize_problem_statement(problem_statement, llm_for_optimizing_problem_statement)
    # print("Optimized Problem Statement:")
    print(optimized_statement)