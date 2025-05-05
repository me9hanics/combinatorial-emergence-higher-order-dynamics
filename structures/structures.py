import numpy as np
import networkx as nx
import copy
from typing import List, Tuple, Dict, Generator, Any

class Structure:
    """
    To gather:
        - the entities, including their initial values,
        - the connections (a function to get the neighbors of entities)

    Currently, the entities dict (stored in self.entities) stores every entity as key, and the values
        are every timestep t0, t1, t2, ... values
    There is consideration to rather store the nonzero values at each time step instead.
    #TODO: t "time slices": should be a dict of times t0, t1, t2, ... storing the nonzero values
    """
    def __init__(self, initial_values=None,
                 time_step: int = 0, base_name: str = "t_",):
        self.entities = self.initialize_entities()
        self.connections = self.initialize_connections()

        key_name = {"base_name":base_name, "index":time_step}
        self.key_name = key_name #TODO rethink, generalize to dict of key names
        self.initial_key_name = base_name + str(time_step)
        self.initial_time_step = time_step
        self.last_iterations = {base_name:time_step}
        if initial_values:
            raise NotImplementedError()
    
    def initialize_entities(self):
        raise NotImplementedError

    def initialize_connections(self):
        raise NotImplementedError
    
    def get_entities(self)-> Dict:
        return self.entities.copy()
    
    def get_connections(self)-> List[Tuple[Any, Any]]:
        return self.connections.copy()
    
    def get_nonzero_entities(self, base_name: str = "t_",
                             t:int = None, initial_time_step: int = None,
                             verbose: bool = True): #-> Generator[Tuple[Any, Any], None, None]: 
        """
        Returns the entities with non-zero value at timestep t.

        If setting `base_name` directly to the key which stores the respective values,
            then `t` and `initial_time_step` shall be None.
        Otherwise, `t` is the timestep to check for non-zero values counting from `initial_time_step`,
            and the property is assumed to be `base_name` + str(t+initial_time_step).
        """
        if t is None and initial_time_step is None:
            base_name = base_name #TODO
        if isinstance(t, int):
            if not isinstance(initial_time_step, int):
                initial_time_step = 0
            base_name = base_name + str(t+initial_time_step)

        nonzero_entities = {}
        for entity, values in self.entities.items():
            if base_name not in values:
                if verbose:
                    print(f"Entity {entity} does not have key {base_name} property.")
            elif values[base_name]:
                nonzero_entities[entity] = values[base_name]
                #TODO consider using yield: yield entity, values[base_name]
        return nonzero_entities

    def get_entity_connections(self, entity):
        """
        Returns the connections of the given entity.
        """
        if entity not in self.entities.keys():
            raise ValueError(f"Entity {entity} is not in the structure.")
        connections = []
        for connection in self.get_connections():
            if entity in connection:
                connections.append(connection)
        return connections
    
    def get_entities_connections_LUT(self, duplicate_removal = True):
        """
        Returns a lookup table of the connections of each entity.
        """
        connections_LUT = {}
        for entity_A, entity_B in self.get_connections():
            if entity_A not in connections_LUT:
                connections_LUT[entity_A] = []
            if entity_B not in connections_LUT:
                connections_LUT[entity_B] = []
            connections_LUT[entity_A].append(entity_B)
            connections_LUT[entity_B].append(entity_A)
        #Remove duplicates (theoretically not needed, but for safety)
        if duplicate_removal:
            for entity, connections in connections_LUT.items():
                connections_LUT[entity] = list(set(connections))
        return connections_LUT
    
    def get_time_slice(self, key_name:str="t_0", fill_missing = False)->np.ndarray:
        entities = self.get_entities()
        if fill_missing:
            entities = {entity:values[key_name] if key_name in values else 0 for entity, values in entities.items()}
        else:
            entities = {entity:values[key_name] for entity, values in entities.items() if key_name in values}
        return entities

    def get_entity_sorted_values(self, entity, base_name:str="t_"):
        """
        Returns dynamic values of an entity, sorted by time
        """
        if entity not in self.get_entities().keys():
            raise ValueError(f"Entity {entity} is not in the structure.")
        values = ([{key:value} for key, value in self.entities[entity].items() if key.startswith(base_name)])
        return sorted(values, key=lambda x: int(next(iter(x)).split(base_name)[1]))

    def get_components_topology_representation(self, key_name:str="t_0"):
        """
        Take each component and "reduce" them to a representation of their topology that
                is easier to deal with - e.g. move by the center of mass, fix orientation
        """
        pass

    def to_dict(self) -> Dict:
        """
        For saving structures to a file
        """
        raise NotImplementedError()
    
    def __deepcopy__(self, memo):
        """
        Generated code
        """
        cls = self.__class__
        new_instance = cls.__new__(cls)
        memo[id(self)] = new_instance  # Avoid infinite recursion for circular references
        for key, value in self.__dict__.items():
            setattr(new_instance, key, copy.deepcopy(value, memo))
        return new_instance

