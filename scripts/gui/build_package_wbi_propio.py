#!/usr/bin/env python3
"""Paquete CFW con WBI propio: base Sony 3.21 + `/usr`, `nflasha3` y Darwin del pkg405 + `nflasha5` volcado de la cámara
tras completar la escalera SSBI (WBI1 + vector `_ssboot`, recortado a cabecera+datos+tabla de secciones). NO instala nada.
Antes, comprobar el volcado: scripts/wbi/escalera.py y scripts/wbi/upm_modulo.py (reports/film-pb-1-wbi-escalera-ssbi-20261128.md).
Uso: build_package_wbi_propio.py NFLASHA5_VOLCADO SALIDA VERSION"""
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


def wbi_member(dump: bytes) -> bytes:
    # Sólo una WBI1 sellada por la propia cámara (pm_finish tras WBI0). Re-firmar un `prof` como WBI1 deja el
    # vector _profile y la reanudación arranca en perfilado: es lo que dejó negro el 4.07.
    firma, n_sec, vector = dump[:4], struct.unpack_from("<I", dump, 4)[0], struct.unpack_from("<I", dump, 12)[0]
    if firma != b"WBI1" or vector != SSBOOT_VECTOR:
        raise ValueError(f"nflasha5 no sellado: firma {firma!r}, vector {vector:#x} (se exige WBI1 y {SSBOOT_VECTOR:#x})")
    data_size = struct.unpack_from("<I", dump, 24)[0]
    end = 262144 + data_size + n_sec * 32  # el WBI de Sony mide exactamente esto (42 293 120 B)
    return dump[:end]

def main(dump_path: Path, out: Path, version: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    base = (FW / "firmware.tar").read_bytes()
    mem = lambda d: {e.name: e.data for e in tarball.parse(d)[0]}
    s, c = mem(base), mem(P405.read_bytes())
    wbi = wbi_member(dump_path.read_bytes())
    repl = {k: c[k] for k in c if c[k] != s.get(k) and k in s and k not in (N[5], build.PART_SUM)}
    repl[N[5]] = wbi
    psum = s[build.PART_SUM].decode("ascii")
    for dev in (3, 5, 15):
        psum, _ = sums.update(psum, f"dev/nflasha{dev}", repl.get(N[dev], s[N[dev]]))
        assert sums.verify(psum, f"dev/nflasha{dev}", repl.get(N[dev], s[N[dev]]))
    repl[build.PART_SUM] = psum.encode("ascii")
    tar, _ = tarball.rebuild(base, repl)
    (out / "firmware.tar").write_bytes(tar)
    cfg = out / f"config-{version.replace('.', '')}.yaml"
    cfg.write_text(build._config_text((FW / "config.yaml").read_text(), version), encoding="utf-8")
    pkg = out / f"package-{version}"; pkg.mkdir(exist_ok=True)
    B.pack(cfg, out / "firmware.tar", FW / "updater.img", pkg)
    with tempfile.TemporaryDirectory() as t:
        B.unpack(pkg / "firmware_packed.dat", Path(t))
        got = mem((Path(t) / "firmware.tar").read_bytes())
        assert got[N[5]] == wbi and got[N[5]][:4] == b"WBI1" and all(got[k] == v for k, v in repl.items())
        assert sums.verify(got[build.PART_SUM].decode("ascii"), "dev/nflasha5", wbi)
    B.package_checksums(pkg)
    print("OK", pkg / "firmware_packed.dat", hashlib.sha256((pkg / "firmware_packed.dat").read_bytes()).hexdigest(), "wbi", len(wbi), "reemplazados", sorted(repl))

if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
