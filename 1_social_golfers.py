"""Social Golfers Problem – DFS + Backtracking.

Modelimi:
    Variablat : X[w][g][s] = lojtari në javën w, grupin g, vendin s
    Domain-i  : {0, 1, ..., n-1}
    C1        : çdo lojtar luan saktësisht një herë në javë
    C2        : çdo çift lojtarësh takohet më së shumti një herë
    Goal      : të gjitha vendet e W javëve janë mbushur pa shkelur C1, C2

Ekzekutimi:  python 1_social_golfers.py        (5 javë)
             python 1_social_golfers.py 3      (numri i javëve si argument)
"""
import sys
from math import factorial

G, P = 8, 4                                     # 8 grupe, 4 lojtarë për grup
W = int(sys.argv[1]) if len(sys.argv) > 1 else 5
N = G * P                                       # 32 lojtarë
orari = [[[] for _ in range(G)] for _ in range(W)]
takuar = [set() for _ in range(N)]              # takuar[a] = me kë është takuar a
nyje = prera = 0


def dfs(pos):
    global nyje, prera
    nyje += 1
    if pos == W * N:                                    # GOAL
        return True
    java, grupi = pos // N, pos % N // P
    grp = orari[java][grupi]
    luan = {x for g in orari[java] for x in g}          # kush luan këtë javë
    if grp:   kandidatet = range(grp[-1] + 1, N)        # rend rritës në grup
    else:     kandidatet = [min(set(range(N)) - luan)]  # i pari: më i vogli i lirë
    for v in kandidatet:
        if v in luan or takuar[v] & set(grp):           # C1, C2 -> prune
            prera += 1
            continue
        for x in grp: takuar[x].add(v); takuar[v].add(x)
        grp.append(v)
        if dfs(pos + 1):
            return True
        grp.pop()                                       # BACKTRACK
        for x in grp: takuar[x].discard(v); takuar[v].discard(x)
    return False


def objective(orari):
    """f(S) = Σ max(0, takime(a,b) - 1). f(S) = 0 => orar i vlefshëm."""
    takime = {}
    for java in orari:
        for grp in java:
            for i in range(len(grp)):
                for j in range(i + 1, len(grp)):
                    cift = (grp[i], grp[j])
                    takime[cift] = takime.get(cift, 0) + 1
    return sum(max(0, m - 1) for m in takime.values())


def landscape():
    ndarje = factorial(N) // (factorial(P) ** G * factorial(G))   # 32!/((4!)^8 · 8!)
    print(f"\nLandscape (w = {W}):")
    print(f"  Pa kufizime  n^(n·w) ≈ 10^{len(str(N ** (N * W))) - 1}")
    print(f"  Me C1        (n!)^w  ≈ 10^{len(str(factorial(N) ** W)) - 1}")
    print(f"  Ndarje       P^w     ≈ 10^{len(str(ndarje ** W)) - 1}   (P = {ndarje:,})")
    print(f"  Kufiri i sipërm i javëve = (n-1)/(p-1) = {(N - 1) // (P - 1)}")


if __name__ == "__main__":
    if dfs(0):
        for w, java in enumerate(orari, 1):
            print(f"Java {w}:", java)
        print(f"\nObjective f(S) = {objective(orari)}")
        print(f"Nyje të vizituara: {nyje}, degë të prera: {prera}")
    else:
        print("Nuk ka zgjidhje")
    landscape()
