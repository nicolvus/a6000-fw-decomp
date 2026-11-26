/* nf6inject.so — 2º .so precargado para el arnés G22 con /dev/nflasha4 real emulado (NFLASH4=1).
 *
 * Igual que reports/evidence/fbm-initb-6-3-nflasha4-20261126/nf4inject.c, pero dedicado a la
 * pregunta «¿qué comando de consola deja el sector 0x31 registrado en 0xA3699C con handle?».
 *
 * Se precarga ADEMÁS de sonyshim.so (LD_PRELOAD="/usr/lib/sonyshim.so /usr/lib/nf6inject.so"),
 * así que no toca el shim: usa dlsym(RTLD_DEFAULT) y desplazamientos de libmpr (VA del ELF).
 *
 * Modos (NF4MODE):
 *   orden   : ejecuta, en el orden pedido, `ChgSec 6 3`, `ChgSec 4 3`, `CRFB`, `INRFB`, `DRWBI`,
 *             `WBI` por el handler REAL del módulo (0x2B50D8) y vuelca la tabla 0xA3699C + el
 *             diff de /nflasha4.img después de cada uno; al final BkRead(0x04,3)  [defecto]
 *   ewbdfd  : `EWBDFD 4 3 0` (alta de la función de escritura dummy en 0x9D23FC) + `InitB 6 3`;
 *             criterio idx 10; BkRead(0x04,3); y luego FBM::Init (0x2B4820) otra vez como proxy
 *             de «reiniciar MPR» (relee el flash y reconstruye la tabla)
 *   ewchg   : igual que ewbdfd pero con `ChgSec 4 3` en vez de `InitB 6 3`
 *   ver     : sólo mira (para la 2ª pasada con la imagen ya parcheada): tabla, criterio, BkRead
 *
 * Convención del monitor (0x6822F8/0x682230): argc cuenta la línea ENTERA con el nombre del
 * módulo y argv[0] es ese nombre; el handler hace argc-1/argv+1.
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

/* 30 entradas de 0x14 B: {u16 nombre(sector), u16 ?, u32 handle, u32 estado, u32 OM, u32 ?} */
static void dump(const char *tag) {
    unsigned char *t = tab();
    int n = 0;
    for (int i = 0; i < 30; i++) if (rdu(t + i * 0x14 + 4)) n++;
    out("[NF6] %s  handle!=0 = %d/30\n", tag, n);
    for (int m = 0; m < 2; m++) {
        char lin[380]; int o = 0;
        for (int i = m * 15; i < m * 15 + 15; i++) {
            o += snprintf(lin + o, sizeof lin - o, "%02d:%03x=h%x/s%x/om%x ", i,
                          rds(t + i * 0x14) & 0xfff, rdu(t + i * 0x14 + 4),
                          rdu(t + i * 0x14 + 8), rdu(t + i * 0x14 + 0xc));
        }
        lin[o] = 0;
        out("[NF6] %s [%02d..%02d]  %s\n", tag, m * 15, m * 15 + 14, lin);
    }
    {
        unsigned char *e = t + 10 * 0x14;
        out("[NF6] CRITERIO idx10 sec=%#x handle=%#x +8=%#x => %s\n", rds(e) & 0xfff, rdu(e + 4), rdu(e + 8),
            (rdu(e + 4) && rdu(e + 8) == 1) ? "OK" : "FALLA");
    }
}

/* Tabla estática {u32 userID, mediaID, fileType, OM, void *fn, void *arg} de 0x18 B.
 * 0x2B3000 la recorre y SALTA las entradas con fn == 0 (0x2B301A: cbz r2). */
