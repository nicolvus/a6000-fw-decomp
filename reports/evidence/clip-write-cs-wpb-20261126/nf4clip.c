/* nf4clip.so — sonda del camino de ESCRITURA de un clip nuevo, sobre el arnés G22 con
 * /dev/nflasha4 real emulado (NFLASH4=1).
 *
 * Se precarga ADEMÁS de sonyshim.so (LD_PRELOAD="/usr/lib/sonyshim.so /usr/lib/nf4clip.so");
 * no toca el shim: sólo usa dlsym(RTLD_DEFAULT) para situar libmpr y llamadas por dirección.
 *
 * NF4INJECT=<s>: a los s segundos (y tras esperar a que FBM::Init llene la tabla 0xA3699C):
 *   1. volcado de 0xA3699C (30 × 0x14 B) + diff de /nflasha4.img          — «arranque»
 *   2. modo `both`: `FBM InitB 6 3` (handler real 0x2B50D8) para crear el sector 0x31 en el proceso
 *   3. ChangeSector(4, 3)              0x2B41B4  + diff de imagen
 *   4. WritePackBegin(4,3,0,0x800,&pack,0,0)  0x2B3D24  + diff de imagen
 *   5. si 4 devuelve 0: WritePackAdd(&pack,buf,0x800)  0x2B3C64
 *                        WritePackEnd(&pack)            0x2B3B94  + diff de imagen
 *   6. modo `pre`: control positivo ChangeSector(0x22, 8) — userID 22/mediaID 8 → fileType 0xA0,
 *      el ÚNICO sector con handle en la imagen prístina: separa «no hay handle» de «no hay módulo»
 *   7. volcado final + «[FBMC] FIN»
 *
 * Firma de WritePackBegin (leída de la función, del format-string de su log y de su llamante real
 * 0x2B3F42 WriteSectorManagerInfo y 0x5CA164 m2psIfo_Backup):
 *   unsigned WritePackBegin(unsigned userID,      // r0
 *                           unsigned mediaID,     // r1
 *                           unsigned dataID,      // r2  (0xFF ⇒ no-op, devuelve 1)
 *                           unsigned dataSize,    // r3  (debe ser PAR)
 *                           RWBPACK *pack,        // [sp+0]  struct de 0x28 B del llamante
 *                           unsigned unused,      // [sp+4]  no se lee
 *                           unsigned operationMode// [sp+8]  sólo si userID == 0x80
 *                          );
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

#define OFF_CHANGESECTOR 0x2b41b4u
#define OFF_WRITEPACKBEGIN 0x2b3d24u
#define OFF_WRITEPACKADD 0x2b3c64u
#define OFF_WRITEPACKEND 0x2b3b94u

static int cfd = -2;
static void out(const char *f, ...) {
    char b[460]; va_list v; va_start(v, f); int n = vsnprintf(b, sizeof b, f, v); va_end(v);
    if (n <= 0) return;
    if (n > (int)sizeof b - 1) n = sizeof b - 1;
    if (cfd == -2) cfd = open("/dev/console", O_WRONLY | O_NOCTTY);
    if (cfd >= 0) { ssize_t r = write(cfd, b, n); (void)r; }
    { ssize_t r = write(2, b, n); (void)r; }
}

static unsigned long base_mpr;
static unsigned char *tab(void) { return (unsigned char *)(base_mpr + 0xa3699c); }
static unsigned rdu(unsigned char *p) { unsigned v; memcpy(&v, p, 4); return v; }
static unsigned rds(unsigned char *p) { unsigned short v; memcpy(&v, p, 2); return v; }

/* 30 entradas de 0x14 B: {u16 nombre(sector)|u16 ?, u32 handle, u32 estado, u32 OM, u32 ?} */
static int handles_no_cero(void) {
    unsigned char *t = tab(); int n = 0;
    for (int i = 0; i < 30; i++) if (rdu(t + i * 0x14 + 4)) n++;
    return n;
}
static void dump(const char *tag) {
    unsigned char *t = tab();
    out("[NF4] %s  handle!=0 = %d/30\n", tag, handles_no_cero());
    for (int m = 0; m < 2; m++) {
        char lin[380]; int o = 0;
        for (int i = m * 15; i < m * 15 + 15; i++)
            o += snprintf(lin + o, sizeof lin - o, "%02d:%03x=h%x/s%x/om%x ", i,
                          rds(t + i * 0x14) & 0xfff, rdu(t + i * 0x14 + 4),
                          rdu(t + i * 0x14 + 8), rdu(t + i * 0x14 + 0xc));
        lin[o] = 0;
        out("[NF4] %s [%02d..%02d]  %s\n", tag, m * 15, m * 15 + 14, lin);
    }
}
static void entrada(const char *tag, int i) {
    unsigned char *e = tab() + i * 0x14;
    out("[NF4] %s idx%02d sec=%#05x handle=%#x estado=%#x om=%#x\n", tag, i,
        rds(e) & 0xfff, rdu(e + 4), rdu(e + 8), rdu(e + 0xc));
}

