"""Extracción independiente: .dat -> fdat/tar -> dev/nflasha15 -> ext2 -> /lib/libmpr.so."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/fwtool"))
from e25_06 import audit_packages as A   # descifrador propio del repo (CXD90014)
from e25_05 import build_packages as B   # fwtool (tercero) para desempaquetar
from e25_27 import tarball, tpzl

DAT = Path("build/cfw_fbm31_pkg397/pkg-3.97/package-3.97/firmware_packed.dat")
FDAT = DAT.with_suffix(".fdat")
W = Path("build/aud397/work")
W.mkdir(parents=True, exist_ok=True)
s = lambda b: hashlib.sha256(b).hexdigest()

dat = DAT.read_bytes()
print("dat_sha256", s(dat), "bytes", len(dat))

# 1. Contenedor .dat: chunks, DEND.
info = A.parse_dat(dat)
print("chunks", info["chunks"], "trailing", info["trailing"])
print("dend_stored", info["dend_stored"], "dend_computed", info["dend_computed"],
      "ok", info["dend_stored"] == info["dend_computed"])
print("fdat_offset", info["fdat_offset"], "fdat_size", info["fdat_size"])

# 2. Descifrado propio del FDAT y comparación byte a byte con el .fdat del paquete.
keys = A.load_keys()
fdat = FDAT.read_bytes()
dec = A.decrypt_fdat(dat, info["fdat_offset"], info["fdat_size"], keys, compare=fdat)
print("decrypt: blocks", dec.blocks, "bad_sum", dec.bad_sum, "bad_flag", dec.bad_flag,
      "bad_len", dec.bad_len, "pad_not_ff", dec.pad_not_ff,
      "first_mismatch_vs_fdat", dec.first_mismatch_vs_fdat, "plain_size", dec.plain_size,
      "sha256(plano)", dec.sha256)
hdr = A.parse_fdat_header(fdat[: A.FDAT_HDR])
print("fdat_header", json.dumps({k: hdr[k] for k in ("magic", "checksum_stored", "checksum_computed",
      "version", "model", "region", "firmware_offset", "firmware_size", "num_filesystems")}))

# 3. Desempaquetado independiente con fwtool (tercero).
out = W / "unpack397"
if not (out / "firmware.tar").exists():
    B.unpack(DAT, out)
print("fwtool_out", sorted(p.name for p in out.iterdir()))
tar_fw = (out / "firmware.tar").read_bytes()
print("tar_sha256", s(tar_fw), "bytes", len(tar_fw))

# 4. Miembro dev/nflasha15 del tar.
entries, resto = tarball.parse(tar_fw)
members = {e.name: e.data for e in entries}
print("tar_miembros", len(members), "resto_tar", len(resto))
n15 = members["0700_part_image/dev/nflasha15"]
(W / "nflasha15-397.bin").write_bytes(n15)
print("nflasha15_sha256", s(n15), "bytes", len(n15))
print("nflasha15_cabe", len(n15) <= 104857600)

# 5. Imagen TPZL -> ext2 -> /lib/libmpr.so (debugfs, solo lectura).
img = tpzl.TpzlImage.parse(n15)
print("tpzl_bloques", len(img.entries), "bloque_size", img.block_size, "data_offset", img.data_offset)
ext = img.decompressed(workers=1)
(W / "usr397.ext2").write_bytes(ext)
print("ext2_sha256", s(ext), "bytes", len(ext))
