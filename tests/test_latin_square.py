import pytest

from ai_search.latin_square.solver import (
    LatinSquareIDDFS, cyclic_construction, is_valid_latin_square, objective,
)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_iddfs_reduced_finds_valid_square(n):
    result = LatinSquareIDDFS(n, reduced=True).solve()
    assert result.solved
    assert is_valid_latin_square(result.grid)
    assert objective(result.grid) == 0


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_iddfs_full_model_finds_valid_square(n):
    result = LatinSquareIDDFS(n, reduced=False).solve()
    assert result.solved and is_valid_latin_square(result.grid)


def test_iddfs_finds_solution_in_last_iteration():
    result = LatinSquareIDDFS(4).solve()
    # IDDFS provon kufijtë 0..d, ku d = numri i qelizave bosh
    assert result.stats.iterations == result.depth_of_solution + 1
    assert len(result.nodes_per_iteration) == result.stats.iterations


def test_reduced_form_keeps_first_row_and_column():
    grid = LatinSquareIDDFS(5).solve().grid
    assert grid[0] == [1, 2, 3, 4, 5]
    assert [row[0] for row in grid] == [1, 2, 3, 4, 5]


def test_timeout_is_reported():
    result = LatinSquareIDDFS(8).solve(time_limit=0.2)
    assert result.timed_out and not result.solved


def test_objective_counts_conflicts_and_blanks():
    assert objective([[1, 1], [0, 2]]) == 1 + 1      # 1 konflikt në rresht + 1 bosh
    assert objective(cyclic_construction(6)) == 0


def test_cyclic_matches_assignment_example():
    assert cyclic_construction(5)[0] == [5, 1, 2, 3, 4]
    assert cyclic_construction(5)[1] == [4, 5, 1, 2, 3]
