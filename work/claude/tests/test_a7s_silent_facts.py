#!/usr/bin/env python3
"""Auto-comprobación por bytes de los hechos decisivos A7S 3.20 / A6000 3.21 (sin dependencias)."""
import hashlib, json, os, struct, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H); B = 0x43541000
a7 = open(f"{W}/input/a7s-av-cam.bin", "rb").read(); a6 = open(f"{W}/input/a6000-av-cam.bin", "rb").read()
u32 = lambda d, va: struct.unpack_from("<I", d, va - B)[0]
hx = lambda d, va, n: d[va - B:va - B + n].hex()
assert hashlib.sha256(a7).hexdigest().startswith("b857d338") and hashlib.sha256(a6).hexdigest().startswith("b60c845c")
# receptor 0x40e3 en ambos: ldrb r2,[r0,#8] ; str.w r2,[r3,#off]
assert u32(a7, 0x43ff79e4) == 0x40e3 and u32(a7, 0x43ff79e8) == 0x437a9cb1 and hx(a7, 0x437a9cb8, 4) == "c3f85022"  # +0x250
assert u32(a6, 0x43fffc60) == 0x40e3 and u32(a6, 0x43fffc64) == 0x438032d5 and hx(a6, 0x438032dc, 4) == "c3f83822"  # +0x238
# conversor: tabla {0,2}
assert struct.unpack_from("<2I", a7, 0x43bc1658 - B) == (0, 2)
# selector A7S con 3 argumentos (cmp r2,#2) y retornos 0x4e/0x4f; A6000 sin ellos
sel7 = a7[0x43826d58 - B:0x43826dae - B]; sel6 = a6[0x437f7f98 - B:0x437f7fe2 - B]
assert bytes.fromhex("022a") in sel7 and bytes.fromhex("4e20") in sel7 and bytes.fromhex("4f20") in sel7
assert bytes.fromhex("4e20") not in sel6 and bytes.fromhex("4f20") not in sel6
# política: A7S compara banco+0x404 con 2; A6000 empieza directamente por +0x41c
assert hx(a7, 0x438649f0, 6) == "d7f80424022a" and hx(a6, 0x4384219e, 6) == "d7f81c140129"
# listas de modos
m7 = struct.unpack_from("<34I", a7, 0x43fee370 - B); m6 = struct.unpack_from("<13I", a6, 0x43fea070 - B)
assert {0x4e, 0x4f, 0x50, 0x51} <= set(m7) and not {0x4e, 0x4f} & set(m6)
# matriz IMX235: columnas Silent propias
j = json.loads(subprocess.check_output([sys.executable, "-I", f"{W}/scripts/imx235_modes.py", f"{W}/input/a7s-av-cam.bin"]))
col = dict(zip(j["modes"], j["mode_to_col"])); assert (col["0x4e"], col["0x4f"], col["0xb"]) == (12, 13, 0)
assert sum(r["cols"][0] != r["cols"][12] for r in j["rows_main"]) == 45 and len(j["rows_main"]) == 69
# IMX235 SetExposure: entrada 2 de la tabla tbb (0x436f4246) == destino del bhi (>4) == 0x436f42fc,
# que carga PC-relativo «ShutMode:%d is not supported.» (0x43c9c8bb) y retorna 1
tb = a7[0x436f4246 - B:0x436f4246 - B + 5]
assert [0x436f4246 + 2 * x for x in tb] == [0x436f424c, 0x436f425c, 0x436f42fc, 0x436f4290, 0x436f42c4]
lit = u32(a7, 0x436f43b4); assert (lit + 0x436f4300 + 4) & 0xffffffff == 0x43c9c8bb
assert a7[0x43c9c8bb - B:0x43c9c8bb - B + 28] == b"ShutMode:%d is not supported"
# IMX210: las 5 entradas tbb son ramas distintas (0..4 aceptadas)
tb6 = a6[0x436d70ca - B:0x436d70ca - B + 5]; assert len({0x436d70ca + 2 * x for x in tb6}) == 5
print("OK: 11 hechos verificados por bytes")
