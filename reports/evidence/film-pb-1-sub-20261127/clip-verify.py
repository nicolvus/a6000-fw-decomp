#!/usr/bin/env python3
"""Integridad estructural del MP4: cobertura de mdat, tablas de muestras, tiempos.

Uso: clip-verify.py <fichero>
"""
import struct
import sys

d = open(sys.argv[1], 'rb').read()
N = len(d)


def u32(o):
    return struct.unpack_from('>I', d, o)[0]


def boxes(start, end):
    o = start
    while o + 8 <= end:
        sz = u32(o)
        ty = d[o + 4:o + 8]
        if sz == 1:
            sz = struct.unpack_from('>Q', d, o + 8)[0]
        if sz < 8 or o + sz > end:
            yield (o, end - o, ty, True)
            return
        yield (o, sz, ty, False)
        o += sz


print('# fichero=%s size=%d' % (sys.argv[1], N))

# 1. cajas de nivel 0 y cobertura total
cov = 0
print('## nivel 0')
for o, sz, ty, bad in boxes(0, N):
    print('  %9d %9d %s%s' % (o, sz, ty.decode('latin1'), ' INVALIDA' if bad else ''))
    cov += sz
print('  cobertura=%d de %d (sobrante=%d)' % (cov, N, N - cov))

# 2. localizar moov/mdat
moffs = {}
for o, sz, ty, bad in boxes(0, N):
    moffs.setdefault(ty, []).append((o, sz))
mdat_o, mdat_sz = moffs[b'mdat'][0]
moov_o, moov_sz = moffs[b'moov'][0]
print('## mdat off=%d size=%d payload=[%d,%d)' % (mdat_o, mdat_sz, mdat_o + 8, mdat_o + mdat_sz))
print('## moov off=%d size=%d  (tras mdat: %s)' % (moov_o, moov_sz, moov_o > mdat_o))


def child(off, base, path):
    """Devuelve (off,tam) de la caja path dentro de base=(o,sz)."""
    for o, sz, ty, bad in boxes(base[0] + 8, base[0] + base[1]):
        if ty == path.encode():
            return (o, sz)
    return None


def traks():
    out = []
    for o, sz, ty, bad in boxes(moov_o + 8, moov_o + moov_sz):
        if ty == b'trak':
            out.append((o, sz))
    return out


def parse_track(t):
    r = {}
    for name in ('tkhd', 'mdhd', 'hdlr', 'stts', 'stsz', 'stco', 'co64', 'stsc', 'stss', 'ctts', 'elst'):
        pass
    mdia = child(0, t, 'mdia')
    r['mdia'] = mdia
    r['tkhd'] = child(0, t, 'tkhd')
    r['edts'] = child(0, t, 'edts')
    r['elst'] = child(0, r['edts'], 'elst') if r['edts'] else None
    r['mdhd'] = child(0, mdia, 'mdhd')
    r['hdlr'] = child(0, mdia, 'hdlr')
    minf = child(0, mdia, 'minf')
    stbl = child(0, minf, 'stbl')
    r['stbl'] = stbl
    for k in ('stsd', 'stts', 'ctts', 'stsc', 'stsz', 'stco', 'stss', 'co64'):
        r[k] = child(0, stbl, k)
    return r


for i, t in enumerate(traks()):
    r = parse_track(t)
    mdhd = r['mdhd']
    ts = u32(mdhd[0] + 20)
    du = u32(mdhd[0] + 24)
    hdlr = d[r['hdlr'][0] + 16:r['hdlr'][0] + 20].decode('latin1')
    stsz = r['stsz']
    cnt = u32(stsz[0] + 16)
    sizes = [u32(stsz[0] + 20 + 4 * k) for k in range(cnt)]
    stts = r['stts']
    ns = u32(stts[0] + 12)
    tot = 0
    deltas = []
    for k in range(ns):
        c = u32(stts[0] + 16 + 8 * k)
        dl = u32(stts[0] + 20 + 8 * k)
        tot += c
        deltas += [dl] * c
    stco = r['stco'] or r['co64']
    nch = u32(stco[0] + 12)
    ch = [u32(stco[0] + 16 + 4 * k) for k in range(nch)]
    stsc = r['stsc']
    nsc = u32(stsc[0] + 12)
    sc = [(u32(stsc[0] + 16 + 12 * k), u32(stsc[0] + 20 + 12 * k)) for k in range(nsc)]
    # reconstruir posiciones de muestra por chunks
    pos = []
    for k, c in enumerate(ch):
        first = max([s for s, per in sc if s <= k + 1], default=None)
        per = dict(sc)[first]
        off = c
        for j in range(per):
            idx = sum([dict(sc).get(x, 0) for x in range(1, first)]) + (k - first + 1) * per + j
            if idx >= cnt:
                break
            pos.append((idx, off, sizes[idx]))
            off += sizes[idx]
    inside = all(mdat_o + 8 <= p < mdat_o + mdat_sz for _, p, _ in pos)
    print('## trak %d hdlr=%s timescale=%d duration=%d (%.6fs) muestras=%d stts_total=%d chunks=%d'
          % (i, hdlr, ts, du, du / ts, cnt, tot, nch))
    print('   muestras cubiertas=%d  dentro de mdat=%s  fin datos=%d (mdat fin=%d)'
          % (len(pos), inside, max(p + s for _, p, s in pos), mdat_o + mdat_sz))
    print('   stts delta unico=%s  primer size=%d  suma=%d' %
          (sorted(set(deltas))[:4], sizes[0], sum(sizes)))
    if r['stss']:
        n = u32(r['stss'][0] + 12)
        print('   stss n=%d %s' % (n, [u32(r['stss'][0] + 16 + 4 * k) for k in range(min(n, 12))]))
    if r['ctts']:
        n = u32(r['ctts'][0] + 12)
        print('   ctts n=%d %s' % (n, [(u32(r['ctts'][0] + 16 + 8 * k), u32(r['ctts'][0] + 20 + 8 * k))
                                       for k in range(min(n, 4))]))
    if r['elst']:
        n = u32(r['elst'][0] + 12)
        print('   elst n=%d %s' % (n, [(u32(r['elst'][0] + 16 + 12 * k), u32(r['elst'][0] + 20 + 12 * k))
                                       for k in range(n)]))
