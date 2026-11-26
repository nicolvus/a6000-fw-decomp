"""G22-OSD-REFRESCO — que la OSD se repinte cuando cambian el modo, la batería y el jack USB.

Sin QEMU. Comprueba tres cosas:

(a) **Repintado del modo**: `Vm.gira()` ya no reabre vistas (el anfitrión no toca la UI); el invitado repinta al ver la tecla del dial
    porque el shim vuelve a activar `view/STLREC` con el modo que da el firmware (`REDIAL` → `openView` sin argumento → OPENVIEWDIAL →
    `CmnViewBigModelUtil::getRecViewFromDial`). `REDIAL=0` lo apaga.
(b) **Estado de cámara**: el shim entrega solo lo que el driver entrega (clave/índice medidos) y el modelo del anfitrión (`B`/`U`) no se
    inventa en el invitado: `CAMGREMU` sigue siendo opt-in y `B` se parsea en decimal.
(c) **Estático** (se salta si no hay firmware 3.21 a mano): qué consume de verdad esos ids —`0x15070050` es clave de `ParamList` (estado
    del dial) y `ACT_ExposureMode::cast` es un downcast por el discriminador de la vtable, no un manejador de evento—; de dónde lee el
    widget de batería (`ACT_IconBattery::WidgetUpdateSync` → `model/POWER` info 0 claves 0x100/0x102/0x104 y `@M084` info 1 clave
    0x101) y de dónde el modo de la OSD (`CmnViewModelWrpCameraExposureMode::getExposureModeActVal` → `@M00B` info 0xf clave 0x12c).

Evidencia medida y offsets: docs/gui/g22-osd-refresco.md.
"""
import inspect
import struct
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "gui" / "harness"))
import live

SHIM = RAIZ / "scripts" / "gui" / "harness" / "shim" / "sonyshim.c"


def _lib(nombre: str) -> Path | None:
    """viewUnified2.so de 3.21 en cualquiera de los dos árboles donde puede estar (nada de descargarlo)."""
    for base in (
        RAIZ / "analysis/gui/g22/harness/stage/cam/usr/lib",
        RAIZ / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib",
    ):
        p = base / nombre
        if p.exists():
            return p
    return None


def _vm_falsa(monkeypatch):
    """Vm sin QEMU: registra lo que se enviaría al invitado."""
    vm = object.__new__(live.Vm)
    vm.cerrojo_dial, vm.sock, vm.enviados = live.threading.Lock(), None, []
    vm.tecla = lambda k, v, i: vm.enviados.append(("K", k, v, i))
    vm.envia = lambda d: vm.enviados.append(d)
    monkeypatch.setattr(live.time, "sleep", lambda _s: None)
    return vm


# --- (a) repintado del modo -------------------------------------------------------------------------------------------------


def test_gira_solo_manda_la_tecla_del_dial(monkeypatch):
    """El anfitrión no reabre ninguna vista: manda la tecla del driver y el invitado decide (G22-OSD-REFRESCO)."""
    vm = _vm_falsa(monkeypatch)
    for nombre, estado in live.POSICIONES_MODO:
        vm.enviados.clear()
        vm.gira(estado)
        assert vm.enviados == [("K", 0x7025, estado, 0x27)], nombre


def test_gira_no_reabre_vistas():
    fuente = inspect.getsource(live.Vm.gira)
    codigo = [ln for ln in fuente.splitlines() if not ln.lstrip().startswith(("#", '"""', "El ", "da ", "el ", "por ", "http"))]
    assert "self.reabre_vista" not in "\n".join(codigo)  # la llamada, no la mención del docstring
    assert "self.envia(" not in "\n".join(codigo)  # el anfitrión no manda líneas «O view/…» al invitado


def test_el_shim_repinta_al_ver_la_tecla_del_dial():
    """El gancho está en el camino de la tecla: K 7025 … → mbx_post_raw + redialhot (misma ruta que la tecla del driver)."""
    src = SHIM.read_text()
    assert 'if (m[0] == 0x7025 && redial_on())' in src
    assert "redialhot" in src and "view/STLREC" in src
    assert 'getenv("REDIAL")' in src  # REDIAL=0 lo apaga
    assert "REDIALROOT" in src  # el «O view/ROOT» previo queda como opción, no por defecto


def test_el_repintado_pide_el_modo_al_firmware():
    """`redialhot` reutiliza `openhot` sin argumento: el modo lo da getRecViewFromDial (OPENVIEWDIAL), no el anfitrión."""
    src = SHIM.read_text()
    i = src.index("static void *redialhot")
    trozo = src[i : src.index("static void *sddump", i)]
    assert "openhot(a)" in trozo
    assert "modo_caliente" not in trozo  # no lo calcula él: lo hace openhot con el nombre sin modo
    j = src.index("static void *openhot")
    assert "arg = modo_caliente(nm)" in src[j : j + 800]
    k = src.index("static int modo_caliente")
    assert "getRecViewFromDial" in src[k : k + 400] or "modo_del_dial" in src[k : k + 400]


