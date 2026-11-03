# 1. Social Golfers Problem — DFS + Backtracking

> Kodi: [`ai_search/social_golfers/solver.py`](../ai_search/social_golfers/solver.py)

## 1.1 Përshkrimi

32 lojtarë luajnë golf një herë në javë, gjithmonë në grupe me nga 4. Sa javë mund të luajnë ashtu që **asnjë çift lojtarësh të mos jetë bashkë në të njëjtin grup më shumë se një herë**?

Forma e përgjithshme: a mund të planifikohen `n = g × p` lojtarë në `g` grupe me `p` lojtarë për `w` javë, pa u takuar dy lojtarë më shumë se një herë? Instanca jonë: **g = 8, p = 4, n = 32**.

## 1.2 Modelimi

| Elementi | Përkufizimi |
|---|---|
| **Gjendja** | Orar i pjesshëm: disa vende `X[w][g][s]` janë caktuar, të tjerat bosh |
| **Gjendja fillestare** | Orar bosh (ose java 1 e fiksuar, shih symmetry breaking) |
| **Veprimi** | Cakto një lojtar në vendin e radhës (java → grupi → vendi) |
| **Goal test** | Të gjitha `w × g × p` vendet janë mbushur dhe asnjë kufizim nuk shkelet |
| **Kostoja** | Uniforme (çdo veprim kushton 1); na intereson vetëm gjetja e zgjidhjes |

## 1.3 Reprezentimi

**Variablat**

```
X[w][g][s]   w ∈ {0..W-1}, g ∈ {0..7}, s ∈ {0..3}
```

`X[w][g][s]` = lojtari që luan në javën `w`, në grupin `g`, në vendin `s`. Për `W` javë kemi `32·W` variabla (p.sh. 160 për 5 javë, 320 për 10).

**Domain-i**: `D = {0, 1, ..., 31}`.

**Kufizimet**

| | Kufizimi | Formalisht |
|---|---|---|
| C1 | Çdo javë është ndarje: çdo lojtar luan saktësisht një herë | `AllDifferent(X[w][*][*])` për çdo `w` |
| C2 | Dy lojtarë takohen më së shumti një herë | `Σ_w [a dhe b janë në të njëjtin grup në javën w] ≤ 1`, për çdo `a < b` |

**Symmetry breaking** (zvogëlon hapësirën pa humbur zgjidhje deri në simetri):

| | Rregulli | Pse është valid |
|---|---|---|
| S1 | Brenda grupit lojtarët janë në rend rritës | Grupi është bashkësi, renditja nuk ka rëndësi |
| S2 | Lojtari i parë i grupit është lojtari më i vogël i pacaktuar i javës | Grupet brenda javës mund të renditen sipas minimumit |
| S3 | Java 1 fiksohet: `{0,1,2,3} {4,5,6,7} ... {28,29,30,31}` | Lojtarët mund të riemërtohen |
| S4 | Javët renditen sipas partnerit të dytë të lojtarit 0 | Javët mund të ndërrohen me njëra-tjetrën |

Reprezentimi në kod përdor **bitmask-a** (`week_used[w]`, `met[a]`) që kontrolli i C1 dhe C2 të bëhet në O(1).

## 1.4 Objective function

Formulohet si problem **minimizimi** i takimeve të tepërta:

```
f(S) = Σ_{a<b} max(0, m(a,b) − 1)
```

ku `m(a,b)` = sa herë lojtarët `a` dhe `b` kanë qenë në të njëjtin grup.

* `f(S) = 0` ⇔ orari është i vlefshëm (asnjë çift i përsëritur).
* Qëllimi i jashtëm: **maksimizo `w`** ashtu që ekziston orar me `f(S) = 0`.

**Kufiri i sipërm** për numrin e javëve: çdo javë lojtari takon `p − 1 = 3` lojtarë të rinj, dhe gjithsej ka `n − 1 = 31` të tjerë, prandaj

```
w ≤ ⌊(n − 1) / (p − 1)⌋ = ⌊31 / 3⌋ = 10
```

Kontroll tjetër: `C(32,2) = 496` çifte gjithsej; çdo javë "konsumon" `8 · C(4,2) = 48` çifte → `w ≤ 496/48 = 10.3`. Literatura konfirmon që 10 javë janë të arritshme (zgjidhja e parë eksplicite u ndërtua nga A. Aguado në 2004).

## 1.5 Landscape (madhësia e hapësirës së kërkimit)

| Modeli | Formula | w = 5 | w = 10 |
|---|---|---:|---:|
| Pa kufizime (çdo variabël 0..31) | `n^(n·w)` | ≈ 6.66 × 10^240 | ≈ 4.44 × 10^481 |
| Çdo javë një permutacion (C1) | `(n!)^w` | ≈ 1.26 × 10^177 | ≈ 1.59 × 10^354 |
| Çdo javë një ndarje (C1 + S1 + S2) | `P^w` | ≈ 7.32 × 10^98 | ≈ 5.36 × 10^197 |
| + Java 1 e fiksuar (S3) | `P^(w−1)` | ≈ 1.23 × 10^79 | ≈ 9.05 × 10^177 |

