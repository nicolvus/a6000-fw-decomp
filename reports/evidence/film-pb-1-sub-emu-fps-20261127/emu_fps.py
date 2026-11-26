#!/usr/bin/env python3
"""Arnés Unicorn sobre libmpr.so REAL (fw 3.21) para la ruta de cadencia de FILM-PB-1.

Carga la librería en su VA de ELF (base 0: las R_ARM_RELATIVE quedan ya aplicadas
por construcción), rellena los JUMP_SLOT de .rel.plt —símbolos definidos en la
propia librería -> VA interno; importados -> trampolín atendido por Python— y
engancha la E/S sobre ficheros reales (open/read/lseek/close/fopen/fread/...).

Modos:
  --control            control positivo: ejecuta los stubs REALES open/read de
                       .plt sobre el fichero y comprueba que devuelven sus bytes.
  --entrada 0x6E0AB8   ejecuta mp4Ifo_AVISequence::GetPlayThumbnailInfo con un
                       objeto sintético (this -> [this+0x208] -> +0xC -> acsr).

Salida determinista (sin fechas ni punteros de heap) para poder comparar MD5.
"""
import argparse
import hashlib
import os
import struct
import subprocess
import sys

from unicorn import (Uc, UcError, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE,
                     UC_HOOK_MEM_UNMAPPED, UC_HOOK_MEM_INVALID)
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5,
                               UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8,
                               UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC)

REGS = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3]
STACK, STACK_SZ = 0x6F000000, 0x00100000
HEAP, HEAP_SZ = 0x70000000, 0x00800000
SCRATCH, SCRATCH_SZ = 0x70800000, 0x00200000
TRAMP, TRAMP_SZ = 0x5F000000, 0x00010000
FIN = TRAMP + 0x8000                # dirección de retorno centinela (mapeada)
LOG_STUBS = (0x65062C,)             # stub de log de la librería
LOGF = (0x6F0A54, 0x1DC9E0, 0x1DC98C, 0x68323C, 0x6831F8)
STUB_OPEN, STUB_READ, STUB_CLOSE = 0x11E834, 0x11FEE0, 0x11E5EC
HITOS = ((0x61A8F0, 'isSupportContent (guarda)'),
         (0x6E8430, 'mp4Ifo_If::GetPlayThumbnailInfo'),
         (0x6E0AB8, 'mp4Ifo_AVISequence::GetPlayThumbnailInfo'),
         (0x1D7022, 'AviIf::GetPlayThumbnailInfo (thunk)'),
         (0x21F1F4, 'CS_FlashAcsr::(metodo)'),
         (0x6E0CD6, 'conversion 1..10 -> 0..9'))