static void tabla_estatica(const char *tag) {
    unsigned char *t = (unsigned char *)(fbm_base + 0x9d23fc);
    for (int k = 0; k < 38; k += 2) {
        char lin[380]; int o = 0;
        for (int j = k; j < k + 2 && j < 38; j++) {
            unsigned char *e = t + j * 0x18;
            o += snprintf(lin + o, sizeof lin - o, "[%02d]u%02x/m%u/ft%03x/om%x/fn%x/arg%x ",
                          j, rdu(e), rdu(e + 4), rdu(e + 8), rdu(e + 0xc), rdu(e + 0x10), rdu(e + 0x14));
        }
        lin[o] = 0;
        out("[NF6] 0x9D23FC(%s): %s\n", tag, lin);
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
    out("[NF6] MON> FBM %s   (argc=%d, al comando=%d)\n", line, ac, ac - 1);
    int r = h(ac, av);
    out("[NF6] FBM %s -> %d\n", line, r);
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
    out("[NF6] 0x2B3000(OM=%u,media=%u,&h) -> ret=%#x handle=%#x  «%s»\n", om, media, r, h,
        r ? errstr(r) : "sin error");
    return r;
}

/* BkRead 0x2B39B8(userID, mediaID, &byte, &u32, &stack5, &entrada): si la entrada de 0xA3699C
 * no tiene handle devuelve 0x10100001 sin tocar nada; si lo tiene, llama a ReadFirstPackData. */
static unsigned leer(unsigned user, unsigned media) {
    unsigned (*bkread)(unsigned, unsigned, void *, void *, void *, void *) = (void *)(fbm_base + 0x2b39b8 + 1);
    unsigned char b3[0x40], b5[0x40], ent[0x40]; unsigned b4[0x40];
    memset(b3, 0, sizeof b3); memset(b4, 0, sizeof b4);
    memset(b5, 0, sizeof b5); memset(ent, 0xcc, sizeof ent);
    out("[NF6] BkRead(%#04x,%u) ...\n", user, media);
    unsigned r = bkread(user, media, b3, b4, b5, ent);
    out("[NF6] BkRead(%#04x,%u) -> %#010x   entrada: sec=%#x h=%#x est=%#x om=%#x\n",
        user, media, r, rds(ent) & 0xfff, rdu(ent + 4), rdu(ent + 8), rdu(ent + 0xc));
    return r;
}

/* Diferencia byte a byte entre la copia escribible del invitado y la imagen de origen. */
static long comparar_imagenes(const char *tag) {
    int a = open("/usr/share/nflasha4.img", O_RDONLY), b = open("/nflasha4.img", O_RDONLY);
    if (a < 0 || b < 0) {
        out("[NF6] imagen(%s): origen fd=%d copia fd=%d (falta alguna)\n", tag, a, b);
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
    out("[NF6] imagen(%s): origen=%ld B copia=%ld B; bytes distintos=%ld; primero=%ld (%#lx) ultimo=%ld (%#lx)\n",
        tag, la, lb, difs, primero, (unsigned long)primero, ultimo, (unsigned long)ultimo);
    return primero;
}

/* Rangos modificados de la copia del invitado, en hex, para poder reconstruir la imagen en el
 * host y repetir el arranque (la copia vive dentro del invitado y no se puede sacar de otra forma).
 * 1ª pasada: localiza los tramos distintos; para cada tramo, `pread` del contenido nuevo. */
static void volcar_diff(const char *tag) {
    int a = open("/usr/share/nflasha4.img", O_RDONLY), b = open("/nflasha4.img", O_RDONLY);
    if (a < 0 || b < 0) { out("[NF6] diff(%s): falta alguna imagen\n", tag); if (a>=0) close(a); if (b>=0) close(b); return; }
    static unsigned char x[4096], y[4096];
    long o = 0, total = 0, desde = -1, ultimo = -1;
    out("[NF6] diff-hex(%s): contenido nuevo de los tramos modificados de /nflasha4.img\n", tag);
    for (;;) {
        ssize_t na = read(a, x, sizeof x), nb = read(b, y, sizeof y);
        if (na <= 0 && nb <= 0) break;
        long n = na > nb ? (long)na : (long)nb;
        for (long i = 0; i < n; i++) {
            int dif = (i >= na || i >= nb) ? 1 : (x[i] != y[i]);
            if (dif) { if (desde < 0) desde = o + i; ultimo = o + i; }
            else if (desde >= 0) { total += ultimo - desde + 1; desde = -1; }
        }
        o += n;
    }
    if (desde >= 0) total += ultimo - desde + 1;
    out("[NF6] diff-hex(%s): %ld B distintos\n", tag, total);
    /* 2ª pasada: por tramos, imprimir offset/longitud y el contenido nuevo */
    lseek(a, 0, SEEK_SET); lseek(b, 0, SEEK_SET); o = 0; desde = -1; ultimo = -1;
    static unsigned char buf[4096];
    for (;;) {
        ssize_t na = read(a, x, sizeof x), nb = read(b, y, sizeof y);
        if (na <= 0 && nb <= 0) break;
        long n = na > nb ? (long)na : (long)nb;
        for (long i = 0; i < n; i++) {
            int dif = (i >= na || i >= nb) ? 1 : (x[i] != y[i]);
            if (dif) { if (desde < 0) desde = o + i; ultimo = o + i; }
            else if (desde >= 0) {
                long L = ultimo - desde + 1;
                out("[NF6] DIFF %#lx %ld\n", (unsigned long)desde, L);
                for (long j = 0; j < L; ) {
                    long m = L - j > 32 ? 32 : L - j;
                    if (pread(b, buf, (size_t)m, (off_t)(desde + j)) != (ssize_t)m) break;
                    char lin[100]; int q = 0;
                    for (long k = 0; k < m; k++) q += snprintf(lin + q, sizeof lin - q, "%02x", buf[k]);
                    out("[NF6] DIFFB %#lx %s\n", (unsigned long)(desde + j), lin);
                    j += m;
                }
                desde = -1;
            }
        }
        o += n;
    }
    close(a); close(b);
}

/* Página de 1 KiB de /nflasha4.img en hexadecimal (32 líneas de 32 B). */
static void pagina_hex(const char *tag, long off) {
    int b = open("/nflasha4.img", O_RDONLY);
    if (b < 0) { out("[NF6] pagina(%s): sin copia\n", tag); return; }
    static unsigned char p[0x400];
    if (pread(b, p, sizeof p, off) != (ssize_t)sizeof p) { out("[NF6] pagina(%s): lectura corta\n", tag); close(b); return; }
    close(b);
    out("[NF6] pagina(%s) de /nflasha4.img en %#lx:\n", tag, (unsigned long)off);
    for (int i = 0; i < 0x400; i += 32) {
        char lin[100]; int o = 0;
        for (int j = 0; j < 32; j++) o += snprintf(lin + o, sizeof lin - o, "%02x", p[i + j]);
        out("[NF6] PG %03x %s\n", i, lin);
    }
}

/* FBM::Init 0x2B4820: reconstruye 0xA3699C desde el flash (CheckExistSector==0x45).
 * Volver a llamarla en el mismo proceso es el proxy de «reiniciar MPR». */
static void __attribute__((unused)) fbm_init_otra_vez(const char *tag) {
    void (*f)(void) = (void *)(fbm_base + 0x2b4820 + 1);
    out("[NF6] FBM::Init (0x2B4820) otra vez [%s] ...\n", tag);
    f();
    out("[NF6] FBM::Init otra vez [%s] hecho\n", tag);
    dump(tag);
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
    if (!sym || !dladdr(sym, &di)) { out("[NF6] sin símbolo de FlashLib: libmpr no cargada\n[FBMC] FIN\n"); return 0; }
    fbm_base = (unsigned long)di.dli_fbase;
    out("[NF6] base libmpr=%#lx tabla sectores=%#lx (0xA3699C)\n", fbm_base, fbm_base + 0xa3699c);

    int listo = 0;                                    /* FBM::Init: 1ª = 0x10, última = 0xbd */
    for (int i = 0; i < 240; i++) {
        if ((rds(tab()) & 0xfff) == 0x10 && (rds(tab() + 29 * 0x14) & 0xfff) == 0xbd) { listo = 1; break; }
        usleep(500000);
    }
    out("[NF6] tabla %s (nombres 0x10..0xbd)\n", listo ? "LLENA" : "SIN llenar: sigo igual");
    sleep(3);

    const char *modo = getenv("NF4MODE");

    if (modo && (!strcmp(modo, "ewbdfd") || !strcmp(modo, "ewchg"))) {
        int chg = !strcmp(modo, "ewchg");
        dump("antes");
        comparar_imagenes("inicio");
        tabla_estatica("antes");
        buscar(6, 3);
        fbm_cmd("EWBDFD 4 3 0");                 /* (user 4, media 3, p_arg=0) -> fn=0x2B5185 */
        tabla_estatica("tras-EWBDFD");
        buscar(6, 3);                            /* el lookup ya debe encontrar (6,3) */
        if (chg) fbm_cmd("ChgSec 4 3");          /* ruta ChangeSector (usa WriteBaseData igual) */
        else     fbm_cmd("InitB 6 3");           /* ruta InitBackupData -> WriteBaseData */
        dump(chg ? "tras-ChgSec-4-3" : "tras-InitB-6-3");
        comparar_imagenes(chg ? "tras-ChgSec" : "tras-InitB");
        buscar(6, 3);                            /* ahora handle != 0: el sector ya está alto */
        leer(0x04, 3);                           /* CRITERIO real: != 0x10100001 */
        dump("tras-BkRead");
        comparar_imagenes("fin");
        volcar_diff("fin");
        /* proxy de reinicio de MPR: WBI borra 0xA3699C y la reconstruye con
         * CheckExistSector (0x2B4680) — es la misma rutina que FBM::Init (0x2B4820). */
        fbm_cmd("WBI");
        dump("tras-WBI-reconstruccion");
        out("[FBMC] FIN\n");
        return 0;
    }

    if (modo && !strcmp(modo, "ltc")) {           /* ruta «oficial»: LTC_01 + InitB */
        dump("antes");
        comparar_imagenes("inicio");
        buscar(6, 3);
        fbm_cmd("LTC 1");                        /* LTC_01: alta dummy (4,3) (0x21,3) (4,4) (0x21,4) */
        tabla_estatica("tras-LTC-1");
        buscar(6, 3);
        fbm_cmd("InitB 6 3");
        dump("tras-InitB-6-3");
        comparar_imagenes("tras-InitB");
        buscar(6, 3);
        leer(0x04, 3);
        dump("tras-BkRead");
        volcar_diff("fin");
        fbm_cmd("WBI");
        dump("tras-WBI-reconstruccion");
        comparar_imagenes("fin");
        out("[FBMC] FIN\n");
        return 0;
    }

    if (modo && !strcmp(modo, "ver")) {
        dump("tras-arranque");
        comparar_imagenes("inicio");
        leer(0x04, 3);
        fbm_init_otra_vez("tras-FBM::Init-remake");
        comparar_imagenes("fin");
        out("[FBMC] FIN\n");
        return 0;
    }

    /* ---- modo por defecto: `orden` (los comandos de la tarea, uno a uno) ---- */
    dump("antes");
    comparar_imagenes("inicio");
    tabla_estatica("antes");

    fbm_cmd("ChgSec 6 3");                       /* userID 6 = no existe en 0x9D23FC */
    dump("tras-ChgSec-6-3");
    comparar_imagenes("tras-ChgSec-6-3");
    buscar(6, 3);
    {   /* valor que imprime INRFB, medido por símbolo (su salida va por osal, no por consola) */
        int (*inr)(void) = (void *)dlsym(RTLD_DEFAULT, "_ZN8FlashLib23IsNeedRepairFlashBackupEv");
        if (inr) out("[NF6] IsNeedRepairFlashBackup() por símbolo -> %d\n", inr());
    }

    fbm_cmd("ChgSec 4 3");                       /* userID 4 = dueño de 0x31 (u04/m3/ft031/om6) */
    dump("tras-ChgSec-4-3");
    comparar_imagenes("tras-ChgSec-4-3");
    buscar(6, 3);

    fbm_cmd("CRFB");
    dump("tras-CRFB");
    comparar_imagenes("tras-CRFB");
    tabla_estatica("tras-CRFB");
    buscar(6, 3);

    fbm_cmd("INRFB");
    dump("tras-INRFB");
    comparar_imagenes("tras-INRFB");

    fbm_cmd("DRWBI");
    dump("tras-DRWBI");
    comparar_imagenes("tras-DRWBI");

    fbm_cmd("WBI");
    dump("tras-WBI");
    comparar_imagenes("tras-WBI");
    buscar(6, 3);

    leer(0x04, 3);
    dump("fin");
    comparar_imagenes("fin");
    out("[FBMC] FIN\n");
    return 0;
}

__attribute__((constructor)) static void nf6_init(void) {
    const char *e = getenv("NF4INJECT");
    if (!e) return;
    unsigned s = 0;                                  /* atoi a mano: la libc 2.11 no tiene __isoc23_strtol */
    while (*e >= '0' && *e <= '9') s = s * 10 + (unsigned)(*e++ - '0');
    pthread_t th;
    if (pthread_create(&th, 0, worker, (void *)(unsigned long)s) == 0) pthread_detach(th);
}
