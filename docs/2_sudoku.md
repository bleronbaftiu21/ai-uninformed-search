# 2. Sudoku Solver — BFS + Backtracking

> Kodi: [`ai_search/sudoku/solver.py`](../ai_search/sudoku/solver.py) · Enigmat: [`ai_search/sudoku/puzzles.py`](../ai_search/sudoku/puzzles.py)

## 2.1 Përshkrimi

Programi zgjidh një Sudoku 9 × 9 dhe parasheh tri nivele: **Easy, Medium, Hard**. Çdo rresht, kolonë dhe kuti 3 × 3 duhet të përmbajë numrat 1–9 saktësisht një herë.

## 2.2 Modelimi

| Elementi | Përkufizimi |
|---|---|
| **Gjendja** | Grid 9 × 9 i pjesshëm, i ruajtur si string me 81 karaktere (`'0'` = bosh) |
| **Gjendja fillestare** | Enigma e dhënë (clues) |
| **Veprimi** | Vendos vlerën `v` në qelizën e radhës bosh |
| **Modeli i tranzicionit** | `Result(s, (i, v))` = `s` me `s[i] = v` |
| **Goal test** | Nuk ka qeliza bosh (dhe, meqë çdo veprim respekton kufizimet, grid-i është i saktë) |
| **Kostoja** | 1 për veprim; të gjitha zgjidhjet janë në thellësinë `k` = numri i qelizave bosh |

## 2.3 Reprezentimi

