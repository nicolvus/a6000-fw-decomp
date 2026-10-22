#!/usr/bin/env python3
"""S117 — escáner del módulo `[AUGI]` (AUGI / AugiExt) del firmware A6000 fw3.21.

Genera:
  - `augi_strings_raw.json`: las cadenas que contienen el literal `[AUGI]`,
    normalizadas al **inicio real de la cadena** (varias viven dentro de bloques
    `[CodecIF]`, p. ej. `"[CodecIF][AUGI][dec]..."`).
  - `augi_refs.json`: sitios PIC (`ldr` + `add pc`) que apuntan a cada cadena.
  - `augi.json`: resumen — cadenas, referencias, funciones contenedoras
    (prólogos Thumb) y diferencial con la A7S fw3.20.

Convención: vaddr = 0x43541000 + file_offset.
"""
import bisect
import json
import os
import struct
from collections import defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
TOKEN = b"[AUGI]"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_LDR_GAP = 4096

# Cabecera del bloque AUGI: 32 B. La copia "host" es little-endian y la copia
# que viaja en el array/stream lleva cada palabra de 4 B en big-endian.
LAYOUT = {
    "size": 32,
    "host_byte_order": "little-endian",
    "stream_byte_order": "big-endian por palabra de 4 B",
    "stride": 32,
    "stride_evidence": [
        "0x436163c2: lsls r3, r1, #5 (bytes 4b 01)",
        "0x436150ea: lsls r4, r4, #5",
    ],
    "transform_evidence": [
        "0x43a5cb12: rev r0, r1 (bytes 08 ba)",
        "0x435d64e8..0x435d6500: bucle rev por palabra, cmp r8, #0x20",
        "0x43a7e32e y 0x43a7e6aa: copia de 32 B invirtiendo cada palabra",
    ],
    "fields": [
        {"off": "0x00", "name": "length", "type": "u32",
         "read": "0x4391caa0: ldr r1, [r4]",
         "write": "0x435d644c: str.w fp, [r8, sb]"},
        {"off": "0x04", "name": "Reserved2", "type": "u16",
         "read": "0x4391caaa: ldrh r1, [r4, #4]"},
        {"off": "0x06", "name": "flags", "type": "u8",
         "bits": {"0": "end_flag", "1": "PS_flag", "2": "EP_flag",
                  "3": "DTS_flag", "4-7": "Reserved1"},
         "read": ["0x4391cab2: ldrb r1, [r4, #6]; 0x4391cab6: and r1, r1, #1",
                  "0x4391cac4: ubfx r1, r1, #1, #1 (PS_flag)",
                  "0x4391cad2: ubfx r1, r1, #2, #1 (EP_flag)",
                  "0x4391cae0: ubfx r1, r1, #3, #1 (DTS_flag)",
                  "0x4391caee: lsrs r1, r1, #4 (Reserved1)"],
         "write": ["0x435d641a..0x435d6422: end_flag desde [r7,#3] bit7",
                   "0x435d6472..0x435d6478: orr #4 (EP_flag)"]},
        {"off": "0x07", "name": "Num_AUs", "type": "u8",
         "read": "0x4391caf8: ldrb r1, [r4, #7]",
         "write": "0x435d6448: strb r3, [r4, #7] (r3=1)"},
        {"off": "0x08", "name": "PTS", "type": "u32",
         "read": "0x4391cb02: ldr r1, [r4, #8]",
         "write": "0x435d64ae: str r2, [r4, #8]"},
        {"off": "0x0c", "name": "DTS", "type": "u32",
         "read": "0x4391cb0c: ldr r1, [r4, #0xc]"},
        {"off": "0x10", "name": "nextHRDBuffer", "type": "u32",
         "read": "0x4391cb16: ldr r1, [r4, #0x10]"},
        {"off": "0x14", "name": "nextPTS", "type": "u32",
         "read": "0x4391cb20: ldr r1, [r4, #0x14]"},
        {"off": "0x18", "name": "pic_parameter_set_id", "type": "u8",
         "read": "0x4391cb2a: ldrb r1, [r4, #0x18]"},
        {"off": "0x19", "name": "num_PPS", "type": "u8",
         "read": "0x4391cb34: ldrb r1, [r4, #0x19]"},
        {"off": "0x1a", "name": "seq_parameter_set_id / num_SPS", "type": "u8",
         "bits": {"0-4": "seq_parameter_set_id", "5-7": "num_SPS"},
         "read": ["0x4391cb3c..0x4391cb40: and r1, r1, #0x1f",
                  "0x4391cb4a..0x4391cb4e: lsrs r1, r1, #5"]},
        {"off": "0x1b", "name": "flags2", "type": "u8",
         "bits": {"0": "change_PPS_flag", "1": "change_SPS_flag",
                  "2": "Reserved4", "3": "Reffered_flag",
                  "4-6": "PictureType", "7": "Reserved3"},
         "read": ["0x4391cb56..0x4391cb5a: and r1, r1, #1",
                  "0x4391cb68: ubfx r1, r1, #1, #1",
                  "0x4391cb76: ubfx r1, r1, #2, #1",
                  "0x4391cb84: ubfx r1, r1, #3, #1",
                  "0x4391cb92: ubfx r1, r1, #4, #3 (PictureType)",
                  "0x4391cb9c..0x4391cba0: lsrs r1, r1, #7"]},
        {"off": "0x1c", "name": "size_PPS", "type": "u16",
         "read": "0x4391cbaa: ldrh r1, [r4, #0x1c]"},
        {"off": "0x1e", "name": "size_SPS", "type": "u16",
         "read": "0x4391cbb4: ldrh r1, [r4, #0x1e]"},
    ],
    "stream_words": [
        {"bytes": "0x00-0x03", "content": "length (BE)"},
        {"bytes": "0x04", "content": "Num_AUs"},
        {"bytes": "0x05", "content": "flags (+0x06: end/PS/EP/DTS/Reserved1)"},
        {"bytes": "0x06-0x07", "content": "Reserved2 (BE)"},
        {"bytes": "0x08-0x0b", "content": "PTS (BE)"},
        {"bytes": "0x0c-0x0f", "content": "DTS (BE)"},
        {"bytes": "0x10-0x13", "content": "nextHRDBuffer (BE)"},
        {"bytes": "0x14-0x17", "content": "nextPTS (BE)"},
        {"bytes": "0x18", "content": "flags2 (+0x1b)"},
        {"bytes": "0x19", "content": "seq_parameter_set_id/num_SPS (+0x1a)"},
        {"bytes": "0x1a", "content": "num_PPS (+0x19)"},
        {"bytes": "0x1b", "content": "pic_parameter_set_id (+0x18)"},
        {"bytes": "0x1c-0x1d", "content": "size_SPS (BE)"},
        {"bytes": "0x1e-0x1f", "content": "size_PPS (BE)"},
    ],
}

