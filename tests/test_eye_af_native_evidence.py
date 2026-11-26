"""Eye AF nativo de la A6000: comprobaciones de bytes sobre el firmware extraído.

Fija mecánicamente lo que afirma `docs/capture/eye-af-nativo-a6000.md`: el detector de ojos
existe en `av-cam`, sus datos por ojo se copian a un contexto concreto y la orden de punto de
AF que usa la app remota lleva `msgid 0x192` / `paramid 0x8d`.

Todo se omite si el firmware no está extraído (el CI del repositorio corre sin firmware).
"""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AVCAM_6000 = ROOT / "analysis" / "rea-independent" / "input" / "av-cam.bin"
AVCAM_6300 = (ROOT / "firmware" / "extracted" / "a6300-fw201" / "payload" / "firmware.tar_unpacked"
              / "0700_part_image" / "dev" / "nflasha3_unpacked_unpacked" / "av-cam.bin")
ORB = (ROOT / "firmware" / "extracted" / "fw321" / "firmware.tar_unpacked" / "0700_part_image"
       / "dev" / "nflasha15_unpacked_unpacked" / "bin" / "orb-server")

BASE_6000 = 0x43541000  # av-cam de la A6000: vaddr = BASE + offset (convención del proyecto)


def _leer(path: Path) -> bytes:
    if not path.is_file():
        pytest.skip(f"falta {path.relative_to(ROOT)} (firmware no extraído)")
    return path.read_bytes()


def _bytes_en(data: bytes, vaddr: int, base: int, n: int) -> bytes:
    off = vaddr - base
    return data[off:off + n]


def _texto_a_offset(elf: bytes) -> int:
    """diferencia (vaddr - offset) de .text, leída de la tabla de secciones del ELF32."""
    e_shoff = struct.unpack_from("<I", elf, 0x20)[0]
    e_shentsize = struct.unpack_from("<H", elf, 0x2E)[0]
    e_shnum = struct.unpack_from("<H", elf, 0x30)[0]
    e_shstrndx = struct.unpack_from("<H", elf, 0x32)[0]
    str_off = struct.unpack_from("<I", elf, e_shoff + e_shstrndx * e_shentsize + 0x10)[0]
    for i in range(e_shnum):
        base = e_shoff + i * e_shentsize
        nombre_off = struct.unpack_from("<I", elf, base)[0]
        nombre = elf[str_off + nombre_off:elf.index(b"\0", str_off + nombre_off)].decode()
        if nombre == ".text":
            sh_addr, sh_offset = struct.unpack_from("<II", elf, base + 0x0C)
            return sh_addr - sh_offset
    raise AssertionError("el ELF no tiene .text")


def test_detector_de_ojos_presente_en_avcam():
    data = _leer(AVCAM_6000)
    texto = data.decode("latin-1")
    assert "EyeDetection" in texto, "no aparece la cadena del motor de detección de ojos"
    assert "FC/Drv/fc_drv_edt.cpp" in texto, "falta el driver EDT del módulo Camera::FC"
    assert "idt_edt_start" in texto and "idt_edt_get_result" in texto
    # dirección de la cadena (0x43cf7022) usada en el informe
    assert data.find(b"EyeDetection\0") == 0x43CF7022 - BASE_6000


def test_el_productor_copia_los_ojos_al_contexto():
    """0x437b6ee4: ctx+0xde/0xdf = validez de cada ojo; ctx+0xe0..0xe7 = sus rectángulos."""
    data = _leer(AVCAM_6000)
    # strb.w r1, [r6, #0xde] / strb.w r1, [r6, #0xdf]
    assert _bytes_en(data, 0x437B6FCE, BASE_6000, 4) == bytes.fromhex("86f8de10")
    assert _bytes_en(data, 0x437B6FF2, BASE_6000, 4) == bytes.fromhex("86f8df10")
    # ldrh.w r1, [r7, #0x56] (origen: x del ojo izquierdo en el resultado del detector)
    assert _bytes_en(data, 0x437B6FD8, BASE_6000, 4) == bytes.fromhex("b7f85610")
    # strh.w r1, [r6, #0xe0] (destino en el contexto de FC)
    assert _bytes_en(data, 0x437B6FDC, BASE_6000, 4) == bytes.fromhex("a6f8e010")


def test_el_consumidor_usa_los_ojos_y_avisa_si_son_invalidos():
    """0x437b7200: el marco de AF se calcula desde los ojos; si el flag por ojo es 0, avisa."""
    data = _leer(AVCAM_6000)
    texto = data.decode("latin-1")
    assert "Eye data is invalid, but lc flag is true." in texto
    # cmp r3, #1 tras leer ctx+0xdf y ctx+0xde (guardas por ojo)
    assert _bytes_en(data, 0x437B723E, BASE_6000, 4) == bytes.fromhex("94f8df30")
    assert _bytes_en(data, 0x437B7274, BASE_6000, 4) == bytes.fromhex("94f8de30")


def test_a6300_anade_el_estado_de_enfocar_al_ojo_y_la_a6000_no_lo_tiene():
    """La diferencia nativa: CPafStateEyeFocus (seguimiento continuo) sólo en la A6300."""
    a6000 = _leer(AVCAM_6000).decode("latin-1")
    a6300 = _leer(AVCAM_6300).decode("latin-1")
    assert "CPafStateEyeFocus" not in a6000, "la A6000 tendría el estado continuo de la A6300"
    assert "CPafStateEyeFocus" in a6300
    assert "CPafStateEyeStart" in a6000, "sí debe tener Eye-Start AF"
    for cadena in ("EyeDetection", "idt_edt_start"):
        assert cadena in a6000 and cadena in a6300


def test_la_orden_del_punto_de_af_lleva_192_y_8d():
    """orb-server 0x2150d0: movs r2,#0x8d ; 0x2150d2: mov.w r1,#0x192 (paramid y msgid)."""
    data = _leer(ORB)
    assert data[:4] == b"\x7fELF", "orb-server debe ser ELF"
    base = _texto_a_offset(data)
    assert _bytes_en(data, 0x2150D0, base, 2) == bytes.fromhex("8d22")      # movs r2, #0x8d
    assert _bytes_en(data, 0x2150D2, base, 4) == bytes.fromhex("4ff4c971")  # mov.w r1, #0x192


def test_eye_start_af_es_del_visor_y_no_eye_af():
    """Corrige la etiqueta de g83: EYE_START_AF es el sensor del visor, no el ojo del sujeto."""
    data = _leer(AVCAM_6000).decode("latin-1")
    # el módulo EyeSens (sensor de proximidad del visor) convive con Eye-Start AF
    assert "[EyeSens] EYE_DET_PORT:%d, EYE_DET_BIT:%d" in data
    assert "EyeSens" in data
