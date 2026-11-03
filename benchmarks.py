#!/usr/bin/env python3
"""Mat performancën e algoritmeve dhe printon tabela Markdown për dokumentim.

    python benchmarks.py
"""

from __future__ import annotations

from ai_search.latin_square.solver import LatinSquareIDDFS
from ai_search.social_golfers.solver import SocialGolfersDFS, search_max_weeks
from ai_search.sudoku.puzzles import LEVELS, PUZZLES
from ai_search.sudoku.solver import SudokuBFS


def latin() -> None:
    print("### Latin Square – IDDFS\n")
    print("| n | Modeli | Iteracione | Nyje te zgjeruara | Koha (s) |")
    print("|---|--------|-----------:|------------------:|---------:|")
    for n in range(2, 8):
        for reduced in (True, False):
            if not reduced and n > 5:
                continue
            r = LatinSquareIDDFS(n, reduced).solve(time_limit=30)
            model = "reduced" if reduced else "full"
            time_s = f"{r.stats.elapsed:.3f}" if r.solved else "> 30 (timeout)"
            print(f"| {n} | {model} | {r.stats.iterations} | {r.stats.nodes_expanded:,} | {time_s} |")
    print()


def sudoku() -> None:
    print("### Sudoku – BFS\n")
    print("| Enigma | Clues | Ordering | Nyje te zgjeruara | Frontier max | Koha (s) |")
    print("|--------|------:|----------|------------------:|-------------:|---------:|")
    for level in LEVELS:
        for i, puzzle in enumerate(PUZZLES[level], 1):
            clues = 81 - puzzle.count("0")
            for ordering in ("fixed", "mrv"):
                try:
                    r = SudokuBFS(ordering, max_frontier=2_000_000).solve(puzzle, time_limit=30)
                    if r.solved:
                        row = (f"{r.stats.nodes_expanded:,} | {r.stats.max_frontier:,} | "
                               f"{r.stats.elapsed:.3f}")
                    else:
                        row = "– | – | > 30 (timeout)"
                except MemoryError:
                    row = "– | > 2,000,000 | memoria (stop)"
                print(f"| {level} #{i} | {clues} | {ordering} | {row} |")
    print()


def golfers() -> None:
    print("### Social Golfers (8-4) – DFS\n")
    print("| Javë | Rezultati | Nyje te zgjeruara | Koha (s) |")
    print("|-----:|-----------|------------------:|---------:|")
    for w in range(1, 7):
        r = SocialGolfersDFS(8, 4, w).solve(time_limit=30)
        res = "u gjet" if r.solved else "timeout (30 s)"
        print(f"| {w} | {res} | {r.stats.nodes_expanded:,} | {r.stats.elapsed:.3f} |")
    r = search_max_weeks(8, 4, restarts=10, time_per_run=3)
    print(f"\nDFS + restarts (10 x 3 s): maksimumi i gjetur = **{r.best_weeks} jave** "
          f"(seed = {r.stats.extra.get('Run (seed)')})\n")


if __name__ == "__main__":
    latin()
    sudoku()
    golfers()
