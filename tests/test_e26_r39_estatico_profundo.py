"""E26-R39 — investigación estática a fondo: emulación de la ruta TPZL→LDEC, NAND física, arranque del actualizador,
persistencia de `MODE`, guard de la sesión USB y fuentes de la clave de `nflasha0`.

Leen binarios, paquetes y volcados locales no versionados; se omiten si faltan.  Nada toca la cámara.
"""

import io
import struct
import sys
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT / "references/fwtool"),
    str(ROOT / "scripts"),
    str(ROOT / "analysis/e26-recovery"),
]

NAND = ROOT / "analysis/camera-dumps/nand-20261020"
UPD = ROOT / "analysis/camera-dumps/updater-20261020-175427"
FW = ROOT / "firmware/extracted/fw321"
FAT_SRC = ROOT / "analysis/session18/codex-g/oss-linux/linux/fs/fat"
REC326 = ROOT / "analysis/darwin-patch/fdat/recuperacion-326/firmware_packed.fdat"


def _need(*paths: Path) -> None:
    for p in paths:
        if not p.exists():
            pytest.skip(f"falta {p.relative_to(ROOT)} (no versionado)")


def _fat(path: Path) -> dict[str, bytes]:
    from fwtool.archive.fat import readFat  # type: ignore[import-not-found]

    return {
        f.path: f.contents.read()
        for f in readFat(io.BytesIO(path.read_bytes()))
        if f.contents
    }


@pytest.fixture(scope="module")
def initrd() -> dict[str, bytes]:
    from fwtool.archive.cramfs import readCramfs  # type: ignore[import-not-found]

    _need(NAND / "dev_nflasha1.bin")
    img = _fat(NAND / "dev_nflasha1.bin")["/boot/initrd.img"]
    return {
        f.path: f.contents.read() for f in readCramfs(io.BytesIO(img)) if f.contents
    }


# 1. Emulación de Loader3 + ARM7 con el LDEC modelado


def test_emulacion_reproduce_el_fallo_del_325_y_valida_el_constructor():
    import r39_tpzl_emu as E

    _need(E.BL, E.SONY, E.INSTALLED_325)
    bl = E.BL.read_bytes()
    code, arm7 = bl[0x22800 : 0x22800 + E.L3_LEN], bl[0x18800 : 0x18800 + 0x3800]
    imgs = E.images()
    sony = E.run(imgs["sony_3.21"], code, arm7, blocks=[0, 1, 240])
    assert not sony["fallos"] and sony["avisos_residuo"] == 0
    bad = E.run(imgs["instalada_3.25"], code, arm7)
    assert len(bad["fallos"]) == 361
    assert bad["avisos_residuo"] == 359 and bad["primer_fallo"] == 0
    b0, b240 = bad["bloques"][0], bad["bloques"][240]
    assert b0["ldec"]["motivo"] == "registro de 65536 B"
    # el residuo llega al trabajo (+8) pero el ARM7 no lo escribe en el LDEC
    assert b240["residuo_trabajo+8"] == 256 and b240["ldec_registros"] == 16
    assert b240["ldec_escrituras"] == [0x0, 0x4, 0xC, 0x10, 0x28, 0x2C, 0x30]
    assert not b240["ldec"]["ok"]
    fixed = E.run(imgs["corregida_R36"], code, arm7)
    assert not fixed["fallos"] and fixed["avisos_residuo"] == 0


# 2. NAND física


def test_particiones_son_ventanas_lineales_de_nflasha_y_el_byte_no_se_puede_reprogramar():
    _need(NAND / "dev_nflasha.bin", NAND / "dev_nflasha2.bin")
    with (NAND / "dev_nflasha.bin").open("rb") as f:
        f.seek(0x640000)
        assert f.read(0xD00000) == (NAND / "dev_nflasha2.bin").read_bytes()
    # programar NAND solo pasa bits de 1 a 0: 0xE5 -> 0x4D necesita subir el bit 3
    assert 0x4D & ~0xE5 == 0x08


def test_nand_ko_es_una_ftl_completa():
    ko = (
        FW
        / "firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/kmod/nand.ko"
    )
    _need(ko)
    data = ko.read_bytes()
    for sym in (
        b"mumin_ebi_get_ltu_tables",
        b"mumin_vbm_get_udb_of_least_erased_counts",
        b"mumin_pbm_s_mark_bad_pblk",
        b"mumin_pbm_s_serach_pab_of_specified_extra_data",
        b"mumin_cmn_get_pagegp_extra_and_ecc_buff",
    ):
        assert sym in data


# 3. Arranque del actualizador


