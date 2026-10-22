#!/usr/bin/env python3
"""S120 — datos estructurados del módulo `[IDT_OPD]` (A6000 fw3.21).

Genera `idt_opd.json` con:
  - las 274 trazas (vaddr, offset, texto, referencias, función),
  - el mapa función → traza (kill analysis de `scan_pic_refs_v2.py`),
  - los sub-bloques de la tabla de cadenas (rangos exactos),
  - las estructuras de bloque verificadas contra los bytes (IE / MAP / punteros),
  - el diferencial A7S fw3.20 y A6300 fw2.01 texto a texto.

Convención: vaddr = 0x43541000 + file_offset.
"""
import json
import os
import struct
import sys
from collections import defaultdict

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
A7S = os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                        "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                          "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = os.path.dirname(os.path.abspath(__file__))
PIC = "/tmp/opencode/pic_refs_v2.json"

# ---------------------------------------------------------------- sub-bloques
# Rangos exactos de la tabla de cadenas del módulo (contiguos en el binario).
SUBBLOCKS = [
    ("0x43cf11f9", "0x43cf1aa3", "driver_canal",
     "Mensajes del canal con el gestor de captura (SEND MESSAGE, Cap, FOPD, Split, AF, PBL)"),
    ("0x43cf1aa3", "0x43cf1d7d", "driver_modos",
     "Driver: overflow, traducción FRM, VATR-only, load_delay, ganancia, distorsión, display"),
    ("0x43cf1d7d", "0x43cf23af", "bloque_IE",
     "Bloque IE (IE_CCinit): punteros (ie_miniraw, backImgData, imgmap, ie_out, refmap) y "
     "metadatos (tar_num, isSpectRef, isMapOut, gains r/g/b, offset, tamaño, aspecto)"),
    ("0x43cf23af", "0x43cf2634", "bloque_LC",
     "Bloque LC: lc_miniraw, lc_out, lc_offset, lc_imgwidth/height/addnum, lc_aspect y semáforos"),
    ("0x43cf2634", "0x43cf2740", "RC_del_mapa",
     "MapWidthRC / MapHeightRC: cálculo del rectángulo de recorte del mapa"),
    ("0x43cf2740", "0x43cf292a", "params_sync",
     "Parámetros: CCinitParam (tras una tabla de 11 offsets en 0x43cf2740), "
     "ECinitParam, CCsyncParam, ECsyncParam, CCsyncRes, ECsyncRes"),
    ("0x43cf292a", "0x43cf2bb6", "umbrales_y_regiones",
     "umbrales de detección: kido_th, ratio_wak, sel_wak, sel_waku, sel_hist, sel_sum"),
    ("0x43cf2bb6", "0x43cf2d56", "bloque_MAP",
     "Bloque MAP: miniraw, shade_map, 4cmap, histmap, summap, out_opd_cc, out_opd_ec"),
    ("0x43cf2d56", "0x43cf2f5c", "geometria_MAP",
     "Geometría del bloque MAP: offset, imgwidth, imgheight, imgaddnum, aspect, "
     "x_size, y_size, x.sel, y.sel, x.span, y.span"),
    ("0x43cf2f5c", "0x43cf322c", "regiones_integracion",
     "Regiones de integración: intn, intWak, histWak, cwaku y límites de spec"),
    ("0x43cf322c", "0x43cf3306", "sync_y_4cmap",
     "Sincronización CC/EC (syncflg) y error de aspecto del 4cmap"),
    ("0x43cf3306", "0x43cf3588", "IDTSA",
     "Captura partida: GetIDTSA, cálculo de SplitIDTSA, Invalid Ch select"),
    ("0x43cf3588", "0x43cf37d6", "FRM_sync_async",
     "Tamaños de lectura FRM en modo síncrono (sync) y asíncrono (async)"),
    ("0x43cf37d6", "0x43cf3ec8", "DET_HIST_CAE_GLE",
     "DET / HIST / CAE / GLE: tamaños, bloques y puntos finales de las regiones de análisis"),
    ("0x43cf3ec8", "0x43cf4090", "VATR",
     "VATR: detector de varianza (det, gle, tamaño, modo, RAW size)"),
    ("0x43cf4090", "0x43cf431d", "miniRAW_y_debug",
     "miniRAW (dirección, tamaño) y extracción de información de depuración"),
    ("0x43cf431d", "0x43cf44e9", "tasas_y_AF_param",
     "Tasas: FRM rate, FOPD rate, parámetros de AF (pix/clk)"),
    ("0x43cf44e9", "0x43cf4545", "AF_param_async",
     "Parámetros de AF en modo asíncrono"),
    ("0x43cf4545", "0x43cf47f1", "volcado_de_punteros",
     "Volcado de los 18 punteros del bloque de mapas (4cmap, hmap, smap, ccout, ecout, "
     "shade, input, msain0/1, msaout, ieout, p_img_map, p_backImgData, ie_in, mapRC_in, "
     "lc_out, lc_in, refmap)"),
    ("0x43cf47f1", "0x43cf4907", "SGC_y_RefMap",
     "SGC (cambio de ganancia) y IE_RefMap nulo / miniRAW sin memoria"),
    ("0x43cf4907", "0x43cf4a85", "memoria_VATR",
     "Gestión de memoria del VATR (Get / Release / IsAlloc)"),
    ("0x43cf4a85", "0x43cf4d51", "semforos",
     "Semáforos: ec_sem, cc_sem, lc_sem, signals y overflow de EC/CC"),
    ("0x43cf4d51", "0x43cf4f35", "load_delay_y_pixclk",
     "load_delay, límite de pix/clk del VATR, conversión de FOPD rate"),
    ("0x43cf4f35", "0x43cf50ed", "Request_y_SyncRate",
     "Petición de AF/LC, conversión de tasa síncrona y asíncrona"),
    ("0x43cf50ed", "0x43cf5811", "modos_FRM_y_EE",
     "Modos FRM, máscaras, tamaños 0size y camino EE (end-to-end)"),
]

