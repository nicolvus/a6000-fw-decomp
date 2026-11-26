/* nf4inject.so — inyección para el arnés G22 con /dev/nflasha4 real emulado (NFLASH4=1).
 *
 * Se precarga ADEMÁS de sonyshim.so (LD_PRELOAD="/usr/lib/sonyshim.so /usr/lib/nf4inject.so"),
 * así que no toca el shim del arnés: sólo usa dlsym(RTLD_DEFAULT) y desplazamientos de libmpr.
 *
 * NF4INJECT=<s>: a los s segundos (y tras esperar a que FBM::Init llene la tabla):
 *   A) base de libmpr y espera a que 0xA3699C tenga los 30 nombres (0x10..0xbd)
 *   B) volcado de 0xA3699C (30 × 0x14 B)                        — «antes»
 *   C) volcado EN VIVO de la tabla estática 0x9D23FC (37 × 0x18: userID, mediaID, fileType, OM, fn, arg)
 *   D) 0x2B3000(OM,media,&handle) — el primer paso de WriteBaseData — para (6,3) y (9,8) de control
 *   E) BackupMgr::InitBackupData(6,3) por dirección (0x2B43F0): el código exacto que devuelve InitB
 *   F) `FBM View` y `FBM InitB 6 3` por el handler REAL del módulo (0x2B50D8) + volcado «después»
 *   G) criterio idx 10 (0x31): handle != 0 y +8 == 1
 *   H) si sigue sin handle: CreateSector32(0x31) por símbolo + GetErrorString del código
 *   I) diferencia byte a byte entre /nflasha4.img (copia del invitado) y /usr/share/nflasha4.img
 *   J) BkRead 0x2B39B8 — el camino de RcsBackupTblData — para (0x04,3) y (0x21,3)
 *   K) SINTÉTICO: `FBM SetSMI 10 31 3 1 6` (alta directa en 0xA3699C, sin NAND) y BkRead(0x04,3)
 *      otra vez, para ver qué devuelve la lectura cuando la entrada SÍ tiene handle
 *   L) «[FBMC] FIN» (el lanzador corta la VM con esa marca)
 *
 * Convención del monitor (0x6822F8/0x682230): argc cuenta la línea ENTERA con el nombre del
 * módulo y argv[0] es ese nombre; el handler del módulo hace argc-1/argv+1.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

static int cfd = -2;
static void out(const char *f, ...) {
    char b[460]; va_list v; va_start(v, f); int n = vsnprintf(b, sizeof b, f, v); va_end(v);
    if (n <= 0) return;
    if (n > (int)sizeof b - 1) n = sizeof b - 1;
    if (cfd == -2) cfd = open("/dev/console", O_WRONLY | O_NOCTTY);
    if (cfd >= 0) { ssize_t r = write(cfd, b, n); (void)r; }
    { ssize_t r = write(2, b, n); (void)r; }
}

static unsigned long fbm_base;
static unsigned char *tab(void) { return (unsigned char *)(fbm_base + 0xa3699c); }
static unsigned rdu(unsigned char *p) { unsigned v; memcpy(&v, p, 4); return v; }
static unsigned rds(unsigned char *p) { unsigned short v; memcpy(&v, p, 2); return v; }

/* 30 entradas de 0x14 B: {u16 nombre(sector)|u16 ?, u32 handle, u32 estado, u32 OM, u32 ?} */
static void dump(const char *tag) {
    unsigned char *t = tab();
    int n = 0;
    for (int i = 0; i < 30; i++) if (rdu(t + i * 0x14 + 4)) n++;
    out("[NF4] %s  handle!=0 = %d/30\n", tag, n);
    for (int m = 0; m < 2; m++) {
        char lin[380]; int o = 0;
        for (int i = m * 15; i < m * 15 + 15; i++) {
            o += snprintf(lin + o, sizeof lin - o, "%02d:%03x=h%x/s%x/om%x ", i,
                          rds(t + i * 0x14) & 0xfff, rdu(t + i * 0x14 + 4),
                          rdu(t + i * 0x14 + 8), rdu(t + i * 0x14 + 0xc));
        }
        lin[o] = 0;
        out("[NF4] %s [%02d..%02d]  %s\n", tag, m * 15, m * 15 + 14, lin);
    }
}

