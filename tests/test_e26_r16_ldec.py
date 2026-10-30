"""E26-R16 — pruebas offline: conciliación 89/111 B, estructura de segmentos TPZL y sectores por petición.

Dependen de firmware local no versionado (``firmware/``, ``analysis/e25-27``, volcados); se omiten si faltan.
Son comprobaciones de archivos y de desensamblado: no demuestran comportamiento del LDEC físico.
"""

import importlib
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))

LZ = importlib.import_module("r16_lz_features")
DIS = importlib.import_module("r16_dis")
needs_fw = pytest.mark.skipif(
    not LZ.ORIG.is_file() or not LZ.INTEG.is_file(),
    reason="firmware local no versionado",
)
needs_loader = pytest.mark.skipif(
    not DIS.BL.is_file(), reason="bootloader.bin histórico ausente"
)


def _block(*segments: bytes) -> bytes:
    return b"".join(segments)


def test_synthetic_segment_walk():
    lit = (
        bytes([0xF0, 0x00]) + bytes(8) + bytes([0x01, 0x00, 0x00])
    )  # 8 literales + terminador
    assert LZ.seg_sizes(lit * 2) == [("lz", 8), ("lz", 8)]
    raw = bytes([0x0F, 0, 4, 0]) + bytes(4)
    assert LZ.seg_sizes(raw) == [("raw", 4)]
    assert LZ.seg_sizes(bytes([0xAA])) == [("bad", 0xAA)]


@needs_fw
def test_sony_blocks_are_16_segments_of_4096():
    st = LZ.segment_structure(LZ.ORIG)
    assert st["segmentos_por_bloque"] == {16: 369}
    assert set(st["tamanos_segmento"]) == {"lz:4096", "raw:4096"}


@needs_fw
def test_integrated_325_breaks_segment_structure_only_in_blocks_0_48_57():
    st = LZ.segment_structure(LZ.INTEG)
    assert st["segmentos_por_bloque"] == {16: 366, 1: 3}
    assert st["tamanos_segmento"]["lz:65536"] == 3
    d = LZ.INTEG.read_bytes()
    _, _, toc, _ = struct.unpack_from("<4sIII", d, 0)
    single = [
        i
        for i in range(369)
        if len(
            LZ.seg_sizes(
                d[struct.unpack_from("<II", d, toc + 8 * i)[0] :][
                    : struct.unpack_from("<II", d, toc + 8 * i)[1]
                ]
            )
        )
        == 1
    ]
    assert single == [0, 48, 57]


@needs_loader
def test_loader3_passes_block_size_shr_12_as_unit_count():
    # c01fde0a: lsrs r0, r7, #0xc ; c01fde0c: str r0, [sp, #0x10] (job+0xc) con r7 = 1 << shift
    assert DIS.dis(0xC01FDE0A, 4) == [
        "c01fde0a: lsrs r0, r7, #0xc",
        "c01fde0c: str r0, [sp, #0x10]",
    ]
    assert (1 << 16) >> 12 == 16


def test_arm7_copies_job_fields_c_and_10_not_8():
    arm7 = importlib.import_module("r16_arm7")
    if not arm7.BL.is_file():
        pytest.skip("bootloader.bin histórico ausente")
    assert arm7.sha().startswith("b70a89a0")
    body = "\n".join(arm7.dis(0x3F4, 0x48))
    assert "ldr r3, [r0, #0xc]" in body and "ldr r0, [r0, #0x10]" in body
    assert "[r0, #8]" not in body


@needs_fw
def test_avcam_reconciliation_89_bionz_plus_22_darwin():
    rec = importlib.import_module("r16_avcam_reconcile").main()
    assert rec["integ_eq_extraida"] and rec["nflasha3_artifact_eq_tar"]
    assert rec["bytes_distintos_orig_vs_integ"] == 89 and rec["darwin_distintos"] == 22
    assert rec["manifiesto_diff_count"] == {
        "c3b": 61,
        "darwin": 22,
        "selector": 28,
        "total": 111,
    }
    assert rec["distintos_en_parches"] == 89 and rec["distintos_fuera_de_parches"] == []
    assert rec["bionz_escritos"] == 92
