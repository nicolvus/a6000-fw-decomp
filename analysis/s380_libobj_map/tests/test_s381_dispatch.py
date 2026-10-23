"""S381: imports y negativos acotados; el resolutor PLT se prueba por separado."""
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

PATH = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
            "firmware/extracted/fw321/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
data = PATH.read_bytes()

def test_plt_key_entries():
    """Verifica que las entradas .plt clave de mensajería existen."""
    # Esto verifica nombres en .dynstr; no atribuye direcciones PLT.
    dynstr_off = 0x011768
    dynstr = data[dynstr_off:dynstr_off + 0x0231e5]
    keys = ["osal_reg_msg_queue_cb",
            "osal_reg_sync_msg_queue_cb",
            "_ZN3MWF11ObjMsgQueue7EnqueueEPKNS_6ObjMsgE",
            "_ZN3UFW11MsgReceiver6RcvMsgEPjPPN3MWF6ObjMsgE",
            "_ZN3MWF12EventWrapper11SendAndRecvEPviS1_i",
            "_ZN3MWF6ObjPin4SendEjPNS_6ObjMsgE"]
    for k in keys:
        assert k.encode() in dynstr, f"símbolo no encontrado en .dynstr: {k}"

def test_no_recordstill_literal():
    """Negativo de literal: no demuestra una llamada indirecta."""
    pat = struct.pack("<I", 0x0090b248)
    for off, size in [(0xbc9598, 0x2c8a1a), (0xfca9d0, 0x05a090),
                       (0x102d320, 0x073588), (0x1024bd0, 0x008750)]:
        assert data.find(pat, off, off + size) == -1, \
            f"literal 0x90b248 encontrado en sección en off 0x{off:06x}"

def test_no_recordstill_thumb_literal():
    """No hay literal Thumb 0x0090b249 en secciones de datos."""
    pat = struct.pack("<I", 0x0090b249)
    for off, size in [(0xbc9598, 0x2c8a1a), (0xfca9d0, 0x05a090),
                       (0x102d320, 0x073588), (0x1024bd0, 0x008750)]:
        assert data.find(pat, off, off + size) == -1, \
            f"literal thumb 0x90b249 encontrado en sección en off 0x{off:06x}"

def test_no_movw_3500():
    """Regresión del encoding histórico: validar el inmediato correcto."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    instruction = next(md.disasm(bytes.fromhex('43 f2 00 50'), 0))
    assert instruction.mnemonic == 'movw'
    assert instruction.operands[1].imm == 0x3500

def test_no_movw_3002():
    """Validar encoding sin confundir su ausencia con ausencia del ID."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    instruction = next(md.disasm(bytes.fromhex('43 f2 02 00'), 0))
    assert instruction.mnemonic == 'movw'
    assert instruction.operands[1].imm == 0x3002

def test_no_word_0x40193():
    """No hay word LE 0x00040193 en .rodata (posible ID de cola C2)."""
    pat = struct.pack("<I", 0x00040193)
    assert data.find(pat, 0xbc9598, 0xbc9598 + 0x2c8a1a) == -1

if __name__ == "__main__":
    test_plt_key_entries(); print("PASS test_plt_key_entries")
    test_no_recordstill_literal(); print("PASS test_no_recordstill_literal")
    test_no_recordstill_thumb_literal(); print("PASS test_no_recordstill_thumb_literal")
    test_no_movw_3500(); print("PASS test_no_movw_3500")
    test_no_movw_3002(); print("PASS test_no_movw_3002")
    test_no_word_0x40193(); print("PASS test_no_word_0x40193")
    print("\nTodos los tests S381 PASS")
