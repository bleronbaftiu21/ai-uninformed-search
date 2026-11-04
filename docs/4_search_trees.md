# 4. Search Trees

> Kodi: [`4_search_trees.py`](../4_search_trees.py)

Një **search tree** tregon si kërkimi i eksploron gjendjet:
- **rrënja** = gjendja fillestare
- **çdo degë** = një veprim (shënohet si `--veprimi-->`)
- **çdo nyje-fëmijë** = gjendja që del pas atij veprimi

Legjenda e diagrameve:

| Ngjyra | Kuptimi | Në daljen e programit |
|---|---|---|
| 🟩 jeshile | Gjendja qëllim | `[GOAL]` |
| 🟦 blu, me shigjeta të trasha | Rruga nga rrënja te qëllimi | – |
| ⬜ gri | Gjendje e parë më herët, nuk zgjerohet më | `[përsëritur]` |
| 🟥 e kuqe, me ✗ | Gjendje që shkel kufizimet, prerë nga backtracking-u | `[X]` |
| 🟪 vjollcë | Gjendje e zakonshme e zgjeruar ose e gjeneruar | – |

Diagramet janë në formatin **Mermaid**, të cilin GitHub e vizaton automatikisht. Nën secilin diagram është edhe pema si tekst, ashtu siç e printon `python 4_search_trees.py`.

Funksioni `printo()` e vizaton pemën rekursivisht: për çdo nyje printon etiketën dhe pastaj fëmijët e saj me `├──` dhe `└──`.

---

## 4.1 8-Puzzle

| Elementi | Përkufizimi |
|---|---|
| **Gjendja** | String me 9 karaktere, rresht pas rreshti; `0` = vendi bosh |
| **Fillimi** | `123046758`, pra `1 2 3 / _ 4 6 / 7 5 8` |
| **Qëllimi** | `123456780`, pra `1 2 3 / 4 5 6 / 7 8 _` |
| **Veprimet** | Lëviz vendin bosh: **U** (lart), **D** (poshtë), **L** (majtas), **R** (djathtas) |
| **Kostoja** | 1 për lëvizje |
| **Landscape** | `9! / 2 = 181 440` gjendje të arritshme; faktori i degëzimit 2–4 |

Pema ndërtohet me **BFS deri në thellësinë 3**. Lëvizja që e zhbën lëvizjen e mëparshme (p.sh. `D` pas `U`) nuk gjenerohet, që pema të mos ketë gjendje të kota.

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

<details>
<summary>Pema si tekst (dalja e programit)</summary>

```
123046758
├── --U--> 023146758
│   └── --R--> 203146758
│       ├── --D--> 243106758
│       └── --R--> 230146758
├── --D--> 123746058
│   └── --R--> 123746508
│       ├── --U--> 123706548
│       └── --R--> 123746580
└── --R--> 123406758
    ├── --U--> 103426758
    │   ├── --L--> 013426758
    │   └── --R--> 130426758
    ├── --D--> 123456708
    │   ├── --L--> 123456078
    │   └── --R--> 123456780 [GOAL]
    └── --R--> 123460758
        ├── --U--> 120463758
        └── --D--> 123468750
```

</details>

**Zgjidhja optimale:** R → D → R (3 lëvizje).

---

## 4.2 Missionaries and Cannibals

| Elementi | Përkufizimi |
|---|---|
| **Gjendja** | `(M, C, B)`: misionarë dhe kanibalë në bregun e majtë; `B = 1` kur varka është majtas. Në diagram: `MMMC \| CC ⛵` = bregu i majtë \| bregu i djathtë, ⛵ = ku është varka |
| **Fillimi → Qëllimi** | `(3, 3, 1)` → `(0, 0, 0)` |
| **Veprimet** | Varka bart `(m, c) ∈ {(1,0), (2,0), (0,1), (0,2), (1,1)}`, shënuar si `1M0C`, `0M2C` etj. |
| **Kufizimi** | Në asnjë breg misionarët (nëse ka) nuk mund të jenë më pak se kanibalët (`mc_valid`) |
| **Landscape** | `4 × 4 × 2 = 32` gjendje teorike, 20 të vlefshme, 16 të arritshme nga fillimi |

Pema ndërtohet me **BFS**. Gjendjet që shkelin kufizimin preren dhe nuk shfaqen. Gjendjet që janë parë më herët shënohen `[përsëritur]` dhe nuk zgjerohen.

