import sys, struct, re
sys.path.insert(0, '/tmp')
from elfhelper import Elf
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

SO = '/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so'

class Binary:
    def __init__(self, path=SO):
        self.e = Elf(path)
        self.d = self.e.d
        self.sec = self.e.sec
        self.md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        self.md.detail = False
        self.text_va, self.text_off, self.text_sz = self.sec['.text']
        self.funcs = self._exidx()
        self.fmap = {f[0]: f for f in self.funcs}
        self._starts = sorted(self.fmap)

    def _prel31(self, w, at):
        v = w & 0x7fffffff
        if v & 0x40000000:
            v -= 0x80000000
        return at + v

    def _exidx(self):
        va, off, sz = self.sec['.ARM.exidx']
        starts = set()
        for i in range(0, sz, 8):
            w1 = struct.unpack_from('<I', self.d, off + i)[0]
            at = va + i
            f = self._prel31(w1, at)
            starts.add(f & ~1)
        st = sorted(s for s in starts if self.text_va <= s < self.text_va + self.text_sz)
        out = []
        for i, s in enumerate(st):
            e = st[i+1] if i+1 < len(st) else self.text_va + self.text_sz
            out.append((s, e))
        return out

    def read(self, va, n):
        return self.e.read(va, n)

    def word(self, va):
        b = self.read(va, 4)
        return struct.unpack('<I', b)[0] if len(b) == 4 else None

    def dis(self, va, n=0x80, stop_at=()):
        """Linear thumb disasm; stops at control-flow terminator when stop_at given."""
        res = []
        base = va
        code = self.read(va, n)
        for i in self.md.disasm(code, va):
            res.append(i)
            if stop_at and i.mnemonic in stop_at:
                break
        return res

    def func_at(self, va):
        import bisect
        i = bisect.bisect_right(self._starts, va) - 1
        if i < 0:
            return None
        s = self._starts[i]
        e = self.fmap[s][1]
        return (s, e) if va < e else None

    def calls_to(self, target):
        """all bl/blx imm sites targeting absolute address (thumb bit insensitive)."""
        text_va, text_off, text_sz = self.text_va, self.text_off, self.text_sz
        out = []
        d = self.d
        for o in range(text_off, text_off + text_sz - 3, 2):
            hw1, hw2 = struct.unpack_from('<HH', d, o)
            if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xC000) != 0xC000:
                continue
            s = (hw1 >> 10) & 1
            imm10 = hw1 & 0x3FF
            j1 = (hw2 >> 13) & 1
            j2 = (hw2 >> 11) & 1
            imm11 = hw2 & 0x7FF
            i1 = (~(j1 ^ s)) & 1
            i2 = (~(j2 ^ s)) & 1
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
            if s:
                imm -= 1 << 25
            pc = text_va + (o - text_off)
            if pc + 4 + imm == target:
                out.append(pc)
        return out

    def xrefs_word(self, target, lo=None, hi=None):
        pat = struct.pack('<I', target)
        out = []
        i = 0
        d = self.d
        while True:
            i = d.find(pat, i)
            if i < 0:
                break
            va = self.e.off2va(i)
            if va is not None and (lo is None or lo <= va <= hi):
                out.append(va)
            i += 1
        return out

    def fmt(self, ins, extra=''):
        return '%08x  %-8s %-30s%s' % (ins.address, ins.bytes.hex(), ins.mnemonic + ' ' + ins.op_str, extra)

    def dump(self, va, n, title=None):
        if title:
            print('--- %s ---' % title)
        for i in self.dis(va, n):
            print(self.fmt(i))

    def str_at(self, va, maxlen=64):
        b = self.read(va, maxlen)
        if not b:
            return None
        s = b.split(b'\0')[0]
        try:
            t = s.decode('latin1')
        except Exception:
            return None
        return t if t else None

if __name__ == '__main__':
    b = Binary()
    print('text', hex(b.text_va), hex(b.text_sz), 'funcs', len(b.funcs))
