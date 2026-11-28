#!/usr/bin/env python3
"""Paquete CFW con WBI propio: base Sony 3.21 + `/usr`, `nflasha3` y Darwin del pkg405 + `nflasha5` volcado de la cámara
tras completar la escalera SSBI (WBI1 + vector `_ssboot`, recortado a cabecera+datos+tabla de secciones). NO instala nada.
Antes, comprobar el volcado: scripts/wbi/escalera.py y scripts/wbi/upm_modulo.py (reports/film-pb-1-wbi-escalera-ssbi-20261128.md).
Con `-` en lugar del volcado el paquete va sin `nflasha5` (arranque en frío). `--memclr` apunta `wbi_memclr=` de
`kemco.txt` a una palabra del kernel que vale 1: el frío pone a cero las regiones `wbimem=` como el de fábrica (informe §2b).
Uso: build_package_wbi_propio.py [--memclr] NFLASHA5_VOLCADO|- SALIDA VERSION"""
import hashlib, struct, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_05 import build_packages as B
from e25_27 import build, sums, tarball
FW = ROOT / "firmware/extracted/fw321"
P405 = ROOT / "build/wbi_silent/pkg405/firmware.tar"
N = {k: f"0700_part_image/dev/nflasha{k}" for k in (3, 5, 15)}

SSBOOT_VECTOR = 0x800523BC  # cxd90014_cpu_resume_ssboot (stat 4); verificado con scripts/wbi/escalera.py
KEMCO, APPLI_SUM = "0800_appli/setting/kemco.txt", "0801_appli_sum/appli.sum"
# Palabra del kernel (vmlinux.bin en crudo en 0x80038000) que vale 1 en el fichero y en la RAM de las dos instantáneas.
MEMCLR_UNO = 0x8029FDC8


def kemco_memclr(text: bytes) -> bytes:
    """`wbi_memclr=` (warm.c wbi_memclr: borra wbimem= si la palabra apuntada vale 1) -> MEMCLR_UNO, misma longitud."""
    old, new = b"wbi_memclr=0x800210e8", b"wbi_memclr=0x%08x" % MEMCLR_UNO
    if text.count(old) != 1:
        raise ValueError("kemco.txt sin una única línea wbi_memclr=0x800210e8")
    return text.replace(old, new)


def wbi_member(dump: bytes) -> bytes:
    # Sólo una WBI1 sellada por la propia cámara (pm_finish tras WBI0). Re-firmar un `prof` como WBI1 deja el
    # vector _profile y la reanudación arranca en perfilado: es lo que dejó negro el 4.07.
    firma, n_sec, vector = dump[:4], struct.unpack_from("<I", dump, 4)[0], struct.unpack_from("<I", dump, 12)[0]
    if firma != b"WBI1" or vector != SSBOOT_VECTOR:
        raise ValueError(f"nflasha5 no sellado: firma {firma!r}, vector {vector:#x} (se exige WBI1 y {SSBOOT_VECTOR:#x})")
    data_size = struct.unpack_from("<I", dump, 24)[0]
    end = 262144 + data_size + n_sec * 32  # el WBI de Sony mide exactamente esto (42 293 120 B)
    return dump[:end]

def main(dump_path: Path | None, out: Path, version: str, memclr: bool = False) -> None:
    out.mkdir(parents=True, exist_ok=True)
    base = (FW / "firmware.tar").read_bytes()
    mem = lambda d: {e.name: e.data for e in tarball.parse(d)[0]}
    s, c = mem(base), mem(P405.read_bytes())
    wbi = wbi_member(dump_path.read_bytes()) if dump_path else None
    repl: dict[str, bytes | None] = {k: c[k] for k in c if c[k] != s.get(k) and k in s and k not in (N[5], build.PART_SUM)}
    repl[N[5]] = wbi
    psum = s[build.PART_SUM].decode("ascii")
    for dev in (3, 15) + ((5,) if wbi else ()):
        data = repl.get(N[dev]) or s[N[dev]]
        psum, _ = sums.update(psum, f"dev/nflasha{dev}", data)
        assert sums.verify(psum, f"dev/nflasha{dev}", data)
    if not wbi:  # sin nflasha5: ud_wbi_drop deja la cabecera a cero y Loader3 arranca en frío
        lineas = psum.splitlines(keepends=True)
        psum = "".join(ln for ln in lineas if not ln.rstrip().endswith(",dev/nflasha5,"))
        assert len(psum.splitlines()) == len(lineas) - 1, "falta la línea de dev/nflasha5"
    repl[build.PART_SUM] = psum.encode("ascii")
    if memclr:
        kemco = kemco_memclr(repl.get(KEMCO) or s[KEMCO])
        asum, _ = sums.update((repl.get(APPLI_SUM) or s[APPLI_SUM]).decode("ascii"), "setting/kemco.txt", kemco)
        repl |= {KEMCO: kemco, APPLI_SUM: asum.encode("ascii")}
    tar, _ = tarball.rebuild(base, repl)
    (out / "firmware.tar").write_bytes(tar)
    cfg = out / f"config-{version.replace('.', '')}.yaml"
    cfg.write_text(build._config_text((FW / "config.yaml").read_text(), version), encoding="utf-8")
    pkg = out / f"package-{version}"; pkg.mkdir(exist_ok=True)
    B.pack(cfg, out / "firmware.tar", FW / "updater.img", pkg)
    with tempfile.TemporaryDirectory() as t:
        B.unpack(pkg / "firmware_packed.dat", Path(t))
        got = mem((Path(t) / "firmware.tar").read_bytes())
        assert all(got.get(k) == v for k, v in repl.items())
        if wbi:
            assert got[N[5]][:4] == b"WBI1" and sums.verify(got[build.PART_SUM].decode("ascii"), "dev/nflasha5", wbi)
        if memclr:
            assert sums.verify(got[APPLI_SUM].decode("ascii"), "setting/kemco.txt", got[KEMCO])
    B.package_checksums(pkg)
    print("OK", pkg / "firmware_packed.dat", hashlib.sha256((pkg / "firmware_packed.dat").read_bytes()).hexdigest(),
          "wbi", len(wbi) if wbi else "sin", "memclr", memclr, "reemplazados", sorted(repl))

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--memclr"]
    main(None if args[0] == "-" else Path(args[0]), Path(args[1]), args[2], memclr="--memclr" in sys.argv[1:])
