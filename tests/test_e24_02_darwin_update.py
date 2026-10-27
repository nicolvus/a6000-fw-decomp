"""E24-02: comprobaciones reproducibles del protocolo de actualización de Darwin.

Leen binarios locales no versionados (firmware oficial, volcado NAND, manual de servicio);
se omiten si faltan. Informe: docs/capture/e24-02-protocolo-actualizacion-darwin.md.
"""
import re
import shutil
import struct
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NAND = ROOT / "analysis/camera-dumps/nand-20261020"
FW = ROOT / "firmware/extracted"
DARWIN = FW / "fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
SERVICE = ROOT / "references/manuals/a6000_service_L3.pdf"
FM3 = ROOT / "references/manuals/fm3_peripheral_main.txt"
BASE = 0x4200

capstone = pytest.importorskip("capstone")
MD = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)


def _need(path: Path) -> bytes:
    if not path.exists():
        pytest.skip(f"falta {path.relative_to(ROOT)}")
    return path.read_bytes()


def _u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def _dis(data: bytes, base: int, addr: int, n: int) -> list[str]:
    """Instrucciones `mnemonic op_str` desde `addr` (ocupa `n` bytes)."""
    return [f"{i.mnemonic} {i.op_str}" for i in MD.disasm(data[addr - base:addr - base + n], addr)]


@pytest.fixture(scope="module")
def core() -> bytes:
    return _need(DARWIN)


