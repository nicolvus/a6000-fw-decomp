"""D4: resuelve las 86 filas VIGENTE del triaje S400 con casos razonados y evidencia con hash.

Dos fases (la revisión del destino debe existir en Git antes de fijarla en las filas):
  python d4_resolve.py avisos        # añade el aviso D4 a los destinos con lectura rectificada
  python d4_resolve.py resolver REV  # REV = commit que contiene los avisos
Los avisos evitan las palabras que el grafo lee como corrección, para no crear aristas nuevas."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CAP = "docs/capture/"
MARK = "**Aviso D4 (25-10-2026):**"

AVISOS = {
    "s130-new-modules": "[S170](../../analysis/s170_illumi/illumi.md) rectifica la lectura de `[ILLUMI]` como contenido nuevo: el subsistema de iluminación tiene las mismas RTTI en los tres modelos; lo propio de la A6000 son las trazas. Que sea el mismo código en los tres sigue NO_VERIFICADO.",
    "s41-message-origin-imx210": "[S42](s42-exposure-call-identity.md) rectifica la nomenclatura de «propagación de valores» y «Línea C»: `0x436d6320` es el wrapper de despacho y `0x436d6f6c` el método virtual del backend IMX210; no son alias.",
    "s46-vd-base-and-context-identity": "[S47](s47-payload-producer-and-order.md) cierra el pendiente de orden: si el callback se ejecuta en esa invocación, escribe antes de la copia (no se recertifica un orden universal).",
    "s57-imx235-silent-register-diff": "[S58](s58-a7s-silent-effective-diff.md) reemplaza esta comparación: la matriz tiene 69 filas de 0x14 B con selección indirecta de 15 columnas, no 35 filas de 40 B con 34 columnas directas; los pares `0x000C` y `0x000A` de aquí proceden de esa lectura.",
    "s57-ssb-pulse-analysis": "[S58](s58-conclusions.md) retira la lectura del umbral `0x1000` como condición de exposición: pertenece a SetRead/AGC (SetExposure A7S `0x436f4168`, SetRead `0x436f4a94`).",
    "s58-ae-timing-producers": "[S59 SOL-07](s59-sol.md) rectifica la atribución de clk del §5: el mismo offset `+0x4c0` no demuestra alias; el escritor de histogramas recibe el objeto `0x43eb121c` y la entrada AE P `0x43eaee84`.",
    "s309-chain-presence": "[S310](s310-vtable-thunk.md) rectifica el mecanismo: `0x43ad96fa`/`0x43ad9704` son thunks de llamada virtual, no un constructor de mensajes.",
    "s310-vtable-thunk": "[S314](s314-selector-object.md) rectifica este informe: `0x43ad9704` no es el thunk del slot `0x64` (lo es `0x43ad96f8`) y va a `0x43ad9ada` (`vtable+0x24`).",
    "s313-synthesis-carril-b": "[S314](s314-selector-object.md) rectifica la fila 13 (slot `0x64`) y [S341 §4](s341-synthesis-b2.md) enumera las rectificaciones posteriores del carril B; esta síntesis no las incorpora.",
    "s302-drive-modes": "[S321](s321-matrix-rows.md) rectifica «cabecera = puntero a descriptor» (es el destino de escritura del valor) y [S325](s325-position-map.md) el mapa de columnas (posición→columna de 34 entradas, no modo→columna de 82).",
    "s321-mode-matrix": "[S325](s325-position-map.md) y [S329](s329-mode-timing-tables.md) retiran «`0x4e`/`0x4f` comparten la columna 1»: el mapa es posición→columna y `0x4e`→columna 12, `0x4f`→13.",
    "s321-matrix-rows": "[S325](s325-position-map.md) y [S329](s329-mode-timing-tables.md) retiran «`0x4c`–`0x4f` → columna 1» y el mapa de 82 B por código: el mapa es posición→columna de 34 entradas.",
    "s334-pair-dataflow": "[S340](s340-w0-selector.md) rectifica `w0` como «código de operación»: es un selector de canal MMIO (`0x436f74c0`).",
    "s304-rea-dumper-callers": "[S303 §5](s303-ref-tree-43ff3200.md) rectifica las direcciones de la rev.1 usadas aquí: `0x438581e8` y `0x43858390` eran entradas reales +0x58 (`0x43858190` y `0x43858338`).",
}

COR = "CORRECCION_APLICADA"
FP = "FALSO_POSITIVO"
CASOS = {
    "d4-s116": (COR, "El destino ya lleva las cifras de la regla actual (117 cadenas, 131 puntos, 52 funciones) y sfrs.md §156 describe la regla laxa retirada; el script aborta si una cadena o sitio queda sin atribuir.",
                [("analysis/s116_sfrs/sfrs.md", "156:160"), (CAP + "s116-sfrs.md", "13:14")]),
    "d4-s307": (COR, "S308 §2 retira la entrada del bloque de tiempos de S307 (`0x438645bc`, prólogo decodificado) y S307 ya recoge la entrada real en su texto.",
                [(CAP + "s308-silent-flow.md", "27:30"), (CAP + "s307-a7s-only-writers.md", "39:40")]),
    "d4-s60": (COR, "S60 ya declara la base TBH rectificada (`…c28`/`…d06`) y S61 la cierra con base PC `0x43806a08`, script y test.",
               [(CAP + "s60-conclusions.md", "7:7"), (CAP + "s61-conclusions.md", "7:7")]),
    "d4-s130": (COR, "S170 retira la lectura de ILLUMI como contenido nuevo (mismas RTTI en tres modelos; propio de A6000 son las trazas). La equivalencia de código sigue NO_VERIFICADO. El destino lleva aviso.",
                [("analysis/s170_illumi/illumi.md", "38:41")]),
    "d4-s41": (COR, "S42 separa wrapper `0x436d6320` y método de backend `0x436d6f6c` y retira la nomenclatura de S41. El destino lleva aviso; no se recertifica el objeto/vtable.",
               [(CAP + "s42-exposure-call-identity.md", "34:40")]),
    "d4-s46": (COR, "S47 cierra el pendiente de orden de S46 bajo la condición de que el callback se ejecute en esa invocación; no recertifica un orden universal. El destino lleva aviso.",
               [(CAP + "s47-payload-producer-and-order.md", "100:105")]),
    "d4-s57-matriz": (COR, "S58 reemplaza la comparación de S57-D: 69 filas de 0x14 B y 15 columnas con selección indirecta; los pares 0x000C/0x000A procedían de leer 35 filas de 40 B. El destino lleva aviso.",
                      [(CAP + "s58-a7s-silent-effective-diff.md", "5:8"), (CAP + "s58-conclusions.md", "15:15")]),
    "d4-s57-umbral": (COR, "S58 atribuye el umbral 0x1000 a SetRead/AGC y no a la exposición (vtable y ejecución independientes). El destino lleva aviso.",
                      [(CAP + "s58-conclusions.md", "14:14")]),
    "d4-s58-clk": (COR, "S59 SOL-07 separa los objetos `0x43eb121c` y `0x43eaee84` y retira el alias de clk de S58-A §5; la prueba `test_histogram_writer_has_a_different_object` pasa. El destino lleva aviso.",
                   [(CAP + "s59-sol.md", "28:28")]),
    "d4-s309": (COR, "S310 desensambla `0x43ad96fa`/`0x43ad9704` y los identifica como thunks de llamada virtual, no constructor de mensajes (S309 fila 3). El destino lleva aviso; el consumidor del modo sigue NO_VERIFICADO.",
                [(CAP + "s310-vtable-thunk.md", "1:6")]),
    "d4-s310": (COR, "S314 retira que `0x43ad9704` sea el thunk del slot 0x64 (lo es `0x43ad96f8`); la tabla de bytes está en S314. El destino lleva aviso.",
                [(CAP + "s314-selector-object.md", "47:53")]),
    "d4-s313": (COR, "S314 retira la fila 13 de S313 (slot 0x64) y S341 §4 enumera las rectificaciones del carril B que S313 no incorpora. El destino lleva aviso.",
                [(CAP + "s314-selector-object.md", "49:52"), (CAP + "s341-synthesis-b2.md", "44:52")]),
    "d4-s302": (COR, "S321 retira «cabecera = puntero a descriptor» (es el destino de escritura) y S325 el mapa modo→columna de 82 B (es posición→columna de 34). El destino lleva aviso.",
                [(CAP + "s321-matrix-rows.md", "60:63"), (CAP + "s325-position-map.md", "7:10")]),
    "d4-s321m": (COR, "S325/S329 retiran el «comparte columna 1»: `0x4e`→columna 12 y `0x4f`→13 por posición; S341 §4 lo recoge. El destino lleva aviso.",
                 [(CAP + "s325-position-map.md", "7:10"), (CAP + "s341-synthesis-b2.md", "46:47")]),
    "d4-s321r": (COR, "S325/S329 retiran el mapa de 82 B por código y el «columna 1» de `0x4c`–`0x4f`; el mapa es posición→columna. El destino lleva aviso.",
                 [(CAP + "s325-position-map.md", "7:10"), (CAP + "s341-synthesis-b2.md", "46:47")]),
    "d4-s334": (COR, "S340 identifica `w0` como selector de canal MMIO y retira «código de operación» de S334. El destino lleva aviso.",
                [(CAP + "s340-w0-selector.md", "7:7"), (CAP + "s340-w0-selector.md", "16:17")]),
    "d4-s304": (COR, "S303 §5 muestra por bytes que `0x438581e8`/`0x43858390` eran interiores (+0x58) de `0x43858190`/`0x43858338`; S304 usa esas direcciones. El destino lleva aviso.",
                [(CAP + "s303-ref-tree-43ff3200.md", "106:116")]),
    "d4-auditoria": (COR, "Los cinco informes destino declaran al inicio que la auditoría S605–S627 rectifica sus conclusiones históricas, y la tabla de hallazgos enumera las rectificaciones concretas (13 omisiones, 21 núcleos, gemelas S606, prefijo `[ADR]` de S625). No se certifica el logger dual ni las equivalencias.",
                     [(CAP + "S605-S627_tabla_hallazgos.md", "34:41"), (CAP + "S605-S627_tabla_hallazgos.md", "74:74")]
                     + [(CAP + f"{n}.md", "3:3") for n in ("s605-jpeg", "s607-cam_cmd", "s616-lens_pdr", "s625-adr", "s627-eo_sw")]),
    "d4-resumen": (FP, "La línea es un resumen acumulado (README, STATE o checkpoint del carril B) que lista varias sesiones. Las rectificaciones concretas se juzgan en las filas de cada documento corrector; este destino no es el sujeto de la cita.", []),
    "d4-ausente": (FP, "La rectificación citada se refiere a una lectura que este destino no contiene (otra tabla, otro informe o una consulta del propio autor). Si otro documento la sostiene, la arista correcta apunta allí.", []),
}
RESUMEN, AUSENTE = "d4-resumen", "d4-ausente"
INV, ADY, NEG = "procedencia-invertida", "adyacencia", "negacion"
FILAS = {
    17: "d4-s116", 23: "d4-s130", 48: AUSENTE, 398: AUSENTE, 95: "d4-s41", 97: "d4-s46",
    107: "d4-s57-matriz", 112: "d4-s57-matriz", 109: "d4-s57-umbral", 116: "d4-s58-clk",
    137: INV, 139: INV, 284: INV, 286: INV, 140: ADY, 287: ADY,
    143: INV, 290: INV, 144: "d4-s309", 292: "d4-s309", 146: INV, 293: INV,
    148: "d4-s313", 294: "d4-s313", 257: "d4-s313", 270: "d4-s313",
    149: INV, 150: INV, 296: INV, 297: INV, 191: INV, 192: INV,
    154: AUSENTE, 300: AUSENTE, 158: AUSENTE, 306: AUSENTE, 258: AUSENTE, 260: AUSENTE, 500: AUSENTE,
    155: "d4-s302", 302: "d4-s302", 259: "d4-s302",
    156: "d4-s321m", 304: "d4-s321m", 157: "d4-s321r", 303: "d4-s321r",
    173: RESUMEN, 174: RESUMEN, 318: RESUMEN, 321: RESUMEN, 179: RESUMEN, 181: RESUMEN,
    324: RESUMEN, 327: RESUMEN, 348: RESUMEN, 353: RESUMEN, 378: RESUMEN, 379: RESUMEN,
    215: RESUMEN, 217: RESUMEN, 218: RESUMEN,
    213: "d4-s334", 249: NEG, 250: "d4-s304", 252: "d4-s307", 255: INV, 256: "d4-s310", 499: "d4-s60",
}
AUDITORIA = {390, 391, 392, 448, 449, 450, 455, 456, 458, 461, 462, 463, 464, 472, 473, 474, 475, 476}
FILAS.update({i: "d4-auditoria" for i in AUDITORIA})
CON_AVISO = {"d4-s130", "d4-s41", "d4-s46", "d4-s57-matriz", "d4-s57-umbral", "d4-s58-clk", "d4-s309",
             "d4-s310", "d4-s313", "d4-s302", "d4-s321m", "d4-s321r", "d4-s334", "d4-s304"}
AVISO_DE = {"d4-s130": "s130-new-modules", "d4-s41": "s41-message-origin-imx210",
            "d4-s46": "s46-vd-base-and-context-identity", "d4-s57-matriz": "s57-imx235-silent-register-diff",
            "d4-s57-umbral": "s57-ssb-pulse-analysis", "d4-s58-clk": "s58-ae-timing-producers",
            "d4-s309": "s309-chain-presence", "d4-s310": "s310-vtable-thunk", "d4-s313": "s313-synthesis-carril-b",
            "d4-s302": "s302-drive-modes", "d4-s321m": "s321-mode-matrix", "d4-s321r": "s321-matrix-rows",
            "d4-s334": "s334-pair-dataflow", "d4-s304": "s304-rea-dumper-callers"}


def avisos() -> None:
    for name, text in AVISOS.items():
        path = ROOT / CAP / f"{name}.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        if any(MARK in line for line in lines[:12]):
            continue
        lines[1:1] = ["", f"> {MARK} {text}"]
        if len(lines) > 3 and lines[3].strip():
            lines.insert(3, "")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def evidencia(archivo: str, rango: str) -> dict:
    raw = (ROOT / archivo).read_bytes()
    a, b = map(int, rango.split(":"))
    return {"archivo": archivo, "localizador": rango,
            "cita": "\n".join(raw.decode().splitlines()[a - 1:b]), "sha256": hashlib.sha256(raw).hexdigest()}


def aviso_evidencia(name: str) -> dict:
    lines = (ROOT / CAP / f"{name}.md").read_text(encoding="utf-8").splitlines()
    n = next(i for i, line in enumerate(lines, 1) if MARK in line)
    return evidencia(CAP + f"{name}.md", f"{n}:{n}")


def resolver(revision: str) -> None:
    triage_path, review_path = HERE / "triage.json", HERE / "manual_review.json"
    rows, review = json.loads(triage_path.read_text()), json.loads(review_path.read_text())
    pendientes = {i for i, r in enumerate(rows) if r["veredicto"] == "VIGENTE"}
    assert pendientes == set(FILAS), sorted(pendientes ^ set(FILAS))
    for case in review["casos"].values():  # los avisos desplazan 3 líneas las citas posteriores a la cabecera
        for e in case["evidencias"]:
            if Path(e["archivo"]).stem in AVISOS and e["archivo"].startswith(CAP) and MARK not in e["cita"]:
                a, b = map(int, e["localizador"].split(":"))
                e.update(evidencia(e["archivo"], f"{a if a == 1 else a + 3}:{b + 3}"))
    for name, (verdict, razon, ev) in CASOS.items():
        evidencias = [evidencia(a, r) for a, r in ev]
        if name in AVISO_DE:
            evidencias.append(aviso_evidencia(AVISO_DE[name]))
        review["casos"][name] = {"veredicto": verdict, "razon": razon, "evidencias": evidencias}
    for i, name in FILAS.items():
        case = review["casos"][name]
        row = rows[i]
        row.update(veredicto=case["veredicto"], motivo=case["razon"], revision_manual=name)
        if name in AVISO_DE:
            row["revision_destino"] = revision
            row["destino_cita"] = "\n".join(subprocess.check_output(
                ["git", "show", f"{revision}:{row['destino']}"], cwd=ROOT, text=True).splitlines()[:12])
    review["alcance"] += " El 25-10-2026 (D4) se resolvieron las 86 filas VIGENTE restantes: ver los casos `d4-*`."
    triage_path.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    review_path.write_text(json.dumps(review, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    avisos() if sys.argv[1] == "avisos" else resolver(sys.argv[2])
