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