# ---------------------------------------------------------------- estructuras
# Verificadas desensamblando (ver `analysis/s120_idt_opd/block_fields.py`).
STRUCT_IE = {
    "descripcion": "bloque IE (IE_CCinit) validado en 0x439e80c8; base = puntero recibido "
                   "como arg0 (r0)",
    "funcion": "0x439e80c8",
    "campos": [
        {"offset": "0x00", "tipo": "u16", "campo": "tar_num"},
        {"offset": "0x0c", "tipo": "u8", "campo": "isSpectRef"},
        {"offset": "0x0d", "tipo": "u8", "campo": "isMapOut"},
        {"offset": "0x10", "tipo": "u32", "campo": "refmap (adrs)"},
        {"offset": "0x16", "tipo": "u16", "campo": "r.val.high"},
        {"offset": "0x18", "tipo": "u16", "campo": "r.val.low"},
        {"offset": "0x1c", "tipo": "u16", "campo": "g.val.high"},
        {"offset": "0x1e", "tipo": "u16", "campo": "g.val.low"},
        {"offset": "0x22", "tipo": "u16", "campo": "b.val.high"},
        {"offset": "0x24", "tipo": "u16", "campo": "b.val.low"},
        {"offset": "0x54", "tipo": "u32", "campo": "ie_miniraw (adrs)"},
        {"offset": "0x58", "tipo": "u32", "campo": "ie_offset"},
        {"offset": "0x5c", "tipo": "u16", "campo": "ie_imgwidth"},
        {"offset": "0x5e", "tipo": "u16", "campo": "ie_imgheight"},
        {"offset": "0x60", "tipo": "u16", "campo": "ie_imgaddnum"},
        {"offset": "0x62", "tipo": "u16", "campo": "ie_aspect"},
        {"offset": "0x70", "tipo": "u32", "campo": "ie_out (adrs)"},
        {"offset": "0x74", "tipo": "u32", "campo": "imgmap (adrs)"},
        {"offset": "0x78", "tipo": "u32", "campo": "backImgData (adrs)"},
    ],
}

