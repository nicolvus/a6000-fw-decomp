"""S66-B: genera analysis/s66/lensfile_format.json.

Fuentes verificadas:
- firmware/extracted/fw321/firmware.tar_unpacked/0800_appli/lens/VX*.bin (A6000 fw321)
- firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0800_appli/lens/VX*.bin
- tarjetas de nombres en av-cam.bin A6000 (VA = base 0x43541000 + fileoff VERIFICADO)
  y av-cam.bin A6300 (solo fileoff VERIFICADO; base de carga NO_VERIFICADO).
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
back = ROOT / "firmware/extracted"
DAV = 0x43541000
AVCAM = {
    "A6000-fw321": back / "fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300-fw201": back / "a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
DIRS = {
    "A6000-fw321": back / "fw321/firmware.tar_unpacked/0800_appli/lens",
    "A6300-fw201": back / "a6300-fw201/payload/firmware.tar_unpacked/0800_appli/lens",
}


def sections(b):
    out = []
    off = 0x10
    while off + 8 <= len(b) - 4:
        magic = b[off:off + 2].decode("latin1", "replace")
        hdr_len = struct.unpack_from("<H", b, off + 2)[0]
        plen = struct.unpack_from("<I", b, off + 4)[0]
        out.append({"magic": magic, "hdr_off": off, "hdr_len": hdr_len,
                    "payload_off": off + hdr_len, "payload_len": plen,
                    "payload_sha256": hashlib.sha256(b[off + hdr_len:off + hdr_len + plen]).hexdigest()})
        off += hdr_len + plen
    return out


def parse_file(path):
    b = path.read_bytes()
    lid = struct.unpack_from("<H", b, 12)[0]
    secs = sections(b)
    ed = next((s for s in secs if s["magic"] == "ED"), None)
    cs = next((s for s in secs if s["magic"] == "CS"), None)
    lc = next((s for s in secs if s["magic"] == "LC"), None)
    return {
        "vx": f"VX{lid:04X}",
        "name": path.name,
        "path_rel": str(path.relative_to(ROOT)),
        "size": len(b),
        "header": {
            "magic": "LF",
            "hdr_len_u16@2": struct.unpack_from("<H", b, 2)[0],
            "size_u32@4": struct.unpack_from("<I", b, 4)[0],
            "const_u32@8": struct.unpack_from("<I", b, 8)[0],
            "lens_id_u16@12": lid,
            "u16@14": struct.unpack_from("<H", b, 14)[0],
        },
        "lens_id": lid,
        "size_field_matches_size_minus_header": struct.unpack_from("<I", b, 4)[0] == len(b) - 0x10,
        "sha256": hashlib.sha256(b).hexdigest(),
        "checksum_u32_end": struct.unpack_from("<I", b, len(b) - 4)[0],
        "checksum_algo": "NO_VERIFICADO",
        "sections": secs,
        "ed_prelude_u16@0x18": list(struct.unpack_from("<8H", b, 0x18)) if ed else None,
        "lc_payload_u16": list(struct.unpack_from("<6H", b, lc["payload_off"])) if lc else None,
        "ed_sha": ed["payload_sha256"] if ed else None,
    }


def read_slot_table(model, fileoff0, nslots, stride=0x42, prefix="A"):
    blob = AVCAM[model].read_bytes()
    slots = []
    for k in range(nslots):
        a = fileoff0 + stride * k
        key = struct.unpack_from("<H", blob, a)[0]
        name = blob[a + 2:a + 2 + 32].split(b"\x00")[0].decode("latin1")
        entry = {"k": f"{prefix}{k}", "key": key, "path": name, "fileoff": a}
        if model == "A6000-fw321":
            entry["va"] = DAV + a
        slots.append(entry)
    return slots


def read_slot_table_A6300():
    model = "A6300-fw201"
    blob = AVCAM[model].read_bytes()
    out = read_slot_table(model, 0x7C826A, 18, prefix="A")
    fa = 0x7C870E
    out.append({"k": "fixed", "key": struct.unpack_from("<H", blob, fa)[0], "path": blob[fa + 2:fa + 2 + 32].split(b"\x00")[0].decode("latin1"), "fileoff": fa})
    out += read_slot_table(model, 0x7C8750, 22, prefix="B")
    return out


data = {
    "meta": {
        "task": "s66/subtarea B: formato VX*_lensfile.bin + tablas en av-cam.bin + cargador",
        "date": "2026-10-20",
        "avcam_base": {
            "A6000-fw321": DAV,
            "A6300-fw201": None,
        },
        "direccionamiento": (
            "A6000: VA = 0x43541000 + fileoff, VERIFICADO por sesiones previas (entry_point). "
            "A6300: solo fileoff verificado (pool PIC loop interno); base de carga NO_VERIFICADA."),
        "flags": {
            "VERIFICADO": "cabecera/secciones/trailer/tamano/lens_id/tablas/literal del parser/instrucciones citadas",
            "INFERENCIA": "los datos ED/CS/LC son tablas u16 opticas; VX9103/VX9123 = mismo optico; 18 ficheros identicos byte a byte entre A6000 y A6300",
            "NO_VERIFICADO": "semantica exacta de los datos; algoritmo del trailer (4 B tras LC); significado de u32@8 (0xB/0xE/0xC); A-mount mapping",
        },
    },
    "formato_fichero": {
        "header_len": 16,
        "header_fields": {
            "off": "campo (endianness LE)",
            "0x00": "magic 'LF' (u16 LE 0x464c; comparado literal 0x464c en parser 0x43907c7c)",
            "0x02": "u16 header_len = 0x0010 (VERIFICADO en parser 0x43907c7c: consume hdr[u16@2] bytes)",
            "0x04": "u32 payload_size = filesize - 0x10 (igual en los 57 ficheros A6000+A6300; NO es el tamaño total)",
            "0x08": "u32 0xB en 16/18 ficheros A6000; VX9111=0xE, VX9116=0xC (semántica NO_VERIFICADA)",
            "0x0c": "u16 lens_id (0x9101..0x9129, coincide con el nombre VX91xx; VERIFICADO)",
            "0x0e": "u16 0",
        },
        "section_layout": "[ magic u16 ][ hdr_len u16 = 8 ][ payload_len u32 ][ payload(hdr_len=8)+payload_len bytes ]",
        "section_magics": {
            "ED (0x4445 'ED')": "payload tabla u16 (0x5c..0x32a4 B según lente); parser av-cam 0x43907c7c salta a 0x43907f54 (setup accessor + 0x43b2bf88)",
            "CS (0x5343 'CS')": "payload tabla u16 (0x38..0xc0 B)",
            "LC (0x434c 'LC')": "payload 12 B = 6 x u16, en TODOS los ficheros",
        },
        "trailer": "4 bytes tras LC en los 57 ficheros (cadena ED->CS->LC acaba en filesize-4; algoritmo NO_VERIFICADO: crc32/adler/sum/fnv descartados)",
        "orden_secciones": "todos los ficheros: HDR(16) + ED + CS + LC + trailer(4), sin excepción (A6000: 18/18; A6300: 39/39)",
        "identificativos": {
            "2 bytes": "lens_id en 0x0c..0x0d",
            "4 bytes": "trailer",
            "pares": "VX9103/VX9123 difieren SOLO en lens_id@0x0c y 1 byte del trailer (datos ED+CS+LC idénticos)",
            "A6000=A6300": "los 18 ficheros VX91xx de A6000 son byte a byte idénticos a los de A6300",
        },
    },
    "ficheros": {},
    "pares_ED_identico": {},
    "slots_avcam": {
        "A6000-fw321": {
            "table_fileoff": 0x6E1BF2,
            "table_va": 0x43C22BF2,
            "nslots": 18,
            "stride": 0x42,
            "layout": "[u16 key][char path '/lens/VX%s_lensfile.bin' NUL-padded]",
            "keys": "0x8011..0x802d (semántica NO_VERIFICADA)",
            "lookup_fn": "0x43907bc4 (único bl desde 0x43b2a846)",
            "slots": read_slot_table("A6000-fw321", 0x6E1BF2, 18),
        },
        "A6300-fw201": {
            "table_va": None,
            "lookup_fn": "dos tablas; fileoff relativos al blob (base de carga NO_VERIFICADA): "
                         "tabla A: base 0x7C826A, 18 slots (bucle fileoff 0x44c10e..0x44c11e, cmp r2,#0x12), "
                         "claves 0x8011..0x802d, paths VX9101..VX9129; "
                         "slot 'fixed': clave 0xFFFF comprobada en fileoff 0x44c122..0x44c126 (cmp r1,#0xffff), "
                         "entrada en 0x7C870E con path '/lens/fixed_lensfile.bin' en 0x7C8710 (k=18, base_A+0x4A4); "
                         "tabla B: base 0x7C8750 (tabla_A+0x4E4), 22 slots (bucle fileoff 0x44c130..0x44c14a, cmp r2,#0x16), "
                         "claves 0x0020..0x0046, paths VX89xx/VX920x (VX8905 repetida en 0x35 y 0x45)",
            "slots": read_slot_table_A6300(),
        },
        "A7S-fw320": "ABSENTE: 0 hits de b'/lens/V', b'lensfile', b'VX9' y del patrón de bucle (movs r0,#0x42+mla) en su av-cam.bin; su firmware tampoco incluye un dir lens/",    },
    "codigo_A6000": {
        "tabla_nombres": {"va": 0x43C22BF2, "fileoff": 0x6E1BF0},
        "lookup_fn": 0x43907BC4,
        "lookup_instruccion": "ldrh r4,[r3,r0](lit+pc -> 0x43C22BF2); cmp r4,r1; mla 0x42; adds r0,#2",
        "lookup_caller": 0x43B2A846,
        "caller_chain": [0x436E1328, 0x43721B34, 0x43902FBC, 0x43B2CACC, 0x43904FB0, 0x43B2A7E2, 0x43907BC4],
        "parser_main": 0x43907C7C,
        "parser_stream": 0x43904CFC,
        "ed_setup": 0x43907F54,
        "ed_next": 0x43907F9C,
        "tlv_reader": 0x43B2BF88,
        "log_err_va": 0x43C9AE7E,
        "log_err_func": 0x43721624,
    },
}

for tag, d in DIRS.items():
    rows = []
    for f in sorted(d.glob("VX*_lensfile.bin")):
        rows.append(parse_file(f))
    data["ficheros"][tag] = rows

ids = {}
for tag, rows in data["ficheros"].items():
    for r in rows:
        ids.setdefault(r["ed_sha"], []).append(f"{tag}/{r['name']}")
data["pares_ED_identico"] = {k: v for k, v in ids.items() if len(v) > 1}

out = Path(__file__).resolve().parent / "lensfile_format.json"
out.write_text(json.dumps(data, indent=1, ensure_ascii=False))
print("escrito", out, out.stat().st_size)
