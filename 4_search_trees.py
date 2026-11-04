"""Search Trees: 8-Puzzle, Missionaries & Cannibals, Rotating Workforce Scheduling."""
import re
from collections import deque
from itertools import permutations


def printo(nyja, femijet, etiketa, prefix="", veprimi="", fundit=True):
    """Printon pemën; femijet[nyja] = lista e (veprimi, femija)."""
    lidhja = ("└── " if fundit else "├── ") if veprimi else ""
    hyrja = f"--{veprimi}--> " if veprimi else ""
    print(prefix + lidhja + hyrja + etiketa[nyja])
    if veprimi:
        prefix += "    " if fundit else "│   "
    lista = femijet.get(nyja, [])
    for k, (v, f) in enumerate(lista):
        printo(f, femijet, etiketa, prefix, v, k == len(lista) - 1)


# ---------------------------------------------------------------- 8-PUZZLE
def puzzle_pema(start="123046758", qellimi="123456780", thellesia=3):
    levizjet = {"U": -3, "D": 3, "L": -1, "R": 1}
    kundert = {"U": "D", "D": "U", "L": "R", "R": "L"}
    femijet, etiketa, id_ = {}, {0: start}, 1
    radha = deque([(0, start, 0, "")])                  # BFS
    while radha:
        nid, s, d, e_fundit = radha.popleft()
        if s == qellimi or d == thellesia:
            continue
        b = s.index("0")
        for m, delta in levizjet.items():
            if (m == "U" and b < 3) or (m == "D" and b > 5) or \
               (m == "L" and b % 3 == 0) or (m == "R" and b % 3 == 2) or \
               kundert[m] == e_fundit:                  # mos e zhbëj lëvizjen e fundit
                continue
            t = list(s); t[b], t[b + delta] = t[b + delta], t[b]
            t = "".join(t)
            femijet.setdefault(nid, []).append((m, id_))
            etiketa[id_] = t + (" [GOAL]" if t == qellimi else "")
            radha.append((id_, t, d + 1, m)); id_ += 1
    print("\n=== 8-PUZZLE (BFS, thellësia 3) ===")
    printo(0, femijet, etiketa)


# ---------------------------------------------------------------- MISSIONARIES & CANNIBALS
def mc_valid(m, c):
    return 0 <= m <= 3 and 0 <= c <= 3 and (m == 0 or m >= c) and (m == 3 or 3 - m >= 3 - c)


def mc_pema():
    start, qellimi = (3, 3, 1), (0, 0, 0)               # (M, C, varka) në bregun e majtë
    femijet, etiketa, id_ = {}, {0: str(start)}, 1
    radha, pare = deque([(0, start)]), {start}          # BFS
    while radha:
        nid, (m, c, b) = radha.popleft()
        if (m, c, b) == qellimi:
            break
        s = -1 if b else 1
        for dm, dc in [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]:
            f = (m + s * dm, c + s * dc, 1 - b)
            if not mc_valid(f[0], f[1]):
                continue                                # shkel kufizimin -> prune
            shenja = " [GOAL]" if f == qellimi else (" [përsëritur]" if f in pare else "")
            femijet.setdefault(nid, []).append((f"{dm}M{dc}C", id_))
            etiketa[id_] = str(f) + shenja
            if f not in pare:
                pare.add(f); radha.append((id_, f))
            id_ += 1
    print("\n=== MISSIONARIES & CANNIBALS (BFS) ===")
    printo(0, femijet, etiketa)


# ---------------------------------------------------------------- ROTATING WORKFORCE
def rws_valid(kolonat, plote):
    """3 punëtorë × 7 ditë; orari lexohet si cikël: rreshti 1, 2, 3, pastaj prapë 1."""
    rreshtat = ["".join(k[r] for k in kolonat) for r in range(3)]
    varg = "".join(rreshtat) if plote else None
    for x in ([varg + varg[:7]] if plote else rreshtat):
        if "ND" in x or "NNN" in x or re.search("[DN]{5}", x):
            return False                                # N->D, >2 netë, >4 ditë punë
    return True


def rws_pema():
    femijet, etiketa, id_ = {}, {0: "Start"}, [1]
    kolonat = []

    def dfs(nid):                                       # DFS + Backtracking
        if len(kolonat) == 7:
            return True
        for k in permutations("DN-"):                   # çdo ditë: 1 D, 1 N, 1 pushim
            kolonat.append(k)
            ok = rws_valid(kolonat, len(kolonat) == 7)
            f = id_[0]; id_[0] += 1
            femijet.setdefault(nid, []).append((f"dita {len(kolonat)}", f))
            etiketa[f] = "".join(k) + ("" if ok else " [X]")
            if ok and len(kolonat) == 7:
                etiketa[f] += " [GOAL]"
            if ok and dfs(f):
                return True
            kolonat.pop()                               # BACKTRACK
        return False

    dfs(0)
    print("\n=== ROTATING WORKFORCE (DFS + Backtracking) ===")
    print("Çdo nyje = ndërrimet e ditës për P1 P2 P3 (D=ditë, N=natë, -=pushim)")
    printo(0, femijet, etiketa)
    print("\nOrari:")
    for r in range(3):
        print(f"Java {r + 1}: " + " ".join(k[r] for k in kolonat))


if __name__ == "__main__":
    puzzle_pema()
    mc_pema()
    rws_pema()
