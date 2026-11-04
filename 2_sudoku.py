"""Sudoku Solver – BFS + Backtracking.

Modelimi:
    Gjendja   : string me 81 karaktere ('0' = qelizë bosh)
    Variablat : qelizat bosh X[r][c]
    Domain-i  : {1, ..., 9}
    Kufizimet : AllDifferent në çdo rresht, kolonë dhe kuti 3x3
    Veprimi   : vendos një vlerë të lejuar në qelizën bosh
    Goal      : nuk ka më qeliza bosh

Ekzekutimi:  python 2_sudoku.py          (të gjitha nivelet)
             python 2_sudoku.py hard     (vetëm një nivel)
"""
import sys
from collections import deque

PUZZLES = {
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
        "000000012003600000000007000410020000000500300700000600280000040000300500000000000",
    ],
}

# PEERS[i] = qelizat në të njëjtin rresht, kolonë ose kuti me qelizën i
PEERS = [{j for j in range(81) if j != i and (j // 9 == i // 9 or j % 9 == i % 9 or
          (j // 27, j % 9 // 3) == (i // 27, i % 9 // 3))} for i in range(81)]


def kandidatet(s, i):
    """Domain-i i qelizës i pas heqjes së vlerave që shkelin kufizimet."""
    return [d for d in "123456789" if d not in {s[j] for j in PEERS[i]}]


def bfs(start):
    radha = deque([start])                      # FIFO -> BFS
    nyje = frontier_max = 0
    while radha:
        s = radha.popleft()
        nyje += 1
        if "0" not in s:                        # GOAL
            return s, nyje, frontier_max
        # zgjidh qelizën bosh me më pak kandidatë (MRV)
        i, vlerat = None, None
        for k in range(81):
            if s[k] == "0":
                kk = kandidatet(s, k)
                if vlerat is None or len(kk) < len(vlerat):
                    i, vlerat = k, kk
                    if len(kk) <= 1:
                        break
        for d in vlerat:                        # vetëm vlerat e lejuara (prune)
            radha.append(s[:i] + d + s[i + 1:])
        frontier_max = max(frontier_max, len(radha))
        # nëse vlerat == [] s'shtohet asgjë: dega braktiset -> BACKTRACK
    return None, nyje, frontier_max


def objective(s):
    """f = konflikte në rreshta/kolona/kuti + qeliza bosh. f = 0 => zgjidhje."""
    konflikte = sum(1 for i in range(81) if s[i] != "0"
                    for j in PEERS[i] if j > i and s[j] == s[i])
    return konflikte + s.count("0")


def shfaq(s):
    for r in range(9):
        if r in (3, 6):
            print("------+-------+------")
        rr = s[r * 9:r * 9 + 9].replace("0", ".")
        print(" ".join(rr[:3]), "|", " ".join(rr[3:6]), "|", " ".join(rr[6:]))


if __name__ == "__main__":
    nivelet = [sys.argv[1]] if len(sys.argv) > 1 else PUZZLES
    for niveli in nivelet:
        for nr, enigma in enumerate(PUZZLES[niveli], 1):
            k = enigma.count("0")
            print(f"\n===== {niveli.upper()} #{nr} =====  f = {objective(enigma)}, "
                  f"landscape 9^{k} ≈ 10^{len(str(9 ** k)) - 1}")
            shfaq(enigma)
            zgjidhja, nyje, fmax = bfs(enigma)
            print("\nZgjidhja:")
            shfaq(zgjidhja)
            print(f"Objective f = {objective(zgjidhja)}, nyje: {nyje}, frontier max: {fmax}")