STRUCT_MAP = {
    "descripcion": "bloque MAP validado en 0x439ee7e8 (arg0 = puntero al bloque); "
                   "los mismos offsets se ven en el volcado 0x439f85d4 (base global 0x43f41b30)",
    "funcion": "0x439ee7e8",
    "campos": [
        {"offset": "0x0c", "tipo": "u32", "campo": "miniraw (adrs)"},
        {"offset": "0x10", "tipo": "u32", "campo": "offset"},
        {"offset": "0x14", "tipo": "u16", "campo": "imgwidth"},
        {"offset": "0x16", "tipo": "u16", "campo": "imgheight"},
        {"offset": "0x18", "tipo": "u16", "campo": "imgaddnum"},
        {"offset": "0x1a", "tipo": "u16", "campo": "aspect"},
        {"offset": "0x28", "tipo": "u8", "campo": "x_size"},
        {"offset": "0x29", "tipo": "u8", "campo": "y_size"},
        {"offset": "0x2a", "tipo": "u16", "campo": "x.sel"},
        {"offset": "0x2c", "tipo": "u16", "campo": "x.span"},
        {"offset": "0x2e", "tipo": "u16", "campo": "y.sel"},
        {"offset": "0x30", "tipo": "u16", "campo": "y.span"},
        {"offset": "0x38", "tipo": "u32", "campo": "shade_map (adrs)"},
        {"offset": "0x3c", "tipo": "u32", "campo": "4cmap (adrs)"},
        {"offset": "0x40", "tipo": "u32", "campo": "histmap (adrs)"},
        {"offset": "0x44", "tipo": "u32", "campo": "summap (adrs)"},
        {"offset": "0x48", "tipo": "u32", "campo": "out_opd_cc (adrs)"},
        {"offset": "0x4c", "tipo": "u32", "campo": "out_opd_ec (adrs)"},
        {"offset": "0x54", "tipo": "u32", "campo": "input (adrs)"},
    ],
}

STRUCT_PUNTEROS = {
    "descripcion": "volcado de punteros 0x439f85d4: 18 punteros repartidos en 3 bloques "
                   "y 4 globales sueltos",
    "funcion": "0x439f85d4",
    "bloques": [
        {"base": "0x43f41b30", "campos": [
            {"offset": "0x38", "nombre": "shade"},
            {"offset": "0x3c", "nombre": "4cmap"},
            {"offset": "0x40", "nombre": "hmap"},
            {"offset": "0x44", "nombre": "smap"},
            {"offset": "0x48", "nombre": "ccout"},
            {"offset": "0x4c", "nombre": "ecout"},
            {"offset": "0x54", "nombre": "input"}]},
        {"base": "0x43f41cbc", "campos": [
            {"offset": "0x28", "nombre": "ieout"},
            {"offset": "0x2c", "nombre": "p_img_map"},
            {"offset": "0x30", "nombre": "p_backImgData"},
            {"offset": "0x38", "nombre": "ie_in"}]},
        {"base": "0x43f418a8", "campos": [
            {"offset": "0x28", "nombre": "lc_out"},
            {"offset": "0x30", "nombre": "lc_in"}]},
    ],
    "globales": [
        {"addr": "0x43f41bbc", "nombre": "msain0"},
        {"addr": "0x43f41ef0", "nombre": "msain1"},
        {"addr": "0x43f41ad8", "nombre": "msaout"},
        {"addr": "0x43f41f14", "nombre": "mapRC_in"},
        {"addr": "0x43f4189c", "nombre": "refmap"},
    ],
}


def u16(data, a):
    return struct.unpack_from("<H", data, a - BASE)[0]


def u32(data, a):
    return struct.unpack_from("<I", data, a - BASE)[0]


def cstr(data, a):
    o = a - BASE
    e = data.find(b"\x00", o)
    return data[o:e].decode("latin1")


def extract(data, prefix):
    out = []
    idx = 0
    p = prefix.encode()
    while True:
        i = data.find(p, idx)
        if i < 0:
            break
        idx = i + 1
        out.append((BASE + i, cstr(data, BASE + i)))
    return out


