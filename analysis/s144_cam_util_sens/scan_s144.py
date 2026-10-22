#!/usr/bin/env python3
"""S144 — modulo `[CAM_UTIL_SENS]` (21 trazas) del firmware A6000 fw3.21.

Recalcula de forma independiente:
  * las 21 cadenas `[CAM_UTIL_SENS]` y sus direcciones,
  * los sitios de referencia PIC (regla **estricta** canónica del repo:
    `analysis/s106_imaging_cap/scan_pic_refs_strict.py`),
  * la atribucion sitio -> funcion (prologo Thumb mas cercano hacia atras),
  * los destinos de llamada (`bl`/`blx` de 16 y 32 bits) de cada funcion y el
    conjunto de cadenas referenciadas en la banda del modulo,
  * los globales (bloque de parametros) que usa el modulo,
  * el diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01.

Convencion: vaddr = 0x43541000 + file_offset (A6000 fw3.21; valida tambien
para A7S fw3.20 y A6300 fw2.01, verificado en S143 con la tabla "Sens").

Salida: analysis/s144_cam_util_sens/cam_util_sens.json
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
TOKEN = b"[CAM_UTIL_SENS]"
MAX_LDR_GAP = 4096

# banda de codigo del modulo (las 5 funciones + ayudantes)
MOD_LO, MOD_HI = 0x43901000, 0x43902610
# funciones del modulo (asignadas a mano, verificadas por desensamblado)
FUNC_NAMES = {
    0x439012D0: "CB for BKID change (callback de cambio de bloque del sensor)",
    0x43901D50: "Debug IM ASync Open (apertura de fichero en la memoria interna)",
    0x43902168: "SET FILE NUM Func (asignacion de numero de fichero/adr/tamano)",
    0x439023B8: "UTIL MS Mgr) Call CB (invocacion del callback del gestor MS)",
    0x43902418: "Debug IM Sync Open (variante sincrona de la apertura)",
}
# ayudantes verificados por desensamblado
HELPERS = {
    0x43900FF8: "getFlg: devuelve un byte global (el 'Flg'/'MountSTAT' de las trazas)",
    0x439010DC: "setter de parametro (usado por 0x43901380)",
    0x43901150: "log [CAM_UTIL_SENS] (formato + varargs -> mensaje OSAL)",
    0x43901274: "setParam16: escribe un valor en el bloque de parametros global",
    0x4390129C: "setParam4: escribe 4 bytes en el bloque de parametros global",
    0x43901B7C: "log [CAM_UTIL_SENS] (2.a copia del ayudante de log)",
    0x43901C04: "envia el mensaje OSAL con la plantilla de 12 B",
    0x43901CA0: "setParam16b: escribe u16 en +8 y 0 en +0xa del bloque global",
    0x43901CCC: "setParam4b: escribe 4 bytes (+8,+9,+0xa,+0xb) del bloque global",
    0x43901D00: "setParam32: escribe un u32 en +8 del bloque global",
    0x43901380: "seleccion de una entrada de una tabla global (indice r0)",
    0x43900E30: "[CAMERA_ADJ] Utility MS Mount Start (usado por el CB de BKID)",
    0x43900F18: "[CAMERA_ADJ] Utility MS UnMount Start (usado por el CB de BKID)",
}


# --------------------------------------------------------------------- utils
def cstr(data, off, maxlen=400):
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin-1")


def u16(data, off):
    return struct.unpack_from("<H", data, off)[0]


def u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


def sign_ext(v, bits):
    m = 1 << (bits - 1)
    return (v ^ m) - m


def pic_index(data):
    """{destino: [sitios `add rX,pc`]} — regla estricta (canonica del repo)."""
    n = len(data)
    ldrs = []
    adds = []
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
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= n - 4:
                ldrs.append((a, reg, u32(data, o2)))
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            adds.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    for a, reg in adds:
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
    return out, ldrs, adds


def ldr_for_add(ldrs, add_addr, reg=None):
    """(ldr_addr, valor_del_pool) del `ldr` emparejado con el `add`.

    `reg` = registro del `add` (0-7). Si se da, solo se consideran los `ldr`
    del MISMO registro (igual que la regla estricta de `pic_index`).
    """
    best = None
    for a, r, w in ldrs:
        if reg is not None and r != reg:
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


def branch_targets(data, lo, hi):
    """[(addr, kind, target)] de BL de 16 bits y BL de 32 bits en [lo,hi)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(data) - 4:
            a += 2
            continue
        h1 = u16(data, o)
        if (h1 & 0xF800) == 0xE000:
            imm = sign_ext(h1 & 0x7FF, 11) << 1
            out.append((a, "bl16", (a + 4 + imm) & 0xFFFFFFFF))
            a += 2
            continue
        if (h1 & 0xF800) == 0xF000:
            h2 = u16(data, o + 2)
            S = (h1 >> 10) & 1
            if (h2 & 0xC000) == 0xC000 and (h2 & 0x1000):
                imm10 = h1 & 0x3FF
                J1 = (h2 >> 13) & 1
                J2 = (h2 >> 11) & 1
                imm11 = h2 & 0x7FF
                I1 = 1 - (J1 ^ S)
                I2 = 1 - (J2 ^ S)
                imm = (S << 24) | (I1 << 23) | (I2 << 22) | (imm10 << 12) | (imm11 << 1)
                out.append((a, "bl", (a + 4 + sign_ext(imm, 25)) & 0xFFFFFFFF))
                a += 4
                continue
        a += 2
    return out