/* offset del último byte distinto de la última comparación (para volcar la página del FINAL del
 * rango, que es donde caen los datos del clip, no la primera página de control) */
static long ultimo_dif = -1;
static void trozo(const char *tag, long off, long len);

/* Diferencia byte a byte entre la copia escribible del invitado y la imagen de origen.
 * Devuelve el primer byte distinto (-1 si no hay ninguna) e imprime el recuento. */
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
    ultimo_dif = ultimo;
    out("[NF4] imagen(%s): origen=%ld B copia=%ld B; bytes distintos=%ld; primero=%ld (%#lx) ultimo=%ld (%#lx)\n",
        tag, la, lb, difs, primero, (unsigned long)primero, ultimo, (unsigned long)ultimo);
    return primero;
}

/* Busca la primera tirada de 32 bytes 0x5a (el relleno de WritePackAdd) en la copia del invitado:
 * es la prueba directa de que el payload llegó al dispositivo. */
static void buscar_5a(const char *tag) {
    int b = open("/nflasha4.img", O_RDONLY);
    if (b < 0) return;
    static unsigned char x[65536];
    long o = 0, found = -1; ssize_t n; int run = 0;
    while ((n = read(b, x, sizeof x)) > 0) {
        for (ssize_t i = 0; i < n; i++) {
            if (x[i] == 0x5a) { if (++run >= 32 && found < 0) found = o + i - run + 1; } else run = 0;
        }
        o += n;
    }
    close(b);
    out("[NF4] patron(0x5a x32) %s: primer byte en %ld (%#lx)\n", tag, found, (unsigned long)found);
    if (found >= 0) trozo(tag, found, 32);
}

/* Página de 1 KiB de /nflasha4.img en hexadecimal (32 líneas de 32 B). */
static void pagina_hex(const char *tag, long off) {
    int b = open("/nflasha4.img", O_RDONLY);
    if (b < 0) { out("[NF4] pagina(%s): sin copia\n", tag); return; }
    static unsigned char p[0x400];
    if (pread(b, p, sizeof p, off) != (ssize_t)sizeof p) {
        out("[NF4] pagina(%s): lectura corta\n", tag); close(b); return;
    }
    close(b);
    out("[NF4] pagina(%s) de /nflasha4.img en %#lx:\n", tag, (unsigned long)off);
    for (int i = 0; i < 0x400; i += 32) {
        char lin[100]; int o = 0;
        for (int j = 0; j < 32; j++) o += snprintf(lin + o, sizeof lin - o, "%02x", p[i + j]);
        out("[NF4] PG %03x %s\n", i, lin);
    }
}

