#!/usr/bin/env python3
"""Test S380: verifica mapa de secciones y símbolos clave de libObj.so A6000."""
import struct, json
from pathlib import Path

PATH = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
            "firmware/extracted/fw321/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
data = PATH.read_bytes()

def test_elf_header():
    assert data[:4] == b"\x7fELF"
    e_type = struct.unpack_from("<H", data, 0x10)[0]
    assert e_type == 3, f"ET_DYN esperado (3), got {e_type}"  # PIE
    e_machine = struct.unpack_from("<H", data, 0x12)[0]
    assert e_machine == 0x28  # ARM

def test_section_count():
    e_shoff = struct.unpack_from("<I", data, 0x20)[0]
    e_shnum = struct.unpack_from("<H", data, 0x30)[0]
    assert e_shnum == 26

def test_text_section():
    e_shoff = struct.unpack_from("<I", data, 0x20)[0]
    e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
    e_shnum = struct.unpack_from("<H", data, 0x30)[0]
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        st_name, stype, flags, addr, offset, size = struct.unpack_from("<IIIIII", data, off)
        # .text está en index 10 según el listado de secciones
        if i == 10:
            assert addr == 0x000e2b70
            assert size == 0xae6a1c
            return
    raise AssertionError(".text no encontrado en índice esperado")

def test_plt_section():
    e_shoff = struct.unpack_from("<I", data, 0x20)[0]
    e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
    e_shnum = struct.unpack_from("<H", data, 0x30)[0]
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        st_name, stype, flags, addr, offset, size = struct.unpack_from("<IIIIII", data, off)
        if i == 9:  # .plt
            assert addr == 0x000db3c4
            assert size == 0x0077a0
            # Cabecera de 20 B y veneer Thumb del primer cuerpo ARM.
            assert data[offset + 20:offset + 24] == bytes.fromhex('78 47 c0 46')
            return
    raise AssertionError(".plt no encontrado")

def test_relplt_entries():
    e_shoff = struct.unpack_from("<I", data, 0x20)[0]
    e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
    e_shnum = struct.unpack_from("<H", data, 0x30)[0]
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        st_name, stype, flags, addr, offset, size = struct.unpack_from("<IIIIII", data, off)
        if i == 7:  # .rel.plt
            nrel = size // 8
            assert nrel == 2420
            return
    raise AssertionError(".rel.plt no encontrado")

def test_key_symbols_present():
    key = ["_ZN3MWF11ObjMsgQueue7EnqueueEPKNS_6ObjMsgE",
           "_ZN3UFW11MsgReceiver6RcvMsgEPjPPN3MWF6ObjMsgE",
           "_ZN3MWF12EventWrapper11SendAndRecvEPviS1_i",
           "osal_reg_msg_queue_cb",
           "osal_reg_sync_msg_queue_cb",
           "osal_snd_msg",
           "ObjStillRecorder_Init"]
    dynstr_off = 0x011768
    dynstr = data[dynstr_off:dynstr_off + 0x0231e5]
    found = 0
    for name in key:
        if name.encode() in dynstr:
            found += 1
    assert found == len(key), f"símbolos clave faltantes: {found}/{len(key)}"

def test_recordstill_execute_thumb2():
    # 0x90b248: push.w {r4,r5,r6,r7,r8,sb,sl,fp,lr} = Thumb-2 (bytes LE: 2d e9 f0 4f)
    data_at = data[0x90b248:0x90b248+4]
    assert data_at == b"\x2d\xe9\xf0\x4f", f"prólogo inesperado: {data_at.hex()}"

if __name__ == "__main__":
    test_elf_header(); print("PASS test_elf_header")
    test_section_count(); print("PASS test_section_count")
    test_text_section(); print("PASS test_text_section")
    test_plt_section(); print("PASS test_plt_section")
    test_relplt_entries(); print("PASS test_relplt_entries")
    test_key_symbols_present(); print("PASS test_key_symbols_present")
    test_recordstill_execute_thumb2(); print("PASS test_recordstill_execute_thumb2")
    print("\nTodos los tests S380 PASS")
