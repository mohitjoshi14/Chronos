import os
import yaml

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