/* bytes distintos dentro de [off, off+len) de la copia, para señalar qué trozo cambió */
static void trozo(const char *tag, long off, long len) {
    int b = open("/nflasha4.img", O_RDONLY);
    if (b < 0) return;
    static unsigned char p[0x1000];
    if (len > (long)sizeof p) len = sizeof p;
    if (pread(b, p, (size_t)len, off) != (ssize_t)len) { close(b); return; }
    close(b);
    char lin[300]; int o = 0;
    for (long i = 0; i < len && o < 260; i++)
        o += snprintf(lin + o, sizeof lin - o, "%02x", p[i]);
    lin[o] = 0;
    out("[NF4] trozo(%s) @%#lx %ld B: %s\n", tag, (unsigned long)off, len, lin);
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
    int (*h)(long, char **) = (void *)(base_mpr + 0x2b50d8 + 1);
    out("[NF4] MON> FBM %s   (argc=%d, al comando=%d)\n", line, ac, ac - 1);
    int r = h(ac, av);
    out("[NF4] FBM %s -> %d\n", line, r);
    return r;
}

static const char *errstr(unsigned c) {
    const char *(*ges)(unsigned) = (void *)dlsym(RTLD_DEFAULT, "_ZN8FlashLib14GetErrorStringEm");
    return ges ? ges(c) : "?";
}

static unsigned change_sector(unsigned userID, unsigned mediaID, const char *rot) {
    unsigned (*f)(unsigned, unsigned) = (void *)(base_mpr + OFF_CHANGESECTOR + 1);
    out("[NF4] ChangeSector(%u,%u) [%s] ...\n", userID, mediaID, rot);
    unsigned r = f(userID, mediaID);
    out("[NF4] ChangeSector(%u,%u) [%s] -> %#010x  «%s»\n", userID, mediaID, rot, r,
        r ? errstr(r) : "sin error");
    return r;
}

/* el struct del llamante: 0x28 B; GetRWBuffer (0x2B38B4) escribe +0x22 (índice de búfer). */
static unsigned char pack[0x40] __attribute__((aligned(8)));
static unsigned char datos[0x800] __attribute__((aligned(8)));

static unsigned write_pack_begin(unsigned userID, unsigned mediaID, unsigned dataID, unsigned size) {
    unsigned (*f)(unsigned, unsigned, unsigned, unsigned, void *, unsigned, unsigned) =
        (void *)(base_mpr + OFF_WRITEPACKBEGIN + 1);
    memset(pack, 0, sizeof pack);
    out("[NF4] WritePackBegin(%u,%u,%u,%#x,&pack,0,0) ...\n", userID, mediaID, dataID, size);
    unsigned r = f(userID, mediaID, dataID, size, pack, 0, 0);
    out("[NF4] WritePackBegin(%u,%u,%u,%#x) -> %#010x  «%s»  bufferIndex=%#x\n", userID, mediaID,
        dataID, size, r, r ? errstr(r) : "sin error", rds(pack + 0x22));
    out("[NF4]   pack: hdr=%02x%02x%02x%02x%02x%02x totalDL=%#x curDL=%#x hdrDL=%#x sector=%#x handle=%#x\n",
        pack[0], pack[1], pack[2], pack[3], pack[4], pack[5], rdu(pack + 0x14), rdu(pack + 0x1c),
        rdu(pack + 0x18), rds(pack), rdu(pack + 4));
    return r;
}

static unsigned write_pack_add(unsigned len) {
    unsigned (*f)(void *, unsigned char *, unsigned) = (void *)(base_mpr + OFF_WRITEPACKADD + 1);
    memset(datos, 0x5a, sizeof datos);
    out("[NF4] WritePackAdd(&pack, buf(0x5a…), %#x) ...\n", len);
    unsigned r = f(pack, datos, len);
    out("[NF4] WritePackAdd(&pack,buf,%#x) -> %#010x  «%s» curDL=%#x\n", len, r,
        r ? errstr(r) : "sin error", rdu(pack + 0x1c));
    return r;
}

static unsigned write_pack_end(void) {
    unsigned (*f)(void *) = (void *)(base_mpr + OFF_WRITEPACKEND + 1);
    out("[NF4] WritePackEnd(&pack) ...\n");
    unsigned r = f(pack);
    out("[NF4] WritePackEnd(&pack) -> %#010x  «%s»\n", r, r ? errstr(r) : "sin error");
    return r;
}

