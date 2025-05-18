from typing import Dict, Callable#, Any, List, Tuple
from higherorder.structures.structures import Structure, Grid, Graph
##rule (dynamics logic) functions

def general_impact(impact_function:Callable,
                 structure: Structure = None,
                 field_name:str = None,
                 entities: Dict = {},
                 connections_LUT: Dict = {},
                 active_only: bool = True,
                 #only_nonzero=False,
                 #only_state_change=False,
                 **kwargs):
    if not entities:
        entities = structure.get_entities()
    if not connections_LUT:
        connections_LUT = structure.get_entities_connections_LUT()

    #only taking active entities
    if field_name:
        entities = {k: v[field_name] for k, v in entities.items() if field_name in v}
    if structure:
        for entity in structure.get_entities():
            if entity not in entities:
                entities[entity] = 0
    elif connections_LUT:
        for entity in connections_LUT.keys():
            if entity not in entities:
                entities[entity] = 0
    impacts = impact_function(entities = entities, connections_LUT = connections_LUT,
                              tructure = structure, active_only = active_only, **kwargs)
    return impacts
    
def game_of_life_impact(entities: Dict = None,
                 connections_LUT: Dict = None,
                 structure: Structure = None,
                 active_only: bool = True,
                 **kwargs):
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

    impacts = {}
    entities = {k: 0 if v <= 0 else 1 for k, v in entities.items()}
    for entity in entities.keys():
        state = entities[entity]
        neighbors = connections_LUT[entity]
        if (state == 0):
            if active_only:
                continue
            else:
                for neighbor in neighbors:
                    neighbor_state = entities[neighbor]
                    neighbor_other_neighbors = sum(entities[other] for other in connections_LUT[neighbor])
                    #TODO Rethink this
                    if neighbor_state == 1 and neighbor_other_neighbors == 1:
                        impacts[(entity, neighbor)] = "nonactive_kill"
                    if neighbor_state == 1 and neighbor_other_neighbors == 3:
                        impacts[(entity, neighbor)] = "nonactive_live"
                    if neighbor_state == 1 and neighbor_other_neighbors == 2:
                        impacts[(entity, neighbor)] = "nonactive_redundancy_live"#not necessary
                    if neighbor_state == 0 and neighbor_other_neighbors == 3:
                        impacts[(entity, neighbor)] = "nonactive_birth"
                    if neighbor_state == 0 and neighbor_other_neighbors == 2:
                        impacts[(entity, neighbor)] = "nonactive_no_birth"
        else:            
            for neighbor in neighbors:
                #assuming state is 1
                neighbor_state = entities[neighbor]
                neighbor_other_live_neighbors = sum(entities[other] for other in connections_LUT[neighbor]) - state #-1
                if neighbor_state == 1 and neighbor_other_live_neighbors == 3:
                    impacts[(entity, neighbor)] = "kill"
                if neighbor_state == 1 and neighbor_other_live_neighbors > 3:
                    impacts[(entity, neighbor)] = "redundancy_kill"
                if neighbor_state == 0 and neighbor_other_live_neighbors == 1:
                    impacts[(entity, neighbor)] = "birth"
                if neighbor_state == 0 and neighbor_other_live_neighbors == 3:
                    impacts[(entity, neighbor)] = "no_birth"
                #no "redundancy_birth"
                if neighbor_state == 1 and neighbor_other_live_neighbors == 2:
                    impacts[(entity, neighbor)] = "redundancy_live"

    return impacts