#2 blobs distance stats
# ...

def impact_group_ratio(impacts: dict, group: set, return_counts=False):
    """
    Calculate the ratio of impacts between entities in `group` vs. all impacts involving at least one entity from `group`.
    Args:
        impacts: dict of impacts at a timestep, keys are (entity1, entity2) tuples.
        group: set of entities (e.g., set of (x, y) tuples).
        return_counts: if True, also return (between_count, total_count).
    Returns:
        ratio (float), and optionally (between_count, total_count)
    """
    between_count = 0
    total_count = 0
    for (src, tgt) in impacts.keys():
        src_in = src in group
        tgt_in = tgt in group
        if src_in or tgt_in:
            total_count += 1
            if src_in and tgt_in:
                between_count += 1
    ratio = between_count / total_count if total_count > 0 else 0.0
    if return_counts:
        return ratio, between_count, total_count
    return ratio

def flatten_impacts_all_time(impacts_all_time: dict) -> list:
    """
    Flattens impacts across all time steps into a list of (src, tgt) edges,
    preserving repeated impacts.

    Args:
        impacts_all_time: dict of timestep -> dict of (src, tgt) -> any

    Returns:
        list of (src, tgt) edges (with duplicates)
    """
    all_impacts = []
    for timestep in impacts_all_time:
        timestep_impacts = impacts_all_time[timestep]
        all_impacts.extend(timestep_impacts.keys())  # preserve duplicates if any
    return all_impacts

def group_impact_strength(impacts: dict, group: set,
                          total_nodes: int = None, return_counts=True):
    """
    Computes the group impact strength S and compares it to the expected value.

    Args:
        impacts: dict of (src, tgt) -> any
        group: set of entities
        total_nodes: total number of nodes in the system (required if impacts are sparse)
        return_counts: return (I, O, S_expected) if True

    Returns:
        S/S_expected value, optionally with counts
    """
    I = 0  # inner impacts (both src and tgt in group)
    O = 0  # outer impacts (only one in group)
    for src, tgt in impacts:
        src_in = src in group
        tgt_in = tgt in group
        if src_in and tgt_in:
            I += 2
        elif src_in or tgt_in:
            O += 1
    S = I / (I + O) if (I + O) > 0 else 0.0

    k = len(group)
    if total_nodes is None:
        involved_nodes = {node for pair in impacts.keys() for node in pair}
        n = len(involved_nodes)
    else:
        n = total_nodes
    if n <= 1 or k <= 1 or n == k:
        S_expected = 1.0
    else:
        S_expected = (k-1) / (n-1)
    ratio = S / S_expected if S_expected > 0 else 0.0

    if return_counts:
        return ratio, I, O, S_expected
    return ratio

def find_self_controlling_group(impacts: dict, nodes: set,
                                min_group_size = 4):
    """
    Greedy algorithm to find a strongly self-controlling group.

    Args:
        impacts: dict of (src, tgt) -> any
        nodes: full set of nodes to select from

    Returns:
        group: set of nodes with strong internal impact
    """
    # Compute total nodes
    n = len(nodes)

    # Step 1: Find node with max impact (appearances)
    impact_counts = {}
    for src, tgt in impacts:
        impact_counts[src] = impact_counts.get(src, 0) + 1
        impact_counts[tgt] = impact_counts.get(tgt, 0) + 1

    current_group = {max(impact_counts, key=impact_counts.get)}
    candidate_nodes = nodes - current_group

    # Step 2: Greedy addition
    improved = True
    I = O = 0
    for src, tgt in impacts:
        if src in current_group and tgt in current_group:
            I += 2
        elif src in current_group or tgt in current_group:
            O += 1

    def compute_ratio(I, O, k, n):
        S = I / (I + O) if (I + O) > 0 else 0
        S_expected = (k-1)/(n-1) if k > 1 and n > k else 0
        return S / S_expected if S_expected > 0 else 0

    current_ratio = compute_ratio(I, O, len(current_group), n)

    while improved:
        improved = False
        #best_ratio = current_ratio
        best_node = None

        for node in candidate_nodes:
            new_I = I
            new_O = O
            max_ratio = 0
            for src, tgt in impacts:
                in_group_src = src in current_group
                in_group_tgt = tgt in current_group
                if node == src and in_group_tgt:
                    new_I += 2
                elif node == tgt and in_group_src:
                    new_I += 2
                elif node == src or node == tgt:
                    new_O += 1

            new_k = len(current_group) + 1
            new_ratio = compute_ratio(new_I, new_O, new_k, n)
            if new_ratio > max_ratio:
                max_ratio = new_ratio
                best_node = node
                best_I = new_I
                best_O = new_O

        if (max_ratio > current_ratio or len(current_group) < min_group_size):
            current_group.add(best_node)
            candidate_nodes.remove(best_node)
            I, O = best_I, best_O
            current_ratio = max_ratio
            improved = True
    return current_group
