# simulation_core.py
import pandas as pd
import numpy as np
import logging
import os

# Do not configure logging here; use the root logger set up by orchestrator.py
logger = logging.getLogger(__name__)

class Stock:
    """Represents an accumulation in the system."""
    def __init__(self, name: str, initial_value: float, unit: str, description: str = ""):
        self.name = name
        self.value = initial_value
        self.unit = unit
        self.description = description
        self.inflows = []
        self.outflows = []

    def update(self, dt: float):
        """Update the stock's value based on its net flows."""
        net_flow = sum(flow.rate for flow in self.inflows) - \
                   sum(flow.rate for flow in self.outflows)
        self.value += net_flow * dt 
        self.value = max(0.0, self.value) # Ensure non-negative stock values

    def __repr__(self):
        return f"Stock({self.name}={self.value:.2f} {self.unit})"

class Flow:
    """Represents a rate of change, calculated from a string formula."""
    def __init__(self, name: str, formula: str, unit: str, description: str = ""):
        self.name = name
        self.formula = formula
        self.unit = unit
        self.description = description
        self.rate = 0.0

    def calculate_rate(self, system_state: dict):
        """
        Calculate the flow rate using eval() on the formula string.
        The formula can reference stock values, auxiliary values, and parameters
        from the system_state dictionary.
        """
        try:
            self.rate = eval(self.formula, globals(), system_state)
            self.rate = max(0.0, self.rate) # Ensure non-negative flow rates
        except Exception as e:
            logger.error(f"Error calculating flow '{self.name}' with formula '{self.formula}': {e}")
            raise ValueError(f"Error calculating flow '{self.name}' with formula '{self.formula}': {e}")

    def __repr__(self):
        return f"Flow({self.name}={self.rate:.2f} {self.unit})"

class Auxiliary:
    """Represents a variable that influences flows, calculated from a string formula."""
    def __init__(self, name: str, formula: str, unit: str, description: str = ""):
        self.name = name
        self.formula = formula
        self.unit = unit
        self.description = description
        self.value = 0.0

    def calculate_value(self, system_state: dict):
        """
        Calculate the auxiliary's value using eval() on the formula string.
        The formula can reference stock values, other auxiliary values,
        and parameters from the system_state dictionary.
        """
        try:
            self.value = eval(self.formula, globals(), system_state)
        except Exception as e:
            logger.error(f"Error calculating auxiliary '{self.name}' with formula '{self.formula}': {e}")
            raise ValueError(f"Error calculating auxiliary '{self.name}' with formula '{self.formula}': {e}")

    def __repr__(self):
        return f"Auxiliary({self.name}={self.value:.2f} {self.unit})"

