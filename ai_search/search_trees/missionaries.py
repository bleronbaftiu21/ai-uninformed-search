"""Search Tree për Missionaries and Cannibals.

* Gjendja : (M, C, B) = misionarë dhe kanibalë në bregun e MAJTË,
            B = 1 nëse varka është majtas, 0 nëse djathtas.
* Fillimi : (3, 3, 1)       Goal: (0, 0, 0)
* Veprimet: varka bart (m, c) ∈ {(1,0), (2,0), (0,1), (0,2), (1,1)}.
* Kufizimi: në asnjë breg misionarët (nëse > 0) nuk duhet të jenë më pak se
            kanibalët.

Pema ndërtohet me BFS. Gjendjet që shkelin kufizimin shfaqen me të kuqe
(prerë nga backtracking), ndërsa gjendjet e përsëritura me gri.
"""

from __future__ import annotations

from collections import deque
from typing import Iterator, List, Tuple

from ai_search.search_trees.tree import SearchTree

State = Tuple[int, int, int]
START: State = (3, 3, 1)
GOAL: State = (0, 0, 0)
BOAT_LOADS = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]


def label(state: State) -> str:
    m, c, b = state
    left = "M" * m + "C" * c or "-"
    right = "M" * (3 - m) + "C" * (3 - c) or "-"
    boat = "<B" if b == 1 else "B>"
    return f"({m},{c},{b})\n{left} {boat} {right}"


def is_valid(state: State) -> bool:
    m, c, _ = state
    if not (0 <= m <= 3 and 0 <= c <= 3):
        return False
    if m > 0 and m < c:              # bregu i majtë
        return False
    if (3 - m) > 0 and (3 - m) < (3 - c):   # bregu i djathtë
        return False
    return True


def successors(state: State) -> Iterator[Tuple[str, State]]:
    m, c, b = state
    sign = -1 if b == 1 else 1
    for dm, dc in BOAT_LOADS:
        new = (m + sign * dm, c + sign * dc, 1 - b)
        if 0 <= new[0] <= 3 and 0 <= new[1] <= 3:
            yield f"{dm}M{dc}C {'→' if b == 1 else '←'}", new


def build_tree(show_invalid: bool = True) -> SearchTree:
    tree = SearchTree("Missionaries & Cannibals — Search Tree (BFS)")
    root = tree.add(label(START))
    queue = deque([(root, START)])
    seen = {START}
    goal_id = None

    while queue and goal_id is None:
        nid, state = queue.popleft()
        for action, child in successors(state):
            if not is_valid(child):
                if show_invalid:
                    tree.add(label(child), nid, action, "invalid")
                continue
            if child in seen:
                tree.add(label(child), nid, action, "repeated")
                continue
            seen.add(child)
            status = "goal" if child == GOAL else "normal"
            cid = tree.add(label(child), nid, action, status)
            if status == "goal":
                goal_id = cid
                break
            queue.append((cid, child))

    # nyjet që mbetën në radhë kur u gjet qëllimi janë frontier
    for nid, _ in queue:
        if tree.nodes[nid].status == "normal":
            tree.nodes[nid].status = "frontier"
    if goal_id is not None:
        tree.mark_path(goal_id)
    return tree


def solution_path() -> List[State]:
    """Zgjidhja optimale me BFS (11 kalime)."""
    queue = deque([[START]])
    seen = {START}
    while queue:
        path = queue.popleft()
        if path[-1] == GOAL:
            return path
        for _, child in successors(path[-1]):
            if is_valid(child) and child not in seen:
                seen.add(child)
                queue.append(path + [child])
    return []