class Grid(Structure):
    """
    Grid structure, defined width, height, initial values, and connections
        (depending on periodic boundary and diagonal neighbors).
    """
    #TODO fix array 
    def __init__(self, initial_values: np.ndarray | Dict[Tuple[int, int], Any] = None,
                 width: int = None, height: int = None,
                 periodic_boundary: bool = True, diagonal_neighbours: bool = True,
                 time_step: int = 0, base_name: str = "t_"):
        """
        Initialize a grid structure.
        TODO: left_top_corner
        """
        
        initial_values, width, height = self._setup_initialization(initial_values, width, height)

        key_name = {"base_name":base_name, "index":time_step}
        initial_key_name = base_name + str(time_step)
        entities = self.initialize_entities(initial_values, width, height, initial_key_name)
        connections = self.initialize_connections(width, height, periodic_boundary, diagonal_neighbours)

        self.key_name = key_name #TODO rethink, generalize to dict of key names
        self.initial_key_name = initial_key_name
        self.initial_time_step = time_step
        self.last_iterations = {base_name:time_step}
        self.entities = entities
        self.connections = connections
        self.width = width
        self.height = height
        self.periodic_boundary = periodic_boundary
        self.diagonal_neighbours = diagonal_neighbours

    def _setup_initialization(self, initial_values, width, height):
        if isinstance(initial_values, np.ndarray):
            if not width:   
                width = initial_values.shape[0]
            if not height:
                height = initial_values.shape[1]
            #left_top_corner = (0, 0)
        elif isinstance(initial_values, dict):
            """Assuming the dictionary keys are tuples (x, y) of positive coordinates"""
            #TODO check for negative coordinates
            max_x = max(x for x, _ in initial_values.keys())
            max_y = max(y for _, y in initial_values.keys())
            if not width:
                width = max_x + 1
            elif width < max_x + 1:
                raise ValueError(f"Width {width} is smaller than the maximum x coordinate {max_x}.")
            if not height:
                height = max_y + 1
            elif height < max_y + 1:
                raise ValueError(f"Height {height} is smaller than the maximum y coordinate {max_y}.")
            #left_top_corner = (min(x for x, _ in initial_values.keys()), min(y for _, y in initial_values.keys()))
        elif not initial_values:
            #reconsider of how to "cooperate" with the left_top_corner parameter once implemented
            if not isinstance(width, int) or not isinstance(height, int):
                raise ValueError(f"Either proper initial_values is given, or width and height must be provided, as integers")
            initial_values = np.zeros((width, height))
        else:
            raise ValueError(f"Current implementation: initial_values must be numpy array or dict, not {type(initial_values)}")
        return initial_values, width, height
    
    def initialize_entities(self, initial_values, width, height, initial_key_name="t_0"):
        entities = {(x,y):{initial_key_name:0} for x in range(width) for y in range(height)}
        if isinstance(initial_values, np.ndarray):
            from higherorder.utils.utils import array_to_dict #Lazy import to avoid circular import
            initial_values = array_to_dict(initial_values)
        if isinstance(initial_values, dict):
            for (x,y), value in initial_values.items():
                if (x,y) in entities:
                    entities[(x,y)][initial_key_name] = value
                else:
                    raise ValueError(f"Initial value for ({x},{y}) is not in the grid.")
        return entities
    
    def initialize_connections(self, width, height, periodic_boundary, diagonal_neighbours):
        """
        Define the connections of the grid structure.

        If diagonal_neighbours is True, diagonal connections are added (the so-called Moore neighborhood).
            If False, only the side neighbors are added (the so-called von Neumann neighborhood).

        If periodic_boundary is True, the grid is treated as a torus (edges of the complete grid are connected).
            If False, the grid ends are not connected, the grid is treated as a rectangle.
        """
        #TODO remove duplicate connections in case of short side (e.g. 2xN grid)
        connections = []
        horizontal = [((x, y), (x + 1, y)) for x in range(height - 1) for y in range(width)]
        vertical = [((x, y), (x, y + 1)) for x in range(height) for y in range(width - 1)]
        
        if periodic_boundary:
            horizontal += [((height - 1, y), (0, y)) for y in range(width)]
            vertical += [((x, width - 1), (x, 0)) for x in range(height)]

        connections += horizontal + vertical

        if diagonal_neighbours:
            diagonal = [((x, y), (x + 1, y + 1)) for x in range(height - 1) for y in range(width - 1)]
            diagonal += [((x, y), (x + 1, y - 1)) for x in range(height - 1) for y in range(1, width)]
            if periodic_boundary:
                diagonal += [((x, width - 1), (x + 1, 0)) for x in range(height - 1)]
                diagonal += [((x, width - 1), (x - 1, 0)) for x in range(1, height)]
                diagonal += [((height - 1, y), (0, y + 1)) for y in range(width - 1)]
                diagonal += [((height - 1, y), (0, y - 1)) for y in range(1, width)]
                diagonal += [((height - 1, width - 1), (0, 0))]
                diagonal += [((height - 1, 0), (0, width - 1))]
            connections += diagonal

        return connections

    def get_components_topology_representation(self, entities = None, key_name:str=None, orientation = False,
                                               only_nonzero: bool = True):
        """
        Move each component by their center of mass (for simpler comparison of topology),
            and optionally unify orientation.
        """
        from higherorder.utils.utils import blobs #Lazy import to avoid circular import
        if orientation:
            raise NotImplementedError("Orientation not implemented yet.")
        if not entities and not key_name:
            key_name = "t_0"
        #if key_name:
        #    entities = self.get_entities()
        #    entities = {k: v[key_name] for k, v in entities.items()}
        components = blobs(structure=self, entities = entities,
                           connections_LUT = self.get_entities_connections_LUT(),
                           key_name = key_name, only_nonzero=only_nonzero)
        for i, component in enumerate(components.copy()):
            mean_x = np.mean([x for x, y in component])
            mean_y = np.mean([y for x, y in component])
            for j, (x, y) in enumerate(component):
                component[j] = (round(x - mean_x, 7) , round(y - mean_y, 7))
            components[i] = sorted(component, key=lambda coord: (coord[0], coord[1]))
        return sorted(components, key=lambda comp: (comp[0][0], comp[0][1])) #if x else (float('inf'), float('inf'))

    def to_dict(self) -> Dict:
        """
        Convert the grid structure to a dictionary.
        """
        return {
            "structure_type": "Grid",
            "variables": {
                "width": self.width,
                "height": self.height,
                "periodic_boundary": self.periodic_boundary,
                "diagonal_neighbours": self.diagonal_neighbours,
                "key_name": self.key_name.copy(),
                "initial_key_name": self.initial_key_name,
                "initial_time_step": self.initial_time_step,
                "last_iterations": self.last_iterations.copy(),
                "connections": self.get_connections(),
                "entities": self.get_entities(),
            },
        }

