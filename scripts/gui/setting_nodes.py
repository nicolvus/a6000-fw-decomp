#!/usr/bin/env python3
"""Vuelca las listas de propiedades de nodos de ajuste (`cmnViewSettingPropertyList*`) de CautionConfig.so (solo lectura).

Formato (VERIFICADO en A6000 fw3.21 y A6300 fw2.01): array de tripletas u32 {id_propiedad, 0|1, valor}:
  0 = texto de etiqueta (0x0204xxxx; &0xffff = id en string_*.uxc) · 6 = texto de ayuda/valor · 0xe = ProcessId (solo en la raíz)
  0xf / 0x10 = valor interno de la opción · 0xb, 0xc, 0x11, 0x14 = indicadores/avisos (sin descifrar)
Uso: setting_nodes.py CautionConfig.so STRING_UXC REGEX   (REGEX sobre el nombre sin el prefijo)
"""
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import uxc_strings

PREFIX = "cmnViewSettingPropertyList"


def property_lists(lib: Path, pattern: str):
    """Rinde (nombre, [(id, flag, valor), ...]) para las listas cuyo nombre casa con `pattern`."""
    data = lib.read_bytes()
    for line in subprocess.run(["nm", "-D", "-S", str(lib)], capture_output=True, text=True, check=True).stdout.splitlines():
        f = line.split()
        if len(f) == 4 and f[2] == "R" and f[3].startswith(PREFIX) and re.search(pattern, f[3][len(PREFIX):]):
            addr, size = int(f[0], 16), int(f[1], 16)
            words = struct.unpack_from(f"<{size // 4}I", data, addr)
            yield f[3][len(PREFIX):], [tuple(words[i:i + 3]) for i in range(0, len(words), 3)]


if __name__ == "__main__":
    lib, strings, pattern = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    _, _, texts = uxc_strings.parse(strings.read_bytes())
    for name, props in property_lists(lib, pattern):
        print(name)
        for pid, flag, val in props:
            note = f"  «{texts[val & 0xFFFF][:50]}»" if pid in (0, 6) and val >> 16 == 0x204 and (val & 0xFFFF) in texts else ""
            print(f"  prop {pid:#04x} flag {flag} valor {val:#x}{note}")
