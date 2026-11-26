"""Comparación independiente 3.97 vs base 3.94: tar y árbol ext2."""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/fwtool"))
from e25_05 import build_packages as B
from e25_27 import tarball, tpzl

W = Path("build/aud397/work")
s = lambda b: hashlib.sha256(b).hexdigest()

base = W / "unpack394"
if not (base / "firmware.tar").exists():
    B.unpack(Path("build/cfw_avcam_limpio/firmware_packed-3.94.dat"), base)
tar394 = (base / "firmware.tar").read_bytes()
tar397 = (W / "unpack397" / "firmware.tar").read_bytes()
m94 = {e.name: e.data for e in tarball.parse(tar394)[0]}
m97 = {e.name: e.data for e in tarball.parse(tar397)[0]}
print("tar394", s(tar394), len(tar394))
print("tar397", s(tar397), len(tar397))
print("miembros", len(m94), len(m97))
print("distintos:", sorted(k for k in set(m94) | set(m97) if m94.get(k) != m97.get(k)))
print("quitados:", sorted(set(m94) - set(m97)), "anadidos:", sorted(set(m97) - set(m94)))

n94 = m94["0700_part_image/dev/nflasha15"]
n97 = m97["0700_part_image/dev/nflasha15"]
print("nflasha15 394", len(n94), s(n94))
print("nflasha15 397", len(n97), s(n97))
img94, img97 = tpzl.TpzlImage.parse(n94), tpzl.TpzlImage.parse(n97)
print("bloques", len(img94.entries), len(img97.entries))
so = [i for i in range(len(img94.entries)) if img94.block(i) == img97.block(i)]
print("bloques identicos", len(so), "distintos", len(img94.entries) - len(so))
print("alineado 512 (397):", all(o % 512 == 0 for o, _ in img97.entries),
      "contiguo:", all(img97.entries[i][0] + img97.entries[i][1] == img97.entries[i + 1][0]
                       for i in range(len(img97.entries) - 1)),
      "violaciones_ldec:", len(tpzl.hardware_violations(img97)),
      "max_sectores:", max(-(-sz // 512) for _, sz in img97.entries))

for tag, img, name in (("x394", img94, "usr394-aud.ext2"), ("x397", img97, "usr397-aud.ext2")):
    p = W / name
    if not p.exists():
        p.write_bytes(img.decompressed(workers=1))
    d = W / tag
    if not d.exists():
        d.mkdir()
        subprocess.run(["debugfs", "-R", f"rdump / {d}", str(p)], capture_output=True, check=True)

def arbol(p):
    return {str(f.relative_to(p)): s(f.read_bytes()) for f in sorted(Path(p).rglob("*")) if f.is_file()}

a94, a97 = arbol(W / "x394"), arbol(W / "x397")
print("ficheros ext2", len(a94), len(a97))
print("ficheros distintos:", sorted(k for k in set(a94) | set(a97) if a94.get(k) != a97.get(k)))
print("libmpr 397 desde debugfs:", a97.get("lib/libmpr.so"))
