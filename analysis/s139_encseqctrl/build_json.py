#!/usr/bin/env python3
"""S139 — construye `analysis/s139_encseqctrl/encseqctrl.json` a partir de:
  * `analysis/s106_imaging_cap/pic_refs_strict_global.json` (mapa PIC, regla estricta),
  * `encseqctrl_raw.json` (cadenas, sitios, funciones, diferencial),
  * `line_numbers.py` (nº de línea del .cpp por traza),
  * desensamblado puntual (tabla de ids de mensaje, tabla O/U Crank).

Salida: analysis/s139_encseqctrl/encseqctrl.json
"""
import bisect
import importlib.util
import json
import os
import struct
import sys

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
G = json.load(open(os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")))
RAW = json.load(open(os.path.join(HERE, "encseqctrl_raw.json")))

spec = importlib.util.spec_from_file_location("ln", os.path.join(HERE, "line_numbers.py"))
ln = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ln)

FILE_STR = 0x43C4BD0F
MOD_ID = 0x0E


def cstr(va):
    o = va - BASE
    e = B.find(b"\0", o)
    return B[o:e].decode("latin1")


def prologues():
    out = []
    a = 0x43541000
    while a < 0x43A00000:
        h = struct.unpack_from("<H", B, a - BASE)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = struct.unpack_from("<H", B, a - BASE + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


P = prologues()


def fstart(site):
    i = bisect.bisect_right(P, site) - 1
    return P[i] if i >= 0 else None


def main():
    # 1) identificar método y fichero de cada función del módulo
    inv = {}
    for dest, sites in G.items():
        for s in sites:
            inv.setdefault(s, []).append(int(dest, 16))
    funciones = {}
    for f, v in RAW["funciones"].items():
        fs = int(f, 16)
        nxt = bisect.bisect_right(P, fs)
        fend = P[nxt] if nxt < len(P) else fs + 0x1000
        strs = {}
        for s, dests in inv.items():
            if fs <= s < fend:
                for d in dests:
                    strs.setdefault(d, []).append(s)
        metodo = None
        fichero = None
        for d in sorted(strs):
            t = cstr(d)
            if metodo is None and "::" in t and t[:1].isupper():
                metodo = {"vaddr": hex(d), "texto": t}
            if fichero is None and t.endswith(".cpp"):
                fichero = {"vaddr": hex(d), "texto": t}
        e = dict(v)
        e["metodo"] = metodo
        e["fichero"] = fichero
        funciones[f] = e

    # 2) números de línea por traza

    import subprocess
    out = subprocess.run([sys.executable, os.path.join(HERE, "line_numbers.py")],
                         capture_output=True, text=True)
    ln_rows = json.loads(out.stdout)
    lineas = {}
    for r in ln_rows:
        if r["line"] is not None:
            lineas.setdefault(r["fmt"], []).append({"line": r["line"],
                                                     "log_call": r["log_call"],
                                                     "fn": r["fn"]})

    # 3) tabla de ids de mensaje (ProcAvcMsg)
    tbh = 0x435D8D4C
    base = tbh + 4
    msgids = []
    nombres = {
        0x8101: "MSGID_AVC_ENC_VIDEO_OPEN_COMP",
        0x8102: "MSGID_AVC_ENC_VIDEO_CLOSE_COMP",
        0x8103: "MSGID_AVC_ENC_VIDEO_INITIALIZE_MOVIE_COMP",
        0x8104: "MSGID_AVC_ENC_VIDEO_INITIALIZE_STILL_COMP",
        0x8105: "MSGID_AVC_ENC_VIDEO_ENC_PICTURE_COMP",
        0x8106: "MSGID_AVC_ENC_VIDEO_ENC_FINAL_PICTURE_COMP",
        0x8107: "MSGID_AVC_ENC_VIDEO_FINALIZE_COMP",
        0x8108: "MSGID_AVC_ENC_VIDEO_RELEASE_ES_COMP",
        0x8111: "MSGID_AVC_ENC_VIDEO_RELEASE_PICTURE_NOTIFY",
        0x8112: "MSGID_AVC_ENC_VIDEO_GET_ES_NOTIFY",
        0x8109: "MSGID_AVC_ENC_VIDEO_SET_MOVIE_QUALITY_INFO_COMP",
        0x810A: "MSGID_AVC_ENC_VIDEO_SET_FACE_INFO_COMP",
    }
    # posiciones de las cadenas de nombre dentro de la función
    det = {d["sitio"]: d for d in RAW["funciones"]["0x435d8d38"]["detalle"]}
    for i in range(18):
        hwv = struct.unpack_from("<H", B, base + 2 * i - BASE)[0]
        tgt = base + 2 * hwv
        mid = 0x8101 + i
        # la cadena cuyo sitio cae en [tgt, siguiente destino)
        nxt = None
        for j in range(18):
            if j == i:
                continue
            hw2 = struct.unpack_from("<H", B, base + 2 * j - BASE)[0]
            t2 = base + 2 * hw2
            if t2 > tgt and (nxt is None or t2 < nxt):
                nxt = t2
        cand = [s for s in det if tgt <= int(s, 16) < (nxt or 0xFFFFFFFF)]
        nom = None
        for s in cand:
            t = det[s]["texto"]
            if "MSGID_AVC_ENC_VIDEO" in t:
                nom = t.split("]")[1].split()[0]
        msgids.append({"msgid": hex(mid), "tbh_destino": hex(tgt),
                       "nombre": nom, "nombre_esperado": nombres.get(mid),
                       "cadena": det[cand[0]]["cadena"] if cand else None,
                       "sitio": cand[0] if cand else None})

    # 4) tabla O/U Crank (57 entradas × 8 B)
    tab = 0x43B93BF4
    oucrank = []
    for i in range(57):
        o = tab + 8 * i - BASE
        f0, f4 = struct.unpack_from("<II", B, o)
        oucrank.append({"idx": i, "vaddr": hex(tab + 8 * i), "f0": f0, "f0_hex": hex(f0),
                        "u32_4": f4, "byte_4": f4 & 0xFF, "byte_5": B[o + 5]})

    # 5) estados observados (valores pasados al setter de estado 0x435d715c)
    estados = {
        "campo_estado_offset": "0x15B84",
        "setter": "0x435d715c",
        "nota": "u32 en [obj+0x15B84]; el setter lo escribe y lo anuncia con "
                "[ENCSEQCTRL][state]0x%x -> 0x%x (0x43c4bda2)",
    }

    out = {
        "hito": "S139",
        "token": "[ENCSEQCTRL]",
        "firmware": {"modelo": "A6000", "version": "fw3.21",
                     "binario": "analysis/rea-independent/input/av-cam.bin",
                     "convencion": "vaddr = 0x43541000 + file_offset"},
        "clase": {"nombre": "McAvcEncSeqCtrl", "vaddr": "0x43c4320f",
                  "fichero": "seqCtrl/mcAvcEncSeqCtrl.cpp", "vaddr_fichero": "0x43c4bd0f",
                  "componente": "Avbb-MovieCodec_131H (ruta de build 0x43c41227)"},
        "sigla": {"desarrollo": None,
                  "nota": "no hay base textual para desarrollar ENCSEQCTRL; "
                          "la clase de RTTI es McAvcEncSeqCtrl (Mc=MovieCodec, "
                          "Avc=AVC/H.264, Enc=encoder, SeqCtrl=sequence control)"},
        "totales": RAW["totales"],
        "regla_pic": "estricta (analysis/s106_imaging_cap/scan_pic_refs_strict.py, "
                     "mapa global pic_refs_strict_global.json)",
        "id_modulo_log": "0x0e (movs r1,#0xe en todas las llamadas al logger)",
        "cadenas": [],
        "sub_bloques": RAW["sub_bloques"],
        "funciones": funciones,
        "tabla_msgids": msgids,
        "tabla_ouc_rank": {"vaddr": hex(tab), "entradas": 57, "bytes_por_entrada": 8,
                           "entradas_completas": oucrank},
        "estados": estados,
        "numeros_de_linea_fuente": lineas,
        "rtti_clases": RAW["rtti_clases"],
        "ficheros_fuente": RAW["ficheros_fuente"],
        "diferencial": RAW["diferencial"],
    }

    for c in RAW["cadenas"]:
        va = c["vaddr"]
        out["cadenas"].append({
            "vaddr": va,
            "texto": c["texto"],
            "sub_bloque": c["sub_bloque"],
            "sitios": RAW["sitios"].get(va, []),
            "funciones": sorted({hex(fstart(int(s, 16)))
                                 for s in RAW["sitios"].get(va, [])}, key=lambda x: int(x, 16)),
            "lineas_fuente": sorted({x["line"] for x in lineas.get(va, [])}),
        })

    with open(os.path.join(HERE, "encseqctrl.json"), "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps(out["totales"], indent=1))
    print("lineas recuperadas:", sum(len(v) for v in lineas.values()),
          "en", len(lineas), "cadenas")
    print("msgids con nombre:", sum(1 for m in msgids if m["nombre"]))


if __name__ == "__main__":
    main()