class Graph(Structure):
    def __init__(self, G: nx.Graph,
                 initial_values : Dict = None,
                 time_step: int = 0, base_name: str = "t_",
                 ):
        """
        Initialize a graph structure.
        """
        key_name = {"base_name":base_name, "index":time_step}
        initial_key_name = base_name + str(time_step)
        G, entities = self.initialize_entities(G, initial_values = initial_values,
                                               initial_key_name = initial_key_name)

        self.key_name = key_name #TODO rethink, generalize to dict of key names
        self.initial_key_name = initial_key_name
        self.initial_time_step = time_step
        self.last_iterations = {base_name:time_step}
        self.entities = entities
        self.connections = list(G.edges())

    def initialize_entities(self, G, initial_values, initial_key_name="t_0"):
        if initial_values:
            if not isinstance(initial_values, dict):
                raise ValueError(f"Initial values must be a dictionary of node: value pairs, not {type(initial_values)}")
            for node, value in initial_values.items():
                if node not in G.nodes:
                    raise ValueError(f"Node {node} is not in the graph.")
                G.nodes[node][initial_key_name] = value
        
        for node in G.nodes:
            if initial_key_name not in G.nodes[node]:
                G.nodes[node][initial_key_name] = 0
        return G, dict(G.nodes()) #data=True
    
    def initialize_connections(self):
        pass
