/* G89 (LUT-SD-1) — carga de `.cube` desde la SD EN LA CÁMARA, userland (se inyecta en `viewUnified2.so`, proceso de `libObj`).
 * Sin libc ni datos globales (clang -fropi): todo el estado va en `struct ctx` (malloc); las funciones del sistema llegan por `dlsym` en `struct api`.
 * Por cada ranura 1…SLOTS lee `X:/LUT/LUT<n>.cube`, lo remuestrea a la LUT 5×9×9 del ISP por muestreo directo de cada nodo con corrección de 2.ª diferencia (G90; punto fijo Q16, igual que
 * `lut_sd_userland.referencia`) y lo guarda empaquetado a 21 bits (1064 B) en el id de Backup `BK_ID` (16 KB): av-cam lo lee con `Backup_read`.
 * Contratos (leídos del código real, g89 §2): Fsys_Open(path, int *h, modo=1) · Fsys_Read(h, buf, n) → bytes · Fsys_Close(h) · Fsys_GetDriveLetter(dispositivo) → letra
 * · Backup_read(id, buf) · Backup_write(id>>16, id, buf). */
typedef unsigned int u32;
typedef int i32;
typedef long long i64;
typedef unsigned long long u64;
typedef unsigned char u8;

#define SLOTS 6
#define TAM_TABLA 1064
#define BK_TAM 16384
#define BK_ID 0x150005u
#define CHUNK 4096
#define MAGIC 0x5354554Cu /* "LUTS" */

struct api {
    i32 (*f_open)(const char *, i32 *, i32);
    i32 (*f_read)(i32, void *, i32);
    i32 (*f_close)(i32);
    i32 (*f_drive)(const char *);
    i32 (*b_read)(u32, void *);
    i32 (*b_write)(u32, u32, const void *);
    void *(*m_alloc)(u32);
    void (*m_free)(void *);
    u32 (*s_sleep)(u32);
};

struct ctx {
    struct api a;
    u8 blob[BK_TAM];
    u8 tmp[BK_TAM];
    u8 chunk[CHUNK];
    i32 diag[6 * 4], rd[6];
    char line[96];
    i32 *cube;     /* n³·3 en Q16, índice ((b·n+g)·n+r)·3+canal */
    i32 n, lo[3], hi[3], filled, ll, drive, err;
};

void *memset(void *p, int v, u32 n) {
    u8 *q = p;
    while (n--) *q++ = (u8)v;
    return p;
}

void *memcpy(void *d, const void *s, u32 n) {
    u8 *q = d;
    const u8 *r = s;
    while (n--) *q++ = *r++;
    return d;
}

static void zero(void *p, u32 n) { memset(p, 0, n); }

/* división sin ARM `udiv` (Cortex-A9 userland sin idiv) ni libgcc: desplazar y restar */
static u64 div64(u64 n, u64 d) {
    u64 q = 0, r = 0;
    for (i32 i = 63; i >= 0; i--) {
        r = (r << 1) | ((n >> i) & 1);
        if (r >= d) { r -= d; q |= (u64)1 << i; }
    }
    return q;
}

/* Q16 desde texto decimal (signo, parte entera, fracción, exponente) */
static i32 q16(const char *s, const char **fin) {
    i32 neg = 0, e10 = 0;
    i64 m = 0;
    while (*s == ' ' || *s == '\t') s++;
    if (*s == '-') { neg = 1; s++; } else if (*s == '+') s++;
    while (*s >= '0' && *s <= '9') { if (m < 100000000000000000LL) m = m * 10 + (*s - '0'); else e10++; s++; }
    if (*s == '.') {
        s++;
        while (*s >= '0' && *s <= '9') { if (m < 100000000000000000LL) { m = m * 10 + (*s - '0'); e10--; } s++; }
    }
    if (*s == 'e' || *s == 'E') {
        i32 en = 0, x = 0;
        s++;
        if (*s == '-') { en = 1; s++; } else if (*s == '+') s++;
        while (*s >= '0' && *s <= '9') { if (x < 1000) x = x * 10 + (*s - '0'); s++; }
        e10 += en ? -x : x;
    }
    *fin = s;
    while (e10 > 0 && m < 100000000000000LL) { m *= 10; e10--; }
    i64 d = 1;
    while (e10 < 0 && d < 100000000000000000LL) { d *= 10; e10++; }
    i64 v = (i64)div64((u64)(m << 16) + (u64)(d >> 1), (u64)d);
    if (v > 0x7FFFFFFF) v = 0x7FFFFFFF;
    return neg ? -(i32)v : (i32)v;
}

