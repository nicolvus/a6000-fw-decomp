/* msvprobe.so — 2º .so precargado para el arnés G22 con /dev/nflasha4 real emulado (NFLASH4=1).
 *
 * Pregunta que mide: con el sector FBM 0x31 registrado en 0xA3699C (idx 10 con handle), ¿devuelve 0
 *   · mp4Ifo_General::FlashLoadForMsv   0x698EC8, y
 *   · MsvMcmd::RcsBackupTblData         0x3AFA94 ?
 *
 * No inventa objetos: al arrancar, la propia cámara llama a 0x698EC8 (de ahí sale la línea 1749 del
 * anillo), así que este .so pone una trampa UDF de un solo uso en la ENTRADA de 0x698EC8 y captura
 * r0 = `this` (el objeto mp4Ifo_General real). De ahí salen también los otros dos eslabones:
 *   sub = [this+0x00]   (mp4Ifo_If)      msv = [sub+0x08]   (MsvMcmd)
 * y con esos punteros REALES se llama por dirección a 0x3AFA94(msv) y 0x698EC8(this).
 *
 * Además, para documentar por qué un objeto sintético no sirve, se construyen dos objetos en memoria
 * del invitado ([+0x4088]=4, [+0x408c]=3) y se llaman las mismas direcciones con captura de fallo
 * (SIGSEGV/SIGBUS + siglongjmp): se registra el valor devuelto o la pc/lr exacta del fallo.
 *
 * Se precarga JUNTO a sonyshim.so (LD_PRELOAD="/usr/lib/sonyshim.so /usr/lib/msvprobe.so"); no toca
 * el shim: usa dlsym(RTLD_DEFAULT) y desplazamientos de libmpr (VA del ELF).
 *
 * Variables: MSVPROBE=<s> retardo antes de medir · MSVWAIT=<s> espera máxima de la captura
 *            MSVHITS=<n> capturas como máximo (por omisión 6)
 * Salida: líneas «[MSV] …» por /dev/console (van a consola.log) y «[FBMC] FIN» al terminar.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <pthread.h>
#include <setjmp.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ucontext.h>
#include <sys/mman.h>
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
static unsigned rva(unsigned long a) { unsigned v; memcpy(&v, (void *)a, 4); return v; }

static const char *errstr(unsigned c) {
    const char *(*ges)(unsigned) = (void *)dlsym(RTLD_DEFAULT, "_ZN8FlashLib14GetErrorStringEm");
    return ges ? ges(c) : "?";
}

/* ---------- trampa UDF (misma técnica que TRACEFN2 del shim) ---------- */
#define NT 6
#define MAXH 3
struct trampa { const char *nom; unsigned long off, pc, step; unsigned short orig, orig2; volatile int nh; unsigned long hits[MAXH]; };
static struct trampa traps[NT] = {
    { "698ec8 FlashLoadForMsv",        0x698ec8, 0, 0, 0, 0, 0, {0} },
    { "3afa94 MsvMcmd::RcsBackupTbl",  0x3afa94, 0, 0, 0, 0, 0, {0} },
    { "35ea1c RcsBackupTblData",       0x35ea1c, 0, 0, 0, 0, 0, {0} },
    { "698fb8 mp4Ifo_General::Load",   0x698fb8, 0, 0, 0, 0, 0, {0} },
    { "67ca6c MMgrMp4IfoAcsr::CrAndLd",0x67ca6c, 0, 0, 0, 0, 0, {0} },
    { "698f18 CheckSalvageStatus",     0x698f18, 0, 0, 0, 0, 0, {0} },
};
static int ntraps;
static volatile int trace_armed;
static struct sigaction prev_ill;

static int rearma(struct trampa *t) {          /* UDF en la instrucción siguiente (para repetir) */
    unsigned long nx = t->pc + (((t->orig >> 11) >= 0x1d) ? 4 : 2);
    t->step = nx; t->orig2 = *(unsigned short *)nx; *(unsigned short *)nx = 0xde00;
    __builtin___clear_cache((char *)nx, (char *)nx + 2);
    return 0;
}

