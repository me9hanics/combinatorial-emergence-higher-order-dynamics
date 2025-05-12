# Emergent features and complexity from mechanisms - analysis on graph models and cellular automata
This contains work done for my MSc thesis at the Central European University in Vienna, Austria in data science. The work uses ideas and measures from complexity science, and tries to extend them by exploring a more combinatorial approach than current works (focusing on statistical methods).<br>
On the most case, this means trying to mathematically derive how different types/aspects of mechanisms (that drive a dynamical system) causally (combinatorially) impact its future properties, such as having collective behaviour, emergent self-sufficient substructures, or high complexity. What differents some rulesets of cellular automata from others, in being able to create complex emergent patterns? My aim is to derive what aspects impact the ability of emergent patterns to form (at any scale), i.e. find the set of attributes which are necessary and sufficient for emergent patterns to appear. After all, the only provable causality is the derivative one (which is also explanatory) - if we can mathematically show whether dynamic patterns could form just by looking at the rules of the system, that already 

Secondary, more long term goals of this work are very extensive; e.g. how to design specific mechanisms that give rise to specific mesoscale patterns, the connection between emergence and complexity, the importance of self-referentiality in complex systems, and so on.

## Setup

To simply set up the environment, include this TOML file in the same directory as the repository itself (not inside the repository):

<script src="https://gist.github.com/me9hanics/a00fcde722e5ebe6ac2e7e378b54e5ab.js"></script>

Then run the following command in the terminal:

Linux:
```bash
python -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Then, go to the directory where the repository and the TOML file are located (not inside the repository) and run:
```bash
pip install -e .
```
(`-e` allows you to dynamically update the environment when editing the code, without reinstalls.)

## Implementation

Most modern dynamical systems are represented by their structure, and the dynamics of and on the structure. The software implementation is broad enough to enable various set of rules (mechanisms) on any structure (grid, graph, other types of networks e.g. hypergraphs, etc.) as long as the structure has entities and connections well-defined. This comes in handy for easily defining different mechanisms and testing them on different systems without need for configuration. (The current implementation includes grid (cellular automata) and graph structures, and various mechanisms of dynamics).<br>
Implementation is written in Python, and uses the design pattern that I would call "Structures and Dynamics" (likely not a pattern that has been published): keeping the structures and the dynamics separate in the code, by having an abstract class for structure from which the concrete structures (grid, graph, ...) inherit, having methods that return the entities and connections in the structure, and implementing the dynamics as a separate class that takes a structure, and a function containing the logic of the dynamics as an input. (This simplifies the dynamics down to a function that takes current (discrete time) states of entities and returns the next state, based on the logic they represent).

## Why a combinatorial approach?

*Coming soon...*
