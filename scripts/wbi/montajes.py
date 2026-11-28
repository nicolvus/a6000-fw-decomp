"""Lista los montajes guardados en una instantánea WBI/prof (kernel 3.0 de la A6000).

Uso (desde la raíz del repo): python3 scripts/wbi/montajes.py IMAGEN [IMAGEN...]
Recorre el árbol de vfsmount desde el /usr de im.elf y lee de cada superbloque
tipo, s_flags y s_magic. Desplazamientos comprobados con s_magic conocidos.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapram import Ram

MS_RDONLY = 1


def cstr(r, p, n=64):
    return r.read(p, n).split(b'\0')[0].decode('latin1')


def dname(r, d):
    ln = r.u(d + 0x34)
    if not 0 < ln < 256:
        raise ValueError(hex(d))
    return r.read(r.u(d + 0x38), ln).decode('latin1')


def dpath(r, d):
    parts = []
    for _ in range(32):
        parent = r.u(d + 0x18)
        n = dname(r, d)
        if parent == d:
            break
        parts.append(n)
        d = parent
    return '/' + '/'.join(reversed(parts))


def nodes(r, head, offset):
    v, prev, seen = r.u(head), head, set()
    while v != head:
        assert v not in seen and r.u(v + 4) == prev
        seen.add(v)
        yield v - offset
        prev, v = v, r.u(v)


def mounts(r):
    _, mm = next(r.tasks(b'im.elf'))
    usr = r.u(r.u(r.u(mm) + 0x4c) + 8)  # vma->vm_file->f_path.mnt
    root, seen = usr, set()
    while r.u(root + 8) != root:
        seen.add(root)
        root = r.u(root + 8)
    out, stack = [], [(root, '')]
    while stack:
        m, base = stack.pop()
        mp = dname(r, r.u(m + 0xc))
        path = base if m == root else (base.rstrip('/') + '/' + mp if mp != '/' else base)
        sb = r.u(m + 0x14)
        fstype = cstr(r, r.u(r.u(sb + 0x20)))
        out.append({'mnt': hex(m), 'path': path or '/', 'dev': cstr(r, r.u(m + 0x3c)),
                    'fs': fstype, 'ro': bool(r.u(sb + 0x34) & MS_RDONLY),
                    'sflags': hex(r.u(sb + 0x34)), 'magic': hex(r.u(sb + 0x38)),
                    'mntflags': hex(r.u(m + 0x30))})
        for ch in nodes(r, m + 0x20, 0x28):
            if r.u(ch + 8) == m:
                stack.append((ch, path or '/'))
    return out


if __name__ == '__main__':
    for p in sys.argv[1:]:
        r = Ram(Path(p))
        print('==', p, r.header[:4])
        for x in sorted(mounts(r), key=lambda x: x['path']):
            print(f"{x['path']:<28} {x['dev']:<18} {x['fs']:<8} ro={int(x['ro'])} "
                  f"s_flags={x['sflags']} magic={x['magic']} mnt_flags={x['mntflags']}")
