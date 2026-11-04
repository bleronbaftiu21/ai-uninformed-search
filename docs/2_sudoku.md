# 2. Sudoku Solver — BFS + Backtracking

> Kodi: [`2_sudoku.py`](../2_sudoku.py)

## 2.1 Përshkrimi

Programi zgjidh një Sudoku 9 × 9: çdo rresht, kolonë dhe kuti 3 × 3 duhet t'i përmbajë numrat 1–9 saktësisht një herë. Programi i parasheh tri nivele: **Easy, Medium, Hard**, me nga 3 enigma secili.

## 2.2 Modelimi

| Elementi | Përkufizimi |
|---|---|
| **Gjendja** | Grid 9 × 9 i plotësuar pjesërisht, i ruajtur si string me 81 karaktere (`'0'` = bosh) |
| **Gjendja fillestare** | Enigma e dhënë |
| **Veprimi** | Vendos një vlerë të lejuar në një qelizë bosh |
| **Goal test** | Nuk ka më qeliza bosh (`"0" not in s`) |
| **Kostoja** | 1 për veprim; të gjitha zgjidhjet janë në thellësinë `k` = numri i qelizave bosh |

## 2.3 Reprezentimi

**Variablat:** qelizat bosh `X[r][c]` (51 te Easy #1, 64 te Hard).

**Domain-i:** `D = {1, ..., 9}`. Gjatë kërkimit, domain-i efektiv i një qelize është:

```
D(r,c) = {1..9} \ { vlerat në rreshtin r, kolonën c dhe kutinë e (r,c) }
```

Këtë e llogarit funksioni `kandidatet(s, i)`.

**Kufizimet:** 27 kufizime AllDifferent: 9 rreshta + 9 kolona + 9 kuti.

**Në kod:** `PEERS[i]` = 20 qelizat që janë në të njëjtin rresht, kolonë ose kuti me qelizën `i`. Llogaritet një herë në fillim, kështu kontrolli i kufizimeve bëhet shpejt.

## 2.4 Objective function

Problem **minimizimi**:

```
f(X) = (numri i çifteve me vlerë të njëjtë në rresht/kolonë/kuti) + (numri i qelizave bosh)
```

- Enigma Easy #1 në fillim: `f = 0 konflikte + 51 bosh = 51`
- **`f(X) = 0` ⇔ Sudoku është zgjidhur saktë**
- Çdo veprim i vlefshëm e ul `f` saktësisht për 1, prandaj thellësia e zgjidhjes = `f` i fillimit.

## 2.5 Landscape

| Masa | Vlera |
|---|---|
| Grid pa asnjë kufizim `9^81` | ≈ 10^77 |
| Easy #1, 51 qeliza bosh, `9^51` | ≈ 10^48 |
| Hard, 64 qeliza bosh, `9^64` | ≈ 10^61 |
| Numri i Sudoku-ve të plota të vlefshme | ≈ 6.67 × 10^21 |
| Zgjidhje për çdo enigmë të mirëformuar | 1 |

Hapësira është e pamundur të eksplorohet plotësisht. Falë pruning-ut, BFS i viziton vetëm gjendjet që respektojnë kufizimet: për Easy #1, **52 nyje nga 10^48**.

## 2.6 Algoritmi: BFS + Backtracking

```
BFS(fillimi):
    radha ← [fillimi]                         # FIFO
    while radha jo bosh:
        s ← radha.popleft()                   # i pari që hyn, i pari që del
        if s s'ka qeliza bosh: return s       # GOAL
        i ← qeliza me më pak kandidatë        # MRV
        for v in kandidatet(s, i):            # vetëm vlerat e lejuara (prune)
            radha.append(s me s[i] = v)
        # nëse s'ka kandidatë: asgjë s'shtohet, dega braktiset (BACKTRACK)
    return FAIL
```

**BFS** e eksploron pemën **nivel pas niveli**: radha FIFO (`deque`, `popleft()`) garanton që të gjitha gjendjet me `k` qeliza të mbushura zgjerohen para atyre me `k + 1`.

**Backtracking te BFS:** BFS nuk kthehet prapa me rekursion si DFS. Backtracking-u këtu ka dy pjesë:
1. **Pruning**: gjenerohen vetëm fëmijët me vlera të lejuara.
2. **Braktisja e degëve pa dalje**: nëse një qelizë nuk ka asnjë kandidat, gjendja nuk gjeneron fëmijë dhe zhduket nga radha. Kërkimi vazhdon me alternativat e tjera që janë ende në radhë.

**MRV (Minimum Remaining Values):** zgjedh qelizën me më pak kandidatë. **Nuk e ndryshon BFS-në**: radha mbetet FIFO dhe kërkimi mbetet i painformuar ndaj qëllimit. MRV vetëm zgjedh cilën variabël ta degëzojë. Pa të, enigmat Hard nuk zgjidhen, sepse radha rritet në miliona gjendje (më shumë se 2 000 000 në memorie). Te Easy, MRV gjen gjithmonë qeliza me 1 kandidat, prandaj radha mbetet me 1 element.

**Vetitë e BFS:** complete, optimal (të gjitha zgjidhjet janë në të njëjtën thellësi), por **memoria `O(b^d)`**: kjo është dobësia kryesore e BFS.

## 2.7 Rezultatet

| Enigma | Qeliza bosh | Nyje të vizituara | Frontier max |
|---|---:|---:|---:|
| Easy #1 | 51 | 52 | 1 |
| Easy #2 | 49 | 50 | 1 |
| Easy #3 | 45 | 46 | 1 |
| Medium #1 | 51 | 96 | 3 |
| Medium #2 | 51 | 215 | 11 |
| Medium #3 | 53 | 206 | 9 |
| Hard #1 | 64 | 8 070 | 438 |
| Hard #2 | 64 | 3 723 | 150 |
| Hard #3 | 64 | 17 438 | 908 |

Të 9 enigmat zgjidhen me `f = 0`, gjithsej për rreth 2–3 sekonda.

**Si e tregojnë numrat nivelin:**
- **Easy**: nyje = qeliza bosh + 1, pra asnjë degëzim. Çdo hap ka vetëm një mundësi.
- **Medium**: pak degëzim (frontier max 3–11).
- **Hard**: vetëm 17 të dhëna, prandaj degëzim i madh (mijëra nyje, frontier deri në 908).

**Frontier max** tregon sa gjendje mban BFS njëkohësisht në memorie, dhe kjo rritet shpejt te enigmat e vështira.

## 2.8 Pyetje të mundshme

**Pse BFS dhe jo DFS?** Detyra kërkon BFS. Te Sudoku zgjidhja është gjithmonë në të njëjtën thellësi, prandaj DFS do të ishte më efikas në memorie. BFS e tregon qartë koston e kërkimit nivel pas niveli.

**A është MRV heuristikë, e kështu kërkim i informuar?** MRV është heuristikë për **renditjen e variablave**, jo heuristikë `h(n)` që vlerëson distancën deri te qëllimi. Radha mbetet FIFO, kështu që algoritmi mbetet BFS. Kërkim i informuar do të ishte nëse radha renditej sipas `h(n)`, si te Greedy ose A*.

**Ku është backtracking-u në kod?** Kur `vlerat` është listë bosh, cikli `for d in vlerat` nuk shton asgjë në radhë, dhe dega braktiset.

**Çka ndodh me memorien?** Çdo gjendje në radhë është string me 81 karaktere. Te Hard #3 radha arrin 908 gjendje njëkohësisht, ndërsa pa MRV do të arrinte miliona.