```mermaid
flowchart TD
    n0["(3,3,1)<br/>⛵ MMMCCC | –"]
    n1["(3,2,0)<br/>MMMCC | C ⛵"]
    n2["(3,1,0)<br/>MMMC | CC ⛵"]
    n3["(2,2,0)<br/>MMCC | MC ⛵"]
    n4["(3,3,1)<br/>⛵ MMMCCC | –<br/>(përsëritur)"]
    n5["(3,2,1)<br/>⛵ MMMCC | C"]
    n6["(3,3,1)<br/>⛵ MMMCCC | –<br/>(përsëritur)"]
    n7["(3,2,1)<br/>⛵ MMMCC | C<br/>(përsëritur)"]
    n8["(3,3,1)<br/>⛵ MMMCCC | –<br/>(përsëritur)"]
    n9["(2,2,0)<br/>MMCC | MC ⛵<br/>(përsëritur)"]
    n10["(3,1,0)<br/>MMMC | CC ⛵<br/>(përsëritur)"]
    n11["(3,0,0)<br/>MMM | CCC ⛵"]
    n12["(3,1,1)<br/>⛵ MMMC | CC"]
    n13["(3,2,1)<br/>⛵ MMMCC | C<br/>(përsëritur)"]
    n14["(1,1,0)<br/>MC | MMCC ⛵"]
    n15["(3,0,0)<br/>MMM | CCC ⛵<br/>(përsëritur)"]
    n16["(3,1,1)<br/>⛵ MMMC | CC<br/>(përsëritur)"]
    n17["(2,2,1)<br/>⛵ MMCC | MC"]
    n18["(0,2,0)<br/>CC | MMMC ⛵"]
    n19["(1,1,0)<br/>MC | MMCC ⛵<br/>(përsëritur)"]
    n20["(2,2,1)<br/>⛵ MMCC | MC<br/>(përsëritur)"]
    n21["(0,3,1)<br/>⛵ CCC | MMM"]
    n22["(0,2,0)<br/>CC | MMMC ⛵<br/>(përsëritur)"]
    n23["(0,1,0)<br/>C | MMMCC ⛵"]
    n24["(1,1,1)<br/>⛵ MC | MMCC"]
    n25["(0,2,1)<br/>⛵ CC | MMMC"]
    n26["(0,3,1)<br/>⛵ CCC | MMM<br/>(përsëritur)"]
    n27["(0,1,0)<br/>C | MMMCC ⛵<br/>(përsëritur)"]
    n28["(0,0,0)<br/>– | MMMCCC ⛵<br/>GOAL"]
    n29["(0,1,0)<br/>C | MMMCC ⛵<br/>(përsëritur)"]
    n30["(0,0,0)<br/>– | MMMCCC ⛵<br/>GOAL"]
    n0 -->|0M1C| n1
    n0 ==>|0M2C| n2
    n0 -->|1M1C| n3
    n1 -->|0M1C| n4
    n2 ==>|0M1C| n5
    n2 -->|0M2C| n6
    n3 -->|1M0C| n7
    n3 -->|1M1C| n8
    n5 -->|1M0C| n9
    n5 -->|0M1C| n10
    n5 ==>|0M2C| n11
    n11 ==>|0M1C| n12
    n11 -->|0M2C| n13
    n12 ==>|2M0C| n14
    n12 -->|0M1C| n15
    n14 -->|2M0C| n16
    n14 ==>|1M1C| n17
    n17 ==>|2M0C| n18
    n17 -->|1M1C| n19
    n18 -->|2M0C| n20
    n18 ==>|0M1C| n21
    n21 -->|0M1C| n22
    n21 ==>|0M2C| n23
    n23 ==>|1M0C| n24
    n23 -->|0M1C| n25
    n23 -->|0M2C| n26
    n24 -->|1M0C| n27
    n24 ==>|1M1C| n28
    n25 -->|0M1C| n29
    n25 -->|0M2C| n30
    classDef goal fill:#c8f0c8,stroke:#1e7b1e,stroke-width:3px,color:#000
    classDef path fill:#dcebff,stroke:#1f5fbf,stroke-width:3px,color:#000
    classDef rep fill:#eeeeee,stroke:#888888,color:#555
    class n28,n30 goal
    class n0,n2,n5,n11,n12,n14,n17,n18,n21,n23,n24 path
    class n4,n6,n7,n8,n9,n10,n13,n15,n16,n19,n20,n22,n26,n27,n29 rep
```

