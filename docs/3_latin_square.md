# 3. Latin Square — IDDFS + Backtracking

> Kodi: [`ai_search/latin_square/solver.py`](../ai_search/latin_square/solver.py)

## 3.1 Përshkrimi

Një **Latin Square** është grid `n × n` i mbushur me `n` numra të ndryshëm, ku secili paraqitet saktësisht një herë në çdo rresht dhe në çdo kolonë. Për hyrjen `n` duhet të printohet një matricë e tillë me numrat `1..n`.

```
Hyrja: 5            Dalja (IDDFS, forma e reduktuar):
                    1 2 3 4 5
                    2 1 4 5 3
                    3 4 5 1 2
                    4 5 2 3 1
                    5 3 1 2 4
```

## 3.2 Modelimi

| Elementi | Përkufizimi |
|---|---|
| **Gjendja** | Grid `n × n` i pjesshëm (`0` = qelizë bosh) |
| **Gjendja fillestare** | Grid bosh, ose me rreshtin/kolonën e parë të fiksuar (forma e reduktuar) |
| **Veprimi** | Vendos vlerën `v ∈ {1..n}` në qelizën e radhës bosh (renditje row-major) |
| **Goal test** | Të gjitha qelizat janë mbushur |
| **Thellësia e zgjidhjes** | `d = n²` (full) ose `d = (n−1)²` (reduced) |

## 3.3 Reprezentimi

**Variablat**: `X[r][c]`, `0 ≤ r, c < n` → `n²` variabla.

**Domain-i**: `D = {1, 2, ..., n}`.

**Kufizimet**:

| | Kufizimi |
|---|---|
| C1 | `AllDifferent(X[r][0..n−1])` për çdo rresht `r` |
| C2 | `AllDifferent(X[0..n−1][c])` për çdo kolonë `c` |

**Symmetry breaking – forma e reduktuar** (`reduced=True`, default): rreshti i parë dhe kolona e parë fiksohen në `1, 2, ..., n`. Çdo Latin Square mund të shndërrohet në këtë formë duke ndërruar kolonat dhe pastaj rreshtat, kështu që asnjë zgjidhje nuk humbet (deri në izomorfizëm), por mbeten vetëm `(n−1)²` variabla të lira.

Kontrolli i kufizimeve bëhet me **bitmask**: `row_used[r]` dhe `col_used[c]` – vlera `v` lejohet vetëm nëse biti `v` nuk është i ndezur në asnjërin.

## 3.4 Objective function

Problem **minimizimi**:

```
f(X) = Σ_r (vlera të përsëritura në rreshtin r) + Σ_c (vlera të përsëritura në kolonën c) + (qeliza bosh)
```

* `f(X) = 0` ⇔ `X` është Latin Square i vlefshëm.
* Shembull: `[[1,1],[0,2]]` → 1 konflikt në rresht + 1 qelizë bosh → `f = 2`.

## 3.5 Landscape

| n | Pa kufizime `n^(n²)` | Reduced `n^((n−1)²)` | Latin Squares të vlefshme | Të reduktuara |
|---:|---:|---:|---:|---:|
| 3 | 19 683 | 81 | 12 | 1 |
| 4 | ≈ 4.29 × 10^9 | 262 144 | 576 | 4 |
| 5 | ≈ 2.98 × 10^17 | ≈ 1.52 × 10^11 | 161 280 | 56 |
| 6 | ≈ 1.03 × 10^28 | ≈ 2.84 × 10^19 | 812 851 200 | 9 408 |
| 7 | ≈ 2.56 × 10^41 | ≈ 2.65 × 10^30 | ≈ 6.15 × 10^13 | 16 942 080 |

Problemi **ka gjithmonë zgjidhje** për çdo `n ≥ 1` – p.sh. konstruksioni ciklik `L[r][c] = (c − r − 1) mod n + 1` jep pikërisht shembullin e detyrës (`5 1 2 3 4 / 4 5 1 2 3 / ...`). Në kod ky konstruksion (`cyclic_construction`) përdoret vetëm për krahasim dhe teste.

## 3.6 Algoritmi: IDDFS + Backtracking

```
IDDFS():
    for L = 0, 1, 2, ..., d:                      # rrit kufirin e thellësisë
        if DLS(0, L): return SUCCESS

DLS(depth, L):                                    # Depth-Limited Search
    if depth == d: return SUCCESS                 # goal test
    if depth == L: return CUTOFF
    (r, c) ← qeliza bosh nr. depth
    for v in 1..n:
        if v në rreshtin r ose kolonën c: prune   # BACKTRACKING
        vendos v
        if DLS(depth + 1, L): return SUCCESS
        hiq v                                     # zhbëj veprimin
    return FAIL
```

**Vetitë e IDDFS**: complete, optimal (gjen zgjidhjen më të cekët), memoria **O(b·d)** si DFS – por i ri-viziton nivelet e sipërme në çdo iteracion.

### Vërejtje e rëndësishme për këtë problem

Te Latin Square të gjitha zgjidhjet janë në të njëjtën thellësi `d`. Prandaj iteracionet `L < d` nuk mund ta gjejnë kurrë zgjidhjen dhe i eksplorojnë **plotësisht** të gjitha gjendjet e qëndrueshme deri në thellësinë `L`. Iteracioni i fundit (`L = d`) e gjen zgjidhjen shumë shpejt (p.sh. 29 nyje për n = 5).

Nyjet e zgjeruara për çdo iteracion (n = 5, reduced):

```
L:      0  1  2   3   4   5    6    7    8    9   10   11   12   13   14   15  16
nyje:   1  5  14  28  39  64  125  201  247  323  433  569  625  681  737  793  29
```

Kjo tregon qartë koston e IDDFS: puna dominohet nga iteracionet që "nuk mund të fitojnë". IDDFS shkëlqen kur thellësia e zgjidhjes **nuk dihet**; këtu dihet (`d = (n−1)²`), prandaj DFS i thjeshtë do të ishte më efikas – por detyra kërkon IDDFS, dhe rezultatet e dokumentojnë këtë kompromis.

## 3.7 Rezultatet

| n | Modeli | Iteracione | Nyje të zgjeruara | Koha (s) |
|---|--------|-----------:|------------------:|---------:|
| 2 | reduced | 2 | 3 | 0.000 |
| 2 | full | 5 | 21 | 0.000 |
| 3 | reduced | 5 | 19 | 0.000 |
| 3 | full | 10 | 326 | 0.000 |
| 4 | reduced | 10 | 161 | 0.000 |
| 4 | full | 17 | 24 861 | 0.015 |
| 5 | reduced | 17 | 4 914 | 0.004 |
| 5 | full | 26 | 13 505 923 | 10.08 |
| 6 | reduced | 26 | 1 194 077 | 0.98 |
| 7 | reduced | 21+ | > 40 000 000 | > 30 (timeout) |

**Përfundimi**: symmetry breaking është vendimtar – për n = 5 zvogëlon punën nga 13.5 milionë në 4 914 nyje (≈ 2 750× më pak). Me IDDFS, `n ≤ 6` zgjidhet nën 1 sekondë; për `n ≥ 7` numri i katrorëve të reduktuar (≈ 1.7 × 10^7) e bën iteracionin e parafundit shumë të shtrenjtë në Python.

## 3.8 Ekzekutimi

```bash
python main.py latin --n 5                  # forma e reduktuar (default)
python main.py latin --n 4 --full           # modeli i plotë, pa symmetry breaking
python main.py latin --n 7 --time-limit 30  # demonstron kufirin e IDDFS
```
