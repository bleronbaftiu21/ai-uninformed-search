"""Struktura e përbashkët për ndërtimin dhe vizatimin e Search Trees.

Një Search Tree ka:
* nyjen rrënjë (gjendja fillestare),
* për çdo nyje, fëmijët = gjendjet që arrihen me një veprim,
* etiketë në degë = veprimi që u aplikua.

Nyjet ngjyrosen sipas statusit:
    goal      – gjendja qëllim (jeshile)
    path      – në rrugën nga rrënja te qëllimi (blu)
    invalid   – gjendje që shkel kufizimet, prerë nga backtracking (e kuqe)
    repeated  – gjendje e përsëritur, nuk zgjerohet (gri)
    frontier  – e gjeneruar por e pazgjeruar për shkak të kufirit të thellësisë
    normal    – e zgjeruar
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

STYLE = {
    "normal": ('#FFFFFF', '#333333'),
    "path": ('#DCEBFF', '#1F5FBF'),
    "goal": ('#C8F0C8', '#1E7B1E'),
    "invalid": ('#FFE0E0', '#B22222'),
    "repeated": ('#EEEEEE', '#888888'),
    "frontier": ('#FFF6D5', '#B08900'),
}


@dataclass
class TreeNode:
    id: int
    label: str
    depth: int
    parent: Optional[int] = None
    action: str = ""
    status: str = "normal"
    children: List[int] = field(default_factory=list)


class SearchTree:
    def __init__(self, title: str) -> None:
        self.title = title
        self.nodes: List[TreeNode] = []

    def add(self, label: str, parent: Optional[int] = None, action: str = "",
            status: str = "normal") -> int:
        depth = 0 if parent is None else self.nodes[parent].depth + 1
        node = TreeNode(len(self.nodes), label, depth, parent, action, status)
        self.nodes.append(node)
        if parent is not None:
            self.nodes[parent].children.append(node.id)
        return node.id

    def mark_path(self, goal_id: int) -> List[int]:
        """Shënon rrugën rrënjë → qëllim dhe e kthen si listë id-sh."""
        path = []
        cur: Optional[int] = goal_id
        while cur is not None:
            path.append(cur)
            if self.nodes[cur].status != "goal":
                self.nodes[cur].status = "path"
            cur = self.nodes[cur].parent
        return list(reversed(path))

    # ------------------------------------------------------------------ #
    # Statistika
    # ------------------------------------------------------------------ #
    def counts(self) -> dict:
        result: dict = {"total": len(self.nodes)}
        for n in self.nodes:
            result[n.status] = result.get(n.status, 0) + 1
        result["depth"] = max((n.depth for n in self.nodes), default=0)
        return result

    # ------------------------------------------------------------------ #
    # Eksport
    # ------------------------------------------------------------------ #
    def to_text(self, max_nodes: int = 400) -> str:
        marks = {"goal": " [GOAL]", "invalid": " [X invalid]", "repeated": " [perseritur]",
                 "frontier": " [...]", "path": " *", "normal": ""}
        lines: List[str] = [self.title]
        shown = 0

        def walk(nid: int, prefix: str, is_last: bool) -> None:
            nonlocal shown
            if shown >= max_nodes:
                return
            shown += 1
            node = self.nodes[nid]
            label = node.label.replace("\n", " / ")
            act = f"--{node.action}--> " if node.action else ""
            connector = "" if node.parent is None else ("└── " if is_last else "├── ")
            lines.append(f"{prefix}{connector}{act}{label}{marks[node.status]}")
            child_prefix = prefix + ("" if node.parent is None else ("    " if is_last else "│   "))
            for i, cid in enumerate(node.children):
                walk(cid, child_prefix, i == len(node.children) - 1)

        if self.nodes:
            walk(0, "", True)
        if shown >= max_nodes:
            lines.append(f"... ({len(self.nodes) - shown} nyje të tjera)")
        return "\n".join(lines)

    def to_dot(self, rankdir: str = "TB", fontname: str = "Helvetica") -> str:
        out = [
            "digraph SearchTree {",
            f'  graph [rankdir={rankdir}, labelloc=t, fontsize=20, fontname="{fontname}", '
            f'label="{self.title}", nodesep=0.25, ranksep=0.45];',
            f'  node [shape=box, style="rounded,filled", fontname="Courier", fontsize=11];',
            f'  edge [fontname="{fontname}", fontsize=9, color="#555555"];',
        ]
        for n in self.nodes:
            fill, border = STYLE[n.status]
            label = n.label.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            pen = "2.2" if n.status in ("goal", "path") else "1"
            out.append(f'  n{n.id} [label="{label}", fillcolor="{fill}", color="{border}", '
                       f'penwidth={pen}];')
        for n in self.nodes:
            if n.parent is not None:
                bold = n.status in ("goal", "path")
                attrs = f'label=" {n.action}"'
                if bold:
                    attrs += ', color="#1F5FBF", penwidth=2'
                out.append(f"  n{n.parent} -> n{n.id} [{attrs}];")
        out.append("}")
        return "\n".join(out)

    def save(self, directory: Path, name: str, rankdir: str = "TB") -> List[Path]:
        """Ruan .dot, .txt dhe (nëse Graphviz është i instaluar) .png."""
        directory.mkdir(parents=True, exist_ok=True)
        dot_path = directory / f"{name}.dot"
        txt_path = directory / f"{name}.txt"
        dot_path.write_text(self.to_dot(rankdir), encoding="utf-8")
        txt_path.write_text(self.to_text(), encoding="utf-8")
        written = [dot_path, txt_path]
        if shutil.which("dot"):
            png_path = directory / f"{name}.png"
            subprocess.run(["dot", "-Tpng", "-Gdpi=110", str(dot_path), "-o", str(png_path)],
                           check=True)
            written.append(png_path)
        return written
