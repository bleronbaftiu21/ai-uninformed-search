#!/usr/bin/env python3
"""Pika hyrëse (CLI) për Detyrën 1 – Teknikat e painformuara të kërkimit.

Shembuj:
    python main.py latin --n 5
    python main.py sudoku --level hard
    python main.py sudoku --level all
    python main.py sudoku --generate medium --seed 7
    python main.py golfers --weeks 5
    python main.py golfers --max-weeks
    python main.py trees
    python main.py all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Windows console: siguro që karakteret ë, ç, →, × të printohen saktë.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ai_search.stats import sci  # noqa: E402

ROOT = Path(__file__).resolve().parent
LINE = "=" * 72


def header(title: str) -> None:
    print(f"\n{LINE}\n  {title}\n{LINE}")


# ---------------------------------------------------------------------- #
# 1. Social Golfers – DFS + Backtracking
# ---------------------------------------------------------------------- #
def run_golfers(args: argparse.Namespace) -> None:
    from ai_search.social_golfers.solver import (
        SocialGolfersDFS, format_schedule, is_valid, landscape, objective, search_max_weeks,
    )

    g, p = args.groups, args.size
    header(f"SOCIAL GOLFERS  –  DFS + Backtracking  (n={g * p}, g={g}, p={p})")

    if args.max_weeks:
        print(f"Kerkim per numrin max te javeve ({args.restarts} run x {args.time_limit}s)...")
        result = search_max_weeks(g, p, restarts=args.restarts, time_per_run=args.time_limit)
        schedule = result.best_schedule
    else:
        result = SocialGolfersDFS(g, p, args.weeks).solve(time_limit=args.time_limit)
        schedule = result.schedule or result.best_schedule
        status = "U GJET" if result.solved else (
            "KOHA MBAROI" if result.timed_out else "NUK KA ZGJIDHJE")
        print(f"Kerkesa: {args.weeks} jave  ->  {status}")

    print(f"\nOrari ({len(schedule)} jave):")
    print(format_schedule(schedule))
    print(f"\nObjective f(S) = {objective(schedule)}  (0 = asnje cift nuk takohet dy here)")
    print(f"I vlefshem: {is_valid(schedule, g, p)}")
    print("\nStatistika:")
    print(result.stats.summary())

    print("\nLandscape (madhesia e hapesires se kerkimit):")
    for key, value in landscape(g, p, max(len(schedule), 1)).items():
        print(f"  {key:<28}: {sci(value)}")


# ---------------------------------------------------------------------- #
# 2. Sudoku – BFS + Backtracking
# ---------------------------------------------------------------------- #
def run_sudoku(args: argparse.Namespace) -> None:
    from ai_search.sudoku.puzzles import LEVELS, PUZZLES, generate
    from ai_search.sudoku.solver import SudokuBFS, format_grid, is_solved, objective

    solver = SudokuBFS(ordering=args.ordering)

    if args.generate:
        puzzles = [(f"{args.generate} (gjeneruar, seed={args.seed})",
                    generate(args.generate, args.seed))]
    elif args.puzzle:
        puzzles = [("hyrje", args.puzzle)]
    else:
        levels = LEVELS if args.level == "all" else (args.level,)
        puzzles = [(f"{lvl} #{i + 1}", pz) for lvl in levels for i, pz in enumerate(PUZZLES[lvl])]
        if args.level != "all" and not args.every:
            puzzles = puzzles[:1]

    for name, puzzle in puzzles:
        header(f"SUDOKU  –  BFS + Backtracking  [{name}]  (ordering={args.ordering})")
        clues = 81 - puzzle.count("0") - puzzle.count(".")
        print(f"Enigma ({clues} clues), f(X) = {objective(puzzle.replace('.', '0'))}:")
        print(format_grid(puzzle.replace(".", "0")))
        result = solver.solve(puzzle, time_limit=args.time_limit)
        if result.solved:
            print(f"\nZgjidhja (f(X) = {objective(result.solution)}, "
                  f"e sakte: {is_solved(result.solution)}):")
            print(format_grid(result.solution))
        else:
            print("\nNuk u gjet zgjidhje" + (" (koha mbaroi)" if result.timed_out else ""))
        print("\nStatistika:")
        print(result.stats.summary())
        levels = result.nodes_per_level
        if levels:
            widest = max(range(len(levels)), key=levels.__getitem__)
            print(f"  Niveli me i gjere : niveli {widest} me {levels[widest]:,} nyje "
                  f"(nga {len(levels)} nivele)")


# ---------------------------------------------------------------------- #
# 3. Latin Square – IDDFS + Backtracking
# ---------------------------------------------------------------------- #
def run_latin(args: argparse.Namespace) -> None:
    from ai_search.latin_square.solver import (
        LatinSquareIDDFS, format_grid, is_valid_latin_square, objective,
    )
    from math import factorial

    n = args.n
    header(f"LATIN SQUARE  –  IDDFS + Backtracking  (n={n}, reduced={not args.full})")
    result = LatinSquareIDDFS(n, reduced=not args.full).solve(time_limit=args.time_limit)

    if result.solved:
        print("Zgjidhja:")
        print(format_grid(result.grid))
        print(f"\nObjective f(X) = {objective(result.grid)}, "
              f"e vlefshme: {is_valid_latin_square(result.grid)}")
    else:
        print("Koha mbaroi pa gjetur zgjidhje." if result.timed_out else "Nuk ka zgjidhje.")

    print(f"\nThellesia e zgjidhjes (qeliza per t'u mbushur): {result.depth_of_solution}")
    print("\nStatistika:")
    print(result.stats.summary())
    print(f"  Nyje per iteracion: {result.nodes_per_iteration}")

    free = result.depth_of_solution
    print("\nLandscape:")
    print(f"  Pa kufizime n^(n*n)       : {sci(n ** (n * n))}")
    print(f"  Variablat e lira n^k      : {sci(n ** free)}  (k = {free})")
    print(f"  Permutacione (n!)^n       : {sci(factorial(n) ** n)}")


# ---------------------------------------------------------------------- #
# 4. Search Trees
# ---------------------------------------------------------------------- #
def run_trees(args: argparse.Namespace) -> None:
    from ai_search.search_trees import eight_puzzle, missionaries, rotating_workforce as rws

    out = ROOT / "docs" / "trees"
    header("SEARCH TREES")

    tree = eight_puzzle.build_tree(max_depth=args.depth)
    files = tree.save(out, "eight_puzzle")
    print(tree.to_text())
    print(f"-> {tree.counts()}\n   {[f.name for f in files]}\n")

    tree = missionaries.build_tree()
    files = tree.save(out, "missionaries_cannibals")
    print(tree.to_text())
    print(f"-> {tree.counts()}\n   {[f.name for f in files]}")
    path = missionaries.solution_path()
    print(f"   Zgjidhja optimale ({len(path) - 1} kalime): "
          + " -> ".join(str(s) for s in path) + "\n")

    tree, schedule = rws.build_tree()
    files = tree.save(out, "rotating_workforce", rankdir="TB")
    print(tree.to_text())
    print(f"-> {tree.counts()}\n   {[f.name for f in files]}")
    if schedule:
        print("\nOrari i gjetur (cikel 3-javor):")
        print(rws.format_schedule(schedule))
    print(f"\nFajllat u ruajten ne: {out}")


# ---------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detyra 1 – Teknikat e painformuara te kerkimit (Uninformed Search)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("golfers", help="Social Golfers – DFS + Backtracking")
    p.add_argument("--groups", type=int, default=8, help="numri i grupeve g (default 8)")
    p.add_argument("--size", type=int, default=4, help="lojtare per grup p (default 4)")
    p.add_argument("--weeks", type=int, default=5, help="numri i javeve w (default 5)")
    p.add_argument("--max-weeks", action="store_true",
                   help="gjej sa me shume jave (DFS + restarts)")
    p.add_argument("--restarts", type=int, default=10)
    p.add_argument("--time-limit", type=float, default=10.0, help="sekonda (per run)")
    p.set_defaults(func=run_golfers)

    p = sub.add_parser("sudoku", help="Sudoku – BFS + Backtracking")
    p.add_argument("--level", choices=["easy", "medium", "hard", "all"], default="easy")
    p.add_argument("--every", action="store_true", help="zgjidh te gjitha enigmat e nivelit")
    p.add_argument("--puzzle", help="enigma si 81 karaktere (0 ose . per bosh)")
    p.add_argument("--generate", choices=["easy", "medium", "hard"],
                   help="gjenero enigme te re me zgjidhje unike")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--ordering", choices=["mrv", "fixed"], default="mrv",
                   help="renditja e variablave (default mrv)")
    p.add_argument("--time-limit", type=float, default=60.0)
    p.set_defaults(func=run_sudoku)

    p = sub.add_parser("latin", help="Latin Square – IDDFS + Backtracking")
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--full", action="store_true",
                   help="pa symmetry breaking (rreshti/kolona e pare jo te fiksuara)")
    p.add_argument("--time-limit", type=float, default=60.0)
    p.set_defaults(func=run_latin)

    p = sub.add_parser("trees", help="Search Trees: 8-Puzzle, M&C, RWS")
    p.add_argument("--depth", type=int, default=3, help="thellesia e pemes se 8-puzzle")
    p.set_defaults(func=run_trees)

    p = sub.add_parser("all", help="ekzekuto te gjitha detyrat")
    p.set_defaults(func=run_all)
    return parser


def run_all(_: argparse.Namespace) -> None:
    parser = build_parser()
    for argv in (["golfers", "--weeks", "5"], ["sudoku", "--level", "all"],
                 ["latin", "--n", "5"], ["trees"]):
        ns = parser.parse_args(argv)
        ns.func(ns)


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
