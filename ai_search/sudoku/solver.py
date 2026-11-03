"""Sudoku me Breadth First Search (BFS) + Backtracking.

Modelimi
--------
* Gjendja  : grid 9x9 (string me 81 karaktere, '0' = bosh).
* Variablat: qelizat bosh X[r][c].
* Domain-i : D = {1, ..., 9}.
* Kufizimet: AllDifferent në çdo rresht, kolonë dhe kuti 3x3.
* Veprimi  : vendos vlerën v në qelizën e radhës bosh.
* Goal test: nuk ka më qeliza bosh.

BFS e eksploron pemën nivel pas niveli me një radhë FIFO (deque). Nivelin k e
përbëjnë të gjitha gjendjet me k qeliza të mbushura nga kërkimi.

"Backtracking" në kontekstin e BFS do të thotë: një fëmijë gjenerohet VETËM
nëse vlera nuk shkel kufizimet; nyjet që nuk kanë asnjë vlerë të lejuar për
qelizën e radhës janë "dead ends" dhe hidhen (dega braktiset) – pra kthehemi
te alternativat e tjera që janë ende në radhë.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from ai_search.stats import SearchStats, SearchTimeout

DIGITS = "123456789"

# Për çdo qelizë i (0..80) ruajmë "peers": qelizat në të njëjtin rresht,
# kolonë ose kuti. Llogariten një herë, në import.
ROW_OF = [i // 9 for i in range(81)]
COL_OF = [i % 9 for i in range(81)]
BOX_OF = [(i // 27) * 3 + (i % 9) // 3 for i in range(81)]
PEERS: List[List[int]] = [
    [
        j
        for j in range(81)
        if j != i
        and (ROW_OF[j] == ROW_OF[i] or COL_OF[j] == COL_OF[i] or BOX_OF[j] == BOX_OF[i])
    ]
    for i in range(81)
]


@dataclass
class SudokuResult:
    solution: Optional[str]
    stats: SearchStats
    nodes_per_level: List[int]
    timed_out: bool = False

    @property
    def solved(self) -> bool:
        return self.solution is not None


# ---------------------------------------------------------------------- #
# Hyrje / dalje
# ---------------------------------------------------------------------- #
def parse(puzzle: str) -> str:
    """Pranon '.', '0' ose '_' për qeliza bosh, injoron hapësirat/rreshtat."""
    chars = [ch for ch in puzzle if ch in DIGITS or ch in "0._"]
    if len(chars) != 81:
        raise ValueError(f"Sudoku duhet të ketë 81 qeliza, u gjetën {len(chars)}")
    return "".join(ch if ch in DIGITS else "0" for ch in chars)


def format_grid(state: str) -> str:
    lines = []
    for r in range(9):
        if r in (3, 6):
            lines.append("------+-------+------")
        row = state[r * 9 : r * 9 + 9].replace("0", ".")
        lines.append(" ".join(row[0:3]) + " | " + " ".join(row[3:6]) + " | " + " ".join(row[6:9]))
    return "\n".join(lines)


# ---------------------------------------------------------------------- #
# Kufizimet
# ---------------------------------------------------------------------- #
def candidates(state: str, i: int) -> List[str]:
    """Vlerat e lejuara për qelizën i (domain-i pas pruning-ut)."""
    used = {state[j] for j in PEERS[i]}
    return [d for d in DIGITS if d not in used]


def is_consistent(state: str) -> bool:
    """A respektohen të gjitha kufizimet nga qelizat e mbushura?"""
    for i, ch in enumerate(state):
        if ch != "0" and any(state[j] == ch for j in PEERS[i]):
            return False
    return True


def is_solved(state: str) -> bool:
    return "0" not in state and is_consistent(state)


def objective(state: str) -> int:
    """Objective function (minimizim): konflikte + qeliza bosh.

    f(X) = Σ_{njësi ∈ rreshta ∪ kolona ∪ kuti} (numri i vlerave të përsëritura)
           + numri i qelizave bosh
    f(X) = 0  <=>  Sudoku është zgjidhur saktë.
    """
    conflicts = 0
    units = (
        [[r * 9 + c for c in range(9)] for r in range(9)]
        + [[r * 9 + c for r in range(9)] for c in range(9)]
        + [[i for i in range(81) if BOX_OF[i] == b] for b in range(9)]
    )
    for unit in units:
        values = [state[i] for i in unit if state[i] != "0"]
        conflicts += len(values) - len(set(values))
    return conflicts + state.count("0")


# ---------------------------------------------------------------------- #
# BFS + Backtracking
# ---------------------------------------------------------------------- #
class SudokuBFS:
    """Zgjidh Sudoku me BFS + Backtracking.

    Args:
        ordering: si zgjidhet qeliza e radhës (variabla):
            * ``"fixed"`` – qeliza e parë bosh (row-major). BFS e pastër.
            * ``"mrv"``   – Minimum Remaining Values: qeliza me më pak
              kandidatë. Nuk ndryshon BFS-në (radha mbetet FIFO), vetëm
              renditjen e variablave – kjo e zvogëlon shumë faktorin e
              degëzimit te Sudoku-të e vështira.
        max_frontier: kufi sigurie për memorien (numri max i nyjeve në radhë).
    """

    def __init__(self, ordering: str = "mrv", max_frontier: int = 5_000_000) -> None:
        if ordering not in ("fixed", "mrv"):
            raise ValueError("ordering duhet të jetë 'fixed' ose 'mrv'")
        self.ordering = ordering
        self.max_frontier = max_frontier

    def _select_cell(self, state: str):
        """Kthen (qeliza, kandidatët) ose (None, None) nëse grid-i është plot."""
        if self.ordering == "fixed":
            i = state.find("0")
            if i < 0:
                return None, None
            return i, candidates(state, i)

        best_i, best_c = None, None
        for i, ch in enumerate(state):
            if ch == "0":
                c = candidates(state, i)
                if best_c is None or len(c) < len(best_c):
                    best_i, best_c = i, c
                    if len(c) <= 1:
                        break
        return best_i, best_c

    def solve(self, puzzle: str, time_limit: Optional[float] = None) -> SudokuResult:
        start = parse(puzzle)
        stats = SearchStats()
        stats.start()
        deadline = None if time_limit is None else time.perf_counter() + time_limit

        if not is_consistent(start):
            stats.stop()
            return SudokuResult(None, stats, [])

        filled_at_start = 81 - start.count("0")
        nodes_per_level: Dict[int, int] = {}
        frontier = deque([start])
        stats.max_frontier = 1
        solution: Optional[str] = None
        timed_out = False

        try:
            while frontier:
                state = frontier.popleft()            # FIFO -> BFS
                stats.nodes_expanded += 1
                depth = (81 - state.count("0")) - filled_at_start
                nodes_per_level[depth] = nodes_per_level.get(depth, 0) + 1
                stats.max_depth = max(stats.max_depth, depth)

                if deadline is not None and (stats.nodes_expanded & 0x3FF) == 0:
                    if time.perf_counter() > deadline:
                        raise SearchTimeout

                cell, values = self._select_cell(state)
                if cell is None:                       # goal test
                    solution = state
                    break
                if not values:                         # dead end -> backtrack
                    stats.pruned += 1
                    continue

                for v in values:                       # vetëm vlera të vlefshme
                    stats.nodes_generated += 1
                    frontier.append(state[:cell] + v + state[cell + 1 :])

                if len(frontier) > stats.max_frontier:
                    stats.max_frontier = len(frontier)
                    if stats.max_frontier > self.max_frontier:
                        raise MemoryError(
                            "Frontier-i i BFS tejkaloi kufirin; provo ordering='mrv'"
                        )
        except SearchTimeout:
            timed_out = True

        stats.stop()
        levels = [nodes_per_level.get(d, 0) for d in range(stats.max_depth + 1)]
        return SudokuResult(solution, stats, levels, timed_out)


# ---------------------------------------------------------------------- #
# Numërimi i zgjidhjeve (për validim dhe për gjeneratorin)
# ---------------------------------------------------------------------- #
def count_solutions(puzzle: str, limit: int = 2) -> int:
    """Numëron zgjidhjet (deri në `limit`) me DFS të shpejtë. Përdoret për të
    verifikuar që një enigmë ka zgjidhje unike."""
    grid = list(parse(puzzle))
    count = 0

    def dfs() -> bool:
        nonlocal count
        best_i, best_c = -1, None
        for i, ch in enumerate(grid):
            if ch == "0":
                used = {grid[j] for j in PEERS[i]}
                c = [d for d in DIGITS if d not in used]
                if best_c is None or len(c) < len(best_c):
                    best_i, best_c = i, c
                    if len(c) <= 1:
                        break
        if best_c is None:
            count += 1
            return count >= limit
        for d in best_c:
            grid[best_i] = d
            if dfs():
                return True
            grid[best_i] = "0"
        return False

    if is_consistent("".join(grid)):
        dfs()
    return count


def solve_many(puzzles: Sequence[str], **kwargs) -> List[SudokuResult]:
    solver = SudokuBFS(**kwargs)
    return [solver.solve(p) for p in puzzles]
