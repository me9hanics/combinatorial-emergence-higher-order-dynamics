from typing import Dict, Callable, Any, List, Tuple
import datetime
from higherorder.structures.structures import Structure, Grid, Graph

def get_nonzero_entities(entities: Dict,
                         key = None):
    if key:
        entities = {k: v[key] for k, v in entities.items()}

    nonzero_entities = {}
    for entity, value in entities.items():
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