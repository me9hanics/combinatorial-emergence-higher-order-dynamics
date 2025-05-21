from .stats import *
from .info_measures import *
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Tuple, List

import matplotlib.pyplot as plt
import numpy as np

def plot_grid(entities, width=None, height=None,
              cmap='gray', title=None, show_values=False,
              xlim=None, ylim=None, center=False,
              show_colorbar=False, show_ticks=False):
    """
    Plots a 2D cellular automaton grid from a dictionary of {(x, y): value}.
    
    Parameters:
        entities: dict — keys are (x, y) tuples, values are numerical (0–1)
        width: int — width of grid (optional)
        height: int — height of grid (optional)
        cmap: str — matplotlib colormap (default: 'gray')
        title: str — optional title
        show_values: bool — annotate cells with their value
        xlim: tuple (xmin, xmax) — restrict plot to a range of x
        ylim: tuple (ymin, ymax) — restrict plot to a range of y
        center: bool — center nonzero region in the plot window
        show_colorbar: bool — include colorbar (default: False)
        show_ticks: bool — include axis ticks (default: False)
    """

    if width is not None and height is not None and isinstance(entities, dict):
        entities = {
            (x, y): v for (x, y), v in entities.items()
            if 0 <= x < width and 0 <= y < height
        }

    if not entities:
        raise ValueError("entities must be a non-empty dictionary")
    if isinstance(entities, dict):
        from higherorder.utils.utils import dict_to_array
        arr = dict_to_array(entities, width=width, height=height).copy()
    else:
        arr = np.array(entities).copy()

    arr_height, arr_width = arr.shape

    if not xlim:
        xlim = (0, arr.shape[0])
    if not ylim:
        ylim = (0, arr.shape[1])

    if center:
        # Compute nonzero coordinates
        nonzero_coords = np.array([coord for coord, val in entities.items() if val])
        if nonzero_coords.size > 0:
            x_coords, y_coords = nonzero_coords[:, 0], nonzero_coords[:, 1]
            xmin, xmax = x_coords.min(), x_coords.max()
            ymin, ymax = y_coords.min(), y_coords.max()
            xmid = (xmin + xmax) // 2
            ymid = (ymin + ymax) // 2
            #xlen = xmax - xmin + 1
            xlen = xlim[1] - xlim[0] + 1
            #ylen = ymax - ymin + 1
            ylen = ylim[1] - ylim[0] + 1

            xlim = (xmid - xlen // 2, xmid + xlen // 2 + 1)
            ylim = (ymid - ylen // 2, ymid + ylen // 2 + 1)

    #arr = arr[xlim[0]:xlim[1], :]
    #arr = arr[:, ylim[0]:ylim[1]]
    x0, x1 = max(0, xlim[0]), min(arr.shape[0], xlim[1])
    y0, y1 = max(0, ylim[0]), min(arr.shape[1], ylim[1])
    arr = arr[x0:x1, y0:y1]
    
    fig, ax = plt.subplots()
    cax = ax.imshow(arr.T, cmap=cmap, origin='lower', vmin=0, vmax=1)
    if title:
        ax.set_title(title)
        
    if show_ticks:
        ax.set_xticks(np.arange(arr.shape[0]))
        ax.set_yticks(np.arange(arr.shape[1]))
        ax.set_xticklabels(np.arange(x0, x1))
        ax.set_yticklabels(np.arange(y0, y1))
    else:
        ax.set_xticks([])
        ax.set_yticks([])

    ax.set_xticks(np.arange(-.5, arr.shape[0], 1), minor=True)
    ax.set_yticks(np.arange(-.5, arr.shape[1], 1), minor=True)
    ax.grid(which='minor', color='lightgray', linestyle='-', linewidth=0.5)

    if show_values:
        for (x, y), value in np.ndenumerate(arr):
            ax.text(x, y, f'{value:.1f}', ha='center', va='center', color='red', fontsize=8)

    if show_colorbar:
        fig.colorbar(cax, ax=ax)

    plt.tight_layout()
    plt.show()

def show_pygame_grid(array: np.ndarray, pix_size: int = 20, title: str = "Grid"):
    import pygame
    """
    Displays a grid using pygame. 0 = black, 1 = white, intermediate = grayscale.

    array: np.ndarray — values between 0 and 1
    pix_size: int — size of each cell in pixels
    """
    pygame.init()
    height, width = array.shape
    screen = pygame.display.set_mode((width * pix_size, height * pix_size))
    pygame.display.set_caption(title)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False

        screen.fill((255, 255, 255))
        for y in range(height):
            for x in range(width):
                value = array[y, x]
                gray = int(255 * value)
                color = (gray, gray, gray)
                pygame.draw.rect(screen, color,
                                 pygame.Rect(x * pix_size, y * pix_size, pix_size, pix_size))
        pygame.display.flip()

    pygame.quit()

def plot_impact_group_ratio_over_time(model, group, timestep_names=None, return_counts=False):
    """
    Plot the ratio of group-to-group impacts over time for a Model object.
    Args:
        model: Model instance with .impact attribute (dict of timestep_name -> impacts dict)
        group: set of entities (e.g., set of (x, y) tuples)
        timestep_names: list of timestep names to plot (default: all in model.impact)
        return_counts: if True, also plot counts as dashed lines
    """
    if not hasattr(model, "impact") or not model.impact:
        print("No impacts stored in model.")
        return
    if timestep_names is None:
        timestep_names = sorted(model.impact.keys(), key=lambda x: int(''.join(filter(str.isdigit, x))))
    elif type(timestep_names) is tuple:
        #TODO add more robustness
        start_time, end_time = timestep_names
        base_name = model.base_name
        if end_time is None:
            end_time = max(model.impact.keys(), key=lambda x: int(''.join(filter(str.isdigit, x))))
        timestep_names = [f"{base_name}{i}" for i in range(start_time, end_time + 1)]
    ratios = []
    between_counts = []
    total_counts = []
    for t in timestep_names:
        result = impact_group_ratio(model.impact[t], group, return_counts=True)
        ratios.append(result[0])
        between_counts.append(result[1])
        total_counts.append(result[2])
    plt.figure(figsize=(8, 4))
    if not return_counts:
        plt.plot(timestep_names, ratios, marker='o', label='Ratio (within group / all involving group)')
    if return_counts:
        plt.plot(timestep_names, between_counts, '--', label='Within-group count')
        plt.plot(timestep_names, total_counts, '--', label='Total involving group')
    plt.xlabel('Timestep')
    if len(timestep_names) > 20:
        plt.xticks(timestep_names[::5], rotation=45)
    else:
        plt.xticks(rotation=45)

    plt.ylabel('Ratio')
    plt.title('Ratio of within-group impacts over time')
    plt.legend()
    plt.tight_layout()
    plt.show()