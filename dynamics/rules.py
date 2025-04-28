from typing import Dict, Callable#, Any, List, Tuple
from higherorder.structures.structures import Structure, Grid, Graph
from higherorder.utils.utils import get_nonzero_entities
##rule (dynamics logic) functions

def general_rule(rule_function:Callable,
                 structure: Structure = None,
                 field_name:str = None,
                 entities: Dict = {},
                 connections_LUT: Dict = {},
                 only_nonzero=False,
                 only_state_change=False,
                 **kwargs):
    if not entities:
        entities = structure.get_entities()
    if not connections_LUT:
        connections_LUT = structure.get_entities_connections_LUT()

    if field_name:
        for entity, values in entities.items():
            if field_name not in values:
                entities[entity][field_name] = 0
        entities = {k: v[field_name] for k, v in entities.items()}
    states = rule_function(entities = entities, connections_LUT = connections_LUT,
                           structure = structure, **kwargs)
    if only_nonzero:
        states = get_nonzero_entities(states)
    if only_state_change:
        states = {k: v for k, v in states.items() if k in entities and entities[k] != v}
    return states
    
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

def operations_in_sequence(sequence: list,
                           entities: Dict = None,
                           connections_LUT: Dict = None,
                           structure: Structure = None,
                           operations: str = "copy"):
    """
    Rule function that applies a sequence of steps deterministically.

    Args:
        sequence: List of (A,B, operation) tuples (where A and B are entities),
                representing the A->B operations in order  
        entities: Current states of the entities.
        connections_LUT: Lookup table for connections between entities.
        structure: The structure containing entities and connections.
    """
    if not entities:
        entities = structure.get_entities()
    if not connections_LUT:
        connections_LUT = structure.get_entities_connections_LUT()
    new_states = entities.copy()

    for step in sequence:
        source = step[0]
        target = step[1]
        operation = step[2] if len(step) > 2 else operations

        if operation == "copy":
            new_states[target] = new_states[source]
        elif operation == "copy_from":
            new_states[source] = new_states[target]
        elif operation == "add":
            new_states[target] += new_states[source]
        elif operation == "subtract":
            new_states[target] -= new_states[source]
        elif operation == "replace":
            new_states[target] = new_states[source]
            new_states[source] = 0
        elif operation == "swap":
            new_states[source], new_states[target] = new_states[target], new_states[source]
        elif type(operation) == function:
            new_states[source], new_states[target] = operation(source_value = new_states[source],
                                                               target_value = new_states[target])

    return new_states

def copy_below(entities: Dict = None,
               connections_LUT: Dict = None,
               structure: Grid = None,
               ):
    """
    Only for Grid structure - copy the state of the entity below the current one.
    """
    height = structure.height
    if not entities:
        entities = structure.get_entities()
    new_states = {
        (x, y): 0 if (x == height - 1) and (not structure.periodic_boundary)
                  else entities[((x + 1) % height, y)] for x, y in entities.keys()
    }
    return new_states