"""G22-B — arnés de la UI: formato de `bk.tbl` (gen_bk.py ↔ `bk_find` del shim) y compilación de `sonyshim.c`."""
from __future__ import annotations

import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts/gui/harness"
NVRAM = ROOT / "analysis/camera-dumps/20261105-volcado-total-nvram/backup_flash.bin"
CAM_LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib"
WORK = Path(os.environ.get("A6000_HARNESS_WORK", ROOT / "analysis/gui/g22/harness"))


# F4: DERECHA (0x1af, índice 0x14) a los 150 s e INTRO (CEC 0xe000000, índice 0x1bc) a los 160 s abren «Ajustes personalizados», página 4
SUBMENU_ENV = ("WAIT=200 CVWAIT=0 POKE=fef348 OPENVIEW=view/ROOT,view/GLOBAL_MENU OPENVIEWAT=40 OPENVIEWGAP=14 "
               "STARTEV=11004002:100,11004012,11004013 STARTGAP=f SALVAGE=0 SKIPFN=7fa3d4=0 ACKQ0=58003f FULLLOG=1 "
               "KEYQ=7a0020 KEYONACTIVE=0 KEYINIT=7000001:1:177 KEYINITON=06A_viewUnified2 GPUDUMP=/tmp/gpu.txt "
               "DUMPAT=185 DUMPTHR=ninguno AREADUMP=stream@80000000,stream@bc000000 "
               "INJECT=96:7a0020:1af,0,1,0,14/96:7a0020:1af,0,0,0,14/a0:7a0020:e000000,0,1,0,1bc/a0:7a0020:e000000,0,0,0,1bc")
PKG379 = ROOT / "analysis/gui/g22/pkg-379w"


def filas_de_texto(png: Path) -> int:
    """Filas de ajustes de la página del submenú: franjas con texto claro en la columna de nombres."""
    import numpy as np
    from PIL import Image
    b = (np.asarray(Image.open(png))[130:420, 20:330].max(axis=2) > 128).any(axis=1)
    return int(np.count_nonzero(np.diff(b.astype(int)) == 1) + b[0])


def bk_find(tbl: bytes, wanted: int) -> bytes | None:
    """Mismo recorrido que `bk_find()` en sonyshim.c: registros {id u32, len u32, datos rellenados a 4}."""
    o = 0
    while o + 8 <= len(tbl):
        i, n = struct.unpack_from("<II", tbl, o)
        if i == wanted:
            return tbl[o + 8:o + 8 + n]
        o += 8 + ((n + 3) & ~3)
    return None


def bk_u32(tbl: bytes, wanted: int) -> int:
    d = bk_find(tbl, wanted)
    assert d is not None and len(d) == 4, hex(wanted)
    return struct.unpack("<I", d)[0]


@pytest.mark.skipif(not NVRAM.exists(), reason="volcado NVRAM no disponible")
def test_gen_bk_sirve_la_zona_mwf(tmp_path: Path) -> None:
    out = tmp_path / "bk.tbl"
    subprocess.run([sys.executable, str(HARNESS / "gen_bk.py"), str(NVRAM), str(out)], check=True)
    tbl = out.read_bytes()
    # Valores que libObj pide al servicio 0x3e014d al arrancar (G22-B avance 5): base física y tamaño de la zona fija MWF.
    assert bk_u32(tbl, 0xFA0028) == 0x82DF9000
    assert bk_u32(tbl, 0xFA005D) == 0x7C000
    assert bk_find(tbl, 0xFFFFFFFF) is None


@pytest.mark.skipif(not (shutil.which("clang") and CAM_LIB.exists() and (WORK / "sysroot/usr/include/arm-linux-gnueabihf").is_dir()),
                    reason="clang, rootfs de la cámara o sysroot Debian (setup.sh) no disponibles")
def test_shim_compila_y_exporta_los_ganchos(tmp_path: Path) -> None:
    so = tmp_path / "sonyshim.so"
    subprocess.run(["sh", str(HARNESS / "shim/build.sh"), str(WORK / "sysroot"), str(CAM_LIB), str(so)], check=True)
    syms = subprocess.run(["readelf", "--dyn-syms", "-W", str(so)], capture_output=True, text=True, check=True).stdout
    for hook in ("open", "open64", "ioctl", "mmap", "fopen", "dlopen", "pthread_cond_wait", "munmap", "abort"):
        assert f" {hook}\n" in syms or f" {hook}@" in syms, hook


