from typing import Dict, Callable, Any, List, Tuple #, TYPE_CHECKING
import numpy as np
import json
import datetime
from higherorder.structures.structures import Structure, Grid, Graph
#if TYPE_CHECKING:
#    from higherorder.structures.structures import Structure, Grid, Graph

def get_nonzero_entities(entities: Dict,
                         key = None):
    if key:
        entities = {k: v[key] for k, v in entities.items() if key in v}

    nonzero_entities = {}
    for entity, value in entities.items():
        if type(value) == dict:
            print(f"{entity} has dict as value instead of a number - likely forgot to set key")
        if value != 0:
            nonzero_entities[entity] = value
    return nonzero_entities

def save_structures(structures: List[Graph | Grid],
                    file_path: str,
                    file_name: str = None,
                    ):
    """
    Save structures to a file.
    """
    import os
    import json

    if not file_name:
        file_name = "structures" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"

    structures_dict = {}
    for structure in structures:
        structures_dict[structure.name] = structure.to_dict()

    with open(os.path.join(file_path, file_name), 'w') as f:
        json.dump(structures_dict, f, indent=4)

    #TODO function to turn key-value dict into key-dict{"key_name": value} dict

def save_init_grids(grids: List[Grid],
                    filename: str):
    grids_dict = {} 
    for i, grid in enumerate(grids):
        grids_dict[i] = grid.get_nonzero_entities(string_keys=True)

    with open(filename, 'w') as f:
        json.dump(grids_dict, f, indent=4)

def load_init_grid_dicts(filename,
                         listify = True):
    #TODO grid_format, etc.
    with open(filename, 'r') as f:
        grids_dict = json.load(f)

    for i, grid in grids_dict.items():
        grids_dict[i] = {eval(k): v for k, v in grid.items()}
    if listify:
        return [grid for grid in grids_dict.values()]
    return grids_dict

def dict_to_array(entities: Dict) -> np.ndarray:
    width = max(x for x, _ in entities.keys()) + 1
    height = max(y for _, y in entities.keys()) + 1
    array = np.zeros((width, height))
    for (x, y), value in entities.items():
        array[x, y] = value
    return array

def array_to_dict(array: np.ndarray) -> Dict:
    return {(x, y): array[x, y] for x in range(array.shape[0]) for y in range(array.shape[1])}

def unique_connections(connections: List,
                       undirected = True) -> List:
    """
    Get unique connections from a list of connections.
    """
    unique_connections = []
    for (a,b) in connections:
        if (a,b) not in unique_connections:
            if (not undirected) or ((b,a) not in unique_connections):
                unique_connections.append((a,b))
    return unique_connections

def blobs(structure: Structure = None,
          entities: Dict = None,
          connections_LUT: Dict = None,
          only_nonzero: bool = True,
          key_name: str = None):
    """
    Find connected components (SCCs) of the given structure
    using Tarjan's algorithm (flat, no nested function).
    
    The implementation of the algorithmic part is taken from [1],
    refactored for this usecase with code generative tools.

    Args:
        structure: The structure containing entities and connections.
        entities: The current states of the entities.
        connections_LUT: Lookup table for connections between entities.
        only_nonzero: Whether to only include non-zero entities.
        key_name: Key to extract from entity values.

    Returns:
        A list of strongly connected components (SCCs),
        where each component is a list of entities.

    [1] https://www.geeksforgeeks.org/tarjan-algorithm-find-strongly-connected-components/
    """

    if entities is None:
        entities = structure.get_entities()
    if only_nonzero:
        entities = get_nonzero_entities(entities, key=key_name)
    elif key_name:
        entities = {k: v[key_name] for k, v in entities.items()}
    if connections_LUT is None:
        connections_LUT = structure.get_entities_connections_LUT()
    connections_LUT = {k: v for k, v in connections_LUT.items() if k in entities}
    connections_LUT = {k: [n for n in v if n in entities] for k, v in connections_LUT.items()}

    index_counter = [0]
    indices = {} #Discovered nodes
    low_link = {}
    stack = []
    on_stack = set()
    components = []
    to_visit = [] #(current_node, parent_node, neighbor_index)

    for entity in entities.keys():
        if entity in indices:
            continue
        to_visit.append((entity, None, 0))  

        while to_visit:
            node, parent, neighbor_idx = to_visit.pop()
            if node not in indices:
                indices[node] = index_counter[0]
                low_link[node] = index_counter[0]
                index_counter[0] += 1
                stack.append(node)
                on_stack.add(node)
            neighbors = connections_LUT.get(node, [])

            while neighbor_idx < len(neighbors):
                neighbor = neighbors[neighbor_idx]
                if neighbor not in indices:
                    to_visit.append((node, parent, neighbor_idx + 1))
                    to_visit.append((neighbor, node, 0))
                    break
                elif neighbor in on_stack:
                    low_link[node] = min(low_link[node], indices[neighbor])
                neighbor_idx += 1
            else:
                if parent is not None:
                    low_link[parent] = min(low_link[parent], low_link[node])

                if low_link[node] == indices[node]:
                    #New component
                    component = []
                    while True:
                        w = stack.pop()
                        on_stack.remove(w)
                        component.append(w)
                        if w == node:
                            break
                    components.append(component)
    return components

def get_keys_with_value(input: Dict,
                        value: Any,
                        return_list = True) -> List|Dict:
    """
    Get keys of a dictionary with a specific value.
    """
    if return_list:
        return [k for k, v in input.items() if v == value]
    else:
        return {k: v for k, v in input.items() if v == value}

def flattened_entities_order(entities: List[Tuple] = None,
                             width_height: Tuple[int, int] = None):
    if entities and width_height:
        raise ValueError("Either entities or width_height should be provided, not both.")
    if entities:
        return [(i, j) for i, j in sorted(entities, key=lambda x: (x[0], x[1]))]
    elif width_height:
        return [(i, j) for i in range(width_height[0]) for j in range(width_height[1])]

def entities_time_array(entities: Dict[Tuple, Dict[str, Any]],
                        base_name: str = "t_",
                        extra_dimension: bool = False,
                        return_column_names: bool = False,
                        width_height: Tuple[int, int] = None,
                        ignore_empty: bool = False,
                        ):
    """
    Get entities in time ordering.

    ignore_empty: In the case of no extra dimension, makes the array only have as many columns as
        inputted entities (typically the entities with non-zero values, which may be a subet of all entities).
    """
    if (not width_height):
        width_height = (1 + max(x for x, _ in entities.keys()),
                        1 + max(y for _, y in entities.keys()))
        
    num_entities = len(entities) if ignore_empty and not extra_dimension else width_height[0] * width_height[1]
    #Order: (0,0), (0,1), (0,2), ... (1,0), (1,1), (1,2), ... (2,0), ...
    num_timesteps = 1 + max(int(timesteps.split(base_name)[-1])
                                for states in entities.values()
                                for timesteps in states.keys())
    #entities_in_order = list(entities.keys()) if ignore_empty #every possible entity

    if not extra_dimension:
        arr = np.zeros((num_timesteps, num_entities))
    else:
        arr = np.zeros((num_timesteps, width_height[0], width_height[1]))

    for i, (entity, states) in enumerate(entities.items()):
        entity, states = _, entities[entity]
        values = {k: v for k, v in states.items() if k.startswith(base_name)}
        for time_step, value in values.items():
            t = int(time_step.split(base_name)[1])
            if not extra_dimension:
                arr[t, i] = value
            else:
                arr[t, entity[0], entity[1]] = value
    if return_column_names:
        return arr, list(entities.keys())
    return arr
