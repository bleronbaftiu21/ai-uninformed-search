import pytest

from ai_search.sudoku.puzzles import LEVELS, PUZZLES, generate
from ai_search.sudoku.solver import (
    SudokuBFS, count_solutions, is_consistent, is_solved, objective, parse,
)

ALL = [(level, p) for level in LEVELS for p in PUZZLES[level]]


@pytest.mark.parametrize("level,puzzle", ALL)
def test_every_puzzle_has_unique_solution(level, puzzle):
    assert count_solutions(puzzle) == 1


@pytest.mark.parametrize("level,puzzle", ALL)
def test_bfs_mrv_solves_all_levels(level, puzzle):
    result = SudokuBFS("mrv").solve(puzzle)
    assert result.solved and is_solved(result.solution)
    assert objective(result.solution) == 0
    # zgjidhja duhet të respektojë të dhënat fillestare
    assert all(c == "0" or c == s for c, s in zip(puzzle, result.solution))


@pytest.mark.parametrize("puzzle", PUZZLES["easy"] + PUZZLES["medium"])
def test_bfs_fixed_order_solves_easy_and_medium(puzzle):
    result = SudokuBFS("fixed").solve(puzzle)
    assert result.solved and is_solved(result.solution)


def test_bfs_explores_level_by_level():
    result = SudokuBFS("fixed").solve(PUZZLES["medium"][0])
    assert sum(result.nodes_per_level) == result.stats.nodes_expanded
    assert result.nodes_per_level[0] == 1


def test_invalid_puzzle_returns_no_solution():
    bad = "11" + "0" * 79
    assert not is_consistent(bad)
    assert not SudokuBFS().solve(bad).solved


def test_parse_accepts_dots_and_whitespace():
    text = "\n".join(". " * 9 for _ in range(9))
    assert parse(text) == "0" * 81
    with pytest.raises(ValueError):
        parse("123")


@pytest.mark.parametrize("level", LEVELS)
def test_generator_produces_unique_puzzles(level):
    puzzle = generate(level, seed=42)
    assert count_solutions(puzzle) == 1
    assert SudokuBFS().solve(puzzle).solved