static void on_ill(int sig, siginfo_t *si, void *u) {
    mcontext_t *c = &((ucontext_t *)u)->uc_mcontext;
    unsigned long pc = c->arm_pc & ~1UL;
    for (int i = 0; i < ntraps; i++) {
        struct trampa *t = &traps[i];
        if (t->step && pc == t->step) {        /* paso hecho: restaurar la siguiente y rearmar la entrada */
            *(unsigned short *)pc = t->orig2; t->step = 0;
            *(unsigned short *)t->pc = 0xde00;
            __builtin___clear_cache((char *)pc, (char *)pc + 2);
            __builtin___clear_cache((char *)t->pc, (char *)t->pc + 2);
            return;
        }
        if (t->pc && pc == t->pc) {
            int n = t->nh;
            if (n < MAXH) t->hits[n] = c->arm_r0;
            t->nh = n + 1;
            *(unsigned short *)pc = t->orig;
            __builtin___clear_cache((char *)pc, (char *)pc + 2);
            if (n + 1 < MAXH) rearma(t); else t->pc = 0;   /* tras MAXH se desarma */
            return;
        }
    }
    if ((prev_ill.sa_flags & SA_SIGINFO) && prev_ill.sa_sigaction) { prev_ill.sa_sigaction(sig, si, u); return; }
    if (prev_ill.sa_handler && prev_ill.sa_handler != SIG_DFL && prev_ill.sa_handler != SIG_IGN) {
        prev_ill.sa_handler(sig); return;
    }
    signal(SIGILL, SIG_DFL);
}

static void armar_trampas(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_ill; sa.sa_flags = SA_SIGINFO | SA_NODEFER;
    if (sigaction(SIGILL, &sa, &prev_ill) != 0) { out("[MSV] sigaction(SIGILL) falló\n"); return; }
    for (int i = 0; i < NT; i++) {
        unsigned long va = fbm_base + traps[i].off;
        unsigned short *q = (unsigned short *)va;
        if (mprotect((void *)(va & ~4095UL), 8192, PROT_READ | PROT_WRITE | PROT_EXEC) != 0) {
            out("[MSV] mprotect(%#lx) falló (%s)\n", va, traps[i].nom); continue;
        }
        if (*q == 0xde00) { out("[MSV] %s: ya había UDF\n", traps[i].nom); continue; }
        traps[i].pc = va; traps[i].orig = *q; traps[i].step = 0; traps[i].nh = 0;
        *q = 0xde00;
        __builtin___clear_cache((char *)q, (char *)q + 2);
        out("[MSV] trampa %s en %#lx (orig %04x)\n", traps[i].nom, va, traps[i].orig);
    }
    ntraps = NT; trace_armed = 1;
}

/* ---------- llamada por dirección con captura de fallo ---------- */
static sigjmp_buf jb;
static volatile int guard_on;
static volatile unsigned long flt_pc, flt_lr, flt_sig;
static struct sigaction prev_segv, prev_bus, prev_abrt;
static int guard_instalada;

static void on_fault(int sig, siginfo_t *si, void *u) {
    if (guard_on) {
        mcontext_t *c = &((ucontext_t *)u)->uc_mcontext;
        flt_pc = c->arm_pc; flt_lr = c->arm_lr; flt_sig = (unsigned long)sig;
        guard_on = 0;
        siglongjmp(jb, 1);
    }
    signal(sig, SIG_DFL);
}

struct res { unsigned long ret, pc, lr, sig; int fault; };

static void instala_guardia(void) {
    if (guard_instalada) return;
    struct sigaction sa; memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_fault; sa.sa_flags = SA_SIGINFO | SA_NODEFER;
    sigaction(SIGSEGV, &sa, &prev_segv); sigaction(SIGBUS, &sa, &prev_bus);
    sigaction(SIGABRT, &sa, &prev_abrt);
    guard_instalada = 1;
}

static struct res llamar(unsigned long va, unsigned long a0) {
    struct res r; memset(&r, 0, sizeof r);
    if (!va) { r.fault = 2; return r; }
    instala_guardia();
    flt_pc = flt_lr = flt_sig = 0;
    if (!sigsetjmp(jb, 1)) {
        unsigned (*f)(unsigned long) = (void *)va;
        guard_on = 1;
        r.ret = (unsigned long)f(a0);
        guard_on = 0;
    } else {
        r.fault = 1;
    }
    r.pc = flt_pc; r.lr = flt_lr; r.sig = flt_sig;
    return r;
}

/* lectura de 4 B con el mismo guardia: devuelve 0 si la dirección no es legible */
static int leer32(unsigned long a, unsigned long *v) {
    if (!a) return 0;
    instala_guardia();
    flt_pc = flt_lr = flt_sig = 0;
    if (!sigsetjmp(jb, 1)) {
        guard_on = 1;
        *v = (unsigned long)*(volatile unsigned *)a;
        guard_on = 0;
        return 1;
    }
    guard_on = 0;
    return 0;
}
static int leer8(unsigned long a, unsigned long *v) {
    if (!a) return 0;
    instala_guardia();
    flt_pc = flt_lr = flt_sig = 0;
    if (!sigsetjmp(jb, 1)) {
        guard_on = 1;
        *v = (unsigned long)*(volatile unsigned char *)a;
        guard_on = 0;
        return 1;
    }
    guard_on = 0;
    return 0;
}