/* Tabla estática {u32 userID, u32 mediaID, u32 fileType, u32 OM, void *fn, void *arg} de 0x18 B;
 * 0x2B3000 la recorre y SALTA las entradas con fn == 0 (0x2B301A: cbz r2). */
static void tabla_estatica(void) {
    unsigned char *t = (unsigned char *)(fbm_base + 0x9d23fc);
    for (int k = 0; k < 38; k += 2) {
        char lin[380]; int o = 0;
        for (int j = k; j < k + 2 && j < 38; j++) {
            unsigned char *e = t + j * 0x18;
            o += snprintf(lin + o, sizeof lin - o, "[%02d]u%02x/m%u/ft%03x/om%x/fn%x/arg%x ",
                          j, rdu(e), rdu(e + 4), rdu(e + 8), rdu(e + 0xc), rdu(e + 0x10), rdu(e + 0x14));
        }
        lin[o] = 0;
        out("[NF4] tabla 0x9D23FC: %s\n", lin);
    }
}

static int fbm_cmd(const char *line) {
    char buf[128]; char *av[13]; int ac = 0;
    strncpy(buf, line, sizeof buf - 1); buf[sizeof buf - 1] = 0;
    av[ac++] = "FBM";
    for (char *p = buf; *p && ac < 12; ) {
        while (*p == ' ') *p++ = 0;
        if (!*p) break;
        av[ac++] = p;
        while (*p && *p != ' ') p++;
    }
    int (*h)(long, char **) = (void *)(fbm_base + 0x2b50d8 + 1);   /* 0x2B50D8 | 1 (Thumb) */
    out("[NF4] MON> FBM %s   (argc=%d, al comando=%d)\n", line, ac, ac - 1);
    int r = h(ac, av);
    out("[NF4] FBM %s -> %d\n", line, r);
    return r;
}

static const char *errstr(unsigned c) {
    const char *(*ges)(unsigned) = (void *)dlsym(RTLD_DEFAULT, "_ZN8FlashLib14GetErrorStringEm");
    return ges ? ges(c) : "?";
}

static unsigned buscar(unsigned om, unsigned media) {
    unsigned (*f)(unsigned, unsigned, unsigned *) = (void *)(fbm_base + 0x2b3000 + 1);
    unsigned h = 0xdeadbeef;
    unsigned r = f(om, media, &h);
    out("[NF4] 0x2B3000(OM=%u,media=%u,&h) -> ret=%#x handle=%#x  «%s»\n", om, media, r, h,
        r ? errstr(r) : "sin error");
    return r;
}

static unsigned backup_init(unsigned om, unsigned media) {
    unsigned (*f)(unsigned, unsigned) = (void *)(fbm_base + 0x2b43f0 + 1);
    unsigned r = f(om, media);
    out("[NF4] BackupMgr::InitBackupData(%u,%u) -> %#x  «%s»\n", om, media, r, r ? errstr(r) : "sin error");
    return r;
}

/* BkRead 0x2B39B8(userID, mediaID, &byte, &u32, &stack5, &entrada): si la entrada de 0xA3699C
 * no tiene handle devuelve 0x10100001 sin tocar nada; si lo tiene, llama a ReadFirstPackData. */
static unsigned leer(unsigned user, unsigned media) {
    unsigned (*bkread)(unsigned, unsigned, void *, void *, void *, void *) = (void *)(fbm_base + 0x2b39b8 + 1);
    unsigned char b3[0x40], b5[0x40], ent[0x40]; unsigned b4[0x40];
    memset(b3, 0, sizeof b3); memset(b4, 0, sizeof b4);
    memset(b5, 0, sizeof b5); memset(ent, 0xcc, sizeof ent);
    out("[NF4] BkRead(%#04x,%u) ...\n", user, media);          /* marca ANTES: si bloquea, se ve dónde */
    unsigned r = bkread(user, media, b3, b4, b5, ent);
    out("[NF4] BkRead(%#04x,%u) -> %#010x   entrada: sec=%#x h=%#x est=%#x om=%#x\n",
        user, media, r, rds(ent) & 0xfff, rdu(ent + 4), rdu(ent + 8), rdu(ent + 0xc));
    return r;
}

