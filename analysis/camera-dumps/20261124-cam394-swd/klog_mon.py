#!/usr/bin/env python3
"""CAM-394: registro continuo del log del kernel (printk) por AHB-AP, SIN detener la CPU (base: analysis/e26-r59/bz_mon.py).
Solo lectura de memoria; escribe únicamente registros de depuración (DP ABORT/CTRL/SELECT, AP CSW/TAR). Reconecta tras cada reinicio.
log_buf_len/log_buf en VA 0x4037c760/+4 y log_end en VA 0x40395290 (kernel 3.21, kallsyms + emit_log_char); PA = VA + 0x40000000.
Uso: klog_mon.py SALIDA.txt EVENTOS.log"""
import struct, sys, time
import usb.core, usb.util

LEN_PA, END_PA, OFF = 0x8037C760, 0x80395290, 0x40000000
salida, eventos = sys.argv[1], sys.argv[2]
dev = usb.core.find(idVendor=0x2E8A, idProduct=0x000C)
intf = next(i for i in dev.get_active_configuration() if i.bInterfaceClass == 0xFF and len(i.endpoints()) >= 2)
usb.util.claim_interface(dev, intf)
ep_out, ep_in = sorted(intf.endpoints(), key=lambda e: usb.util.endpoint_direction(e.bEndpointAddress))
DP_W, DP_R, AP_W, AP_R = 0x00, 0x02, 0x01, 0x03


def ev(m):
    with open(eventos, "a") as f:
        f.write(f"{time.strftime('%T')} {m}\n")


def out(b):
    with open(salida, "ab") as f:
        f.write(b)


def cmd(b):
    ep_out.write(bytes(b))
    r = bytes(ep_in.read(64, timeout=2000))
    assert r[0] == b[0]
    return r


def xfer(ops):
    b = [0x05, 0, len(ops)]
    for req, v in ops:
        b.append(req)
        if v is not None:
            b += struct.pack("<I", v)
    r = cmd(b)
    if r[1] != len(ops) or r[2] != 1:
        raise IOError(f"transfer hechas={r[1]} ack={r[2]}")
    return list(struct.unpack_from(f"<{(len(r) - 3) // 4}I", r, 3))


def conecta():
    cmd([0x02, 0x01]); cmd([0x11, *struct.pack("<I", 1_000_000)])
    cmd([0x04, 0, *struct.pack("<HH", 64, 0)]); cmd([0x13, 0x00])
    cmd([0x12, 136] + [0xFF] * 7 + [0x9E, 0xE7] + [0xFF] * 7 + [0x00])
    xfer([(DP_R, None)])
    xfer([(DP_W, 0x1E), (DP_W | 0x04, 0x50000000), (DP_W | 0x08, 0)])
    csw = xfer([(AP_R, None), (DP_R | 0x0C, None)])[1]
    xfer([(AP_W, (csw & ~0x37) | 0x12)])


def read(addr, nbytes):
    a0 = addr & ~3; n = (addr + nbytes + 3 & ~3) - a0; o = b""; a = a0
    while n > 0:
        k = min(n, 0x400 - (a & 0x3FF), 4 * 15)
        xfer([(AP_W | 0x04, a)])
        r = cmd([0x06, 0, *struct.pack("<H", k // 4), AP_R | 0x0C])
        if r[3] != 1:
            raise IOError(f"block ack={r[3]}")
        o += r[4:4 + k]; a += k; n -= k
    return o[addr - a0:addr - a0 + nbytes]


ok, last = None, -1
ev("klog_mon iniciado")
while True:
    try:
        if not ok:
            conecta()
        ln, buf = struct.unpack("<II", read(LEN_PA, 8)); end = struct.unpack("<I", read(END_PA, 4))[0]
        if not 0 < ln <= 0x100000:
            raise IOError(f"log_buf_len raro {ln:#x}")
        if not ok:
            ev(f"enlace SI (log_buf={buf:#x} len={ln:#x} log_end={end:#x})"); ok = True
        if last < 0 or end < last or end - last > ln:
            last = max(0, end - ln)
            out(f"\n=== {time.strftime('%T')} arranque/reinicio o primer vistazo (log_end={end:#x}) ===\n".encode())
        while last < end:
            i = last % ln; n = min(end - last, ln - i, 1024)
            out(read(buf + OFF + i, n)); last += n
    except Exception as e:
        if ok is not False:
            ev(f"enlace no ({e})")
        ok, last = False, -1
        try: xfer([(DP_W, 0x1E)])
        except Exception: pass
    time.sleep(0.3)
