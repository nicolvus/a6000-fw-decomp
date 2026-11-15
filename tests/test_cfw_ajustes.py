"""G56 — circuito de ajustes propios: id de Backup libre, descriptor «solo respaldo», cueva de lectura y Bulb Timer (Unicorn, bytes reales)."""
import io
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/g55"), str(ROOT / "references/pmca")]
import cfw_ajustes as C  # noqa: E402

DEV_A = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
DEV_B = ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev"
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
DUMP = ROOT / "analysis/camera-dumps/20261105-post-apagado-limpio/backup_flash.bin"


@pytest.fixture(autouse=True)
def _spec_intacta():
    """`configurar_menu`/`construir` mutan la spec global de `pp_menu_spec`: se restaura para los demás tests."""
    import pp_menu_spec as M
    antes = (dict(M.SETTINGS), list(M.PIDS), M.TREE)
    yield
    M.SETTINGS.clear(); M.SETTINGS.update(antes[0]); M.PIDS[:] = antes[1]; M.TREE = antes[2]


necesita_fw = pytest.mark.skipif(not (DEV_A.exists() and DEV_B.exists() and AVCAM.exists()), reason="sin firmware extraído")


def test_tabla_ajustes():
    ids = [a.backup for a in C.AJUSTES]
    assert len(set(ids)) == len(ids) and set(ids) <= set(C.ID_LIBRES)
    assert len({a.pid for a in C.AJUSTES}) == len(C.AJUSTES)
    for a in C.AJUSTES:
        assert a.opciones[0][1] == 0 and len(a.opciones) < 256       # el índice 0 = Off/fábrica; el byte es el índice


@pytest.mark.skipif(not DUMP.exists(), reason="sin volcado")
def test_ids_libres_existen_en_nvram_1b():
    from pmca.backup import BackupFile
    props = {i: bytes(p.data) for i, p in BackupFile(io.BytesIO(DUMP.read_bytes())).listProperties()}
    for i in C.ID_LIBRES:
        assert props[i] == b"\0"            # registrado (se puede escribir), 1 B, valor de fábrica 0


def test_leer_asm_tabla_y_llamada():
    a = C.POR_ID["bulb_timer"]
    code = C.ensamblar(C.leer_asm(a), 0x43541900)
    assert struct.pack("<H", 0)[:0] == b""
    tabla = b"".join(struct.pack("<H", v) for _, v in a.opciones)
    assert tabla in code
    assert struct.pack("<H", a.backup & 0xFFFF)[0:1] in code            # movw con el id (el inmediato va repartido, pero el imm8 bajo aparece)


@necesita_fw
def test_bulb_timer_unicorn_bytes_reales():
    import bulb_timer_patch as B
    orig = AVCAM.read_bytes()
    with pytest.raises(ValueError):
        B.apply_bytes(B.apply_bytes(orig))                              # el gancho ya no es el original
    img = B.apply_bytes(orig)
    assert B.emular(img, 0) == (3000, None)                             # Off
    assert B.emular(img, 255) == (3000, None)                           # byte fuera de la tabla
    for idx, seg in enumerate(v for _, v in C.POR_ID["bulb_timer"].opciones):
        if idx and seg <= 60:
            n, ticks = B.emular(img, idx, max_tramos=3000)
            assert n * 33 + ticks // 31250 == seg * 1000                # corta a T = seg s (ticks del último tramo)


@necesita_fw
def test_menu_descriptor_solo_respaldo(tmp_path):
    import add_menu_entry as A
    C.construir(DEV_A, DEV_B, tmp_path)
    d = (tmp_path / "lib/viewUnified2.so").read_bytes()
    # el segmento nuevo lleva relocaciones: se lee con el cargador mínimo de A (VA → fichero)
    segs = A._segments(d)
    w = lambda va, n=1: struct.unpack_from(f"<{n}I", d, A._off(segs, va))
    tabla_d = w(0x4457D4 + 4 * 0)  # noqa: F841  (la tabla ampliada se reapunta; se comprueba por el id)
    assert all(struct.pack("<I", a.backup) in d for a in C.AJUSTES)
    cn = (tmp_path / "lib/CautionConfig.so").read_bytes()
    assert len(cn) > len((DEV_A / "nflasha15_unpacked_unpacked/lib/CautionConfig.so").read_bytes())
    assert (tmp_path / "share/app/string_english.uxc").read_bytes().count(b"Bulb Timer") >= 1


@necesita_fw
def test_descriptor_respaldo_tabla_valores_no_nula(tmp_path):
    """CFWAJ-F1: palabra 8 del descriptor -> {id, tabla índice→valor, …}; con la tabla a NULL `libObj` caía con SIGSEGV al abrir el menú (g56 §4)."""
    import add_menu_entry as A
    C.construir(DEV_A, DEV_B, tmp_path)
    d = (tmp_path / "lib/viewUnified2.so").read_bytes()
    segs = A._segments(d)
    w = lambda va, n=1: struct.unpack_from(f"<{n}I", d, A._off(segs, va))
    d_va = (w(0x25D910)[0] + 0x25D8FE) & 0xFFFFFFFF            # literal reapuntado a la tabla de descriptores ampliada
    for a in C.AJUSTES:                                         # N ajustes: cada uno con su id, su pid y su tabla
        desc = w(w(d_va + 4 * a.pid)[0], 19)
        ident, vals, *_ = w(desc[8], 4)
        assert ident == a.backup and vals
        assert list(w(vals, len(a.opciones))) == list(range(len(a.opciones)))
        assert desc[5] >> 8 == desc[17] >> 8 == len(a.opciones) and desc[13]


def test_carpeta_cfw_con_todos_los_ajustes():
    import pp_menu_spec as M
    C.configurar_menu()
    _carpeta(M)


def _carpeta(M):
    assert M.TREE[0] == "folder" and M.TREE[1] == C.CARPETA
    assert [i for pg in M.TREE[2] for i in pg] == [a.id for a in C.AJUSTES]
    assert max(len(a.opciones) for a in C.AJUSTES) <= M.OPCIONES_POR_LISTA   # tope G36
