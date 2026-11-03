import pytest

from ai_search.social_golfers.solver import (
    SocialGolfersDFS, is_valid, landscape, objective, search_max_weeks, upper_bound_weeks,
)


@pytest.mark.parametrize("weeks", [1, 2, 3, 4, 5])
def test_dfs_finds_32_golfers_schedule(weeks):
    result = SocialGolfersDFS(8, 4, weeks).solve(time_limit=10)
    assert result.solved
    assert is_valid(result.schedule, 8, 4)
    assert objective(result.schedule) == 0


def test_kirkman_9_golfers_4_weeks():
    # 9 lojtarë në 3 grupe me 3: maksimumi është 4 javë (Kirkman)
    result = SocialGolfersDFS(3, 3, 4).solve(time_limit=10)
    assert result.solved and is_valid(result.schedule, 3, 3)


def test_dfs_proves_infeasibility_for_small_instance():
    # 9 lojtarë, 3x3: 5 javë kërkojnë 5*2 = 10 partnerë > 8 -> e pamundur
    result = SocialGolfersDFS(3, 3, 5).solve(time_limit=10)
    assert not result.solved and not result.timed_out
    assert result.best_weeks == 4


def test_randomized_restarts_reach_at_least_five_weeks():
    result = search_max_weeks(8, 4, restarts=3, time_per_run=1.0)
    assert result.best_weeks >= 5
    assert is_valid(result.best_schedule, 8, 4)


def test_objective_counts_repeated_pairs():
    week = [[0, 1], [2, 3]]
    assert objective([week]) == 0
    assert objective([week, week]) == 2


def test_upper_bound_and_landscape():
    assert upper_bound_weeks(8, 4) == 10
    land = landscape(8, 4, 1)
    assert land["ndarje_per_jave"] == 59287247761257140625  # 32!/(4!^8 * 8!)
    assert land["cifte_totale C(n,2)"] == 496
