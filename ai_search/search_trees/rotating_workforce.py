"""Search Tree për Rotating Workforce Scheduling (RWS).

Instanca (e vogël, për t'u vizatuar):
* 3 punëtorë, cikël 3-javor. Orari është matricë 3 × 7: rreshti i = java i e
  ciklit. Punëtori që e fillon në rreshtin 1 kalon në rreshtin 2 javën tjetër,
  e kështu me radhë (orari lexohet si një varg ciklik me 21 ditë).
* Ndërrimet: D = ditë, N = natë, - = pushim.

Kufizimet:
    C1  Kërkesa ditore: çdo ditë (kolonë) duhet 1 × D, 1 × N, 1 × -.
    C2  Ndalohet sekuenca N → D (pa pushim pas ndërrimit të natës).
    C3  Maksimum 4 ditë pune radhazi.
    C4  Maksimum 2 netë radhazi.
    C5  Blloku i punës zgjat të paktën 2 ditë (nuk lejohet 1 ditë pune e vetme
        mes dy pushimeve).

Modelimi i kërkimit:
* Variablat: kolonat (ditët) 0..6.
* Domain-i : 3! = 6 permutacione të {D, N, -} (kjo e plotëson C1 automatikisht).
* Veprimi  : cakto permutacionin për ditën e radhës.
* Pema     : DFS me backtracking; degët që shkelin C2–C4 preren (të kuqe).
"""

from __future__ import annotations

from itertools import permutations
from typing import List, Optional, Sequence, Tuple

from ai_search.search_trees.tree import SearchTree

SHIFTS = ("D", "N", "-")
EMPLOYEES = 3
DAYS = 7
MAX_WORK = 4
MAX_NIGHTS = 2
MIN_WORK = 2
COLUMNS: List[Tuple[str, ...]] = list(permutations(SHIFTS))
DAY_NAMES = ["Hë", "Ma", "Më", "En", "Pr", "Sh", "Di"]

Schedule = List[List[str]]


def _sequence(columns: Sequence[Tuple[str, ...]], complete: bool) -> List[str]:
    """Kthen orarin si varg (rreshtat njëri pas tjetrit)."""
    rows = [[col[r] for col in columns] for r in range(EMPLOYEES)]
    if not complete:
        return []
    return [s for row in rows for s in row]


def _row_ok(row: Sequence[str]) -> bool:
    work = nights = 0
    for i, s in enumerate(row):
        if i > 0 and row[i - 1] == "N" and s == "D":
            return False                                     # C2
        work = work + 1 if s != "-" else 0
        nights = nights + 1 if s == "N" else 0
        if work > MAX_WORK or nights > MAX_NIGHTS:           # C3, C4
            return False
    # C5: blloqet e punës që janë "të mbyllura" (pushim - punë - pushim).
    i = 0
    while i < len(row):
        if row[i] != "-" and i > 0 and row[i - 1] == "-":
            j = i
            while j < len(row) and row[j] != "-":
                j += 1
            if j < len(row) and j - i < MIN_WORK:
                return False
            i = j
        else:
            i += 1
    return True


def is_consistent(columns: Sequence[Tuple[str, ...]]) -> bool:
    """Kontrollon kufizimet për një orar të pjesshëm (kolonat 0..k)."""
    for r in range(EMPLOYEES):
        if not _row_ok([col[r] for col in columns]):
            return False
    if len(columns) == DAYS:
        seq = _sequence(columns, complete=True)
        cyclic = seq + seq[: DAYS]                            # mbështjellja ciklike
        if not _row_ok(cyclic):
            return False
    return True


def label(column: Tuple[str, ...], day: int) -> str:
    return f"{DAY_NAMES[day]}\n" + "\n".join(f"P{i + 1}:{s}" for i, s in enumerate(column))


def build_tree(max_nodes: int = 120) -> Tuple[SearchTree, Optional[Schedule]]:
    """DFS + backtracking; çdo nyje e gjeneruar shtohet në pemë.

    Kthen pemën dhe orarin e gjetur (si matricë 3×7)."""
    tree = SearchTree("Rotating Workforce Scheduling — Search Tree (DFS + Backtracking)")
    root = tree.add("Start\n(orar bosh)")
    solution: List[Optional[Schedule]] = [None]
    goal: List[Optional[int]] = [None]

    def dfs(nid: int, columns: List[Tuple[str, ...]]) -> bool:
        day = len(columns)
        if day == DAYS:
            return True
        for col in COLUMNS:
            if len(tree.nodes) >= max_nodes:
                tree.nodes[nid].status = "frontier"
                return False
            columns.append(col)
            ok = is_consistent(columns)
            cid = tree.add(label(col, day), nid, f"dita {day + 1}",
                           "normal" if ok else "invalid")
            if ok and dfs(cid, columns):
                if goal[0] is None:
                    goal[0] = cid
                    tree.nodes[cid].status = "goal"
                return True
            columns.pop()
        return False

    columns: List[Tuple[str, ...]] = []
    if dfs(root, columns):
        solution[0] = [[col[r] for col in columns] for r in range(EMPLOYEES)]
    if goal[0] is not None:
        tree.mark_path(goal[0])
    return tree, solution[0]


def solve() -> Tuple[Optional[Schedule], int]:
    """DFS i plotë pa kufi nyjesh; kthen (orari, nyje_të_vizituara)."""
    visited = 0
    columns: List[Tuple[str, ...]] = []

    def dfs() -> bool:
        nonlocal visited
        visited += 1
        if len(columns) == DAYS:
            return True
        for col in COLUMNS:
            columns.append(col)
            if is_consistent(columns) and dfs():
                return True
            columns.pop()
        return False

    found = dfs()
    if not found:
        return None, visited
    return [[col[r] for col in columns] for r in range(EMPLOYEES)], visited


def format_schedule(schedule: Schedule) -> str:
    header = "Java | " + " ".join(f"{d:>2}" for d in DAY_NAMES)
    lines = [header, "-" * len(header)]
    for i, row in enumerate(schedule, 1):
        lines.append(f"  {i}  | " + " ".join(f"{s:>2}" for s in row))
    return "\n".join(lines)