<details>
<summary>Pema si tekst (dalja e programit)</summary>

```
(3, 3, 1)
├── --0M1C--> (3, 2, 0)
│   └── --0M1C--> (3, 3, 1) [përsëritur]
├── --0M2C--> (3, 1, 0)
│   ├── --0M1C--> (3, 2, 1)
│   │   ├── --1M0C--> (2, 2, 0) [përsëritur]
│   │   ├── --0M1C--> (3, 1, 0) [përsëritur]
│   │   └── --0M2C--> (3, 0, 0)
│   │       ├── --0M1C--> (3, 1, 1)
│   │       │   ├── --2M0C--> (1, 1, 0)
│   │       │   │   ├── --2M0C--> (3, 1, 1) [përsëritur]
│   │       │   │   └── --1M1C--> (2, 2, 1)
│   │       │   │       ├── --2M0C--> (0, 2, 0)
│   │       │   │       │   ├── --2M0C--> (2, 2, 1) [përsëritur]
│   │       │   │       │   └── --0M1C--> (0, 3, 1)
│   │       │   │       │       ├── --0M1C--> (0, 2, 0) [përsëritur]
│   │       │   │       │       └── --0M2C--> (0, 1, 0)
│   │       │   │       │           ├── --1M0C--> (1, 1, 1)
│   │       │   │       │           │   ├── --1M0C--> (0, 1, 0) [përsëritur]
│   │       │   │       │           │   └── --1M1C--> (0, 0, 0) [GOAL]
│   │       │   │       │           ├── --0M1C--> (0, 2, 1)
│   │       │   │       │           │   ├── --0M1C--> (0, 1, 0) [përsëritur]
│   │       │   │       │           │   └── --0M2C--> (0, 0, 0) [GOAL]
│   │       │   │       │           └── --0M2C--> (0, 3, 1) [përsëritur]
│   │       │   │       └── --1M1C--> (1, 1, 0) [përsëritur]
│   │       │   └── --0M1C--> (3, 0, 0) [përsëritur]
│   │       └── --0M2C--> (3, 2, 1) [përsëritur]
│   └── --0M2C--> (3, 3, 1) [përsëritur]
└── --1M1C--> (2, 2, 0)
    ├── --1M0C--> (3, 2, 1) [përsëritur]
    └── --1M1C--> (3, 3, 1) [përsëritur]
```

</details>

**Zgjidhja optimale ka 11 kalime.** Pema tregon dy rrugë të ndryshme me gjatësi 11, që ndryshojnë vetëm në dy kalimet e fundit:

```
(3,3,1) → (3,1,0) → (3,2,1) → (3,0,0) → (3,1,1) → (1,1,0) → (2,2,1)
        → (0,2,0) → (0,3,1) → (0,1,0) → (1,1,1) → (0,0,0)
```

---

## 4.3 Rotating Workforce Scheduling

Instanca e vogël, që pema të jetë e lexueshme:

- **3 punëtorë**, cikël **3-javor**: orari është matricë 3 × 7. Punëtori që e fillon në rreshtin 1 kalon në rreshtin 2 javën tjetër, pastaj në rreshtin 3, pastaj prapë në 1. Prandaj orari lexohet si një varg ciklik me 21 ditë.
- **Ndërrimet:** `D` (ditë), `N` (natë), `-` (pushim).

| | Kufizimi | Në kod |
|---|---|---|
| C1 | Çdo ditë: 1 × D, 1 × N, 1 × pushim | `permutations("DN-")` |
| C2 | Ndalohet natë → ditë (pa pushim pas natës) | `"ND" in x` |
| C3 | Maksimum 2 netë radhazi | `"NNN" in x` |
| C4 | Maksimum 4 ditë pune radhazi | `re.search("[DN]{5}", x)` |

| Elementi | Përkufizimi |
|---|---|
| **Variablat** | Ditët (kolonat) 1..7 |
| **Domain-i** | `3! = 6` permutacione të `{D, N, −}`, që e plotëson C1 automatikisht |
| **Veprimi** | Cakto ndërrimet e ditës së radhës për të 3 punëtorët |
| **Landscape** | `3^21 ≈ 10^10` pa kufizime; `6^7 = 279 936` me C1 |

