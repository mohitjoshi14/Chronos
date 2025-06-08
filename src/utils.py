import os
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


# Load prompt templates from files
def load_prompt_from_file(filepath):
    """Loads prompt messages from a YAML file."""
    # from prompts folder
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt file not found: {filepath}")   
    if not filepath.endswith('.yaml'):
        raise ValueError("Prompt file must be a YAML file.")
    # Load the YAML file
    with open(filepath, 'r', encoding='utf-8') as f:
        prompt_data = yaml.safe_load(f)
    return prompt_data

def select_llm_model(llm_config):
    """Selects the appropriate LLM model based on the model name."""
    provider = llm_config.get("provider", "google")
    model_name = llm_config.get("model_name", "gemini-2.0-flash")
    temperature = llm_config.get("temperature", 0.2)

    if provider == "openai":
        llm = ChatOpenAI(model=model_name, temperature=temperature)
    elif provider == "google":
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
    elif provider == "anthropic":
        llm = ChatAnthropic(model_name=model_name, temperature=temperature, timeout=60, stop=[])
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers are: openai, google, anthropic.")
    return llm
