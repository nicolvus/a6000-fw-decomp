"""Tablas reproducibles de E24-05: `python scripts/e24_05/report.py` (solo lectura de darwin_core.bin)."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dwn import DARWIN, SHA256, Core
from graph import BASE, build, build_all
from reach import ERR, PRIMS, Reach, Scenario, summarize

TARGETS = {**PRIMS, 0x1F5A6: "rearme directo (gated)", 0x1FCB8: "freno P4=3 + apagado", ERR: "error", 0xD18E: "libera máscara",
           0x20C90: "bobina on", 0x1F396: "inner A", 0x1F3B6: "inner B", 0x1984E: "API cargar"}


def closure(g):
    c = g.c
    vec = sorted({c.u32(BASE + 4 * k) - 1 for k in range(1, 0x40) if c.u32(BASE + 4 * k) & 1})
    st = lambda s, j: c.u32(0x25B50 + 16 * s + 4 * j) - 1
    c1 = [0x45C8, 0x46AC, 0x4538, 0x4562] + [st(s, j) for s in (0, 1) for j in range(4)] + [st(5, 1), 0xEC42, 0xECE4, 0xECA0]
    _, s1 = build(c1, g)
    _, s2 = build(c1 + vec + [st(4, j) for j in range(4)], g)
    return s1, s2, vec


def differential(r: Reach):
    rows = []
    for name, ent, r0 in (("API cargar(0) 0x1984e", 0x1984E, 0), ("API cargar(1) 0x1984e", 0x1984E, 1),
                          ("API B 0x19998", 0x19998, 0), ("API C 0x199b8", 0x199B8, 0), ("op 5 (recuperación) 0xd46e", 0xD46E, None)):
        for gate in (0, 4):
            res = r.run(ent, Scenario(gate, 0), r0)
            s = summarize(res, TARGETS)
            err6 = sorted({hex(a) for a, _, r0v in s.get(ERR, []) if r0v == 6})
            rows.append((name, gate, sorted({hex(p) for d, p in res.lists if d == 0x29CF0}), sorted(i for d, i in res.states if d == 0x29CF0),
                         sorted(hex(t) for t in s if t in PRIMS or t in (0x1F5A6, 0x1FCB8)), err6))
    return rows


def write_closure(g, s1, s2, path: Path):
    """Evidencia de la clausura: funciones C1/C2 y sitios de llamada indirecta de C1 con su estado."""
    import json
    resolved = {0x496C: "tabla de estados 0x25b50 (init)", 0x4970: "tabla de estados (main)", 0x4974: "tabla de estados (next)",
                0x497A: "tabla de estados (exit)", 0x442E: "scatter-load: manejadores 0x4438/0x4494", 0x45CE: "salto a scatter-load 0x43fd",
                0x45C2: "salto al vector del arranque 0x0000-0x41ff (destino SIN binario)"}
    sites = sorted(a for f in s1 for a in g.indirect.get(f, []))
    out = {"binario_sha256": SHA256, "c1": sorted(s1), "c2": sorted(s2),
           "indirectas_c1": [{"sitio": a, "resuelta": resolved.get(a, "abierta")} for a in sites]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1))
    n_open = sum(1 for a in sites if a not in resolved)
    print(f"escrito {path} ({len(sites)} sitios indirectos en C1, {n_open} abiertos)")


def main():
    core = Core()
    assert core.sha256() == SHA256, "darwin_core.bin no es el 3.21 oficial"
    print("binario", DARWIN.name, hashlib.sha256(core.data).hexdigest())
    g = build_all()
    s1, s2, vec = closure(g)
    print(f"clausura C1 (reset→Init→Seton→COM→InitCom→Upd): {len(s1)} funciones; C2 (+vectores {len(vec)} y Off): {len(s2)}; funciones descritas: {len(g.bodies)}")
    if "--write" in sys.argv:
        write_closure(g, s1, s2, Path(__file__).resolve().parents[2] / "analysis/e24-05/recovery-closure.json")
    r = Reach(core)
    for row in differential(r):
        print(row)


if __name__ == "__main__":
    main()