def test_gpu_draw_no_descarta_listas_de_mas_de_64_vertices() -> None:
    """§5.18z⁶: el marco de foco y las filas del menú son listas de 118–454 vértices; con tope 64 no se dibujaban y el cursor desaparecía."""
    src = (HARNESS / "shim/sonyshim.c").read_text()
    draw = src[src.index("static void gpu_draw("):src.index("/* LIVE=/dev/vportNp1")]
    assert "n > 64" not in draw and "n > 4095" in draw and "sx[4096]" in draw


def test_menu_se_reabre_con_la_ruta_real_de_la_camara() -> None:
    """§5.18z⁷: MENU con el menú cerrado abre «@V00E» (DefRootView::ActionOpenSettingMenu); el menú inicial usa la misma ruta y el shim sigue su estado por las trazas Vn/Vd."""
    live, _ = _live()
    assert "OPENVIEW=view/ROOT,@V00E" in live.SHIMENV
    src = (HARNESS / "shim/sonyshim.c").read_text()
    assert 'strncmp(p + 4, "07C_", 4)' in src and '"@V00E"' in src and "m[0] == 0x1ab && m[2] == 1 && !menu_open" in src


def test_postrootev_crea_modelstillrec_tras_view_root() -> None:
    """§5.18z⁸: tras abrir view/ROOT el shim lanza @T0E3 (POSTROOTEV), que instancia model/STILL_REC (@M00F)."""
    live, _ = _live()
    assert "POSTROOTEV=11004002:e3" in live.SHIMENV
    src = (HARNESS / "shim/sonyshim.c").read_text()
    assert 'getenv("POSTROOTEV") && !strcmp(it, "view/ROOT")' in src and 'startev(getenv("POSTROOTEV"))' in src


def test_vdf_59000e_responde_y_stat_msgq_cuenta_pendientes() -> None:
    """§5.18z⁹: cada petición a 0x59000e recibe respuesta tipo 2 (MSGID 0x8200) y stat_msgq informa los pendientes (freeOsalId no se bloquea)."""
    src = (HARNESS / "shim/sonyshim.c").read_text()
    assert "w[0] == 0x59000e && !getenv(\"NOVDF59\")" in src and "body[-1] = 0x8200" in src
    assert "o[0] = n; o[1] = o[2] = o[3] = 0;" in src


def test_efcs_emula_respuesta_objcamera_y_backup_107086e() -> None:
    """g22-respuesta-efcs-objcamera §6: la orden 0x75fa (libObj+0x689745) no llega a ObjCamera en el arnés; el shim aplica
    el efecto de CMP 0x75fb/EVT 0x85a6 (ranuras SET/ACT del modelo) y escribe Backup 0x107086e (1 = Activar, 2 = Desactivar);
    al crear ModelStillRec (libObj+0x681eb2) carga las ranuras desde ese registro para que el ajuste sobreviva al arranque en frío."""
    src = (HARNESS / "shim/sonyshim.c").read_text()
    assert "efcs_ra = base + 0x689745" in src and "efcs_pc = base + 0x681eb2" in src
    assert "0x107086e" in src and "base + 0x68e0ce + 1" in src and 'getenv("NOEFCS")' in src


def test_50004_pinget_responde_con_eco_de_pin() -> None:
    """g22-respuesta-efcs-objcamera §10: CAMUSER (libObj 0xaeebee → 0xa14f88) pide por dataflow a 0x50004 {cate 0x1000, msg} con
    pinType/pinDir/pinNo en carga+8..+0x13 y compara la respuesta tipo 1 (0x20 B) con lo pedido (0x97ecd4); con ceros queda en error."""
    src = (HARNESS / "shim/sonyshim.c").read_text()
    assert 'w[0] == 0x50004 && !getenv("NO50004")' in src and "dataflow_reply(w[0], rq, (unsigned char *)m, 1)" in src