# ------------------------------------------------------------------ principal
def main():
    data = open(BIN, "rb").read()
    pic, ldrs, adds = pic_index(data)
    starts = prologues(data)

    # 1. las 21 cadenas
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

    # 2. mapa funcion -> trazas
    by_func = {}
    for c in cadenas:
        for st in c["sites"]:
            f = fstart(starts, int(st["site"], 16))
            by_func.setdefault(f"0x{f:08x}", []).append((c, st))
    funciones = []
    for f, items in sorted(by_func.items(), key=lambda kv: int(kv[0], 16)):
        fi = int(f, 16)
        funciones.append({
            "func": f,
            "nombre": FUNC_NAMES.get(fi, "(sin nombre)"),
            "n_sitios": len(items),
            "trazas": [{"site": st["site"], "vaddr": c["vaddr"], "text": c["text"]}
                       for c, st in items],
        })

    # 3. limites y destinos de llamada de cada funcion
    br = branch_targets(data, MOD_LO, MOD_HI)
    for fu in funciones:
        fi = int(fu["func"], 16)
        nxt = [s for s in starts if s > fi]
        hi = nxt[0] if nxt else fi + 0x2000
        fu["vaddr_fin_estimado"] = f"0x{hi:08x}"
        calls = [{"site": f"0x{a:08x}", "tipo": k, "dest": f"0x{t:08x}"}
                 for a, k, t in br if fi <= a < hi]
        fu["llamadas"] = calls
        fu["destinos_unicos"] = sorted({c["dest"] for c in calls})

    # 3b. llamantes de las 5 funciones (bl/blx de 16 y 32 bits + punteros absolutos)
    br_all = branch_targets(data, BASE, BASE + len(data))
    llamantes = {}
    for fu in funciones:
        fi = int(fu["func"], 16)
        calls = [{"site": f"0x{a:08x}", "tipo": k} for a, k, t in br_all if t == fi]
        pat = struct.pack("<I", fi | 1)
        ptrs = []
        i = 0
        while True:
            j = data.find(pat, i)
            if j < 0:
                break
            ptrs.append(f"0x{BASE + j:08x}")
            i = j + 1
        llamantes[fu["func"]] = {
            "n_llamadas_bl": len(calls),
            "llamadas_bl": calls,
            "punteros_absolutos_4B": ptrs,
        }

    # 4. cadenas referenciadas en la banda del modulo
    banda = []
    for dest, ss in pic.items():
        if not any(MOD_LO <= s < MOD_HI for s in ss):
            continue
        txt = cstr(data, dest - BASE, maxlen=200)
        banda.append({"dest": f"0x{dest:08x}", "text": txt,
                      "n_sites": len(ss),
                      "sites": [f"0x{s:08x}" for s in sorted(ss)[:20]]})
    banda.sort(key=lambda x: x["dest"])

    # 5. globales: bases de bloques de parametros (patron `ldr rX,[pc]` + `add rX,pc`)
    #    Solo se calculan los `add` concretos verificados a mano (lista explicita).
    GLOB_ADD = [
        (0x43901CD2, "bloque de parametros del modulo (SENS): lo usan 0x43901ccc/0x43901ca0/0x43901d00 (y es la plantilla de 12 B del mensaje)"),
        (0x43900FFA, "byte global 'MountSTAT'/'STAT' (lo devuelve 0x43900ff8)"),
        (0x43901D7E, "byte global 'Flg' (lo leen las trazas '[Flg]%04x')"),
        (0x439023BE, "el mismo byte 'Flg' (lo pone a 0 'UTIL MS Mgr) Call CB')"),
        (0x439023C4, "puntero al callback del gestor MS (invocado con blx r3)"),
        (0x43901D5E, "base de la tabla de objetos 'sl' de 0x43901d50"),
        (0x439012E4, "base del objeto global copiado en el CB de BKID (0x439012d0)"),
    ]

    def base_de(add_addr):
        o = add_addr - BASE
        h = u16(data, o)
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        la, w = ldr_for_add(ldrs, add_addr, reg)
        if not la:
            return None, None
        return la, (w + (add_addr + 4)) & 0xFFFFFFFF

    globales = []
    for a, rol in GLOB_ADD:
        la, b = base_de(a)
        if b is None:
            continue
        globales.append({"add": f"0x{a:08x}", "ldr": f"0x{la:08x}",
                         "base": f"0x{b:08x}", "rol": rol})

    # 6. diferencial
    def occ(path, pat):
        return open(path, "rb").read().count(pat)

    def all_strings(path):
        d = open(path, "rb").read()
        return set(m.group()[:-1].decode("latin-1")
                   for m in re.finditer(rb"[ -~]{4,300}\x00", d))

    a7s_s, a6300_s = all_strings(A7S), all_strings(A6300)
    interiores = [c["text"].replace("[CAM_UTIL_SENS]:", "").strip() for c in cadenas]
    MARCAS = ["[CAM_UTIL_SENS]", "[CAM_UTIL_ADJ]", "[CAM_UTIL]", "[CAMERA_ADJ]",
              "UTIL MS Mgr", "Debug IM ASync Open", "Debug IM Sync Open",
              "SET FILE NUM", "SWFLG", "MODEFLG", "FileNum", "MountSTAT",
              "FsysMode", "CALL BACK NULL", "CB for BKID change",
              "cam_util_debug_file_write", "MemAreaMSDebug", "MS_Writer",
              "WiriteMsDebug", "BKID", "Sens:", "SensRamAcs", "Senser RAM Access",
              "tsk_cam_adjctrl", "cam_adjcmd_handle_cb"]
    marcas = {m: {"a6000": occ(BIN, m.encode()), "a7s": occ(A7S, m.encode()),
                  "a6300": occ(A6300, m.encode())} for m in MARCAS}

    dif = {
        "n_cadenas_a6000": len(cadenas),
        "n_ocurrencias_a6000": occ(BIN, TOKEN),
        "n_cadenas_a7s": occ(A7S, TOKEN),
        "n_cadenas_a6300": occ(A6300, TOKEN),
        "interiores_presentes_a7s": sum(1 for x in interiores if x in a7s_s),
        "interiores_presentes_a6300": sum(1 for x in interiores if x in a6300_s),
        "interiores": interiores,
        "marcas_auxiliares": marcas,
    }

    # 7. cadenas "Sens:*" (canal de comandos) en los tres firmwares
    def sens_strings(path):
        d = open(path, "rb").read()
        return [cstr(d, m.start()) for m in re.finditer(rb"Sens:[ -~]{0,60}\x00", d)]

    # 8. vecindario: que otros modulos se referencian en la banda 0x43900000-0x43910000
    LO, HI = 0x43900000, 0x43910000
    vec = {}
    for dest, ss in pic.items():
        if not (LO <= ss[0] < HI):
            continue
        txt = cstr(data, dest - BASE)
        m = re.match(r"\[([A-Z0-9_]+)\]", txt)
        mod = m.group(1) if m else "(sin etiqueta)"
        vec.setdefault(mod, {"cadenas": set(), "funciones": set()})
        vec[mod]["cadenas"].add(dest)
        vec[mod]["funciones"].add(f"0x{fstart(starts, ss[0]):08x}")
    vecindario = {k: {"n_cadenas": len(v["cadenas"]),
                      "funciones": sorted(v["funciones"])}
                  for k, v in sorted(vec.items(), key=lambda kv: -len(kv[1]["cadenas"]))}

    # 9. nombres de fichero fuente referenciados en la banda 0x43900000-0x43910000
    FNAME = re.compile(rb"[A-Za-z0-9_./\\-]{3,60}\.(?:cpp|c|h|hpp)\x00")
    in_band = []
    for m in FNAME.finditer(data):
        s = m.start()
        if not (s == 0 or 32 <= data[s - 1] < 127):
            continue
        va = BASE + s
        sites = pic.get(va, [])
        if any(0x43900000 <= x < 0x43910000 for x in sites):
            in_band.append({"vaddr": f"0x{va:08x}", "text": m.group()[:-1].decode(),
                            "sites": [f"0x{x:08x}" for x in sites]})

    # 10. negativo: obturador / iris / ISO / exposicion en el vocabulario del modulo
    NEG = ["shut", "shutter", "iris", "aperture", "iso", "exposure", "exp.",
           "silent", "elec", "efcs", "frame", "fps", "speed", "ss ", "tv "]
    vocabulario = sorted({c["text"] for c in cadenas} |
                         {b["text"] for b in banda})
    negativo = {n: [v for v in vocabulario if n in v.lower()] for n in NEG}
    negativo = {k: v for k, v in negativo.items() if v}

    out = {
        "milestone": "S144",
        "modulo": "[CAM_UTIL_SENS]",
        "firmware": "A6000 fw3.21",
        "convencion": "vaddr = 0x43541000 + file_offset",
        "regla_pic": "estricta (canonica) - analysis/s106_imaging_cap/scan_pic_refs_strict.py",
        "banda_codigo": [f"0x{MOD_LO:08x}", f"0x{MOD_HI:08x}"],
        "contadores": {
            "cadenas": len(cadenas),
            "cadenas_con_referencia": sum(1 for c in cadenas if c["n_sites"]),
            "sitios": sum(c["n_sites"] for c in cadenas),
            "funciones": len(funciones),
            "cadenas_en_banda_del_modulo": len(banda),
        },
        "cadenas": cadenas,
        "funciones": funciones,
        "llamantes": llamantes,
        "ayudantes": [{"vaddr": f"0x{k:08x}", "rol": v} for k, v in sorted(HELPERS.items())],
        "cadenas_referenciadas_en_banda": banda,
        "globales_banda": globales,
        "vecindario_0x43900000_0x43910000": vecindario,
        "cadenas_sens_por_firmware": {
            "a6000_fw321": sens_strings(BIN),
            "a7s_fw320": sens_strings(A7S),
            "a6300_fw201": sens_strings(A6300),
        },
        "ficheros_fuente_referenciados_en_banda": in_band,
        "negativo_obturador_iris_iso": negativo,
        "diferencial": dif,
    }
    dest_path = os.path.join(REPO, "analysis/s144_cam_util_sens/cam_util_sens.json")
    with open(dest_path, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"cadenas={len(cadenas)} sitios={out['contadores']['sitios']} "
          f"funciones={len(funciones)} banda={len(banda)} -> {dest_path}")


if __name__ == "__main__":
    main()
