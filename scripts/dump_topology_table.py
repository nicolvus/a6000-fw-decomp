"""Vuelca la tabla de topologías de libObj.so (TopologyManager) y m_pinTbl/m_objTbl de libSysDef.so.
Uso: python3 -I scripts/dump_topology_table.py [salida.json]
Direcciones ELF (Ghidra = ELF + 0x10000). Tabla: .rodata 0xcc4210, 211 filas de 0x20 B (sesión 14).
"""
import json
import struct
import sys
from pathlib import Path

LIBDIR = Path("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib")
TOPO_BASE, TOPO_ROWS = 0xCC4210, 211  # filas: 8 u32 (ver COLS)
COLS = ("pin_type", "sts_id", "src_obj", "src_dir", "src_no", "dst_obj", "dst_dir", "dst_no")
SYSDEF_PIN_TBL, SYSDEF_PIN_N = 0x1B948, 12  # .data.rel.ro: 4 u32 por fila (file off = vaddr - 0x8000)
SYSDEF_OBJ_TBL, SYSDEF_OBJ_N = 0x1B78C, 37  # 3 u32 (cateId, "CATEID_x", "ObjX")


def cstr(d: bytes, p: int) -> str:
    return d[p:d.index(b"\0", p)].decode()


def main(out: str) -> None:
    obj = (LIBDIR / "libObj.so").read_bytes()
    sd = (LIBDIR / "libSysDef.so").read_bytes()
    rows = [dict(zip(COLS, struct.unpack_from("<8I", obj, TOPO_BASE + i * 0x20))) | {"id": i} for i in range(TOPO_ROWS)]
    pins = []
    for i in range(SYSDEF_PIN_N):
        cate, typ, n1, n2 = struct.unpack_from("<4I", sd, SYSDEF_PIN_TBL - 0x8000 + 16 * i)
        pins.append({"msg_category": hex(cate), "type": typ, "name": cstr(sd, n1)})
    objs = []
    for i in range(SYSDEF_OBJ_N):
        cate, n1, n2 = struct.unpack_from("<3I", sd, SYSDEF_OBJ_TBL - 0x8000 + 12 * i)
        objs.append({"index": i, "cate": hex(cate), "cate_name": cstr(sd, n1), "obj_name": cstr(sd, n2)})
    Path(out).write_text(json.dumps({"topology_rows": rows, "pin_tbl": pins, "obj_tbl_libsysdef": objs}, indent=1))
    assert rows[0x2A]["src_obj"] == 9 and rows[0x2A]["dst_obj"] == 11 and rows[0x2A]["pin_type"] == 0  # self-check
    print(f"{len(rows)} topologías -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "analysis/topology-table-libobj.json")