/* Diferencia byte a byte entre la copia escribible del invitado y la imagen de origen. */
static long comparar_imagenes(const char *tag) {
    int a = open("/usr/share/nflasha4.img", O_RDONLY), b = open("/nflasha4.img", O_RDONLY);
    if (a < 0 || b < 0) {
        out("[NF4] imagen(%s): origen fd=%d copia fd=%d (falta alguna)\n", tag, a, b);
        if (a >= 0) close(a);
        if (b >= 0) close(b);
        return -1;
    }
    long la = (long)lseek(a, 0, SEEK_END), lb = (long)lseek(b, 0, SEEK_END);
    lseek(a, 0, SEEK_SET); lseek(b, 0, SEEK_SET);
    static unsigned char x[65536], y[65536];
    long o = 0, difs = 0, primero = -1, ultimo = -1;
    for (;;) {
        ssize_t na = read(a, x, sizeof x), nb = read(b, y, sizeof y);
        if (na <= 0 && nb <= 0) break;
        long n = na > nb ? (long)na : (long)nb;
        if (na < n) memset(x + (na > 0 ? na : 0), 0, (size_t)(n - (na > 0 ? na : 0)));
        if (nb < n) memset(y + (nb > 0 ? nb : 0), 0, (size_t)(n - (nb > 0 ? nb : 0)));
        for (long i = 0; i < n; i++) if (x[i] != y[i]) {
            difs++; if (primero < 0) primero = o + i; ultimo = o + i;
        }
        o += n;
    }
    close(a); close(b);
    out("[NF4] imagen(%s): origen=%ld B copia=%ld B; bytes distintos=%ld; primero=%ld (%#lx) ultimo=%ld (%#lx)\n",
        tag, la, lb, difs, primero, (unsigned long)primero, ultimo, (unsigned long)ultimo);
    return primero;
}

/* Página de 1 KiB de /nflasha4.img en hexadecimal (16 líneas de 64 B), para poder reconstruirla. */
static void pagina_hex(const char *tag, long off) {
    int b = open("/nflasha4.img", O_RDONLY);
    if (b < 0) { out("[NF4] pagina(%s): sin copia\n", tag); return; }
    static unsigned char p[0x400];
    if (pread(b, p, sizeof p, off) != (ssize_t)sizeof p) { out("[NF4] pagina(%s): lectura corta\n", tag); close(b); return; }
    close(b);
    out("[NF4] pagina(%s) de /nflasha4.img en %#lx:\n", tag, (unsigned long)off);
    for (int i = 0; i < 0x400; i += 32) {
        char lin[100]; int o = 0;
        for (int j = 0; j < 32; j++) o += snprintf(lin + o, sizeof lin - o, "%02x", p[i + j]);
        out("[NF4] PG %03x %s\n", i, lin);
    }
}

