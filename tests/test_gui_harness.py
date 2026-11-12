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