static struct res llamar3(unsigned long va, unsigned long a0, unsigned long a1, unsigned long a2) {
    struct res r; memset(&r, 0, sizeof r);
    if (!va) { r.fault = 2; return r; }
    instala_guardia();
    flt_pc = flt_lr = flt_sig = 0;
    if (!sigsetjmp(jb, 1)) {
        unsigned (*f)(unsigned long, unsigned long, unsigned long) = (void *)va;
        guard_on = 1;
        r.ret = (unsigned long)f(a0, a1, a2);
        guard_on = 0;
    } else {
        r.fault = 1;
    }
    r.pc = flt_pc; r.lr = flt_lr; r.sig = flt_sig;
    return r;
}


/* llamada en un hilo aparte con tope de tiempo: las macros de traza (0x34E468 -> osal_valloc_msg_wait)
 * pueden bloquearse desde un hilo que no es de OSAL; así una llamada colgada no pierde la pasada. */
struct tcall { unsigned long va, a0; struct res r; volatile int done; };
static void *tcall_fn(void *p) { struct tcall *c = (struct tcall *)p; c->r = llamar(c->va, c->a0); c->done = 1; return 0; }
static struct res llamar_to(unsigned long va, unsigned long a0, int secs, int *timeout) {
    static struct tcall c;
    memset(&c, 0, sizeof c); c.va = va; c.a0 = a0;
    *timeout = 0;
    pthread_t th;
    if (pthread_create(&th, 0, tcall_fn, &c) != 0) return llamar(va, a0);
    pthread_detach(th);
    for (int i = 0; i < secs * 10 && !c.done; i++) usleep(100000);
    if (!c.done) { struct res r; memset(&r, 0, sizeof r); r.fault = 3; *timeout = 1; return r; }
    return c.r;
}

/* stubs temporales: dejan sin efecto las macros de traza/log que pueden bloquear (bx lr) */
static struct { unsigned long va; unsigned short orig[2]; int on; } stubs[] = {
    { 0x34e468, {0,0}, 0 }, { 0x34e490, {0,0}, 0 },   /* solo las macros TRACE de 0x3AFA94/0x35E04C */
};
static void stubs_on(int on) {
    for (unsigned i = 0; i < sizeof stubs / sizeof stubs[0]; i++) {
        unsigned long va = fbm_base + stubs[i].va;
        unsigned short *q = (unsigned short *)va;
        if (on) {
            mprotect((void *)(va & ~4095UL), 8192, PROT_READ | PROT_WRITE | PROT_EXEC);
            stubs[i].orig[0] = q[0]; stubs[i].orig[1] = q[1]; stubs[i].on = 1;
            q[0] = 0x2000; q[1] = 0x4770;              /* movs r0,#0 ; bx lr */
            __builtin___clear_cache((char *)q, (char *)q + 4);
        } else if (stubs[i].on) {
            mprotect((void *)(va & ~4095UL), 8192, PROT_READ | PROT_WRITE | PROT_EXEC);
            q[0] = stubs[i].orig[0]; q[1] = stubs[i].orig[1]; stubs[i].on = 0;
            __builtin___clear_cache((char *)q, (char *)q + 4);
        }
    }
    out("[MSV] stubs de traza %s (%u funciones)\n", on ? "puestos" : "retirados",
        (unsigned)(sizeof stubs / sizeof stubs[0]));
}

static void log_res(const char *tag, unsigned long va, unsigned long arg, struct res r) {
    if (r.fault == 2) { out("[MSV] %s: sin VA\n", tag); return; }
    if (r.fault == 3) { out("[MSV] %s VA=%#lx(arg=%#lx) NO VUELVE (tope de tiempo)\n", tag, va, arg); return; }
    if (r.fault) {
        out("[MSV] %s VA=%#lx(arg=%#lx) FALLO señal=%lu pc=%#lx lr=%#lx\n",
            tag, va, arg, r.sig, r.pc, r.lr);
    } else {
        out("[MSV] %s VA=%#lx(arg=%#lx) -> ret=%#010lx  «%s»\n",
            tag, va, arg, r.ret, errstr((unsigned)r.ret));
    }
}

