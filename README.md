# Chronos: Doctor Strange's Guide to System Dynamics

Ever wished you could peek into the future, like Doctor Strange, and see how your decisions play out? Welcome to Chronos\! This project lets you do just that, but for complex systems. It's like having the Eye of Agamotto for your business, environmental, or social challenges.

We use the power of advanced AI (Large Language Models, or LLMs) to build, simulate, and analyze "System Dynamics" models. In plain terms, you tell our AI a problem, and it builds a mini-universe to show you how things might unfold over time, including "what-if" scenarios.

Note: Currently the product is not production ready and can generate errors. Use at your own risk.

-----

## 1\. The Multiverse Unveiled: What is This Project?

System Dynamics helps us study and manage complex systems that change over time, especially those with lots of interconnected parts and feedback loops. Think of it like understanding the flow of magic in a complex spell. This project makes building and analyzing these "magic systems" super easy using LLMs.

Just tell our system your problem, and it will:

  * Conjure up a detailed model of "stocks" and "flows" (more on these later\!).
  * Run simulations to show you how your system behaves.
  * Even create multiple "what-if" scenarios by tweaking parts of your model, just like Doctor Strange exploring different timelines.
  * Give you AI-powered summaries of each simulation's outcome.
  * Finally, provide a grand, AI-driven comparison of all your alternate realities (scenarios).

## 2\. Understanding the Fabric of Reality: System Dynamics Basics

### Thinking Like a Sorcerer Supreme: System Thinking

System Thinking is about looking at the whole picture, not just isolated pieces. Instead of getting lost in the details of a single problem, it helps us see how everything connects, how actions ripple through a system, and how things change over time. It's seeing the grand tapestry, not just a single thread.

### The Building Blocks of Your Reality: Stocks, Flows, and Auxiliaries

System Dynamics models are built from three fundamental magical ingredients:

  * **Stocks (or Levels):**

      * **What they are:** These are the *accumulations* in your system, like the amount of water in a bathtub or the number of people in a city. They're the "nouns" of your system – what's being held or stored.
      * **Analogy:** The water level in a bathtub is a classic "stock."
      * **Role in Analysis:** Stocks tell you the state of your system at any moment. They have "memory," meaning their current value depends on their past.

  * **Flows (or Rates):**

      * **What they are:** These are the *rates of change* for your stocks. They are the actions that fill up or drain your stocks. Think of them as the "verbs" – what's causing the change.
      * **Analogy:** The water flowing *into* the bathtub (inflow) and water draining *out* (outflow) are "flows."
      * **Relationship:** Flows directly affect stocks.
      * **Role in Analysis:** Flows are what *drive* the system's changes. Understanding them is key to understanding how your stocks fluctuate.

  * **Auxiliaries (or Converters):**

      * **What they are:** These are intermediate calculations or variables that *influence* your flow rates. They're not stocks or flows themselves, but they represent rules, policies, or other factors that impact how things flow.
      * **Analogy:** The position of the faucet handle (which controls how fast water flows in) is like an auxiliary.
      * **Relationship:** Auxiliaries often take information from stocks and other fixed values to determine how fast flows happen.
      * **Role in Analysis:** Auxiliaries are vital for capturing the *logic* and *decision-making* within your system. They're the "levers" you can pull to change the system's behavior.

### Casting Spells: How We Analyze Systems

Our System Dynamics analysis uses these elements to:

1.  **Map the System:** Create visual diagrams (like magical blueprints) showing how stocks, flows, and auxiliaries are connected through "feedback loops."
2.  **Identify Feedback Loops:** Uncover the self-reinforcing (amplifying) and balancing (goal-seeking) cycles that govern your system's behavior.
3.  **Formulate Equations:** Translate these relationships into mathematical formulas that describe how flows change stocks over time.
4.  **Simulate Behavior:** Run computer simulations to watch your system evolve over time under different conditions. This often reveals surprising patterns like growth, decline, or oscillations.
5.  **Conduct "What-If" Analysis:** Just like Doctor Strange exploring alternate realities, you can test different scenarios by changing parameters, initial conditions, or auxiliary formulas to see their impact.

### Why Bother with Time Travel? The Benefits of System Dynamics