static i32 empieza(const char *s, const char *k) {
    while (*k) if (*s++ != *k++) return 0;
    return 1;
}

static void linea(struct ctx *c) {
    const char *s = c->line, *f;
    c->line[c->ll] = 0;
    for (i32 i = 0; i < c->ll; i++) if (c->line[i] == '#') { c->line[i] = 0; break; }
    while (*s == ' ' || *s == '\t' || *s == '\r') s++;
    if (!*s) return;
    if (empieza(s, "LUT_3D_SIZE")) {
        i32 n = 0;
        s += 11;
        while (*s == ' ' || *s == '\t') s++;
        while (*s >= '0' && *s <= '9') n = n * 10 + (*s++ - '0');
        if (n < 2 || n > 64 || c->cube) { c->err = 1; return; }
        c->n = n;
        c->cube = c->a.m_alloc((u32)n * n * n * 3 * 4);
        if (!c->cube) c->err = 1;
    } else if (empieza(s, "DOMAIN_MIN") || empieza(s, "DOMAIN_MAX")) {
        i32 *d = s[8] == 'I' ? c->lo : c->hi;
        s += 10;
        for (i32 k = 0; k < 3; k++) { d[k] = q16(s, &f); s = f; }
    } else if (empieza(s, "LUT_1D") || empieza(s, "LUT_3D_INPUT")) {
        c->err = 1;
    } else if ((*s >= '0' && *s <= '9') || *s == '-' || *s == '+' || *s == '.') {
        if (!c->cube || c->filled >= c->n * c->n * c->n) { c->err = 1; return; }
        for (i32 k = 0; k < 3; k++) { c->cube[c->filled * 3 + k] = q16(s, &f); s = f; }
        c->filled++;
    }
    /* TITLE y demás cabeceras: ignoradas */
}

static void alimenta(struct ctx *c, const u8 *p, i32 n) {
    for (i32 i = 0; i < n && !c->err; i++) {
        if (p[i] == '\n') { linea(c); c->ll = 0; }
        else if (c->ll < (i32)sizeof c->line - 1) c->line[c->ll++] = (char)p[i];
    }
}

static i32 trilineal(const struct ctx *c, const i32 *x, i32 *out) {
    i32 i0[3], f[3];
    for (i32 k = 0; k < 3; k++) {
        i64 den = (i64)c->hi[k] - c->lo[k];
        i64 u = 0;
        if (den > 0 && x[k] > c->lo[k]) u = (i64)div64((u64)((i64)x[k] - c->lo[k]) << 16, (u64)den);
        if (u > 65536) u = 65536;
        u *= c->n - 1;
        i32 i = (i32)(u >> 16);
        if (i > c->n - 2) i = c->n - 2;
        i0[k] = i;
        f[k] = (i32)(u - ((i64)i << 16));
    }
    for (i32 ch = 0; ch < 3; ch++) {
        i64 acc = 0;
        for (i32 d = 0; d < 8; d++) {
            i32 dr = d & 1, dg = (d >> 1) & 1, db = (d >> 2) & 1;
            i64 w = ((dr ? f[0] : 65536 - f[0]) * (i64)(dg ? f[1] : 65536 - f[1])) >> 16;
            w = (w * (db ? f[2] : 65536 - f[2])) >> 16;
            i32 idx = (((i0[2] + db) * c->n + i0[1] + dg) * c->n + i0[0] + dr) * 3 + ch;
            acc += w * c->cube[idx];
        }
        out[ch] = (i32)(acc >> 16);
    }
    return 0;
}