Pema ndërtohet me **DFS + Backtracking**. Çdo nyje tregon ndërrimet e ditës për punëtorët P1 P2 P3 (p.sh. `D-N` = P1 ditë, P2 pushim, P3 natë). Degët `[X]` e shkelin një kufizim dhe preren menjëherë.

```mermaid
flowchart TD
    n0["Start"]
    n1["P1: D<br/>P2: N<br/>P3: -"]
    n2["P1: D<br/>P2: N<br/>P3: -"]
    n3["P1: D<br/>P2: N<br/>P3: -<br/>✗"]
    n4["P1: D<br/>P2: -<br/>P3: N"]
    n5["P1: D<br/>P2: N<br/>P3: -"]
    n6["P1: D<br/>P2: N<br/>P3: -<br/>✗"]
    n7["P1: D<br/>P2: -<br/>P3: N<br/>✗"]
    n8["P1: N<br/>P2: D<br/>P3: -<br/>✗"]
    n9["P1: N<br/>P2: -<br/>P3: D<br/>✗"]
    n10["P1: -<br/>P2: D<br/>P3: N<br/>✗"]
    n11["P1: -<br/>P2: N<br/>P3: D"]
    n12["P1: D<br/>P2: N<br/>P3: -<br/>✗"]
    n13["P1: D<br/>P2: -<br/>P3: N"]
    n14["P1: D<br/>P2: N<br/>P3: -<br/>GOAL"]
    n0 ==>|dita 1| n1
    n1 ==>|dita 2| n2
    n2 -->|dita 3| n3
    n2 ==>|dita 3| n4
    n4 ==>|dita 4| n5
    n5 -->|dita 5| n6
    n5 -->|dita 5| n7
    n5 -->|dita 5| n8
    n5 -->|dita 5| n9
    n5 -->|dita 5| n10
    n5 ==>|dita 5| n11
    n11 -->|dita 6| n12
    n11 ==>|dita 6| n13
    n13 ==>|dita 7| n14
    classDef goal fill:#c8f0c8,stroke:#1e7b1e,stroke-width:3px,color:#000
    classDef path fill:#dcebff,stroke:#1f5fbf,stroke-width:3px,color:#000
    classDef bad fill:#ffe0e0,stroke:#b22222,color:#000
    class n14 goal
    class n0,n1,n2,n4,n5,n11,n13 path
    class n3,n6,n7,n8,n9,n10,n12 bad
```

<details>
<summary>Pema si tekst (dalja e programit)</summary>

```
Start
└── --dita 1--> DN-
    └── --dita 2--> DN-
        ├── --dita 3--> DN- [X]
        └── --dita 3--> D-N
            └── --dita 4--> DN-
                ├── --dita 5--> DN- [X]
                ├── --dita 5--> D-N [X]
                ├── --dita 5--> ND- [X]
                ├── --dita 5--> N-D [X]
                ├── --dita 5--> -DN [X]
                └── --dita 5--> -ND
                    ├── --dita 6--> DN- [X]
                    └── --dita 6--> D-N
                        └── --dita 7--> DN- [GOAL]
```

</details>

Shembuj prerjesh:
- **Dita 3, `DN-` [X]**: P2 do të kishte `N N N`, 3 netë radhazi (C3).
- **Dita 5, `DN-` [X]**: P1 do të kishte `D D D D D`, 5 ditë pune radhazi (C4).

**Orari i gjetur:**

```
Java 1: D D D D - D D
Java 2: N N - N N - N
Java 3: - - N - D N -
```

## 4.4 Pyetje të mundshme

**Çka është search tree, dhe si dallon nga state space?** State space është bashkësia e të gjitha gjendjeve. Search tree është mënyra si një algoritëm i viziton ato, ku e njëjta gjendje mund të paraqitet disa herë (prandaj ka nyje `[përsëritur]`).

**Pse BFS për 8-Puzzle dhe M&C?** BFS gjen zgjidhjen me më pak hapa (optimale), sepse çdo veprim kushton 1.

**Pse DFS për Rotating Workforce?** Të gjitha zgjidhjet janë në thellësinë 7 (7 ditë), prandaj DFS + backtracking është më efikas.

**Pse 8-Puzzle ka vetëm 181 440 gjendje dhe jo 9! = 362 880?** Gjysma e renditjeve nuk mund të arrihen me lëvizje të ligjshme (varet nga pariteti i numrit të inversioneve).