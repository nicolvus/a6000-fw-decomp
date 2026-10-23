"""S382: llamadas a 0x90b248 (RecordImage; antigua etiqueta RecordStill::Execute)."""
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

PATH = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
            "firmware/extracted/fw321/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
data = PATH.read_bytes()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True
text_va = 0x0e2b70
text_end = text_va + 0xae6a1c

def test_recordimage_prologue():
    """0x90b248 empieza con push.w Thumb-2; no prueba un nombre C++."""
    ins = next(md.disasm(data[0x90b248:0x90b248+4], 0x90b248))
    assert ins.mnemonic == 'push.w'
    assert 'r4' in ins.op_str and 'r5' in ins.op_str

def test_recordimage_movw_100f():
    """movw r1, #0x100f en 0x90b2a4 (content-info)."""
    ins = next(md.disasm(data[0x90b2a4:0x90b2a8], 0x90b2a4))
    assert ins.mnemonic == 'movw'
    assert '0x100f' in ins.op_str

def test_candidate_90de2e_calls_recordstill():
    """0x90de2e contiene bl #0x90b248."""
    ins = next(md.disasm(data[0x90de2e:0x90de32], 0x90de2e))
    assert ins.mnemonic == 'bl'
    # Verificar target (capstone da target absoluto en imm para BL Thumb-2)
    assert ins.operands[0].type == 2
    assert ins.operands[0].imm == 0x90b248

def test_candidate_91634e_calls_recordstill():
    """0x91634e contiene bl #0x90b248."""
    ins = next(md.disasm(data[0x91634e:0x916352], 0x91634e))
    assert ins.mnemonic == 'bl'
    assert ins.operands[0].type == 2
    assert ins.operands[0].imm == 0x90b248

def test_block_90de2c():
    """Bloque de argumentos; no atribuye una entrada de función a 0x90de2c."""
    ins1 = next(md.disasm(data[0x90de2c:0x90de2e], 0x90de2c))
    assert ins1.mnemonic == 'mov'
    assert 'r1, r6' in ins1.op_str

def test_block_91634a():
    """Argumentos del BL; 0x91631e pertenece a los datos del TBB."""
    ins1 = next(md.disasm(data[0x91634a:0x91634c], 0x91634a))
    ins2 = next(md.disasm(data[0x91634c:0x91634e], 0x91634c))
    assert ins1.mnemonic == 'mov' and 'r0, r4' in ins1.op_str
    assert ins2.mnemonic == 'mov' and 'r1, r6' in ins2.op_str

def test_bl_targets_7484dc():
    """Regresión: Capstone entrega el destino absoluto, sin sumar PC ni escalar."""
    ins = next(md.disasm(data[0x7484dc:0x7484e0], 0x7484dc))
    assert ins.bytes == bytes.fromhex("99 f5 ea e0")
    assert ins.mnemonic == 'blx'
    assert ins.operands[0].imm == 0xe16b4
    assert ins.operands[0].imm != 0x90b248


def test_755af8_is_not_a_call_to_90de2c():
    """El mismo cálculo incorrecto produjo un segundo llamador falso."""
    ins = next(md.disasm(data[0x755af8:0x755afc], 0x755af8))
    assert ins.bytes == bytes.fromhex("86 f5 4e e3")
    assert ins.mnemonic == 'blx'
    assert ins.operands[0].imm == 0xdc198
    assert ins.operands[0].imm != 0x90de2c

if __name__ == "__main__":
    test_recordimage_prologue(); print("PASS test_recordimage_prologue")
    test_recordimage_movw_100f(); print("PASS test_recordimage_movw_100f")
    test_candidate_90de2e_calls_recordstill(); print("PASS test_candidate_90de2e_calls_recordstill")
    test_candidate_91634e_calls_recordstill(); print("PASS test_candidate_91634e_calls_recordstill")
    test_block_90de2c(); print("PASS test_block_90de2c")
    test_block_91634a(); print("PASS test_block_91634a")
    test_bl_targets_7484dc(); print("PASS test_bl_targets_7484dc")
    test_755af8_is_not_a_call_to_90de2c(); print("PASS test_755af8_is_not_a_call_to_90de2c")
    print("\nTodos los tests S382 PASS")
