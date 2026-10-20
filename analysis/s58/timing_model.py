"""S58-A/B: modelo Python (aritmética entera de 32 bit, truncada como ARM) del productor de svd/shd/spl del IMX210 (A6000, firmware 3.21).
Cada función cita la dirección de av-cam.bin que reproduce. Se valida con Unicorn en tests/test_s58_timing_a7s.py."""
M32 = 0xffffffff
def udiv(a, b): return (a & M32) if b == 0 else ((a & M32) // (b & M32))    # 0x43b084e8: b==0 -> a (0x4355faf0 para b!=0)
def sdiv(a, b):                                                              # 0x43b0791e: b==0 -> a
    a = a if a < 1 << 31 else a - (1 << 32); b = b if b < 1 << 31 else b - (1 << 32)
    if b == 0: return a & M32
    q = abs(a) // abs(b); return (q if (a < 0) == (b < 0) else -q) & M32
def tick(clk_hz):
    """0x4383d4d0: sl = 256e6 / (clk/1000); clk==0 -> 0xde3 (=72 MHz)."""
    return 0xde3 if clk_hz == 0 else udiv(0xf424000, udiv(clk_hz, 1000))
def time_split(T, M, clk_hz):
    """0x4383d4d0(T, M, clk, &n, &shd, &spl): descompone el tiempo T en n periodos de (F*svr), líneas (shd) y relojes finos (spl).
    M: u32 s0=M[0x00], lt=M[0x04], fb=M[0x08], F=M[0x20]; u16 vmax=M[0x10], shmin=M[0x14], hmax=M[0x2c]; u8 svr=M[0x16]."""
    sl = tick(clk_hz); Fs = (M['F'] * M['svr']) & M32
    n = sdiv(T, Fs); rem = (T - n * Fs) & M32
    h = M['hmax']
    if h:
        fine = udiv(h * sl, 1000); sb = (M['s0'] - M['fb'] - fine) & M32 if M['s0'] > (fine + M['fb']) & M32 else 0
    else:
        sb = max((M['s0'] - M['fb']) & M32, 0)
    lines = udiv((rem - sb) & M32, M['lt']) if rem > sb else 0
    shd = M['shmin'] if ((M['vmax'] - M['shmin']) & M32) < lines else (M['vmax'] - lines) & 0xffff
    if h:
        rem2 = (rem - M['lt'] * lines) & M32
        f2 = udiv(1000 * ((rem2 - sb) & M32), sl) if rem2 > sb else 0
        spl = 0 if h < f2 else h - f2
    else: spl = 0
    return n, shd, spl, lines
def reconstruct_time(n, shd, spl, M, clk_hz, sb_rest):
    """Inversa algebraica (0x4383d430): T = n*F*svr + (vmax-shd)*lt + (hmax-spl)*tick/1000 + sb. No es una función del firmware, solo la identidad usada."""
    return n * M['F'] * M['svr'] + (M['vmax'] - shd) * M['lt'] + udiv((M['hmax'] - spl) * tick(clk_hz), 1000) + sb_rest

def clamp3(a, b, c):
    """0x43adb0d2 / 0x43b08960 (idénticas): c<=a ? (c<b ? b : c) : a   (comparaciones sin signo)."""
    if c <= a:
        a = c
        if c < b: a = b
    return a & M32
def spl_remaining(p1, p2, flag):
    """0x4383c7e0: p1<p2 ? 0 : (p1-p2)&0xffff ; con flag==1 además escribe un byte de estado en [..+0x468] (no modelado)."""
    return 0 if p1 < p2 else (p1 - p2) & 0xffff
def s16(v): v &= 0xffff; return v - 0x10000 if v & 0x8000 else v
def build_rows(G, dbg_flag_ret=0):
    """0x4383c9dc(G, G224): filas de 16 B por banco (shd=word0, svd=+4, spl=+6, fine=+10, +12, +14) que 0x43849fb8 copia a arg[0..0xf] de SetExposure.
    G: dict con b0[4], c0[4], d0[4] (u32), u16 {'10','14','18','28','2a','2c','2e','38'}, u8 {'16','24','3a','163','164','190'}, u32 {'30','34'}."""
    rows = []; u6 = G['2e']
    for i in range(4):
        shdb, fine, ni = G['b0'][i], G['c0'][i], G['d0'][i]
        sv2 = G['2c']; u9 = G['10']; l40 = u9; l3c = ni
        if G['24']:
            i16 = (G['18'] * (((G['30'] - 1) & M32) - l3c)) & M32
            shdb = (shdb + i16) & M32; l40 = (i16 + u9) & M32; l3c = G['30']
        if sv2 and G['24']: l40 = u9
        svr = G['16']; N = G['30']; vd = s16(G['38']) if G['38'] else 0
        if G['34'] == 0:
            ret1 = dbg_flag_ret == 1
            f6c = 1 if (G['163'] == 1 or G['164'] == 1) and ret1 else (G['190'] if (G['163'] == 1 or G['164'] == 1) else 0)
            i16 = (N - 1) & M32 if f6c == 1 else N
            s4 = ((i16 * svr) & 0xffff) if vd == 0 else udiv((i16 * svr) & M32, vd & M32)
            svd = (s4 - 1) & 0xffff; word0 = shdb
            i15 = (svr * N) & M32 if vd == 0 else udiv((svr * N) & M32, vd & M32)
            spl = spl_remaining((i15 - 1) & M32, (l3c * svr) & M32, G['3a'])
        else: svd = 0; word0 = shdb; spl = 0
        r36 = fine & 0xffff if sv2 else 0; r38 = 0; r3a = 0
        if G['34'] == 0:
            if svr == 0: svd = 3
            else:
                rem = (svd + 1) % svr
                if rem: svd = svr - 1
                i11 = (svr * N) & M32 if vd == 0 else udiv((svr * N) & M32, vd & M32)
                svd = clamp3((i11 - 1) & 0xffff, 0, svd)
        elif svd: svd = 0
        word0 = clamp3(l40, G['14'], word0)
        spl = clamp3(svd, 0, spl); r36 = clamp3(sv2, 0, r36); r38 = clamp3(G['28'], G['2a'], r38)
        u6 = clamp3(u6, 0, r3a); r3a = u6
        rows.append(dict(shd=word0 & 0xffff, shd_hi=(word0 >> 16) & 0xffff, svd=svd & 0xffff, spl=spl & 0xffff, f36=r36, f38=r38, f3a=r3a))
    return rows