**Variablat**: qelizat bosh `X[r][c]`, `0 ≤ r, c ≤ 8` (p.sh. 51 variabla për enigmën Easy #1, 64 për Hard).

**Domain-i**: `D = {1, 2, ..., 9}`. Gjatë kërkimit domain-i efektiv i një qelize është

```
D(r, c) = {1..9} \ { vlerat në rreshtin r, kolonën c dhe kutinë e (r, c) }
```

**Kufizimet** (27 kufizime AllDifferent):

| Kufizimi | Numri |
|---|---|
| `AllDifferent(rreshti r)` | 9 |
| `AllDifferent(kolona c)` | 9 |
| `AllDifferent(kutia b)` | 9 |

Në kod, për çdo qelizë llogariten një herë **peers** (20 qelizat në të njëjtin rresht, kolonë ose kuti), kështu që kontrolli i kufizimeve është i shpejtë.

## 2.4 Objective function

Problem **minimizimi**:

```
f(X) = Σ_{u ∈ rreshta ∪ kolona ∪ kuti} (numri i vlerave të përsëritura në u)  +  (numri i qelizave bosh)
```

* `f(X) = 0` ⇔ Sudoku është zgjidhur saktë.
* Për enigmën Easy #1 në fillim: `f = 51` (0 konflikte + 51 bosh).
* Çdo veprim i vlefshëm e ul `f` me saktësisht 1, prandaj thellësia e zgjidhjes = `f(fillimi)`.

## 2.5 Landscape

| Masa | Vlera |
|---|---|
| Grid-a pa kufizime `9^81` | ≈ 1.96 × 10^77 |
| Hapësira e Easy #1 (51 bosh) `9^51` | ≈ 4.63 × 10^48 |
| Hapësira e Hard (64 bosh) `9^64` | ≈ 1.17 × 10^61 |
| Numri i Sudoku-ve të plota të vlefshme | ≈ 6.67 × 10^21 |
| Zgjidhje për enigmë të mirëformuar | 1 (verifikuar në teste) |

Hapësira "e rrafshët" (`9^k`) është e pamundur të eksplorohet. Me backtracking, BFS sheh vetëm gjendjet **e qëndrueshme** (consistent) – për Easy #1 vetëm 4 632 nyje (fixed) ose 52 (MRV) nga 10^48.

## 2.6 Algoritmi: BFS + Backtracking

```
BFS(fillimi):
    frontier ← Queue([fillimi])                       # FIFO
    while frontier jo bosh:
        s ← frontier.popleft()
        i, vlerat ← zgjidh_qelizen(s)                # fixed ose MRV
        if i == None: return s                        # goal: s'ka qeliza bosh
        if vlerat == ∅: continue                      # dead end → BACKTRACK
        for v in vlerat:                              # vetëm vlera pa konflikt
            frontier.append(s me s[i] = v)
    return FAIL
```

**Backtracking te BFS** – BFS nuk "kthehet prapa" në kuptimin rekursiv si DFS; backtracking-u realizohet me:

1. **Pruning** – gjenerohen vetëm fëmijët që respektojnë kufizimet (vlerat e lejuara).
2. **Braktisja e dead ends** – gjendjet ku qeliza e radhës nuk ka asnjë vlerë të lejuar hidhen dhe kërkimi vazhdon me alternativat e tjera që janë në radhë.

**Renditja e variablave** (`--ordering`):

* `fixed` – qeliza e parë bosh (row-major). BFS "e pastër".
* `mrv` (default) – *Minimum Remaining Values*: qeliza me më pak kandidatë. Nuk e ndryshon BFS-në (radha mbetet FIFO dhe kërkimi mbetet i painformuar ndaj qëllimit); ndryshon vetëm cila variabël degëzohet – kjo zvogëlon faktorin e degëzimit.

Vetitë e BFS këtu: **complete** (gjen zgjidhjen nëse ekziston), **optimal** (të gjitha zgjidhjet janë në të njëjtën thellësi), por **memoria O(b^d)** – prandaj kodi ka kufi sigurie për frontier-in.

## 2.7 Nivelet dhe enigmat

| Niveli | Clues | Enigma |
|---|---:|---|
| Easy | 30–36 | 3 enigma (përfshirë shembullin klasik nga Wikipedia) |
| Medium | 28–30 | 3 enigma |
| Hard | 17 | 3 enigma me minimumin teorik të clues |

Përveç enigmave fikse, `generate(level, seed)` krijon enigma të reja me **zgjidhje unike**: gjeneron një grid të plotë të rastësishëm dhe heq qeliza derisa të arrihet numri i synuar i clues (36 / 30 / 25), duke verifikuar unicitetin pas çdo heqjeje.

## 2.8 Rezultatet

| Enigma | Clues | Ordering | Nyje të zgjeruara | Frontier max | Koha (s) |
|--------|------:|----------|------------------:|-------------:|---------:|
| easy #1 | 30 | fixed | 4 632 | 738 | 0.006 |
| easy #1 | 30 | mrv | 52 | 1 | 0.000 |
| easy #2 | 32 | fixed | 929 | 146 | 0.001 |
| easy #2 | 32 | mrv | 50 | 1 | 0.001 |
| easy #3 | 36 | fixed | 69 | 5 | 0.000 |
| easy #3 | 36 | mrv | 46 | 1 | 0.000 |
| medium #1 | 30 | fixed | 2 170 | 235 | 0.003 |
| medium #1 | 30 | mrv | 96 | 3 | 0.001 |
| medium #2 | 30 | fixed | 4 299 | 728 | 0.006 |
| medium #2 | 30 | mrv | 215 | 11 | 0.002 |
| medium #3 | 28 | fixed | 22 919 | 3 616 | 0.030 |
| medium #3 | 28 | mrv | 206 | 9 | 0.002 |
| hard #1 | 17 | fixed | – | > 2 000 000 | memoria (stop) |
| hard #1 | 17 | mrv | 8 070 | 438 | 0.125 |
| hard #2 | 17 | fixed | – | > 2 000 000 | memoria (stop) |
| hard #2 | 17 | mrv | 3 723 | 150 | 0.058 |
| hard #3 | 17 | fixed | – | > 2 000 000 | memoria (stop) |
| hard #3 | 17 | mrv | 93 952 | 5 441 | 1.313 |

**Përfundimi**: BFS e pastër (`fixed`) i zgjidh menjëherë nivelet Easy dhe Medium, por te Hard frontier-i rritet eksponencialisht (milionë gjendje në memorie) – kjo është dobësia klasike e BFS. Me renditjen MRV të gjitha nivelet zgjidhen nën 2 sekonda. Te Easy, MRV gjithmonë gjen qeliza me 1 kandidat, prandaj frontier-i mbetet 1 (asnjë degëzim).

## 2.9 Ekzekutimi

```bash
python main.py sudoku --level easy
python main.py sudoku --level hard --every            # të 3 enigmat Hard
python main.py sudoku --level all                     # të 9 enigmat
python main.py sudoku --level medium --ordering fixed # BFS e pastër
python main.py sudoku --generate hard --seed 7        # enigmë e re
python main.py sudoku --puzzle "530070000600195000..." # enigma juaj
```
