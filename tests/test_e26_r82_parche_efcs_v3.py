"""E26-R82: parche EFCS v3 en sitio (prefijo de 0x18d6e con tabla), via D (NVRAM), via B (huecos). Solo offline."""
import io
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for d in ("scripts", "scripts/e26_r76", "scripts/e26_r82", "references/pmca"):
    sys.path.insert(0, str(ROOT / d))
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
pytestmark = pytest.mark.skipif(not DARWIN.exists(), reason="falta darwin_core.bin")
for mod in ("capstone", "unicorn", "keystone"):
    pytest.importorskip(mod)

import e26_r76_calibrar_efcs as K
import e26_r76_parche_darwin_tabla as P
import e26_r82_compactacion as C
import e26_r82_huecos as H
import e26_r82_nvram as N

IMG = DARWIN.read_bytes()
PAT = C.parchear(IMG)
TVS, TS, TAB = P.tabla_por_velocidad(IMG)
RAW = C.tabla_bytes(TAB)


def test_solo_cambia_el_prefijo_y_el_tamano_es_el_mismo():
    from e25_24 import patch_darwin as PD
    from e25_27 import build
    assert len(PAT) == len(IMG) == 157_276
    out, diff = build.efcs_tabla_diff(IMG)
    assert out == PAT and diff
    cambiados = {d["address"] for d in diff}
    assert cambiados <= build.efcs_tabla_allowed_addresses() == set(range(0x18D6E, 0x18E10))
    protegidos = {x for _, a, b in PD.PROTECTED for x in range(a, b)}
    parches338 = {addr + i for addr, old, new, _ in PD.PATCHES for i in range(len(old))}
    assert not cambiados & (protegidos | parches338)


def test_nada_externo_salta_al_interior_del_prefijo():
    assert P.referencias_externas(IMG, 0x18D70, 0x18E10) == []
    assert PAT[0x18E10 - 0x4200:] == IMG[0x18E10 - 0x4200:]


def test_prefijo_mide_lo_mismo_y_acaba_en_0x18e10():
    code = C.ensamblar_prefijo()
    assert len(code) == 0x18E10 - 0x18D6E == 162
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    ins = list(md.disasm(code, 0x18D6E))
    assert ins[-1].address + ins[-1].size == 0x18E10 and ins[-1].mnemonic == "mov"      # `mov ip, r3` cae en 0x18e10
    destinos = [int(i.op_str.lstrip("#"), 16) for i in ins if i.mnemonic == "b" and i.op_str.startswith("#0x18e1")]
    assert destinos and set(destinos) == {0x18E10}                                      # las otras ramas saltan a 0x18e10


def test_equivalencia_sin_tabla_es_exacta():
    assert C.equivalencia(IMG, PAT, 3000, con_tabla=False)["con_c"] == 0


def test_equivalencia_con_tabla_aleatoria_frente_a_original_y_modelo():
    assert C.equivalencia(IMG, PAT, 3000)["con_c"] > 0


def test_barrido_de_codigos_tv_con_la_tabla_real():
    assert C.barrido_exhaustivo(IMG, PAT, RAW, 61)["con_c"] > 0


def test_t_de_0x19a12_a_mano_coincide_con_la_emulacion():
    for tv in range(0x1400, 0x1D00, 7):
        assert C.t_modelo(IMG, tv) == P.t_us(IMG, tv)


def test_esperas_a_b_sin_tabla_y_efcs_off_identicas():
    for tv in TVS[::2]:
        assert P.emular_18d6e(IMG, tv, None) == P.emular_18d6e(PAT, tv, bytes(56))
        assert P.emular_18d6e(IMG, tv, None, efcs=False) == P.emular_18d6e(PAT, tv, TAB, efcs=False)


def test_con_tabla_todos_los_tv_igual_que_el_anexo_y_sin_rama_intermedia():
    anexo = P.parchear_anexo(IMG)                       # via C: implementacion independiente de la misma semantica
    n = 0
    for tv in range(0x1500, 0x1D00):                    # 1/4000 .. ~1/22 en pasos de 1/256 EV
        if not 200 <= P.t_us(IMG, tv) <= 45000:
            continue
        r = P.emular_18d6e(PAT, tv, TAB)
        assert r[0] != "intermedia", hex(tv)
        assert r == P.emular_18d6e(anexo, tv, TAB), hex(tv)
        n += 1
    assert n > 1500


def test_tabla_bytes_formato_y_validacion():
    assert RAW == P.tabla_bytes(TAB) and len(RAW) == 56
    assert struct.unpack_from("<hH", RAW, 0) == (TAB[0][0] - 3407, TAB[0][1])
    assert struct.unpack_from("<hH", RAW, 4 * len(TAB)) == (-32768, 0)
    with pytest.raises(ValueError):
        P.tabla_bytes([(1000, 1)] * 15)
    with pytest.raises(ValueError):
        P.tabla_bytes([(1000, 2001)])
    with pytest.raises(ValueError):
        P.tabla_bytes([(40000 + 3407, 10)])