/* ---------- volcados ---------- */
static void dump(const char *tag) {
    unsigned char *t = tab();
    int n = 0;
    for (int i = 0; i < 30; i++) if (rdu(t + i * 0x14 + 4)) n++;
    out("[MSV] %s  handle!=0 = %d/30\n", tag, n);
    for (int m = 0; m < 2; m++) {
        char lin[380]; int o = 0;
        for (int i = m * 15; i < m * 15 + 15; i++) {
            o += snprintf(lin + o, sizeof lin - o, "%02d:%03x=h%x/s%x/om%x ", i,
                          rds(t + i * 0x14) & 0xfff, rdu(t + i * 0x14 + 4),
                          rdu(t + i * 0x14 + 8), rdu(t + i * 0x14 + 0xc));
        }
        lin[o] = 0;
        out("[MSV] %s [%02d..%02d]  %s\n", tag, m * 15, m * 15 + 14, lin);
    }
    {   unsigned char *e = t + 10 * 0x14;
        out("[MSV] CRITERIO idx10 sec=%#x handle=%#x +8=%#x => %s\n", rds(e) & 0xfff, rdu(e + 4), rdu(e + 8),
            (rdu(e + 4) && rdu(e + 8) == 1) ? "OK" : "FALLA");
    }
}

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
        out("[MSV] tabla 0x9D23FC (%s): %s\n", tag, lin);
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
    out("[MSV] MON> FBM %s   (argc=%d, al comando=%d)\n", line, ac, ac - 1);
    int r = h(ac, av);
    out("[MSV] FBM %s -> %d\n", line, r);
    return r;
}

static unsigned buscar(unsigned om, unsigned media) {
    unsigned (*f)(unsigned, unsigned, unsigned *) = (void *)(fbm_base + 0x2b3000 + 1);
    unsigned h = 0xdeadbeef;
    unsigned r = f(om, media, &h);
    out("[MSV] 0x2B3000(OM=%u,media=%u,&h) -> ret=%#x handle=%#x  «%s»\n", om, media, r, h,
        r ? errstr(r) : "sin error");
    return r;
}

static unsigned leer(unsigned user, unsigned media) {
    unsigned (*bkread)(unsigned, unsigned, void *, void *, void *, void *) = (void *)(fbm_base + 0x2b39b8 + 1);
    unsigned char b3[0x40], b5[0x40], ent[0x40]; unsigned b4[0x40];
    memset(b3, 0, sizeof b3); memset(b4, 0, sizeof b4);
    memset(b5, 0, sizeof b5); memset(ent, 0xcc, sizeof ent);
    out("[MSV] BkRead(%#04x,%u) ...\n", user, media);
    unsigned r = bkread(user, media, b3, b4, b5, ent);
    out("[MSV] BkRead(%#04x,%u) -> %#010x   entrada: sec=%#x h=%#x est=%#x om=%#x\n",
        user, media, r, rds(ent) & 0xfff, rdu(ent + 4), rdu(ent + 8), rdu(ent + 0xc));
    return r;
}

