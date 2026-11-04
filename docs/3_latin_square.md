# 3. Latin Square — IDDFS + Backtracking

> Kodi: [`3_latin_square.py`](../3_latin_square.py)

## 3.1 Përshkrimi

Një **Latin Square** është grid `n × n`, i mbushur me numrat `1..n`, ku secili numër paraqitet saktësisht një herë në çdo rresht dhe në çdo kolonë. Për hyrjen `n` printohet një matricë e tillë.

```
Hyrja: 5
Dalja:
1 2 3 4 5
2 1 4 5 3
3 4 5 1 2
4 5 2 3 1
5 3 1 2 4
```

> Dalja ndryshon nga shembulli i detyrës (`5 1 2 3 4 / 4 5 1 2 3 / ...`), por është po aq e saktë: një `n` ka shumë Latin Squares të vlefshme. IDDFS kthen të parën që gjen.

## 3.2 Modelimi

| Elementi | Përkufizimi |
|---|---|
| **Gjendja** | Grid `n × n` i plotësuar pjesërisht (`0` = bosh) |
| **Gjendja fillestare** | Rreshti i parë dhe kolona e parë = `1, 2, ..., n`, pjesa tjetër bosh |
| **Veprimi** | Vendos vlerën `v ∈ {1..n}` në qelizën e radhës bosh (rresht pas rreshti) |
| **Goal test** | Të gjitha qelizat janë mbushur |
| **Thellësia e zgjidhjes** | `d = (n − 1)²` (numri i qelizave bosh) |

## 3.3 Reprezentimi

**Variablat:** `X[r][c]`, `0 ≤ r, c < n`, gjithsej `n²` variabla, prej të cilave `(n−1)²` janë të lira.

**Domain-i:** `D = {1, ..., n}`.

**Kufizimet:**

| | Kufizimi | Në kod |
|---|---|---|
| C1 | Çdo vlerë një herë në çdo rresht | `v in grid[r]` |
| C2 | Çdo vlerë një herë në çdo kolonë | `any(grid[i][c] == v ...)` |

**Symmetry breaking: forma e reduktuar.** Rreshti i parë dhe kolona e parë fiksohen në `1, 2, ..., n`. Çdo Latin Square mund të shndërrohet në këtë formë duke i ndërruar kolonat dhe rreshtat, prandaj nuk humbet asnjë zgjidhje, por hapësira zvogëlohet shumë (te n = 5, nga 25 në 16 qeliza të lira).

## 3.4 Objective function

Problem **minimizimi**:

```
f(X) = Σ_rreshta (vlera të përsëritura) + Σ_kolona (vlera të përsëritura) + (qeliza bosh)
```

- `[[1,1],[0,2]]` → 1 përsëritje në rreshtin e parë + 1 qelizë bosh → `f = 2`
- **`f(X) = 0` ⇔ `X` është Latin Square i vlefshëm**

## 3.5 Landscape

| n | Pa kufizime `n^(n²)` | Forma e reduktuar `n^((n−1)²)` | Latin Squares të vlefshme |
|---:|---:|---:|---:|
| 3 | 19 683 | 81 | 12 |
| 4 | ≈ 4.3 × 10^9 | 262 144 | 576 |
| 5 | ≈ 3.0 × 10^17 | ≈ 1.5 × 10^11 | 161 280 |
| 6 | ≈ 1.0 × 10^28 | ≈ 2.8 × 10^19 | 812 851 200 |

Problemi ka **gjithmonë zgjidhje** për çdo `n ≥ 1`. P.sh. zhvendosja ciklike e rreshtit të parë e jep gjithmonë një Latin Square, si te shembulli i detyrës.

## 3.6 Algoritmi: IDDFS + Backtracking

```
IDDFS():
    for kufiri = 0, 1, 2, ..., d:             # rrit kufirin e thellësisë
        if DLS(0, kufiri): return SUCCESS

DLS(thellesia, kufiri):                       # Depth-Limited Search
    if thellesia == d:      return TRUE        # GOAL
    if thellesia == kufiri: return FALSE       # cutoff
    (r, c) ← qeliza bosh nr. thellesia
    for v in 1..n:
        if v në rreshtin r ose kolonën c: prune
        vendos v
        if DLS(thellesia + 1, kufiri): return TRUE
        hiq v                                  # BACKTRACK
    return FALSE
```

**IDDFS** = DFS i përsëritur me kufi thellësie që rritet: 0, 1, 2, ... Në çdo iteracion bëhet një DFS i plotë deri te kufiri.

**Vetitë:**
- **Memoria `O(d)`**, si DFS, sepse ruhet vetëm rruga aktuale
- **Complete dhe optimal**, si BFS, sepse gjen zgjidhjen më të cekët
- **Kostoja:** nivelet e sipërme rivizitohen në çdo iteracion

## 3.7 Rezultatet

| n | Iteracione | Nyje gjithsej | Koha |
|---:|---:|---:|---:|
| 1 | 1 | 1 | 0 s |
| 2 | 2 | 3 | 0 s |
| 3 | 5 | 19 | 0 s |
| 4 | 10 | 161 | 0 s |
| 5 | 17 | 4 914 | < 0.1 s |
| 6 | 26 | 1 194 077 | ≈ 1.5 s |
| 7 | – | – | nuk përfundon brenda 30 s |

**Nyjet për çdo iteracion (n = 5):**

```
kufiri: 0  1   2   3   4   5    6    7    8    9   10   11   12   13   14   15  16
nyje:   1  5  14  28  39  64  125  201  247  323  433  569  625  681  737  793  29
```

### Çka tregon kjo tabelë

Te Latin Square **të gjitha zgjidhjet janë në të njëjtën thellësi** (`d = 16` për n = 5). Prandaj iteracionet me kufi `< 16` **nuk mund ta gjejnë kurrë** zgjidhjen dhe e eksplorojnë plotësisht pemën deri te kufiri. Iteracioni i fundit e gjen zgjidhjen me vetëm **29 nyje**, ndërsa iteracionet e mëparshme harxhojnë **4 885**.

Ky është kompromisi i IDDFS: shkëlqen kur **nuk e dimë** thellësinë e zgjidhjes. Këtu thellësia dihet (`(n−1)²`), prandaj DFS i thjeshtë do të ishte më i shpejtë. Por detyra kërkon IDDFS, dhe rezultatet e tregojnë qartë këtë kosto.

Për `n ≥ 7` numri i katrorëve të reduktuar (≈ 1.7 × 10^7) e bën iteracionin e parafundit shumë të gjatë.
