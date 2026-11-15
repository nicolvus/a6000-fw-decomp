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


def test_envoltorios_resuelven_con_nextsym_y_no_con_dlsym_literal():
    """§5.41: dlsym toma el cerrojo del cargador; un hilo nuevo que lo pida mientras el principal está en dlopen cuelga el arranque."""
    import re
    from pathlib import Path

    src = (Path(__file__).resolve().parents[1] / "scripts/gui/harness/shim/sonyshim.c").read_text()
    assert not re.findall(r'dlsym\(RTLD_NEXT, *"', src)
    assert "nx_ptr[i] = dlsym(RTLD_NEXT, nx_names[i])" in src  # shim_init los resuelve antes de que arranque cualquier hilo


def test_sigsegv_diagnostico_no_se_pierde_en_el_invitado():
    """§5.42: la pila del manejador del shim y el dmesg quedaban en /tmp del invitado; im.sh los vuelca a la consola al morir im.elf, y SIGLOG=1 registra quién cambia la acción de SIGSEGV."""
    from pathlib import Path

    h = Path(__file__).resolve().parents[1] / "scripts/gui/harness"
    src, sh = (h / "shim/sonyshim.c").read_text(), (h / "im.sh").read_text()
    assert "imexit_diag" in sh and "IMSEGV" in sh and "IMDMESG" in sh
    assert 'getenv("SIGLOG")' in src and "int sigaction(" in src and '"sigaction"' in src


def test_envoltorios_no_reservan_marcos_grandes_en_la_pila():
    """§5.42: `char b[65536]` en fake_open gastaba 64 KiB de pila en CADA open(); THREAD_INFRA1/2 de libObj tienen 256 KiB y se desbordaban (SEGV al azar del arranque)."""
    import re
    from pathlib import Path

    src = (Path(__file__).resolve().parents[1] / "scripts/gui/harness/shim/sonyshim.c").read_text()
    grandes = [m.group(0) for m in re.finditer(r"(?<!static )(?:char|unsigned char|uint8_t|unsigned)\s+\w+\[(\d+|0x[0-9a-f]+)\]", src) if int(m.group(1), 0) >= 16384 and "snap" not in m.group(0)]  # snap: miembro de una estructura estática (rtw)
    assert not grandes, grandes


def test_envio_sincrono_no_se_reentra_en_la_misma_cola(tmp_path):
    """§5.42: el callback de la cola síncrona 0x924126 (libObj+0x7ddd88) vuelve a enviar a esa cola; el shim lo entrega en el mismo hilo y recursa (240 B por nivel) hasta agotar la pila (SEGV de arranque)."""
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    if not cc:
        pytest.skip("sin compilador de C")
    (tmp_path / "t.c").write_text(r'''#include <stdio.h>
#include "shimlogic.h"
int main(void) { sync_nest s = {{0}, 0}; int a = sync_nest_enter(&s, 0x924126), b = sync_nest_enter(&s, 0x924126), c = sync_nest_enter(&s, 0x720018);
    sync_nest_leave(&s, 0x720018); sync_nest_leave(&s, 0x924126); int d = sync_nest_enter(&s, 0x924126);
    for (int i = 0; i < 20; i++) sync_nest_enter(&s, 0x1000 + i); printf("%d %d %d %d %d", a, b, c, d, s.n <= 8); return 0; }
''')
    subprocess.run([cc, "-I", str(SHIM), str(tmp_path / "t.c"), "-o", str(tmp_path / "t")], check=True)
    # primera entrega sí, anidada en la misma cola no, otra cola sí, tras salir se puede volver a entregar, y la pila está acotada
    assert subprocess.run([str(tmp_path / "t")], capture_output=True, text=True, check=True).stdout == "1 0 1 1 1"


def test_nflasha4_responde_a_la_ioctl_de_libmpr_y_al_inicio_de_la_particion(tmp_path):
    """§5.43: libmpr (DFA::GetDeviceInfo, +0x2a40c0) abre /dev/nflasha4, hace ioctl 0x6e07 con un {?, lblk_size, num_of_lblks, ltu_size} y lee el inicio de la partición en
    /sys/block/nflasha0/nflasha0p4/start; con el dispositivo inerte (/dev/null, tamaño 0) FlashLib no veía ningún sector y las tablas de respaldo del MPR (RcsTbl) quedaban vacías."""
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    if not cc:
        pytest.skip("sin compilador de C")
    (tmp_path / "t.c").write_text(r'''#include <stdio.h>
#include <string.h>
#include "shimlogic.h"
int main(void) { unsigned a[8]; memset(a, 0xaa, sizeof a); nflash_lblkinfo_fill(a, 10u << 20); char s[16]; nflash_start_text(s, sizeof s);
    printf("%#x %u %#x %s %#x", a[1], a[2], a[3], s, a[4] & a[7]); return 0; }
''')
    subprocess.run([cc, "-I", str(SHIM), str(tmp_path / "t.c"), "-o", str(tmp_path / "t")], check=True)
    # bloque lógico 128 KiB (paso medido entre cabeceras del volcado), 10 MiB = 80 bloques, unidad 0x200; inicio 0x3140000 / 512.
    # La estructura es de 16 B: a[4..] son variables vecinas de la pila de libmpr ([r7+0x78] = 0x200 se usa de divisor; ponerla a 0 daba SIGFPE en el arranque, c43c).
    assert subprocess.run([str(tmp_path / "t")], capture_output=True, text=True, check=True).stdout == "0x20000 80 0x200 100864\n 0xaaaaaaaa"
