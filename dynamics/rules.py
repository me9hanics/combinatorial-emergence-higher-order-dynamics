from typing import Dict, Callable, Any, List, Tuple
from higherorder.structures.structures import Structure, Grid, Graph
##rule (dynamics logic) functions

def general_rule(structure: Structure,
                 rule_function:Callable,
                 key_name:str = None,
                 #entities: Dict,
                 #connections_LUT: Dict,
                 only_nonzero=False,
                 only_state_change=False):
    entities = structure.get_entities()
    connections_LUT = structure.get_entities_connections_LUT()
    if key_name:
        for entity, values in entities.items():
            if key_name not in values:
                entities[entity][key_name] = 0
        entities = {k: v[key_name] for k, v in entities.items()}
    states = rule_function(entities = entities, connections_LUT = connections_LUT,
                           structure = structure)
    pass
    
def copy_below(entities: Dict = None,
               connections_LUT: Dict = None,
               structure: Grid = None,
               ):
    """
    Only for Grid structure
    """
    height = structure.height
    if not entities:
        entities = structure.get_entities()
    new_states = {(x,y): entities[((x+1)%height,y)] for x,y in entities.keys()}
    if not structure.periodic_boundary:
        for (x,y), state in new_states.items():
            if x == height-1:
                new_states[(x,y)] = 0
    return new_states

def game_of_life(entities: Dict = None,
                 connections_LUT: Dict = None,
                 structure: Structure = None
                 ):
    """
    Rule function for Conway's Game of Life.

    1. Any live cell with fewer than two live neighbors dies (underpopulation).
    2. Any live cell with two or three live neighbors lives on to the next generation.
    3. Any live cell with more than three live neighbors dies (overpopulation).
    4. Any dead cell with exactly three live neighbors becomes a live cell (reproduction).
    """
    if not entities:
        entities = structure.get_entities()
    if not connections_LUT:
        connections_LUT = structure.get_entities_connections_LUT()

    new_states = {}
    entities = {k: 0 if v <= 0 else 1 for k, v in entities.items()}
    for entity in entities.keys():
        neighbors = connections_LUT[entity]
        live_neighbors = sum(entities[neighbor] for neighbor in neighbors if neighbor in entities)
        if entities[entity] == 1:
            if live_neighbors < 2 or live_neighbors > 3:
                new_states[entity] = 0
            else:
                new_states[entity] = 1
        else:
            if live_neighbors == 3:
                new_states[entity] = 1
            else:
                new_states[entity] = 0
    return new_states