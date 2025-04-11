import numpy as np
import networkx as nx
from typing import List, Tuple, Dict, Any

def get_nonzero_entities(array: np.ndarray) -> List[Tuple[int, int]]:
    """
    Returns the entities with non-zero value as a dict.
    """
    #TODO: Generalize, put in Structure class
    return {e:array[e] for e in np.ndindex(array.shape) if array[e] != 0} 

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
    def __init__(self, initial_values=None):
        self.entities = self.define_entities()
        self.connections = self.define_connections()
        raise NotImplementedError
    
    def define_entities(self):
        raise NotImplementedError

    def define_connections(self):
        raise NotImplementedError
    
    def get_entities(self):
        return self.entities
    
    def get_connections(self):
        return self.connections
    

class Grid(Structure):
    """
    Grid structure, defined width, height, initial values, and connections
        (depending on periodic boundary and diagonal neighbors).
    """
    def __init__(self, initial_values: np.ndarray | Dict[Tuple[int, int], Any] = None,
                 width: int = None, height: int = None,
                 periodic_boundary: bool = True, diagonal_neighbours: bool = True):
        """
        Initialize a grid structure.
        TODO: left_top_corner
        """
        
        if isinstance(initial_values, np.ndarray):
            width, height = initial_values.shape
            #left_top_corner = (0, 0)
        elif isinstance(initial_values, dict):
            #Assuming the dictionary keys are tuples (x, y) of positive coordinates
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
        
        entities = self.define_entities(initial_values, width, height)
        connections = self.define_connections(width, height, periodic_boundary, diagonal_neighbours)

        self.entities = entities
        self.connections = connections
        self.width = width
        self.height = height
        self.periodic_boundary = periodic_boundary
        self.diagonal_neighbours = diagonal_neighbours


    def define_entities(self, initial_values, width, height):
        entities = {(x,y):{"t0":0} for x in range(width) for y in range(height)}
        if isinstance(initial_values, dict):
            for (x,y), value in initial_values.items():
                if (x,y) in entities:
                    initial_values[(x,y)]["t0"] = value
                else:
                    raise ValueError(f"Initial value for ({x},{y}) is not in the grid.")
        elif isinstance(initial_values, np.ndarray):
            for x in range(width):
                for y in range(height):
                    entities[(x,y)]["t0"] = initial_values[x,y]
        return entities
    
    def define_connections(self, width, height, periodic_boundary, diagonal_neighbours):
        """
        Define the connections of the grid structure.

        If diagonal_neighbours is True, diagonal connections are added (the so-called Moore neighborhood).
            If False, only the side neighbors are added (the so-called von Neumann neighborhood).

        If periodic_boundary is True, the grid is treated as a torus (edges of the complete grid are connected).
            If False, the grid ends are not connected, the grid is treated as a rectangle.
        """
        #TODO remove duplicate connections in case of short side (e.g. 2xN grid)
        connections = []
        horizontal = [((x, y), (x + 1, y)) for x in range(width - 1) for y in range(height)]
        vertical = [((x, y), (x, y + 1)) for x in range(width) for y in range(height - 1)]
        
        if periodic_boundary:
            horizontal += [((width - 1, y), (0, y)) for y in range(height)]
            vertical += [((x, height - 1), (x, 0)) for x in range(width)]

        connections += horizontal + vertical

        if diagonal_neighbours:
            diagonal = [((x, y), (x + 1, y + 1)) for x in range(width - 1) for y in range(height - 1)]
            diagonal += [((x, y), (x + 1, y - 1)) for x in range(width - 1) for y in range(1, height)]
            if periodic_boundary:
                diagonal += [((x, height - 1), (x + 1, 0)) for x in range(width - 1)]
                diagonal += [((width - 1, y), (0, y + 1)) for y in range(height - 1)]
                diagonal += [((width - 1, height - 1), (0, 0))]
                diagonal += [((width - 1, 0), (0, height - 1))]
            connections += diagonal

        return connections

    def get_time_slice(self, T)->np.ndarray:
        pass





class Graph(Structure):
    def __init__(self, G: nx.Graph,
                 initial_values=None,
                 time_step=0,
                 property_name="t_",
                 ):
        """
        Initialize a graph structure.
        """
        initial_property_name = property_name + str(time_step)
        if initial_values:
            if not isinstance(initial_values, dict):
                raise ValueError(f"Initial values must be a dictionary of node: value pairs, not {type(initial_values)}")
            for node, value in initial_values.items():
                if node not in G.nodes:
                    raise ValueError(f"Node {node} is not in the graph.")
                G.nodes[node][initial_property_name] = value
        
        for node in G.nodes:
            if initial_property_name not in G.nodes[node]:
                G.nodes[node][initial_property_name] = 0

        self.entities = G.nodes(data=True)
        self.connections = G.edges(data=True)