static i32 clamp16(i32 v) { return v < 0 ? 0 : v > 65536 ? 65536 : v; }

static void ycc(const i32 *rgb, i32 *o) {
    i32 y = (i32)(((i64)19595 * rgb[0] + (i64)38470 * rgb[1] + (i64)7471 * rgb[2]) >> 16);
    o[0] = y;
    o[1] = (i32)(((i64)(rgb[2] - y) * 36984) >> 16);
    o[2] = (i32)(((i64)(rgb[0] - y) * 46743) >> 16);
}

static i32 satura(i32 q) { return q < -64 ? -64 : q > 63 ? 63 : q; }

/* 405 nodos j·81+a·9+b (Y, Cb, Cr) → 21 bits por nodo: (ΔY&127)<<14 | (ΔCb&127)<<7 | (ΔCr&127).
 * G90: muestreo directo de cada nodo (z en 1/16 de unidad s7, en `tmp`, libre hasta el final del barrido) y corrección de la proyección de mínimos cuadrados sobre
 * la base trilineal: v = z − Σ_ejes Δ²z/12 (Δ² solo con ambos vecinos; 21/256 ≈ 1/12), luego redondeo y saturación a s7. */
static void nodos(struct ctx *c, u8 *dst) {
    i32 *z = (i32 *)c->tmp;
    for (i32 i = 0; i < 405; i++) {
        i32 j = i / 81, a = (i / 9) % 9, b = i % 9;
        i32 y = j * 16384, cb = a * 8192 - 32768, cr = b * 8192 - 32768;
        i32 rgb[3], v[3], u[3], t[3];
        rgb[0] = clamp16(y + (i32)(((i64)91882 * cr) >> 16));
        rgb[2] = clamp16(y + (i32)(((i64)116131 * cb) >> 16));
        i32 n16 = (i32)((((i64)y << 16) - (i64)19595 * rgb[0] - (i64)7471 * rgb[2]) >> 16);
        rgb[1] = clamp16((i32)(((i64)n16 * 111642) >> 16));
        trilineal(c, rgb, v);
        ycc(rgb, u);
        ycc(v, t);
        z[3 * i] = (t[0] - u[0] + 8) >> 4;
        z[3 * i + 1] = (i32)(((i64)(t[1] - u[1]) * 5456 + 32768) >> 16);
        z[3 * i + 2] = (i32)(((i64)(t[2] - u[2]) * 5456 + 32768) >> 16);
    }
    u64 acc = 0;
    i32 nb = 0, pos = 0;
    for (i32 i = 0; i < 405; i++) {
        i32 j = i / 81, a = (i / 9) % 9, b = i % 9, q[3];
        for (i32 k = 0; k < 3; k++) {
            i32 *p = z + 3 * i + k, l = 0;
            if (j > 0 && j < 4) l += p[243] - 2 * *p + p[-243];
            if (a > 0 && a < 8) l += p[27] - 2 * *p + p[-27];
            if (b > 0 && b < 8) l += p[3] - 2 * *p + p[-3];
            q[k] = satura((*p - ((21 * l) >> 8) + 8) >> 4);
        }
        acc |= (u64)(((q[0] & 127) << 14) | ((q[1] & 127) << 7) | (q[2] & 127)) << nb;
        nb += 21;
        while (nb >= 8) { dst[pos++] = (u8)acc; acc >>= 8; nb -= 8; }
    }
    if (nb > 0 && pos < TAM_TABLA) dst[pos++] = (u8)acc;
    while (pos < TAM_TABLA) dst[pos++] = 0;
}

#define DIAG_OFF 0x2000 /* diagnóstico en el blob (lo ignora av-cam): 6×4 i32 de Fsys_Open por variante de ruta + 6 i32 del primer Fsys_Read ≤ 0; cabecera[14] = letra */
#define VARIANTES 4

