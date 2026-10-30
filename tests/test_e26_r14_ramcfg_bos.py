"""E26-R14 — pruebas offline de RAMCFG (Backup 0xfa0080), BOS y geometría FAT de Loader3.

Solo leen volcados y paquetes existentes; no tocan la cámara. Informe: docs/capture/e26-r14-ramcfg-bos-analysis.md
"""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))

r14 = importlib.import_module("r14-ramcfg-bos-fat")
B = importlib.import_module("r14_backup")
L = importlib.import_module("r13_loader3")
R13 = importlib.import_module("r13-led-provenance")


def _cfg():
    return B.ramcfg(B.BK4.load(r14.D / "20261020-first/backup_flash.bin"))


def test_ramcfg_has_six_entries_and_known_paths():
    cfg = _cfg()
    assert [(e.part, e.path, e.flags) for e in cfg] == [
        (3, "\\sabin\\idt_cam.bin", 0x05000000),
        (3, "\\sabin\\sa_dfdet.bin", 0x01000000),
        (3, "\\av-cam.bin", 0x05000000),
        (2, "\\kemco.txt", 0x01000000),
        (3, "\\initrd.img", 0x01000000),
        (3, "\\vmlinux.bin", 0x81000000),
    ]
    assert (
        len(B.BK4.load(r14.D / "20261020-first/backup_flash.bin").read(0xFA0080))
        == 0x2400
    )


def test_ramcfg_identical_in_all_copies_and_packages():
    g = r14.ramcfg_hashes({**r14.backup_copies(), **r14.package_backups()})
    assert len(g) == 1 and sum(len(v) for v in g.values()) >= 55


def test_mode_selection_matches_c01f304c():
    cfg = _cfg()
    sel = lambda m: [e.n for e in B.selected(cfg, m)]
    assert sel(0x01000000) == [0, 1, 2, 3, 4, 5]  # default / HotOFF
    assert sel(0x04000000) == [0, 2]  # boot mode 0xa/0xb, "Normal load OFF"
    assert sel(0x02000000) == [] and sel(0x01100000) == []  # mode 2, early load


def test_loader3_instructions_behind_the_chain():
    R13.use(R13.LOADER3)
    ins = {a: (m, o) for a, m, o, _ in L.disasm(0xC01F4690, 0xC01F46A8)}
    assert (
        ins[0xC01F469A][0] == "bl" and ins[0xC01F46A2][0] == "ldr"
    )  # 2c2a != 0 -> -302
    assert B.BOS_SIG.to_bytes(4, "little") == b"8246"
    # c01f2ff6: mvn r6,#0x12e (-303) is the 2fe8 return when Backup is not state 1
    assert next(i for i in L.disasm(0xC01F2FF6, 0xC01F2FFA))[1:] == (
        "mvn",
        "r6, #0x12e",
        None,
    )


def test_bos_sector0_and_partitions():
    ok, rows = r14.bos()
    assert ok
    assert [(r.n, r.start, r.size, r.kind) for r in rows[1:4]] == [
        (1, 0x40000, 0x600000, 1),
        (2, 0x640000, 0xD00000, 1),
        (3, 0x1340000, 0x1E00000, 3),
    ]


def test_fat_geometry_and_files_for_all_provenances():
    cfg = _cfg()
    for label, vols in r14.volumes().items():
        for part, v in vols.items():
            assert B.fat_checks(v.v[:0x10000])["loader3_accepts"], (label, part)
        assert all(B.entry_verdict(e, vols).code == 0 for e in cfg), label


def test_empty_or_missing_file_gives_minus_302_synthetic():
    vols = r14.volumes()["oficial_3.21"]
    p2 = vols[2]
    k = _cfg()[3]  # \kemco.txt on nflasha2
    off = p2.root
    d = bytearray(p2.v)
    while d[off : off + 11] != p2._sfn("kemco.txt"):
        off += 32
    d[off + 28 : off + 32] = bytes(4)  # size field -> 0 (in-memory copy only)
    assert B.entry_verdict(k, {2: B.FatVol(bytes(d))}).code == -302
    assert (
        B.entry_verdict(B.CfgEntry(9, 2, 0, 0xFFF, 0, "\\nada.txt"), vols).code == -302
    )


def test_updater_script_overwrites_and_rewrites_backup_bin():
    s = (
        ROOT / "firmware/extracted/fw321/updater.img_unpacked/bin/endupdate.sh"
    ).read_text()
    assert (
        "/setting/Backup.bin" in s
        and "WRITE_BACKUP" in s
        and "$KEEP_BACKUP $BACKUP_OPT" in s
    )
