#!/usr/bin/env python3
"""Volcado recursivo de cajas ISO-BMFF de un MP4. Sin dependencias externas.

Uso: clip-boxdump.py <fichero> [--json]
Recorre contenedores conocidos y cajas de muestra (stsd), imprime offset, tamano,
tipo y uuid, y los campos de las cajas que interesan al diagnostico.
"""
import json
import struct
import sys

CONT = {
    b"moov", b"trak", b"mdia", b"minf", b"stbl", b"edts", b"dinf", b"udta",
    b"moof", b"traf", b"mvex", b"ilst", b"meta", b"wave", b"sinf", b"schi",
}
LEAF_DUMP = {b"ftyp", b"mvhd", b"tkhd", b"mdhd", b"hdlr", b"stts", b"ctts",
             b"stss", b"elst", b"vmhd", b"smhd", b"dref", b"stsz", b"stco",
             b"co64", b"stsc", b"avcC", b"esds", b"mehd", b"trex", b"mfhd"}

out = []


def p(*a):
    out.append(" ".join(str(x) for x in a))


def u8(b, o):
    return b[o]


def u16(b, o):
    return struct.unpack_from(">H", b, o)[0]


def u32(b, o):
    return struct.unpack_from(">I", b, o)[0]


def s32(b, o):
    return struct.unpack_from(">i", b, o)[0]


def u64(b, o):
    return struct.unpack_from(">Q", b, o)[0]


def full(b, o):
    """version + flags de una caja FullBox."""
    v = b[o]
    f = int.from_bytes(b[o + 1:o + 4], "big")
    return v, f


def fourcc_ok(t):
    return all(32 <= c < 127 for c in t)


