"""Enigma Sudoku të ndara në tri nivele: Easy, Medium, Hard.

Të gjitha enigmat janë verifikuar (shih ``tests/test_sudoku.py``) që kanë
saktësisht një zgjidhje. Niveli bazohet në numrin e të dhënave (clues) dhe në
sa punë i duhet kërkimit (sa nyje zgjeron BFS).

| Niveli | Clues  | Karakteristika                                             |
|--------|--------|------------------------------------------------------------|
| Easy   | 30–36  | shumë qeliza kanë vetëm 1 kandidat                         |
| Medium | 28–30  | duhen disa degëzime                                        |
| Hard   | 17     | minimumi teorik i clues (17), degëzim i madh              |
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from ai_search.sudoku.solver import DIGITS, PEERS, count_solutions

PUZZLES: Dict[str, List[str]] = {
    "easy": [
        "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
        "003020600900305001001806400008102900700000008006708200002609500800203009005010300",
        "000260701680070090190004500820100040004602900050003028009300074040050036703018000",
    ],
    "medium": [
        "200080300060070084030500209000105408000000000402706000301007040720040060004010003",
        "030050040008010500460000012070502080000603000040109030250000098001020600080060020",
        "000000907000420180000705026100904000050000040000507009920108000034059000507000000",
    ],
    "hard": [
        "000000010400000000020000000000050407008000300001090000300400200050100000000806000",
        "400000805030000000000700000020000060000080400000010000000603070500200000104000000",
        "000000000000003085001020000000507000004000100090000000500000073002010000000040009",
    ],
}

LEVELS = tuple(PUZZLES.keys())

# Numri i synuar i clues për gjeneratorin.
_TARGET_CLUES = {"easy": 36, "medium": 30, "hard": 25}


def get_puzzle(level: str, index: int = 0) -> str:
    level = level.lower()
    if level not in PUZZLES:
        raise ValueError(f"Niveli duhet të jetë një nga {LEVELS}")
    return PUZZLES[level][index % len(PUZZLES[level])]


def _random_full_grid(rng: random.Random) -> str:
    grid = ["0"] * 81

    def fill(i: int) -> bool:
        if i == 81:
            return True
        used = {grid[j] for j in PEERS[i]}
        digits = [d for d in DIGITS if d not in used]
        rng.shuffle(digits)
        for d in digits:
            grid[i] = d
            if fill(i + 1):
                return True
        grid[i] = "0"
        return False

    fill(0)
    return "".join(grid)


def generate(level: str = "medium", seed: Optional[int] = None) -> str:
    """Gjeneron një Sudoku të ri me zgjidhje unike për nivelin e dhënë.

    1. Krijon një grid të plotë të rastësishëm (DFS me vlera të përziera).
    2. Heq qeliza një nga një (në renditje të rastësishme) duke e mbajtur
       heqjen vetëm nëse enigma mbetet me zgjidhje unike.
    3. Ndalet kur arrihet numri i synuar i clues për nivelin.
    """
    level = level.lower()
    if level not in _TARGET_CLUES:
        raise ValueError(f"Niveli duhet të jetë një nga {LEVELS}")
    rng = random.Random(seed)
    grid = list(_random_full_grid(rng))
    target = _TARGET_CLUES[level]

    cells = list(range(81))
    rng.shuffle(cells)
    clues = 81
    for i in cells:
        if clues <= target:
            break
        backup = grid[i]
        grid[i] = "0"
        if count_solutions("".join(grid), limit=2) == 1:
            clues -= 1
        else:
            grid[i] = backup
    return "".join(grid)