def test_tracefn_se_arma_en_caliente_sin_pisar_trampas_armadas() -> None:
    """§10: «E TRACEFN=…» arma trampas tras el arranque; una dirección aún armada (UDF 0xde00) no se vuelve a guardar como original."""
    src = (HARNESS / "shim/sonyshim.c").read_text()
    assert '!strcmp(ln + 2, "TRACEFN") && trc_base) { trace_fns(trc_base)' in src and "if (*p == 0xde00)" in src


def test_fecha_inicial_900141_orden_3_responde_con_fecha() -> None:
    """§5.18z¹⁰: osal_get_init_date (libObj+0x4f5b94) usa snd_sync_direct a 0x900141 orden 3; el shim respondía ceros sin registrar."""
    src = (HARNESS / "shim/sonyshim.c").read_text()
    assert "qid == 0x900141 && ((unsigned short *)m)[8] == 3" in src
    # mismo orden de Backup_read que libObj+0xb58c60…0xb58dbe: año = 0x90000e + 0x90000f, luego mes, día, hora, min, seg, área, verano
    assert "0x90000e, 0x90000f, 0x900008, 0x900004, 0x900006, 0x900007, 0x900009, 0x90000a, 0x900005" in src


@pytest.mark.skipif(not (os.environ.get("A6000_HARNESS_RUN") and (WORK / "base.cpio.gz").exists() and shutil.which("qemu-system-arm")),
                    reason="prueba lenta (≈ 2 min): A6000_HARNESS_RUN=1 y setup.sh hecho")
def test_arranque_en_qemu_llega_a_la_pila_de_ventanas() -> None:
    """Referencia del avance 23: im.elf vivo, > 55 módulos, sin aborto; libgrm, WindowServer, appFw.so y viewUnified2.so cargados."""
    env = {**os.environ, "SHIMENV": "WAIT=70 CVWAIT=0 POKE=fef348 FULLLOG=1"}
    out = subprocess.run([sys.executable, str(HARNESS / "run.py"), str(WORK), str(HARNESS / "im.sh"), "220"],
                         capture_output=True, text=True, check=True, env=env).stdout
    head = next(line for line in out.splitlines() if line.startswith("alive="))
    assert "alive=" in head and "alive= " not in head, head          # im.elf sigue vivo
    assert int(head.split("modulos=")[1]) >= 55, head
    assert "EXIT=" not in out
    log = (WORK / "guest.log").read_text(errors="replace")
    assert "B  Ii 080_libgrm.so" in log and "Initialize Window System" in log
    assert "E  Ii 083_appFw.so" in log and "dlopen(viewUnified2.so) ->" in log  # hilo de aplicación (SEMSIG) y vistas cargadas


@pytest.mark.skipif(not (os.environ.get("A6000_HARNESS_RUN") and (WORK / "base.cpio.gz").exists() and shutil.which("qemu-system-arm")),
                    reason="prueba lenta (≈ 4 min): A6000_HARNESS_RUN=1 y setup.sh hecho")
def test_ciclo_de_modelos_completo_con_acuse_adf() -> None:
    """§5.18v–w: con la respuesta dataflow de ADF (ACKQ0=58003f) ObjMic termina Og, Mi 0ED cierra y el arranque llega a Ts y Mr."""
    env = {**os.environ, "SHIMENV": "WAIT=200 CVWAIT=0 POKE=fef348 OPENVIEW=view/ROOT OPENVIEWAT=40 STARTEV=11004002:100,11004012,11004013 "
                                     "STARTGAP=f SALVAGE=0 SKIPFN=7fa3d4=0 ACKQ0=58003f FULLLOG=1 "
                                     "KEYQ=7a0020 KEYONACTIVE=0 KEYINIT=7000001:1:177 KEYINITON=06A_viewUnified2"}
    subprocess.run([sys.executable, str(HARNESS / "run.py"), str(WORK), str(HARNESS / "im.sh"), "300"],
                   capture_output=True, text=True, check=True, env=env)
    log = (WORK / "guest.log").read_text(errors="replace")
    assert "PrcGetFuncComp(seq_id=" in log and "Unregisterd msg" not in log
    for tag in ("E  Og 001_ObjMic", "E  Mi 0ED_libObj.so", "E  Ts", "E  Mr 0DC_libObj.so"):
        assert tag in log, tag
    # §5.18w: estado inicial del jack USB (KEYINIT) → el checker de ViewRootPowerSw coincide con la cámara sin PATCHFN
    assert "execCheck timeSettled : 2, jackStatus : 2" in log and "execCheck retVal : 0" in log


