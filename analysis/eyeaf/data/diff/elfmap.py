import struct, sys

class ELF:
    def __init__(self, path):
        self.path = path
        self.data = open(path,'rb').read()
        d = self.data
        assert d[:4] == b'\x7fELF'
        self.is64 = d[4] == 2
        self.le = d[5] == 1
        e = '<' if self.le else '>'
        if self.is64:
            self.e_shoff = struct.unpack_from(e+'Q', d, 0x28)[0]
            self.e_shentsize = struct.unpack_from(e+'H', d, 0x3a)[0]
            self.e_shnum = struct.unpack_from(e+'H', d, 0x3c)[0]
            self.e_shstrndx = struct.unpack_from(e+'H', d, 0x3e)[0]
            self.e_phoff = struct.unpack_from(e+'Q', d, 0x20)[0]
            self.e_phentsize = struct.unpack_from(e+'H', d, 0x36)[0]
            self.e_phnum = struct.unpack_from(e+'H', d, 0x38)[0]
            self.e_type = struct.unpack_from(e+'H', d, 0x10)[0]
            self.e_machine = struct.unpack_from(e+'H', d, 0x12)[0]
        else:
            self.e_shoff = struct.unpack_from(e+'I', d, 0x20)[0]
            self.e_shentsize = struct.unpack_from(e+'H', d, 0x2e)[0]
            self.e_shnum = struct.unpack_from(e+'H', d, 0x30)[0]
            self.e_shstrndx = struct.unpack_from(e+'H', d, 0x32)[0]
            self.e_phoff = struct.unpack_from(e+'I', d, 0x1c)[0]
            self.e_phentsize = struct.unpack_from(e+'H', d, 0x2a)[0]
            self.e_phnum = struct.unpack_from(e+'H', d, 0x2c)[0]
            self.e_type = struct.unpack_from(e+'H', d, 0x10)[0]
            self.e_machine = struct.unpack_from(e+'H', d, 0x12)[0]
        self.e = e
        self.sections = []
        for i in range(self.e_shnum):
            off = self.e_shoff + i*self.e_shentsize
            if self.is64:
                name, typ, flags, addr, offset, size = struct.unpack_from(e+'IIQQQQ', d, off)
            else:
                name, typ, flags, addr, offset, size = struct.unpack_from(e+'IIIIII', d, off)
            self.sections.append(dict(idx=i, nameoff=name, type=typ, flags=flags, addr=addr, off=offset, size=size))
        shstr = self.sections[self.e_shstrndx]
        for s in self.sections:
            s['name'] = self.cstr(shstr['off'] + s['nameoff'])
        self.segments = []
        for i in range(self.e_phnum):
            off = self.e_phoff + i*self.e_phentsize
            if self.is64:
                p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz = struct.unpack_from(e+'IIQQQQQ', d, off)
            else:
                p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags = struct.unpack_from(e+'IIIIIII', d, off)
            self.segments.append(dict(type=p_type, off=p_offset, vaddr=p_vaddr, filesz=p_filesz, memsz=p_memsz, flags=p_flags))

    def cstr(self, off):
        end = self.data.find(b'\0', off)
        return self.data[off:end].decode('latin-1')

    def off2va(self, off):
        for s in self.sections:
            if s['type'] != 8 and s['off'] <= off < s['off'] + s['size']:
                return s['addr'] + (off - s['off'])
        for p in self.segments:
            if p['off'] <= off < p['off'] + p['filesz']:
                return p['vaddr'] + (off - p['off'])
        return None

    def va2off(self, va):
        for s in self.sections:
            if s['type'] != 8 and s['addr'] <= va < s['addr'] + s['size'] and s['addr']:
                return s['off'] + (va - s['addr'])
        for p in self.segments:
            if p['vaddr'] <= va < p['vaddr'] + p['filesz']:
                return p['off'] + (va - p['vaddr'])
        return None

    def sec(self, name):
        for s in self.sections:
            if s['name'] == name:
                return s
        return None

    def find_str(self, needle, exact=True):
        """return list of file offsets of needle (cstr-terminated) occurrences"""
        out = []
        pat = needle.encode() if isinstance(needle, str) else needle
        start = 0
        while True:
            i = self.data.find(pat, start)
            if i < 0: break
            if exact:
                j = i + len(pat)
                if j < len(self.data) and self.data[j] == 0:
                    out.append(i)
            else:
                out.append(i)
            start = i + 1
        return out
