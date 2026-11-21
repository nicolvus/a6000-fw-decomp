import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "gui" / "harness"))
import live  # noqa: E402


def variables(env: str) -> dict[str, str]:
    return dict(t.split("=", 1) for t in env.split() if "=" in t)


def test_shimenv_por_defecto_trae_la_sd_emulada():
    v = variables(live.construye_shimenv(True, ""))
    for k in ("SDIMG", "SDSECT", "FRONTRM", "BKMULTIPTR", "INSHORT", "NULLMWF"):
        assert k in v, k
    assert v["SDSECT"] == "8388608"  # 4 GB / 512 B
    assert v["SKIPFN"] == "7fa3d4=0"  # §5.37: SendDbCommand ya no se salta; lo cubre SYNCWAIT (espera de la cola de InfraDatabase)
    assert v["SYNCWAIT"] == "37807c:300"
    assert live.construye_shimenv(True, "").count("SKIPFN=") == 1


def test_shimenv_sin_sd_es_el_anterior():
    v = variables(live.construye_shimenv(False, ""))
    assert "SDIMG" not in v and "FRONTRM" not in v and "TABLE0" not in v
    assert v["SKIPFN"] == "7fa3d4=0"


def test_shimextra_manda_sobre_el_conjunto():
    assert variables(live.construye_shimenv(True, "FRONTRM=9"))["FRONTRM"] == "9"


def test_dial_inicial_p_coherente_con_la_vista_y_keyiniton_vacio():
    """E2E-13: el dial arranca en P (3) y la vista de disparo se abre con el mismo número (getRecViewFromDial es la identidad); el dial se informa al activarse InputService (KEYINITON vacío)."""
    env = live.construye_shimenv(True)
    assert "KEYINIT=7000001:1:177,7025:3:27 " in env and "KEYINITON= " in env and "KEYINITAFTER=not_user_operation " in env
    assert live.DIAL_INICIAL == 3 == live.VISTA_REC and "OPENVIEWARG=3 " in env


def test_estados_del_dial_coinciden_con_getexposuremode():
    """E2E-13 (bytes): en viewUnified2 3.21, getExposureMode (+0x18e454) traduce el estado 2 → 0 (auto), 3 → 0x15 (P), 4 → 0x17 (A), 5 → 0x16 (S), 6 → 0x18 (M)."""
    lib = Path(__file__).resolve().parents[1] / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/viewUnified2.so"
    if not lib.exists():
        pytest.skip("firmware 3.21 extraído no disponible")
    b = lib.read_bytes()
    destino = {2: 0x18E7D2, 3: 0x18E852, 4: 0x18E85A, 5: 0x18E856, 6: 0x18E85E}  # destino del beq de cada `cmp r4, #estado`
    modo = {2: 0x00, 3: 0x15, 4: 0x17, 5: 0x16, 6: 0x18}
    for estado, nombre in ((e, n) for n, e in live.POSICIONES_MODO):
        assert b[destino[estado] + 1] == 0x24 and b[destino[estado]] == modo[estado], nombre  # movs r4, #modo


def test_giro_automatico_del_dial_desactivado_por_defecto():
    """§5.24: el giro a P tras el arranque no es fiable (perfil z1); solo es opt-in."""
    assert live.MODO_TRAS_ARRANQUE is None  # solo con LIVE_MODO_TRAS=n en el entorno


def test_giro_del_dial_informa_la_posicion_y_reabre_la_vista_con_el_modo(monkeypatch):
    """E2E-13: /modo → tecla 0x7025 con el estado y vista ROOT→STLREC con ese modo (el icono de modo sigue al dial)."""
    vm = object.__new__(live.Vm)
    vm.cerrojo_dial, vm.sock, enviados = live.threading.Lock(), None, []
    vm.tecla = lambda k, v, i: enviados.append(("K", k, v, i))
    vm.envia = lambda d: enviados.append(d)
    monkeypatch.setattr(live.time, "sleep", lambda _: None)
    monkeypatch.setattr(live.threading, "Thread", lambda target, args, daemon: type("T", (), {"start": lambda self: target(*args)})())
    for nombre, estado in live.POSICIONES_MODO:
        enviados.clear()
        vm.gira(estado)
        assert enviados == [("K", 0x7025, estado, 0x27), b"O view/ROOT 0\n", f"O view/STLREC {estado:x}\n".encode()], nombre
    assert dict(live.POSICIONES_MODO) == {"Auto": 2, "P": 3, "A": 4, "S": 5, "M": 6}


