"""Regresiones del inventario: etiqueta, cadena, referencia y módulo son distintos."""
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "pending_audit", ROOT / "analysis/s178_census/audit_pending.py"
)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def test_suffix_keeps_containing_string_and_reference():
    data = b"\0[IMAGING_CAP]: error [MODE_CAP]\0"
    rows = audit.occurrences(data, {"[MODE_CAP]"}, {hex(audit.BASE + 1): [123]})
    item = rows["[MODE_CAP]"][0]
    assert item["cadena_vaddr"] == hex(audit.BASE + 1)
    assert item["token_vaddr"] != item["cadena_vaddr"]
    assert item["referencias_pic_candidatas"] == ["0x7b"]


def test_unknown_is_not_automatically_a_module():
    row = audit.classification("[FOO]", {})
    assert row["veredicto"] == "NO_VERIFICADO"
    assert row["examinada"] is False


def test_capture_precedes_volume():
    assert audit.priority("[MODE_CAP]", 0) < audit.priority("[DECMODEMGR]", 30)
    assert audit.priority("[DECMODEMGR]", 30) < audit.priority("[AUDDECCTRL]", 17)


def test_inventory_is_reproducible_and_complete():
    saved = json.loads((ROOT / "analysis/s178_census/pendientes_auditados.json").read_text())
    assert saved == audit.build(ROOT)
    detail = json.loads((ROOT / "analysis/s178_census/census_detalle.json").read_text())
    rows = saved["etiquetas"]
    assert {r["etiqueta"] for r in rows} == {
        k for k, v in detail.items() if v["estado"] in {"pendiente", "no-modulo"}
    }
    for row in rows:
        assert row["ocurrencias"]
        assert len(row["ocurrencias"]) == detail[row["etiqueta"]]["apariciones_token"]
        assert row["motivo"]
        if row["veredicto"] != "NO_VERIFICADO":
            assert row["fuente_evidencia"]


def test_priority_uses_recounted_containing_strings():
    rows = audit.build(ROOT)["etiquetas"]
    for row in rows:
        assert row["cadenas_con_pic_candidato"] == len({
            occ["cadena_vaddr"] for occ in row["ocurrencias"]
            if occ["referencias_pic_candidatas"]
        })
    keys = [audit.priority(row["etiqueta"], row["cadenas_con_pic_candidato"]) for row in rows]
    assert keys == sorted(keys)


def test_rejected_modules_are_not_coverage():
    detail = json.loads((ROOT / "analysis/s178_census/census_detalle.json").read_text())
    summary = json.loads((ROOT / "analysis/s178_census/census.json").read_text())["recuentos"]
    counts = {state: sum(v["estado"] == state for v in detail.values())
              for state in ("hito", "sub-etiqueta", "pendiente", "no-modulo")}
    assert sum(counts.values()) == 372
    assert counts["no-modulo"] == summary["descartadas_no_modulo"]
    assert summary["cubiertas_total"] == counts["hito"] + counts["sub-etiqueta"]
    for row in detail.values():
        if row["estado"] == "no-modulo":
            assert not row["hitos"] and not row["sub_de"]
            assert row["candidato_modulo"] == "RECHAZO"


def test_decisive_pic_edges_against_original_bytes():
    data = (ROOT / audit.BINARY).read_bytes()
    evidence = json.loads((ROOT / "analysis/s178_census/evidencia_bytes.json").read_text())
    for edge in evidence:
        add = int(edge["add"], 16)
        ldr = int(edge["ldr"], 16)
        pool = int(edge["pool"], 16)
        assert data[add - audit.BASE:add - audit.BASE + 2].hex() == edge["add_bytes"]
        assert data[ldr - audit.BASE:ldr - audit.BASE + len(bytes.fromhex(edge["ldr_bytes"]))].hex() == edge["ldr_bytes"]
        h = struct.unpack_from("<H", data, add - audit.BASE)[0]
        assert h & 0xFF78 == 0x4478  # ADD registro alto con PC como fuente
        reg = ((h >> 7) & 1) * 8 + (h & 7)
        first = struct.unpack_from("<H", data, ldr - audit.BASE)[0]
        if first & 0xF800 == 0x4800:
            assert (first >> 8) & 7 == reg
            assert ((ldr + 4) & ~3) + (first & 255) * 4 == pool
        else:
            assert first == 0xF8DF
            second = struct.unpack_from("<H", data, ldr - audit.BASE + 2)[0]
            assert second >> 12 == reg
            assert ((ldr + 4) & ~3) + (second & 0xFFF) == pool
        word = struct.unpack_from("<I", data, pool - audit.BASE)[0]
        assert hex(word) == edge["pool_word"]
        assert (add + 4 + word) & 0xFFFFFFFF == int(edge["cadena"], 16)


def test_sfr_log_branch_against_original_bytes():
    data = (ROOT / audit.BINARY).read_bytes()
    def at(address: int, size: int) -> bytes:
        return data[address - audit.BASE:address - audit.BASE + size]

    assert at(0x439a63a2, 2).hex() == "9342"  # cmp r3, r2
    assert at(0x439a63a6, 2).hex() == "04d1"  # bne: salta la traza
    assert at(0x439a63a8, 8).hex() == "5f48784405f468fa"
    assert int.from_bytes(at(0x439a64d4, 4), "little") == 0x00FF0481
    assert int.from_bytes(at(0x439a6528, 4), "little") + 0x439a63ae == 0x43ce757f


def test_rejections_are_format_fields_in_every_occurrence():
    saved = audit.build(ROOT)
    for row in saved["etiquetas"]:
        if row["veredicto"] != "RECHAZO":
            continue
        for occ in row["ocurrencias"]:
            text = occ["texto_hasta_nul_latin1"]
            assert occ["token_vaddr"] != occ["cadena_vaddr"]
            if row["etiqueta"].startswith("[MODE_CAP"):
                assert text.startswith("[IMAGING_CAP]: CamCore ") and "Error!" in text
            else:
                assert text.startswith("[CAM_UTIL_ADJ]:")
                assert row["etiqueta"] + ":%04x" in text
