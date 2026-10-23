#!/usr/bin/env python3
"""Test S384: verifica que 0x40193 no aparece como dato inmediato en libObj.so."""
import struct
from pathlib import Path

A6000 = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
             "firmware/extracted/fw321/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
A7S = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
           "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
           "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")

def test_no_word_40193_in_rodata_data():
    """No hay word LE 0x00040193 en .rodata ni .data (solo falsos positivos en .text)."""
    pat = struct.pack('<I', 0x00040193)
    for path, ranges in [(A6000, [(0xbc9598, 0x2c8a1a), (0x102d320, 0x073588)]),
                          (A7S, [(0xad4c48, 0x28cf6e), (0x102d320, 0x073588)])]:
        data = path.read_bytes()
        for off, size in ranges:
            assert data.find(pat, off, off + size) == -1, \
                f"word 0x40193 en datos de {path}"

def test_no_movw_movt_40193():
    """No hay Thumb movw #0x0193 ni movt #0x0040 en ningún binario."""
    # Thumb movw #0x0193 (Rd=r0): 40 F2 93 F9
    # Thumb movt #0x0040 (Rd=r0): 41 C2 40 F8
    for path in [A6000, A7S]:
        data = path.read_bytes()
        assert data.find(bytes([0x40, 0xF2, 0x93, 0xF9])) == -1, f"movw #0x0193 en {path}"
        assert data.find(bytes([0x41, 0xC2, 0x40, 0xF8])) == -1, f"movt #0x0040 en {path}"

def test_no_string_40193():
    """No hay string ASCII '40193'."""
    for path in [A6000, A7S]:
        data = path.read_bytes()
        assert data.find(b'40193') == -1, f"string '40193' en {path}"

def test_word40193_only_in_text():
    """Los word LE 0x40193 que aparecen están solo en .text (falsos positivos de instrucción)."""
    data = A6000.read_bytes()
    pat = struct.pack('<I', 0x00040193)
    pos = 0
    found_in_text = 0
    found_in_data = 0
    while True:
        pos = data.find(pat, pos)
        if pos < 0:
            break
        if 0x0e2b70 <= pos < 0x0e2b70 + 0xae6a1c:
            found_in_text += 1
        elif 0xbc9598 <= pos < 0xbc9598 + 0x2c8a1a or 0x102d320 <= pos < 0x102d320 + 0x073588:
            found_in_data += 1
        pos += 1
    assert found_in_data == 0, f"word 0x40193 en secciones de datos: {found_in_data}"
    assert found_in_text > 0, "esperábamos falsos positivos en .text"

if __name__ == "__main__":
    test_no_word_40193_in_rodata_data(); print("PASS test_no_word_40193_in_rodata_data")
    test_no_movw_movt_40193(); print("PASS test_no_movw_movt_40193")
    test_no_string_40193(); print("PASS test_no_string_40193")
    test_word40193_only_in_text(); print("PASS test_word40193_only_in_text")
    print("\nTodos los tests S384 PASS")
