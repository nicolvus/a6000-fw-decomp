#!/usr/bin/env python3
"""S140 — módulo `[CAM_UTIL_ADJ]` (22 trazas) del firmware A6000 fw3.21.

Recalcula de forma independiente:
  * las 22 cadenas `[CAM_UTIL_ADJ]` y sus direcciones,
  * los sitios de referencia PIC (regla **estricta** canónica del repo:
    `analysis/s106_imaging_cap/scan_pic_refs_strict.py`),
  * la atribución sitio -> función (prólogo Thumb más cercano hacia atrás),
  * la tabla de despacho de `cam_adjcmd_handle_cb()`,
  * la tabla de códigos de comando "Sens:*" en los tres firmwares,
  * el diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01.

Convención: vaddr = 0x43541000 + file_offset (A6000 fw3.21).
Para A7S/A6300 la convención de vaddr NO está verificada: se reporta el offset.

Salida: analysis/s140_cam_util_adj/cam_util_adj.json
"""
import bisect
import json
import os
import re
import struct

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
A7S = os.path.join(REPO, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                          "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = os.path.join(REPO, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
TOKEN = b"[CAM_UTIL_ADJ]"
MAX_LDR_GAP = 4096

# tabla de despacho usada por cam_adjcmd_handle_cb (0x43900a24)
DISPATCH_VADDR = 0x440121F8
DISPATCH_ENTRIES = 3
# stub "no soportado" (respuesta vacia) usado por los indices 0 y 2
STUB_NOOPS = 0x43B2A0B8
# tabla de codigos de comando "Sens:*" (A6000)
SENS_TABLE_VADDR = 0x43FE858C
SENS_CMD_FIRST = 0x0400015D
SENS_CMD_LAST = 0x0400018F


# --------------------------------------------------------------------- utils
def cstr(data, off, maxlen=300):
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin-1")


def u16(data, off):
    return struct.unpack_from("<H", data, off)[0]


def u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


def pic_index(data):
    """{destino: [sitios `add rX,pc`]} — regla estricta (canónica del repo)."""
    n = len(data)
    ldrs = []
    for a in range(BASE, BASE + n - 8, 2):
        o = a - BASE
        h = u16(data, o)
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = u16(data, o + 2)
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is None:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= n - 4:
            ldrs.append((a, reg, u32(data, o2)))
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    keys = {}
    for reg, v in by_reg.items():
        v.sort()
        keys[reg] = [x[0] for x in v]
    out = {}
    for a in range(BASE, BASE + n - 4, 2):
        h = u16(data, a - BASE)
        if (h & 0xFF00) != 0x4400 or ((h >> 3) & 0xF) != 15:
            continue
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by_reg.get(reg)
        if not v:
            continue
        i = bisect.bisect_right(keys[reg], a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        out.setdefault((w + (a + 4)) & 0xFFFFFFFF, []).append(a)
    return out, ldrs


def ldr_for_add(ldrs, add_addr):
    """(ldr_addr, valor_del_pool) del `ldr` emparejado con el `add`."""
    best = None
    for a, reg, w in ldrs:
        if reg is None:
            continue
        if a < add_addr <= a + MAX_LDR_GAP:
            if best is None or a > best[0]:
                best = (a, w)
    return best


def prologues(data):
    out = []
    a = BASE
    n = len(data)
    while a < BASE + n - 4:
        h = u16(data, a - BASE)
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D and (u16(data, a - BASE + 2) & 0x4000):
            out.append(a)
        a += 2
    return out


def fstart(starts, site):
    i = bisect.bisect_right(starts, site) - 1
    return starts[i] if i >= 0 else None


# ------------------------------------------------------------------ principal
def main():
    data = open(BIN, "rb").read()
    pic, ldrs = pic_index(data)
    starts = prologues(data)

    # 1. las 22 cadenas
    cadenas = []
    i = 0
    while True:
        j = data.find(TOKEN, i)
        if j < 0:
            break
        s = j
        while s > 0 and 32 <= data[s - 1] < 127:
            s -= 1
        va = BASE + s
        txt = cstr(data, s)
        sites = sorted(pic.get(va, []))
        items = []
        for st in sites:
            la, w = ldr_for_add(ldrs, st)
            items.append({
                "site": f"0x{st:08x}",
                "ldr": f"0x{la:08x}" if la else None,
                "pool": f"0x{w:08x}" if la else None,
                "dest": f"0x{va:08x}",
                "verificado_a_mano": True,
            })
        cadenas.append({
            "vaddr": f"0x{va:08x}",
            "offset": f"0x{s:08x}",
            "text": txt,
            "n_sites": len(sites),
            "sites": items,
            "func": f"0x{fstart(starts, sites[0]):08x}" if sites else None,
        })
        i = j + 1

    # 2. mapa función -> trazas
    by_func = {}
    for c in cadenas:
        by_func.setdefault(c["func"], []).append(c)
    FUNC_NAMES = {
        0x439007B0: "cam_util_adj_table_rw (Table Write / Table Read)",
        0x43900A24: "cam_adjcmd_handle_cb()",
        0x43900C44: "tsk_cam_adjctrl (bucle de tarea OSAL)",
    }
    funciones = []
    for f, cs in sorted(by_func.items(), key=lambda kv: int(kv[0], 16)):
        fi = int(f, 16)
        funciones.append({
            "func": f,
            "nombre": FUNC_NAMES.get(fi, "(sin nombre)"),
            "n_trazas": len(cs),
            "n_sitios": sum(c["n_sites"] for c in cs),
            "vaddr_inicio": f,
            "vaddr_fin": {
                0x439007B0: "0x439008AC",
                0x43900A24: "0x43900BDE",
                0x43900C44: "0x43900D30",
            }.get(fi),
            "trazas": [{"site": s["site"], "vaddr": c["vaddr"], "text": c["text"]}
                       for c in cs for s in c["sites"]],
        })

    # 3. tabla de despacho de cam_adjcmd_handle_cb
    dispatch = []
    for k in range(DISPATCH_ENTRIES):
        a = DISPATCH_VADDR + k * 8
        o = a - BASE
        w0, w1 = struct.unpack_from("<II", data, o)
        dispatch.append({
            "idx": k,
            "vaddr": f"0x{a:08x}",
            "campo0": f"0x{w0:08x}",
            "func_ptr": f"0x{w1:08x}",
            "destino": f"0x{w1 & ~1:08x}",
            "es_stub_no_soportado": (w1 & ~1) == STUB_NOOPS,
        })

    # 4. tabla de codigos "Sens:*" en los tres firmwares
    def sens_table(path, with_vaddr):
        """Tabla {cmd u32, size u32, str_ptr u32} de codigos "Sens:*".

        Se ancla en la entrada 'Sens:AdjCmd CAIF' (cmd 0x04020180, size 0x0c) y se
        retrocede entrada a entrada hasta el inicio. El puntero de la cadena se
        convierte a offset de fichero usando el delta ancla-puntero (asi tambien
        funciona en A7S/A6300, donde la convencion de vaddr no esta verificada).
        """
        d = open(path, "rb").read()
        anchor = d.find(b"Sens:AdjCmd CAIF")
        if anchor < 0:
            return None
        pat = struct.pack("<II", 0x04020180, 0x0C)
        idx = d.find(pat)
        if idx < 0:
            return None
        delta = u32(d, idx + 8) - anchor       # vaddr_base = offset + delta
        start = idx
        while start >= 12:
            cmd, size, ptr = struct.unpack_from("<III", d, start - 12)
            if not (0x04000000 <= cmd <= 0x0402FFFF or 0x01000000 <= cmd <= 0x0102FFFF):
                break
            start -= 12
        rows = []
        o = start
        while True:
            cmd, size, ptr = struct.unpack_from("<III", d, o)
            if not (0x04000000 <= cmd <= 0x0402FFFF or 0x01000000 <= cmd <= 0x0102FFFF):
                break
            so = ptr - delta
            rows.append({
                "cmd": f"0x{cmd:08x}",
                "size": size,
                "str_ptr": f"0x{ptr:08x}",
                "text": cstr(d, so) if 0 <= so < len(d) else "",
            })
            o += 12
        return {"offset_inicio": f"0x{start:08x}",
                "vaddr_inicio": f"0x{start + BASE:08x}" if with_vaddr else None,
                "delta_vaddr_menos_offset": delta,
                "n": len(rows), "filas": rows}

    sens = {
        "a6000_fw321": sens_table(BIN, True),
        "a7s_fw320": sens_table(A7S, False),
        "a6300_fw201": sens_table(A6300, False),
    }

    # 5. diferencial
    def occ(path, pat):
        return open(path, "rb").read().count(pat)

    def all_strings(path):
        d = open(path, "rb").read()
        return set(m.group()[:-1].decode("latin-1")
                   for m in re.finditer(rb"[ -~]{4,300}\x00", d))

    a7s_s, a6300_s = all_strings(A7S), all_strings(A6300)
    interiores = [c["text"].replace("[CAM_UTIL_ADJ]:", "").strip() for c in cadenas]
    dif = {
        "n_cadenas_a6000": len(cadenas),
        "n_cadenas_a7s": occ(A7S, TOKEN),
        "n_cadenas_a6300": occ(A6300, TOKEN),
        "interiores_presentes_a7s": sum(1 for x in interiores if x in a7s_s),
        "interiores_presentes_a6300": sum(1 for x in interiores if x in a6300_s),
        "interiores": interiores,
        "marcas_auxiliares": {
            "tsk_cam_adjctrl": {"a6000": occ(BIN, b"tsk_cam_adjctrl"),
                                 "a7s": occ(A7S, b"tsk_cam_adjctrl"),
                                 "a6300": occ(A6300, b"tsk_cam_adjctrl")},
            "cam_adjcmd_handle_cb": {"a6000": occ(BIN, b"cam_adjcmd_handle_cb"),
                                     "a7s": occ(A7S, b"cam_adjcmd_handle_cb"),
                                     "a6300": occ(A6300, b"cam_adjcmd_handle_cb")},
            "SensRamAcs": {"a6000": occ(BIN, b"SensRamAcs"),
                           "a7s": occ(A7S, b"SensRamAcs"),
                           "a6300": occ(A6300, b"SensRamAcs")},
            "Senser RAM Access": {"a6000": occ(BIN, b"Senser RAM Access"),
                                  "a7s": occ(A7S, b"Senser RAM Access"),
                                  "a6300": occ(A6300, b"Senser RAM Access")},
            "prefijo_CAM_UTIL": {"a6000": occ(BIN, b"[CAM_UTIL]"),
                                 "a7s": occ(A7S, b"[CAM_UTIL]"),
                                 "a6300": occ(A6300, b"[CAM_UTIL]")},
            "prefijo_CAM_UTIL_SENS": {"a6000": occ(BIN, b"[CAM_UTIL_SENS]"),
                                      "a7s": occ(A7S, b"[CAM_UTIL_SENS]"),
                                      "a6300": occ(A6300, b"[CAM_UTIL_SENS]")},
            "prefijo_CAMERA_ADJ": {"a6000": occ(BIN, b"[CAMERA_ADJ]"),
                                   "a7s": occ(A7S, b"[CAMERA_ADJ]"),
                                   "a6300": occ(A6300, b"[CAMERA_ADJ]")},
            "prefijo_Sens": {"a6000": occ(BIN, b"Sens:"),
                             "a7s": occ(A7S, b"Sens:"),
                             "a6300": occ(A6300, b"Sens:")},
        },
        "tabla_sens_comun": {
            "a6000_n": sens["a6000_fw321"]["n"],
            "a7s_n": sens["a7s_fw320"]["n"],
            "a6300_n": sens["a6300_fw201"]["n"],
            "cmd_ids_identicos_a7s": [r["cmd"] for r in sens["a6000_fw321"]["filas"]] ==
                                     [r["cmd"] for r in sens["a7s_fw320"]["filas"]],
            "cmd_ids_identicos_a6300": [r["cmd"] for r in sens["a6000_fw321"]["filas"]] ==
                                       [r["cmd"] for r in sens["a6300_fw201"]["filas"]],
        },
    }

    # 6. vecindario: que otros modulos se referencian en la misma banda de codigo
    LO, HI = 0x43900000, 0x43910000
    vec = {}
    for dest, ss in pic.items():
        if not (LO <= ss[0] < HI):
            continue
        txt = cstr(data, int(dest) - BASE)
        m = re.match(r"\[([A-Z0-9_]+)\]", txt)
        mod = m.group(1) if m else "(sin etiqueta)"
        vec.setdefault(mod, {"cadenas": set(), "funciones": set()})
        vec[mod]["cadenas"].add(dest)
        vec[mod]["funciones"].add(f"0x{fstart(starts, ss[0]):08x}")
    vecindario = {k: {"n_cadenas": len(v["cadenas"]),
                      "funciones": sorted(v["funciones"])}
                  for k, v in sorted(vec.items(), key=lambda kv: -len(kv[1]["cadenas"]))}

    # 7. cadenas "Sens:*" en los tres firmwares
    def sens_strings(path):
        d = open(path, "rb").read()
        return [cstr(d, m.start()) for m in re.finditer(rb"Sens:[ -~]{0,60}\x00", d)]

    sens_str = {"a6000_fw321": sens_strings(BIN),
                "a7s_fw320": sens_strings(A7S),
                "a6300_fw201": sens_strings(A6300)}

    out = {
        "milestone": "S140",
        "modulo": "[CAM_UTIL_ADJ]",
        "firmware": "A6000 fw3.21",
        "convencion": "vaddr = 0x43541000 + file_offset",
        "regla_pic": "estricta (canonica) - analysis/s106_imaging_cap/scan_pic_refs_strict.py",
        "contadores": {
            "cadenas": len(cadenas),
            "cadenas_con_referencia": sum(1 for c in cadenas if c["n_sites"]),
            "sitios": sum(c["n_sites"] for c in cadenas),
            "funciones": len(funciones),
        },
        "cadenas": cadenas,
        "funciones": funciones,
        "tabla_despacho": dispatch,
        "tabla_sens": sens,
        "vecindario_0x43900000_0x43910000": vecindario,
        "cadenas_sens_por_firmware": sens_str,
        "diferencial": dif,
        "ayudantes": [
            {"vaddr": "0x43900728", "rol": "log [CAM_UTIL] (formato + varargs)"},
            {"vaddr": "0x4390092C", "rol": "construye y envia mensaje OSAL al infra"},
            {"vaddr": "0x439009C8", "rol": "escribe (module id, valor) en variable global"},
            {"vaddr": "0x439009F0", "rol": "escribe (tipo, a, b, c) y despacha"},
            {"vaddr": "0x43900C1C", "rol": "despacha la respuesta; si no lista -> 0x4390092C"},
            {"vaddr": "0x439023B8", "rol": "[CAM_UTIL_SENS] UTIL MS Mgr -> Call CB"},
            {"vaddr": "0x43B2A0B8", "rol": "stub de respuesta 'no soportado'"},
        ],
    }
    dest = os.path.join(REPO, "analysis/s140_cam_util_adj/cam_util_adj.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"cadenas={len(cadenas)} sitios={out['contadores']['sitios']} "
          f"funciones={len(funciones)} -> {dest}")
    print("sens table:", {k: (v["n"] if v else None) for k, v in sens.items()})


if __name__ == "__main__":
    main()