def test_gpu_jobs_decodifica_lista_y_tabla() -> None:
    """Formato medido en §5.18y: pares registro/valor, escritura consecutiva (0x0450f026 + 5 palabras) y fin 0x010=0x12345678."""
    import struct as st
    sys.path.insert(0, str(HARNESS))
    from gpu_jobs import decodifica_lista, trabajos
    words = [0x0041F000, 2, 0x0450F026, 7, 1, 2, 3, 4, 0x0202F000, 0x90000004, 0x0010F000, 0x12345678, 0xDEAD]
    lista = decodifica_lista(st.pack(f"<{len(words)}I", *words), 0, len(words))
    assert lista == [(0x41, [2]), (0x450, [7, 1, 2, 3, 4]), (0x202, [0x90000004]), (0x10, [0x12345678])]
    win = bytearray(0xE8 + 2 * 0x8C)
    st.pack_into("<I", win, 0xE8 + 0x8C + 16, 7)
    assert [(k, e[4]) for k, e in trabajos(bytes(win))] == [(1, 7)]


def test_gpu_raster_dibuja_cuadrilatero_a8_trasladado(tmp_path: Path) -> None:
    """§5.18z: textura A8 en mosaico 8×8, cuadrilátero local 8×8 con traslación (10, 20) por la matriz afín del vértice."""
    import numpy as np
    from PIL import Image
    sys.path.insert(0, str(HARNESS))
    from gpu_raster import main
    tex = bytearray(64)
    tex[0] = 0xFF  # píxel (0, 0) de la textura: índice de Morton 0
    (tmp_path / "area_stream_80000000.bin").write_bytes(bytes(tex))
    regs = "0586 0000f000 00080008\n0589 0000f000 10000000\n058f 0000f000 00000008\n0202 0000f000 90000004\n"
    vtx = "".join(f"VTX {k} {x} {y} 1 1 1 1 1 {u} {v} 1 0 10 0 1 20 0\n" for k, (x, y, u, v) in enumerate([(0, 0, 0, 0), (0, 8, 0, 1), (8, 0, 1, 0), (8, 8, 1, 1)]))
    (tmp_path / "gpu.txt").write_text("JOB 1 lista=0x800a4740\n" + regs + vtx)
    main(tmp_path, tmp_path / "out.png")
    img = np.asarray(Image.open(tmp_path / "out.png"))
    assert img[20, 10].tolist() == [255, 255, 255]   # texel (0,0) opaco → blanco en (10, 20)
    assert img[20, 11].tolist() == [0, 0, 0] and img[19, 10].tolist() == [0, 0, 0]
    assert int(img.sum()) == 3 * 255


@pytest.mark.skipif(not (os.environ.get("A6000_HARNESS_RUN") and (WORK / "base.cpio.gz").exists() and shutil.which("qemu-system-arm")),
                    reason="prueba lenta (≈ 5 min): A6000_HARNESS_RUN=1 y setup.sh hecho")
def test_menu_global_se_dibuja() -> None:
    """§5.18z: con la cola de la GPU sin reencolados y /dev/ldec emulado, view/GLOBAL_MENU lanza ≥ 15 listas; el rasterizador saca texto e imágenes."""
    import numpy as np
    from PIL import Image
    gpu = WORK / "gpu.txt"
    gpu.unlink(missing_ok=True)
    env = {**os.environ, "SHIMENV": "WAIT=160 CVWAIT=0 POKE=fef348 OPENVIEW=view/ROOT,view/GLOBAL_MENU OPENVIEWAT=40 OPENVIEWGAP=14 "
                                     "STARTEV=11004002:100,11004012,11004013 STARTGAP=f SALVAGE=0 SKIPFN=7fa3d4=0 ACKQ0=58003f FULLLOG=1 "
                                     "KEYQ=7a0020 KEYONACTIVE=0 KEYINIT=7000001:1:177 KEYINITON=06A_viewUnified2 GPUDUMP=/tmp/gpu.txt "
                                     "DUMPAT=150 DUMPTHR=ninguno AREADUMP=stream@80000000,stream@bc000000"}
    subprocess.run([sys.executable, str(HARNESS / "run.py"), str(WORK), str(HARNESS / "im.sh"), "270"],
                   capture_output=True, text=True, check=True, env=env)
    assert gpu.read_text().count("\n0202 0000f000 90000004") >= 15
    subprocess.run([sys.executable, str(HARNESS / "gpu_raster.py"), str(WORK), str(WORK / "menu.png")], check=True, capture_output=True)
    img = np.asarray(Image.open(WORK / "menu.png"))
    assert (img.max(axis=2) > 128).sum() > 5000  # texto blanco/gris de las seis categorías y el título
    mx = img.max(axis=2)
    assert ((mx > 20) & (mx < 128)).sum() > 60000  # medios tonos de las fotos de fondo: imágenes LZPT de /dev/ldec (§5.18z; sin ellas el fondo es negro)