def test_tabla_corrupta_o_sin_casar_no_cambia_nada():
    for tv in TVS[::5]:
        base = P.emular_18d6e(IMG, tv, None)
        for malo in ([(32767 + 3407, 30000)] * 14, [(-30000 + 3407, 500)] * 14):
            raw = b"".join(struct.pack("<hH", t - 3407, c) for t, c in malo)
            assert P.emular_18d6e(PAT, tv, raw) == base


def test_r81_el_hueco_0x13d5a_sigue_bloqueado():
    with pytest.raises(RuntimeError, match="BLOQUEADO"):
        P.parchear_hueco_r76(IMG)


def test_huecos_no_hay_codigo_libre_de_40_bytes():
    cov = H.cubierto_recursivo(IMG)
    assert sum(cov[:H.CODE_END - 0x4200]) / (H.CODE_END - 0x4200) > 0.95
    sin_explicar = [(a, b) for a, b in H.rangos_no_cubiertos(cov, 0x4300, H.CODE_END, 40)
                    if "revisar" in H.clasificar(IMG, a, b)]
    assert sin_explicar == [(0x4304, 0x43FC)]           # tabla de vectores: sus ceros ya los usa el parche 3.30-3.38


# --- via D ------------------------------------------------------------------------------------------------
def test_nvram_tabla_cuantitativa_coincide_con_r76():
    _, filas = N.tabla(IMG)
    f = {round(x["t"], -2): x for x in filas}
    assert f[200]["original"][3] < -3 and abs(f[200]["B86=1256"][3] + 0.04) < 0.02   # 1/4000: negro -> -4 %
    assert abs(f[3100]["B86=1256"][3] + 0.32) < 0.02                                # 1/320: B86 satura (-33 %)
    assert abs(f[3900]["G42=2157"][3] - 0.065) < 0.02                               # 1/250: G42 +7 %
    assert abs(f[6200]["G42=2157"][3] - 0.171) < 0.02                               # 1/160: G42 +17 % (+15 % con la cola de R74)


@pytest.mark.skipif(not N.BASE_DUMP.exists(), reason="falta el volcado NVRAM (no versionado)")
def test_nvram_variantes_se_generan_y_se_verifican(tmp_path):
    from pmca.backup import BackupFile
    res = N.generar(tmp_path)
    assert set(res) == {"b86_1256", "g42_2157"}
    base = BackupFile(io.BytesIO(N.BASE_DUMP.read_bytes()))
    b = BackupFile(io.BytesIO((tmp_path / "var_b86_1256.bin").read_bytes()))
    g = BackupFile(io.BytesIO((tmp_path / "var_g42_2157.bin").read_bytes()))
    assert struct.unpack_from("<h", b.getProperty(0x1850001).data, 0x86)[0] == 1256
    assert struct.unpack_from("<H", g.getProperty(0x1850000).data, 0x42)[0] == 2157
    assert b.getProperty(0x1850000).data == base.getProperty(0x1850000).data
    assert g.getProperty(0x1850001).data == base.getProperty(0x1850001).data


# --- calibrar (R81-CPREV, R80 s3) -------------------------------------------------------------------------
def test_t_efectivo_es_el_de_0x19a12():
    assert [K.t_efectivo(s) for s in ("1/4000", "1/500", "1/320", "1/250")] == [244, 1953, 3102, 3906]


def test_c_aplicado_es_el_de_la_tabla_no_el_punto_fijo():
    tab = [(300, 1111), (2000, 1222)]
    assert K.c_tabla(tab, 244) == 1111 and K.c_tabla(tab, 1953) == 1222 and K.c_tabla(tab, 5000) == 0
    r = {"1/4000": 0.5}
    (x0, p0), = K.puntos(r)
    (x1, p1), = K.puntos(r, tab)
    assert x1 - x0 == 1111 and p1 - p0 == 1111              # T' = T + c de la tabla: x y perdida se desplazan en c


def test_unidad_se_lee_del_volcado_y_la_cola_es_cero():
    assert P.perdida(7670) == 0 and P.perdida(4570) == 0     # R80 s3: cola a 0
    if N.BASE_DUMP.exists():
        assert K.leer_unidad(str(N.BASE_DUMP)) == (3407, 6, -21)
    P.usar_unidad(3000, 10, -30)
    try:
        assert P.separacion(1000) == min(1000 - 3000 + 10, -1) and P.WIN_LO == 3000 - 150 - P.MARG
    finally:
        P.usar_unidad()
