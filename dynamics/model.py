from higherorder.structures.structure import Grid, Graph, Structure

class Model:
    def __init__(self, structure: Grid | Graph,
                 rule_function: function,
                 initial_time_step=0, property_name="t_",
                 store_mode='sparse', initial_state=None):
        """
        Takes in a structure, with initial values (possibly included in the structure), and a rule function
        
        - structure: a Structure class object (currently Grid or Graph)
        - rule_function: a function typically defined in rules.py, containing the logic for updating states of entities
        """
        self.structure = structure
        self.rule_function = rule_function
        self.state = {}  # {timestep: {entity: value}} or vice versa
        self.current_time = 0
        self.store_mode = store_mode  # 'full', 'sparse', 'none'
        #self._init_state(initial_state)

    #def _init_state(self, initial_state):
    #    self.state[0] = initial_state

    def step(self):
        pass

    def simulation(self, steps=10):
        pass
        #for _ in range(steps):
        #    self.step()

