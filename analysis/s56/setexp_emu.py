"""S56-A: emulación offline de C_Imager::SetExposure (0x436d6f6c) de A6000: qué registros sombra (ID) cambia cada campo.
Memoria sin mapear se rellena con ceros (páginas bajo demanda); solo lectura/escritura del blob en RAM de Unicorn."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from p2s_emu import P2S, STUB
from unicorn import UC_HOOK_MEM_READ_UNMAPPED, UC_HOOK_MEM_WRITE_UNMAPPED
import rec_users as R
class SetExp(P2S):
    def __init__(s):
        super().__init__()
        def fill(uc, access, addr, size, value, _):
            uc.mem_map(addr & ~0xfff, 0x1000); return True
        s.u.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED, fill)
        for a in (0x436d8a74, 0x436d9f70, 0x436d6738, 0x43ad9a40, 0x43ad99d4): STUB[a] = 'ret1' if a == 0x436d8a74 else 'log'
    def snap(s): return {(R.recs[p], p): s.u8(p + 2) for p in R.tab}
    def run(s, drive, shut, w0, w4, w6, b8=0, b14=0, w10=0, w12=0):
        s.u.mem_write(s.O + 0x170, struct.pack('<I', drive))
        arg = 0x45080000; s.u.mem_write(arg, bytes(0x40))
        s.u.mem_write(arg, struct.pack('<H', w0)); s.u.mem_write(arg + 4, struct.pack('<HH', w4, w6))
        s.u.mem_write(arg + 9, bytes([shut])); s.u.mem_write(arg + 8, bytes([b8])); s.u.mem_write(arg + 0x14, bytes([b14]))
        s.u.mem_write(arg + 0x10, struct.pack('<H', w10)); s.u.mem_write(arg + 0xc, struct.pack('<H', w12))
        before = s.snap(); rc = s.call(0x436d6f6c, s.O, arg); after = s.snap()
        return rc, {f'{i[0]:#x}' + ('@%x' % i[1] if i[0] == 1 else ''): (before[i], after[i]) for i in after if before[i] != after[i]}
if __name__ == '__main__':
    e = SetExp()
    for shut in range(5):
        e = SetExp(); print('shut', shut, e.run(0x0b, shut, 0x1234, 0x0abc, 0x0567))