def desc_box(path, data, off, size, typ, depth):
    pad = "  " * depth
    extra = ""
    if typ == b"uuid":
        extra = " usertype=" + data[off + 8:off + 24].hex()
    p(f"{pad}{off:>9} {size:>9} {typ.decode('latin1')}{extra}")
    hdr = 8
    if u32(data, off) == 1:
        hdr = 16
    if typ == b"uuid":
        hdr += 16
    body = data[off + hdr:off + size]
    if typ == b"ftyp":
        maj = body[0:4]
        minor = u32(body, 4)
        brands = [body[i:i + 4].decode("latin1") for i in range(8, len(body) - 3, 4)]
        p(f"{pad}    major={maj.decode('latin1')} minor={minor} compatible={brands}")
    elif typ == b"mvhd":
        v, f = full(body, 0)
        if v == 0:
            ts, du = u32(body, 12), u32(body, 16)
        else:
            ts, du = u32(body, 20), u64(body, 24)
        p(f"{pad}    v={v} flags={f:#x} timescale={ts} duration={du} "
          f"({du/ts:.6f}s)" if ts else f"{pad}    v={v} timescale=0")
    elif typ == b"tkhd":
        v, f = full(body, 0)
        tid = u32(body, 12 if v == 0 else 20)
        du = u32(body, 20 if v == 0 else 28)
        w = u32(body, len(body) - 8) / 65536.0
        h = u32(body, len(body) - 4) / 65536.0
        p(f"{pad}    v={v} flags={f:#x} track_id={tid} duration={du} "
          f"display={w:.3f}x{h:.3f}")
    elif typ == b"mdhd":
        v, f = full(body, 0)
        ts = u32(body, 12 if v == 0 else 20)
        du = u32(body, 16 if v == 0 else 24)
        lang = u16(body, 20 if v == 0 else 32)
        p(f"{pad}    v={v} timescale={ts} duration={du} lang={lang:#06x}")
    elif typ == b"hdlr":
        p(f"{pad}    handler={body[8:12].decode('latin1')}")
    elif typ == b"stts":
        n = u32(body, 4)
        ent = [(u32(body, 8 + 8 * i), u32(body, 12 + 8 * i)) for i in range(min(n, 8))]
        p(f"{pad}    entries={n} (count,delta)={ent}")
    elif typ == b"ctts":
        v, _ = full(body, 0)
        n = u32(body, 4)
        ent = [(u32(body, 8 + 8 * i), s32(body, 12 + 8 * i)) for i in range(min(n, 6))]
        p(f"{pad}    v={v} entries={n} (count,offset)={ent}")
    elif typ == b"stss":
        n = u32(body, 4)
        ss = [u32(body, 8 + 4 * i) for i in range(min(n, 12))]
        p(f"{pad}    entries={n} first_sync={ss}")
    elif typ == b"elst":
        v, _ = full(body, 0)
        n = u32(body, 4)
        if v == 0:
            ent = [(u32(body, 8 + 12 * i), s32(body, 12 + 12 * i),
                    u16(body, 16 + 12 * i), u16(body, 18 + 12 * i)) for i in range(n)]
        else:
            ent = [(u64(body, 8 + 20 * i), struct.unpack_from(">q", body, 16 + 20 * i)[0],
                    u16(body, 24 + 20 * i), u16(body, 26 + 20 * i)) for i in range(n)]
        p(f"{pad}    v={v} entries={n} (dur,media_time,rate_int,rate_frac)={ent}")
    elif typ in (b"stco", b"co64"):
        n = u32(body, 4)
        sz = 4 if typ == b"stco" else 8
        rd = u32 if typ == b"stco" else u64
        vals = [rd(body, 8 + sz * i) for i in range(min(n, 8))]
        p(f"{pad}    entries={n} first={vals}")
    elif typ == b"stsz":
        ss, n = u32(body, 4), u32(body, 8)
        sizes = [u32(body, 12 + 4 * i) for i in range(min(n, 6))] if ss == 0 else []
        p(f"{pad}    sample_size={ss} count={n} first_sizes={sizes}")
    elif typ == b"stsc":
        n = u32(body, 4)
        ent = [(u32(body, 8 + 12 * i), u32(body, 12 + 12 * i), u32(body, 16 + 12 * i))
               for i in range(min(n, 8))]
        p(f"{pad}    entries={n} (first,per_chunk,sdi)={ent}")
    elif typ == b"avcC":
        nsps = body[5] & 0x1f
        sps = [u16(body, 6 + 2 * 0) ]
        p(f"{pad}    cfgVersion={body[0]} profile={body[1]} compat={body[2]:#04x} "
          f"level={body[3]:#04x} lengthSizeMinusOne={body[4]&3} "
          f"numSPS={nsps} sps_len={u16(body,6)}")
        if nsps >= 1:
            l = u16(body, 6)
            sps0 = body[8:8 + l]
            p(f"{pad}    SPS={sps0.hex()}")
            # parse SPS: profile_idc, constraint flags, level_idc, then UE values
            import io
            p(f"{pad}    SPS.profile={sps0[1]} level={sps0[3]:#04x}")
        np_ = body[8 + u16(body, 6)] if len(body) > 8 + u16(body, 6) else 0
        p(f"{pad}    PPS count={np_}")
    elif typ == b"vmhd":
        p(f"{pad}    v={body[8]} flags={int.from_bytes(body[9:12],'big'):#x}")
    elif typ == b"dref":
        p(f"{pad}    entries={u32(body,4)}")
    elif typ == b"stsd":
        n = u32(body, 4)
        p(f"{pad}    entries={n}")
    elif typ == b"mp4a":
        p(f"{pad}    channels={u16(body,16)} sample_size={u16(body,18)} "
          f"rate={u32(body,24)/65536.0:.1f}")
    elif typ in (b"avc1", b"avc3", b"hvc1", b"hev1", b"mp4v", b"encv"):
        p(f"{pad}    w={u16(body,24)} h={u16(body,26)} hres={u32(body,28)/65536.0:.0f} "
          f"frame_count={u16(body,40)} compressorname={body[42:74].split(bytes([0]))[0]!r} "
          f"depth={u16(body,74):#x}")
    return


def walk(data, start, end, depth=0, path=""):
    off = start
    while off + 8 <= end:
        size = u32(data, off)
        typ = data[off + 4:off + 8]
        hdr = 8
        if size == 1:
            size = u64(data, off + 8)
            hdr = 16
        elif size == 0:
            size = end - off
        if size < hdr or off + size > end:
            p(f"{'  '*depth}{off:>9} {size:>9} !! caja invalida tipo={typ!r}")
            return
        desc_box(path, data, off, size, typ, depth)
        inner = None
        if typ in CONT:
            inner = (off + hdr, off + size)
        elif typ == b"stsd":
            # 1 caja de entrada de muestra: 8 bytes de contador + entrada
            n = u32(data, off + 12)
            if n >= 1:
                inner = (off + 16, off + size)
        elif typ in (b"avc1", b"avc3", b"hvc1", b"hev1", b"mp4v", b"encv"):
            inner = (off + 8 + 78, off + size)
        elif typ == b"mp4a":
            inner = (off + 8 + 28, off + size)
        elif typ == b"meta":
            inner = (off + hdr + 4, off + size)
        if inner:
            walk(data, inner[0], inner[1], depth + 1, path + "/" + typ.decode("latin1"))
        off += size


def main():
    fn = sys.argv[1]
    data = open(fn, "rb").read()
    p(f"# fichero={fn} size={len(data)}")
    walk(data, 0, len(data))
    txt = "\n".join(out)
    print(txt)


if __name__ == "__main__":
    main()
