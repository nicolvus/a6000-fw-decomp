"""S21 (Claude): comprobación estática reproducible del tramo pulsación -> orden de cortina.

Uso (desde la raíz del proyecto): python3 -I analysis/session21/evidence/claude-button-to-shutter.py
Lee solo los binarios originales (no los modifica) y escribe claude-button-to-shutter.json
junto a este script. Cada hecho es un assert: si el binario no coincide, el script falla.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

FW = Path("firmware/extracted/fw321/firmware.tar_unpacked")
AVCAM = FW / "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
NF15 = FW / "0700_part_image/dev/nflasha15_unpacked_unpacked"
LIBOBJ = NF15 / "lib/libObj.so"
INPUT_KO = NF15 / "kmod/input.ko"
DARWIN = FW / "0640_darwin/darwin_core.bin"
SHA = {
    AVCAM: "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9",
    LIBOBJ: "8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a",
    INPUT_KO: "060adbd628ba28d0fd3007f92d2002a43218b6794c59ff5f12e70b61a6f58738",
    DARWIN: "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4",
}
LIRO = 0x43541000  # VA base de av-cam.bin (offset de archivo = VA - base)
DARWIN_ROM = 0x4200


class Image:
    def __init__(self, path: Path, base: int) -> None:
        self.data = path.read_bytes()
        assert hashlib.sha256(self.data).hexdigest() == SHA[path], path
        self.base = base

    def u16(self, va: int) -> int:
        return int(struct.unpack_from("<H", self.data, va - self.base)[0])

    def u32(self, va: int) -> int:
        return int(struct.unpack_from("<I", self.data, va - self.base)[0])

    def bl(self, va: int) -> int:
        """Destino de BL/BLX o B.W (T4, salto de cola) Thumb-2 en va."""
        h1, h2 = self.u16(va), self.u16(va + 2)
        assert h1 >> 11 == 0b11110 and (h2 >> 14 == 0b11 or h2 >> 12 & 0b1101 == 0b1001), hex(va)
        s = (h1 >> 10) & 1
        i1 = 1 - (((h2 >> 13) & 1) ^ s)
        i2 = 1 - (((h2 >> 11) & 1) ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        target = va + 4 + imm
        return target if h2 & 0x1000 else target & ~3

    def lit(self, ldr_va: int) -> int:
        """Valor cargado por 'ldr rX,[pc,#imm8*4]' (Thumb-1) en ldr_va."""
        h = self.u16(ldr_va)
        assert h >> 11 == 0b01001, hex(ldr_va)
        return self.u32(((ldr_va + 4) & ~3) + (h & 0xFF) * 4)

    def pic(self, ldr_va: int, add_va: int) -> int:
        """Dirección absoluta de un par 'ldr rX,[pc]' + 'add rX,pc'."""
        return (self.lit(ldr_va) + add_va + 4) & 0xFFFFFFFF


def avcam_facts(a: Image) -> dict[str, object]:
    f: dict[str, object] = {}
    # RelMgr emite {tipo 2, 0x3011} con origen 0x40193 y DESTINO 0x30001.
    assert a.u16(0x4379EBA8) & 0xFBF0 == 0xF240  # movw r3,#0x3011
    assert a.lit(0x4379EBC4) == 0x30001 and a.lit(0x4379EBC6) == 0x40193
    assert a.bl(0x4379EBC8) == 0x43AEAF18
    assert a.u16(0x43AEAF44) == 0x4628 and a.bl(0x43AEAF48) == 0x4356120C  # Send(r5=r1)
    assert a.bl(0x43AEAF28) == 0x435612D0 and a.u16(0x43AEAF22) == 0x4608  # Alloc(r1)
    f["relmgr_3011_dest_queue"] = "0x30001 (r1); 0x40193 es reply/origen (r2 -> 0x43aeaedc)"
    # Receptor de la cola 0x30001: bucle CamMgr.
    assert a.lit(0x437FEE0A) == 0x30001 and a.bl(0x437FEE12) == 0x43561260
    assert a.bl(0x437FEEAA) == 0x43809148 and a.bl(0x437FEEB4) == 0x438052D8
    f["queue_30001_receiver"] = "0x437fee08: tipo 0/2 -> 0x43809148, tipo 5 -> 0x438052d8"
    # Traductor ObjMsg 0x3000..0x3034 -> código local; 0x3011 -> 0x100.
    tbh = {0x3000 + i: 0x43809170 + 2 * a.u16(0x43809170 + 2 * i) for i in range(0x35)}
    assert tbh[0x3011] == 0x43809254 and tbh[0x3013] == 0x43809284
    assert a.u32(0x43809278) == 0x7380F44F  # mov.w r3,#0x100
    assert a.lit(0x43809270) == 0x302D9 and a.bl(0x43809462) == 0x438090E0
    f["objmsg_to_local"] = {hex(k): hex(v) for k, v in tbh.items() if k in (0x3011, 0x3012, 0x3013, 0x3014, 0x3015)}
    # Receptor 0x302d9 -> máquina de estados -> estado con handler 0x43807f4c.
    assert a.lit(0x4380990C) == 0x302D9 and a.bl(0x43809914) == 0x43561260
    assert a.bl(0x43809940) == 0x43807008
    assert a.u32(0x43FCD3E0) == 0x43807F4D and a.u32(0x43FCD3C4) == 0x43FFFD94
    assert a.bl(0x438082CE) == 0x43807D80
    assert {a.bl(x) for x in (0x43807E74, 0x43807EB4, 0x43807EEE, 0x43807F2A)} == {0x43809ED8}
    assert a.u32(0x44021ED0) == 0x437DF641 and a.bl(0x43809EFC) == 0x439018B0
    assert a.bl(0x437DF87A) == 0x437DF338 and a.bl(0x437DF5C2) == 0x437EABFC
    # Receptor real de 0x40193 y su tabla de 35 filas (corrige s20: 0x43ffff84 -> 0x44000174).
    assert a.lit(0x4381D16E) == 0x40193 and a.bl(0x4381D176) == 0x43561260
    assert a.pic(0x4381D18E, 0x4381D190) == 0x44000174 and a.u16(0x4381D1CA) == 0x2C23
    rows = [(a.u32(0x44000174 + 12 * k), a.u32(0x44000178 + 12 * k)) for k in range(35)]
    assert rows[0] == (0x4044, 0x43AEAA4B) and rows[4] == (0x4043, 0x4379E3FD)
    f["queue_40193_receiver"] = "0x4381d16c; tabla 0x44000174 (35 filas, id u16 en msg+2)"
    f["table_40193"] = {hex(i): hex(fn & ~1) for i, fn in rows}
    # Selectores y tablas de descriptores.
    assert a.u32(0x44022934) == 0x43EDCCF8 and a.u32(0x44025F60) == 0x43EDDD08
    exp_rows = [a.u32(g) & ~1 for g in (0x44023A6C, 0x440265B8, 0x4401F664, 0x44023054, 0x44026070, 0x44022DD4, 0x44023C3C)]
    ca_req = {0x43B1BE54: 0x43B1BE36, 0x43B1BEB6: 0x43B1BE98, 0x43B1BF22: 0x43B1BF04, 0x43B1BF84: 0x43B1BF66,
              0x43B1BFE6: 0x43B1BFC8, 0x43B1C052: 0x43B1C034, 0x43B1C0B2: 0x43B1C096}
    for site, row in ca_req.items():
        assert a.bl(site) == 0x438C2538 and row in exp_rows
    f["outer_rows_calling_ca_request_0x438c2538"] = ["+0xa0", "+0xb4", "+0xc8", "+0xdc", "+0xf0", "+0x104", "+0x118"]
    # Petición CA: 0x438c2538 -> 0x438d033c -> CAIF eventos 1 y 3.
    assert a.bl(0x438C2638) == 0x438D033C
    assert a.bl(0x438D0358) == 0x437DB858 and a.u16(0x438D0352) == 0x2001
    assert a.bl(0x438D038C) == 0x437DB858 and a.u16(0x438D0386) == 0x2003
    tbb = {e: 0x437DB89E + 2 * a.data[0x437DB89E - LIRO + e] for e in range(14)}
    assert tbb[1] == 0x437DB8BC and tbb[3] == tbb[8] == 0x437DB8B4
    assert a.bl(0x437DB8DA) == 0x436B8A50 and a.bl(0x43ACABD0) == 0x436BA234
    assert a.lit(0x436B897A) == 0x1502C7 and a.lit(0x436B89EC) == 0x1502C7
    assert a.lit(0x436BA0FC) == 0x1502C7 and a.bl(0x436BA104) == 0x43561260
    f["caif_event_targets"] = {e: hex(t) for e, t in tbb.items()}
    f["ca_task_queue"] = "0x1502c7, receptor 0x436ba0fc -> máquina 0x436bc140"
    return f


def input_ko_facts() -> dict[str, object]:
    d = INPUT_KO.read_bytes()
    assert hashlib.sha256(d).hexdigest() == SHA[INPUT_KO]
    shoff = struct.unpack_from("<I", d, 0x20)[0]
    entsize, num, strndx = struct.unpack_from("<HHH", d, 0x2E)
    secs = [struct.unpack_from("<IIIIII", d, shoff + i * entsize) for i in range(num)]
    stro = secs[strndx][4]
    text = next(s for s in secs if d[stro + s[0]:].split(b"\0", 1)[0] == b".text")
    word = lambda off: struct.unpack_from("<I", d, text[4] + off)[0]
    queues = {"kbd_send_event": word(0xC44), "front_key_sync": word(0x144), "liro_adc_sync": word(0xB4),
              "vgrip_key_sync": word(0x198), "own_queue": word(0x3670)}
    assert queues["kbd_send_event"] == 0x7A0020 and queues["front_key_sync"] == 0x280132
    return {k: hex(v) for k, v in queues.items()}


def libobj_facts() -> dict[str, object]:
    d = LIBOBJ.read_bytes()
    assert hashlib.sha256(d).hexdigest() == SHA[LIBOBJ]
    w = lambda off: struct.unpack_from("<I", d, off)[0]
    assert w(0x806DAC) == 0x7A0020  # InfraInput: osal_rcv_msg_tmo(0x7a0020) en 0x806b24
    assert all(w(o) == 0x40193 for o in (0xAF92D0, 0xAF9344, 0xAF93B4, 0xAF9424))
    # Ids construidos (byte2 | byte3<<8): adds #0x3d/#0x3e sobre 5 -> 0x42/0x43; movs #0x44/#0x45; byte3 0x40.
    assert d[0xAF9280:0xAF9282] == bytes.fromhex("3d33") and d[0xAF92F4:0xAF92F6] == bytes.fromhex("3e33")
    return {"infrainput_rx_queue": "0x7a0020", "relmgr_ids_sent_to_0x40193": ["0x4042", "0x4043", "0x4044", "0x4045"]}


def darwin_facts() -> dict[str, object]:
    dv = Image(DARWIN, DARWIN_ROM)
    assert dv.bl(0x20C78) == 0x1B080 and dv.bl(0x20C92) == 0x20C74
    # P4D (0x234) solo tipos 1/2 (excluye 3); P4E (0x238) tipos 1/2/3; tipo 0 -> ninguna escritura.
    assert dv.u16(0x20C9E) == 0x2803 and dv.u16(0x20CC0) == 0x2803
    assert dv.u32(0x20CA8) == 0x700DF44F and dv.u32(0x20D10) == 0x700EF44F  # mov.w r0,#0x234 / #0x238
    return {"p4d_types": [1, 2], "p4e_types": [1, 2, 3], "gate": "0x20c74 = 0x1b080(0)&7 in {1,2,3}"}


def main() -> None:
    a = Image(AVCAM, LIRO)
    out = {"avcam": avcam_facts(a), "input_ko": input_ko_facts(), "libobj": libobj_facts(), "darwin": darwin_facts(),
           "schematic_a6000_service_L3": {
               "S0019 shutter switch": "XS_1 (1st), XS_2 (2nd), S1S2_GND; pág. 48",
               "IC6000 main SoC": "XS_1 -> GPIO_S_11 (L15, vía D1100); XS_2 -> GPIO_S_13 (L14); pág. 26",
               "IC5700 Darwin": "XS_1 -> P32/INT10; MSS_S2_REQ_CA -> P29/INT05; DWN_IN_RELEASE -> P06/INT30; pág. 23",
               "IC6000 <- Darwin": "CA_RELEASE_LOCK_MSS -> GPIO_S_7 (L18); pág. 26",
               "method": "pdftotext -bbox, misma fila y; sin inspección visual"}}
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print("PASS", Path(__file__).with_suffix(".json"))


if __name__ == "__main__":
    main()
