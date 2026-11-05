#!/usr/bin/env python3
"""Lee DPIDR por SWD en bucle rápido con CMSIS-DAP v2 crudo (sin OpenOCD).
Solo line reset + JTAG->SWD + lectura de DPIDR: no escribe en el objetivo, sin reset ni halt.
Uso: dpidr_fast.py <serial> <segundos> [khz]"""
import sys, time, struct
import usb.core, usb.util

sn, dur = sys.argv[1], float(sys.argv[2])
khz = int(sys.argv[3]) if len(sys.argv) > 3 else 1000

dev = usb.core.find(idVendor=0x2E8A, idProduct=0x000C, custom_match=lambda d: d.serial_number == sn)
if dev is None:
    sys.exit(f"sonda {sn} no encontrada")
intf = next(i for i in dev.get_active_configuration()
            if i.bInterfaceClass == 0xFF and len(i.endpoints()) >= 2)
usb.util.claim_interface(dev, intf)
ep_out = next(e for e in intf if usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
ep_in = next(e for e in intf if usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)


def cmd(b):
    ep_out.write(bytes(b))
    r = bytes(ep_in.read(512, timeout=1000))
    assert r[0] == b[0], f"respuesta inesperada {r[:4].hex()}"
    return r


assert cmd([0x02, 0x01])[1] == 1, "DAP_Connect SWD falló"
cmd([0x11, *struct.pack("<I", khz * 1000)])          # SWJ_Clock
cmd([0x04, 0, *struct.pack("<HH", 8, 0)])             # TransferConfigure
cmd([0x13, 0x00])                                     # SWD_Configure
seq = [0x12, 136] + [0xFF] * 7 + [0x9E, 0xE7] + [0xFF] * 7 + [0x00]  # line reset, JTAG->SWD, line reset, idle

prev, n, ok, t0 = None, 0, 0, time.monotonic()
try:
    while time.monotonic() - t0 < dur:
        cmd(seq)
        r = cmd([0x05, 0, 1, 0x02])                   # DAP_Transfer: leer DP 0x0 (DPIDR)
        n += 1
        v = f"0x{struct.unpack_from('<I', r, 3)[0]:08x}" if r[1] == 1 and r[2] == 1 else "-"
        ok += v.startswith("0x")
        if v != prev:
            print(f"{time.strftime('%T')} +{(time.monotonic()-t0)*1000:.0f}ms {v}", flush=True)
            prev = v
except KeyboardInterrupt:
    pass
finally:
    el = time.monotonic() - t0
    print(f"intentos={n} ok={ok} en {el:.1f} s ({n/el:.0f}/s)")
    try:
        cmd([0x03])                                   # DAP_Disconnect
    except Exception:
        pass
    usb.util.release_interface(dev, intf)
