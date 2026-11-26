"""El diagnóstico de estado del runbook lee la tabla y los bytes del DFB/FBS sin escribir nada."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts")]
import film_pb1_sector31 as R


class CamaraFalsa:
    """Memoria de mentira: la tabla de 30 entradas con sólo el idx 10 poblado."""

    def __init__(self):
        self.mem = dict.fromkeys(range(R.OFF_TABLA, R.OFF_TABLA + R.N_ENTRADAS * R.TAM_ENTRADA), 0)
        self.mem.update({0x9E484C: 0x01, 0x9E598C: 0x00})
        e = R.OFF_TABLA + R.TAM_ENTRADA * 10
        self.mem.update({e: R.SECTOR, e + 4: 3, e + 8: 1, e + 0xC: 6})

    def _rango(self, ini, n):
        return {addr: self.mem[addr] for addr in range(ini, ini + n) if addr in self.mem}

    def tabla(self, pid, base):
        return self._rango(base + R.OFF_TABLA, R.N_ENTRADAS * R.TAM_ENTRADA)

    def peek(self, pid, addr, n):
        return self._rango(addr, n)


def test_estado_ve_el_sector_y_los_bytes_del_fbs(capsys):
    e = R.estado(CamaraFalsa(), pid=1, base=0, etiqueta="ahora")
    assert e["idx10"]["handle"] == 3 and e["idx10"]["valido"] == 1
    assert [x["idx"] for x in e["con_handle"]] == [10]
    salida = capsys.readouterr().out
    assert "DFB/FBS (diagnóstico)" in salida
    assert "[0x9e484c]=0x01" in salida and "[0x9e598c]=0x00" in salida


@pytest.mark.parametrize(("campo", "valor"), [("sector", 0x30), ("om", 9)])
def test_veredicto_rechaza_fila_de_otro_sector_o_modo(campo, valor):
    e = {"sector": R.SECTOR, "handle": 6, "valido": 1, "om": 6}
    e[campo] = valor
    assert not R.veredicto({"idx10": e, "con_handle": [e]}, None)


@pytest.mark.parametrize("direccion", [R.OFF_TABLA + 0x257, R.OFF_REPARACION])
def test_estado_rechaza_lectura_incompleta(direccion):
    cam = CamaraFalsa()
    del cam.mem[direccion]
    with pytest.raises(R.Fallo, match="lectura incompleta"):
        R.estado(cam, pid=1, base=0, etiqueta="ahora")
