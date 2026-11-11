/* G33 — Picture Profile: Black Level, Black Gamma, Knee y Gamma Still aplicados a la curva de gamma del núcleo (A6000 fw3.21).
 *
 * El núcleo recibe estos ajustes en el mensaje LIRO 0x4066 (bytes 0x17…0x26) pero no hay código que los aplique. Aquí se aplican sobre los 2048 puntos
 * de la curva que luego muestrean los constructores de la LUT de 96 puntos (sitios 0x43853226, 0x4385392e y 0x43853c8e): el gancho `pp_curve` devuelve
 * un puntero a una copia modificada (W) en vez del de la tabla. Compilado con clang a Thumb-2 sin libc (ver pp_tone_patch.py).
 * shortcut: una sola copia W compartida (los constructores usan el puntero de inmediato, en una sola tarea); si dos se solaparan saldría una curva mezclada.
 */
typedef unsigned char u8;
typedef signed char s8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

#define TAB ((const u32 *)0x44001404)           /* punteros de curva: [gamma*2 + modo], modo 1 = vídeo */
#define W ((u16 *)0x43FB7EC0)                   /* copia de trabajo: 0x101A B (2048 puntos + 26 B de parámetros) */
#define N 2048
#define TAIL 0x1000
#define TAILN 0x1A

/* Copia de los bytes 0x17…0x26 del 0x4066 (la rellena el gancho del desempaquetador, `pp_tone_patch.py`). */
struct pp { s8 black; u8 bgr; s8 bgl; u8 sel; u8 kmode; u8 kmax; u8 ksens; u8 kpoint; s8 kslope; u8 dmode; s8 dlevel; s8 dvh; u8 dbw; u8 dlimit; u8 dcrisp; u8 dhil; };
extern volatile struct pp pp;
extern struct { u32 src; u32 key[4]; u32 ok; } cache;

static const u16 RANGO[3] = {400, 256, 128};                 /* Black Gamma Range: Wide / Middle / Narrow = 39 % / 25 % / 12,5 % de 1023 */
static const u16 RANGO_K[3] = {2621, 4096, 8192};           /* 2^20 / RANGO */
static const u8 SLOPE_AUTO[3] = {96, 128, 160};             /* sensibilidad High / Mid / Low, Q8: la rodilla automática es suave (el valor por defecto de Max Point no está verificado) */

/* a / b sin libgcc (solo una vez por llamada) */
static u32 udiv(u32 a, u32 b)
{
    u32 q = 0, r = 0;
    int i;
    for (i = 31; i >= 0; i--) {
        r = (r << 1) | ((a >> i) & 1);
        if (r >= b) {
            r -= b;
            q |= 1u << i;
        }
    }
    return q;
}

