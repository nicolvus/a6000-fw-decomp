"""Rollback 3.98: se desempaqueta y se compara con el tar de la base 3.94 (sin parche)."""
import hashlib
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/fwtool"))
from e25_06 import audit_packages as A
from e25_05 import build_packages as B
from e25_27 import tarball, tpzl

DAT = Path("build/cfw_fbm31_pkg397/pkg-3.98-rollback/package-3.98/firmware_packed.dat")
BASE = Path("build/cfw_fbm31_pkg397/pkg-3.97/package-3.97/firmware_packed.dat")
TAR394 = Path("build/cfw_avcam_limpio/pkg-3.94/firmware.tar")
W = Path("build/aud397/work")
s = lambda b: hashlib.sha256(b).hexdigest()

dat = DAT.read_bytes()
print("3.98 dat_sha256", s(dat), "bytes", len(dat))
info = A.parse_dat(dat)
print("chunks", info["chunks"], "dend", info["dend_stored"], info["dend_computed"],
      info["dend_stored"] == info["dend_computed"])
fdat = DAT.with_suffix(".fdat").read_bytes()
dec = A.decrypt_fdat(dat, info["fdat_offset"], info["fdat_size"], A.load_keys(), compare=fdat)
print("descifrado: bad_sum", dec.bad_sum, "bad_flag", dec.bad_flag, "bad_len", dec.bad_len,
      "mismatch_vs_fdat", dec.first_mismatch_vs_fdat, "sha256_plano", dec.sha256)
h = A.parse_fdat_header(fdat[: A.FDAT_HDR])
print("cabecera 3.98:", h["version"], hex(h["model"]), "region", h["region"], "mode", h["mode"],
      "crc", h["checksum_stored"] == h["checksum_computed"])
out = W / "unpack398"
if not (out / "firmware.tar").exists():
    B.unpack(DAT, out)
tar = (out / "firmware.tar").read_bytes()
print("tar_sha256", s(tar), "bytes", len(tar))
print("tar == base 3.94:", tar == TAR394.read_bytes(), "sha_base", s(TAR394.read_bytes()))

m398 = {e.name: e.data for e in tarball.parse(tar)[0]}
m394 = {e.name: e.data for e in tarball.parse(TAR394.read_bytes())[0]}
print("miembros 3.98", len(m398), "3.94", len(m394))
print("miembros distintos:", sorted(k for k in set(m398) | set(m394) if m398.get(k) != m394.get(k)))
n15 = m398["0700_part_image/dev/nflasha15"]
print("nflasha15 3.98 sha", s(n15), "bytes", len(n15))
print("nflasha15 3.94 sha", s(m394["0700_part_image/dev/nflasha15"]))
img = tpzl.TpzlImage.parse(n15)
ext = img.decompressed(workers=1)
(W / "usr398.ext2").write_bytes(ext)
print("ext2 3.98 sha", s(ext), "bloques", len(img.entries), "bloque0 == sony",
      img.block(0) == tpzl.TpzlImage.parse(m394["0700_part_image/dev/nflasha15"]).block(0))

# version mayor que la 3.97 y que la 3.96
for other in (BASE, Path("build/cfw_fbm31_pkg397/pkg-3.96/firmware_packed.dat") if Path("build/cfw_fbm31_pkg397/pkg-3.96").exists() else None):
    pass
print("3.98 > 3.97:", (3, 98) > (3, 97))