def prologues(data, lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(data) - 4:
            a += 2
            continue
        h = u16(data, a)
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = u16(data, a + 2)
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def main():
    data = open(BIN, "rb").read()
    refs = json.load(open(PIC))
    starts = prologues(data, 0x43541000, 0x43A00000)
    tr = extract(data, "[IDT_OPD]")

    # barrido PIC restringido al código del módulo (0x439d0000-0x43a09000): reproduce
    # exactamente el barrido global canónico (725 sitios) y además permite ejecutar la
    # kill analysis **real** (con `detail` activo y comparación correcta de registros).
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import scan_idt_code_pic as SC
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    allstarts = SC.string_starts(data, 0x0, 0xFFFFFFFF)
    scans = {}
    for etiqueta, detail in (("canonico", False), ("kill_corregido", True)):
        md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        md.detail = detail
        r = SC.scan(data, 0x439D0000, 0x43A09000, allstarts, md)
        scans[etiqueta] = {f"0x{k:x}": v for k, v in r.items()}

    # referencias
    by_str = defaultdict(list)
    for v, sites in refs.items():
        if v in {f"0x{a:x}" for a, _ in tr}:
            for s in sites:
                a = int(s) if not isinstance(s, str) else int(s, 16)
                cand = [x for x in starts if x <= a and a - x <= 0x4000]
                by_str[v].append({"site": f"0x{a:x}",
                                  "func": f"0x{cand[-1]:x}" if cand else None})

    # sub-bloque por rango
    def sub_of(v):
        a = int(v, 16)
        for lo, hi, name, desc in SUBBLOCKS:
            if int(lo, 16) <= a < int(hi, 16):
                return name, desc
        return "(fuera)", "(fuera de los rangos)"

    strings = []
    for a, t in tr:
        v = f"0x{a:x}"
        name, desc = sub_of(v)
        strings.append({"vaddr": v, "off": a - BASE, "text": t,
                        "submodule": name, "submodule_desc": desc,
                        "refs": by_str.get(v, []),
                        "n_refs": len(by_str.get(v, []))})

    funcs = defaultdict(list)
    for s in strings:
        for r in s["refs"]:
            if r["func"]:
                funcs[r["func"]].append(s["vaddr"])

    # diferencial
    a7s = open(A7S, "rb").read()
    a63 = open(A6300, "rb").read()
    a7s_idt = extract(a7s, "[IDT]")
    a63_idt = extract(a63, "[IDT]")
    core6 = {t[len("[IDT_OPD]"):]: f"0x{a:x}" for a, t in tr}
    core7 = {t[len("[IDT]"):]: f"0x{a:x}" for a, t in a7s_idt}
    core63 = {t[len("[IDT]"):]: f"0x{a:x}" for a, t in a63_idt}

    # gemelos [IDT] contiguos
    gemelos = []
    for a, t in tr:
        core = t[len("[IDT_OPD]"):]
        twin = a + len("[IDT_OPD]") + len(core) + 1
        if twin < BASE + len(data) and cstr(data, twin) == "[IDT]" + core:
            gemelos.append({"idt_opd": f"0x{a:x}", "idt": f"0x{twin:x}",
                             "core": core})

    dead = [s["vaddr"] for s in strings if s["n_refs"] == 0]
    trset = {f"0x{a:x}" for a, _ in tr}
    n_can = sum(len(set(scans["canonico"].get(v, []))) for v in trset)
    n_kill = sum(len(set(scans["kill_corregido"].get(v, []))) for v in trset)
    c_can = sum(1 for v in trset if scans["canonico"].get(v))
    c_kill = sum(1 for v in trset if scans["kill_corregido"].get(v))
    dead_kill = sorted(v for v in trset if not scans["kill_corregido"].get(v))

    out = {
        "milestone": "S120",
        "module": "IDT_OPD",
        "modelo": "A6000 fw3.21",
        "bin": "analysis/rea-independent/input/av-cam.bin",
        "convencion": "vaddr = 0x43541000 + file_offset",
        "metodo_referencias": {
            "escaner_canonico": "analysis/s106_imaging_cap/scan_pic_refs_v2.py (kill analysis)",
            "nota": "en el script canónico `md.detail` NO está activado, por lo que "
                    "`_writes_to` siempre devuelve False y la kill analysis es inerte; "
                    "además `op.reg & 0xF` confunde r1 con r3 (Capstone: ARM_REG_Rn = 66+n). "
                    "S120 ejecuta además la kill analysis CORREGIDA (detail activo + "
                    "comparación por nombre de registro).",
            "barrido_restringido": "analysis/s120_idt_opd/scan_idt_code_pic.py "
                                   "0x439d0000-0x43a09000 (contiene los 725 sitios)",
        },
        "counts": {
            "trazas_idt_opd": len(tr),
            "tokens_idt_opd_en_el_binario": data.count(b"[IDT_OPD]"),
            "cadenas_distintas": len({t for _, t in tr}),
            "rango_min": f"0x{min(a for a, _ in tr):x}",
            "rango_max": f"0x{max(a for a, _ in tr):x}",
            "funciones": len(funcs),
            "sitios_pic_canonico": n_can,
            "sitios_pic_kill_corregido": n_kill,
            "cadenas_con_referencia_canonico": c_can,
            "cadenas_con_referencia_kill_corregido": c_kill,
            "cadenas_con_referencia": len([s for s in strings if s["n_refs"]]),
            "cadenas_sin_referencia": len(dead),
            "cadenas_sin_referencia_kill_corregido": len(dead_kill),
            "gemelos_idt_contiguos": len(gemelos),
            "sub_bloques": len(SUBBLOCKS),
            "a7s_traces_idt_opd": a7s.count(b"[IDT_OPD]"),
            "a7s_traces_idt": len(a7s_idt),
            "a7s_comunes_texto": len(set(core6) & set(core7)),
            "a7s_solo_a6000": len(set(core6) - set(core7)),
            "a7s_solo_a7s": len(set(core7) - set(core6)),
            "a6300_traces_idt_opd": a63.count(b"[IDT_OPD]"),
            "a6300_traces_idt": len(a63_idt),
            "a6300_comunes_texto": len(set(core6) & set(core63)),
        },
        "subblocks": [
            {"lo": lo, "hi": hi, "submodule": name, "desc": desc,
             "n": len([s for s in strings if s["submodule"] == name])}
            for lo, hi, name, desc in SUBBLOCKS],
        "strings": strings,
        "functions": [{"func": f, "n": len(v), "strings": sorted(set(v))}
                      for f, v in sorted(funcs.items())],
        "gemelos_idt": gemelos,
        "sin_referencia": dead,
        "sin_referencia_kill_corregido": dead_kill,
        "estructuras": {"IE": STRUCT_IE, "MAP": STRUCT_MAP, "punteros": STRUCT_PUNTEROS},
        "diferencial": {
            "a7s_fw320": {
                "traces_idt_opd": a7s.count(b"[IDT_OPD]"),
                "traces_idt": len(a7s_idt),
                "comunes": len(set(core6) & set(core7)),
                "solo_a6000": sorted(set(core6) - set(core7)),
                "solo_a7s": [{"vaddr": core7[c], "core": c}
                             for c in sorted(set(core7) - set(core6))],
            },
            "a6300_fw201": {
                "traces_idt_opd": a63.count(b"[IDT_OPD]"),
                "traces_idt": len(a63_idt),
                "comunes": len(set(core6) & set(core63)),
                "solo_a6000": sorted(set(core6) - set(core63)),
            },
        },
    }
    json.dump(out, open(os.path.join(HERE, "idt_opd.json"), "w"),
              indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1, ensure_ascii=False))
    print("funciones:", len(funcs))
    for f, v in sorted(funcs.items(), key=lambda kv: -len(kv[1]))[:10]:
        print(f"  {f}  {len(v)}")


if __name__ == "__main__":
    main()
