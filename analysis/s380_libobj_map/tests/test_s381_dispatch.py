#!/usr/bin/env python3
"""Test S381: verifica entradas .plt de mensajería y ausencia de xrefs a RecordStill::Execute."""
import struct
from pathlib import Path

PATH = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
            "firmware/extracted/fw321/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
data = PATH.read_bytes()

def test_plt_key_entries():
    """Verifica que las entradas .plt clave de mensajería existen."""
    # .plt base 0x000db3c4, cada entrada 16 B
    # No podemos verificar cada entrada sin el mapeo .rel.plt, pero verificamos
    # que los símbolos estén en .dynstr
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
    """No hay literal 0x0090b248 en secciones de datos (llamada indirecta)."""
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
    """No hay movw #0x3500 (Thumb-2) en libObj.so."""
    pat = bytes([0x14, 0xF3, 0x00, 0xF9])  # movw Rd, #0x3500
    assert data.find(pat) == -1

def test_no_movw_3002():
    """No hay movw #0x3002 (Thumb-2) en libObj.so."""
    pat = bytes([0xC0, 0xF2, 0x02, 0xF8])  # movw Rd, #0x3002
    assert data.find(pat) == -1

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
