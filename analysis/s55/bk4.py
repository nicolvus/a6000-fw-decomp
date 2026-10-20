"""S55: lector de imágenes de backup BK4 (firmware 0110_backup) con la misma lógica que backup.ko (Data_init/Data_SearchId/Data_GetDataPt)."""
import struct
from pathlib import Path
class BK4:
    def __init__(s, path):
        s.d = Path(path).read_bytes(); d = s.d
        assert d[0x0c:0x0f] == b'BK4', 'no es BK4'
        s.nsid = s.u32(0x10); s.sid = 0x100; s.et = 0x100 + 6 * s.nsid   # Data_init: ctx[4]=base+0x100, ctx[8]=ctx[4]+6*nsid
        s.sids = [(s.u16(s.sid + 6 * i), s.u32(s.sid + 6 * i + 2)) for i in range(s.nsid)]
    def u16(s, o): return struct.unpack_from('<H', s.d, o)[0]
    def u32(s, o): return struct.unpack_from('<I', s.d, o)[0]
    def entry(s, id_):
        sid, ix = id_ >> 16, id_ & 0xffff
        if sid >= s.nsid: return None
        cnt, base = s.sids[sid]
        if ix >= cnt: return None
        o = s.et + 6 * (base + ix)
        size, off = s.u16(o), s.u32(o + 2)
        return None if off == 0xffffffff else (size, off)
    def ptr(s, id_):                       # Data_GetDataPt: base + (off & 0xffffff) + {0:4, 0xff:2, otro:0}
        e = s.entry(id_)
        if not e: return None
        fl = e[1] >> 24
        return (e[1] & 0xffffff) + (4 if fl == 0 else 2 if fl == 0xff else 0)
    def u32val(s, id_):                    # Backup_read_4Byte: solo si tamaño == 4
        e = s.entry(id_); p = s.ptr(id_)
        return None if not e or e[0] != 4 and e[0] != 0 else s.u32(p)   # shortcut: tamaño 0 observado en estas entradas, no se valida
