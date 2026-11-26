#!/usr/bin/env python3
"""Firma de la ruta de video por perfil del arnes (log del MMgr ya extraido).

Lee reports/evidence/logs-arnes-todos/<perfil>.log.txt (salida literal de
extraer_log_estado.py) y <perfil>.agujas.tsv (conteos en el flujo crudo), y escribe:
  index.tsv   una fila por perfil con la firma completa
  firmas.md   agrupacion: firma -> perfiles
  resumen.txt veredictos y respondibilidad de "¿algun IFO cargado?"

Regla de oro: solo cuentan como EMITIDAS las lineas con valor rellenado (codigo
0x........, numero de linea concreto) o las que varian entre perfiles; las cadenas
constantes en los 214 perfiles son literales de .rodata y NO prueban nada.
"""
import re
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
LOGS = RAIZ / "reports/evidence/logs-arnes-todos"
LIVE = RAIZ / "analysis/gui/g22/harness/live"

PLANTILLA = re.compile(r"%[0-9.\-+ l#]*[sdluxXfcgeEp]")
# [MMGR][MMGR_ACSR] ## ERROR(MMGR):0xB0800001 ## mmgrifoacsr/MMgrMp4IfoAcsr.cpp(2319) LoadSub()
ERROR_MMGR = re.compile(
    r"## ERROR\((?P<mod>[A-Z_]+)\):(?P<code>0x[0-9A-F]{8}) ## "
    r"(?P<src>[\w/]+\.cpp)\((?P<line>\d+)\) (?P<fn>\w+)\(\)"
)
AVISEQ = re.compile(r"AviSeq(?P<mod>\w+)\.cpp Error=\[(?P<cod>\w+)\]")
IFO_ERR = re.compile(r"mp4Ifo faild at (?P<src>[^\s]+)\((?P<line>\d+)\) ErrCd: (?P<cod>0x[0-9A-F]{8})")
XAVC_ERR = re.compile(r"xavcIfo faild at (?P<src>[^\s]+)\((?P<line>\d+)\) ErrCd: (?P<cod>0x[0-9A-F]{8})")
AVIMMGR = re.compile(r"\[AVIMMGR\]\[\w+\](?P<msg>[^\r\n]{0,70})")

GRUPOS = ("Mp4", "Xavc", "AvcHd", "IfoComposer")


def emitidas(ruta: Path):
    for raw in ruta.read_bytes().split(b"\n"):
        if len(raw) < 12:
            continue
        s = bytes(c for c in raw if 32 <= c < 127).decode("ascii", "replace").strip()
        if len(s) >= 12 and not PLANTILLA.search(s):
            yield s


def firma(perfil: str):
    mmgr, aviseq, ifo, xavc, avimmgr, txt = [], [], [], [], [], []
    for s in emitidas(LOGS / f"{perfil}.log.txt"):
        if m := ERROR_MMGR.search(s):
            mmgr.append(f"{m['src'].split('/')[-1]}:{m['line']}:{m['fn']}:{m['code']}")
        if m := IFO_ERR.search(s):
            ifo.append(f"{m['src'].split('/')[-1]}:{m['line']}:{m['cod']}")
        if m := XAVC_ERR.search(s):
            xavc.append(f"{m['src'].split('/')[-1]}:{m['line']}:{m['cod']}")
        if m := AVISEQ.search(s):
            aviseq.append(f"{m['mod']}:{m['cod']}")
        if m := AVIMMGR.search(s):
            txt.append(m["msg"].strip())
    return (
        sorted(set(mmgr)),
        sorted(set(aviseq)),
        sorted(set(ifo)),
        sorted(set(xavc)),
        sorted(set(txt)),
    )


def agujas(perfil: str):
    ruta = LOGS / f"{perfil}.agujas.tsv"
    if not ruta.exists():
        return {}
    return {l.split("\t")[0]: int(l.split("\t")[1]) for l in ruta.read_text().splitlines() if "\t" in l}


def clave(mmgr, aviseq, ifo, xavc, txt):
    """Agrupa por el CONJUNTO de codigos que aparecen (no por orden)."""
    mods = tuple(sorted({x.rsplit(":", 1)[1] for x in mmgr}))
    ifos = tuple(sorted({x.rsplit(":", 1)[1] for x in ifo + xavc}))
    return mods, ifos, tuple(sorted(set(aviseq)))