static void *worker(void *a) {
    unsigned s = (unsigned)(unsigned long)a;
    if (s) sleep(s);
    void *sym = 0;
    for (int i = 0; i < 480 && !sym; i++) {          /* hasta 240 s: libmpr se carga con dlopen */
        sym = dlsym(RTLD_DEFAULT, "_ZN8FlashLib12CreateSectorEt12FBS_MOVEFLAGPmPt");
        if (!sym) usleep(500000);
    }
    Dl_info di;
    if (!sym || !dladdr(sym, &di)) { out("[NF4] sin símbolo de FlashLib: libmpr no cargada\n[FBMC] FIN\n"); return 0; }
    fbm_base = (unsigned long)di.dli_fbase;
    out("[NF4] base libmpr=%#lx tabla sectores=%#lx (0xA3699C)\n", fbm_base, fbm_base + 0xa3699c);

    int listo = 0;                                    /* FBM::Init (0x2B4820): 1ª = 0x10, última = 0xbd */
    for (int i = 0; i < 240; i++) {
        if ((rds(tab()) & 0xfff) == 0x10 && (rds(tab() + 29 * 0x14) & 0xfff) == 0xbd) { listo = 1; break; }
        usleep(500000);
    }
    out("[NF4] tabla %s (nombres 0x10..0xbd)\n", listo ? "LLENA" : "SIN llenar: sigo igual");
    sleep(3);

    const char *modo = getenv("NF4MODE");

    if (modo && !strcmp(modo, "ver")) {           /* imagen ya con el sector 0x31: sólo mirar y leer */
        dump("tras-arranque");
        comparar_imagenes("inicio");
        {
            unsigned char *e = tab() + 10 * 0x14;
            out("[NF4] CRITERIO idx10 sec=%#x handle=%#x +8=%#x => %s\n", rds(e) & 0xfff, rdu(e + 4), rdu(e + 8),
                (rdu(e + 4) && rdu(e + 8) == 1) ? "OK" : "FALLA");
        }
        leer(0x04, 3);
        leer(0x21, 3);
        comparar_imagenes("fin");
        out("[FBMC] FIN\n");
        return 0;
    }

    if (modo && !strcmp(modo, "b21h")) {          /* (0x21,3) con handle: crear 0x31 + SetSMI y leer */
        unsigned (*cs32b)(unsigned, int, unsigned *, unsigned *) =
            (void *)dlsym(RTLD_DEFAULT, "_ZN8FlashLib14CreateSector32Em12FBS_MOVEFLAGPmS1_");
        unsigned h = 0, id = 0;
        dump("antes");
        if (cs32b) {
            unsigned r = cs32b(0x31, 0, &h, &id);
            out("[NF4] CreateSector32(0x31) -> ret=%#x handle=%u id=%#x\n", r, h, id & 0xffff);
        }
        {
            char l[40];
            snprintf(l, sizeof l, "SetSMI 10 31 %u 1 6", h);
            fbm_cmd(l);
        }
        dump("tras-SetSMI");
        leer(0x21, 3);
        leer(0x04, 3);
        comparar_imagenes("fin");
        out("[FBMC] FIN\n");
        return 0;
    }

    if (modo && !strcmp(modo, "b21")) {           /* sólo la lectura de (0x21,3), la primera del proceso */
        dump("antes");
        leer(0x21, 3);
        out("[FBMC] FIN\n");
        return 0;
    }

    dump("antes");
    comparar_imagenes("inicio");
    tabla_estatica();
    buscar(6, 3);
    buscar(9, 8);

    fbm_cmd("View");
    fbm_cmd("InitB 6 3");            /* (OM 6 = M2PS, mediaID 3 = MS1) -> fileType 0x31, idx 10 */
    dump("despues-InitB-6-3");

    {
        unsigned char *e = tab() + 10 * 0x14;
        out("[NF4] CRITERIO idx10 sec=%#x handle=%#x +8=%#x => %s\n", rds(e) & 0xfff, rdu(e + 4), rdu(e + 8),
            (rdu(e + 4) && rdu(e + 8) == 1) ? "OK" : "FALLA");
    }

    long dif = comparar_imagenes("tras-InitB");
    if (dif >= 0) pagina_hex("tras-InitB", dif & ~0x3ffL);

    {   /* CreateSector32 por símbolo: mide el FBS sin pasar por 0x2B3000 */
        unsigned (*cs32)(unsigned, int, unsigned *, unsigned *) =
            (void *)dlsym(RTLD_DEFAULT, "_ZN8FlashLib14CreateSector32Em12FBS_MOVEFLAGPmS1_");
        if (cs32) {
            unsigned h = 0xdead, id = 0xdead;
            unsigned r = cs32(0x31, 0, &h, &id);
            out("[NF4] CreateSector32(0x31, 0, &handle, &id) -> ret=%#x handle=%#x id=%#x  «%s»\n",
                r, h, id & 0xffff, errstr(r));
        } else out("[NF4] sin símbolo CreateSector32\n");
    }
    dif = comparar_imagenes("tras-CreateSector32");
    if (dif >= 0) pagina_hex("tras-CreateSector32", dif & ~0x3ffL);

    /* SINTÉTICO (no crea nada en NAND): alta directa en la tabla para ver la lectura con handle */
    fbm_cmd("SetSMI 10 31 3 1 6");
    dump("tras-SetSMI-sintetico");

    dump("antes-de-BkRead");
    leer(0x04, 3);                   /* con handle: ya pasa de 0x10100001 a ReadFirstPackData 0x2B3948 */

    comparar_imagenes("fin");
    out("[FBMC] FIN\n");
    return 0;
}

__attribute__((constructor)) static void nf4_init(void) {
    const char *e = getenv("NF4INJECT");
    if (!e) return;
    unsigned s = 0;                                  /* atoi a mano: la libc 2.11 no tiene __isoc23_strtol */
    while (*e >= '0' && *e <= '9') s = s * 10 + (unsigned)(*e++ - '0');
    pthread_t th;
    if (pthread_create(&th, 0, worker, (void *)(unsigned long)s) == 0) pthread_detach(th);
}