IDENTITIES = [
    {"func": "0x436150ce", "name": None,
     "role": "handler del comando de depuracion `augicsv` (a|v)",
     "evidence": ["0x436150e0 cita 0x43c6a25c 'Usage: augicsv <a(audio)|v(video)>'",
                  "0x43615108 cita 0x43c6a28a '[AUGI][PRINT] size[%d] %s'"]},
    {"func": "0x43615eac", "name": "DecExAugiConverter::Print",
     "evidence": ["0x43615ebc cita 0x43c6a8db 'virtual void DecExAugiConverter::Print(void*)'"]},
    {"func": "0x4361610c", "name": "DecInAudioAugiConverter::Print",
     "evidence": ["0x43616116 cita 0x43c6acc5 'virtual void DecInAudioAugiConverter::Print(void*)'"]},
    {"func": "0x43616200", "name": "DecInVideoAugiConverter::Print",
     "evidence": ["0x4361620a cita 0x43c6b02e 'virtual void DecInVideoAugiConverter::Print(void*)'"]},
    {"func": "0x436163c0", "name": "EncExAugiConverter::Print",
     "evidence": ["0x436163d2 cita 0x43c6b554 'virtual void EncExAugiConverter::Print(UInt16, const void*)'"]},
    {"func": "0x4391ca90", "name": None,
     "role": "volcado de depuracion del bloque (literales '[AUGI] length...size_SPS')",
     "evidence": ["0x4391ca96 cita 0x43cd993d '[AUGI] ----------------------------------'",
                  "0x4391cbb6 cita 0x43cd9c8d '[AUGI] size_SPS              = %d'",
                  "llamado desde 0x4391d12e y 0x4391d136"]},
]

