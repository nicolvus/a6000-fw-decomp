"""Instantánea de los objetos de estado de los 31 parámetros PP de libObj (this guardado en DATA+0x54 por el parche en vivo). Uso: snap.py SALIDA.json"""
import json, re, struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from camera_telnet import run
H = "192.168.1.18"
P, maps = [x.strip() for x in run(H, ["busybox pidof im.elf", "P=$(busybox pidof im.elf); busybox cat /proc/$P/maps | busybox grep libObj"], timeout=40)]
base = int(re.match(r"([0-9a-f]+)-", maps).group(1), 16)
def rd(blocks):
    cmds = [f"busybox dd if=/proc/{P}/mem of=/android/data/s.bin bs=1 skip={a} count={n} 2>/dev/null; chroot /android /system/bin/hd /data/s.bin; echo ===" for a, n in blocks]
    out = run(H, cmds + ["rm -f /android/data/s.bin"], timeout=120)
    res = []
    for o, (a, n) in zip(out, blocks):
        b = bytearray(n)
        for l in o.splitlines():
            m = re.match(r"^([0-9a-f]{8}): ((?:[0-9a-f]{2} ){1,16})", l)
            if m:
                off, x = int(m.group(1), 16), bytes.fromhex(m.group(2).replace(" ", ""))
                b[off:off + len(x)] = x
        res.append(bytes(b))
    return res
this = struct.unpack("<I", rd([(base + 0xFCB100 + 0x54, 4)])[0])[0]
a560, a12d8 = rd([(this + 0x560, 31 * 4), (this + 0x12d8, 0x180)])
idx = struct.unpack("<31I", a560)
objp = [struct.unpack_from("<I", a12d8, 4 * i + 4)[0] if i * 4 + 8 <= len(a12d8) else 0 for i in range(0x60)]
snap = {"this": this, "idx": list(idx)}
blocks, meta = [], []
for i, k in enumerate(idx):
    op = struct.unpack_from("<I", a12d8, 4 * k + 4)[0]
    meta.append((i, k, op))
wr = rd([(op, 16) for _, _, op in meta])
inner = [struct.unpack("<4I", w) for w in wr]
ins = rd([(v[1], 64) for v in inner])
snap["params"] = [{"i": i, "idx": k, "obj": op, "obj_words": list(inner[j]), "inner_hex": ins[j].hex()} for j, (i, k, op) in enumerate(meta)]
Path(sys.argv[1]).write_text(json.dumps(snap, indent=1))
print("this", hex(this), "params", len(snap["params"]))