@pytest.fixture(scope="module")
def updater_root(tmp_path_factory) -> Path:
    img = NAND / "dev_nflasha1.bin"
    _need(img)
    if not (shutil.which("mcopy") and shutil.which("7z")):
        pytest.skip("faltan mtools/7z")
    out = tmp_path_factory.mktemp("nflasha1")
    subprocess.run(["mcopy", "-s", "-n", "-i", str(img), "::boot", str(out)], check=True)
    subprocess.run(["7z", "x", "-y", f"-o{out / 'initrd'}", str(out / "boot/initrd.img")],
                   check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out / "initrd/usr/bin"


def test_no_package_ships_darwin_boo():
    for tar in ("fw321/firmware.tar_unpacked", "a7s-fw320/payload/firmware.tar_unpacked",
                "a6300-fw201/payload/firmware.tar_unpacked"):
        root = FW / tar
        if not root.exists():
            pytest.skip(f"falta {root.relative_to(ROOT)}")
        assert sorted(p.name for p in (root / "0640_darwin").iterdir()) == ["darwin_core.bin"]


def test_core_is_mapped_at_0x4200_so_reset_vector_zero_is_not_core(core):
    # el core empieza en 0x4200 (SP, reset); el vector de reinicio del FM3 está en 0x0 (manual FM3)
    assert (_u32(core, 0), _u32(core, 4)) == (0x20002A00, 0x45C9)
    assert len(core) == 0x2665C  # tamaño de darwin.sum


def test_core_handoff_to_vector_zero_with_mailbox_4(core):
    # 0x45bc: msp = [r0]; pc = [r0+4]
    assert core[0x45BC - BASE:0x45C6 - BASE].hex() == "016881f30888d0f804f0"  # ldr r1,[r0]; msr msp,r1; ldr.w pc,[r0,#4]
    # único salto: `Upd main` pone [0x20000706]=4, [0x20000707]=0 y llama con r0=0
    assert _dis(core, BASE, 0x8DEE, 12) == ["movs r0, #4", "strb r0, [r5, #6]", "movs r0, #0",
                                            "strb r0, [r5, #7]", "bl #0x45bc"]
    assert _u32(core, 0x8E00 - BASE) == 0x20000700  # r5 = buzón de arranque (literal de 0x8daa)
    n_calls = 0
    for a in range(BASE, BASE + 0x23000, 2):
        i = list(MD.disasm(core[a - BASE:a - BASE + 4], a, 1))
        if i and i[0].mnemonic == "bl" and i[0].op_str == "#0x45bc":
            n_calls += 1
    assert n_calls == 1


def test_state_table_has_upd_entry_and_label(core):
    entry5 = [_u32(core, 0x25B50 + 5 * 16 + 4 * k - BASE) for k in range(2)]
    assert entry5 == [0x8DA5, 0x8DA9]  # 0x8da8 = `Upd main`
    assert b" Upd main" in core[0x8E00 - BASE:0x8E10 - BASE]


def test_com_task_dispatch_has_no_flash_update_commands(core):
    # InitCom 0x4bca..0x4ec0: despacha 0x11, 0x12, 0x13, 0x16 y nada más
    cmps = [m for a in range(0x4BCA, 0x4EC0, 2)
            for i in MD.disasm(core[a - BASE:a - BASE + 4], a, 1)
            if (m := re.fullmatch(r"r1, #(0x[0-9a-f]+)", i.op_str)) and i.mnemonic == "cmp"]
    assert sorted({m.group(1) for m in cmps}) == ["0x11", "0x12", "0x13", "0x16"]
    # 0x11: el estado 4 hace salir del bucle (`beq 0x4e0c`)
    assert _dis(core, BASE, 0x4D34, 6) == ["ldrb r0, [r5]", "cmp r0, #4", "beq #0x4e0c"]


def test_core_has_no_flash_programming_code(core):
    # ni secuencias de comando de flash (0x1550/0xaa8) ni escrituras en FLASH_IF (0x40000000)
    for a in range(BASE, BASE + 0x23000, 2):
        for i in MD.disasm(core[a - BASE:a - BASE + 4], a, 1):
            assert not re.search(r"#(0x1550|0xaa8|0x1554|0xaaa)\b", i.op_str), hex(a)
    # única lectura del bloque FLASH_IF: `ldr r0,[r1,#0x100]` (espejo CRTRMM) en 0x50e0
    assert _dis(core, BASE, 0x50E0, 8) == ["mov.w r1, #0x40000000", "ldr.w r0, [r1, #0x100]"]


def test_core_uses_hardware_crc_and_hw_watchdog(core):
    # CRC: ldr r3,[pc,#0x1c] en 0xa1e4 → 0x40039000; escribe bytes en +8 y lee +0xc
    lit = _u32(core, ((0xA1E4 + 4) & ~3) + 0x1C - BASE)
    assert lit == 0x40039000
    # alimentación del watchdog (0xa524): desbloqueo 0x1acce551 sobre 0x40011000 y borrado de +0xc
    assert _u32(core, 0xA538 - BASE) == 0x1ACCE551 and _u32(core, 0xA53C - BASE) == 0x40011000
    assert _dis(core, BASE, 0xA500, 4) == ["orr r0, r0, #2"]  # control: RESEN y luego INTEN


def test_firmup_frames_match_protocol(updater_root):
    elf = _need(updater_root / "ud_darwin_firmup.elf")

    def d(addr, n):
        return _dis(elf, 0x8000, addr, n)

    assert d(0x8B44, 6)[0] == "movw r5, #0x1021"            # CRC-16-CCITT
    assert d(0x8B5A, 2) == ["cmp r3, #0x7e"]                 # sobre 0x7e bytes
    assert d(0x8B90, 2) == ["movs r3, #0x80"]                # trama de 0x80 bytes
    assert d(0x8C68, 4) == ["movs r3, #0x14", "strb r3, [r6]"]            # inicio de actualización
    assert d(0x8D32, 2) == ["movs r3, #0x15"]                              # bloque de datos
    assert d(0x8CC4, 2) == ["cmp r3, #5"] and d(0x8D0A, 2) == ["cmp r3, #5"]  # estado «actualizando»
    assert d(0x8CFA, 2) == ["cmp r3, #0x10"]                               # com_id de la respuesta
    assert d(0x8F62, 2) == ["movs r2, #1"] and d(0x9034, 2) == ["movs r2, #2"]  # destino: 1 = boo, 2 = core
    assert d(0x8E88, 8)[0:2] == ["movs r3, #0x11", "add.w r0, r7, #0x78"]
    # el programa lee de la respuesta: [8..11] = desplazamiento, [0xc] = longitud (0 = fin)
    assert d(0x8D7A, 4)[0] == "ldrb.w r8, [r4, #9]" and d(0x8D80, 4)[0] == "ldrb.w sb, [r4, #0xc]"


def test_darwin_reboot_sends_state_3(updater_root):
    elf = _need(updater_root / "ud_darwin_reboot.elf")
    got = _dis(elf, 0x8000, 0x8D06, 12)
    assert got == ["movs r3, #0x11", "add.w r0, r7, #0x18", "strb r3, [r6]", "subs r3, #0xe",
                   "strb r3, [r6, #1]"]  # trama 0x11 con estado 3


def _pdf_words(page: int) -> list[tuple[str, float, float]]:
    if not (shutil.which("pdftotext") and SERVICE.exists()):
        pytest.skip("falta pdftotext o el manual de servicio")
    html = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-bbox", str(SERVICE), "-"],
                          capture_output=True, text=True, check=True).stdout
    return [(m[2], float(m[0]), float(m[1])) for m in
            re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)"[^>]*>([^<]+)<', html)]


def test_schematic_exposes_darwin_download_port():
    words = _pdf_words(23)
    at = {w: (x, y) for w, x, y in words}
    for net in ("MD0_DWN", "XDWN_RESET", "TRST_DWN", "TCK_DWN", "TDI_DWN", "TMS_DWN", "TDO_DWN",
                "DWN_UART_TXD", "DWN_UART_RXD", "INITX", "MD0"):
        assert net in at, net
    # DWN_UART_TXD/RXD salen alineados con P22/SOT0 y P21/SIN0 de IC5700
    assert abs(at["DWN_UART_TXD"][1] - at["P22/SOT0(SDA0)"][1]) < 2
    sin0 = [y for w, x, y in words if w == "P21/SIN0" and x > 700]  # etiqueta del lado de IC5700 (no la del símbolo)
    assert any(abs(at["DWN_UART_RXD"][1] - y) < 2 for y in sin0)
    conn = {w for w, _, _ in _pdf_words(38)}
    assert {"BOOT_MODE_1", "UART_RXD_DWN", "UART_TXD_DWN", "NSRST", "DEBUG_MODE"} <= conn


def test_fm3_manual_serial_writer_mode():
    text = _need(FM3).decode(errors="ignore")
    assert "Serial Writer Mode" in text
    assert re.search(r"Products other than TYPE0.*?0\s+1\s+Serial Writer Mode", text, re.DOTALL)