# Vistas de depuracion de los converters de decodificacion: NO son la cabecera
# de 32 B del bloque, sino estructuras en memoria distintas.
DEC_VIEWS = {
    "0x43615eac": {
        "note": "recibe un stream de 32 B y lo invierte por palabra (0x43a7e32e)",
        "fields": {
            "0x00": "length", "0x04": "offset", "0x08": "flags (bit0 EP_flag, bits2-3 PTS_DTS_flag)",
            "0x09": "AUGI_type", "0x0a": "num_AUs", "0x0c": "PTS", "0x10": "DTS",
            "0x14": "STC_Offset_Sign", "0x15": "discontinuity_cc",
            "0x17": "bit4 end_flag / bit5 start_up_flag / bits0-3 discontinuity_flags",
            "0x18": "STC_Offset",
        }},
    "0x4361610c": {
        "note": "lee la estructura directamente (sin 0x43a7e32e)",
        "fields": {
            "0x00": "length", "0x08": "pts_dts_flag", "0x09": "augi_type",
            "0x0c": "pts", "0x10": "pts_33 (u8)", "0x1c": "stc_offset",
            "0x20": "stc_offset_33 (u8)", "0x21": "stc_offset_sign", "0x22": "end_flag",
        }},
    "0x43616200": {
        "note": "lee la estructura directamente (sin 0x43a7e32e); anade offset y los campos dts/e_ptm",
        "fields": {
            "0x00": "length", "0x04": "offset", "0x08": "pts_dts_flag", "0x09": "augi_type",
            "0x0c": "pts", "0x10": "pts_33 (u8)", "0x14": "dts", "0x18": "dts_33 (u8)",
            "0x1c": "stc_offset", "0x20": "stc_offset_33 (u8)", "0x21": "stc_offset_sign",
            "0x22": "end_flag", "0x24": "e_ptm", "0x28": "e_ptm_33 (u8)",
            "0x29": "stc_offset_sign_33", "0x2a": "end_flag_33",
        }},
}

with open(BIN, "rb") as fh:
    B = fh.read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def printable(c):
    return 32 <= c < 127


def strings_with_token(data):
    """Cadenas (normalizadas al inicio) que contienen `[AUGI]`."""
    seen = set()
    out = []
    start = 0
    while True:
        i = data.find(TOKEN, start)
        if i < 0:
            break
        s = i
        while s > 0 and printable(data[s - 1]):
            s -= 1
        e = i + len(TOKEN)
        while e < len(data) and printable(data[e]):
            e += 1
        if s not in seen:
            seen.add(s)
            out.append({"vaddr": f"0x{BASE + s:x}", "off": s,
                        "text": data[s:e].decode("latin1")})
        start = i + 1
    return sorted(out, key=lambda x: x["off"])


def ldr_sites(lo, hi):
    """[(addr, reg, literal_w)] de `ldr rX,[pc,#imm]` (T1 y T2 de 32 bits)."""
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 8:
            continue
        h = U16(B, o)[0]
        if (h & 0xF800) == 0x4800:                 # ldr rT, [pc, #imm5*4]
            reg, lit = (h >> 8) & 7, ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:               # ldr.w rT, [pc, #±imm12]
            # cubre las dos codificaciones: T2 = 0xF85F (offset negativo) y
            # T3 = 0xF8DF (offset positivo, la habitual en este firmware).
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm12
        else:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= N - 4:
            out.append((a, reg, U32(B, o2)[0]))
    return out


def add_sites(lo, hi):
    """[(addr, reg)] de los `add rX, pc` de 16 bits (`add rX, pc, #0`)."""
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400:
            rm = (h >> 3) & 0xF
            rd = (((h >> 7) & 1) << 3) | (h & 7)
            if rm == 15:
                out.append((a, rd))
    return out


