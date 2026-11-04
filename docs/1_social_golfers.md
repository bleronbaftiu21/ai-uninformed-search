# 1. Social Golfers Problem — DFS + Backtracking

> Kodi: [`1_social_golfers.py`](../1_social_golfers.py)

## 1.1 Përshkrimi

32 lojtarë luajnë golf një herë në javë, gjithmonë në grupe me nga 4. Për sa javë mund të luajnë ashtu që **dy lojtarë të mos luajnë së bashku në të njëjtin grup më shumë se një herë**?

Forma e përgjithshme: a mund të planifikohen `n = g × p` lojtarë në `g` grupe me `p` lojtarë për `w` javë? Instanca jonë: **g = 8, p = 4, n = 32**.

## 1.2 Modelimi

| Elementi | Përkufizimi |
|---|---|
| **Gjendja** | Orar i plotësuar pjesërisht (disa vende kanë lojtarë, të tjerat janë bosh) |
| **Gjendja fillestare** | Orar krejtësisht bosh |
| **Veprimi** | Vendos një lojtar në vendin e radhës bosh (renditja: java → grupi → vendi) |
| **Goal test** | Të gjitha `w × 8 × 4` vendet janë mbushur pa shkelur asnjë kufizim |
| **Kostoja** | Çdo veprim kushton 1; na intereson vetëm gjetja e një zgjidhjeje |

## 1.3 Reprezentimi

**Variablat:** `X[w][g][s]` = lojtari në javën `w`, grupin `g`, vendin `s`, ku `w ∈ {0..W−1}`, `g ∈ {0..7}`, `s ∈ {0..3}`. Për `W` javë kemi `32·W` variabla (160 për 5 javë).

**Domain-i:** `D = {0, 1, ..., 31}`, numri i lojtarit.

**Kufizimet:**

| | Kufizimi | Në kod |
|---|---|---|
| C1 | Çdo lojtar luan saktësisht një herë në javë | `v in luan` |
| C2 | Çdo çift lojtarësh takohet më së shumti një herë në gjithë orarin | `takuar[v] & set(grp)` |

**Strukturat në kod:**
- `orari[java][grupi]`: lista e lojtarëve në atë grup
- `takuar[a]`: bashkësia e lojtarëve me të cilët `a` ka qenë tashmë në grup
- `luan`: lojtarët që janë caktuar tashmë në javën aktuale

**Symmetry breaking** (shmang provimin e orareve që janë të njëjta me renditje tjetër):
- Brenda grupit lojtarët janë në rend rritës: `{0,4,8,12}` dhe `{12,8,4,0}` janë i njëjti grup.
- Lojtari i parë i grupit është më i vogli i lirë: grupet e një jave nuk provohen në renditje të ndryshme.

Kjo nuk e humb asnjë zgjidhje, sepse çdo orar mund të rishkruhet në këtë formë.

## 1.4 Objective function

Problem **minimizimi**:

```
f(S) = Σ  max(0, m(a,b) − 1)      për çdo çift lojtarësh a < b
```

ku `m(a,b)` = sa herë lojtarët `a` dhe `b` kanë qenë në të njëjtin grup.

- Takim 1 herë → `max(0, 0) = 0`, në rregull.
- Takim 3 herë → `max(0, 2) = 2`, dy takime të tepërta.
- **`f(S) = 0` ⇔ orari është i vlefshëm.**

Qëllimi i jashtëm i problemit: **maksimizo `w`** ashtu që ekziston orar me `f(S) = 0`.

> **Objective function ≠ heuristikë.** Objective function vlerëson sa e mirë është një zgjidhje. Heuristika `h(n)` vlerëson sa larg është qëllimi nga një gjendje e pjesshme, dhe përdoret vetëm te kërkimi **i informuar** (A*, Greedy). DFS është kërkim **i painformuar**, prandaj nuk përdor heuristikë.

## 1.5 Landscape

Landscape-i është madhësia e hapësirës së kërkimit, pra sa orare të mundshme ekzistojnë.

| Modeli | Formula | w = 5 |
|---|---|---|
| Pa kufizime: çdo variabël 0..31 | `32^(32·w)` | ≈ 10^240 |
| Me C1: çdo javë është permutacion i 32 lojtarëve | `(32!)^w` | ≈ 10^177 |
| Çdo javë është ndarje në grupe | `P^w` | ≈ 10^98 |

Numri i ndarjeve të 32 lojtarëve në 8 grupe me 4:

```
P = 32! / ( (4!)^8 · 8! ) = 59 287 247 761 257 140 625 ≈ 5.93 × 10^19
```

- `32!`: të gjitha renditjet e lojtarëve
- `(4!)^8`: në secilin nga 8 grupet, 4 lojtarët mund të renditen në 4! = 24 mënyra, por janë i njëjti grup
- `8!`: 8 grupet mund të ndërrohen me njëri-tjetrin, por java mbetet e njëjtë

**Kufiri i sipërm i javëve:** çdo javë lojtari takon `p − 1 = 3` lojtarë të rinj, dhe ka gjithsej `n − 1 = 31` të tjerë:

```
w ≤ ⌊(n − 1) / (p − 1)⌋ = ⌊31 / 3⌋ = 10
```

Kontroll tjetër: ka `C(32,2) = 496` çifte gjithsej, dhe çdo javë "harxhon" `8 · C(4,2) = 48` çifte, prandaj `w ≤ 496 / 48 ≈ 10.3`.

