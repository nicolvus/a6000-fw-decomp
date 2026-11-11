"""Lee por telnet los contadores de trazas de libObj (CFW_TRACE=1): [0] nº getModelInfo · [4] índice · [8..0x47] últimos 16 ids · [0x48] ecos · [0x4c] último valor · [0x50] casos 0x4a."""
import re, struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from camera_telnet import run

H = "192.168.1.18"
P, maps = [x.strip() for x in run(H, ["busybox pidof im.elf", "P=$(busybox pidof im.elf); busybox cat /proc/$P/maps | busybox grep libObj"], timeout=40)]
base = int(re.match(r"([0-9a-f]+)-", maps).group(1), 16)
addr = base + 0xFCB000 + 0x100
o = run(H, [f"busybox dd if=/proc/{P}/mem of=/android/data/c.bin bs=1 skip={addr} count=128 2>/dev/null; chroot /android /system/bin/hd /data/c.bin; rm -f /android/data/c.bin"], timeout=60)[0]
buf = bytearray(128)
for l in o.splitlines():
    m = re.match(r"^([0-9a-f]{8}): ((?:[0-9a-f]{2} ){1,16})", l)
    if m:
        off, b = int(m.group(1), 16), bytes.fromhex(m.group(2).replace(" ", ""))
        buf[off:off + len(b)] = b
w = struct.unpack("<32I", bytes(buf))
print(f"pid {P} base {base:#x}  getModelInfo={w[0]} idx={w[1]} ecos={w[0x48//4]} ultimo_valor={w[0x4c//4]:#x} casos0x4a={w[0x50//4]}")
print("anillo (antiguo→reciente):", [("ECO(valor %#x)" % (v & 0xff) if v >> 8 == 0xEC else hex(v)) for v in (w[2 + (w[1] + i) % 16] for i in range(16))])
