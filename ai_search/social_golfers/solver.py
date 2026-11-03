"""Social Golfers Problem me Depth First Search (DFS) + Backtracking.

Problemi
--------
n = g × p lojtarë luajnë çdo javë në g grupe me nga p lojtarë. Gjej një orar
për w javë ku asnjë çift lojtarësh nuk bie bashkë në grup më shumë se një herë.
Instanca e detyrës: g = 8, p = 4 (n = 32).

Modelimi
--------
* Variablat: X[w][g][s] = lojtari në javën w, grupin g, vendin s
  (0 <= w < W, 0 <= g < G, 0 <= s < P).
* Domain-i : {0, 1, ..., n-1}.
* Kufizimet:
    C1  Çdo javë është ndarje (partition): çdo lojtar luan saktësisht një herë.
    C2  Për çdo çift (a, b): numri i javëve ku a dhe b janë në të njëjtin grup <= 1.
* Veprimi  : cakto lojtarin e radhës në vendin e radhës (week → group → slot).
* Goal     : të gjitha W javët janë mbushur pa shkelur C1, C2.

Symmetry breaking (valide – nuk humbet asnjë zgjidhje deri në simetri):
* S1  Brenda grupit lojtarët janë në rend rritës.
* S2  Lojtari i parë i çdo grupi është lojtari më i vogël ende i pacaktuar në
      atë javë (grupet renditen sipas lojtarit të parë).
* S3  Java 0 fiksohet: {0..p-1}, {p..2p-1}, ...
* S4  Javët renditen sipas partnerit të dytë të lojtarit 0 (X[w][0][1] rritës).
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from math import comb, factorial
from typing import List, Optional

from ai_search.stats import SearchStats, SearchTimeout

Schedule = List[List[List[int]]]  # schedule[week][group] = [lojtarët]


@dataclass
class GolfersResult:
    schedule: Optional[Schedule]        # orari për numrin e kërkuar të javëve
    best_schedule: Schedule             # orari më i gjatë i gjetur (javë të plota)
    weeks_requested: int
    stats: SearchStats
    timed_out: bool = False

    @property
    def solved(self) -> bool:
        return self.schedule is not None

    @property
    def best_weeks(self) -> int:
        return len(self.best_schedule)


class SocialGolfersDFS:
    def __init__(self, groups: int = 8, size: int = 4, weeks: int = 10,
                 symmetry_breaking: bool = True, seed: Optional[int] = None) -> None:
        if groups < 1 or size < 1 or weeks < 1:
            raise ValueError("groups, size dhe weeks duhet të jenë >= 1")
        self.g = groups
        self.p = size
        self.w = weeks
        self.n = groups * size
        self.symmetry_breaking = symmetry_breaking
        # seed=None -> DFS klasik (vlerat provohen në rend rritës).
        # seed=k    -> DFS me renditje të rastësishme të vlerave (randomized DFS).
        self.seed = seed

    # ------------------------------------------------------------------ #
    def solve(self, time_limit: Optional[float] = None) -> GolfersResult:
        G, P, W, N = self.g, self.p, self.w, self.n
        sym = self.symmetry_breaking
        stats = SearchStats()
        stats.start()
        deadline = None if time_limit is None else time.perf_counter() + time_limit

        sched: Schedule = [[[-1] * P for _ in range(G)] for _ in range(W)]
        week_used = [0] * W          # bitmask: kush luan tashmë në javën w
        met = [0] * N                # met[a] bitmask: me kë është takuar a
        best: List[Schedule] = [[]]  # mbajmë orarin më të gjatë të plotë

        total_positions = W * G * P
        full_mask = (1 << N) - 1
        rng = random.Random(self.seed) if self.seed is not None else None

        def record_best(weeks_done: int) -> None:
            if weeks_done > len(best[0]):
                best[0] = [[grp[:] for grp in sched[k]] for k in range(weeks_done)]

        start_pos = 0
        if sym:
            # S3: java 0 fiksohet.
            for gi in range(G):
                members = list(range(gi * P, gi * P + P))
                sched[0][gi] = members
                for a in members:
                    week_used[0] |= 1 << a
                    for b in members:
                        if a != b:
                            met[a] |= 1 << b
            start_pos = G * P
            record_best(1)

        def week_still_feasible(w: int) -> bool:
            free = full_mask & ~week_used[w]
            rest = free
            while rest:
                low = rest & -rest
                u = low.bit_length() - 1
                rest ^= low
                if (free & ~met[u] & ~low).bit_count() < P - 1:
                    return False
            return True

        def has_big_clique() -> bool:
            # Kontroll i shpejtë (greedy) për klikë në grafin "kush është takuar".
            # Nëse gjendet klikë me > G lojtarë, java e ardhshme s'ka zgjidhje.
            for u in range(N):
                clique = 1 << u
                cand = met[u]
                size = 1
                while cand:
                    low = cand & -cand
                    x = low.bit_length() - 1
                    cand ^= low
                    if met[x] & clique == clique:
                        clique |= low
                        size += 1
                        cand &= met[x]
                        if size > G:
                            return True
            return False

        def dfs(pos: int) -> bool:
            stats.nodes_expanded += 1
            if deadline is not None and (stats.nodes_expanded & 0x3FFF) == 0:
                if time.perf_counter() > deadline:
                    raise SearchTimeout

            if pos == total_positions:                    # goal
                return True

            w, rest = divmod(pos, G * P)
            gi, s = divmod(rest, P)
            if pos > stats.max_depth:
                stats.max_depth = pos

            group = sched[w][gi]
            group_mask = 0
            for k in range(s):
                group_mask |= 1 << group[k]

            used = week_used[w]
            met_union = 0
            for k in range(s):
                met_union |= met[group[k]]

            if s == 0 and sym:
                # S2: vetëm lojtari më i vogël i pacaktuar.
                v = 0
                while used >> v & 1:
                    v += 1
                values = range(v, v + 1)
            else:
                lo = group[s - 1] + 1 if (s > 0 and sym) else 0      # S1
                if sym and w > 0 and gi == 0 and s == 1 and w > 1:   # S4
                    lo = max(lo, sched[w - 1][0][1] + 1)
                values = range(lo, N)
                if rng is not None:
                    values = list(values)
                    rng.shuffle(values)

            for v in values:
                bit = 1 << v
                if used & bit:                            # C1
                    stats.pruned += 1
                    continue
                if met[v] & group_mask:                   # C2
                    stats.pruned += 1
                    continue
                if not sym and s > 0 and v < group[s - 1]:
                    # edhe pa symmetry breaking mbajmë grupet si bashkësi
                    stats.pruned += 1
                    continue

                if s < P - 1:
                    # Forward check (backtracking i hershëm): a mbeten mjaft
                    # lojtarë të lirë, > v, që nuk e kanë takuar askënd nga
                    # grupi (përfshirë v), për t'i mbushur vendet e mbetura?
                    free = full_mask & ~(used | bit) & ~((bit << 1) - 1)
                    free &= ~(met[v] | met_union)
                    if free.bit_count() < P - 1 - s:
                        stats.pruned += 1
                        continue

                # apliko
                stats.nodes_generated += 1
                group[s] = v
                week_used[w] |= bit
                for k in range(s):
                    met[group[k]] |= bit
                met[v] |= group_mask

                if s == P - 1 and gi == G - 1:
                    record_best(w + 1)                    # java w u përfundua
                if s == P - 1 and gi == G - 1 and w < W - 1 and has_big_clique():
                    # Java u mbyll, por ekziston një grup prej > G lojtarësh që
                    # janë takuar të gjithë me njëri-tjetrin; në javën tjetër
                    # secili prej tyre duhet në grup të ndryshëm -> e pamundur.
                    stats.pruned += 1
                elif s == P - 1 and not week_still_feasible(w):
                    # Grupi u mbyll, por ndonjë lojtar i mbetur i javës nuk ka
                    # më (p-1) partnerë të mundshëm -> dega nuk ka zgjidhje.
                    stats.pruned += 1
                elif dfs(pos + 1):
                    return True

                # backtrack
                for k in range(s):
                    met[group[k]] &= ~bit
                met[v] &= ~group_mask
                week_used[w] &= ~bit
                group[s] = -1
            return False

        found = False
        timed_out = False
        try:
            found = dfs(start_pos)
        except SearchTimeout:
            timed_out = True
        if found:
            record_best(W)

        stats.stop()
        stats.extra["Javet e gjetura"] = len(best[0])
        return GolfersResult(
            schedule=[[grp[:] for grp in wk] for wk in sched] if found else None,
            best_schedule=best[0],
            weeks_requested=W,
            stats=stats,
            timed_out=timed_out,
        )


def search_max_weeks(groups: int = 8, size: int = 4, restarts: int = 10,
                     time_per_run: float = 5.0, first_seed: int = 0) -> GolfersResult:
    """Kërkon numrin maksimal të javëve.

    Run 0 është DFS klasik (deterministik). Run-et e tjera janë DFS me renditje
    të rastësishme të vlerave (restarts). Kthen rezultatin me më shumë javë.
    """
    target = upper_bound_weeks(groups, size)
    best: Optional[GolfersResult] = None
    for k in range(restarts):
        seed = None if k == 0 else first_seed + k
        result = SocialGolfersDFS(groups, size, target, seed=seed).solve(time_per_run)
        result.stats.extra["Run (seed)"] = "klasik" if seed is None else seed
        if best is None or result.best_weeks > best.best_weeks:
            best = result
        if result.solved:
            break
    assert best is not None
    return best


# ---------------------------------------------------------------------- #
# Objective function, validim, landscape
# ---------------------------------------------------------------------- #
def objective(schedule: Schedule) -> int:
    """f(S) = Σ_{a<b} max(0, takime(a, b) - 1)  (minimizim; 0 = orar i vlefshëm).

    Numëron sa takime të tepërta (çifte që përsëriten) ka orari.
    """
    meetings: dict = {}
    for week in schedule:
        for group in week:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    key = (min(group[i], group[j]), max(group[i], group[j]))
                    meetings[key] = meetings.get(key, 0) + 1
    return sum(max(0, m - 1) for m in meetings.values())


def is_valid(schedule: Schedule, groups: int, size: int) -> bool:
    n = groups * size
    for week in schedule:
        if len(week) != groups or any(len(g) != size for g in week):
            return False
        players = sorted(v for g in week for v in g)
        if players != list(range(n)):
            return False
    return objective(schedule) == 0


def upper_bound_weeks(groups: int, size: int) -> int:
    """Kufiri i sipërm: çdo javë lojtari takon (p-1) të rinj nga (n-1) gjithsej,
    pra w <= floor((n-1)/(p-1))."""
    n = groups * size
    return (n - 1) // (size - 1) if size > 1 else 10**9


def landscape(groups: int, size: int, weeks: int) -> dict:
    """Madhësia e hapësirës së kërkimit për modele të ndryshme."""
    n = groups * size
    raw = n ** (n * weeks)                                   # çdo variabël 0..n-1
    perms = factorial(n) ** weeks                            # çdo javë një permutacion
    partitions_per_week = factorial(n) // (factorial(size) ** groups * factorial(groups))
    partitions = partitions_per_week ** weeks                # çdo javë një ndarje
    with_sym = partitions_per_week ** (weeks - 1) if weeks > 1 else 1
    return {
        "variabla": n * weeks,
        "pa_kufizime (n^(n*w))": raw,
        "permutacione (n!^w)": perms,
        "ndarje_per_jave": partitions_per_week,
        "ndarje (P^w)": partitions,
        "me_jave_0_fikse (P^(w-1))": with_sym,
        "cifte_totale C(n,2)": comb(n, 2),
        "cifte_per_jave g*C(p,2)": groups * comb(size, 2),
        "kufiri_siperm_javeve": upper_bound_weeks(groups, size),
    }


def format_schedule(schedule: Schedule) -> str:
    if not schedule:
        return "(bosh)"
    lines = []
    for w, week in enumerate(schedule, 1):
        groups = "  ".join("{" + ",".join(f"{v:>2}" for v in g) + "}" for g in week)
        lines.append(f"Java {w:>2}: {groups}")
    return "\n".join(lines)
