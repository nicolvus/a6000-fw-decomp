"""S57: arnés Unicorn ampliado sobre S56 (p2s_emu/setexp_emu). Ejecuta el código real de av-cam.bin A6000 (ARM Thumb):
SetExposure, Execute (0x436d839c) y hojas de preparación de ID1, con memoria sin mapear rellena de ceros bajo demanda.
Simplificaciones (documentadas): llamadas fuera de AMBITO devuelven 0 (stub); flags OSAL/IRQ stub; sin hardware del sensor.
Estado inicial parametrizable (fill=0x00/0xA5) para detectar dependencia artificial de memoria a cero."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 's56'))
from p2s_emu import P2S, STUB, SENT, frames
from unicorn import UC_HOOK_MEM_READ_UNMAPPED, UC_HOOK_MEM_WRITE_UNMAPPED, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0
import rec_users as R
B = 0x43541000
AMBITO = [(0x436d5000, 0x436daa00), (0x43ad8c00, 0x43ad9700), (0x43560d00, 0x43560e00)]
ID1A, ID1B = 0x4401ca2c, 0x4401c734      # registros sombra de ID1 (tabla idx 1 y 2)
VT_SLOT = 0x26b0                           # GOT: base de vtable de C_Imager (+8), ver ctor 0x436d93d0
class Emu(P2S):
    def __init__(s, fill=0x00, ambito=True):
        super().__init__()
        s.fill = fill; s.calls = []; s.stubbed = []; s.trace_fn = set(); s.hits = []
        def mapfill(uc, access, addr, size, value, _):
            a = addr & ~0xfff; uc.mem_map(a, 0x1000)
            if fill: uc.mem_write(a, bytes([fill]) * 0x1000)
            return True
        s.u.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED, mapfill)
        for a in (0x436d8a74,): STUB[a] = 'ret1'
        for a in (0x436d9f70, 0x436d6738, 0x43ad9a40, 0x43ad99d4, 0x43902718): STUB[a] = 'log'
        s.ambito = ambito
        s.u.hook_add(UC_HOOK_CODE, s._amb)
        got = struct.unpack_from('<I', R.d, 0x4401eee4 + VT_SLOT - B)[0]
        s.vt = got + 8
    def _amb(s, uc, a, sz, _):
        if s.hits is not None and a in s.trace_fn: s.hits.append(a)
        if not s.ambito or a == (SENT & ~1) or a in STUB: return
        if any(lo <= a < hi for lo, hi in AMBITO): return
        s.stubbed.append(a); uc.reg_write(UC_ARM_REG_R0, 0); uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)
    def new_obj(s):
        """Construye el objeto C_Imager con el ctor real (0x436d93d0) y fija la vtable."""
        s.call(0x436d93d0, s.O); s.u.mem_write(s.O, struct.pack('<I', s.vt))
    def reg(s, p): return s.u8(p + 2)
    def id1(s): return s.reg(ID1A), s.reg(ID1B)
    def setf(s, off, v, n=1): s.u.mem_write(s.O + off, v.to_bytes(n, 'little'))
    def getf(s, off, n=1): return int.from_bytes(s.rd(s.O + off, n), 'little')
if __name__ == '__main__':
    e = Emu(); e.new_obj(); print('vt', hex(e.vt), 'ID1', [hex(x) for x in e.id1()], 'stub', [hex(x) for x in e.stubbed[:10]])

def trim(b):
    out, i = b'', 0
    while i < len(b) and b[i] == 0x81 and b[i + 1]:
        out += b[i:i + 2 + b[i + 1]]; i += 2 + b[i + 1]
    return out
def wire(e):
    """Decodifica las transacciones P2S pendientes en listas (dirección, dato) en orden de transmisión."""
    txs, ctl = e.split(); return [frames(trim(t)) for t in txs]
def set_exposure(e, shut, w0=0x1234, w4=0xabc, w6=0x567, b8=0, b14=0, w10=0, w12=0):
    arg = 0x45080000; e.u.mem_write(arg, bytes(0x40))
    e.u.mem_write(arg, struct.pack('<H', w0)); e.u.mem_write(arg + 4, struct.pack('<HH', w4, w6))
    e.u.mem_write(arg + 9, bytes([shut])); e.u.mem_write(arg + 8, bytes([b8])); e.u.mem_write(arg + 0x14, bytes([b14]))
    e.u.mem_write(arg + 0x10, struct.pack('<H', w10)); e.u.mem_write(arg + 0xc, struct.pack('<H', w12))
    return e.call(0x436d6f6c, e.O, arg)
def scenario(drive=0x0b, shut=1, ssb=False, f279=0, f27c=0, f277=0, f278=0, fill=0, prev=None, exposure=True, **kw):
    e = Emu(fill=fill); e.new_obj()
    e.setf(0x170, drive, 4); e.setf(0x174, drive if prev is None else prev, 4)
    e.setf(0x279, f279); e.setf(0x27c, f27c, 4); e.setf(0x277, f277); e.setf(0x278, f278)
    if exposure: set_exposure(e, shut, **kw)
    pre = e.id1()
    if ssb: e.setf(0x268, 1)
    e.mmio.clear(); e.flags.clear()
    e.call(0x436d839c, e.O, 1)
    w = wire(e)
    return dict(pre=pre, post=e.id1(), tx=w, ssbflag=e.getf(0x268), e=e)
def id1_seq(r):
    return [(i, d) for tx in r['tx'] if tx for i, (a, d) in enumerate(tx) if a == 1]
