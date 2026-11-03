"""Statistika të përbashkëta për të gjithë algoritmet e kërkimit."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class SearchStats:
    """Mban numrat që na tregojnë sa punë ka bërë algoritmi.

    Attributes:
        nodes_expanded: sa nyje (gjendje) janë vizituar/zgjeruar.
        nodes_generated: sa fëmijë (gjendje të reja) janë gjeneruar.
        pruned: sa degë janë prerë nga backtracking-u (shkelin kufizimet).
        max_frontier: madhësia maksimale e frontier-it (vetëm për BFS).
        max_depth: thellësia maksimale e arritur.
        iterations: numri i iteracioneve (vetëm për IDDFS).
        elapsed: koha totale në sekonda.
    """

    nodes_expanded: int = 0
    nodes_generated: int = 0
    pruned: int = 0
    max_frontier: int = 0
    max_depth: int = 0
    iterations: int = 0
    elapsed: float = 0.0
    extra: dict = field(default_factory=dict)

    _start: float = field(default=0.0, repr=False)

    def start(self) -> None:
        self._start = time.perf_counter()

    def stop(self) -> None:
        self.elapsed = time.perf_counter() - self._start

    def summary(self) -> str:
        lines = [
            f"  Nyje te zgjeruara : {self.nodes_expanded:,}",
            f"  Nyje te gjeneruara: {self.nodes_generated:,}",
            f"  Dege te prera     : {self.pruned:,}",
            f"  Thellesia max     : {self.max_depth}",
        ]
        if self.max_frontier:
            lines.append(f"  Frontier max      : {self.max_frontier:,}")
        if self.iterations:
            lines.append(f"  Iteracione IDDFS  : {self.iterations}")
        for key, value in self.extra.items():
            lines.append(f"  {key:<18}: {value}")
        lines.append(f"  Koha              : {self.elapsed:.4f} s")
        return "\n".join(lines)


class SearchTimeout(Exception):
    """Ngritet kur kërkimi tejkalon kohën e lejuar."""


def sci(value: int) -> str:
    """Formaton numra shumë të mëdhenj si '≈ 2.39 × 10^15'."""
    if value < 10**7:
        return f"{value:,}"
    digits = str(value)
    exp = len(digits) - 1
    mantissa = int(digits[:3]) / 100
    return f"≈ {mantissa:.2f} × 10^{exp}"