/* Tabla estática {u32 userID, u32 mediaID, u32 fileType, u32 OM, void *fn, void *arg} de 0x18 B;
 * 0x2B3000 la recorre y SALTA las filas con fn == 0 (0x2B301A: cbz r2). */
static void tabla_estatica(void) {
    unsigned char *t = (unsigned char *)(base_mpr + 0x9d23fc);
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

/* Stub propio para el campo `fn` de 0x9D23FC: 0x2B3F7C lo llama con r0 = arg y trata r0 != 0
 * como error. Se compila en ARM y se pasa su dirección tal cual (blx r3, interworking). */
static unsigned dummy_fn(unsigned arg) { (void)arg; return 0; }

/* Descompone lo que hace ChangeSector antes de tocar la tabla: userID/mediaID -> fileType
 * (0x2B2B18), fileType -> índice en 0xA3699C (0x2B2F48) y índice -> handle (0x2B3094).
 * Añade los dos pasos que ChangeSector usa después: 0x2B3000 (exige fn != 0 en 0x9D23FC) y
 * 0x2B4030 BackupMgr::WriteBaseData(OM, mediaID). */
static void desglose(unsigned userID, unsigned mediaID, const char *rot) {
    unsigned ft = 0xdeadbeef, ix = 0xdeadbeef, h = 0xdeadbeef;
    unsigned (*gf)(unsigned, unsigned, unsigned *) = (void *)(base_mpr + 0x2b2b18 + 1);
    unsigned (*gi)(unsigned, unsigned, unsigned *) = (void *)(base_mpr + 0x2b2f48 + 1);
    unsigned (*gh)(unsigned, unsigned, unsigned *) = (void *)(base_mpr + 0x2b3094 + 1);
    unsigned r1 = gf(userID, mediaID, &ft);
    unsigned r2 = gi(userID, mediaID, &ix);
    unsigned r3 = gh(userID, mediaID, &h);
    unsigned (*gom)(unsigned, unsigned *) = (void *)(base_mpr + 0x2b2bcc + 1);
    unsigned (*isd) (unsigned) = (void *)(base_mpr + 0x2b1dcc + 1);
    unsigned om = 0xdeadbeef;
    unsigned r4 = gom(userID, &om);
    out("[NF4] desglose(%u,%u)[%s]: 0x2B2B18-> %#x fileType=%#x ; 0x2B2F48-> %#x idx=%#x ; "
        "0x2B3094-> %#x handle=%#x ; 0x2B2BCC-> %#x operationMode=%#x ; 0x2B1DCC(%#x)=%#x\n",
        userID, mediaID, rot, r1, ft, r2, ix & 0xff, r3, h, r4, om, om,
        r4 ? 0xdead : isd(om));
}

static void desglose_om(unsigned om, unsigned mediaID) {
    unsigned (*g3000)(unsigned, unsigned, unsigned *) = (void *)(base_mpr + 0x2b3000 + 1);
    unsigned (*wb)(unsigned, unsigned) = (void *)(base_mpr + 0x2b4030 + 1);
    unsigned h = 0xdeadbeef;
    unsigned r = g3000(om, mediaID, &h);
    out("[NF4] 0x2B3000(OM=%u,media=%u,&h) -> %#010x handle=%#x  «%s»\n", om, mediaID, r, h,
        r ? errstr(r) : "sin error");
    r = wb(om, mediaID);
    out("[NF4] BackupMgr::WriteBaseData(OM=%u,media=%u) -> %#010x  «%s»\n", om, mediaID, r,
        r ? errstr(r) : "sin error");
}

/* Por qué WritePackEnd devuelve 0x10800020: 0x2B3C18 llama a 0x2B25D0, que llama a
 * FlashLib::WriteSector por la PLT 0x11E810 (GOT 0x9C3A7C) y traduce el código FBS crudo con
 * 0x2B242C (0 -> 0, 0x57 -> 0x10100009, 0x0A -> 0x10100003, cualquier otro -> 0x10800020).
 * Aquí se llama a los símbolos exportados para ver el código CRUDO. */
static void diag_sector(unsigned handle) {
    unsigned (*gsi)(unsigned, void *) = (void *)dlsym(RTLD_DEFAULT, "_ZN8FlashLib13GetSectorInfoEmP8FBS_INFO");
    unsigned (*ws)(unsigned, unsigned, unsigned char *, unsigned *) =
        (void *)dlsym(RTLD_DEFAULT, "_ZN8FlashLib11WriteSectorEmmPhPm");
    unsigned char info[0x40];
    memset(info, 0xcc, sizeof info);
    if (gsi) {
        unsigned r = gsi(handle, info);
        out("[NF4] diag FlashLib::GetSectorInfo(%u,&info) -> %#x  «%s»\n", handle, r, r ? errstr(r) : "sin error");
        char lin[300]; int o = 0;
        for (int i = 0; i < 0x28; i++) o += snprintf(lin + o, sizeof lin - o, "%02x", info[i]);
        lin[o] = 0;
        out("[NF4] diag info[0..0x27] = %s\n", lin);
        out("[NF4] diag info: u16[0]=%#x u16[2]=%#x u32[4]=%#x u32[8]=%#x u32[0xc]=%#x u32[0x10]=%#x\n",
            rds(info), rds(info + 2), rdu(info + 4), rdu(info + 8), rdu(info + 0xc), rdu(info + 0x10));
    } else out("[NF4] diag sin símbolo GetSectorInfo\n");
    if (ws) {
        unsigned w = 0xdeadbeef;
        memset(datos, 0x5a, sizeof datos);
        unsigned r = ws(handle, 0x10, datos, &w);
        out("[NF4] diag FlashLib::WriteSector(%u,0x10,buf,&w) -> %#x (CRUDO) written=%#x\n", handle, r, w);
    } else out("[NF4] diag sin símbolo WriteSector\n");
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
    base_mpr = (unsigned long)di.dli_fbase;
    out("[NF4] base libmpr=%#lx tabla sectores=%#lx (0xA3699C)\n", base_mpr, base_mpr + 0xa3699c);

    int listo = 0;                                   /* FBM::Init (0x2B4820): 1ª = 0x10, última = 0xbd */
    for (int i = 0; i < 240; i++) {
        if ((rds(tab()) & 0xfff) == 0x10 && (rds(tab() + 29 * 0x14) & 0xfff) == 0xbd) { listo = 1; break; }
        usleep(500000);
    }
    out("[NF4] tabla %s (nombres 0x10..0xbd)\n", listo ? "LLENA" : "SIN llenar: sigo igual");
    sleep(3);

    const char *modo = getenv("NF4MODE");
    if (!modo) modo = "pre";
    out("[NF4] ===== modo %s =====\n", modo);

    dump("arranque");
    entrada("arranque", 10);
    tabla_estatica();
    comparar_imagenes("arranque");

    if (!strcmp(modo, "fn") || !strcmp(modo, "fnpost")) {
        unsigned *fn = (unsigned *)(base_mpr + 0x9d23fc + 13 * 0x18 + 0x10);
        unsigned *arg = (unsigned *)(base_mpr + 0x9d23fc + 13 * 0x18 + 0x14);
        out("[NF4] tabla 0x9D23FC[13] (u04/m3/ft031/om6): fn=%#x arg=%#x -> ", *fn, *arg);
        *arg = 0;
        *fn = (unsigned)(unsigned long)&dummy_fn;
        out("fn=%#x arg=%#x (stub propio de %p)\n", *fn, *arg, (void *)&dummy_fn);
        dump("tras-registrar-fn");
    }

    if (!strcmp(modo, "both")) {                     /* crea el sector en ESTE proceso */
        fbm_cmd("InitB 6 3");
        dump("tras-InitB-6-3");
        entrada("tras-InitB-6-3", 10);
        long d = comparar_imagenes("tras-InitB-6-3");
        if (d >= 0) pagina_hex("tras-InitB-6-3", d & ~0x3ffL);
    }

    /* (a) ChangeSector(4,3) — el que llamaba m2psIfo_Backup (0x5C9F7E: r0=4, r1=[this+0xC]) */
    unsigned rc = change_sector(4, 3, "clip");
    long d = comparar_imagenes("tras-ChangeSector-4-3");
    if (d >= 0) { pagina_hex("tras-ChangeSector-4-3", d & ~0x3ffL); trozo("tras-ChangeSector-4-3", d, 32); }

    /* (b) WritePackBegin(4,3,0,0x800,&pack,0,0) — 0x5CA164 llama igual con (4,mediaID,dataID,len,&pack,0,0) */
    unsigned rb = write_pack_begin(4, 3, 0, 0x800);
    d = comparar_imagenes("tras-WritePackBegin");
    if (d >= 0) { pagina_hex("tras-WritePackBegin", d & ~0x3ffL); trozo("tras-WritePackBegin", d, 32); }
    if (rb == 0) {
        unsigned ra = write_pack_add(0x800);
        d = comparar_imagenes("tras-WritePackAdd");
        if (d >= 0) { pagina_hex("tras-WritePackAdd", d & ~0x3ffL); trozo("tras-WritePackAdd", d, 32); }
        unsigned re = write_pack_end();
        (void)ra;
        d = comparar_imagenes("tras-WritePackEnd");
        if (d >= 0) { pagina_hex("tras-WritePackEnd", d & ~0x3ffL); trozo("tras-WritePackEnd", d, 32); }
        if (ultimo_dif >= 0) pagina_hex("tras-WritePackEnd-final", ultimo_dif & ~0x3ffL);
        buscar_5a("tras-WritePackEnd");
        (void)re;
        sleep(2);
        comparar_imagenes("WritePackEnd+2s");
    } else {
        out("[NF4] no se llama WritePackAdd/End: WritePackBegin devolvió %#x\n", rb);
    }

    /* descomposición de los dos pasos (después de medir los diff de arriba, para no ensuciarlos) */
    desglose(4, 3, "clip");
    desglose_om(6, 3);
    d = comparar_imagenes("tras-desglose-6-3");
    if (d >= 0) { pagina_hex("tras-desglose-6-3", d & ~0x3ffL); trozo("tras-desglose-6-3", d, 32); }

    diag_sector(rdu(tab() + 10 * 0x14 + 4));    /* handle del sector 0x31, el que usa el clip */
    d = comparar_imagenes("tras-diag-WriteSector");
    if (d >= 0) { pagina_hex("tras-diag-WriteSector", d & ~0x3ffL); trozo("tras-diag-WriteSector", d, 32); }

    if (!strcmp(modo, "pre")) {                      /* CONTROL POSITIVO: userID 22/mediaID 8 → 0xA0,
                                                      * el único sector CON handle en la imagen prístina */
        unsigned r = change_sector(0x22, 8, "control-handle-existente");
        (void)r;
        desglose(0x22, 8, "control-handle-existente");
        desglose_om(9, 8);
        d = comparar_imagenes("tras-ChangeSector-control");
        if (d >= 0) { pagina_hex("tras-ChangeSector-control", d & ~0x3ffL); trozo("tras-ChangeSector-control", d, 32); }
    }

    dump("fin");
    entrada("fin", 10);
    comparar_imagenes("fin");
    out("[FBMC] FIN\n");
    return 0;
}

__attribute__((constructor)) static void nf4c_init(void) {
    const char *e = getenv("NF4INJECT");
    if (!e) return;
    unsigned s = 0;                                  /* atoi a mano: la libc 2.11 no tiene __isoc23_strtol */
    while (*e >= '0' && *e <= '9') s = s * 10 + (unsigned)(*e++ - '0');
    pthread_t th;
    if (pthread_create(&th, 0, worker, (void *)(unsigned long)s) == 0) pthread_detach(th);
}