This type of analysis is incredibly powerful for understanding complex systems and gaining specific insights, much like seeing all possible futures:

  * **Holistic Understanding:** It forces you to look at the whole picture, revealing the root causes of problems rather than just treating symptoms. Often, "the problem is the system itself."
  * **Understanding Long-Term Dynamics:** It helps predict trends, cycles, and growth/decline patterns that aren't obvious from a quick glance. Essential for strategic planning and foresight\!
  * **Identifying Leverage Points:** By mapping out connections, it helps you find the most effective places to intervene for the biggest, most lasting impact.
  * **Designing Better Policies:** You can test different strategies in a simulated environment, anticipating unintended consequences and refining your plans before implementing them in the real world. This saves time and resources, preventing a "Dormammu, I've come to bargain" situation.
  * **Clarifying Mental Models:** Building a model makes you clearly articulate your assumptions, improving everyone's understanding and fostering a shared vision.
  * **Revealing Counter-intuitive Outcomes:** Complex systems often behave in unexpected ways. Our simulations can uncover these surprises, explaining why good intentions sometimes lead to bad results.
  * **Generating Specific Insights:** Beyond general understanding, Chronos can answer precise "what-if" questions (e.g., "What if our magic reserves double?", "What if chitauri invaders increase by 10%?"), quantifying potential impacts.

## 3\. Sorcerous Features

  * **LLM-driven Model Generation:** Our AI automatically creates your system's blueprint (stocks, flows, auxiliaries, parameters, connections) from your natural language problem statement.
  * **Dynamic Simulation Engine:** A Python-powered core that brings your magical models to life.
  * **Parameter Variation / Scenario Analysis:** The LLM can generate multiple, logical "what-if" scenarios by changing key parameters, just like Doctor Strange exploring different possibilities.
  * **AI-powered Summarization:** LLMs summarize individual simulation results and provide a comparative analysis across different scenarios, revealing the optimal timeline.
  * **Unit-aware Processing:** Handles units for all model components, ensuring consistency and making summaries more informative.
  * **Robust Error Handling:** Comprehensive logging and specific error messages help you debug if your spell goes awry.
  * **Configurable LLM Prompts:** The "instructions" for our AI are in easy-to-edit YAML files, so you can fine-tune its magical abilities.

## 4\. Initiating the Mystical Arts: Getting Started

### Setting Up Your Sanctum: Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a virtual environment and install packages using `uv` (recommended for a clean Sanctum and speedy setup):**
    ```bash
    uv venv
    source .venv/bin/activate # On Windows: `.venv\Scripts\activate`
    uv pip install -r requirements.txt
    ```

### Attuning Your Orb: Environment Setup

This project uses Google's Gemini LLMs, so you'll need a Google API Key:

1.  Obtain your Google API Key from the Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2.  Create a file named `.env` in the root directory of your project.
3.  Add your API key to this file like so:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

## 5\. Casting Your First Simulation

### The Incantation: Running the Analysis

Execute the `main.py` script from your project's root directory:

```bash
python main.py
```

### The Problem Scroll: Input Problem Statement

The script will ask you to describe the problem you want to analyze:

```
--- System Dynamics Model Generation and Analysis ---
Please enter the problem statement you want to analyze (e.g., 'What is the impact of Coca-Cola doubling their price?'):
```

Provide a clear and concise description of the system you want to model, and the question you're asking, like "What happens if Thanos snaps his fingers again?"

### Visions of the Future: Number of Parameter Variations

You'll also be asked how many alternate realities (parameter variations) to generate:

```
Enter the number of parameter variations to generate (1 for base run only, >1 for scenario analysis):
```

  * Enter `1` for a single simulation with the base model, like viewing one specific future.
  * Enter a number greater than `1` to generate additional scenarios by varying key parameters, just as Doctor Strange explores countless possibilities. The LLM will create these variations, and the system will simulate and summarize each one.

### Unveiling Destiny: Output

Upon successful completion, the simulation results and AI-generated summaries will appear in your console.
Additionally, magical output files will be saved in the `analysis_results/` directory:

  * `simulation_analysis_<timestamp>.md`: Contains the detailed simulation results for each scenario.
  * `final_analysis_<timestamp>.md`: Contains the comprehensive comparative summary across all scenarios (if you chose more than one variation).

Log files are saved in the `logs/` directory:

  * `error_<timestamp>.log`: Contains detailed error logs if any issues occur during execution.

## 6\. The Grand Design: Project Structure

