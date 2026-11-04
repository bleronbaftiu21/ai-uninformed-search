# Teknikat e Painformuara të Kërkimit (Uninformed Search)

**Detyra e parë semestrale – Inteligjenca Artificiale**

| # | Problemi | Algoritmi | Kodi | Dokumentimi |
|---|---|---|---|---|
| 1 | Social Golfers (32 lojtarë, 8 grupe × 4) | DFS + Backtracking | [`1_social_golfers.py`](1_social_golfers.py) | [docs/1_social_golfers.md](docs/1_social_golfers.md) |
| 2 | Sudoku Solver (Easy, Medium, Hard) | BFS + Backtracking | [`2_sudoku.py`](2_sudoku.py) | [docs/2_sudoku.md](docs/2_sudoku.md) |
| 3 | Latin Square (n × n) | IDDFS + Backtracking | [`3_latin_square.py`](3_latin_square.py) | [docs/3_latin_square.md](docs/3_latin_square.md) |
| 4 | Search Trees: 8-Puzzle, Missionaries & Cannibals, Rotating Workforce | BFS / DFS | [`4_search_trees.py`](4_search_trees.py) | [docs/4_search_trees.md](docs/4_search_trees.md) |

Për problemet 1–3, çdo dokument i mbulon kërkesat e detyrës me radhë: **modelimi**, **reprezentimi** (variablat, domain-i, kufizimet), **objective function**, **landscape** dhe **algoritmi**, plus rezultatet dhe pyetjet e mundshme.

## Ekzekutimi

Kërkohet Python 3.8+, pa paketa shtesë.

```bash
python 1_social_golfers.py        # 5 javë (ose: python 1_social_golfers.py 3)
python 2_sudoku.py                # të 9 enigmat (ose: python 2_sudoku.py hard)
python 3_latin_square.py          # kërkon n, p.sh. 5
python 4_search_trees.py          # printon të tri pemët
```

## Rezultatet në një vështrim

| Problemi | Rezultati |
|---|---|
| **Social Golfers** | Orar për 5 javë me `f(S) = 0` (161 nyje). Kufiri teorik është 10 javë; DFS ngec te java 6 për shkak të thrashing-ut (shpjeguar në dokumentim). |
| **Sudoku** | Të 9 enigmat zgjidhen me `f = 0`: Easy 46–52 nyje, Medium 96–215, Hard 3 723–17 438. |
| **Latin Square** | `n ≤ 6` zgjidhet nën 2 s; n = 5 me 4 914 nyje në 17 iteracione IDDFS. |
| **Search Trees** | 8-Puzzle: R → D → R (3 lëvizje). M&C: 11 kalime. RWS: orar 3-javor që respekton të gjitha kufizimet. |

## Search Tree: shembull

Pema e kërkimit për **8-Puzzle** (BFS, thellësia 3). Rruga blu është zgjidhja **R → D → R**. Të tri pemët (8-Puzzle, Missionaries & Cannibals, Rotating Workforce) janë te [docs/4_search_trees.md](docs/4_search_trees.md).

```mermaid
flowchart TD
    n0["1 2 3<br/>_ 4 6<br/>7 5 8"]
    n1["_ 2 3<br/>1 4 6<br/>7 5 8"]
    n2["1 2 3<br/>7 4 6<br/>_ 5 8"]
    n3["1 2 3<br/>4 _ 6<br/>7 5 8"]
    n4["2 _ 3<br/>1 4 6<br/>7 5 8"]
    n5["1 2 3<br/>7 4 6<br/>5 _ 8"]
    n6["1 _ 3<br/>4 2 6<br/>7 5 8"]
    n7["1 2 3<br/>4 5 6<br/>7 _ 8"]
    n8["1 2 3<br/>4 6 _<br/>7 5 8"]
    n9["2 4 3<br/>1 _ 6<br/>7 5 8"]
    n10["2 3 _<br/>1 4 6<br/>7 5 8"]
    n11["1 2 3<br/>7 _ 6<br/>5 4 8"]
    n12["1 2 3<br/>7 4 6<br/>5 8 _"]
    n13["_ 1 3<br/>4 2 6<br/>7 5 8"]
    n14["1 3 _<br/>4 2 6<br/>7 5 8"]
    n15["1 2 3<br/>4 5 6<br/>_ 7 8"]
    n16["1 2 3<br/>4 5 6<br/>7 8 _<br/>GOAL"]
    n17["1 2 _<br/>4 6 3<br/>7 5 8"]
    n18["1 2 3<br/>4 6 8<br/>7 5 _"]
    n0 -->|U| n1
    n0 -->|D| n2
    n0 ==>|R| n3
    n1 -->|R| n4
    n2 -->|R| n5
    n3 -->|U| n6
    n3 ==>|D| n7
    n3 -->|R| n8
    n4 -->|D| n9
    n4 -->|R| n10
    n5 -->|U| n11
    n5 -->|R| n12
    n6 -->|L| n13
    n6 -->|R| n14
    n7 -->|L| n15
    n7 ==>|R| n16
    n8 -->|U| n17
    n8 -->|D| n18
    classDef goal fill:#c8f0c8,stroke:#1e7b1e,stroke-width:3px,color:#000
    classDef path fill:#dcebff,stroke:#1f5fbf,stroke-width:3px,color:#000
    class n16 goal
    class n0,n3,n7 path
```

## Krahasimi i algoritmeve

| Algoritmi | Memoria | Complete | Optimal | Ku duket dobësia |
|---|---|---|---|---|
| **DFS** | `O(d)` | po (në hapësirë të fundme) | jo | Thrashing: gabimet e hershme zbulohen vonë (Social Golfers, java 6) |
| **BFS** | `O(b^d)` | po | po (kosto uniforme) | Radha rritet shpejt (Sudoku Hard: frontier deri në 908 gjendje) |
| **IDDFS** | `O(d)` | po | po (kosto uniforme) | Rivizitimi i niveleve të sipërme (Latin Square: 4 885 nga 4 914 nyje në iteracionet pa zgjidhje) |

Në të gjitha problemet, **backtracking-u** (gjenerohen vetëm gjendjet që respektojnë kufizimet) është arsyeja që hapësira të mëdha, nga 10^42 deri në 10^240, eksplorohen me vetëm disa qindra ose mijëra nyje.
