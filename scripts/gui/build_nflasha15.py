#!/usr/bin/env python3
"""Reconstruye la partición `nflasha15` (/usr, TPZL de un ext2) con ficheros sustituidos (G08/G09). Solo ficheros; no toca la cámara.

Método (el mismo que `scripts/e25_27` para `nflasha3`): descomprimir el TPZL original → sustituir ficheros en el ext2 con
`debugfs` (rm + write, atributos y fechas conservados) → `e2fsck -fn` limpio → recomponer SOLO los bloques de 64 KiB que cambian
(`tpzl.patch_decompressed`: registros originales para las páginas intactas, LZ77 de Sony para las nuevas, alineado a 512 B,
comprobación de las reglas del LDEC) → CRC-32 y tamaño para `part_image.sum`.
Uso: build_nflasha15.py NFLASHA15_ORIGINAL PAQUETE SALIDA   (PAQUETE = carpeta de build_silent_menu_test.py: lib/, share/app/)
"""
import json
import shutil
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from e25_27 import tpzl

PARTITION_LIMIT = 104_857_600  # mount.conf: /dev/nflasha15 /usr raw 104857600


def stat_fields(image: Path, path: str) -> dict:
    text = subprocess.run(["debugfs", "-R", f"stat {path}", str(image)], capture_output=True, text=True, check=True).stdout
    mode = int(text.split("Mode:")[1].split()[0], 8)
    uid = int(text.split("User:")[1].split()[0])
    gid = int(text.split("Group:")[1].split()[0])
    times = {k: text.split(f"{k}:")[1].split()[0] for k in ("ctime", "atime", "mtime")}
    return {"mode": mode, "uid": uid, "gid": gid, **times}


def replace_files(image: Path, package: Path, files: list[str]) -> None:
    for rel in files:
        dest = "/" + rel  # la raíz del ext2 es /usr: lib/… → /lib/…, share/app/… → /share/app/…
        attrs = stat_fields(image, dest)
        script = Path(tempfile.mkstemp(suffix=".dbg")[1])
        script.write_text("\n".join([
            f"rm {dest}", f"write {package / rel} {dest}",
            f"set_inode_field {dest} mode {attrs['mode'] | 0o100000:#o}", f"set_inode_field {dest} uid {attrs['uid']}",
            f"set_inode_field {dest} gid {attrs['gid']}",
        ]) + "\n")
        subprocess.run(["debugfs", "-w", "-f", str(script), str(image)], capture_output=True, text=True, check=True)
        script.unlink()


def main(original: Path, package: Path, out: Path) -> dict:
    manifest = json.loads((package / "MANIFEST.json").read_text())
    files = sorted(manifest["parcheados"])
    blob = original.read_bytes()
    image = tpzl.TpzlImage.parse(blob)
    ext2 = image.decompressed()
    work = Path(tempfile.mkdtemp(prefix="nflasha15-"))
    img = work / "usr.ext2"
    img.write_bytes(ext2)
    replace_files(img, package, files)
    fsck = subprocess.run(["e2fsck", "-fn", str(img)], capture_output=True, text=True, check=False)
    assert fsck.returncode == 0, fsck.stdout[-400:]
    patched = img.read_bytes()
    new_blob, info = tpzl.patch_decompressed(image, patched)
    re = tpzl.TpzlImage.parse(new_blob)
    assert re.decompressed() == patched and not tpzl.hardware_violations(re)
    out.write_bytes(new_blob)
    changed = [i for i in info if i["recompressed"]]
    report = {
        "original_bytes": len(blob), "nuevo_bytes": len(new_blob), "limite_particion": PARTITION_LIMIT,
        "bloques_64KiB": len(info), "bloques_recompuestos": len(changed),
        "crc32": f"{zlib.crc32(new_blob):08x}", "ficheros": files, "fsck": "limpio",
    }
    assert len(new_blob) <= PARTITION_LIMIT, "no cabe en la partición"
    (out.with_suffix(".json")).write_text(json.dumps(report, indent=1))
    shutil.rmtree(work)
    return report


if __name__ == "__main__":
    print(json.dumps(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])), indent=1))
