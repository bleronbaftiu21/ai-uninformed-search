"""Latin Square me Iterative Deepening DFS (IDDFS) + Backtracking.

Modelimi
--------
* Gjendja  : një grid n x n pjesërisht i mbushur (0 = qelizë bosh).
* Variablat: qelizat X[r][c], 0 <= r, c < n.
* Domain-i : D = {1, ..., n} për çdo qelizë.
* Kufizimet: AllDifferent për çdo rresht dhe për çdo kolonë.
* Veprimi  : vendos një vlerë v në qelizën e radhës bosh (renditje row-major).
* Goal test: të gjitha qelizat janë mbushur (dhe meqë çdo veprim respekton
  kufizimet, grid-i i plotë është Latin Square i vlefshëm).

IDDFS ekzekuton Depth-Limited Search (DLS) me kufi L = 0, 1, 2, ... derisa ta
gjejë zgjidhjen. Backtracking-u do të thotë që gjenerojmë vetëm vlerat që NUK
shkelin kufizimet (pruning) dhe kthehemi prapa sapo një degë ngec.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import time

from ai_search.stats import SearchStats, SearchTimeout

Grid = List[List[int]]


@dataclass
class LatinSquareResult:
    grid: Optional[Grid]
    stats: SearchStats
    depth_of_solution: int
    nodes_per_iteration: List[int]
    timed_out: bool = False

    @property
    def solved(self) -> bool:
        return self.grid is not None


class LatinSquareIDDFS:
    """Zgjidh problemin e Latin Square me IDDFS + Backtracking.

    Args:
        n: madhësia e katrorit.
        reduced: nëse True, rreshti i parë dhe kolona e parë fiksohen në
            1..n (forma e reduktuar / "normalized"). Kjo është *symmetry
            breaking*: çdo Latin Square mund të shndërrohet në formë të
            reduktuar duke ndërruar rreshtat/kolonat, kështu që nuk humbet
            asnjë zgjidhje, por hapësira e kërkimit zvogëlohet shumë.
    """

    def __init__(self, n: int, reduced: bool = True) -> None:
        if n < 1:
            raise ValueError("n duhet të jetë >= 1")
        self.n = n
        self.reduced = reduced

    # ------------------------------------------------------------------ #
    # Problemi
    # ------------------------------------------------------------------ #
    def initial_state(self) -> Grid:
        n = self.n
        grid = [[0] * n for _ in range(n)]
        if self.reduced:
            for i in range(n):
                grid[0][i] = i + 1  # rreshti i parë 1..n
                grid[i][0] = i + 1  # kolona e parë 1..n
        return grid

    # ------------------------------------------------------------------ #
    # Algoritmi
    # ------------------------------------------------------------------ #
    def solve(self, time_limit: Optional[float] = None) -> LatinSquareResult:
        """Ekzekuton IDDFS.

        Args:
            time_limit: kufi kohor në sekonda (None = pa kufi). IDDFS rritet
                shpejt me n (shih docs), prandaj për n >= 7 këshillohet kufi.
        """
        n = self.n
        deadline = None if time_limit is None else time.perf_counter() + time_limit
        stats = SearchStats()
        stats.start()

        grid = self.initial_state()
        # Qelizat bosh në renditje row-major: këto janë variablat që kërkojmë.
        empty = [(r, c) for r in range(n) for c in range(n) if grid[r][c] == 0]
        goal_depth = len(empty)

        # Bitmask-a për kontroll të shpejtë të kufizimeve:
        # row_used[r] ka bitin v të ndezur nëse vlera v është në rreshtin r.
        row_used = [0] * n
        col_used = [0] * n
        for r in range(n):
            for c in range(n):
                v = grid[r][c]
                if v:
                    row_used[r] |= 1 << v
                    col_used[c] |= 1 << v

        nodes_per_iteration: List[int] = []

        def dls(depth: int, limit: int) -> bool:
            """Depth-Limited Search rekursiv me backtracking."""
            stats.nodes_expanded += 1
            if deadline is not None and (stats.nodes_expanded & 0x3FFF) == 0:
                if time.perf_counter() > deadline:
                    raise SearchTimeout
            if depth > stats.max_depth:
                stats.max_depth = depth

            if depth == goal_depth:          # goal test
                return True
            if depth == limit:               # cutoff
                return False

            r, c = empty[depth]
            used = row_used[r] | col_used[c]
            for v in range(1, n + 1):
                bit = 1 << v
                if used & bit:               # shkel kufizimin -> prune
                    stats.pruned += 1
                    continue
                stats.nodes_generated += 1
                # apliko veprimin
                grid[r][c] = v
                row_used[r] |= bit
                col_used[c] |= bit
                if dls(depth + 1, limit):
                    return True
                # backtrack: zhbëj veprimin
                grid[r][c] = 0
                row_used[r] &= ~bit
                col_used[c] &= ~bit
            return False

        found = False
        timed_out = False
        try:
            for limit in range(goal_depth + 1):
                stats.iterations += 1
                before = stats.nodes_expanded
                found = dls(0, limit)
                nodes_per_iteration.append(stats.nodes_expanded - before)
                if found:
                    break
        except SearchTimeout:
            timed_out = True

        stats.stop()
        return LatinSquareResult(
            grid=[row[:] for row in grid] if found else None,
            stats=stats,
            depth_of_solution=goal_depth,
            nodes_per_iteration=nodes_per_iteration,
            timed_out=timed_out,
        )


# ---------------------------------------------------------------------- #
# Funksione ndihmëse
# ---------------------------------------------------------------------- #
def objective(grid: Grid) -> int:
    """Objective function: numri i konflikteve (duhet minimizuar).

    f(X) = Σ_rreshta (n - |vlera unike|) + Σ_kolona (n - |vlera unike|)
           + numri i qelizave bosh

    f(X) = 0  <=>  X është Latin Square i vlefshëm.
    """
    n = len(grid)
    conflicts = 0
    for r in range(n):
        values = [v for v in grid[r] if v]
        conflicts += len(values) - len(set(values))
    for c in range(n):
        values = [grid[r][c] for r in range(n) if grid[r][c]]
        conflicts += len(values) - len(set(values))
    empty = sum(1 for row in grid for v in row if v == 0)
    return conflicts + empty


def is_valid_latin_square(grid: Grid) -> bool:
    n = len(grid)
    target = set(range(1, n + 1))
    rows_ok = all(set(row) == target for row in grid)
    cols_ok = all({grid[r][c] for r in range(n)} == target for c in range(n))
    return rows_ok and cols_ok


def cyclic_construction(n: int) -> Grid:
    """Konstruksion direkt O(n²) (për krahasim): L[r][c] = (c - r) mod n + 1.

    Jep të njëjtin model si shembulli në detyrë (5 1 2 3 4 / 4 5 1 2 3 / ...)
    kur zhvendosim me +1. Tregon se problemi ka gjithmonë zgjidhje.
    """
    return [[(c - r - 1) % n + 1 for c in range(n)] for r in range(n)]


def format_grid(grid: Grid) -> str:
    width = len(str(len(grid)))
    return "\n".join(" ".join(f"{v:>{width}}" for v in row) for row in grid)