@pytest.mark.skipif(not (os.environ.get("A6000_HARNESS_RUN") and (WORK / "base.cpio.gz").exists() and shutil.which("qemu-system-arm")),
                    reason="prueba lenta (≈ 5 min): A6000_HARNESS_RUN=1 y setup.sh hecho")
def test_teclas_derecha_e_intro_abren_submenu() -> None:
    """§5.18z (F4): DERECHA (clave 0x1af, índice 0x14) y INTRO (CEC 0xe000000, índice 0x1bc) por la cola del driver 0x7a0020
    abren la vista 0x27 (Ajustes personalizados); el submenú se dibuja con tiras de 16 vértices (pestaña activa)."""
    import numpy as np
    from PIL import Image
    gpu = WORK / "gpu.txt"
    gpu.unlink(missing_ok=True)
    env = {**os.environ, "SHIMENV": SUBMENU_ENV}
    subprocess.run([sys.executable, str(HARNESS / "run.py"), str(WORK), str(HARNESS / "im.sh"), "300"],
                   capture_output=True, text=True, check=True, env=env)
    log = (WORK / "guest.log").read_text(errors="replace")
    assert "E  Vo 00000027" in log  # vista del submenú abierta por la tecla
    assert "\n0202 0000f000 90000010" in gpu.read_text()
    subprocess.run([sys.executable, str(HARNESS / "gpu_raster.py"), str(WORK), str(WORK / "submenu.png")], check=True, capture_output=True)
    img = np.asarray(Image.open(WORK / "submenu.png"))
    assert (img[130:380, 20:620].max(axis=2) > 128).sum() > 8000  # cinco filas de ajustes con su valor
    assert filas_de_texto(WORK / "submenu.png") == 5  # firmware de Sony; el 3.79 añade dos (F5)


@pytest.mark.skipif(not ((PKG379 / "nflasha15-379.bin").exists() and (WORK / "stage/cam/usr").is_dir() and shutil.which("debugfs")),
                    reason="CFW 3.79 construido y setup.sh hecho")
def test_pkg_usr_saca_solo_los_ficheros_del_paquete(tmp_path: Path) -> None:
    """F5: el /usr leído de la imagen TPZL del 3.79 difiere del de Sony justo en los ficheros que el constructor sustituyó."""
    import json
    out = subprocess.run([sys.executable, str(HARNESS / "pkg_usr.py"), str(PKG379 / "nflasha15-379.bin"), str(WORK / "stage/cam/usr"), str(tmp_path)],
                         capture_output=True, text=True, check=True).stdout.split()
    assert out == json.loads((PKG379 / "build-nflasha15.json").read_text())["ficheros"]
    assert (tmp_path / "cam/usr/lib/viewUnified2.so").stat().st_mode & 0o111


@pytest.mark.skipif(not (os.environ.get("A6000_HARNESS_RUN") and (WORK / "base.cpio.gz").exists() and shutil.which("qemu-system-arm")
                         and (PKG379 / "nflasha15-379.bin").exists()),
                    reason="prueba lenta (≈ 5 min): A6000_HARNESS_RUN=1, setup.sh hecho y CFW 3.79 construido")
