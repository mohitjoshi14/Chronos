import os
from datetime import datetime
import json
import re

def extract_variables(text):
    """
    Extracts strings that start and end with an alphabet, number, or underscore.
    This effectively captures any "word" composed of alphanumeric characters and underscores.

    Args:
        text (str): The input string from which to extract the patterns.

    Returns:
        list: A list of unique strings found that match the defined patterns.
    """
    # Regex explanation:
    # \b          : Word boundary (ensures we match whole words)
    # [a-zA-Z0-9_]+ : Matches one or more (the `+` sign) occurrences of:
    #                 - any lowercase letter (a-z)
    #                 - any uppercase letter (A-Z)
    #                 - any digit (0-9)
    #                 - an underscore (_)
    #               Since it matches one or more, it inherently starts and ends
    #               with one of these characters if it's a valid match.
    # \b          : Word boundary (ensures we match whole words)
    pattern = re.compile(r'\b[a-zA-Z0-9_]+\b')

    # Find all matches
    matches = pattern.findall(text)

    # Return unique matches to avoid duplicates if a string appears multiple times
    return sorted(list(set(matches)))

# function generates a mermaid diagram for a given model
# uses different visual styles for stocks, auxiliaries, flows, and parameters
def generate_model_diagram(model_config: dict) -> str:
    """
    Generates a Mermaid diagram string for the given model configuration.
    """

    # add mermaid diagram header
    diagram = "```mermaid\n"
    diagram += "graph LR\n"

    # Add stocks
    for stock in model_config['stocks']:
        diagram += f"  {stock['name']}[\"STOCK: {stock['name']} ({stock['unit']})\"]\n"
        diagram += f"  class {stock['name']} stockNode\n"

    # Add auxiliaries, use assymetric node shape for auxiliaries (example: a1>"This is the text in the box"] )
    for aux in model_config['auxiliaries']:
        diagram += f"  {aux['name']}>\"AUX: {aux['name']} ({aux['unit']}\"] \n"
        diagram += f"  class {aux['name']} auxNode\n"

    # Add parameters, use database node shape for parameters (example: d1[(Database)])
    for param_name, param in model_config['parameters'].items():
        diagram += f"  {param_name}[(\"PARAM: {param_name} ({param['unit']})\")] \n"
        diagram += f"  class {param_name} paramNode\n"

    # Add flows, use subroutine node shape for flows (example: f1[[Flow]])
    for flow in model_config['flows']:
        diagram += f"  {flow['name']}[[\"FLOW: {flow['name']} ({flow['unit']})\"]]\n"
        diagram += f"  class {flow['name']} flowNode\n"

    # Add flow connections with animated arrows
    count = 0
    for connection in model_config['flow_connections']:
        flow_name, stock_name, direction = connection
        count += 1
        if direction == 'inflow':
            diagram += f"  {flow_name} e{count}@==>|\"inflow\"| {stock_name}:::animated\n"
            diagram += f"  e{count}@{{ animate: true }}\n"
        else:
            diagram += f"  {stock_name} e{count}@==>|\"outflow\"| {flow_name}:::animated\n"
            diagram += f"  e{count}@{{ animate: true }}\n"

    # Connect parameters to auxiliaries to flows
    # if a parameter is used in an auxiliary or flow formula, then add a connection to that auxiliary or flow
    # if auxiliary is used in a flow formula, then add a connection to that flow
    # these connects should be in the form of dashed lines
    for aux in model_config['auxiliaries']:
        for param_name in extract_variables(aux.get('formula', '')):
            # # remove ['value'] string from parameter name
            # if '[' in param_name:
            #     param_name = param_name.split('[')[0]
            # param_name = ''.join(c for c in param_name if c.isalnum() or c == '_')
            # print(f"Checking parameter: {param_name} in auxiliary: {aux['name']}")
            if param_name in model_config['parameters'].keys():
                # print(f"Adding connection from parameter: {param_name} to auxiliary: {aux['name']}")
                diagram += f"  {param_name} -.-> {aux['name']}\n"
            # else:
                # print(f"Parameter: {param_name} not found in {model_config['parameters'].keys()}.")
    for aux in model_config['auxiliaries']:
        for aux_name in extract_variables(aux.get('formula', '')):
            # if '[' in aux_name:
            #     aux_name = aux_name.split('[')[0]
            # aux_name = ''.join(c for c in aux_name if c.isalnum() or c == '_')
            if any(aux_item['name'] == aux_name for aux_item in model_config['auxiliaries']):
                diagram += f"  {aux_name} -.-> {aux['name']}\n"
    for flow in model_config['flows']:
        for param_name in extract_variables(flow.get('formula', '')):
            if param_name in model_config['parameters'].keys():
                diagram += f"  {param_name} -.-> {flow['name']}\n"
    for flow in model_config['flows']:
        for aux_name in extract_variables(flow.get('formula', '')):
            # if '[' in aux_name:
            #     aux_name = aux_name.split('[')[0]
            # aux_name = ''.join(c for c in aux_name if c.isalnum() or c == '_')
            if any(aux['name'] == aux_name for aux in model_config['auxiliaries']):
                diagram += f"  {aux_name} -.-> {flow['name']}\n"
    for flow in model_config['flows']:
        for flow_name in extract_variables(flow.get('formula', '')):
            # if '[' in flow_name:
            #     flow_name = flow_name.split('[')[0]
            # flow_name = ''.join(c for c in flow_name if c.isalnum() or c == '_')
            if any(flow_item['name'] == flow_name for flow_item in model_config['flows']):
                diagram += f"  {flow_name} -.-> {flow['name']}\n"
    for aux in model_config['auxiliaries']:
        for stock_name in extract_variables(aux.get('formula', '')):
            # if '[' in stock_name:
            #     stock_name = stock_name.split('[')[0]
            # stock_name = ''.join(c for c in stock_name if c.isalnum() or c == '_')
            if any(stock_item['name'] == stock_name for stock_item in model_config['stocks']):
                diagram += f"  {stock_name} --- {aux['name']}\n"
    for flow in model_config['flows']:
        for stock_name in extract_variables(flow.get('formula', '')):
            # if '[' in stock_name:
            #     stock_name = stock_name.split('[')[0]
            # stock_name = ''.join(c for c in stock_name if c.isalnum() or c == '_')
            if any(stock_item['name'] == stock_name for stock_item in model_config['stocks']):
                diagram += f"  {stock_name} --- {flow['name']}\n"
    
    # Add class definitions for node colors/styles
    diagram += "  classDef stockNode fill:#FFD700,stroke:#B8860B,stroke-width:4px,color:#000,font-weight:bold\n"
    diagram += "  classDef flowNode fill:#87CEEB,stroke:#4682B4,stroke-width:2px,color:#000\n"
    diagram += "  classDef auxNode fill:#B0E57C,stroke:#228B22,stroke-width:2px,color:#000\n"
    diagram += "  classDef paramNode fill:#E0E0E0,stroke:#888,stroke-width:1px,color:#666\n"
    diagram += "  classDef animated stroke-dasharray: 5 5, animate: true, animation: fast\n"

    # close the mermaid diagram with ```
    diagram += "```\n"

    return diagram

if __name__ == "__main__":
    # read a json file with the model configuration
    with open('model_config.json', 'r') as f:
        example_model_config = json.load(f)     

    # Generate the diagram and write to an output file in analysis_results (model_diagram_<timestamp>.md)

    if not os.path.exists('analysis_results'):  # Ensure the output directory exists
        os.makedirs('analysis_results')
    
    output_file = 'analysis_results/model_diagram_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.md'
    diagram = generate_model_diagram(example_model_config)
    with open(output_file, 'w') as f:
        f.write(diagram)