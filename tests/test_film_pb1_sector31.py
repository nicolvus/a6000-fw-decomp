"""El diagnóstico de estado del runbook lee la tabla y los bytes del DFB/FBS sin escribir nada."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts")]
import film_pb1_sector31 as R


class CamaraFalsa:
    """Memoria de mentira: la tabla de 30 entradas con sólo el idx 10 poblado."""

    def __init__(self):
        self.mem = {0x9E484C: 0x01, 0x9E598C: 0x00}
        for i in range(R.N_ENTRADAS):
            e = R.OFF_TABLA + i * R.TAM_ENTRADA
            self.mem.update({e: 0, e + 4: 0, e + 8: 0, e + 0xC: 0})
        e = R.OFF_TABLA + R.TAM_ENTRADA * 10
        self.mem.update({e: R.SECTOR, e + 4: 3, e + 8: 1, e + 0xC: 6})

    def _rango(self, ini, n):
        return {ini + i: self.mem.get(ini + i, 0) for i in range(n)}

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
