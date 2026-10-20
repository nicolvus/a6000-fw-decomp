"""S56-A: emulación offline (Unicorn) del formateador P2S real de av-cam.bin A6000 (ARM Thumb).
Alimenta pares (ID u16, dato u8) y captura las escrituras MMIO que quedarían en la RAM de datos P2S.
No ejecuta nada en cámara. uso: p2s_emu.py"""
import sys, struct, hashlib
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP
sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
from gpio_calls_diff import MODELS, B
SENT = 0x44f00000
STUB = {0x43560de0: 'waitflg', 0x43560da8: 'setflg', 0x43560dc4: 'clrflg', 0x43ad8c80: 'int_en', 0x436d594c: 'cb_reg', 0x43ad8d8c: 'dump',
        0x436d5ac8: 'log', 0x43902718: 'log2', 0x439c5320: 'memcpy', 0x436d5848: 'log3', 0x43561110: 'irq', 0x4356112c: 'irq2', 0x436d5f84: 'irq3'}
class P2S:
    def __init__(s, channel=1, cfg=(2, 1, 0, 2, 0)):
        d = MODELS['A6000']['path'].read_bytes(); s.sha = hashlib.sha256(d).hexdigest()
        u = s.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(B, (len(d) + 0xfff) & ~0xfff); u.mem_write(B, d)
        u.mem_map(0x44100000, 0x400000); u.mem_map(0x45000000, 0x100000)       # RAM/pila/objeto
        for m in (0xf3c00000, 0xfc088000): u.mem_map(m, 0x2000)
        s.mmio = []; s.flags = []
        u.hook_add(UC_HOOK_MEM_WRITE, lambda uc, t, a, sz, v, _: s.mmio.append((a, sz, v & ((1 << 8 * sz) - 1))) if a >= 0xf3000000 else None)
        u.hook_add(UC_HOOK_CODE, s._code)
        s.O = 0x45000000; s.P = s.O + 0x298; s.cfg = s.O + 0x348
        s.call(0x43ad8cb2, s.P, 0, 0x10, 8, stack=[channel])
        u.mem_write(s.cfg, bytes(cfg))
    def _code(s, uc, a, sz, _):
        if a in STUB:
            n = STUB[a]
            if n == 'memcpy':
                uc.mem_write(uc.reg_read(UC_ARM_REG_R0), bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1), uc.reg_read(UC_ARM_REG_R2))))
            if n in ('setflg', 'clrflg', 'waitflg'): s.flags.append((n, uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)))
            uc.reg_write(UC_ARM_REG_R0, 0); uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)
    def call(s, fn, *args, stack=()):
        u = s.u; sp = 0x44400000 - 0x100
        for i, v in enumerate(stack): u.mem_write(sp + 4 * i, struct.pack('<I', v))
        for i, v in enumerate(args[:4]): u.reg_write(UC_ARM_REG_R0 + i, v)
        u.reg_write(UC_ARM_REG_SP, sp); u.reg_write(UC_ARM_REG_LR, SENT | 1)
        u.emu_start(fn | 1, SENT, count=200000); return u.reg_read(UC_ARM_REG_R0)
    def rd(s, a, n): return bytes(s.u.mem_read(a, n))
    def u8(s, a): return s.rd(a, 1)[0]
    def frame(s, pairs):
        """Reproduce 0x43ad928a: P2S_Open(cfg) + una escritura (formateador real) + commit real. Devuelve (bytes del buffer, MMIO)."""
        s.call(0x436d5b74, s.P, s.cfg); s.mmio.clear()
        for i, v in pairs: s.call(0x436d5e04, s.P, i, v)
        n = s.u8(s.P + 0x14); buf = s.rd(s.P + 0x28, n); s.call(0x43ad8dca, s.P); return buf, list(s.mmio)
    def records(s, lst):
        t = lst; out = []
        while True:
            p = struct.unpack_from('<I', s.rd(t, 4))[0]
            if not p: return out
            out.append((struct.unpack_from('<H', s.rd(p, 2))[0], s.u8(p + 2))); t += 4
    def tx(s, mode, pairs):
        """Réplica de 0x436d75f8 (consumidor): mode 2 = sincronizado + espera; otro = inmediato. Devuelve transacciones P2S (trama FIFO, nº de disparos)."""
        u = s.u; u.mem_write(s.cfg, bytes([mode]) + bytes(u.mem_read(s.cfg + 1, 4))); s.mmio.clear(); s.flags.clear()
        if mode == 2:
            s.call(0x436d5b74, s.P, s.cfg)
            for i, v in pairs: s.call(0x436d5e04, s.P, i, v)
            s.call(0x43ad8dca, s.P)
        else:
            s.call(0x43ad8d1c, s.P)
            for i, v in pairs: s.call(0x43ad9004, s.P, i, v)
            s.call(0x43ad8d38, s.P); s.call(0x43ad8de4, s.P, s.cfg)
        return s.split()
    def split(s):
        txs, cur, armed = [], {}, False
        for a, sz, v in s.mmio:
            off = a - 0xfc088300
            if 0x40 <= off < 0x240: cur[(off - 0x40) // 4] = v
            if a == 0xfc088808:
                if v == 0: armed = True
                elif armed: txs.append(bytes(cur[i] for i in range(max(cur) + 1)) if cur else b''); cur = {}; armed = False
        if cur: txs.append(bytes(cur[i] for i in range(max(cur) + 1)))  # carga sin pulso de inicio (SyncMode != 2)
        return txs, [(hex(a), v) for a, sz, v in s.mmio if a in (0xfc088800, 0xfc088808, 0xfc088300, 0xfc08830c)]
def frames(b):
    out, i = [], 0
    while i < len(b):
        assert b[i] == 0x81, (i, b.hex())
        n = b[i + 1]; body = b[i + 2:i + 2 + n]; assert body[0] == 0x81
        a = body[1] << 8 | body[2]; out += [(a + k, x) for k, x in enumerate(body[3:])]; i += 2 + n
    return out
if __name__ == '__main__':
    e = P2S()
    for pairs in ([(1, 0x40)], [(0x100, 0x00), (0x101, 0x38)], [(0x100, 0), (0x101, 0x38), (0x102, 0)], [(1, 0x40), (0x65, 0xcc)]):
        buf, mm = e.frame(pairs); print(pairs, '->', buf.hex(' '))
        print('   MMIO:', [f'{a:#x}={v:#x}' for a, sz, v in mm][:14])