def test_cfw_379_muestra_silent_y_picture_profile(tmp_path: Path) -> None:
    """F5: con el /usr del nflasha15 del 3.79 la página 4 de «Ajustes personalizados» tiene 6 filas (Sony: 5): «Silent Shooting» y «Picture Profile»."""
    subprocess.run([sys.executable, str(HARNESS / "pkg_usr.py"), str(PKG379 / "nflasha15-379.bin"), str(WORK / "stage/cam/usr"), str(tmp_path / "ovl")],
                   capture_output=True, check=True)
    w = tmp_path / "w"
    w.mkdir()
    for n in ("vmlinuz", "base.cpio.gz", "overlay"):
        (w / n).symlink_to(WORK / n)
    env = {**os.environ, "SHIMENV": SUBMENU_ENV, "OVERLAY2": str(tmp_path / "ovl")}
    subprocess.run([sys.executable, str(HARNESS / "run.py"), str(w), str(HARNESS / "im.sh"), "300"], capture_output=True, text=True, check=True, env=env)
    assert "E  Vo 00000027" in (w / "guest.log").read_text(errors="replace")
    subprocess.run([sys.executable, str(HARNESS / "gpu_raster.py"), str(w), str(w / "submenu.png")], check=True, capture_output=True)
    assert filas_de_texto(w / "submenu.png") == 6


def _live():
    sys.path.insert(0, str(HARNESS))
    import live
    import run
    return live, run


def test_bk_patch_sustituye_y_anade_registros() -> None:
    _, run = _live()
    tbl = struct.pack("<II", 1, 1) + b"\x05\0\0\0" + struct.pack("<II", 2, 5) + b"abcde\0\0\0"
    out = run.bk_patch(tbl, {1: b"\x09", 2: b"xy", 7: b"\x01\x02\x03\x04"})
    assert out == (struct.pack("<II", 1, 1) + b"\x09\0\0\0" + struct.pack("<II", 2, 2) + b"xy\0\0" + struct.pack("<II", 7, 4) + b"\x01\x02\x03\x04")
    assert run.bk_patch(tbl, {}) == tbl


def test_huella_cambia_con_el_shim_el_entorno_y_el_overlay(tmp_path: Path) -> None:
    live, _ = _live()
    (tmp_path / "overlay/cam/usr/lib").mkdir(parents=True)
    so = tmp_path / "overlay/cam/usr/lib/sonyshim.so"
    so.write_bytes(b"uno")
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    base = live.huella(tmp_path, "", "A=1")
    assert live.huella(tmp_path, "", "A=1") == base
    assert live.huella(tmp_path, "", "A=2") != base
    so.write_bytes(b"dos")
    assert live.huella(tmp_path, "", "A=1") != base
    (pkg / "x").write_bytes(b"1")
    assert live.huella(tmp_path, str(pkg), "A=1") != live.huella(tmp_path, "", "A=1")


def test_escribe_atomico_no_deja_temporales(tmp_path: Path) -> None:
    live, _ = _live()
    f = tmp_path / "nvram.json"
    live.escribe_atomico(f, b"{}")
    live.escribe_atomico(f, b'{"a": 1}')
    assert f.read_bytes() == b'{"a": 1}' and [p.name for p in tmp_path.iterdir()] == ["nvram.json"]


def test_msg_hora_lleva_la_hora_local() -> None:
    live, _ = _live()
    import time
    t = 1_800_000_000.7
    assert live.msg_hora(t) == f"T {int(t) + time.localtime(t).tm_gmtoff:x}\n".encode()


def test_emu_config_valida_teclas_y_defaults(tmp_path: Path) -> None:
    """T3: la config se completa con valores por defecto, rechaza botones/teclas repetidas y se guarda de forma atómica."""
    sys.path.insert(0, str(HARNESS))
    import emu_config as E
    botones = E.botones_conocidos()
    assert {"arriba", "abajo", "izquierda", "derecha", "menu", "intro", "disparador"} <= set(botones)  # las claves del literal TECLAS de live.py
    cfg = E.valida_config({"teclas": {"disparador": ["KeyP"], "menu": ["Escape"]}}, botones)
    assert cfg["teclas"]["disparador"] == ["KeyP"] and cfg["teclas"]["arriba"] == ["ArrowUp"] and cfg["sd"]["tamano_gb"] == 4
    assert E.mapa_inverso(cfg["teclas"])["KeyP"] == "disparador"
    for malo in ({"teclas": {"menu": ["KeyM"], "intro": ["KeyM"]}}, {"teclas": {"fn": ["KeyF"]}}, {"teclas": {"menu": ["Ctrl+M"]}},
                 {"firmware": {"origen": "dat"}}, {"firmware": {"origen": "x"}}, {"sd": {"tamano_gb": 0}}, {"sensor": {"fuente": "tv"}}):
        with pytest.raises(ValueError):
            E.valida_config(malo, botones)
    ruta = tmp_path / "c/config.json"
    assert E.carga_config(ruta) == E.valida_config({})  # sin fichero: valores por defecto
    E.guarda_config({"red": {"telnet": True}}, ruta)
    assert E.carga_config(ruta)["red"] == {"telnet": True, "wifi": False, "puerto": 2323}