```
.
├── example.py                       # Example script for running the magic simulation.
├── requirements.txt                 # List of required magical ingredients (Python dependencies).
├── .env                             # Your personal book of secrets (e.g., GOOGLE_API_KEY).
├── analysis_results/                # Where your visions of the future and summaries are stored.
├── logs/                            # The archive of any magical mishaps.
├── prompts/                         # YAML files containing the ancient texts for our LLM.
│   ├── model_generation_prompt.yaml # Instructions for generating the initial model.
│   ├── parameter_variation_prompt.yaml # Instructions for creating alternate realities.
│   ├── sim_analysis_prompt.yaml     # Instructions for summarizing simulation results.
│   └── final_sim_analysis_prompt.yaml # Instructions for summarizing multiple scenarios.
└── src/                             # The core of the magical engine.
    ├── orchestrator.py              # The master spell, orchestrating the whole process.
    ├── simulation_core.py           # The beating heart: defines and runs the system dynamics model.
    ├── model_generation.py          # AI-powered model generation for conjuring model configurations.
    ├── parameter_variation.py       # AI-powered parameter variation for generating infinite timelines.
    ├── analysis_and_summary.py      # AI-powered analysis and summary for summarizing your visions.
    └── utils.py                     # Handy magical helper functions.
```

## 7\. The Core Artifacts: Key Components

  * **`main.py`**: The entry point, much like the Ancient One guiding new sorcerers. It handles user input, model generation, simulation, scenario creation, and summarization.
  * **`src/simulation_core.py`**: Contains the fundamental classes (`Stock`, `Flow`, `Auxiliary`, `System`) that define and execute your system dynamics model. It knows how to update stock values based on flows and evaluate formulas. **Crucially, it understands how to read parameter values like `PARAMETER_NAME['value']`, as taught by the LLM prompt.**
  * **`src/model_generation.py`**: Manages talking to the LLM to create the initial JSON model configuration from your natural language problem statement. It uses powerful Pydantic magic for strict output validation.
  * **`src/parameter_variation.py`**: Handles the LLM interaction for creating multiple distinct parameter variations (scenarios) based on your base model.
  * **`src/analysis_and_summary.py`**: Integrates with the LLM to generate natural language summaries of simulation results, including starting/ending states, parameter values, and units. It also produces a comprehensive comparative summary for multiple scenarios.
  * **`prompts/`**: This directory holds the YAML files that define the instructions for the LLM. These are highly customizable, allowing you to fine-tune the LLM's behavior and make it truly your own.
  * **`src/utils.py`**: Contains shared utility functions, like loading your prompt files.

## 8\. Speaking to the Oracle: LLM Prompts and Customization

The behavior of our LLMs is controlled by the mystical prompt files in the `prompts/` directory:

  * **`model_generation_prompt.yaml`**: This prompt instructs the LLM on how to create the initial system dynamics model JSON. It includes critical guidelines like naming conventions, formula syntax (e.g., `PARAMETER_NAME['value']`), and unit requirements.
  * **`parameter_variation_prompt.yaml`**: This prompt guides the LLM in generating plausible parameter variations for scenario analysis. It specifies the number of variations, which fields to change (only `value` of parameters), and the expected JSON output format.
  * **`sim_analysis_prompt.yaml`**: This prompt explains how to summarize each simulation analysis.
  * **`final_sim_analysis_prompt.yaml`**: This prompt explains how to summarize scenarios from all simulation result into one comprehensive analysis.

You can modify these YAML files to:

  * Adjust the specificity or detail of the generated models.
  * Refine the types of parameter variations, perhaps focusing on "chaos magic" or "reality warping" scenarios.
  * Change naming conventions or other structural requirements.
  * Improve the natural language generation for summaries, making them sound more like pronouncements from the Eye of Agamotto.

## 9\. Shielding from Chaos: Error Handling and Logging

The project includes comprehensive error handling and logging, designed to help you understand if your spell misfires.

  * Errors during model generation, formula evaluation, or LLM interactions are caught and reported to the console, much like Mordo warning of cosmic consequences.
  * Detailed error messages, including `NameError` specifics (e.g., missing variables in formulas), are logged to `logs/error_<timestamp>.log`. This file is crucial for debugging issues related to the LLM's generated output, helping you correct your incantations.

## 10\. Future Dimensions: Enhancements
  * **Evals / Automated Tests:** Develop multiple test cases and test data for automated evaluations and end to end tests.
  * **UI/Web Interface:** Develop a simple web interface for easier interaction and visualization, making Chronos accessible to all aspiring Sorcerers.
  * **Interactive Visualization:** Create stunning visual representations of your future timelines.
  * **Model Validation:** Add automated checks for common model inconsistencies (e.g., unconnected flows, undefined variables) and incorrect formula generations, preventing accidental paradoxes.
  * **Human-in-the-Loop:** Allow users to add/remove stocks, flows and auxiliaries interactively, and then run the simulation. Allow sharing of reports through various channels.

## 11\. Joining the Mystic Arts: Contributing

Contributions are welcome\! Please feel free to open issues or submit pull requests. Let's build a stronger Chronos together\!

## 12\. The Ancient One's Blessing: License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE). Go forth and explore the multiverse of possibilities\!