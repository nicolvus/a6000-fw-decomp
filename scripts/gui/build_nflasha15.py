#!/usr/bin/env python3
"""Reconstruye la partición `nflasha15` (/usr, TPZL de un ext2) con ficheros sustituidos (G08/G09). Solo ficheros; no toca la cámara.

Método (el mismo que `scripts/e25_27` para `nflasha3`): descomprimir el TPZL original → sustituir ficheros en el ext2 con
`debugfs` (rm + write; modo, uid y gid conservados y comprobados; las fechas no) → `e2fsck -fn` limpio → recomponer SOLO los bloques de 64 KiB que cambian
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
BLOCK0 = 65536
# Campos contables que debugfs actualiza en el bloque TPZL 0 (superbloque y descriptores de grupo). R55: recomponer el
# bloque 0 de nflasha3 colgó el LZP de Linux (causa sin aislar), así que el bloque 0 se deja byte a byte como el de Sony.
SB, GDT = 1024, 2048
COUNTERS = {SB + i for i in (12, 13, 14, 15, 16, 17, 18, 19, 48, 49, 50, 51)}  # s_free_blocks/inodes_count, s_wtime
FSCK_ONLY_COUNTS = ("Free blocks count wrong", "Free inodes count wrong", "Directories count wrong", "Filesystem still has errors")


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
            # debugfs no acepta el prefijo «0o» de :#o y lo ignora sin error (3.39/3.40 quedaron en 0644)
            f"set_inode_field {dest} mode 0{attrs['mode'] | 0o100000:o}", f"set_inode_field {dest} uid {attrs['uid']}",
            f"set_inode_field {dest} gid {attrs['gid']}",
        ]) + "\n")
        subprocess.run(["debugfs", "-w", "-f", str(script), str(image)], capture_output=True, text=True, check=True)
        script.unlink()
        got = stat_fields(image, dest)  # debugfs -f devuelve 0 aunque falle un comando
        assert all(got[k] == attrs[k] for k in ("mode", "uid", "gid")), (dest, got, attrs)


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
    patched = bytearray(img.read_bytes())
    diff0 = {i for i in range(BLOCK0) if patched[i] != ext2[i]}
    gdt_counters = {GDT + 32 * g + k for g in range(64) for k in (12, 13, 14, 15, 16, 17)}
    assert diff0 <= COUNTERS | gdt_counters, f"el bloque 0 cambia fuera de los contadores: {sorted(diff0 - COUNTERS - gdt_counters)[:8]}"
    patched[:BLOCK0] = ext2[:BLOCK0]  # bloque TPZL 0 idéntico al de Sony; solo quedan contadores libres desfasados
    img.write_bytes(patched)
    fsck2 = subprocess.run(["e2fsck", "-fn", str(img)], capture_output=True, text=True, check=False)
    problems = [ln for ln in fsck2.stdout.splitlines() if "wrong" in ln or "Fix?" in ln or "error" in ln.lower()]
    assert all(any(k in ln for k in FSCK_ONLY_COUNTS) or ln.strip().startswith("Fix?") for ln in problems), problems
    patched = bytes(patched)
    new_blob, info = tpzl.patch_decompressed(image, patched)
    re = tpzl.TpzlImage.parse(new_blob)
    assert re.decompressed() == patched and not tpzl.hardware_violations(re)
    out.write_bytes(new_blob)
    changed = [i for i in info if i["recompressed"]]
    report = {
        "original_bytes": len(blob), "nuevo_bytes": len(new_blob), "limite_particion": PARTITION_LIMIT,
        "bloques_64KiB": len(info), "bloques_recompuestos": len(changed),
        "crc32": f"{zlib.crc32(new_blob):08x}", "ficheros": files,
        "fsck": "limpio antes de restaurar el bloque 0; después solo contadores de libres desfasados",
        "bloque0_igual_que_sony": new_blob[re.entries[0][0]:re.entries[0][0] + image.entries[0][1]] == image.block(0),
    }
    assert len(new_blob) <= PARTITION_LIMIT, "no cabe en la partición"
    out.with_name(out.name + ".json").write_text(json.dumps(report, indent=1))  # with_suffix pisaba nflasha15.json con nflasha15.34x
    shutil.rmtree(work)
    return report


if __name__ == "__main__":
    print(json.dumps(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])), indent=1))