def sha256(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


class Lib:
    def __init__(self, path):
        self.path = path
        self.d = open(path, 'rb').read()
        self.sha = hashlib.sha256(self.d).hexdigest()
        self.syms, self.undef = {}, set()
        out = subprocess.run(['readelf', '--dyn-syms', '-W', path],
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            f = line.split()
            if len(f) < 8 or f[3] not in ('FUNC', 'OBJECT'):
                continue
            name = f[7].split('@')[0]
            val = int(f[1], 16)
            (self.undef.add(name) if val == 0 else self.syms.__setitem__(name, val))

    def relplt(self):
        out = subprocess.run(['readelf', '-rW', self.path],
                             capture_output=True, text=True).stdout
        res, on = [], False
        for line in out.splitlines():
            if line.startswith("Relocation section '.rel.plt'"):
                on = True
                continue
            if not on:
                continue
            if not line.strip():
                if res:
                    break
                continue
            if not line.startswith('0'):
                continue
            f = line.split()
            res.append((int(f[0], 16), f[4].split('@')[0]))
        return res


class Emu:
    def __init__(self, libpath, fichero):
        self.lib = Lib(libpath)
        self.fichero = fichero
        self.uc = u = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        u.mem_map(0x0, 0x9BC000)
        u.mem_write(0x0, self.lib.d[:0x9BB1C8])
        u.mem_map(0x9C3000, 0x11D000)
        u.mem_write(0x9C31C8, self.lib.d[0x9BB1C8:0x9BB1C8 + 0x1C640])
        for base, sz in ((STACK, STACK_SZ), (HEAP, HEAP_SZ),
                         (SCRATCH, SCRATCH_SZ), (TRAMP, TRAMP_SZ)):
            u.mem_map(base, sz)
        self.brk = HEAP
        self.files = {}
        self.nextfd = 3
        self.llamadas, self.logs, self.mensajes, self.formateos = [], [], [], []
        self.paradas, self.es_ops = [], []
        self._gots()
        self._hooks()

    # ---- memoria ----
    def r32(self, a):
        return struct.unpack('<I', self.uc.mem_read(a, 4))[0]

    def w32(self, a, v):
        self.uc.mem_write(a, struct.pack('<I', v & 0xFFFFFFFF))

    def rstr(self, a, n=220):
        out = bytearray()
        try:
            for i in range(n):
                b = self.uc.mem_read(a + i, 1)[0]
                if b == 0:
                    break
                out.append(b if 32 <= b < 127 else 0x2E)
        except UcError:
            return '<?>'
        return out.decode()

    def malloc(self, n):
        p = (self.brk + 7) & ~7
        self.brk = p + n + 8
        if self.brk >= HEAP + HEAP_SZ:
            raise RuntimeError('heap agotado')
        return p

    # ---- GOT / PLT ----
    def _gots(self):
        self.tramp2name = {}
        i = 0
        for slot, name in self.lib.relplt():
            if name in self.lib.undef:
                t = TRAMP + 4 * i
                i += 1
                self.tramp2name[t] = name
                self.w32(slot, t | 1)
            else:
                v = self.lib.syms.get(name)
                if v:
                    self.w32(slot, v)

    def _hooks(self):
        u = self.uc
        u.hook_add(UC_HOOK_CODE, self._h_tramp, begin=TRAMP, end=TRAMP + TRAMP_SZ)
        for a in list(LOG_STUBS) + list(LOGF):
            u.hook_add(UC_HOOK_CODE, self._h_log, begin=a, end=a + 4)
        self.hitos = []
        for va, nom in HITOS:
            u.hook_add(UC_HOOK_CODE, self._h_hito, begin=va, end=va + 4)
        u.hook_add(UC_HOOK_CODE, self._h_fin, begin=FIN, end=FIN + 4)
        u.hook_add(UC_HOOK_MEM_UNMAPPED | UC_HOOK_MEM_INVALID, self._h_fault)

    def _h_fin(self, uc, address, size, _):
        uc.emu_stop()

    def _h_hito(self, uc, address, size, _):
        nom = dict(HITOS).get(address)
        if nom and nom not in self.hitos:
            self.hitos.append(nom)

    def _h_fault(self, uc, access, address, size, value, _):
        self.paradas.append('fallo de memoria en 0x%08x (pc=0x%08x)' %
                            (address, uc.reg_read(UC_ARM_REG_PC)))
        uc.emu_stop()
        return False

    def _h_tramp(self, uc, address, size, _):
        name = self.tramp2name.get(address & ~1)
        args = [uc.reg_read(r) for r in REGS]
        fn = getattr(self, 'f_' + (name or '').split('@')[0], None)
        ret = 0
        if fn is not None:
            try:
                ret = fn(args)
            except Exception as e:                      # noqa: BLE001
                self.llamadas.append((name, 'EXC %r' % e))
        elif len(self.llamadas) < 60:
            self.llamadas.append((name, args))
        uc.reg_write(UC_ARM_REG_R0, (ret or 0) & 0xFFFFFFFF)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _h_log(self, uc, address, size, _):
        args = [uc.reg_read(r) for r in REGS]
        txt = [self.rstr(x) if 0x7A3E90 <= x < 0x956750 else x for x in args]
        if len(self.logs) < 40:
            self.logs.append(txt)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    # ---- libc modelada ----
    def f_memcpy(self, a):
        self.uc.mem_write(a[0], bytes(self.uc.mem_read(a[1], a[2])))
        return a[0]

    f_memmove = f_memcpy

    def f_memset(self, a):
        self.uc.mem_write(a[0], bytes([a[1] & 0xFF]) * a[2])
        return a[0]

    def f_strlen(self, a):
        return len(self.rstr(a[0], 4096))

    def f_strcmp(self, a):
        x, y = self.rstr(a[0]), self.rstr(a[1])
        return 0 if x == y else (1 if x > y else -1)

    def f_strncmp(self, a):
        x, y = self.rstr(a[0], a[2]), self.rstr(a[1], a[2])
        return 0 if x == y else (1 if x > y else -1)

    def f_malloc(self, a):
        return self.malloc(a[0])

    f__Znwj = f_malloc
    f__Znaj = f_malloc
    f__ZnwjRKSt9nothrow_t = f_malloc
    f__ZnajRKSt9nothrow_t = f_malloc

    def f_free(self, a):
        return 0

    f__ZdlPv = f_free
    f__ZdaPv = f_free

    def f_aeabi_uidiv(self, a):
        return a[0] // a[1] if a[1] else 0

    def f_aeabi_idiv(self, a):
        return int(a[0] / a[1]) if a[1] else 0

    # ---- E/S real ----
    def f_open(self, a):
        path = self.rstr(a[0])
        acc = int(a[1]) & 3
        try:
            f = open(path, 'rb' if acc == 0 else 'r+b')
        except OSError:
            self.es_ops.append(('open', path, -1))
            return 0xFFFFFFFF
        fd = self.nextfd
        self.nextfd += 1
        self.files[fd] = f
        self.es_ops.append(('open', path, fd))
        return fd

    def f_close(self, a):
        f = self.files.pop(a[0], None)
        self.es_ops.append(('close', a[0], 0 if f else -1))
        if f:
            f.close()
            return 0
        return 0xFFFFFFFF

    def f_lseek(self, a):
        f = self.files.get(a[0])
        if not f:
            return 0xFFFFFFFF
        off = a[1] - (1 << 32) if a[1] & 0x80000000 else a[1]
        r = f.seek(off, a[2] if a[2] <= 2 else 0)
        self.es_ops.append(('lseek', a[0], off, r))
        return r

    def f_read(self, a):
        f = self.files.get(a[0])
        if not f:
            return 0xFFFFFFFF
        data = f.read(a[2])
        self.uc.mem_write(a[1], data)
        self.es_ops.append(('read', a[0], a[2], len(data)))
        return len(data)

    def f_fopen(self, a):
        return self.f_open([a[0], 0, 0])

    def f_fread(self, a):
        f = self.files.get(a[3])
        if not f:
            return 0
        data = f.read(a[1] * a[2])
        self.uc.mem_write(a[0], data)
        self.es_ops.append(('fread', a[3], a[1] * a[2], len(data)))
        return len(data) // (a[1] or 1)

    def f_fseek(self, a):
        return self.f_lseek([a[0], a[1], a[2]])

    def f_ftell(self, a):
        f = self.files.get(a[0])
        return f.tell() if f else 0xFFFFFFFF

    def f_fclose(self, a):
        return self.f_close(a)

    # ---- formato / IPC ----
    def _fmt(self, dst, dstsz, fmt, ap):
        f = self.rstr(fmt)
        vals = []
        if ap:
            try:
                vals = [self.r32(ap + 4 * k) for k in range(4)]
            except UcError:
                pass
        txt = f
        if f.count('%') == 1 and vals:
            v = vals[0]
            txt = f.replace('%s', self.rstr(v) if v > 0x10000 else str(v)) \
                   .replace('%d', str(v))
        elif f.count('%') == 2 and len(vals) >= 2:
            txt = (f.replace('%s', self.rstr(vals[0]), 1).replace('%d', str(vals[1]), 1))
        self.formateos.append(txt)
        if dst and dstsz:
            b = (txt + '\0').encode()[:dstsz - 1]
            self.uc.mem_write(dst, b + b'\0')
        return len(txt)

    def f_vsnprintf(self, a):
        return self._fmt(a[0], a[1], a[2], a[3])

    f_snprintf = f_vsnprintf

    def f_printf(self, a):
        return self._fmt(0, 0, a[0], a[1])

    def f_sprintf(self, a):
        return self._fmt(a[0], 0, a[1], a[2])

    def f_osal_valloc_msg_wait(self, a):
        n = max(a[2], 0x40)
        blk = self.malloc(n + 8)
        self.uc.mem_write(blk, b'\0' * n)
        return blk

    f_osal_alloc_msg = f_osal_valloc_msg_wait

    def _ipc(self, tag, a):
        self.mensajes.append((tag, a[0], a[1], a[2], a[3]))
        return 0

    def f_osal_snd_sync_direct(self, a):
        return self._ipc('snd_sync_direct', a)

    def f_osal_snd_sync_msg(self, a):
        return self._ipc('snd_sync_msg', a)

    def f_osal_snd_msg(self, a):
        return self._ipc('snd_sync_msg', a)

    def f_osal_free_msg(self, a):
        return 0

    # ---- ejecución ----
    def ejecutar(self, entry, regs, stack_args=(), maxinsn=600000):
        u = self.uc
        sp = STACK + STACK_SZ - 0x200
        for v in reversed(list(stack_args)):
            sp -= 4
            self.w32(sp, v)
        u.reg_write(UC_ARM_REG_SP, sp)
        u.reg_write(UC_ARM_REG_LR, FIN)
        mapa = {'r0': UC_ARM_REG_R0, 'r1': UC_ARM_REG_R1, 'r2': UC_ARM_REG_R2,
                'r3': UC_ARM_REG_R3, 'r4': UC_ARM_REG_R4, 'r5': UC_ARM_REG_R5,
                'r6': UC_ARM_REG_R6, 'r7': UC_ARM_REG_R7, 'r8': UC_ARM_REG_R8}
        for k, r in mapa.items():
            u.reg_write(r, regs.get(k, 0))
        self.pc_final = None
        try:
            u.emu_start(entry, FIN, count=maxinsn)
        except UcError as e:
            self.paradas.append('UcError: %s' % e)
        self.pc_final = u.reg_read(UC_ARM_REG_PC)
        return u.reg_read(UC_ARM_REG_R0)


def control(e, path):
    """Control positivo: ejecuta los stubs reales open/read/close de .plt."""
    p = SCRATCH + 0x100
    e.uc.mem_write(p, path.encode() + b'\0')
    e.uc.reg_write(UC_ARM_REG_SP, STACK + STACK_SZ - 0x200)
    e.uc.reg_write(UC_ARM_REG_LR, FIN)
    e.uc.reg_write(UC_ARM_REG_R0, p)
    e.uc.reg_write(UC_ARM_REG_R1, 0)
    e.uc.emu_start(STUB_OPEN, FIN, count=64)
    fd = e.uc.reg_read(UC_ARM_REG_R0)
    buf = SCRATCH + 0x300
    e.uc.reg_write(UC_ARM_REG_R0, fd)
    e.uc.reg_write(UC_ARM_REG_R1, buf)
    e.uc.reg_write(UC_ARM_REG_R2, 8)
    e.uc.reg_write(UC_ARM_REG_LR, FIN)
    e.uc.reg_write(UC_ARM_REG_PC, STUB_READ)
    e.uc.emu_start(STUB_READ, FIN, count=64)
    n = e.uc.reg_read(UC_ARM_REG_R0)
    datos = bytes(e.uc.mem_read(buf, 8)) if n == 8 else b''
    real = open(path, 'rb').read(8)
    print('CONTROL POSITIVO (stubs .plt reales 0x%08x / 0x%08x)' % (STUB_OPEN, STUB_READ))
    print('  fd devuelto        : %d' % fd)
    print('  bytes leidos       : %d' % n)
    print('  datos emulados     : %s' % datos.hex())
    print('  datos reales       : %s' % real.hex())
    print('  COINCIDE           : %s' % (datos == real))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lib', required=True)
    ap.add_argument('--file', required=True)
    ap.add_argument('--control', action='store_true')
    ap.add_argument('--maxinsn', type=int, default=600000)
    ap.add_argument('--entrada', default='0x6E0AB8')
    ap.add_argument('--wrapper', action='store_true',
                    help='entra por 0x6E8430 (mp4Ifo_If) con vtable y lock sintéticos')
    a = ap.parse_args()

    e = Emu(a.lib, a.file)
    print('libmpr.so    %s' % e.lib.sha)
    print('fichero      %s  %s  %d B' % (os.path.basename(a.file),
                                        sha256(a.file), os.path.getsize(a.file)))
    print('trampolines  %d símbolos importados' % len(e.tramp2name))
    if a.control:
        control(e, a.file)
        return

    A, P, Q, D = SCRATCH, SCRATCH + 0x400, SCRATCH + 0x800, SCRATCH + 0x1000
    if a.wrapper:
        V = SCRATCH + 0x1800
        e.w32(A, SCRATCH + 0x200)        # [this] = impl
        e.w32(A + 4, SCRATCH + 0x600)    # [this+4] = objeto de lock
        e.w32(SCRATCH + 0x200, V)        # [impl] = vtable
        e.w32(V + 0x18, 0x6E0AB9)        # vtable+0x18 = mp4Ifo_AVISequence::GetPlayThumbnailInfo
        a.entrada = '0x6E8430'
    e.w32(A + 0x208, P)          # this->[0x208]  (AviIf*)
    e.w32(P + 0xC, Q)            # AviIf->[0x0C]  (acsr)
    e.w32(D + 0x00, 1)           # descriptor de secuencia
    e.w32(D + 0x04, 0)
    e.w32(D + 0x10, 0)
    e.w32(D + 0x14, 0)
    outs = [SCRATCH + 0x2000 + 0x100 * i for i in range(12)]
    r0 = e.ejecutar(int(a.entrada, 0) | 1, {'r0': A, 'r1': D, 'r2': 0, 'r3': 0},
                    stack_args=outs, maxinsn=a.maxinsn)
    print('entrada      0x%08x  (this=0x%08x)' % (int(a.entrada, 0), A))
    print('R0           0x%08x' % (r0 & 0xFFFFFFFF))
    print('paradas      %s' % (e.paradas or 'ninguna (retorno por LR)'))
    print('log libreria %d líneas' % len(e.logs))
    for t in e.logs[:8]:
        print('   %s' % t[1:])
    print('formateos    %s' % (e.formateos[:4] or 'ninguno'))
    print('mensajes IPC %d %s' % (len(e.mensajes), e.mensajes[:3]))
    print('E/S fichero  %d %s' % (len(e.es_ops), e.es_ops[:6]))
    print('externas     %d %s' % (len(e.llamadas), e.llamadas[:8]))
    print('hitos        %s' % (e.hitos or 'ninguno'))
    print('buffer out   +0x100=%d +0x124=%d' %
          (e.r32(D + 0x100), e.r32(D + 0x124)))


if __name__ == '__main__':
    main()
