from ai_search.search_trees import eight_puzzle, missionaries, rotating_workforce as rws


def test_eight_puzzle_tree_contains_goal_at_depth_3():
    tree = eight_puzzle.build_tree(max_depth=3)
    goals = [n for n in tree.nodes if n.status == "goal"]
    assert goals and goals[0].depth == 3
    assert eight_puzzle.is_solvable(eight_puzzle.DEFAULT_START)


def test_missionaries_optimal_solution_has_11_crossings():
    path = missionaries.solution_path()
    assert path[0] == missionaries.START and path[-1] == missionaries.GOAL
    assert len(path) - 1 == 11
    assert all(missionaries.is_valid(s) for s in path)


def test_missionaries_tree_marks_invalid_and_repeated():
    counts = missionaries.build_tree().counts()
    assert counts["goal"] == 1
    assert counts["invalid"] > 0 and counts["repeated"] > 0


def test_rotating_workforce_schedule_respects_constraints():
    schedule, _ = rws.solve()
    assert schedule is not None
    for day in range(rws.DAYS):
        assert sorted(row[day] for row in schedule) == sorted(rws.SHIFTS)   # C1
    seq = [s for row in schedule for s in row]
    cyclic = seq + seq
    assert not any(a == "N" and b == "D" for a, b in zip(cyclic, cyclic[1:]))  # C2


def test_tree_exports(tmp_path):
    tree = eight_puzzle.build_tree(max_depth=1)
    files = tree.save(tmp_path, "t")
    assert (tmp_path / "t.dot").read_text().startswith("digraph")
    assert any(f.suffix == ".txt" for f in files)
