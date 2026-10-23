#!/usr/bin/env python3
"""S347 - verificador independiente de `odl_field.json`.

Re-decodifica TODO desde los binarios sin usar `build_odl_field.py` ni capstone
para las comprobaciones clave:

  * las instrucciones se identifican por **bytes exactos** (p. ej. `0d22` =
    `movs r2,#0xd`, `4482` = `strh r4,[r0,#0x12]`, `1823` = `movs r3,#0x18`);
  * las tablas se re-reconstruyen con `struct` y se comprueba su terminador;
  * las bases PIC se re-calculan con la formula `literal + (add+4 & ~1)`;
  * los pares `{id,0x000d}` y la lista de ids se re-cuentan;
  * el fichero `LensAberrationData.bin` se re-hashea y se busca en el la tabla
    `{id,0x000d}` y la lista de ids (deben ser ausencias).

Uso:  .venv/bin/python analysis/s347_odl_field/verify_odl_field.py
Salida: "N comprobaciones OK" o la primera discrepancia (exit 1).
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FW = ROOT / "firmware/extracted"
BLOBS = {
    "a7s_fw320": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/"
                       "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6000_fw321": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300_fw201": FW / ("a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/"
                         "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
LENSBIN = {
    "a7s_fw320": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/"
                       "nflasha3_unpacked_unpacked/lensbin_lensproperty/LensAberrationData.bin"),
    "a6000_fw321": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/lensbin_lensproperty/LensAberrationData.bin"),
    "a6300_fw201": FW / ("a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/lensbin_lensproperty/LensAberrationData.bin"),
}
DATA = json.loads((HERE / "odl_field.json").read_text(encoding="utf-8"))
CHECKS = 0


def check(cond: bool, msg: str) -> None:
    global CHECKS
    CHECKS += 1
    if not cond:
        raise SystemExit(f"FALLO #{CHECKS}: {msg}")


def read(addr: int, size: int, blob: bytes) -> bytes:
    off = addr - BASE
    check(0 <= off and off + size <= len(blob), f"0x{addr:08x} fuera del blob")
    return blob[off:off + size]


def u16(addr: int, blob: bytes) -> int:
    return struct.unpack("<H", read(addr, 2, blob))[0]


def u32(addr: int, blob: bytes) -> int:
    return struct.unpack("<I", read(addr, 4, blob))[0]


def find_all(blob: bytes, pattern: bytes) -> list[int]:
    out: list[int] = []
    i = blob.find(pattern)
    while i >= 0:
        out.append(BASE + i)
        i = blob.find(pattern, i + 1)
    return out


def pic_base(blob: bytes, ldr: int, add: int) -> int:
    h = u16(ldr, blob)
    check((h & 0xF800) == 0x4800, f"0x{ldr:08x} no es ldr pc-rel")
    lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    h2 = u16(add, blob)
    check((h2 & 0xFF00) == 0x4400, f"0x{add:08x} no es add rD,pc")
    check((h2 & 7) == ((h >> 8) & 7), f"0x{add:08x} no usa el registro del ldr")
    return (u32(lit, blob) + ((add + 4) & ~1)) & 0xFFFFFFFF


def ids_at(blob: bytes, table: int, entries: int) -> list[tuple[int, int]]:
    return [(u16(table + 4 * i, blob), u16(table + 4 * i + 2, blob))
            for i in range(entries)]


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    models = DATA["models"]

    # 1. firmware hashes
    for k, p in BLOBS.items():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        check(DATA["firmware"][k]["sha256"] == h, f"sha256 de {k}")
        check(DATA["firmware"][k]["size"] == len(blobs[k]), f"tamano de {k}")

    # 2. tabla, terminador y campo constante
    for k, m in models.items():
        blob = blobs[k]
        table = int(m["table"]["address"], 16)
        n = m["table"]["entries"]
        check(DATA["cross_model"]["entries"][k] == n, f"{k}: nº de entradas")
        pairs = ids_at(blob, table, n)
        check([p[1] for p in pairs] == [0x000D] * n, f"{k}: segundo campo != 0x000d")
        check([p[0] for p in pairs] == m["table"]["ids"], f"{k}: lista de ids")
        # terminador: la entrada n ya no es {id,0x000d}
        check(u16(table + 4 * n + 2, blob) != 0x000D, f"{k}: terminador de la tabla")
        # el contenido del campo 0x000d (la propia tabla) sigue siendo el esperado
        check(m["table"]["second_fields"] == [0x000D], f"{k}: second_fields")

    # 3. dos bases PIC a la tabla, cero literales absolutos
    for k, m in models.items():
        blob = blobs[k]
        table = int(m["table"]["address"], 16)
        sites = []
        for off in range(0, len(blob) - 8, 2):
            h = struct.unpack_from("<H", blob, off)[0]
            if (h & 0xF800) != 0x4800:
                continue
            rd = (h >> 8) & 7
            lit = ((BASE + off + 4) & ~3) + ((h & 0xFF) * 4)
            if lit - BASE + 4 > len(blob):
                continue
            word = struct.unpack_from("<I", blob, lit - BASE)[0]
            for kk in (2, 4, 6, 8):
                a = BASE + off + kk
                if a - BASE + 2 > len(blob):
                    break
                h2 = struct.unpack_from("<H", blob, a - BASE)[0]
                if ((h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
                        and (h2 & 7) == rd and ((h2 >> 7) & 1) == 0):
                    if (word + ((a + 4) & ~1)) & 0xFFFFFFFF == table:
                        sites.append(f"0x{BASE + off:08x}")
                    break
        check(len(sites) == 2, f"{k}: nº de bases PIC = {len(sites)}")
        check(sorted(sites) == sorted(DATA["negatives"]["pic_bases_to_table"][k]),
              f"{k}: direcciones de las bases PIC {sites}")
        for psite in sites:
            ldr = int(psite, 16)
            bases = set()
            for delta in (2, 4):
                try:
                    bases.add(pic_base(blob, ldr, ldr + delta))
                except SystemExit:
                    pass
            check(table in bases,
                  f"{k}: la base PIC del sitio {psite} no apunta a la tabla")
        lits = sum(1 for i in range(0, len(blob) - 3, 2)
                   if struct.unpack_from("<I", blob, i)[0] == table)
        check(lits == 0, f"{k}: literales absolutos a la tabla = {lits}")

    # 4. bucles de los dos consumidores (bytes exactos)
    EXPECT_LOOP = {
        "a7s_fw320": ("452f", "b5f58a7f"),
        "a6000_fw321": ("2f2f", "bc2d"),
        "a6300_fw201": ("452f", "b5f58a7f"),
    }
    for k, m in models.items():
        blob = blobs[k]
        a = m["consumers"]["A"]["closed_loop"]["insn"]["address"]
        b = m["consumers"]["B"]["closed_loop"]["insn"]["address"]
        la, lb = EXPECT_LOOP[k]
        check(read(int(a, 16), len(la) // 2, blob).hex() == la, f"{k}: cmp del bucle A")
        check(read(int(b, 16), len(lb) // 2, blob).hex() == lb, f"{k}: cmp del bucle B")
        n = m["table"]["entries"]
        check(m["consumers"]["A"]["closed_loop"]["iterations"] == n, f"{k}: iteraciones A")
        check(m["consumers"]["B"]["closed_loop"]["iterations"] == n, f"{k}: iteraciones B")
        # el contador del bucle B avanza de 4 en 4 (`adds r5,#4` seis bytes antes)
        check(read(int(b, 16) - 6, 2, blob).hex() == "0435",
              f"{k}: paso del bucle B")

    # 5. camino de carga: 0221 0d22 unico por modelo, cabecera 0x18, id en +0x12
    for k, m in models.items():
        blob = blobs[k]
        hits = find_all(blob, bytes.fromhex("02210d22"))
        check(len(hits) == 1, f"{k}: sitios de `movs r1,#2`+`movs r2,#0xd` = {len(hits)}")
        site = hits[0]
        check(m["load_path"]["init"]["size"] == 0x0D, f"{k}: tamano en el camino de carga")
        init_addr = int(m["load_path"]["init"]["size_insn"]["address"], 16)
        check(init_addr == site + 2, f"{k}: direccion del `movs r2,#0xd`")
        call = int(m["load_path"]["init"]["call_insn"]["address"], 16)
        check((u16(call, blob) & 0xF800) == 0xF000, f"{k}: el init se invoca con bl")
        # capacidad de la cabecera = 0x18 justo despues
        head = int(m["load_path"]["header_capacity"]["insn"]["address"], 16)
        check(read(head, 2, blob).hex() == "1823", f"{k}: cabecera 0x18")
        check(m["load_path"]["header_capacity"]["value"] == 0x18, f"{k}: valor cabecera")
        # prologo del constructor de mensaje: 20 B
        builder = int(m["load_path"]["builder"]["address"], 16)
        pro = read(builder, 20, blob).hex()
        check(pro.startswith("0123038043800371"), f"{k}: prologo del constructor")
        check(pro[24:28] == "4482", f"{k}: `strh r4,[r0,#0x12]` en el prologo")
        check(pro == DATA["models"][k]["load_path"]["message_prologue_20b"],
              f"{k}: prologo registrado")
        # offset = 0 en +0x14
        off_addr = int(m["load_path"]["offset_store"]["address"], 16)
        check(read(off_addr, 2, blob).hex() == "4361", f"{k}: offset 0 en +0x14")

    # 6. el mismo 13 en el allocador de la tabla completa
    for k, m in models.items():
        blob = blobs[k]
        addr = int(m["consumers"]["B"]["alloc_first_arg"]["address"], 16)
        check(read(addr, 2, blob).hex() == "0d20", f"{k}: `movs r0,#0xd` del alloc")
        check(m["consumers"]["B"]["alloc_value"] == 0x0D, f"{k}: valor del alloc")
        # el 13 es independiente del nº de entradas
        check(m["consumers"]["B"]["alloc_value"] != m["table"]["entries"],
              f"{k}: 13 no es el nº de entradas")

    # 7. sitio con longitud de runtime en el mismo inicializador (A7S)
    blob7 = blobs["a7s_fw320"]
    check(read(0x438F7FDC, 4, blob7).hex() == "bdf84c20",
          "ldrh.w r2,[sp,#0x4c] en 0x438f7fdc")
    check((u16(0x438F7FE2, blob7) & 0xF800) == 0xF000,
          "bl al inicializador en 0x438f7fe2")

    # 8. relacion entre modelos
    ids7 = models["a7s_fw320"]["table"]["ids"]
    ids6 = models["a6000_fw321"]["table"]["ids"]
    ids63 = models["a6300_fw201"]["table"]["ids"]
    check(ids6 == [x for x in ids7 if x <= 0x4E], "A6000 != A7S filtrada por <=0x4e")
    check(ids63 == ids7, "A6300 != A7S")
    check(sorted(set(ids7) - set(ids6)) == list(range(0x4F, 0x65)),
          "faltantes de A6000 != 0x4f..0x64")
    check(DATA["cross_model"]["a6000_missing"] == list(range(79, 101)),
          "lista de faltantes registrada")
    check(len(ids6) == 47 and len(ids7) == 69 and len(ids63) == 69, "tamanos 47/69/69")
    shared = 0
    while shared < len(ids6) and ids6[shared] == ids7[shared]:
        shared += 1
    check(shared == 41 and DATA["cross_model"]["shared_prefix_entries"] == 41,
          "prefijo comun != 41")

    # 9. config 0x402/+0x680 (persistencia del "aberration data info")
    CFG = {
        "a7s_fw320": ("a3f88046", "b3f88056"),
        "a6000_fw321": ("a3f88066", "b3f88066"),
        "a6300_fw201": ("a3f88046", "b3f88056"),
    }
    for k, m in models.items():
        blob = blobs[k]
        w = int(m["config_persistence"]["write"]["address"], 16)
        r = int(m["config_persistence"]["read"]["address"], 16)
        cw = int(m["config_persistence"]["config_id_write"]["address"], 16)
        cr = int(m["config_persistence"]["config_id_read"]["address"], 16)
        check(read(w, 4, blob).hex() == CFG[k][0], f"{k}: store en +0x680")
        check(read(r, 4, blob).hex() == CFG[k][1], f"{k}: load de +0x680")
        check(read(cw, 4, blob).hex() == "40f20240", f"{k}: config write 0x402")
        check(read(cr, 4, blob).hex() == "40f20240", f"{k}: config read 0x402")

    # 10. LensAberrationData.bin: identico, sin tabla {id,13}, sin la lista de ids
    hashes = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in LENSBIN.items()}
    check(len(set(hashes.values())) == 1, "LensAberrationData.bin difiere entre modelos")
    check(hashes == DATA["lens_aberration_file"]["sha256"], "hash registrado del lensbin")
    lens = LENSBIN["a7s_fw320"].read_bytes()
    check(len(lens) == 161766, "tamano del lensbin")
    max_pairs = 0
    for off in range(0, len(lens) - 4, 2):
        if struct.unpack_from("<H", lens, off + 2)[0] == 0x000D:
            n = 1
            while (off + 4 * n + 4 <= len(lens)
                   and struct.unpack_from("<H", lens, off + 4 * n + 2)[0] == 0x000D):
                n += 1
            max_pairs = max(max_pairs, n)
    check(max_pairs == DATA["lens_aberration_file"]["max_consecutive_pairs_with_second_0x000d"],
          "pares {x,0x000d} en el lensbin")
    check(max_pairs < 2, f"el lensbin contiene pares {{id,13}}: {max_pairs}")
    id_list = b"".join(struct.pack("<H", x) for x in ids7)
    check(id_list not in lens, "el lensbin contiene la lista de ids A7S")
    check(lens[:8].hex() == "4949000120008000", "cabecera del lensbin")

    # 11. coherencia de veredictos del JSON
    v = DATA["verdicts"]
    check(v["second_field_is_constant_13"] is True, "veredicto: 13 constante")
    check(v["second_field_is_per_id_data"] is False, "veredicto: no es dato por id")
    check(v["same_13_in_load_path_all_models"] is True, "veredicto: 13 en carga")
    check(v["same_13_in_group_alloc_all_models"] is True, "veredicto: 13 en alloc")
    check(v["13_equals_message_header_size"] is False, "veredicto: 13 != cabecera")
    check(v["ids_index_the_lensbin_file"] is False, "veredicto: ids no indexan el fichero")
    check(v["semantic_of_13"].startswith("INFERENCIA"), "veredicto: 13 es inferencia")

    print(f"{CHECKS} comprobaciones OK")


if __name__ == "__main__":
    main()