def test_arranque_del_actualizador_no_toca_nflasha3_5_7(initrd):
    scripts = {
        p: v.decode("latin1")
        for p, v in initrd.items()
        if p.endswith(".sh") or p == "/sbin/init"
    }
    assert (
        "UdtrMain.sh" in scripts["/sbin/init"] and "insmod.sh" in scripts["/sbin/init"]
    )
    for text in scripts.values():
        for dev in ("nflasha3", "nflasha5", "nflasha7", "P3_DEV", "P3_MNT_DIR"):
            assert dev not in text or "P3_DEV=" in text or "P3_MNT_DIR=" in text
    assert "mount -t vfat /dev/nflasha2" in scripts["/usr/bin/insmod.sh"]


def test_darwin_325_solo_difiere_en_la_cueva_y_dos_llamadas():
    o = FW / "firmware.tar_unpacked/0640_darwin/darwin_core.bin"
    n = ROOT / "analysis/e25-27/artifacts/darwin_core.integrated.bin"
    _need(o, n)
    a, b = o.read_bytes(), n.read_bytes()
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    assert len(a) == len(b) and len(diff) == 22
    # vectores 70–77 (cueva en 0x4318) y las llamadas de bobina (0x20c78) y motor (0x1fe6c)
    assert all(
        0x118 <= i < 0x134
        or i in range(0x1BC6C, 0x1BC70)
        or i in range(0x1CA78, 0x1CA7C)
        for i in diff
    )


# 4. Persistencia de MODE


def test_kernel_del_actualizador_es_el_3_0_27_de_sony_y_compara_sin_mayusculas():
    _need(NAND / "dev_nflasha1.bin", FAT_SRC / "dir.c")
    z = _fat(NAND / "dev_nflasha1.bin")["/boot/vmlinux.bin"]
    k = zlib.decompressobj(31).decompress(z[z.find(b"\x1f\x8b\x08") :])
    assert (
        b"Linux version 3.0.27_nl-rt106" in k
        and b"posix_attr" in k
        and b"shortname=mixed" in k
    )
    dir_c = (FAT_SRC / "dir.c").read_text()
    inode_c = (FAT_SRC / "inode.c").read_text()
    assert "if (sbi->options.name_check != 's')\n\t\treturn !nls_strnicmp" in dir_c
    assert "opts->name_check = 'n';" in inode_c
    # shortname=mixed -> DISPLAY_WINNT: sin bandera de minúsculas se lista tal cual (MODE)
    assert (
        "case Opt_shortname_mixed:\n\t\t\topts->shortname = VFAT_SFN_DISPLAY_WINNT"
        in inode_c
    )


# 5. Guard de la sesión USB


def test_guard_de_sauu_acepta_el_326_con_los_datos_de_la_camara(initrd):
    _need(REC326, NAND / "dev_nflasha1.bin")
    sauu = initrd["/usr/bin/sauu"]
    # isRegionOK / isModelOK: igualdad estricta con dat3 / dat2
    # ldr r0,[r4,#0x24]; ldr r3,[r4,#0x10]; subs; rsbs; adc (región) y lo mismo con +0x20/+0xc (modelo)
    assert sauu[0xD3A0 - 0x8000 : 0xD3AC - 0x8000].hex() == "606a2369c31a584240eb0300"
    assert sauu[0xD3BE - 0x8000 : 0xD3CA - 0x8000].hex() == "206ae368c21a504240eb0200"
    n1 = _fat(NAND / "dev_nflasha1.bin")
    model, region = (
        struct.unpack("<I", n1["/dat2"])[0],
        struct.unpack("<I", n1["/dat3"])[0],
    )
    h = REC326.read_bytes()[:0x200]
    assert (struct.unpack_from("<II", h, 36)) == (model, region) == (0x41030035, 0)
    new, installed = (h[33], h[32]), (0x03, 0x25)  # dat4 tras el 3.25 (R38)
    assert new > installed
    for blob in (sauu, initrd["/usr/lib/libupdaterufunc.so"]):
        assert b"batt" not in blob.lower()


# 6. Clave de nflasha0


def test_ningun_cargador_toca_la_palabra_de_la_clave():
    _need(UPD / "bootloader.bin", UPD / "bootrom.bin")
    bl, rom = (UPD / "bootloader.bin").read_bytes(), (UPD / "bootrom.bin").read_bytes()

    def refs(d: bytes) -> set[int]:
        return {
            v
            for i in range(0, len(d) - 3, 2)
            if 0xC0000000 <= (v := struct.unpack_from("<I", d, i)[0]) < 0xC0002000
        }

    assert refs(rom) == {0xC0000600, 0xC0001200}
    used = (
        refs(bl[0x600:0x7200]) | refs(bl[0x22800:0x38000]) | refs(bl[0x18800:0x1C000])
    )
    assert not {v for v in used if 0xC0001200 <= v < 0xC0001400}


def test_el_actualizador_ya_lee_paginas_de_arranque_en_sram(initrd):
    ins = initrd["/usr/bin/insmod.sh"].decode()
    assert "ud_get_mem2file.elf /ramdsk/MIS.bin 0xc003d000" in ins
    assert "ud_get_mem2file.elf /ramdsk/DGU.bin 0xc0038000" in ins
