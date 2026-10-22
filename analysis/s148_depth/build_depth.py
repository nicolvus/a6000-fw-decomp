#!/usr/bin/env python3
"""S148 — construye `analysis/s148_depth/depth.json` con los datos verificados
del modulo `[DEPTH]` (16 trazas) del firmware A6000 fw3.21.

Todo lo que hay aqui se ha verificado desensamblando bytes del blob
(convencion vaddr = 0x43541000 + file_offset). Los sitios PIC usan la
regla **estricta** canonica del repo (`analysis/s106_imaging_cap/scan_pic_refs_strict.py`).

Salida: analysis/s148_depth/depth.json
"""
import bisect
import json
import os
import struct
import sys

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A6000 = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
A7S = os.path.join(REPO, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = os.path.join(REPO, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
GLOBAL = os.path.join(REPO, "analysis/s106_imaging_cap/pic_refs_strict_global.json")

U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MAX_LDR_GAP = 4096

# --- tabla de comandos del modulo (verificada leyendo los bytes) ------------
# 12 B por entrada: {const char* nombre, const char* nombre, puntero a handler}
CMD_TABLE_A6000 = 0x43FD7C30
CMD_TABLE_A7S = 0x43FD9914
CMD_TABLE_A6300 = 0x4419920C
COMMANDS = ["update", "getLiro", "getMsg", "notifyOn", "notifyOff", "enableDummyRecv"]

# --- roles verificados de cada funcion --------------------------------------
FUNC_ROLES = {
    0x43541B00: "implementacion de `update`: recorta valueDepth a 0xFA0 y traza 'UPDATE'",
    0x4356228C: "handler del comando `enableDummyRecv` (registra el receptor 'dummy')",
    0x435622D4: "callback de respuesta (Rsp): traza cid/status/valueDepth y libera el mensaje",
    0x4356230C: "handler del comando `getMsg`",
    0x43562354: "handler del comando `notifyOff`",
    0x435623BC: "handler del comando `notifyOn`",
    0x43562424: "handler del comando `getLiro`",
    0x43562454: "handler del comando `update` (parsea 2 hexadecimales)",
    0x4356248C: "registro del modulo: init + alta con el nombre 'depth' y su tabla de comandos",
    0x435624B0: "constructor de la clase DepthGaugeMain (fija el vptr 0x43FB8F50)",
    0x43562578: "fija el vptr de un objeto DepthGaugeMain",
    0x43562590: "init: registra el callback de notificacion (0x43A3ACE2) con 0x439B4244",
    0x435625DC: "init: da de alta el modulo como receptor del GID 0x018B04DC",
    0x43562618: "getLiro interno: envia una peticion al GID 0x018B04DC y lee el valor",
    0x43562634: "manejador de la notificacion GET (traza 'GET %d %d')",
    0x43562660: "emite la notificacion al GID destino (traza 'NOTIFY to ...')",
    0x435626D4: "despachador de notificaciones: cmd 1=GET, 2=NOTIFY_ON, 3=NOTIFY_OFF",
    0x43A3AC8C: "API: conversion de cadena hexadecimal (strtoul base 16)",
    0x43A3AC98: "API: getMsg -> 0x43562634",
    0x43A3ACAA: "API: update -> 0x43541B00",
    0x43A3ACBC: "API: getLiro -> 0x43562618",
    0x43A3ABFE: "funcion de arranque que da de alta el modulo 'depth'",
}


def cstr(B, off, maxlen=200):
    e = off
    while e < len(B) and e < off + maxlen and 32 <= B[e] < 127:
        e += 1
    return B[off:e].decode("latin-1")


def strings_with_token(B, token, base=BASE):
    out, seen = [], set()
    idx = 0
    while True:
        i = B.find(token, idx)
        if i < 0:
            break
        idx = i + 1
        s = i
        while s > 0 and 32 <= B[s - 1] < 127:
            s -= 1
        e = i
        while e < len(B) and 32 <= B[e] < 127:
            e += 1
        a = base + s
        if a not in seen:
            seen.add(a)
            out.append((a, B[s:e].decode("latin-1")))
    return out


def build_ldrs(B):
    out = []
    for a in range(BASE, BASE + len(B) - 8, 2):
        o = a - BASE
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= len(B) - 4:
                out.append((a, reg, lit, U32(B, o2)[0]))
    return out


def prologues(B):
    out = []
    for a in range(BASE, BASE + len(B) - 4, 2):
        o = a - BASE
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (U16(B, o + 2)[0] & 0x4000):
            out.append(a)
    return out


def cmd_table(B, addr, base=BASE):
    """Lee la tabla de 12 B por entrada; devuelve [(nombre, handler)]."""
    out = []
    for i in range(16):
        a = addr + 12 * i
        o = a - base
        if o < 0 or o + 12 > len(B):
            break
        n1, n2, h = U32(B, o)[0], U32(B, o + 4)[0], U32(B, o + 8)[0]
        if n1 == 0 and n2 == 0 and h == 0:
            break
        out.append((cstr(B, n1 - base), n2, h & ~1))
    return out


def main():
    B = open(A6000, "rb").read()
    toks = strings_with_token(B, b"[DEPTH]")
    gmap = {int(k, 16): v for k, v in json.load(open(GLOBAL)).items()}
    starts = prologues(B)
    ldrs = build_ldrs(B)
    by_reg = {}
    for a, reg, lit, w in ldrs:
        by_reg.setdefault(reg, []).append((a, lit, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}

    def resolve(add_addr):
        """(ldr, pool, W, destino) del par PIC de un `add rX,pc` (regla estricta)."""
        o = add_addr - BASE
        h = U16(B, o)[0]
        if not ((h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15):
            return None
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by_reg.get(reg, [])
        i = bisect.bisect_right(keys[reg], add_addr) - 1
        if i < 0:
            return None
        la, lit, w = v[i]
        if add_addr - la > MAX_LDR_GAP:
            return None
        return la, lit, w, (w + add_addr + 4) & 0xFFFFFFFF

    def func_of(site):
        i = bisect.bisect_right(starts, site) - 1
        return starts[i] if i >= 0 else None

    # --- trazas ------------------------------------------------------------
    strings = []
    for a, t in toks:
        sites = sorted(set(gmap.get(a, [])))
        rows = []
        for s in sites:
            r = resolve(s)
            assert r is not None, hex(s)
            la, lit, w, dest = r
            assert dest == a, (hex(s), hex(dest), hex(a))
            rows.append({
                "site": f"0x{s:08x}",
                "ldr": f"0x{la:08x}",
                "pool": f"0x{lit:08x}",
                "pool_value": f"0x{w:08x}",
                "dest": f"0x{dest:08x}",
                "func": f"0x{func_of(s):08x}",
            })
        strings.append({
            "addr": f"0x{a:08x}",
            "text": t,
            "n_sites": len(rows),
            "sites": rows,
        })

    funcs = sorted({r["func"] for s in strings for r in s["sites"]},
                   key=lambda x: int(x, 16))
    n_sites = sum(s["n_sites"] for s in strings)

    # --- tabla de comandos -------------------------------------------------
    tab = cmd_table(B, CMD_TABLE_A6000)
    cmds = []
    for (name, n2, h), expect in zip(tab, COMMANDS):
        assert name == expect, (name, expect)
        cmds.append({"name": name, "handler": f"0x{h:08x}",
                     "handler_is_thumb": True})

    # --- diferencial -------------------------------------------------------
    diff = {}
    for name, path, tabaddr in (("a7s_fw320", A7S, CMD_TABLE_A7S),
                                 ("a6300_fw201", A6300, CMD_TABLE_A6300)):
        Ob = open(path, "rb").read()
        ot = strings_with_token(Ob, b"[DEPTH]")
        cores_a = {t.split("]", 2)[-1] for _, t in toks}
        cores_o = {t.split("]", 2)[-1] for _, t in ot}
        ttab = cmd_table(Ob, tabaddr)
        diff[name] = {
            "n_token_depth": len(ot),
            "n_cadenas_depth": len(ot),
            "n_cores_comunes": len(cores_a & cores_o),
            "cores_solo_a6000": sorted(cores_a - cores_o),
            "clase_depthgauge_main": Ob.count(b"14DepthGaugeMain"),
            "tabla_comandos": [
                {"name": n, "handler": f"0x{h:08x}"} for (n, _n2, h) in ttab],
            "gid_0x018b04dc": Ob.count(struct.pack("<I", 0x018B04DC)),
        }
    diff["a6000_fw321"] = {
        "n_token_depth": len(toks),
        "n_cadenas_depth": len(toks),
        "n_cores_comunes": len(toks),
        "cores_solo_a6000": [],
        "clase_depthgauge_main": B.count(b"14DepthGaugeMain"),
        "tabla_comandos": cmds,
        "gid_0x018b04dc": B.count(struct.pack("<I", 0x018B04DC)),
    }

    out = {
        "hito": "S148",
        "modulo": "[DEPTH]",
        "fw": "A6000 fw3.21",
        "base": "vaddr = 0x43541000 + file_offset",
        "regla_pic": "estricta (analysis/s106_imaging_cap/scan_pic_refs_strict.py)",
        "contadores": {
            "n_cadenas": len(strings),
            "n_textos_distintos": len({s["text"] for s in strings}),
            "rango": [strings[0]["addr"], strings[-1]["addr"]],
            "n_sitios_pic": n_sites,
            "n_funcs_emisoras": len(funcs),
            "n_funcs_modulo_total": len(FUNC_ROLES),
            "n_comandos": len(cmds),
            "n_muertas": 0,
        },
        "cadenas": strings,
        "funcs_emisoras": funcs,
        "funcs_roles": {f"0x{k:08x}": v for k, v in sorted(FUNC_ROLES.items())},
        "tabla_comandos": {
            "a6000": f"0x{CMD_TABLE_A6000:08x}",
            "a7s": f"0x{CMD_TABLE_A7S:08x}",
            "a6300": f"0x{CMD_TABLE_A6300:08x}",
            "formato_entrada": "12 B: {char* nombre, char* nombre, puntero a handler}",
            "entradas": cmds,
        },
        "datos_verificados": {
            "gid": "0x018B04DC",
            "clase": "14DepthGaugeMain (RTTI, 0x43C24B85)",
            "type_info": "0x43FD7C84 (vptr 0x43FD04F8 + nombre)",
            "vtable": "0x43FB8F50 (offset-to-top 0, type_info, 2 funciones virtuales)",
            "nombre_registro": "depth (0x43C24B46)",
            "singleton": "0x43E131E8",
            "tabla_servicios_global": "0x4401EEE4",
            "clamp_valueDepth": "0xFA0 (4000) en 0x43541B04",
            "ids_notificacion": "1=GET, 2=NOTIFY_ON, 3=NOTIFY_OFF (0x435626D4)",
        },
        "consumidores_verificados": [
            {"fichero": "CS_ExifMakerNote.cpp (0x43CC56DC)",
             "sitio": "0x438B900A",
             "que_hace": "llama a getMsg (0x43A3AC98) y escribe el valor en el MakerNote: "
                         "tag Exif 0x5001 = racional (valueDepth*10 : 1000) en 0x438B90A8 "
                         "y tag 0x5002 = estado (0 / 0x80 / 0x81) en 0x438B90B8"},
            {"fichero": "[ACCY][INFO][HOUSING] (0x43C25414)",
             "sitio": "0x43564DC0",
             "que_hace": "llama a update (0x43A3ACAA) con {status=2, valueDepth=0}"},
            {"fichero": "[ACCY][INFO][HOUSING] (0x43C25414)",
             "sitio": "0x43564ED2",
             "que_hace": "llama a update (0x43A3ACAA) con el estado recibido"},
        ],
        "linea_obturador": {
            "menciona_obturador": 0,
            "menciona_sensor": 0,
            "menciona_exposicion": 0,
            "menciona_enfoque": 0,
            "menciona_lectura_sensor": 0,
            "conclusion": "sin relacion con el obturador electronico; S51 (A/B/C = NO) intacto",
        },
        "diferencial": diff,
        "no_verificado": [
            "que magnitud fisica mide 'valueDepth' (0..4000) y que significa 'status'",
            "el fichero fuente que implementa el modulo: no hay ningun nombre de fichero "
            "embebido en sus 16 trazas ni en la zona de codigo 0x4356228C-0x435627B0",
            "el significado de la sigla DEPTH (no aparece expandida en ningun byte)",
            "el receptor final del GID 0x018B04DC fuera de este binario",
            "el sentido de los codigos 0x80/0x81 escritos en el tag Exif 0x5002",
        ],
    }

    dest = os.path.join(REPO, "analysis/s148_depth/depth.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("->", dest)
    print("cadenas:", len(strings), " sitios PIC:", n_sites, " funciones:", len(funcs))


if __name__ == "__main__":
    main()