u16 *pp_curve(u16 *orig, u32 idx)
{
    const u16 *base = orig;
    const u32 *k = (const u32 *)&pp;
    s32 bl, bgl, pt, sl;
    u32 sel, r, rk, i, t;
    s32 prev, top, rtop;
    int log_, knee;

    sel = pp.sel;
    if (!orig || !sel)
        return orig;
    if (sel == 5 && idx == 21 && orig == (u16 *)TAB[21] && TAB[0])      /* Gamma Still en vídeo: curva de contraste de fotografía */
        base = (const u16 *)TAB[0];
    log_ = sel == 2 || sel == 10 || sel == 11;                        /* S-Log3, S-Log2, ITU709(800%) */
    bl = pp.black;
    bgl = log_ ? 0 : pp.bgl;
    r = pp.bgr > 2 ? 2 : pp.bgr;
    pt = 0;
    sl = 256;
    knee = 0;
    if (sel >= 3 && sel <= 5) {                                     /* ITU709, Movie, Still */
        u32 kp = pp.kpoint, km = pp.kmax, ks = pp.ksens;
        if (pp.kmode == 1) {
            kp = kp > 12 ? 12 : kp;
            pt = (1023 * (750 + 25 * kp)) / 1000;
            sl = 128 - 18 * pp.kslope;
        } else {
            km = km > 4 ? 4 : km;
            pt = (1023 * (900 + 25 * km)) / 1000;
            sl = SLOPE_AUTO[ks > 2 ? 2 : ks];
        }
        knee = pt < 1023 && sl < 256;
    }
    if (!bl && !bgl && !knee && base == orig)
        return orig;
    if (cache.ok && cache.src == (u32)orig && cache.key[0] == k[0] && cache.key[1] == k[1] && cache.key[2] == k[2] && cache.key[3] == k[3])
        return W;

    rk = RANGO_K[r];
    top = base[N - 1] > 64 ? base[N - 1] : 64;                         /* blanco de la curva: el Black Level se desvanece hasta él */
    rtop = (s32)udiv(1u << 20, (u32)top);
    prev = 0;
    for (i = 0; i < N; i++) {
        s32 v = base[i];
        if (bgl && v < (s32)RANGO[r]) {
            t = ((u32)v * rk) >> 10;                                 /* 0…1024 */
            v += (bgl * (s32)RANGO[r] * (s32)(((4 * t * (1024 - t)) >> 10) >> 2)) >> 13;   /* ±RANGO/32 por nivel: con más pendiente la curva dejaría de ser monótona y se aplanaría */
        }
        if (bl && v < top)
            v += (s32)(((bl * 6 * (top - v)) * rtop) >> 20);
        if (knee && v > pt)
            v = pt + (((v - pt) * sl) >> 8);
        v = v < 0 ? 0 : v > 2047 ? 2047 : v;
        v = v < prev ? prev : v;
        prev = v;
        W[i] = (u16)v;
    }
    for (i = 0; i < TAILN; i++)
        ((u8 *)W)[TAIL + i] = ((const u8 *)orig)[TAIL + i];
    cache.src = (u32)orig;
    cache.key[0] = k[0];
    cache.key[1] = k[1];
    cache.key[2] = k[2];
    cache.key[3] = k[3];
    cache.ok = 1;
    return W;
}

/* ---- Detail (G33): se aplica a los parámetros APC (apertura) que el núcleo calcula para el perfil de creative style, justo antes de escribirlos en el hardware ---- */

/* g[0] = apgain (0…0x1FF), g[1] = vapgain, g[2] = hapgain (0…0x10). Detail Level escala la ganancia, V/H Balance reparte entre vertical y horizontal y Limit la recorta. */
void pp_gain(u16 *g)
{
    s32 a, v, h, cap, l;
    if (!pp.sel || pp.dmode != 1)
        return;
    a = ((s32)g[0] * (256 + 30 * pp.dlevel)) >> 8;                  /* −7…+7 → 0,18…1,82 */
    l = pp.dlimit > 7 ? 7 : pp.dlimit;
    cap = (0x1FF * (l + 4)) / 11;                                   /* Limit 7 = sin recorte */
    a = a > cap ? cap : a;
    v = ((s32)g[1] * (256 + 60 * pp.dvh)) >> 8;                     /* V/H −2…+2 → vertical 0,70…1,30, horizontal inverso */
    h = ((s32)g[2] * (256 - 60 * pp.dvh)) >> 8;
    g[0] = (u16)(a < 0 ? 0 : a > 0x1FF ? 0x1FF : a);
    g[1] = (u16)(v < 0 ? 0 : v > 0x10 ? 0x10 : v);
    g[2] = (u16)(h < 0 ? 0 : h > 0x10 ? 0x10 : h);
}

/* c[0…2] = coring vertical p0…p2, c[3] = aplk, c[4…6] = coring horizontal p0…p2, c[7] = aplk. Crispening sube el umbral de coring (menos detalle de bajo contraste). */
void pp_coring(u16 *c)
{
    static const u8 IDX[6] = {0, 1, 2, 4, 5, 6};
    u32 f, i, x;
    if (!pp.sel || pp.dmode != 1)
        return;
    f = 256 + 100 * (pp.dcrisp > 7 ? 7 : pp.dcrisp);
    for (i = 0; i < 6; i++) {
        x = ((u32)c[IDX[i]] * f) >> 8;
        c[IDX[i]] = (u16)(x > 0x1FF ? 0x1FF : x);
    }
}
