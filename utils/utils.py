from typing import Dict, Callable, Any, List, Tuple
import datetime
from higherorder.structures.structures import Structure, Grid, Graph

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
