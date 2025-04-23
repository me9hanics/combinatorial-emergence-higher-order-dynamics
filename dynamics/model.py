from higherorder.structures.structures import Grid, Graph, Structure
from .rules import general_rule
from typing import Dict, Tuple, Any, Callable, Union

class Model:
    def __init__(self, structure: Grid | Graph,
                 dynamics_func: Callable,
                 time_step: int = None, base_name: str = None,
                 #initial_state=None
                 ):
        """
        Takes in a structure, with initial values (possibly included in the structure), and a rule function
        
        - structure: a Structure class object (currently Grid or Graph)
        - dynamics_func: a function typically defined in rules.py, containing the logic for updating states of entities
        - time_step: The previous (discrete) timestep, simulation starts from one value above it. Default is 0
        - base_name: The base name for the key in the structure. Default is None, which is automatically set to either
                "t_" or structure.key_name[base_name].

        #TODO store_mode='sparse',
        #TODO initial_state?
        """
        #if not isinstance(structure, Structure):
        #    raise ValueError(f"Structure must be an instance of Structure class, not {type(structure)}")

        if isinstance(base_name, type(None)):
            base_name = getattr(structure, 'key_name', {}).get('base_name', "t_")

        if isinstance(time_step, type(None)):
            time_step = getattr(structure, 'last_iterations', {}).get(base_name, 0)
        
        self.structure = structure
        #self.entities = structure.get_entities()
        #self.connections
        self.dynamics_func = dynamics_func
        self.base_name = base_name
        self.time_step = time_step
        self.initial_time_step = time_step

    def simulation(self, steps=10,
                   time_step = None,
                   base_name = None,
                   only_nonzero=False,
                   only_state_change=False):
        if isinstance(base_name, type(None)):
            base_name = getattr(self.structure, 'key_name', {}).get('base_name', "t_")

        if isinstance(time_step, type(None)):
            time_step = getattr(self.structure, 'last_iterations', {}).get(base_name, 0)
        
        key_name = base_name + str(time_step)
        if not any([key_name in v for v in self.structure.entities.values()]):
            raise ValueError(f"Key name {key_name} not found in some structure entities.")
        
        states = self.structure.get_entities()
        states = {k: v[key_name] for k, v in states.items()}
        connections_LUT = self.structure.get_entities_connections_LUT()
        #self.initial_key_name = key_name #TODO rethink
        #self.initial_time_step = time_step
        for i in range(1, steps+1):
            states = general_rule(
                        rule_function=self.dynamics_func,
                        #structure=self.structure,
                        #field_name = key_name,
                        entities=states,
                        connections_LUT=connections_LUT,
                        only_nonzero=only_nonzero,
                        only_state_change=only_state_change,
                     )
            key_name = base_name + str(time_step + i)
            for entity, value in self.structure.entities.items():
                #TODO handle only_state_change=True
                if entity not in states: 
                    #TODO: fix bug - some entities go "beyond" the grid (e.g. instead of going around)
                    self.structure.entities[entity] = {}
                self.structure.entities[entity][key_name] = states[entity]
            self.structure.last_iterations[base_name] = time_step + i
            self.key_name = {"base_name": base_name, "index": time_step + i}
            self.time_step = time_step + i
        #return self.structure.entities, self.structure.last_iterations, self.key_name