def test_el_repintado_espera_al_hilo_del_driver():
    """El estado del dial lo escribe el hilo del driver (libObj+0x806f88): sin la espera se consultaría el modo anterior."""
    src = SHIM.read_text()
    i = src.index("static void *redialhot")
    assert "usleep(" in src[i : src.index("static void *sddump", i)]


# --- (b) estado de cámara: lo que entrega el shim y lo que no inventa --------------------------------------------------------


def test_shim_no_inventa_manejadores_de_los_ids_de_estado():
    """El shim solo entrega el mensaje del driver (clave/índice medidos); no fabrica eventos de modo ni de batería."""
    src = SHIM.read_text()
    assert "CLAVE_JACK_USB" in src and "IDX_JACK_USB" in src
    # el jack viaja como el driver lo da (0x7000001 / índice 0x177) y el dial como 0x7025 / 0x27 en live.TECLAS
    assert live.DIAL_MODO == (0x7025, 0x27)


def test_bateria_del_shim_es_decimal_y_opt_in():
    src = SHIM.read_text()
    assert 'getenv("CAMGREMU")' in src  # la respuesta emulada de CamMgr es opt-in
    i = src.index("if (ln[0] == 'B' && ln[1] == ' ')")
    trozo = src[i : i + 400]
    assert "bv * 10" in trozo  # decimal, no hexv («100» tiene que valer cien)
    assert "if (bv > 100) bv = 100;" in trozo


def test_orden_u_mapea_el_jack_a_0_o_1():
    src = SHIM.read_text()
    i = src.index("entrada_estado(CLAVE_JACK_USB")
    assert "st ? 1u : 0u" in src[i : i + 200]


# --- (c) estático: qué consume cada id y de dónde salen los iconos ----------------------------------------------------------


@pytest.mark.skipif(_lib("viewUnified2.so") is None, reason="viewUnified2.so de 3.21 no disponible")
def test_act_exposuremode_cast_es_un_downcast_no_un_manejador():
    """`ACT_ExposureMode::cast` (viewUnified2+0x2b6e2c) llama a la vtable +0x190 y compara: no mira ningún id de evento.

    0x2b6e2c: b0b5 0546 074c 00af 7c44 50b1 | 0368 (ldr r3,[r0]) | d3f8 9031 (ldr.w r3,[r3,#0x190]) | 9847 (blx r3)
    """
    b = _lib("viewUnified2.so").read_bytes()
    cast = b[0x2B6E2C:0x2B6E2C + 44]
    assert cast[12:18] == bytes.fromhex("0368d3f89031")  # ldr r3,[r0]; ldr.w r3,[r3,#0x190]
    assert cast[18:20] == bytes.fromhex("9847")  # blx r3
    assert struct.pack("<I", 0x15070050) not in cast  # el id del dial no aparece: no es un manejador


@pytest.mark.skipif(_lib("viewUnified2.so") is None, reason="viewUnified2.so de 3.21 no disponible")
def test_los_ids_del_dial_y_del_jack_son_claves_de_paramlist():
    """0x15070050 sale en getRecViewFromDial (clave del estado del dial) y 0x15040010 en los checkers de la vista."""
    b = _lib("viewUnified2.so").read_bytes()
    dial, jack = struct.pack("<I", 0x15070050), struct.pack("<I", 0x15040010)
    assert b[0x19F130:0x19F134] == dial  # dentro de getRecViewFromDial (0x19f004): literal que se pasa a ParamList::get
    assert b[0x135A8C:0x135A90] == dial  # 0x135a7c: devuelve el id (consulta), no lo maneja
    for off in (0x17083C, 0x1708CC, 0x171A7C):  # CheckerUSBAndClockReady (ViewRootPowerSw): jackStatus, §5.18
        assert b[off : off + 4] == jack, hex(off)


@pytest.mark.skipif(_lib("viewUnified2.so") is None, reason="viewUnified2.so de 3.21 no disponible")
def test_de_donde_lee_la_osd_el_modo_y_la_bateria():
    """Modo: @M00B info 0xf clave 0x12c. Batería: model/POWER info 0 claves 0x100/0x102/0x104 y @M084 info 1 clave 0x101."""
    b = _lib("viewUnified2.so").read_bytes()
    assert b"@M00B\x00" in b and b"model/POWER\x00" in b and b"@M084\x00" in b
    g = b[0x1C0EB4:0x1C0EB4 + 80]  # CmnViewModelWrpCameraExposureMode::getExposureModeActVal
    assert bytes.fromhex("0f21") in g  # movs r1,#0xf  (info 15)
    assert bytes.fromhex("4ff49671") in g  # mov.w r1,#0x12c (clave 300: el modo de exposición)
    # ACT_IconBattery::WidgetUpdateSync (0x2758b8) = pop {r7,lr}; b.w 0x275530
    assert b[0x2758BC:0x2758C0] == bytes.fromhex("bde88040")
    upd = b[0x275530:0x275530 + 0x160]
    assert bytes.fromhex("40f20111") in upd  # movw r1,#0x101 (info 1: estado de la batería)
    # Las claves de model/POWER info 0 (0x100 tipo de alimentación, 0x102 y 0x104) van como `mov.w r1,#imm12`, cuyo inmediato no
    # aparece como palabra suelta; quedan documentadas con sus offsets en el informe y se comprueba solo el ancla del nombre.
    assert upd[:4] == bytes.fromhex("2de9f041")  # push.w {r4,r5,r6,r7,r8,lr}: es la función grande de actualización