static long comparar_imagenes(const char *tag) {
    int a = open("/usr/share/nflasha4.img", O_RDONLY), b = open("/nflasha4.img", O_RDONLY);
    if (a < 0 || b < 0) {
        out("[MSV] imagen(%s): origen fd=%d copia fd=%d (falta alguna)\n", tag, a, b);
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
    out("[MSV] imagen(%s): origen=%ld B copia=%ld B; bytes distintos=%ld; primero=%ld (%#lx) ultimo=%ld (%#lx)\n",
        tag, la, lb, difs, primero, (unsigned long)primero, ultimo, (unsigned long)ultimo);
    return primero;
}

/* ---------- objeto sintético ---------- */
static unsigned char *bloque(size_t n) {
    unsigned char *p = (unsigned char *)malloc(n);
    if (p) memset(p, 0, n);
    return p;
}
static void pon(unsigned char *p, unsigned long off, unsigned v) { memcpy(p + off, &v, 4); }


/* Construye el objeto REAL de la clase con su propio constructor 0x3B04A4 (MsvMcmd):
 *   0x3B04A4(this, cfg*, void **out)   vtable 0x835980; new(0x4B78) + ctor 0x3B1DE8 -> [this+0x50]
 * Devuelve el objeto (r0 = this) o 0 si falla. */
static unsigned long construir_msv(unsigned char **child_out) {
    unsigned char *o = bloque(0x200), *cfg = bloque(0x40);
    unsigned long oout = 0;
    *child_out = 0;
    if (!o || !cfg) return 0;
    out("[MSV] CTOR 0x3B04A4(this=%p, cfg=%p, &out) ...\n", (void *)o, (void *)cfg);
    struct res r = llamar3(fbm_base + 0x3b04a4 + 1, (unsigned long)o, (unsigned long)cfg, (unsigned long)&oout);
    (void)r;
    if (r.fault) {
        out("[MSV] CTOR FALLO señal=%lu pc=%#lx lr=%#lx\n", r.sig, r.pc, r.lr);
        return 0;
    }
    unsigned long vt = 0, ch = 0;
    leer32((unsigned long)o, &vt); leer32((unsigned long)o + 0x50, &ch);
    out("[MSV] CTOR -> ret=%#lx  [obj]=%#lx (esperado base+0x835980=%#lx)  [obj+0x50]=%#lx  out=%#lx\n",
        r.ret, vt, fbm_base + 0x835980, ch, oout);
    if (!ch) return 0;
    *child_out = (unsigned char *)ch;
    return (unsigned long)o;
}

static void sinteticos(unsigned long msv_real) {
    /* (a) mínimo del enunciado: sólo +0x4088=4 y +0x408c=3, resto a cero */
    unsigned char *a = bloque(0x4100);
    if (!a) { out("[MSV] SIN1: sin memoria\n"); return; }
    pon(a, 0x4088, 0x04); pon(a, 0x408c, 3);
    out("[MSV] SIN1 obj=%p [obj+0x4088]=4 [obj+0x408c]=3 resto=0\n", (void *)a);
    log_res("SIN1 0x3AFA94(obj-sintetico)", fbm_base + 0x3afa94 + 1, (unsigned long)a,
            llamar(fbm_base + 0x3afa94 + 1, (unsigned long)a));

    /* (b) autorreferente: además [obj+0x50]=obj (lo primero que lee 0x3AFA94), logger reales
     *     y el objeto auxiliar real, para ver hasta dónde llega */
    unsigned char *b = bloque(0x4100);
    if (!b) { out("[MSV] SIN2: sin memoria\n"); return; }
    pon(b, 0x4088, 0x04); pon(b, 0x408c, 3);
    pon(b, 0x50, (unsigned long)b);
    if (msv_real) {
        pon(b, 0x38, rva(msv_real + 0x38));            /* logger de MsvMcmd */
        pon(b, 0x4084, rva(msv_real + 0x4084));        /* logger del objeto +0x4000 */
        pon(b, 0x30c8, rva(msv_real + 0x30c8));        /* objeto auxiliar 1 */
    }
    out("[MSV] SIN2 obj=%p [obj+0x50]=obj logger=%#x/%#x aux=%#x\n", (void *)b,
        rva((unsigned long)b + 0x38), rva((unsigned long)b + 0x4084), rva((unsigned long)b + 0x30c8));
    log_res("SIN2 0x3AFA94(obj-autorref)", fbm_base + 0x3afa94 + 1, (unsigned long)b,
            llamar(fbm_base + 0x3afa94 + 1, (unsigned long)b));

    /* (c) 0x698EC8 con objeto EXTERIOR sintético (2 saltos) y el MsvMcmd REAL dentro */
    if (msv_real) {
        unsigned char *ifo = bloque(0x40), *sub = bloque(0x40);
        if (ifo && sub) {
            pon(sub, 8, msv_real);
            pon(ifo, 0, (unsigned long)sub);
            out("[MSV] SIN3 ifo=%p sub=%p [sub+8]=msv real=%#lx\n", (void *)ifo, (void *)sub, msv_real);
            log_res("SIN3 0x698EC8(obj-exterior-sintetico)", fbm_base + 0x698ec8 + 1, (unsigned long)ifo,
                    llamar(fbm_base + 0x698ec8 + 1, (unsigned long)ifo));
        }
    }
}

/* ---------- hilo ---------- */
/* parser de /proc/self/maps a mano: la libc 2.11 no tiene los sscanf de glibc 2.3x */
static char *saltar_campos(char *p, int n) {
    while (n-- > 0) { while (*p && *p != ' ') p++; while (*p == ' ') p++; }
    return p;
}
static int parse_maps(char *ln, unsigned long *a, unsigned long *b, char *perms, char **path) {
    char *p = ln; unsigned long v = 0;
    while (*p && *p != '-') { int c = *p++; v = v * 16 + (unsigned long)(c <= '9' ? c - '0' : (c | 32) - 'a' + 10); }
    if (*p != '-') return 0;
    *a = v; p++; v = 0;
    while (*p && *p != ' ') { int c = *p++; v = v * 16 + (unsigned long)(c <= '9' ? c - '0' : (c | 32) - 'a' + 10); }
    *b = v;
    while (*p == ' ') p++;
    for (int i = 0; i < 6 && *p && *p != ' '; i++) perms[i] = *p++;
    perms[6] = 0;
    *path = saltar_campos(p, 4);
    return 1;
}

/* barrido de emergencia: busca en el heap un objeto con [+0x4088]=4 y [+0x408c]=3 */
static unsigned long scan_msv(void) {
    int fd = open("/proc/self/maps", O_RDONLY);
    if (fd < 0) { out("[MSV] scan: sin /proc/self/maps\n"); return 0; }
    static char buf[65536]; ssize_t n = read(fd, buf, sizeof buf - 1); close(fd);
    if (n <= 0) { out("[MSV] scan: maps vacío\n"); return 0; }
    buf[n] = 0;
    unsigned long lmin = ~0UL, lmax = 0, cand[8]; int nc = 0; unsigned long visit = 0;
    for (char *ln = strtok(buf, "\n"); ln; ln = strtok(0, "\n")) {
        unsigned long a = 0, b = 0; char perms[8] = {0}; char *path = 0;
        if (!parse_maps(ln, &a, &b, perms, &path)) continue;
        if (strstr(path, "libmpr.so")) { if (a < lmin) lmin = a; if (b > lmax) lmax = b; }
    }
    if (lmax <= lmin) { out("[MSV] scan: no veo libmpr en maps\n"); return 0; }
    out("[MSV] scan: libmpr %#lx-%#lx\n", lmin, lmax);
    /* segunda pasada: regiones anónimas escribibles */
    memset(buf, 0, sizeof buf);
    fd = open("/proc/self/maps", O_RDONLY); n = read(fd, buf, sizeof buf - 1); close(fd);
    if (n <= 0) return 0;
    buf[n] = 0;
    instala_guardia();
    for (char *ln = strtok(buf, "\n"); ln; ln = strtok(0, "\n")) {
        unsigned long a = 0, b = 0; char perms[8] = {0}; char *path = 0;
        if (!parse_maps(ln, &a, &b, perms, &path)) continue;
        if (perms[0] != 'r' || perms[1] != 'w') continue;
        if (b - a < 0x4100 || b - a > 0x20000000UL) continue;
        if (strstr(path, ".so") || strstr(path, "/dev/") || strstr(path, "/usr/") || strstr(path, "/cam/")) continue;
        if (!sigsetjmp(jb, 1)) {
            guard_on = 1;
            for (unsigned long q = a; q + 0x4100 < b; q += 4) {
                if (*(volatile unsigned *)(q + 0x4088) != 4) continue;
                if (*(volatile unsigned *)(q + 0x408c) != 3) continue;
                unsigned vt = *(volatile unsigned *)q;
                if (vt < lmin || vt >= lmax) continue;
                if (!*(volatile unsigned *)(q + 0x50)) continue;
                if (nc < 8) cand[nc++] = q;
            }
            guard_on = 0; visit += b - a;
        } else { guard_on = 0; }
    }
    out("[MSV] scan: %lu MiB barridos, %d candidatos\n", visit >> 20, nc);
    for (int i = 0; i < nc; i++) {
        unsigned long q = cand[i], v50 = 0, v84 = 0, v30 = 0, v38 = 0, v88 = 0, v8c = 0, c88 = 0;
        leer32(q, &v50); leer32(q + 0x38, &v38); leer32(q + 0x4084, &v84); leer32(q + 0x4088, &v88);
        leer32(q + 0x408c, &v8c); leer32(q + 0x30c8, &v30);
        out("[MSV] scan[%d] %#lx vptr=%#x [+38]=%#lx [+50]=%#lx [+4084]=%#lx [+4088]=%#lx [+408c]=%#lx [+30c8]=%#lx\n",
            i, q, rva(q), v38, v50, v84, v88, v8c, v30);
        if (v50 && leer32(v50 + 0x4088, &c88) && c88 == 4)
            out("[MSV] scan[%d] [obj+0x50]=%#lx con [+0x4088]=%#lx: encaja\n", i, v50, c88);
    }
    return nc ? cand[0] : 0;
}

static void medir(const char *tag, unsigned long va, unsigned long arg) {
    int to = 0;
    out("[MSV] %s: llamando VA=%#lx(arg=%#lx) ...\n", tag, va, arg);
    struct res r = llamar_to(va, arg, 30, &to);
    log_res(tag, va, arg, r);
}

static void *worker(void *arg) {
    unsigned s = (unsigned)(unsigned long)arg;
    void *sym = 0;
    for (int i = 0; i < 240000 && !sym; i++) {        /* hasta ~240 s: libmpr se carga con dlopen */
        sym = dlsym(RTLD_DEFAULT, "_ZN8FlashLib12CreateSectorEt12FBS_MOVEFLAGPmPt");
        if (!sym) usleep(1000);
    }
    Dl_info di;
    if (!sym || !dladdr(sym, &di)) { out("[MSV] sin símbolo de FlashLib: libmpr no cargada\n[FBMC] FIN\n"); return 0; }
    fbm_base = (unsigned long)di.dli_fbase;
    out("[MSV] base libmpr=%#lx tabla sectores=%#lx (0xA3699C)\n", fbm_base, fbm_base + 0xa3699c);

    armar_trampas();

    if (s) sleep(s);

    int listo = 0;
    for (int i = 0; i < 240; i++) {
        if ((rds(tab()) & 0xfff) == 0x10 && (rds(tab() + 29 * 0x14) & 0xfff) == 0xbd) { listo = 1; break; }
        usleep(500000);
    }
    out("[MSV] tabla %s (nombres 0x10..0xbd)\n", listo ? "LLENA" : "SIN llenar: sigo igual");

    const char *we = getenv("MSVWAIT");
    int wmax = 150; if (we) { wmax = 0; while (*we >= '0' && *we <= '9') wmax = wmax * 10 + (*we++ - '0'); }
    for (int i = 0; i < wmax * 10; i++) {
        int vivos = 0;
        for (int k = 0; k < NT; k++) if (traps[k].pc) vivos = 1;
        if (!vivos) break;
        if (traps[0].nh || traps[1].nh || traps[2].nh) break;   /* ya hay objeto real: no esperar más */
        usleep(100000);
    }
    for (int k = 0; k < NT; k++)
        out("[MSV] trampa %s: %d capturas\n", traps[k].nom, traps[k].nh);

    /* elige el objeto real con (userID 4, mediaID 3) */
    unsigned long ifo = 0, msv = 0, obj4000 = 0;
    {   struct trampa *t = &traps[0];                          /* 0x698EC8: this = mp4Ifo_General */
        for (int i = 0; i < t->nh && i < MAXH; i++) {
            unsigned long sub = 0, m = 0;
            if (!leer32(t->hits[i], &sub) || !sub) continue;
            if (!leer32(sub + 8, &m) || !m) continue;
            unsigned long v88 = 0, v8c = 0;
            leer32(m + 0x4088, &v88); leer32(m + 0x408c, &v8c);
            out("[MSV] CAP698 this=%#lx sub=%#lx msv=%#lx (+4088=%#lx +408c=%#lx)\n", t->hits[i], sub, m, v88, v8c);
            if (!ifo && v88 == 4 && v8c == 3) { ifo = t->hits[i]; msv = m; }
        }
    }
    if (!msv) {                                                /* 0x3AFA94: r0 = MsvMcmd */
        struct trampa *t = &traps[1];
        for (int i = 0; i < t->nh && i < MAXH; i++) {
            unsigned long v88 = 0, v8c = 0, v50 = 0;
            leer32(t->hits[i] + 0x4088, &v88); leer32(t->hits[i] + 0x408c, &v8c); leer32(t->hits[i] + 0x50, &v50);
            out("[MSV] CAP3A msv=%#lx (+4088=%#lx +408c=%#lx +50=%#lx)\n", t->hits[i], v88, v8c, v50);
            if (v88 == 4 && v8c == 3 && v50) { msv = t->hits[i]; if (!obj4000) obj4000 = v50; }
        }
    }
    if (!obj4000) {                                            /* 0x35EA1C: r0 = objeto +0x4000 */
        struct trampa *t = &traps[2];
        for (int i = 0; i < t->nh && i < MAXH; i++) {
            unsigned long v88 = 0, v8c = 0;
            leer32(t->hits[i] + 0x4088, &v88); leer32(t->hits[i] + 0x408c, &v8c);
            out("[MSV] CAP35 obj=%#lx (+4088=%#lx +408c=%#lx)\n", t->hits[i], v88, v8c);
            if (v88 == 4 && v8c == 3 && !obj4000) obj4000 = t->hits[i];
        }
    }
    if (!obj4000) { out("[MSV] sin objeto real todavia: barrido de emergencia\n"); obj4000 = scan_msv(); }
    if (!msv) {                                               /* construir la clase con su ctor real */
        unsigned char *ch = 0;
        unsigned long o = construir_msv(&ch);
        if (o && ch) {
            pon(ch, 0x4088, 4); pon(ch, 0x408c, 3);
            out("[MSV] objeto construido: this=%#lx hijo=%p; fijados [+0x4088]=4 [+0x408c]=3\n", o, (void *)ch);
            msv = o; obj4000 = (unsigned long)ch;
        }
    }

    /* si no hay `this` de mp4Ifo_General, se usa el MsvMcmd real; si tampoco, el objeto +0x4000 real
     * envuelto en un MsvMcmd sintético mínimo ([+0x50]=obj, [+0x38]=logger real) */
    unsigned char *msv_sint = 0, *ifo_sint = 0, *sub_sint = 0;
    if (!msv && obj4000) {
        msv_sint = bloque(0x60);
        unsigned long lg = 0; leer32(obj4000 + 0x4084, &lg);
        pon(msv_sint, 0x50, obj4000); pon(msv_sint, 0x38, lg);
        msv = (unsigned long)msv_sint;
        out("[MSV] MsvMcmd sintetico %p: [+0x50]=%#lx (objeto +0x4000 real) [+0x38]=%#lx\n", (void *)msv_sint, obj4000, lg);
    }
    if (!msv) { out("[MSV] NO hay objeto real (4,3): no se puede medir\n[FBMC] FIN\n"); return 0; }
    if (!ifo) {
        ifo_sint = bloque(0x40); sub_sint = bloque(0x40);
        pon(sub_sint, 8, msv); pon(ifo_sint, 0, (unsigned long)sub_sint);
        ifo = (unsigned long)ifo_sint;
        out("[MSV] objeto exterior de 0x698EC8 sintetico %p -> sub %p -> msv %#lx\n", (void *)ifo_sint, (void *)sub_sint, msv);
    }
    out("[MSV] midiendo con ifo(this)=%#lx msv=%#lx\n", ifo, msv);

    sleep(2);
    dump("antes");
    tabla_estatica("antes");
    buscar(6, 3);

    int only = getenv("MSVONLY") != 0;              /* MSVONLY=1: sólo crear el sector y medir BkRead */
    if (only) out("[MSV] MSVONLY=1: se omiten las llamadas a 0x3AFA94/0x698EC8\n");
    if (!only) {
        out("[MSV] ===== ANTES de crear el sector 0x31 =====\n");
        stubs_on(1);
        medir("A1 0x3AFA94(msv real)", fbm_base + 0x3afa94 + 1, msv);
        medir("B1 0x698EC8(this)", fbm_base + 0x698ec8 + 1, ifo);
        medir("A1b 0x3AFA94(msv real) 2a", fbm_base + 0x3afa94 + 1, msv);
        stubs_on(0);
    }

    out("[MSV] ===== creando el sector 0x31 (EWBDFD 4 3 0 + InitB 6 3) =====\n");
    stubs_on(0);
    fbm_cmd("EWBDFD 4 3 0");
    tabla_estatica("tras-EWBDFD");
    buscar(6, 3);
    fbm_cmd("InitB 6 3");
    dump("tras-InitB-6-3");
    comparar_imagenes("tras-InitB");
    buscar(6, 3);

    out("[MSV] ===== DESPUES de crear el sector 0x31 =====\n");
    if (!only) {
    stubs_on(1);
    medir("A2 0x3AFA94(msv real)", fbm_base + 0x3afa94 + 1, msv);
    medir("B2 0x698EC8(this)", fbm_base + 0x698ec8 + 1, ifo);
    medir("A2b 0x3AFA94(msv real) 2a", fbm_base + 0x3afa94 + 1, msv);
    medir("B2b 0x698EC8(this) 2a", fbm_base + 0x698ec8 + 1, ifo);
    stubs_on(0);
    }
    leer(0x04, 3);
    dump("despues");
    comparar_imagenes("fin");

    out("[MSV] ===== objetos sinteticos =====\n");
    sinteticos(msv);

    { unsigned long w = 0; if (leer8(ifo + 0x23, &w)) out("[MSV] mb_load tras todo: [+0x23]=%#lx\n", w); }
    out("[FBMC] FIN\n");
    return 0;
}


__attribute__((constructor)) static void msv_init(void) {
    const char *e = getenv("MSVPROBE");
    if (!e) return;
    unsigned s = 0;
    while (*e >= '0' && *e <= '9') s = s * 10 + (unsigned)(*e++ - '0');
    pthread_t th;
    if (pthread_create(&th, 0, worker, (void *)(unsigned long)s) == 0) pthread_detach(th);
}
