"""Latin Square – IDDFS + Backtracking.

Modelimi:
    Variablat : X[r][c], 0 <= r, c < n
    Domain-i  : {1, ..., n}
    Kufizimet : çdo numër paraqitet një herë në çdo rresht dhe çdo kolonë
    Veprimi   : vendos një vlerë në qelizën e radhës bosh
    Goal      : të gjitha qelizat janë mbushur
    Symmetry breaking: rreshti i parë dhe kolona e parë = 1, 2, ..., n

Ekzekutimi:  python 3_latin_square.py      (kërkon n)
"""
from math import factorial


def iddfs(n):
    grid = [[0] * n for _ in range(n)]
    for i in range(n):
        grid[0][i] = grid[i][0] = i + 1                 # forma e reduktuar
    bosh = [(r, c) for r in range(n) for c in range(n) if grid[r][c] == 0]
    nyje_per_iteracion = []

    def dls(thellesia, kufiri):                          # Depth-Limited Search
        nyje_per_iteracion[-1] += 1
        if thellesia == len(bosh):                       # GOAL
            return True
        if thellesia == kufiri:                          # cutoff
            return False
        r, c = bosh[thellesia]
        for v in range(1, n + 1):
            if v in grid[r] or any(grid[i][c] == v for i in range(n)):
                continue                                 # shkel kufizimin -> prune
            grid[r][c] = v
            if dls(thellesia + 1, kufiri):
                return True
            grid[r][c] = 0                               # BACKTRACK
        return False

    for kufiri in range(len(bosh) + 1):                  # rrit kufirin: 0, 1, 2, ...
        nyje_per_iteracion.append(0)
        if dls(0, kufiri):
            return grid, nyje_per_iteracion
    return None, nyje_per_iteracion


def objective(grid):
    """f = vlera të përsëritura në rreshta + në kolona + qeliza bosh."""
    n = len(grid)
    rreshta = sum(n - len(set(row)) for row in grid)
    kolona = sum(n - len({grid[r][c] for r in range(n)}) for c in range(n))
    return rreshta + kolona + sum(row.count(0) for row in grid)


if __name__ == "__main__":
    n = int(input("Hyrja: "))
    grid, iteracionet = iddfs(n)
    print("Dalja:")
    for row in grid:
        print(*row)
    print(f"\nObjective f = {objective(grid)}")
    print(f"Iteracione IDDFS: {len(iteracionet)} (kufiri 0..{len(iteracionet) - 1})")
    print(f"Nyje për iteracion: {iteracionet}")
    print(f"Nyje gjithsej: {sum(iteracionet)}")
    print(f"\nLandscape:")
    print(f"  Pa kufizime          n^(n²)     = {n ** (n * n):,}")
    print(f"  Forma e reduktuar    n^((n-1)²) = {n ** ((n - 1) ** 2):,}")
    print(f"  Rreshtat permutacione (n!)^n    = {factorial(n) ** n:,}")
