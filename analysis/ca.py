import random
import numpy as np
from typing import List, Tuple
from higherorder.structures import Grid
from higherorder.utils.utils import blobs

def _setup_grid(grid:Grid | np.ndarray = None,
                size:int = 10,
                ) -> Grid | np.ndarray:
    """
    Sets up the grid for random blob generation.
    """
    if isinstance(grid, np.ndarray):
        width = grid.shape[0]
        height = grid.shape[1]
        raise NotImplementedError("Array form not implemented yet")
    elif grid is None:
        grid = Grid(np.zeros((2*size, 2*size)))
    
    return grid

def random_1_blob(grid:Grid | np.ndarray = None,
                  size:int = 10,
                  return_array = False,
                  key = None,
                  seed = 1) -> Grid | np.ndarray:
    """
    Generates a random 1 blob (connected component) with a given size.
    """
    random.seed(seed)
    grid = _setup_grid(grid, size)
    
    #TODO make it possible to start with non-zero grid and generate still
    candidates = [] #TODO check nonzero in key?
    nonzero_cells = []
    for i in range(size):
        if i==0:
            cell = random.choice(list(grid.get_entities().keys()))
        else:
            cell = random.choice(candidates)
        nonzero_cells.append(cell)
        #TODO speed this up by only checking the new cell's neighbours
        candidates = grid.get_entities_neighbours(nonzero_cells, external_only = True,
                                                  duplicate_removal = True)
        #TODO do a different version where duplicates are not removed, and their quantities weight the chance inversely
    
    if not key:
        key = "t_0"
    for cell in nonzero_cells:
        grid.entities[cell][key] = 1
            
    return grid

def blob_random_inner_line(blob, slope_candidates = [0, np.inf],
                           slope_interval_length = 6, seed = 1):
    """
    The cells here are represented as points by their coordinates

    If slope == np.inf, then the line is vertical
    """
    random.seed(seed)
    if slope_candidates:
        slope = random.choice(slope_candidates)
    else:     
        slope = random.uniform(-slope_interval_length/2, slope_interval_length/2)

    v = np.array([1/((1+slope**2)**0.5), slope/((1+slope**2)**0.5)]) if slope != np.inf else np.array([0, 1])
    distances = []
    for point in blob:
        # point - projection gives the "distance vector"
        projection = np.dot(v, np.array(point)) * v
        deviation = np.array(point) - projection
        distance_signed = np.linalg.norm(deviation) * np.sign(np.cross(np.append(v,0), np.append(deviation,0))[-1])
        distances.append(distance_signed)
    min_d, max_d = min(distances), max(distances)
    d = random.uniform(min_d, max_d)

    if slope == np.inf:
        other_param = -d #TODO derive correctness
    else:
        other_param = d * (np.sqrt(1+slope**2))# d*cos(theta)
    return slope, other_param #this is (m,b) for mx+b for every slope, except for vertical lines, where it is (np.inf, c) for x=c

def shift_grid_entities(entities, dimension_size, axis = 0,
                        direction = 1, amount = 1):
    if type(dimension_size) == tuple:
        dimension_size = dimension_size[axis]
    entities = [np.array(entity) for entity in entities]

    for entity in entities:
        entity[axis] = (entity[axis] + direction*amount) % dimension_size
    return [tuple(entity) for entity in entities]

def split_random_blob(components: List[tuple],
                      distance:int = 3,
                      grid_dimensions: tuple = None,
                      grid:Grid | np.ndarray = None,
                      seed = 1) -> Grid | np.ndarray:
    """
    Splits a randomly chosen blob into two blobs with a given distance between them.
    """
    random.seed(seed)
    if type(components[0]) != list:
        components = [components]
    component = random.choice(components)

    if not grid_dimensions:
        grid_dimensions = (grid.width, grid.height)
    m, b = blob_random_inner_line(component, slope_candidates = [], seed = seed)
    above, below = [(x,y) for x,y in component if y >= m*x + b], [(x,y) for x,y in component if y < m*x + b]
    
    for i in range(distance):
        axis = random.choice([-1, 1]) #"vertical", "horizontal"
        direction = random.choice([-1, 1])
        slope_x_direction_factor = -1 if axis == -1 and m < 0 else 1
        if axis * direction == 1:
            above = shift_grid_entities(above, grid_dimensions, axis = 1 if axis == 1 else 0,
                                        direction = direction*slope_x_direction_factor, amount = 1)
        else:
            below = shift_grid_entities(below, grid_dimensions, axis = 1 if axis == 1 else 0,
                                        direction = direction*slope_x_direction_factor, amount = 1)
    
    return above, below

def random_2_blob(grid:Grid | np.ndarray = None,
                  size_total:int = 10,
                  distance:int = 3,
                  return_array = False,
                  key = None,
                  seed = 1,
                  return_components = False) -> Grid | np.ndarray:
    """
    Generates a random 2 blob (connected component) with a given size.
    """
    random.seed(seed)
    grid = random_1_blob(grid, size_total, return_array, key, seed)
    component = random.choice(blobs(grid, key_name = key))
    #TODO cut the blob into two (e.g. along a horizontal or vertical line) and shift away one of the parts
    #set its original cells to 0, and set the new cells (above, below) to 1
    above, below = split_random_blob(component, distance, grid_dimensions = (grid.width, grid.height), seed = seed)
    for cell in component:
        grid.entities[cell][key] = 0
    for cell in above+below:
        grid.entities[cell][key] = 1

    if return_components:
        return grid, component, above, below
    return grid