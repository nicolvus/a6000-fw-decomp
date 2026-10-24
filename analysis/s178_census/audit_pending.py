"""Inventario reproducible; nunca infiere cobertura a partir de menciones."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

BASE = 0x43541000
PAT = re.compile(rb"\[[A-Z][A-Z0-9_]{1,24}\]")
BINARY = "analysis/rea-independent/input/av-cam.bin"
PIC = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
DIRECT = {"[IMAGING_IMG]", "[SFR]", "[EXL]", "[SYS_SENSER_CA_PUTS]"}
RELATED = {"[CMDMLTSYNC]", "[SYNCENCSTART]", "[SYNCSETMODE]", "[EVF]",
           "[PANELEVF]", "[PNLEVF]", "[VSYNC]", "[SDF_ERR]"}


def priority(tag, referenced):
    """Relación léxica con captura primero; no es una conclusión funcional."""
    tier = 0 if tag.startswith("[MODE_CAP") or tag in DIRECT else 1 if tag in RELATED else 2
    return tier, -referenced, tag


def occurrences(data, tags, refs):
    rows = {tag: [] for tag in tags}
    for match in PAT.finditer(data):
        tag = match.group().decode("ascii")
        if tag not in tags:
            continue
        start = match.start()
        while start and 32 <= data[start - 1] < 127:
            start -= 1
        end = data.find(b"\0", match.end())
        if end < 0:
            end = len(data)
        address = hex(BASE + start)
        rows[tag].append({
            "token_vaddr": hex(BASE + match.start()), "token_offset": match.start(),
            "cadena_vaddr": address, "cadena_offset": start,
            "texto_hasta_nul_latin1": data[start:end].decode("latin1"),
            "referencias_pic_candidatas": [hex(x) for x in refs.get(address, [])],
        })
    return rows


def classification(tag, decisions):
    return decisions.get(tag, {
        "veredicto": "NO_VERIFICADO", "examinada": False,
        "motivo": "Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo.",
        "fuente_evidencia": [],
    })


def build(root):
    paths = [BINARY, PIC, "analysis/s178_census/census_detalle.json",
             "analysis/s178_census/decisiones_auditoria.json",
             "analysis/s178_census/evidencia_bytes.json",
             "analysis/s178_census/funciones_historicas.json",
             "analysis/s178_census/rea_intento.json",
             "analysis/s178_census/llvm_instrucciones.json"]
    contents = {path: (root / path).read_bytes() for path in paths}
    detail = json.loads(contents[paths[2]])
    decisions = json.loads(contents[paths[3]])
    tags = {tag for tag, row in detail.items() if row["estado"] in {"pendiente", "no-modulo"}}
    found = occurrences(contents[BINARY], tags, json.loads(contents[PIC]))
    counts = {tag: len({occ["cadena_vaddr"] for occ in items
                        if occ["referencias_pic_candidatas"]}) for tag, items in found.items()}
    rows = []
    for tag in sorted(tags, key=lambda t: priority(t, counts[t])):
        row = detail[tag]
        rows.append({"etiqueta": tag, "estado_censo": row["estado"],
                     "prioridad": priority(tag, row["cadenas_referenciadas"])[0],
                     "cadenas_con_pic_candidato": counts[tag],
                     "cadenas_referenciadas_censo": row["cadenas_referenciadas"],
                     **classification(tag, decisions), "ocurrencias": found[tag]})
    return {
        "fuentes_sha256": {path: hashlib.sha256(data).hexdigest() for path, data in contents.items()},
        "base_vaddr": hex(BASE),
        "limites": "PIC histórico heurístico, sin prueba de flujo ni de ausencia. Prioridad léxica manual, no semántica demostrada. Cadenas latin1 hasta NUL; inicio ASCII según el mapa original.",
        "antes": {"hito": 94, "sub-etiqueta": 39, "pendiente": 239, "no-modulo": 0},
        "despues": dict(Counter(row["estado"] for row in detail.values())),
        "veredictos": dict(Counter(row["veredicto"] for row in rows)),
        "etiquetas": rows,
    }


def markdown(result):
    text = ["# S178 — inventario de etiquetas pendientes y descartadas", "",
            ("Generado por `audit_pending.py`; direcciones, textos completos y referencias por ocurrencia en "
            "[pendientes_auditados.json](pendientes_auditados.json). "
            "Prioridad 0: captura/sensor; 1: sincronización/visor; 2: resto. "
            "Dentro de cada grupo: cadenas contenedoras con PIC candidato descendentes y etiqueta. "
            "La prioridad expresa una hipótesis de selección, no identidad funcional."), "",
            ("ACEPTO acepta un candidato a módulo; no cierra su decodificación. "
            "RECHAZO se contabiliza fuera de cobertura. NO_VERIFICADO conserva la investigación abierta. "
            "Las referencias PIC son candidatas hasta contrastar instrucciones y pools."), "",
            "| Etiqueta | Prioridad | Cadenas contenedoras con PIC candidato | Candidato | Estado | Motivo |",
            "|---|---:|---:|---|---|---|"]
    for row in result["etiquetas"]:
        text.append(f"| `{row['etiqueta']}` | {row['prioridad']} | "
                    f"{row['cadenas_con_pic_candidato']} | {row['veredicto']} | "
                    f"{row['estado_censo']} | {row['motivo']} |")
    return "\n".join(text) + "\n"


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    result = build(root)
    folder = root / "analysis/s178_census"
    (folder / "pendientes_auditados.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (folder / "pendientes.md").write_text(markdown(result), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("antes", "despues", "veredictos")}))