/* Prueba `X:/LUT/LUTn.cube`, `X:\LUT\LUTn.cube` y las mismas con `.CUB` (8.3): no se sabe cuál acepta Fsys (g89 §4.3). */
static i32 abre(struct ctx *c, i32 slot, i32 *h) {
    for (i32 v = 0; v < VARIANTES; v++) {
        char path[24] = "X:/LUT/LUT1.cube";
        i32 r;
        path[0] = (char)c->drive;
        path[2] = path[6] = (v & 1) ? '\\' : '/';
        path[10] = (char)('1' + slot);
        if (v & 2) { path[12] = 'C'; path[13] = 'U'; path[14] = 'B'; path[15] = 0; }
        *h = -1;
        r = c->a.f_open(path, h, 1);
        c->diag[slot * VARIANTES + v] = (r >= 0 && *h < 0) ? -2 : r;
        if (r >= 0 && *h >= 0) return 1;
    }
    return 0;
}

static i32 lee_ranura(struct ctx *c, i32 slot, u8 *dst) {
    i32 h = -1, r, primera = 1;
    c->cube = 0; c->n = 0; c->filled = 0; c->ll = 0; c->err = 0;
    for (i32 k = 0; k < 3; k++) { c->lo[k] = 0; c->hi[k] = 65536; }
    if (!abre(c, slot, &h)) return 0;
    do {
        r = c->a.f_read(h, c->chunk, CHUNK);
        if (primera) { c->rd[slot] = r > 0 ? 0 : r; primera = 0; }
        if (r > 0) alimenta(c, c->chunk, r > CHUNK ? CHUNK : r);
    } while (r > 0 && !c->err);
    c->a.f_close(h);
    if (c->ll) { c->line[c->ll] = 0; linea(c); c->ll = 0; }
    i32 ok = !c->err && c->cube && c->filled == c->n * c->n * c->n;
    if (ok) nodos(c, dst);
    if (c->cube) c->a.m_free(c->cube);
    c->cube = 0;
    return ok;
}

static i32 letra_sd(struct ctx *c) {
    i32 l = c->a.f_drive("/dev/mmca");
    if (!(l >= 'A' && l <= 'z')) l = c->a.f_drive("/dev/msm");
    return l >= 'A' && l <= 'z' ? l : 0;
}

/* G95 (LUT-PKG-1): `X:/LUT/LUT<n>.LUT` precalculado en el PC (`lut_pkg.py`): cabecera de 16 B + tabla de 1064 B ya en el formato de la ranura.
 * La cámara no remuestrea nada: valida firma, versión, longitud y CRC32 y copia. */
#define PKG_MAGIC 0x544C3641u /* "A6LT" */
#define PKG_TAM (16 + TAM_TABLA)

static u32 le32(const u8 *p) { return p[0] | p[1] << 8 | p[2] << 16 | (u32)p[3] << 24; }

static u32 crc32(const u8 *p, i32 n) {
    u32 c = 0xFFFFFFFFu;
    for (i32 i = 0; i < n; i++) {
        c ^= p[i];
        for (i32 k = 0; k < 8; k++) c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1)));
    }
    return ~c;
}

i32 lutsd_paquete(const u8 *p, i32 n, u8 *dst) {
    if (n != PKG_TAM || le32(p) != PKG_MAGIC || p[4] != 1 || (p[6] | p[7] << 8) != TAM_TABLA || le32(p + 8) != crc32(p + 16, TAM_TABLA)) return 0;
    memcpy(dst, p + 16, TAM_TABLA);
    return 1;
}