def main() -> None:
    perfiles = sorted(p.name[: -len(".log.txt")] for p in LOGS.glob("*.log.txt"))
    datos = {}
    for p in perfiles:
        mmgr, aviseq, ifo, xavc, txt = firma(p)
        datos[p] = {
            "mmgr": mmgr,
            "aviseq": aviseq,
            "ifo": ifo,
            "xavc": xavc,
            "txt": txt,
            "agujas": agujas(p),
            "zst_mb": round((LIVE / p / "estado.zst").stat().st_size / 1e6, 1)
            if (LIVE / p / "estado.zst").exists()
            else "",
        }

    grupos = defaultdict(list)
    for p, d in datos.items():
        grupos[clave(d["mmgr"], d["aviseq"], d["ifo"], d["xavc"], d["txt"])].append(p)

    with open(LOGS / "index.tsv", "w", encoding="utf-8") as fh:
        fh.write("perfil\tzst_mb\tintento_ifo\tcodigos_ifo\tmmgr_codigos\taviseq\tavimmgr\tagujas_err\tagujas_ok\n")
        for p, d in datos.items():
            ifos = sorted({x.rsplit(":", 1)[1] for x in d["ifo"] + d["xavc"]})
            mm = sorted({x.rsplit(":", 1)[1] for x in d["mmgr"]})
            a = d["agujas"]
            ok = " ".join(f"{k[:18]}={v}" for k, v in a.items() if "OK" in k or "Success" in k or "Completed" in k)
            err = " ".join(f"{k[:18]}={v}" for k, v in a.items() if "Error" in k or "ErrCd" in k or "faild" in k)
            fh.write(
                f"{p}\t{d['zst_mb']}\t{'SI' if ifos else 'NO'}\t{' '.join(ifos) or '—'}\t"
                f"{' '.join(mm) or '—'}\t{' '.join(d['aviseq']) or '—'}\t{' | '.join(d['txt']) or '—'}\t{err}\t{ok}\n"
            )

    with open(LOGS / "firmas.md", "w", encoding="utf-8") as fh:
        fh.write("# Firmas de la ruta de video por perfil (arnes, 215 estado.zst)\n\n")
        fh.write(f"Perfiles con log: {len(datos)}\n\n")
        orden = sorted(grupos.items(), key=lambda kv: -len(kv[1]))
        for i, ((mods, ifos, avis), ps) in enumerate(orden, 1):
            fh.write(f"## Firma {i} — {len(ps)} perfiles\n\n")
            fh.write(f"- codigos MMGR: {', '.join(mods) or '—'}\n")
            fh.write(f"- codigos IFO: {', '.join(ifos) or '—'}\n")
            fh.write(f"- AviSeq*: {', '.join(avis) or '—'}\n")
            fh.write(f"- perfiles: {', '.join('`%s`' % x for x in ps[:40])}")
            fh.write(f" (+{len(ps) - 40} mas)\n\n" if len(ps) > 40 else "\n\n")

    # resumen
    sin = [p for p, d in datos.items() if not d["ifo"] and not d["xavc"]]
    con = [p for p, d in datos.items() if d["ifo"] or d["xavc"]]
    print(f"perfiles con log: {len(datos)}")
    print(f"con intento de IFO (codigo de fallo): {len(con)}")
    print(f"sin intento de IFO: {len(sin)}")
    print(f"firmas distintas: {len(grupos)}")
    todos_ok = Counter()
    for d in datos.values():
        for k, v in d["agujas"].items():
            todos_ok[(k, v)] += 1
    print("\n=== valores de 'agujas OK' (constante = literal .rodata) ===")
    for (k, v), n in sorted(todos_ok.items()):
        if "OK" in k or "Success" in k or "Completed" in k:
            print(f"  {k[:44]:46s} n={v:<3d} en {n} perfiles")
    print("\n=== agujas de error (variacion = emitidas) ===")
    for (k, v), n in sorted(todos_ok.items()):
        if "Error" in k or "ErrCd" in k or "faild" in k:
            print(f"  {k[:44]:46s} n={v:<3d} en {n} perfiles")


if __name__ == "__main__":
    main()
