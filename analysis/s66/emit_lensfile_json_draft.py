"""S66-B: genera analysis/s66/lensfile_format.json.

Fuentes verificadas:
- firmware/extracted/fw321/firmware.tar_unpacked/0800_appli/lens/VX*.bin (A6000 fw321)
- firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0800_appli/lens/VX*.bin
- tabla de nombres en av-cam.bin A6000 (base 0x43541000, fileoff = VA-0x43541000)
  y av-cam.bin A6300 (fileoff verificado; base de carga NO_VERIFICADO).
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
back = ROOT / "firmware/extracted"
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
    prelude = list(struct.unpack_from("<4H", b, 0x18)) if ed else None
    lc_payload = list(struct.unpack_from("<6H", b, lc["payload_off"])) if lc else None
    return {
        "vx": lid,
        "name": path.name,
        "path_rel": str(path.relative_to(ROOT)),
        "size": len(b),
        "size_field": struct.unpack_from("<I", b, 4)[0],
        "u8_field": struct.unpack_from("<I", b, 8)[0],
        "lens_id": lid,
        "header": {"magic": "LF", "ver16": struct.unpack_from("<H", b, 2)[0],
                    "size": struct.unpack_from("<I", b, 4)[0],
                    "const11": struct.unpack_from("<I", b, 8)[0],
                    "lens_id": lid},
        "sha256": hashlib.sha256(b).hexdigest(),
        "checksum_end": struct.unpack_from("<I", b, len(b) - 4)[0],
        "sections": secs,
        "ed_prelude_u16": prelude,
        "lc_payload_u16": lc_payload,
        "ed_sha": ed["payload_sha256"] if ed else None,
    }


def read_slot_table(model, fileoff0, nslots, stride=0x42, base=0x43541000):
    blob = {
        "A6000-fw321": back / "fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
        "A6300-fw201": back / "a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    }[model].read_bytes()
    slots = []
    for k in range(nslots):
        a = fileoff0 + stride * k
        key = struct.unpack_from("<H", blob, a)[0]
        name = blob[a + 2:a + 2 + 32].split(b"\x00")[0].decode("latin1")
        slots.append({"k": k, "key": key, "path": name, "fileoff": a,
                      "va_supuesto": base + a if model == "A6000-fw321" else None})
    return slots


data = {
    "meta": {
        "task": "s66/B formato VX91xx_lensfile.bin + tabla + cargador en av-cam.bin",
        "date": "2026-10-20",
        "base_a6000_avcam": 0x43541000,
        "nota_direcciones": ("A6000: VA = base + fileoff (base 0x43541000 verificado en el proyecto). "
                             "A6300: solo fileoff verificado internamente (pool<<add pc); base de carga NO_VERIFICADO."),
        "riqueza": {"VERIFICADO": "contra bytes reales del firmware; ver lensfile_format.md",
                    "reload": "xED prelude/CS/Chech NO_VERIFICADO"},
    },
    "formato_fichero": {
        "header_len": 16,
        "fields": {
            "0x00 magic": "'LF' (0x464c LE)",
            "0x02 u16": "header_len = 0x0010 (VERIFICADO: parser 0x43907c7c compara/consume este valor)",
            "0x04 u32": "file size (coincide con tamaño real en los 18+21 ficheros)",
            "0x08 u32": "constante 0x0000000b en todos los ficheros (semántica NO_VERIFICADO)",
            "0x0c u16": "lens_id 0x8xxx/0x9xxx (= VX código del fichero)",
            "0x0e u16": "0",
        },
        "sections": {
            "layout": "repetidas: [magic u16][hdr_len u16=8][payload_len u32][payload]",
            "ED": "0x4445 ('ED'); datos u16 (aberración/distorsión, NO_VERIFICADO semántica)",
            "CS": "0x5343; prelude copiado del ED + tabla u16 ascendente (NO_VERIFICADO)",
            "LC": "0x434c; 6 x u16",
            "fin": "tras LC: checksum u32 (algoritmo NO_VERIFICADO; los 18 valores están en checksum_end)",
        },
    },
    "ficheros": {},
    "slots_avcam": {
        "A6000-fw321": {
            "table_fileoff": 0x6E1BF0,
            "table_va": 0x43C22BF2,
            "stride": 0x42,
            "slots": read_slot_table("A6000-fw321", 0x6E1BF0, 18),
            "lookup": "FUN_43907bc4 (bl desde 0x43b2a846); cmp r2,#0x12",
        },
        "A6300-fw201": {
            "table_fileoff": 0x7C826A,
            "table_va": None,
            "stride": 0x42,
            "slots": read_slot_table("A6300-fw201", 0x7C826A, 41),
            "lookup": "bucle fileoff 0x44c108-0x44c156: key==0xffff -> '/lens/fixed_lensfile.bin' (slot k=18); "
                      "sección VX9xxx: slots 0..17 (cmp #0x12); sección A-mount: slots 19..40 (cmp #0x16)",
        },
        "A7S-fw320": "SIN tabla: 0 hits de '/lens/VX', 'lensfile', 'VX9' en av-cam.bin (len 0xaecbb8)",
    },
    "codigo_A6000": {
        "tabla_nombres":({"va": 0x43C22BF2, "fileoff": 0x6E1BF0}, ),
        "lookup_fn": 0x43907BC4,
        "lookup_caller": 0x43B2A846,
        "chaim": [0x436E1328, {"name": "ODL job", "addr": 0x43B2CACC}, 0x43904FB0, 0x43B2A7E2, 0x43907BC4],
        "parser": 0x43907C7C,
        "parser_stream_variant": 0x43904CFC,
        "ed_setup": 0x43907F54,
        "ed_next_record": 0x43907F9C,
        "tlv_reader": 0x43B2BF88,
        "registro_fila": 0x43B2C0C0,
        "log_err": "0x43c9ae7e '[LENS_YC]: %s: LoadLensAberrationData error (0x%x)' usada en 0x43721718 (func 0x43721624)",
    },
    "pares_rep": {"ED/CS/CHEC identical": ["VX9103==VX9123 (ED,CS,LC idénticos, sha256 sección iguales)"]},
}

for tag, d in DIRS.items():
    rows = []
    for f in sorted(d.glob("VX*_lensfile.bin")):
        rows.append(parse_file(f))
    data["ficheros"][tag] = rows

# detección de grupos con ED idéntico
ids = {}
for tag, rows in data["ficheros"].items():
    for r in rows:
        ids.setdefault(r["ed_sha"], []).append(f"{tag}:{r['name']}")
data["pares_rep"] = {k: v for k, v in ids.items() if len(v) > 1}

out = Path(__file__).resolve().parent / "lensfile_format.json"
out.write_text(json.dumps(data, indent=1, ensure_ascii=False))
print("escrito", out)