class System:
    """
    Orchestrates the simulation, holding all components and managing the time steps.
    Model components are loaded from a structured dictionary (e.g., parsed JSON).
    """
    def __init__(self, model_config: dict):
        # dt is the time step for the simulation
        self.dt = model_config.get('simulation_settings', {}).get('dt', {}).get('value', 1.0)
        self.dt_unit = model_config.get('simulation_settings', {}).get('dt', {}).get('unit', 'time_unit')
        # time is the current simulation time
        self.time = 0.0
        # history is a DataFrame to store simulation results
        self.history = pd.DataFrame()
        # parameters are the model parameters, which can be used in formulas
        self.parameters = model_config.get('parameters', {})
        #problem_description is a string describing the problem being modeled
        self.problem_description = model_config.get('problem_description', 'No description provided.')

        # Store units for later use
        self.component_units = {}
        for s in model_config.get('stocks', []):
            self.component_units[s['name']] = s['unit']
        for a in model_config.get('auxiliaries', []):
            self.component_units[a['name']] = a['unit']
        for f in model_config.get('flows', []):
            self.component_units[f['name']] = f['unit']
        for p_name, p_details in model_config.get('parameters', {}).items():
            if isinstance(p_details, dict) and 'unit' in p_details:
                self.component_units[p_name] = p_details['unit']
            else: # Handle old parameter format gracefully if any
                self.component_units[p_name] = " dimensionless"

        # Initialize Stocks
        stocks_config = model_config.get('stocks', [])
        self.stocks = {s['name']: Stock(s['name'], s['initial_value'], s['unit'], s.get('description', '')) for s in stocks_config}

        # Initialize Auxiliaries
        auxiliaries_config = model_config.get('auxiliaries', [])
        self.auxiliaries = {a['name']: Auxiliary(a['name'], a['formula'], a['unit'], a.get('description', '')) for a in auxiliaries_config}

        # Initialize Flows
        flows_config = model_config.get('flows', [])
        self.flows = {f['name']: Flow(f['name'], f['formula'], f['unit'], f.get('description', '')) for f in flows_config}

        # Establish Flow Connections to Stocks
        flow_connections_config = model_config.get('flow_connections', [])
        for flow_name, stock_name, direction in flow_connections_config:
            if flow_name not in self.flows:
                logger.error(f"Flow '{flow_name}' in connections config not found in defined flows.")
                raise ValueError(f"Flow '{flow_name}' in connections config not found in defined flows.")
            if stock_name not in self.stocks:
                logger.error(f"Stock '{stock_name}' in connections config not found in defined stocks.")
                raise ValueError(f"Stock '{stock_name}' in connections config not found in defined stocks.")

            flow_obj = self.flows[flow_name]
            stock_obj = self.stocks[stock_name] 

            if direction == 'inflow':
                stock_obj.inflows.append(flow_obj)
            elif direction == 'outflow':
                stock_obj.outflows.append(flow_obj)
            else:
                logger.error(f"Invalid direction '{direction}' for flow connection. Must be 'inflow' or 'outflow'.")
                raise ValueError(f"Invalid direction '{direction}' for flow connection. Must be 'inflow' or 'outflow'.")

    def _get_current_dynamic_state_for_history(self):
        """
        Returns a dictionary of current values for stocks, auxiliaries, and flows
        to be recorded in the simulation history DataFrame.
        """
        state_record = {name: stock.value for name, stock in self.stocks.items()}
        state_record.update({name: aux.value for name, aux in self.auxiliaries.items()})
        state_record.update({name: flow.rate for name, flow in self.flows.items()})
        state_record['time'] = self.time # Include time for the DataFrame
        return state_record

    def run_simulation(self, end_time: float):
        """Runs the simulation from current time to end_time."""
        self.history = pd.DataFrame() # Ensure history is reset for each run

        while self.time <= end_time:
            # 1. Record the current dynamic state for the history DataFrame *before* updates
            current_state_record_for_history = self._get_current_dynamic_state_for_history()
            self.history = pd.concat([self.history, pd.DataFrame([current_state_record_for_history])], ignore_index=True)

            # 2. Prepare the context for formula evaluation (for Auxiliaries and Flows)
            eval_context = {name: stock.value for name, stock in self.stocks.items()}
            # Auxiliaries are initialized to 0.0, so update eval_context with their current (potentially 0.0) values
            # before calculating them. This ensures their names are in the context.
            eval_context.update({name: aux.value for name, aux in self.auxiliaries.items()})
            eval_context.update({name: flow.rate for name, flow in self.flows.items()}) # Include current flow rates
            eval_context.update(self.parameters) # Include full parameter dictionaries
            eval_context['time'] = self.time # Include time in eval context

            # Calculate Auxiliaries using the eval_context in multiple passes
            # This helps resolve dependencies where one auxiliary depends on another.
            # TO IMPROVE: This is not a good logic and will need to be improved in future iterations.
            for _ in range(5): # Iterate 5 times to ensure dependencies are met in typical models
                for aux_name, aux in self.auxiliaries.items():
                    aux.calculate_value(eval_context)
                    # IMMEDIATELY update eval_context with the new auxiliary value
                    # This is crucial for auxiliaries calculated later in the same pass
                    eval_context[aux_name] = aux.value

            # 5. Calculate Flows using the now fully updated eval_context
            for flow_name, flow in self.flows.items():
                flow.calculate_rate(eval_context)

            # 6. Update Stocks based on calculated flows
            for stock_name, stock in self.stocks.items():
                stock.update(self.dt)

            # 7. Advance time
            self.time += self.dt

        return self.history