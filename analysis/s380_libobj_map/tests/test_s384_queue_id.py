"""S384: negativos de datos acotados y regresiones de los encodings publicados."""
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

from scripts.elf_string_xrefs import sections

A6000 = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
             "firmware/extracted/fw321/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
A7S = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
           "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
           "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")

def test_no_word_40193_in_rodata_data():
    """No hay word LE 0x00040193 en .rodata ni .data (solo falsos positivos en .text)."""
    pat = struct.pack('<I', 0x00040193)
    for path in [A6000, A7S]:
        data = path.read_bytes()
        for name in ('.rodata', '.data'):
            off, size = sections(data)[name][4:6]
            assert off + size <= len(data)
            assert data.find(pat, off, off + size) == -1, \
                f"word 0x40193 en datos de {path}"

def test_no_movw_movt_40193():
    """Regresión: el encoding correcto de movw r3,#0x193 sí está presente."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    encoding = bytes.fromhex('40 f2 93 13')
    ins = next(md.disasm(encoding, 0))
    assert ins.mnemonic == 'movw'
    assert ins.operands[1].imm == 0x193
    for path in [A6000, A7S]:
        assert encoding in path.read_bytes()


def test_correct_upper_half_is_4():
    """0x40193 requiere movt #4; #0x40 produciría 0x400193."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    ins = next(md.disasm(bytes.fromhex('c0 f2 04 00'), 0))
    assert ins.mnemonic == 'movt'
    assert ins.operands[1].imm == 0x40193 >> 16

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
        elif any(s[4] <= pos < s[4] + s[5] for name, s in sections(data).items()
                 if name in ('.rodata', '.data')):
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
