"""Matriz de registros por modo del IMX210 (A6000 3.21, av-cam base lógica 0x43541000).
Tabla de modos lógicos: 0x43fea070 (13 palabras). Tabla de registros: puntero GOT 0x44022f8c -> 0x43fe9b74,
filas de 20 bytes = {u32 ptr al campo valor (ptr-2 = u16 dirección), 13 bytes valor por modo, 3 relleno}.
Uso: python3 -I scripts/imx210_modes.py [elf] > analysis/imx210-setmode-register-matrix.json"""
import json, struct, sys

BASE, OFF = 0x43541000, 0x1f0
MODE_TABLE, REG_TABLE, N_MODES = 0x43fea070, 0x43fe9b74, 13

class Img:
    def __init__(self, path): self.d = open(path, "rb").read()
    def b(self, a, n): return self.d[a - BASE + OFF: a - BASE + OFF + n]
    def u32(self, a): return struct.unpack("<I", self.b(a, 4))[0]
    def u16(self, a): return struct.unpack("<H", self.b(a, 2))[0]

def matrix(im):
    modes = [im.u32(MODE_TABLE + 4 * i) for i in range(N_MODES)]
    rows = []
    while (ptr := im.u32(REG_TABLE + 20 * len(rows))) != 0:
        r = REG_TABLE + 20 * len(rows)
        rows.append({"reg": im.u16(ptr - 2), "shadow_ptr": ptr, "init": im.b(ptr, 1)[0], "values": list(im.b(r + 4, N_MODES))})
    return {"modes": modes, "rows": rows}

if __name__ == "__main__":
    json.dump(matrix(Img(sys.argv[1] if len(sys.argv) > 1 else "analysis/av-cam-analysis-view.elf")), sys.stdout, indent=1)