# --- (d) G22-ESTADO-CAMARA: model/POWER desde el anfitrión y repintado tras B/U ----------------------------------------------


def test_power_se_rellena_con_el_nivel_del_anfitrion_y_solo_si_falta_el_modelo():
    """`power_params` responde a `model/POWER` con las claves que lee +0x275530 y con el nivel de `B`; POWEREMU=0 lo apaga."""
    src = SHIM.read_text()
    i = src.index("static int power_params")
    trozo = src[i : src.index("/* ViewBase::getModelInfo", i)]
    assert 'strcmp(name, "model/POWER")' in trozo  # solo ese modelo
    for clave in ("0x100", "0x102", "0x103", "0x104", "0x105"):  # info 0
        assert f"add(list, {clave}," in trozo, clave
    for clave in ("0x108", "0x10b", "0x10c"):  # info 1: 0x10c = nivel 0..100 (umbrales 20/50/80)
        assert f"add(list, {clave}," in trozo, clave
    assert "add(list, 0x10c, p)" in trozo and "power_pct()" in trozo
    assert 'getenv("POWEREMU")' in trozo  # opt-out medible
    # el nivel sale de la misma variable que la respuesta emulada de CamMgr («B <pct>»)
    j = src.index("static unsigned power_pct")
    assert "cam_bateria" in src[j : j + 160]


def test_power_no_pisa_al_modelo_real():
    """Las tres puertas de getModelInfo solo rellenan cuando la llamada real devuelve 0 (av-cam real manda)."""
    src = SHIM.read_text()
    for puerta in ("_ZN13viewManagerIf12getModelInfoEPKciP9ParamListPKS2_", "_ZN20LayoutableWidgetBase12getModelInfoEPKciP9ParamListPKS2_"):
        i = src.index("int " + puerta + "(")
        trozo = src[i : i + 900]
        assert "if (!x && readable(a) && power_params(" in trozo, puerta
    i = src.index("int _ZN8ViewBase12getModelInfoEPKciP9ParamListPKS2_(")
    assert "if (!r && real && readable(name) && power_params(" in src[i : i + 3000]


def test_repint_al_cambiar_bateria_o_jack_lo_hace_el_invitado():
    """`B`/`U` cambian el estado y el propio invitado reabre la vista (repinta), sin que el anfitrión mande «O view/…»."""
    src = SHIM.read_text()
    i = src.index("if (ln[0] == 'U')")
    assert 'repinta("JACK USB")' in src[i : i + 600]
    j = src.index("if (ln[0] == 'B' && ln[1] == ' ')")
    assert 'repinta("BATERIA")' in src[j : j + 800]
    k = src.index("static void *repinthot")
    trozo = src[k : src.index("static void *live_keys", k)]
    assert "openhot(a)" in trozo and "view/STLREC" in src[k - 900 : k + 900]
    assert 'getenv("REPINT")' in src[k - 900 : k + 400]  # REPINT=0: control (mismo cambio, sin reapertura)
    # el anfitrión (Python) no reabre nada en el camino de /camara/*
    camara = (RAIZ / "scripts" / "gui" / "harness" / "camara_web.py").read_text()
    assert "O view/" not in camara and "view/STLREC" not in camara


@pytest.mark.skipif(_lib("viewUnified2.so") is None, reason="viewUnified2.so de 3.21 no disponible")
def test_las_claves_de_model_power_que_se_rellenan_son_las_que_lee_el_icono():
    """Bytes de +0x275530: 0x100/0x102/0x104 (info 0), 0x105 (filtro 0x107) y 0x108/0x10b/0x10c (info 1, nivel)."""
    b = _lib("viewUnified2.so").read_bytes()
    for off, imm in ((0x2755A0, "4ff48071"), (0x2755BE, "4ff48171"), (0x2755DC, "4ff48271"),  # mov.w r1,#0x100/0x102/0x104
                     (0x2755FA, "40f20511"), (0x27561A, "40f20311"),                            # movw r1,#0x105/0x103
                     (0x2756BC, "4ff48471"), (0x2756D4, "40f20b11"), (0x2756EC, "4ff48671")):  # mov.w/#0x108, movw #0x10b, mov.w #0x10c
        assert b[off : off + 4] == bytes.fromhex(imm), hex(off)
