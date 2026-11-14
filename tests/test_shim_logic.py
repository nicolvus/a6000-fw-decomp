"""§5.37: lógica pura del shim (shimlogic.h): mapeo monótono de prioridades RT (1..159 -> 1..99) y contexto de osal_reg_msg_queue_cb; se compila con el compilador del anfitrión."""
import itertools
import shutil
import subprocess
from pathlib import Path

import pytest

SHIM = Path(__file__).resolve().parents[1] / "scripts" / "gui" / "harness" / "shim"
C = r'''#include <stdio.h>
#include "shimlogic.h"
int main(void) { for (int p = 0; p <= 170; p++) printf("%d ", rtprio_map(p, 99)); printf("\n"); for (int p = 0; p <= 170; p++) printf("%d ", rtprio_map(p, 159));
    unsigned upm[4] = {0x8817b76c, 0, 0x8817b740, 0}, obj[4] = {0x94fe6c94, 0, 0x1000, 0}, nul[4] = {0x10, 0, 0, 0}, mismo[4] = {0x1000, 0, 0x1000, 0};
    printf("\n%d %d %d %d", reg_ctx_is_t2(upm), reg_ctx_is_t2(obj), reg_ctx_is_t2(nul), reg_ctx_is_t2(mismo)); return 0; }
'''


@pytest.fixture(scope="module")
def tablas(tmp_path_factory):
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    if not cc:
        pytest.skip("sin compilador de C")
    d = tmp_path_factory.mktemp("rtprio")
    (d / "t.c").write_text(C)
    subprocess.run([cc, "-I", str(SHIM), str(d / "t.c"), "-o", str(d / "t")], check=True)
    a, b, c = subprocess.run([str(d / "t")], capture_output=True, text=True, check=True).stdout.strip().split("\n")
    return [int(x) for x in a.split()], [int(x) for x in b.split()], [int(x) for x in c.split()]


def test_monotono_y_dentro_del_rango_del_anfitrion(tablas):
    m99 = tablas[0]
    assert all(a <= b for a, b in itertools.pairwise(m99[1:]))
    assert 1 <= min(m99[1:]) and max(m99) == 99 and m99[0] == 0 and m99[159] == 99


def test_valores_medidos_de_libmpr_siguen_distintos_y_ordenados(tablas):
    m99 = tablas[0]
    assert 99 >= m99[123] > m99[120] > m99[117] > m99[99]  # 80/81/82
    assert m99[:50] == list(range(50))  # los hilos bajos no cambian


def test_identidad_si_el_anfitrion_admite_159(tablas):
    m159 = tablas[1]
    assert m159[:160] == list(range(160))


def test_contexto_de_registro_es_t2_si_t0_es_miembro_de_t2(tablas):
    upm, lejos, sin_ctx, mismo = tablas[2]
    assert (upm, lejos, sin_ctx, mismo) == (1, 0, 0, 0)  # solo UpmWrapper (this+0x2c con this) cambia a t[2]
