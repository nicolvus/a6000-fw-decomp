"""S58-A: ejecuta (Unicorn, código real A6000) una función del pipeline AE con estado aleatorio y registra QUIÉN escribe en rangos dados.
Simplificación: llamadas a funciones fuera de AMBITO devuelven 0 (stub); memoria no mapeada se rellena con patrón (fill) o aleatorio.
uso: from wtrace import W"""
import sys, struct, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
from gpio_calls_diff import MODELS, B
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_HOOK_MEM_READ_UNMAPPED, UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_C1_C0_2, UC_ARM_REG_FPEXC, UC_ARM_REG_CPSR, UC_ARM_REG_R0, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP
SENT = 0x44f00000
def it_ends(model):
    """Direcciones de la primera instrucción tras cada bloque IT (para limpiar ITSTATE: Unicorn 2.1.4 lo deja activo si se saltan instrucciones condicionales; ver s58-conclusions)."""
    import pickle, os
    from tdis import cache
    c = cache(f'itend_{model}.pkl')
    if os.path.exists(c):
        with open(c, 'rb') as fh: return pickle.load(fh)
    from strrefs import sweep
    ins = sweep(MODELS[model]['path'].read_bytes()); out = set()
    for k, i in enumerate(ins):
        if i.mnemonic.startswith('it') and len(i.mnemonic) <= 5 and set(i.mnemonic[2:]) <= set('te'):
            n = len(i.mnemonic) - 1
            if k + n + 1 < len(ins): out.add(ins[k + n + 1].address)
    pickle.dump(out, open(c, 'wb')); return out
class W:
    def __init__(s, model='A6000', ambito=(), fill=0, seed=1, ranges=(), stubfn=None, codehook=True):
        d = MODELS[model]['path'].read_bytes(); s.d = d
        u = s.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(B, (len(d) + 0xfff) & ~0xfff); u.mem_write(B, d)
        u.mem_map(0x44100000, 0x600000); u.mem_map(0x45000000, 0x800000); u.mem_map(SENT & ~0xfff, 0x1000)
        s.rnd = random.Random(seed); s.fill = fill
        def mapfill(uc, access, addr, size, value, _):
            a = addr & ~0xfff
            try: uc.mem_map(a, 0x1000)
            except Exception: return False
            if fill == 'rand': uc.mem_write(a, bytes(s.rnd.randrange(256) for _ in range(0x1000)))
            elif fill: uc.mem_write(a, bytes([fill]) * 0x1000)
            return True
        u.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED, mapfill)
        s.ambito = list(ambito); s.ranges = list(ranges); s.writes = []; s.stubbed = {}; s.stubfn = stubfn or {}
        s.itend = it_ends(model)
        if codehook: u.hook_add(UC_HOOK_CODE, s._code)
        u.hook_add(UC_HOOK_MEM_WRITE, s._wr)
        s.pc = 0
        try:
            u.reg_write(UC_ARM_REG_C1_C0_2, 0x00f00000); u.reg_write(UC_ARM_REG_FPEXC, 0x40000000)   # habilita VFP (el firmware usa vldr/vmul/vdiv en SetRead)
        except Exception as ex: s.vfp_err = str(ex)
    def _code(s, uc, a, sz, _):
        s.pc = a
        if a in s.itend:
            c = uc.reg_read(UC_ARM_REG_CPSR)
            if c & 0x0600fc00: uc.reg_write(UC_ARM_REG_CPSR, c & ~0x0600fc00)
        if a == (SENT & ~1): return
        if a in s.stubfn:
            r = s.stubfn[a](s)
            uc.reg_write(UC_ARM_REG_R0, r & 0xffffffff); uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1); return
        if any(lo <= a < hi for lo, hi in s.ambito): return
        s.stubbed[a] = s.stubbed.get(a, 0) + 1
        uc.reg_write(UC_ARM_REG_R0, 0); uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)
    def _wr(s, uc, t, a, sz, v, _):
        for lo, hi, tag in s.ranges:
            if lo <= a < hi: s.writes.append((s.pc, a, sz, v & ((1 << 8 * sz) - 1), tag))
    def call(s, fn, *args, stack=(), count=3000000):
        u = s.u; sp = 0x44500000 - 0x200
        for i, v in enumerate(stack): u.mem_write(sp + 4 * i, struct.pack('<I', v))
        for i, v in enumerate(args[:4]): u.reg_write(UC_ARM_REG_R0 + i, v)
        u.reg_write(UC_ARM_REG_SP, sp); u.reg_write(UC_ARM_REG_LR, SENT | 1)
        try: u.emu_start(fn | 1, SENT, count=count)
        except Exception as e:
            s.err = str(e)
            raise RuntimeError(f'Emulación incompleta en {fn:#x}: {e}') from e
        if u.reg_read(UC_ARM_REG_PC) != SENT:
            raise RuntimeError(f'Presupuesto de instrucciones agotado en {fn:#x}')
        return u.reg_read(UC_ARM_REG_R0)
    def rd(s, a, n): return bytes(s.u.mem_read(a, n))
    def w32(s, a, v): s.u.mem_write(a, struct.pack('<I', v & 0xffffffff))
    def w16(s, a, v): s.u.mem_write(a, struct.pack('<H', v & 0xffff))
    def r16(s, a): return struct.unpack('<H', s.rd(a, 2))[0]
    def r32(s, a): return struct.unpack('<I', s.rd(a, 4))[0]
