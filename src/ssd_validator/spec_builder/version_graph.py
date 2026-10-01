"""Validate explicit single-parent linear inheritance without sorting version numbers."""

from collections import defaultdict
from heapq import heappop, heappush

from ssd_validator.errors import KnowledgeError


def version_order(parents: dict[str, str | None]) -> tuple[str, ...]:
    children: dict[str, list[str]] = defaultdict(list)
    for key, parent in sorted(parents.items()):
        if parent is not None:
            if parent not in parents:
                raise KnowledgeError("MISSING_PARENT", f"{key} inherits missing {parent}")
            children[parent].append(key)
    ready = sorted(key for key, parent in parents.items() if parent is None)
    ordered = []
    while ready:
        key = heappop(ready)
        ordered.append(key)
        for child in sorted(children[key]):
            heappush(ready, child)
    if len(ordered) != len(parents):
        cycle = sorted(set(parents) - set(ordered))
        raise KnowledgeError("CIRCULAR_INHERITANCE", ", ".join(cycle))
    if any(len(group) > 1 for group in children.values()):
        raise KnowledgeError("NON_LINEAR_INHERITANCE", "Phase 1 supports linear version chains only")
    roots_by_family = defaultdict(list)
    for key, parent in parents.items():
        if parent is None:
            roots_by_family[key.split(":", 1)[0]].append(key)
    if any(len(roots) > 1 for roots in roots_by_family.values()):
        raise KnowledgeError("MULTIPLE_BASE_VERSIONS", "Use one base version per family and explicit deltas")
    return tuple(ordered)
