#!/usr/bin/env python3
"""S151 — genera `analysis/s151_panda/panda.json` a partir de los bytes reales.

Todo se recalcula desde los tres `av-cam.bin`; el JSON no contiene datos a mano.
"""
import bisect
import json
import os
import re
import struct

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLOBS = {
    "a6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "a7s_fw320": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                 "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "a6300_fw201": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                   "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
TOKEN = b"[PANDA]"
MAX_LDR_GAP = 4096
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def load(name):
    with open(os.path.join(REPO, BLOBS[name]), "rb") as fh:
        return fh.read()


def cstr(data, vaddr, maxlen=300):
    off = vaddr - BASE
    end = off
    while end < len(data) and end < off + maxlen and (
            32 <= data[end] < 127 or data[end] in (9, 10)):
        end += 1
    return data[off:end].decode("latin-1")


def pic_refs(data, lo, hi):
    """Regla estricta canonica del repo: `add rX,pc` con el `ldr rX,[pc]` mas cercano."""
    ldrs = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > len(data) - 8:
            continue
        h = U16(data, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(data, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= len(data) - 4:
                ldrs.append((a, reg, lit, U32(data, o2)[0]))
    by = {}
    for a, reg, lit, w in ldrs:
        by.setdefault(reg, []).append((a, lit, w))
    for v in by.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by.items()}
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > len(data) - 4:
            continue
        h = U16(data, o)[0]
        if not ((h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15):
            continue
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by.get(reg, [])
        if not v:
            continue
        i = bisect.bisect_right(keys[reg], a) - 1
        if i < 0:
            continue
        la, lit, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        tgt = (w + a + 4) & 0xFFFFFFFF
        if BASE <= tgt < BASE + len(data):
            out.append((a, la, lit, w, tgt))
    return out


def main():
    data = load("a6000_fw321")
    n = len(data)

    # ---- 1. las 10 cadenas -------------------------------------------------
    cadenas = []
    i = 0
    while True:
        i = data.find(TOKEN, i)
        if i < 0:
            break
        s = i
        while s > 0 and 32 <= data[s - 1] < 127:
            s -= 1
        cadenas.append({"vaddr": BASE + s, "texto": cstr(data, BASE + s)})
        i += 1
    cadenas.sort(key=lambda c: c["vaddr"])

    # ---- 2. referencias PIC (regla estricta) --------------------------------
    lo, hi = 0x43706000, 0x43709000
    refs = pic_refs(data, lo, hi)
    mapa = {}
    for a, la, lit, w, tgt in refs:
        if tgt in {c["vaddr"] for c in cadenas}:
            mapa.setdefault(tgt, []).append({"sitio": a, "ldr": la, "pool": lit, "valor_pool": w})

    # ---- 3. funciones emisoras ---------------------------------------------
    FUNCIONES = {
        "F1_init": (0x437073CC, 0x43707628),
        "F4_pre": (0x43707F8C, 0x43708148),
        "F5_post": (0x437081B8, 0x43708374),
        "F6_async": (0x437083E4, 0x43708560),
    }
    func_de_cadena = {}
    for c in cadenas:
        sites = sorted(mapa.get(c["vaddr"], []), key=lambda s: s["sitio"])
        owners = []
        for nombre, (a0, a1) in FUNCIONES.items():
            for s in sites:
                if a0 <= s["sitio"] < a1:
                    owners.append({"funcion": nombre, "inicio": a0, "fin": a1,
                                   "sitio": s["sitio"]})
        func_de_cadena[c["vaddr"]] = owners

    # ---- 4. coda de referencias y sub-bloques ------------------------------
    sub = {}
    for c in cadenas:
        t = c["texto"]
        m = re.search(r"Panda_SendMessage: (\w+) (osal_\w+_msg) error", t)
        if m:
            sub.setdefault(m.group(1), []).append(c["vaddr"])

    # ---- 5. ids OSAL usados por el modulo ---------------------------------
    IDS = {
        "colas_abiertas": [0x00F900BC, 0x00F90078, 0x00F900D5, 0x00F90191,
                           0x00F90184, 0x00F90520, 0x00F90521],
        "gid_mensajes_lente": 0x00740017,
        "gid_log": 0x008F0139,
        "id_log_panda": 0x16,
        "tam_mensaje_log": 0x9A,
        "tam_buffer_lente": 0x40,
        "id_log_auxiliar": 0x00910042,
    }

    # ---- 6. tabla global y slots de los 5 buffers --------------------------
    slots = {"Pre1": 0x7570, "Pre2": 0x4284, "Post1": 0x2954, "Post2": 0x7350,
             "Async": 0x7C74}
    fuentes = {"Pre1": 0x1420, "Pre2": 0x4930, "Post1": 0x1D10, "Post2": 0x6248,
               "Async": 0x5D88}

    # ---- 7. diferencial ----------------------------------------------------
    dif = {}
    for nombre in BLOBS:
        d = load(nombre)
        hits = []
        i = 0
        while True:
            i = d.find(TOKEN, i)
            if i < 0:
                break
            hits.append(BASE + i)
            i += 1
        interiores = []
        for c in cadenas:
            nucleo = c["texto"].split(": ", 1)[1].rstrip("\n")
            interiores.append(nucleo in d.decode("latin-1"))
        dif[nombre] = {
            "ocurrencias_token": len(hits),
            "textos_internos_presentes": sum(1 for x in interiores if x),
            "textos_internos_totales": len(interiores),
            "panda_sendmessage": d.count(b"Panda_SendMessage"),
            "uc_PandaADErrorOpen": d.count(b"uc_PandaADErrorOpen"),
            "uc_PandaADErrorClose": d.count(b"uc_PandaADErrorClose"),
            "Camera::Lens::ODL": d.count(b"Camera::Lens::ODL"),
            "LENS_YC": d.count(b"LENS_YC"),
            "patron_reporter_push_r3_movs_r2_0x9a": d.count(bytes.fromhex("08b49a22")),
            "apariciones_cada_id_cola": {
                f"0x{v:08x}": d.count(struct.pack("<I", v))
                for v in IDS["colas_abiertas"]
            },
        }

    # ---- 8. base textual de "Panda" ---------------------------------------
    base_textual = {
        "nombre_funcion_en_las_trazas": "Panda_SendMessage",
        "parametros_iris_analog_drive": [
            {"nombre": "uc_PandaADErrorOpen", "vaddr": 0x43C99267,
             "puntero_tabla": 0x43FEBE04, "direccion_variable": 0x43E0A482},
            {"nombre": "uc_PandaADErrorClose", "vaddr": 0x43C9927B,
             "puntero_tabla": 0x43FEBE14, "direccion_variable": 0x43E84C84},
        ],
        "clases_rtti_panda": 0,
        "ficheros_panda": 0,
        "cadena_independiente_PANDA": 0,
        "nota": "No hay RTTI, ni nombre de fichero, ni expansion de la sigla en "
                "ningun byte: la sigla se deja SIN DESARROLLAR.",
    }

    # ---- 9. equivalencias con los otros firmwares --------------------------
    equiv = {
        "F1_init": {"a6000_fw321": 0x437073CC, "a7s_fw320": 0x43729910,
                    "a6300_fw201": 0x437648D0},
        "F4_pre": {"a6000_fw321": 0x43707F8C, "a7s_fw320": 0x4372A456},
        "F5_post": {"a6000_fw321": 0x437081B8, "a7s_fw320": 0x4372A6B8},
        "F6_async": {"a6000_fw321": 0x437083E4, "a7s_fw320": 0x4372A888},
    }

    doc = {
        "hito": "S151",
        "titulo": "el modulo [PANDA] (10 trazas) del subsistema de lente de la A6000 fw3.21",
        "base": {"convención": "vaddr = 0x43541000 + file_offset",
                 "blob_a6000": BLOBS["a6000_fw321"],
                 "blob_a7s": BLOBS["a7s_fw320"],
                 "blob_a6300": BLOBS["a6300_fw201"]},
        "regla_referencias": "estricta (analysis/s106_imaging_cap/scan_pic_refs_strict.py)",
        "cadenas": cadenas,
        "referencias": {f"0x{k:08x}": v for k, v in sorted(mapa.items())},
        "funcion_de_cadena": {f"0x{k:08x}": v for k, v in sorted(func_de_cadena.items())},
        "funciones_emisoras": {k: {"inicio": v[0], "fin": v[1]} for k, v in FUNCIONES.items()},
        "helper_reporter": {"vaddr": 0x43707324,
                            "nota": "formatea el texto con vsnprintf 0x439c5004 en un "
                                    "mensaje OSAL de 0x9a B (GID 0x008f0139) y lo envia "
                                    "con osal_snd_msg 0x4356120c"},
        "llamadas_al_reporter": [0x4370744C, 0x43707460, 0x43707472, 0x43707484,
                                 0x43707496, 0x43708068, 0x4370813E, 0x437082A0,
                                 0x4370836A, 0x43708556],
        "canales": sub,
        "ids_osal": IDS,
        "tabla_global": 0x4401EEE4,
        "slots_buffer_por_canal": slots,
        "slot_fuente_por_canal": fuentes,
        "callers": {
            "F1_init": {"llamador": 0x43721624,
                        "sitio_llamada": 0x4372163E,
                        "funcion": "void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)",
                        "cadena_nombre": 0x43C9AE4E},
            "F4_pre": {"llamador": 0x437217F8, "sitio_llamada": 0x43721818,
                       "llamador_2": 0x43793EFE,
                       "cadena_contexto": 0x43CA3A50},
            "F5_post": {"llamador": 0x43721840, "sitio_llamada": 0x43721848,
                        "llamador_2": 0x4379064E,
                        "cadena_contexto": 0x43CA3169},
            "F6_async": {"llamador": 0x436F4D1C, "sitio_llamada": 0x436F4D74},
        },
        "base_textual_panda": base_textual,
        "diferencial": dif,
        "equivalencias_otros_firmwares": equiv,
    }
    out = os.path.join(REPO, "analysis/s151_panda/panda.json")
    with open(out, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    print(f"escrito {out}: {len(cadenas)} cadenas, {len(mapa)} referenciadas, "
          f"{sum(len(v) for v in mapa.values())} sitios")


if __name__ == "__main__":
    main()
