import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "gui" / "avcam"))
import mensajes as M  # noqa: E402

# muestras reales de analysis/gui/g22/harness/live/t10a/avcam.jsonl
ORDEN_40EC = bytes.fromhex("0500ec400200008001")
RESP_4049 = bytes.fromhex("010049400500008000f00000")
NOTIF_1016 = bytes.fromhex("040016100000000001")


def test_decodifica_orden_y_respuesta_reales():
    o = M.decodifica(ORDEN_40EC)
    assert (o.tipo, o.id, o.seq, o.carga) == (M.TIPO_AJUSTE, 0x40EC, 2, b"\x01")
    r = M.decodifica(RESP_4049)
    assert (r.tipo, r.id, r.seq) == (M.TIPO_RESPUESTA, 0x4049, 5) and r.carga == bytes.fromhex("00f00000")


def test_ida_y_vuelta():
    for b in (ORDEN_40EC, RESP_4049):
        assert M.codifica(M.decodifica(b)) == b
    assert M.decodifica(NOTIF_1016).tipo == M.TIPO_NOTIF


def test_respuesta_repite_id_y_seq():
    o = M.decodifica(bytes.fromhex("05001b400e0000800000010001000000"))
    r = M.respuesta(o)
    assert (r.id, r.seq, r.tipo) == (0x401B, 14, M.TIPO_RESPUESTA) and r.carga.startswith(b"\x00\xf0")
    assert M.ORDENES[0x401B][1] is True
