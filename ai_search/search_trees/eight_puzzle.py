"""Search Tree për 8-Puzzle.

* Gjendja : string me 9 karaktere (rresht pas rreshti), '0' = vendi bosh.
* Veprimet: lëviz vendin bosh Lart (U), Poshtë (D), Majtas (L), Djathtas (R).
* Goal    : 1 2 3 / 4 5 6 / 7 8 _
* Kostoja : 1 për çdo lëvizje.

Pema ndërtohet me BFS deri në një thellësi të caktuar. Për ta mbajtur pemën të
lexueshme, nuk e gjenerojmë veprimin që e zhbën lëvizjen e mëparshme (p.sh. U
pas D) – ky është eliminimi më i thjeshtë i gjendjeve të përsëritura.
"""

from __future__ import annotations

from collections import deque
from typing import Iterator, Tuple

from ai_search.search_trees.tree import SearchTree

GOAL = "123456780"
DEFAULT_START = "123046758"          # zgjidhja optimale: R, D, R (3 lëvizje)

MOVES = {"U": -3, "D": 3, "L": -1, "R": 1}
OPPOSITE = {"U": "D", "D": "U", "L": "R", "R": "L"}


def pretty(state: str) -> str:
    s = state.replace("0", "_")
    return "\n".join(" ".join(s[i:i + 3]) for i in range(0, 9, 3))


def successors(state: str) -> Iterator[Tuple[str, str]]:
    """Gjeneron (veprimi, gjendja_e_re) për çdo lëvizje të vlefshme."""
    b = state.index("0")
    r, c = divmod(b, 3)
    for action, delta in MOVES.items():
        if (action == "U" and r == 0) or (action == "D" and r == 2) \
                or (action == "L" and c == 0) or (action == "R" and c == 2):
            continue
        t = b + delta
        s = list(state)
        s[b], s[t] = s[t], s[b]
        yield action, "".join(s)


def is_solvable(state: str) -> bool:
    """8-puzzle është i zgjidhshëm vetëm nëse numri i inversioneve është çift."""
    tiles = [ch for ch in state if ch != "0"]
    inversions = sum(1 for i in range(8) for j in range(i + 1, 8) if tiles[i] > tiles[j])
    return inversions % 2 == 0


def build_tree(start: str = DEFAULT_START, max_depth: int = 3) -> SearchTree:
    tree = SearchTree(f"8-Puzzle — Search Tree (BFS, thellesia <= {max_depth})")
    root = tree.add(pretty(start), status="goal" if start == GOAL else "normal")
    queue = deque([(root, start, "")])
    goal_id = None

    while queue:
        nid, state, last = queue.popleft()
        if state == GOAL:
            continue
        if tree.nodes[nid].depth >= max_depth:
            tree.nodes[nid].status = "frontier"
            continue
        for action, child in successors(state):
            if last and OPPOSITE[action] == last:
                continue                     # mos e zhbëj lëvizjen e fundit
            status = "goal" if child == GOAL else "normal"
            cid = tree.add(pretty(child), nid, action, status)
            if status == "goal" and goal_id is None:
                goal_id = cid
            queue.append((cid, child, action))

    if goal_id is not None:
        tree.mark_path(goal_id)
    return tree