static i32 lee_paquete(struct ctx *c, i32 slot, u8 *dst) {
    char path[24] = "X:/LUT/LUT1.LUT";
    i32 h = -1, r, n = 0;
    path[0] = (char)c->drive;
    path[10] = (char)('1' + slot);
    if (c->a.f_open(path, &h, 1) < 0 || h < 0) return 0;
    do {                                   /* lee hasta PKG_TAM + 1 en tmp (libre durante el barrido): un byte de más delata un fichero largo */
        r = c->a.f_read(h, c->tmp + n, PKG_TAM + 1 - n);
        if (r > 0) n += r;
    } while (r > 0 && n <= PKG_TAM);
    c->a.f_close(h);
    return lutsd_paquete(c->tmp, n, dst);
}

/* Un barrido: lee las ranuras, arma el blob y lo escribe en el Backup solo si cambia. Devuelve nº de ranuras válidas (-1: sin tarjeta). */
i32 lutsd_barrido(struct ctx *c) {
    i32 nv = 0, letra = letra_sd(c);
    if (!letra) return -1;
    c->drive = letra;
    zero(c->blob, BK_TAM);
    *(u32 *)c->blob = MAGIC;
    c->blob[4] = 1;
    c->blob[6] = SLOTS;
    c->blob[14] = (u8)letra;
    zero(c->diag, sizeof c->diag); zero(c->rd, sizeof c->rd);
    for (i32 s = 0; s < SLOTS; s++)
        if (lee_paquete(c, s, c->blob + 16 + s * TAM_TABLA) || lee_ranura(c, s, c->blob + 16 + s * TAM_TABLA)) { c->blob[8 + s] = 1; nv++; }
    for (i32 i = 0; i < 24; i++) *(i32 *)(c->blob + DIAG_OFF + 4 * i) = c->diag[i];
    for (i32 i = 0; i < 6; i++) *(i32 *)(c->blob + DIAG_OFF + 96 + 4 * i) = c->rd[i];
    if (c->a.b_read(BK_ID, c->tmp) >= 0) {
        i32 igual = 1;
        for (i32 i = 0; i < BK_TAM && igual; i++) igual = c->blob[i] == c->tmp[i];
        if (igual) return nv;
    }
    c->a.b_write(BK_ID >> 16, BK_ID, c->blob);
    return nv;
}

/* Un paso del sondeo (cada 5 s): barre al aparecer la tarjeta; `*con` recuerda si estaba. Separado del bucle para probarlo. */
i32 lutsd_paso(struct ctx *c, i32 *con) {
    i32 r = 0;
    if (letra_sd(c)) { if (!*con) r = 1 + lutsd_barrido(c); *con = 1; }
    else *con = 0;
    return r;
}

/* Entrada del hilo (pthread_create(&t, 0, lutsd_hilo, 0)): reúne las funciones con `dlsym` (`dl`) y sondea para siempre. */
typedef void *(*dlsym_t)(void *, const char *);
void *lutsd_hilo(dlsym_t dl) {
    struct ctx *c;
    i32 con = 0;
    void *(*ma)(u32) = dl(0, "malloc");
    void *(*h)(const char *, i32) = dl(0, "dlopen");
    void *fs, *bk;
    if (!ma || !h) return 0;
    fs = h("libInfraFsys.so", 1);
    bk = h("libbackup.so", 1);
    if (!fs || !bk) return 0;
    c = ma(sizeof *c);
    if (!c) return 0;
    zero(c, sizeof *c);
    c->a.m_alloc = ma;
    c->a.m_free = dl(0, "free");
    c->a.s_sleep = dl(0, "sleep");
    c->a.f_open = dl(fs, "Fsys_Open");
    c->a.f_read = dl(fs, "Fsys_Read");
    c->a.f_close = dl(fs, "Fsys_Close");
    c->a.f_drive = dl(fs, "Fsys_GetDriveLetter");
    c->a.b_read = dl(bk, "Backup_read");
    c->a.b_write = dl(bk, "Backup_write");
    if (!c->a.m_free || !c->a.s_sleep || !c->a.f_open || !c->a.f_read || !c->a.f_close || !c->a.f_drive || !c->a.b_read || !c->a.b_write) return 0;
    for (;;) {
        lutsd_paso(c, &con);
        c->a.s_sleep(5);
    }
}
