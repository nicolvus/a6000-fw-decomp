#!/usr/bin/env python3
"""Vigila regiones de la DRAM del BIONZ por AHB-AP (AP0) con CMSIS-DAP v2 crudo.
Solo lectura de memoria: escribe únicamente registros de depuración (DP CTRL/STAT, SELECT, AP CSW/TAR); sin halt ni reset.
Uso: bz_mon.py <serial> <segundos> <addr:nbytes> [...]   Imprime solo las palabras que cambian."""
import sys, time, struct
import usb.core, usb.util

sn, dur = sys.argv[1], float(sys.argv[2])
regions = [(int(a, 16), int(n, 0)) for a, n in (r.split(":") for r in sys.argv[3:])]

dev = usb.core.find(idVendor=0x2E8A, idProduct=0x000C, custom_match=lambda d: d.serial_number == sn)
if dev is None:
    sys.exit(f"sonda {sn} no encontrada")
intf = next(i for i in dev.get_active_configuration() if i.bInterfaceClass == 0xFF and len(i.endpoints()) >= 2)
usb.util.claim_interface(dev, intf)
ep_out, ep_in = sorted(intf.endpoints(), key=lambda e: usb.util.endpoint_direction(e.bEndpointAddress))


def cmd(b):
    ep_out.write(bytes(b))
    r = bytes(ep_in.read(64, timeout=2000))  # respuestas <= 64 B (DAP_Info packet size)
    assert r[0] == b[0], f"respuesta inesperada {r[:4].hex()}"
    return r


def xfer(ops):  # ops: [(req, value|None)] -> lecturas
    b = [0x05, 0, len(ops)]
    for req, v in ops:
        b.append(req)
        if v is not None:
            b += struct.pack("<I", v)
    r = cmd(b)
    if r[1] != len(ops) or r[2] != 1:
        raise IOError(f"transfer falló: hechas={r[1]} ack={r[2]}")
    return list(struct.unpack_from(f"<{(len(r) - 3) // 4}I", r, 3))


DP_W, DP_R, AP_W, AP_R = 0x00, 0x02, 0x01, 0x03
cmd([0x02, 0x01]); cmd([0x11, *struct.pack("<I", 1_000_000)])
cmd([0x04, 0, *struct.pack("<HH", 64, 0)]); cmd([0x13, 0x00])
cmd([0x12, 136] + [0xFF] * 7 + [0x9E, 0xE7] + [0xFF] * 7 + [0x00])
print(f"DPIDR 0x{xfer([(DP_R, None)])[0]:08x}")
xfer([(DP_W, 0x1E), (DP_W | 0x04, 0x50000000), (DP_W | 0x08, 0)])  # ABORT, CTRL/STAT power-up, SELECT AP0 bank 0
csw = xfer([(AP_R, None), (DP_R | 0x0C, None)])[1]                    # lectura AP posted -> RDBUFF
xfer([(AP_W, (csw & ~0x37) | 0x12)])                                  # 32 bits, autoincremento simple


def read(addr, nbytes):
    out = b""
    while nbytes > 0:
        n = min(nbytes, 0x400 - (addr & 0x3FF), 4 * 15)               # paquete CMSIS-DAP de 64 B; TAR se reinicia cada 1 KiB
        xfer([(AP_W | 0x04, addr)])
        r = cmd([0x06, 0, *struct.pack("<H", n // 4), AP_R | 0x0C])   # DAP_TransferBlock
        if r[3] != 1:
            raise IOError(f"block ack={r[3]}")
        out += r[4:4 + n]; addr += n; nbytes -= n
    return out


prev = {}
t0 = time.monotonic(); scans = 0
try:
    while time.monotonic() - t0 < dur:
        for a, n in regions:
            d = read(a, n)
            old = prev.get(a)
            if old is None:
                print(f"{time.strftime('%T')} inicial {a:08x}: {d.hex(' ', 4)}", flush=True)
            elif d != old:
                ch = [f"{a+i:08x}:{old[i:i+4].hex()}->{d[i:i+4].hex()}" for i in range(0, n, 4) if d[i:i+4] != old[i:i+4]]
                print(f"{time.strftime('%T')} +{(time.monotonic()-t0)*1000:.0f}ms " + " ".join(ch), flush=True)
            prev[a] = d
        scans += 1
except KeyboardInterrupt:
    pass
finally:
    el = time.monotonic() - t0
    print(f"barridos={scans} en {el:.1f} s ({scans/el:.0f}/s)", flush=True)
    try: cmd([0x03])
    except Exception: pass
    usb.util.release_interface(dev, intf)