def test_emu_config_detecta_paquete_a6000() -> None:
    """T3: la cabecera FDAT identifica modelo/versión; un .dat de otra cámara o un fichero cualquiera dan un error claro."""
    sys.path.insert(0, str(HARNESS))
    import emu_config as E
    a6000, a6300 = ROOT / "analysis/darwin-patch/fdat/firmware_packed.dat", ROOT / "firmware/extracted/a6300-fw201/FirmwareData_ILCE6300.dat"
    if not (a6000.exists() and a6300.exists()):
        pytest.skip("faltan los .dat de ejemplo")
    assert E.cabecera_dat(a6000.read_bytes())["version"] == "3.22"
    with pytest.raises(E.DatError, match="otro modelo"):
        E.cabecera_dat(a6300.read_bytes())
    with pytest.raises(E.DatError, match="No es un paquete"):
        E.cabecera_dat(b"no soy un dat" * 100)


def test_sd_emu_numeracion_cuota_y_exif(tmp_path: Path) -> None:
    """T4: DCIM/NNNMSDCF/DSCnnnnn (modo Serie, paso de carpeta a los 9999), clips C%04d, cuota y EXIF mínimo."""
    sys.path.insert(0, str(HARNESS))
    import io

    import sd_emu as S
    from PIL import Image
    assert S.siguiente_foto(tmp_path) == (100, 1) and S.siguiente_clip(tmp_path) == 1
    assert S.ruta_foto(tmp_path, 100, 1) == tmp_path / "DCIM/100MSDCF/DSC00001.JPG"
    d = tmp_path / "DCIM/100MSDCF"
    d.mkdir(parents=True)
    (d / "DSC00007.ARW").write_bytes(b"x" * 10)  # los RAW también cuentan en la serie
    assert S.siguiente_foto(tmp_path) == (100, 8)
    (d / "DSC09999.JPG").write_bytes(b"x")
    assert S.siguiente_foto(tmp_path) == (101, 1)
    c = tmp_path / "PRIVATE/M4ROOT/CLIP"
    c.mkdir(parents=True)
    (c / "C0003.MP4").write_bytes(b"x")
    assert S.siguiente_clip(tmp_path) == 4 and S.ruta_clip(tmp_path, 4) == c / "C0004.MP4"
    assert S.usado(tmp_path) == 12 and S.cabe(tmp_path, 1, 1 << 30) is False and S.cabe(tmp_path, 1, 1000)
    assert S.estado(tmp_path, 4)["libre"] == 4 * (1 << 30) - 12
    buf = io.BytesIO()
    Image.new("RGB", (30, 20), "red").save(buf, "JPEG")
    ex = Image.open(io.BytesIO(S.jpeg_con_exif(buf.getvalue()))).getexif()
    assert (ex[0x010F], ex[0x0110]) == ("SONY", "ILCE-6000") and ex.get_ifd(0x8769)[0x9003] == ex[0x0132]


def test_red_args_telnet_y_wifi():
    import live
    assert live.red_args(None) == ("", [])
    assert live.red_args({"telnet": False, "wifi": False}) == ("", [])
    net, args = live.red_args({"telnet": True, "wifi": True, "puerto": 8623})
    assert net == " NET=telnet,wifi"
    assert "user,id=n0,hostfwd=tcp:127.0.0.1:8623-:23" in args and "virtio-net-device,netdev=n0,mac=fc:c2:de:3a:5d:5c" in args
    net, args = live.red_args({"wifi": True})
    assert net == " NET=wifi" and "hostfwd" not in args[1]


def test_red_puerto_valido():
    import emu_config as E
    with pytest.raises(ValueError, match="puerto"):
        E.valida_config({"red": {"puerto": 80}})
