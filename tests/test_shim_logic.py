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


def test_ioctl_104_de_la_sd_da_el_ultimo_lba_y_no_un_solo_sector(tmp_path):
    """§5.39: libInfraMediaCommon+0x10702 calcula los sectores del soporte como `out[0x1c] + 1` (out = a + 8, a[0x24/4] = último LBA); con a[0x24/4] = 0 el PDM de
    libInfraFsys veía una partición de 1 sector (pdm_part_logical_read devolvía 0x12 en el LBA 0x20 = FAT) y Fsys_Mount desmontaba el volumen."""
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    if not cc:
        pytest.skip("sin compilador de C")
    (tmp_path / "t.c").write_text('#include <stdio.h>\n#include <string.h>\n#include "shimlogic.h"\n'
                                  'int main(void) { unsigned a[20]; memset(a, 0xaa, sizeof a); sd_partinfo_fill(a, 8388608);'
                                  ' printf("%u %u %u", a[0x24 / 4] + 1, a[0x38 / 4], a[0]); return 0; }\n')
    subprocess.run([cc, "-I", str(SHIM), str(tmp_path / "t.c"), "-o", str(tmp_path / "t")], check=True)
    sectores, bloque, estado = map(int, subprocess.run([str(tmp_path / "t")], capture_output=True, text=True, check=True).stdout.split())
    assert sectores == 8388608 and estado == 0
    assert bloque == 8388608  # a[0x38/4] sin tocar: sin dato verificado (se queda como estaba)


def test_ioctl_5_de_la_sd_se_clasifica_sdhc_8201_como_en_libinframediacommon(tmp_path):
    """§5.40: libInfraMediaCommon+0x10770 lee la capacidad (u64) en ctx+0x48 = a[0x24/4..0x28/4] del ioctl 5 (el buffer es ctx+0x24) y clasifica: >= 0x800000001 -> 0x8202
    SDXC; > 0x80000000 -> 0x8201 SDHC; si no 0x8200. libInfraFsys+0x24d14 la pasa a 0x8401 (SDHC)/0x8400 (SDSC). Una SD de 4 GB debe dar 0x8201 -> 0x8401."""
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    if not cc:
        pytest.skip("sin compilador de C")
    (tmp_path / "t.c").write_text('#include <stdio.h>\n#include <string.h>\n#include "shimlogic.h"\n'
                                  'int main(void) { unsigned s[] = {2097152, 8388608, 67108864, 134217728}; for (int i = 0; i < 4; i++) { unsigned a[0x30]; sd_cardinfo_fill(a, s[i]);'
                                  ' printf("%x %x %x %u\\n", sd_media_class(a[0x24 / 4], a[0x28 / 4]), sd_fsys_class(sd_media_class(a[0x24 / 4], a[0x28 / 4])), ((unsigned char *)a)[0], a[0x20 / 4] + 1); } return 0; }\n')
    subprocess.run([cc, "-I", str(SHIM), str(tmp_path / "t.c"), "-o", str(tmp_path / "t")], check=True)
    f = [ln.split() for ln in subprocess.run([str(tmp_path / "t")], capture_output=True, text=True, check=True).stdout.strip().split("\n")]
    assert [x[0] for x in f] == ["8200", "8201", "8201", "8202"]  # 1 GB SDSC, 4 GB SDHC, 32 GB (0x800000000 < 0x800000001: SDHC), 64 GB SDXC
    assert [x[1] for x in f][1] == "8401" and f[0][1] == "8400"
    assert f[1][2] == "3" and f[1][3] == "8388608"
