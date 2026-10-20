"""Entradas estáticas de ImagerDrvParam_IMX210E por modo (A6000 fw 3.21, av-cam.bin).

El constructor C_Imager (0x436d72e8) pasa a ImagerDrvParam_IMX210E (0x436d8774) punteros a tablas de solo lectura; los arrays de
salida (CS/Camcore/EC/LC) están a cero en la imagen y los calcula 0x436d9d00 al arrancar. Aquí se vuelcan las ENTRADAS.
Uso: python3 -I scripts/imx210_param_tables.py > analysis/imx210-drvparam-inputs.json"""
import json
import re
import struct
import subprocess

ELF = "analysis/av-cam-analysis-view.elf"
BASE, OFF = 0x43541000, 0x1F0
CTOR_ARGS = (0x436D7318, 0x436D7378)  # tramo del ctor donde se arman los 15 argumentos
GOT_LIT, GOT_PC = 0x436D7470, 0x436D72F8  # r5 = GOT del módulo (0x4401eee4)
MODE_LIST, N = 0x43FEA070, 13
# offset en la tabla de punteros -> (nombre, dirección, bytes por fila); direcciones obtenidas de CTOR_ARGS
INPUTS = {
    "row72_camcore": (0x43BC16DC, 72),
    "row24_cs": (0x43BC1C20, 24),
    "row36_ec": (0x43BC1D58, 36),
    "ab12_variant0": (0x43BC1AE8, 12),
    "ab12_variant1": (0x43BC1B84, 12),
}


def _read(path: str = ELF) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _u32(d: bytes, a: int) -> int:
    return struct.unpack_from("<I", d, a - BASE + OFF)[0]


def ctor_stack_args(d: bytes) -> dict[int, int]:
    """Intérprete mínimo (ldr literal, add pc, ldr [GOT], adds, str [sp]) del tramo de armado de argumentos."""
    out = subprocess.run(["llvm-objdump", "-d", "--triple=thumbv7", f"--start-address={CTOR_ARGS[0]:#x}",
                          f"--stop-address={CTOR_ARGS[1]:#x}", ELF], capture_output=True, text=True, check=True).stdout
    r: dict[str, int] = {"r5": (_u32(d, GOT_LIT) + GOT_PC + 4) & 0xFFFFFFFF}
    st: dict[int, int] = {}
    for line in out.splitlines():
        m = re.match(r"\s*([0-9a-f]+):\s+(?:[0-9a-f]{4} ){1,2}\s*(\w+(?:\.w)?)\s*(.*?)(?:\s+@.*)?$", line)
        if not m:
            continue
        a, op, args = int(m[1], 16), m[2], m[3]
        p = [x.strip() for x in re.split(r",\s*(?![^\[]*\])", args)]
        if op.startswith("ldr") and p[1].startswith("[pc"):
            r[p[0]] = _u32(d, (a + 4) // 4 * 4 + int(re.search(r"#(0x[0-9a-f]+)", p[1])[1], 16))  # type: ignore[index]
        elif op == "add" and p[1] == "pc":
            r[p[0]] = (r[p[0]] + a + 4) & 0xFFFFFFFF
        elif op.startswith("ldr") and (g := re.match(r"\[(r\d+), (r\d+)\]", p[1])):
            r[p[0]] = _u32(d, r[g[1]] + r[g[2]])
        elif op == "adds" and p[1].startswith("#"):
            r[p[0]] = r[p[0]] + int(p[1][1:], 0)
        elif op == "str" and p[1].startswith("[sp"):
            k = re.search(r"#(0x[0-9a-f]+)", p[1])
            st[int(k[1], 16) if k else 0] = r[p[0]]
    return st


def modes(d: bytes) -> list[int]:
    return list(struct.unpack_from(f"<{N}I", d, MODE_LIST - BASE + OFF))


def per_mode(d: bytes) -> list[dict]:
    ids = modes(d)
    rows = []
    for i, mode in enumerate(ids):
        row: dict = {"mode": mode}
        for name, (addr, size) in INPUTS.items():
            fmt = "<%dI" % (size // 4)
            row[name] = list(struct.unpack_from(fmt, d, addr + i * size - BASE + OFF))
        # CS: bytes y floats según 0x43ad975e (float en +0x14); se conserva también el vuelco crudo
        row["cs_clock_float"] = struct.unpack("<f", struct.pack("<I", row["row24_cs"][5]))[0]
        rows.append(row)
    return rows


if __name__ == "__main__":
    data = _read()
    print(json.dumps({"elf": ELF, "ctor_stack_args": {hex(k): hex(v) for k, v in sorted(ctor_stack_args(data).items())},
                      "modes": per_mode(data)}, indent=1))