def pic_refs(targets, starts, lo=BASE, hi=BASE + N):
    """destino -> [sitios] para los `targets` pedidos.

    Se empareja cada `add rX, pc` con el **`ldr rX,[pc,#imm]` inmediatamente
    anterior de la misma función** (mismo prólogo Thumb). Reglas:

    * solo el `ldr` más cercano del mismo registro: el compilador nunca
      intercala otro `ldr` del mismo registro entre la carga del offset y el
      `add`; probar candidatos más lejanos produce colisiones reales (el mismo
      offset relativo sirve para varias cadenas de la misma zona),
    * el `ldr` debe caer en la misma función (si no, se abandona),
    * el destino debe ser exactamente una de las cadenas pedidas.

    Con esto los sitios son únicos: ningún sitio resuelve a dos cadenas.
    """
    def func_of(a):
        i = bisect.bisect_right(starts, a) - 1
        return starts[i] if i >= 0 else None

    by_reg = defaultdict(list)
    for a, reg, w in ldr_sites(lo, hi):
        by_reg[reg].append((a, w))
    keys = {}
    for reg, v in by_reg.items():
        v.sort()
        keys[reg] = [x[0] for x in v]
    out = defaultdict(list)
    for a, reg in add_sites(lo, hi):
        v = by_reg.get(reg)
        if not v:
            continue
        fn = func_of(a)
        i = bisect.bisect_right(keys[reg], a - 2) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP or func_of(la) != fn:
            continue
        t = (w + (a + 4)) & 0xFFFFFFFF
        if t in targets:
            out[t].append(a)
    return {k: sorted(set(v)) for k, v in out.items()}


def prologues(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = U16(B, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def main():
    strings = strings_with_token(B)
    targets = {int(s["vaddr"], 16) for s in strings}
    starts = prologues(BASE, 0x43A00000)
    refs = pic_refs(targets, starts)

    def container(site):
        cand = [x for x in starts if x <= site and site - x <= 0x4000]
        return cand[-1] if cand else None

    by_func = defaultdict(list)
    for s in strings:
        v = int(s["vaddr"], 16)
        s["refs"] = [f"0x{x:x}" for x in refs.get(v, [])]
        s["funcs"] = sorted({f"0x{container(x):x}" for x in refs.get(v, [])
                             if container(x)})
        for f in s["funcs"]:
            by_func[f].append(v)

    with open(A7S, "rb") as fh:
        a7s = fh.read()
    a7s_strings = strings_with_token(a7s)
    a7s_texts = {s["text"] for s in a7s_strings}
    solo_a6000 = [s["text"] for s in strings if s["text"] not in a7s_texts]
    solo_a7s = [s["text"] for s in a7s_strings if s["text"] not in {x["text"] for x in strings}]

    out = {
        "milestone": "S117",
        "module": "AUGI",
        "counts": {
            "strings": len(strings),
            "referenced": sum(1 for s in strings if s["refs"]),
            "ref_sites": sum(len(s["refs"]) for s in strings),
            "functions": len(by_func),
            "a7s_strings": len(a7s_strings),
            "a7s_comunes": len(strings) - len(solo_a6000),
            "a7s_solo_a6000": len(solo_a6000),
            "a7s_solo_a7s": len(solo_a7s),
        },
        "strings": strings,
        "functions": [{"func": f, "n_strings": len(v),
                       "strings": [f"0x{x:x}" for x in sorted(v)]}
                      for f, v in sorted(by_func.items())],
        "a7s": {"solo_a6000": solo_a6000, "solo_a7s": solo_a7s,
                "strings": a7s_strings},
        "layout": LAYOUT,
        "identities": IDENTITIES,
        "dec_views": DEC_VIEWS,
        "writers": {
            "api_entry": {"func": "0x4360b6f0",
                          "evidence": "0x4360b712 y 0x4360b73e citan 0x43c66fbf "
                                      "'void StrmEngEncCIIf::CodecEventCreateVAUGI(UInt32, const UInt32*)'"},
            "audio": {"func": "0x435d63a0",
                      "evidence": ["0x435d640c: lsl.w r8, r2, #5",
                                   "0x435d644c: str.w fp, [r8, sb] (length)",
                                   "0x435d64e8..0x435d6500: rev por palabra y volcado de 32 B"]},
            "wrappers": ["0x43a5cb26: bl 0x435d63a0 en 0x43a5cb4c",
                         "0x43a5d182: bl 0x435d63a0 en 0x43a5d1a8"],
        },
    }
    with open(os.path.join(HERE, "augi_strings_raw.json"), "w") as fh:
        json.dump({"module": "AUGI", "count": len(strings), "strings": strings},
                  fh, indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "augi_refs.json"), "w") as fh:
        json.dump({f"0x{k:x}": v for k, v in sorted(refs.items())}, fh, indent=0)
    with open(os.path.join(HERE, "augi.json"), "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)

    print(out["counts"])
    print(f"referenciadas: {out['counts']['referenced']}/{len(strings)}, "
          f"funciones: {len(by_func)}")
    for s in strings:
        print(s["vaddr"], len(s["refs"]), s["text"][:80])


if __name__ == "__main__":
    main()