def test_quita_retira_variables_y_direcciones_de_skipfn():
    """§5.35: LIVE_QUITA (opt-in de diagnostico) permite medir sin un atajo concreto sin tocar el codigo."""
    env = live.construye_shimenv(True, quita="NULLMWF,SKIPFN:7fa3d4")
    assert "NULLMWF" not in env and "7fa3d4=0" not in env and "826ed0" not in env
    assert "NULLMWF=1" in live.construye_shimenv(True)


def test_atajos_de_objcntmgr_sustituidos_por_senddbcommand():
    """§5.35: con SendDbCommand (0x826ed0) forzado a OK, onStarting crea de verdad 0x4b8, 0x4e8 y la tabla 0x117c: TABLE0 y los SKIPFN del componente de estado sobran."""
    env = live.construye_shimenv(True, quita="")
    assert "826ed0" not in env and "TABLE0" not in env  # §5.37: SendDbCommand real; SYNCWAIT espera a InfraDatabase (cierra Ii 0c7 ≈ 25 s después de onStarting)
    for a in ("81685a", "829d78", "829da0", "829de8", "829e70", "829eb8", "829f00", "829faa", "829fc0"):
        assert f"{a}=0" not in env
    assert "84569a=0" not in env and "84570e=0" not in env  # el aviso de temperatura ya no cae: el objeto existe


def test_prioridades_rt_y_espera_de_infradatabase_por_defecto():
    """§5.37: sin RTCLAMP (sustituido por RTMAP, activo por defecto en el shim) ni SKIPFN de SendDbCommand; RTMAP/REGARG0 solo se pasan para desactivarlos."""
    env = live.construye_shimenv(True, "")
    assert "RTCLAMP" not in env and "RTMAP" not in env and "REGARG0" not in env and "826ed0" not in env
    assert "SYNCWAIT=37807c:300" in env and "RTMAP=0" in live.construye_shimenv(True, "RTMAP=0")


def test_nflasha4_es_opt_in(monkeypatch, tmp_path):
    """§5.43: sin LIVE_NFLASH4 el arnés no sirve /dev/nflasha4 (dispositivo inerte, como antes); con la ruta añade NFLASH4=<huella> al SHIMENV."""
    assert "NFLASH4" not in variables(live.construye_shimenv(True, ""))
    img = tmp_path / "n4.bin"
    img.write_bytes(b"\xff" * 4096)
    monkeypatch.setenv("LIVE_NFLASH4", str(img))
    v = variables(live.construye_shimenv(True, ""))
    assert len(v["NFLASH4"]) == 12 and v["NFLASH4"] != "1"


def test_shimenv_arranca_por_calma_del_registro():
    """Las esperas fijas del arranque (OPENVIEWAT, STARTGAP, OPENVIEWGAP) terminan al callar el registro de etapas; los plazos siguen como tope."""
    v = variables(live.construye_shimenv(True, ""))
    assert v["CALMA"] == "4" and v["CALMA0"] == "10"
    assert v["OPENVIEWAT"] == "40" and v["STARTGAP"] == "f" and v["OPENVIEWGAP"] == "14"


def test_androidfs_es_opt_in_y_cubre_umount_y_arbol_android():
    """T98: sin ANDROIDFS el umount de libSyncAndroid (fase inact de 155) falla y aborta im.elf; el atajo es opt-in y el arnés por omisión no lo trae."""
    assert "ANDROIDFS" not in variables(live.construye_shimenv())
    h = Path(live.__file__).parent
    assert 'getenv("ANDROIDFS")' in (h / "shim/sonyshim.c").read_text() and "int umount(" in (h / "shim/sonyshim.c").read_text() and "int mount(" in (h / "shim/sonyshim.c").read_text()
    assert "/cam/android/data/backup/bk1.bak" in (h / "im.sh").read_text()
