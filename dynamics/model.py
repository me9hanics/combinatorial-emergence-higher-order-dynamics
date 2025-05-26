from higherorder.structures.structures import Grid, Graph, Structure
from .rules import general_rule
from typing import Dict, Tuple, Any, Callable, Union
from .impacts import general_impact

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
        self.impact = {}
        self.has_ended = False #TODO keep resetting it to False

    def _setup_key_name(self, time_step=None, base_name=None, raise_error=True):
        if isinstance(base_name, type(None)):
            base_name = getattr(self.structure, 'key_name', {}).get('base_name', "t_")

        if isinstance(time_step, type(None)):
            time_step = getattr(self.structure, 'last_iterations', {}).get(base_name, 0)
        
        key_name = base_name + str(time_step)
        if not any([key_name in v for v in self.structure.entities.values()]):
            if raise_error:
                raise ValueError(f"Key name {key_name} not found in some structure entities\
                             - possibly not initialized, or the simulation")
            else:
                return None, None, None
        return key_name, base_name, time_step

    def step(self, rule_function: Callable = None,
             entity_states: Dict = None,
             connections_LUT: Dict = None,
             only_nonzero: bool = False,
             only_state_change: bool = False,
             base_name: Dict = None,
             time_step: int = None,
             store_impact: bool = False,
             impact_function: Callable = None,
             active_only: bool = True,
             ):
        #TODO: store_impact
        key_name, base_name, time_step = self._setup_key_name(time_step, base_name, raise_error=False)
        if key_name is None:
            return None
        rule_function = rule_function or self.dynamics_func
        entity_states = entity_states or {k: v[key_name] for k, v in self.structure.entities.items()}
        connections_LUT = connections_LUT or self.structure.get_entities_connections_LUT()

        if store_impact:
            impacts = general_impact(impact_function=impact_function,
                                     structure=self.structure,
                                     field_name = None,
                                     entities=entity_states,
                                     connections_LUT=connections_LUT,
                                     active_only=active_only,
                                    )
            #take dict, sorted by key
            self.impact[key_name] = {k: v for k, v in sorted(impacts.items(), key=lambda item: item[0])}
            
        states = general_rule(rule_function=rule_function,
                        structure=self.structure,
                        #field_name = None, #key_name,
                        entities=entity_states,
                        connections_LUT=connections_LUT,
                        only_nonzero=only_nonzero,
                        only_state_change=only_state_change,
                     )
        if not states:
            self.has_ended = True
        previous_key_name = key_name
        key_name = base_name + str(time_step + 1)
        if only_state_change:
            #TODO construct the correct states dict
            raise NotImplementedError("only_state_change=True not implemented yet")
            for entity, value in states.items():
                self.structure.entities[entity][key_name] = self.structure.entities[entity][previous_key_name]
        for entity, value in states.items():
            if entity not in self.structure.entities:
                #TODO: fix bug - some entities go "beyond" the grid (e.g. instead of going around)
                self.structure.entities[entity] = {}
            self.structure.entities[entity][key_name] = states[entity]
        self.structure.last_iterations[base_name] = time_step + 1
        self.key_name = {"base_name": base_name, "index": time_step + 1}
        self.time_step = time_step + 1
        return states

    def simulation(self, steps=10,
                   time_step = None,
                   base_name = None,
                   only_nonzero=False,
                   only_state_change=False,
                   store_impact=False,
                   impact_function=None,
                   active_only=True,):
        key_name, base_name, time_step = self._setup_key_name(time_step, base_name)
        states = {k: v[key_name] for k, v in self.structure.get_entities().items()}
        connections_LUT = self.structure.get_entities_connections_LUT()
        #self.initial_key_name = key_name #TODO rethink
        #self.initial_time_step = time_step
        for i in range(0, steps):
            states = self.step(
                        rule_function = self.dynamics_func,
                        entity_states = states,
                        connections_LUT = connections_LUT,
                        only_nonzero = only_nonzero,
                        only_state_change = only_state_change,
                        base_name = base_name,
                        time_step = time_step + i,
                        store_impact = store_impact,
                        impact_function = impact_function,
                        active_only = active_only,
                     )
            if not states:
                self.has_ended = True #TODO keep resetting it to False
                break
        self.last_simulation_step = time_step + i + 1
        #return self.structure.entities, self.structure.last_iterations, self.key_name

    def simulate_till_periodicity(self, 
                                 time_step = None,
                                 base_name = None,
                                 only_nonzero = True,
                                 only_state_change = False,
                                 max_steps=1000,
                                 store_impact=False,
                                 impact_function=None,
                                 active_only=True,
                                 ):
        key_name, base_name, time_step = self._setup_key_name(time_step, base_name)
        states = {k: v[key_name] for k, v in self.structure.get_entities().items()}
        connections_LUT = self.structure.get_entities_connections_LUT()

        states_topology = self.structure.get_components_topology_representation(entities=states,
                                                                                only_nonzero = only_nonzero,
                                                                                )
        states_topologies = []
        steps = 0
        while (states_topology not in states_topologies) and (steps < max_steps):
            states_topologies.append(states_topology)
            states = self.step(
                        rule_function = self.dynamics_func,
                        entity_states = states,
                        connections_LUT = connections_LUT,
                        only_nonzero = only_nonzero,
                        only_state_change = only_state_change,
                        base_name = base_name,
                        time_step = time_step + steps,
                        store_impact = store_impact,
                        impact_function = impact_function,
                        active_only = active_only,
                     )
            states_topology = self.structure.get_components_topology_representation(entities=states,
                                                                                    only_nonzero = only_nonzero,
                                                                                    )
            steps += 1
        self.last_simulation_step = time_step + steps
        #return states_topologies, steps, states

    def get_impact(self, impacts:Dict = None,
                   timestep_name:str = None,
                   impact_type:str = None,
                   redundancy = False):
        #TODO make impact_type a list
        if impacts is None:
            impacts = getattr(self, 'impact', None)
        if not impacts:
            print("No impacts stored")
            return None
        
        if redundancy:
            impacts = {t: {k: w for k, w in v.items() if "redundancy" in w}
                       for t, v in impacts.items()}

        if impact_type is not None:
            if impact_type == 'active':
                active_types = ["kill", "redundancy_kill", "birth", "no_birth", "redundancy_live"]
                impacts = {t: {k: w for k, w in v.items() if w in active_types}
                           for t, v in impacts.items()}
            else:
                impacts = {t: {k: w for k, w in v.items() if w == impact_type}
                           for t, v in impacts.items()}

        if timestep_name is not None:
            impacts = impacts[timestep_name]
        #TODO if impact_type is a string, then just return the list of such impacts

        return impacts