## 1.6 Algoritmi: DFS + Backtracking

```
DFS(pos):
    if pos == W·32: return TRUE                 # GOAL: të gjitha vendet u mbushën
    (java, grupi) ← pozita pos
    for v in kandidatët:                        # symmetry breaking
        if v luan këtë javë:          prune     # C1
        if v është takuar me grupin:  prune     # C2
        vendos v
        if DFS(pos + 1): return TRUE            # shko më thellë
        hiq v                                   # BACKTRACK
    return FALSE                                # asnjë kandidat s'funksionoi
```

- **DFS**: gjithmonë shkon te vendi i radhës (më thellë) para se të provojë alternativa.
- **Pruning**: kandidati që shkel C1 ose C2 nuk provohet fare, dhe e gjithë dega e tij prehet.
- **Backtracking**: kur një vend nuk ka asnjë kandidat të vlefshëm, funksioni kthen `False`, dhe niveli i mëparshëm e heq vendosjen e fundit dhe provon kandidatin tjetër.

**Vetitë:** koha `O(b^d)` në rastin më të keq (`b ≤ 32`, `d = 32·w`), memoria `O(d)`, sepse ruhet vetëm rruga aktuale.

### Shembull i vogël: 6 lojtarë, 3 grupe me 2

Java 1 = `{0,1} {2,3} {4,5}`. Plotësimi i javës 2:

```
Grupi 1:  0, pastaj 1 ✗ C2 (u takuan), 2 ✓          → {0,2}
Grupi 2:  1, pastaj 2 ✗ C1 (luan),     3 ✓          → {1,3}
Grupi 3:  4, pastaj 5 ✗ C2 (u takuan)  → s'ka kandidat
          BACKTRACK: hiq 4, hiq 3
Grupi 2:  1, pastaj 4 ✓                              → {1,4}
Grupi 3:  3, 5 ✓                                     → {3,5}
Java 2 = {0,2} {1,4} {3,5}
```

Kur ngec te grupi 3, algoritmi nuk fillon nga e para, por kthehet vetëm një nivel (te grupi 2) dhe provon lojtarin tjetër.

Për ta provuar: ndrysho `G, P = 8, 4` në `G, P = 3, 2` dhe ekzekuto `python 1_social_golfers.py 5`.

## 1.7 Rezultatet

| Javë | Rezultati | Nyje të vizituara | Degë të prera |
|---:|---|---:|---:|
| 1 | ✅ u gjet | 33 | 0 |
| 2 | ✅ u gjet | 65 | 72 |
| 3 | ✅ u gjet | 97 | 144 |
| 4 | ✅ u gjet | 129 | 216 |
| 5 | ✅ u gjet | 161 | 288 |
| 6 | ⏱️ nuk përfundon brenda minutave | – | – |

Orari për 5 javë (`f(S) = 0`):

```
Java 1: {0,1,2,3}   {4,5,6,7}    {8,9,10,11}  {12,13,14,15} {16,17,18,19} {20,21,22,23} {24,25,26,27} {28,29,30,31}
Java 2: {0,4,8,12}  {1,5,9,13}   {2,6,10,14}  {3,7,11,15}   {16,20,24,28} {17,21,25,29} {18,22,26,30} {19,23,27,31}
Java 3: {0,5,10,15} {1,4,11,14}  {2,7,8,13}   {3,6,9,12}    {16,21,26,31} {17,20,27,30} {18,23,24,29} {19,22,25,28}
Java 4: {0,6,11,13} {1,7,10,12}  {2,4,9,15}   {3,5,8,14}    {16,22,27,29} {17,23,26,28} {18,20,25,31} {19,21,24,30}
Java 5: {0,7,9,14}  {1,6,8,15}   {2,5,11,12}  {3,4,10,13}   {16,23,25,30} {17,22,24,31} {18,21,27,28} {19,20,26,29}
```

> Java 1 ndryshon nga shembulli në detyrë (`{0,1,2,3} {4,5,22,23} ...`). Të dyja janë të sakta: në javën 1 askush nuk është takuar ende, prandaj çdo ndarje është e vlefshme. DFS provon gjithmonë lojtarin më të vogël të parin.

## 1.8 Përgjigjja e pyetjes "për sa javë?"

- **Teorikisht: 10 javë** (kufiri i sipërm). Në literaturë është vërtetuar që 10 javë janë të arritshme. Zgjidhja e parë eksplicite u ndërtua në 2004.
- **DFS gjen 5 javë menjëherë, por ngec te java 6.**

**Pse ngec?** Në 5 javët që gjen DFS, lojtarët 0–15 luajnë gjithmonë vetëm mes vete. Pas 5 javësh, secili prej tyre i ka takuar të 15 të tjerët e kësaj grupe. Në javën 6, këta 16 lojtarë duhet të jenë të gjithë në grupe të ndryshme, por ka vetëm 8 grupe, prandaj **java 6 është e pamundur** me këto 5 javë.

Gabimi ndodh që në **javën 2**, por DFS e zbulon vetëm në **javën 6**. Para se të kthehet deri te java 2, duhet t'i provojë të gjitha kombinimet e javëve 3, 4 dhe 5, që janë miliona. Ky fenomen quhet **thrashing** dhe është kufizimi kryesor i backtracking-ut kronologjik. Për 6–10 javë nevojiten teknika më të fuqishme (constraint propagation, local search, konstruksione matematikore), që janë jashtë kërkimit të painformuar.