ku numri i ndarjeve të 32 lojtarëve në 8 grupe me 4 është

```
P = 32! / ((4!)^8 · 8!) = 59 287 247 761 257 140 625 ≈ 5.93 × 10^19
```

Symmetry breaking e zvogëlon hapësirën me qindra rende madhësie, por ajo mbetet astronomike, prandaj **backtracking-u** (prerja e degëve që shkelin C2 menjëherë) është thelbësor.

## 1.6 Algoritmi: DFS + Backtracking

```
DFS(pos):
    if pos == W·G·P: return SUCCESS                     # goal test
    (w, g, s) ← pozita e radhës
    for v in kandidatët(w, g, s):                       # S1, S2, S4
        if v luan tashmë në javën w:        prune       # C1
        if v është takuar me dikë nga grupi: prune      # C2
        if forward_check dështon:           prune       # mbeten pak lojtarë
        apliko(v)
        if grupi u mbyll dhe java s'është më e realizueshme: prune
        elif DFS(pos + 1): return SUCCESS
        zhbëj(v)                                        # BACKTRACK
    return FAIL
```

Përveç C1 dhe C2, përdoren tri kontrolle të hershme (*look-ahead*) që e bëjnë backtracking-un më efikas pa e ndryshuar natyrën e painformuar të kërkimit:

1. **Forward check** – pasi vendoset `v`, a mbeten mjaft lojtarë të lirë që nuk e kanë takuar askënd nga grupi për t'i mbushur vendet e mbetura?
2. **Fizibiliteti i javës** – pasi mbyllet një grup, a ka çdo lojtar i mbetur i javës ende ≥ 3 partnerë të mundshëm?
3. **Klika** – pasi mbyllet java, nëse ekzistojnë > 8 lojtarë që janë takuar të gjithë me njëri-tjetrin, java e ardhshme është e pamundur (secili do duhej në grup tjetër, por ka vetëm 8 grupe).

Opsionalisht (`seed=k`) vlerat provohen në renditje të rastësishme → **randomized DFS me restarts** (`search_max_weeks`).

## 1.7 Rezultatet

| Javë | Rezultati | Nyje të zgjeruara | Koha (s) |
|-----:|-----------|------------------:|---------:|
| 1 | u gjet | 1 | 0.000 |
| 2 | u gjet | 33 | 0.000 |
| 3 | u gjet | 65 | 0.000 |
| 4 | u gjet | 97 | 0.000 |
| 5 | u gjet | 129 | 0.000 |
| 6 | timeout (30 s) | 6 176 768 | 30.0 |

**DFS + restarts**: gjen **6 javë** brenda pak sekondave (p.sh. seed = 2, 1 865 nyje).

### Pse DFS klasik ngec në javën 6?

Orari i 5 javëve që gjen DFS (renditje leksikografike):

```
Java 1: { 0, 1, 2, 3}  { 4, 5, 6, 7}  { 8, 9,10,11}  {12,13,14,15}  {16,17,18,19} ...
Java 2: { 0, 4, 8,12}  { 1, 5, 9,13}  { 2, 6,10,14}  { 3, 7,11,15}  {16,20,24,28} ...
Java 3: { 0, 5,10,15}  { 1, 4,11,14}  { 2, 7, 8,13}  { 3, 6, 9,12}  {16,21,26,31} ...
...
```

Lojtarët 0–15 luajnë gjithmonë vetëm me njëri-tjetrin. Pas 5 javësh secili prej tyre i ka takuar të 15 të tjerët e grupit 0–15 → formohet një **klikë me 16 lojtarë**. Në javën 6 secili prej këtyre 16 duhet të jetë në grup të ndryshëm, por ka vetëm 8 grupe → **e pamundur**.

Gabimi u bë që në **javën 2**, por DFS e zbulon vetëm në javën 6. Që të kthehet deri te java 2, DFS duhet të provojë të gjitha kombinimet e javëve 3, 4, 5 – miliona nyje. Ky fenomen quhet **thrashing** dhe është kufizimi kryesor i backtracking-ut kronologjik. Restarts me renditje të rastësishme e shmangin pjesërisht këtë strukturë "të mbyllur".

Për 7–10 javë nevojiten teknika më të avancuara (constraint propagation më e fortë, local search, konstruksione matematikore) – këto janë jashtë fushës së kërkimit të painformuar.

### Instanca të vogla (verifikim)

| Instanca | Rezultati |
|---|---|
| 9 lojtarë, 3 × 3, 4 javë (Kirkman) | u gjet |
| 9 lojtarë, 3 × 3, 5 javë | DFS **vërteton** që nuk ka zgjidhje (kërkim i plotë) |

## 1.8 Ekzekutimi

```bash
python main.py golfers --weeks 5                       # 5 javë, DFS klasik
python main.py golfers --weeks 6 --time-limit 30       # tregon kufirin e DFS
python main.py golfers --max-weeks --restarts 10       # DFS + restarts
python main.py golfers --groups 3 --size 3 --weeks 4   # instanca Kirkman
```
