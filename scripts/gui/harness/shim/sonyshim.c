/* Capa LD_PRELOAD del arnés de la UI (G22-B): sustituye los dispositivos del kernel 3.0.27 de Sony que el userland de la cámara
 * espera (/dev/uipc, ...) y registra el resto de accesos a /dev. Compilar con build.sh (clang --target=arm, glibc 2.11 de la cámara). */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <ucontext.h>
#include <signal.h>
#include <errno.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define MAXFD 1024
enum { D_NONE = 0, D_UIPC, D_GENERIC };
static unsigned char kind[MAXFD];
static char devname[MAXFD][32];

#define LOG(...) do { fprintf(stderr, "[shim] " __VA_ARGS__); fputc('\n', stderr); } while (0)

#define E_TMOUT (-1022)
static pthread_mutex_t semlock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t semcond = PTHREAD_COND_INITIALIZER;
static struct { unsigned id; int cnt; } sems[16384];
static int sem_slot(unsigned id) {
    int i, f = -1;
    for (i = 0; i < 16384; i++) { if (sems[i].id == id) return i; if (!sems[i].id && f < 0) f = i; }
    if (f < 0) { LOG("tabla de semáforos llena"); abort(); }
    sems[f].id = id; sems[f].cnt = (id == 0x83037a) ? 0 : 1; return f;  /* shortcut: cuenta inicial 1 (cerrojos); 0x83037a es la señal de salida de im.elf. Mejorar si algún semáforo de señal debe empezar en 0 */
}
static int sem_wait(unsigned id, int tmo_ms) {  /* tmo: 0 = sondeo, -1 = infinito */
    struct timespec ts; int r = 0;
    pthread_mutex_lock(&semlock);
    int i = sem_slot(id);
    if (tmo_ms > 0) { clock_gettime(CLOCK_REALTIME, &ts); ts.tv_sec += tmo_ms / 1000; ts.tv_nsec += (tmo_ms % 1000) * 1000000L;
        if (ts.tv_nsec >= 1000000000L) { ts.tv_sec++; ts.tv_nsec -= 1000000000L; } }
    while (sems[i].cnt <= 0) {
        if (tmo_ms == 0) { r = E_TMOUT; break; }
        if (tmo_ms < 0) {  /* tras 8 s sin señal, vuelca la pila una vez por semáforo */
            struct timespec t8; clock_gettime(CLOCK_REALTIME, &t8); t8.tv_sec += 8;
            if (pthread_cond_timedwait(&semcond, &semlock, &t8)) {
                static unsigned vistos[32]; static int nv; int k, ya = 0;
                for (k = 0; k < nv; k++) if (vistos[k] == id) ya = 1;
                if (!ya && nv < 32) { vistos[nv++] = id; fprintf(stderr, "[shim] BLOQUEO sem %#x >8s\n", id); raise(SIGUSR1); }
            }
        }
        else if (pthread_cond_timedwait(&semcond, &semlock, &ts)) { r = E_TMOUT; break; }
    }
    if (!r) sems[i].cnt--;
    pthread_mutex_unlock(&semlock);
    return r;
}
static void sem_sig(unsigned id) { pthread_mutex_lock(&semlock); sems[sem_slot(id)].cnt++; pthread_cond_broadcast(&semcond); pthread_mutex_unlock(&semlock); }
static int kernel_sleep(int tmo_ms) {  /* espera de una cola de kernel que nunca recibe nada */
    if (tmo_ms == 0) return E_TMOUT;
    if (tmo_ms < 0) for (;;) sleep(3600);
    usleep((unsigned)tmo_ms * 1000u);
    return E_TMOUT;
}

static int real_open_call(const char *p, int fl, mode_t m, int is64) {
    static int (*o)(const char *, int, ...), (*o64)(const char *, int, ...);
    if (!o) { o = dlsym(RTLD_NEXT, "open"); o64 = dlsym(RTLD_NEXT, "open64"); }
    return (is64 ? o64 : o)(p, fl, m);
}

static int fake_open(const char *p, int fl, mode_t m, int is64) {
    if (strncmp(p, "/dev/", 5) != 0 && strncmp(p, "/proc/self", 10) != 0 && strncmp(p, "/tmp/", 5) != 0) {
        int r = real_open_call(p, fl, m, is64); LOG("open(%s) -> %d", p, r); return r;
    }
    if (strncmp(p, "/dev/", 5) != 0 || !strcmp(p, "/dev/null") || !strcmp(p, "/dev/zero") || !strcmp(p, "/dev/urandom") ||
        !strcmp(p, "/dev/random") || !strncmp(p, "/dev/pts", 8) || !strcmp(p, "/dev/tty") || !strcmp(p, "/dev/console"))
        return real_open_call(p, fl, m, is64);
    int fd;
    if (!strcmp(p, "/dev/uipc")) {
        fd = real_open_call("/tmp/uipc.shm", O_RDWR | O_CREAT, 0666, is64);
        if (fd >= 0) { ftruncate(fd, 0x80000); unsigned v = 8; pwrite(fd, &v, 4, 0x10); kind[fd] = D_UIPC; }  /* [base+0x10] = nº de hilos proxy que arranca u_osal_reg_msg_queue_cb */
    } else {
        fd = real_open_call("/dev/null", O_RDWR, 0, is64);  /* dispositivo no modelado: fd inerte, queda registrado */
        if (fd >= 0) kind[fd] = D_GENERIC;
    }
    if (fd >= 0) strncpy(devname[fd], p, 31);
    LOG("open(%s, %#x) -> %d (%s)", p, fl, fd, fd >= 0 && kind[fd] == D_UIPC ? "uipc" : "generico");
    return fd;
}

int open(const char *p, int fl, ...) { va_list a; va_start(a, fl); mode_t m = va_arg(a, mode_t); va_end(a); return fake_open(p, fl, m, 0); }
int open64(const char *p, int fl, ...) { va_list a; va_start(a, fl); mode_t m = va_arg(a, mode_t); va_end(a); return fake_open(p, fl, m, 1); }

int close(int fd) {
    static int (*c)(int);
    if (!c) c = dlsym(RTLD_NEXT, "close");
    if (fd >= 0 && fd < MAXFD) kind[fd] = D_NONE;
    return c(fd);
}

/* Servicio de backup (backup.ko): mensaje de 64 B {op, resultado, nº, qid, -, -, ids...}.
 * Almacén: /usr/share/bk.tbl = registros {id, len, datos rellenados a 4} generados del volcado NVRAM (gen_bk.py). */
#include <sys/syscall.h>
static unsigned char *bk; static long bklen;
static void bk_load(void) {
    static int done; if (done) return; done = 1;
    int fd = syscall(SYS_open, "/usr/share/bk.tbl", 0);
    if (fd < 0) { LOG("bk.tbl ausente"); return; }
    long sz = syscall(SYS_lseek, fd, 0, 2); syscall(SYS_lseek, fd, 0, 0);
    bk = malloc(sz);
    for (long o = 0; o < sz;) { long r = syscall(SYS_read, fd, bk + o, sz - o); if (r <= 0) break; o += r; }
    bklen = sz; syscall(SYS_close, fd); LOG("bk.tbl %ld B", bklen);
}
static unsigned *bk_find(unsigned id, unsigned *len) {
    bk_load();
    for (long o = 0; o + 8 <= bklen; o += 8 + ((((unsigned *)(bk + o))[1] + 3) & ~3u))
        if (((unsigned *)(bk + o))[0] == id) { *len = ((unsigned *)(bk + o))[1]; return (unsigned *)(bk + o + 8); }
    return 0;
}
static void backup_service(unsigned *m) {
    unsigned op = m[0], n = m[2], *id = m + 6, len = 0, *d = bk_find(id[0], &len);
    m[1] = 0;
    switch (op) {
    case 0: m[1] = d ? len : 0; break;                                          /* get_datasize */
    case 3: if (d && n >= 2 && id[1]) memcpy((void *)id[1], d, len); m[1] = d ? len : 0; break;     /* read(id, buf) */
    case 4: m[1] = d ? *d : 0; break;                                           /* read_4Byte */
    case 8: break;                                                              /* write: se descarta */
    default: LOG("backup op=%u n=%u id0=%#x (sin modelar)", op, n, id[0]);
    }
    if (getenv("BKV") || !d) LOG("backup op=%u n=%u id=%#x len=%u r=%#x %s", op, n, id[0], len, m[1], d ? "" : "ausente");
}

/* Servicios de kernel por snd_sync_direct (mm 0x910042, ...). shortcut: sin modelar, responde 0 */
static int direct_service(unsigned qid, unsigned *m) { (void)qid; (void)m; return 0; }

int ioctl(int fd, unsigned long req, ...) {
    static int (*r)(int, unsigned long, ...);
    va_list a; va_start(a, req); void *arg = va_arg(a, void *); va_end(a);
    if (fd >= 0 && fd < MAXFD && kind[fd] == D_UIPC) {
        unsigned idx = req & 0x7fffffff;
        if (idx == 0x10) {  /* connect: {tamaño memoria compartida, montón, reservado, ?} (valores de __k_4u_connect) */
            unsigned *o = *(unsigned **)((char *)arg + 4);
            o[0] = 0x80000; o[1] = 0x20000; o[2] = 0x8000; o[3] = 0;
            return 0;
        }
        unsigned *w = (unsigned *)arg;
        switch (idx) {
        case 10: {  /* valloc_msg_wait {qid, &{out, size, tmo}}: mensaje para una cola de kernel (se descarta al enviarlo) */
            unsigned *t = (unsigned *)w[1];
            unsigned char *b = calloc(1, t[1] + 0x240);
            *(void **)t[0] = b + 0x20;
            if (getenv("VERB")) LOG("uipc valloc qid=%#x size=%u -> %p", w[0], t[1], b + 0x20);
            return 0; }
        case 0: LOG("uipc stat_sem %#x", w[0]); return 0;
        case 1: { LOG("uipc wai_sem? %#x tmo=%d", w[0], (int)w[1]); int r = sem_wait(w[0], (int)w[1]); LOG("uipc wai_sem %#x tmo=%d -> %d", w[0], (int)w[1], r); return r; }
        case 2: sem_sig(w[0]); LOG("uipc sig_sem %#x", w[0]); return 0;
        case 7: { unsigned *t = (unsigned *)w[1]; LOG("uipc rcv_msg qid=%#x tmo=%d", w[0], (int)t[1]);
            if ((int)t[1] < 0 && getenv("RCVSTACK")) { static unsigned vq[64]; static int nq; int k, ya = 0; for (k = 0; k < nq; k++) if (vq[k] == w[0]) ya = 1; if (!ya && nq < 64) { vq[nq++] = w[0]; raise(SIGUSR1); } }
            return kernel_sleep((int)t[1]); }
        case 13: LOG("uipc wait_cb (proxy bloqueado)"); return kernel_sleep(-1);
        case 5: {  /* snd_sync_msg {qid, msg}: 0x8f013a es el registro de trazas (u16 + texto "%4X %s %s") */
            unsigned char *m = *(unsigned char **)w[1];  /* w[1] -> {msg, ...} */
            if (w[0] == 0x8f013a) { if (m[2]) LOG("LOG %s", (char *)m + 2); else if (getenv("VERB")) { char t[200]; int k, o = 0; for (k = 0; k < 40; k++) o += snprintf(t + o, sizeof t - o, "%02x", m[k]); LOG("LOGRAW %s", t); } }
            else if (w[0] == 0x3e014d) backup_service((unsigned *)m);
            else if (w[0] == 0x14c0424 && ((unsigned *)m)[0] == 7) {  /* área de memoria por nombre (dmm): {7, nombre[16], estado, phys, tamaño, ?} */
                static unsigned next = 0x80000000;
                unsigned *r = (unsigned *)m + 5;
                r[0] = 0; r[1] = next; r[2] = 0x4000000; r[3] = 0; next += 0x4000000;  /* shortcut: 64 MiB por área en orden; tamaños reales en DmmConfig.bin */
                LOG("dmm área '%s' -> phys %#x size %#x", (char *)m + 4, r[1], r[2]); return 0; }
            else LOG("uipc snd_sync_msg qid=%#x datos=%08x %08x %08x %08x", w[0], ((unsigned *)m)[0], ((unsigned *)m)[1], ((unsigned *)m)[2], ((unsigned *)m)[3]);
            return 0; }
        case 12: {  /* dynamic_id {0, &{tipo, grupo, &id}}: tipo 0x32 = semáforo nuevo */
            static unsigned next = 0x4000;
            unsigned *t = (unsigned *)w[1];
            if (t[0] == 0x32 && t[2]) { unsigned id = (t[1] << 16) | next++; *(unsigned *)t[2] = id; LOG("uipc dynamic_id sem -> %#x", id); }
            else LOG("uipc dynamic_id tipo=%#x grupo=%#x (sin salida)", t[0], t[1]);
            return 0; }
        case 11: if (getenv("VERB")) LOG("uipc free qid=%#x msg=%#x", w[0], w[1]); return 0;
        case 4: { unsigned char *m = (unsigned char *)w[1];
            if (w[0] == 0x8f0139 || w[0] == 0x8f013a) {  /* registro de trazas asíncrono: texto ASCII dentro del mensaje */
                char t[420]; int k; for (k = 0; k < 410; k++) t[k] = (m[k] >= 32 && m[k] < 127) ? m[k] : '.'; t[410] = 0;
                { char c[420]; int o = 0, pd = 1; for (k = 0; t[k]; k++) { if (t[k] == '.') { if (!pd) c[o++] = ' '; pd = 1; } else { c[o++] = t[k]; pd = 0; } } c[o] = 0; if (o > 6) LOG("TRAZA %s", c); }
                if (strstr(t, "MMapBase")) { char h[500]; int o = 0; for (k = 0; k < 200; k++) o += snprintf(h + o, sizeof h - o, "%02x", m[k]); LOG("TRAZAHEX %s", h); }
                return 0; }
            if (w[0] == 0x9a015a || w[0] == 0x9c015b) { static int n; if (n++ < 4) raise(SIGUSR1); if (n > 5) { usleep(20000); return 0; } }  /* bucle HDMI: pila y silencio */
            LOG("uipc snd_msg a la cola de kernel %#x (descartado) cab=%02x%02x%02x%02x datos=%08x %08x", w[0], m[-12], m[-11], m[-10], m[-9],
                ((unsigned *)m)[0], ((unsigned *)m)[1]); return 0; }
        case 6: { unsigned char *m = (unsigned char *)w[1]; char h[200]; int k, o = 0;
            for (k = 0; k < 64; k++) o += snprintf(h + o, sizeof h - o, "%02x", m[k]);
            if (getenv("VERB")) LOG("uipc snd_sync_direct qid=%#x msg=%s", w[0], h); return direct_service(w[0], (unsigned *)m); }
        default: LOG("uipc ioctl idx=%u args %#x %#x (ignorada)", idx, w[0], w[1]); return 0;
        }
    }
    if (fd >= 0 && fd < MAXFD && kind[fd] == D_GENERIC) { LOG("ioctl(%s, %#lx, %p)", devname[fd], req, arg); return 0; }
    if (!r) r = dlsym(RTLD_NEXT, "ioctl");
    return r(fd, req, arg);
}

static unsigned hex(const char *p, char **end) {
    unsigned v = 0;
    for (;; p++) { int c = *p; if (c >= '0' && c <= '9') v = v * 16 + c - '0'; else if (c >= 'a' && c <= 'f') v = v * 16 + c - 'a' + 10; else break; }
    *end = (char *)p; return v;
}
static void efp(const char *f, ...) {  /* escritura sin cerrojo de stderr: usable desde el manejador de señal */
    char b[300]; va_list v; va_start(v, f); int n = vsnprintf(b, sizeof b, f, v); va_end(v);
    if (n > 0) { if (n > (int)sizeof b - 1) n = sizeof b - 1; write(2, b, n); }
}
static struct { unsigned lo, hi, off; char name[96]; } maps[512];
static int nmaps;
static void load_maps(void) {
    FILE *f = fopen("/proc/self/maps", "r"); char line[256]; nmaps = 0;
    while (f && fgets(line, sizeof line, f) && nmaps < 512) {
        char *e; unsigned lo = hex(line, &e), hi = hex(e + 1, &e);
        char *perm = e + 1, *p = perm + 5; unsigned off = hex(p, &e);
        if (perm[2] == 'x') {
            char *nm = strrchr(line, ' '); if (nm) { nm++; nm[strcspn(nm, "\n")] = 0; }
            maps[nmaps].lo = lo; maps[nmaps].hi = hi; maps[nmaps].off = off; strncpy(maps[nmaps].name, nm ? nm : "", 95); nmaps++;
        }
    }
    if (f) fclose(f);
}
static void sym(unsigned v) {
    for (int i = 0; i < nmaps; i++)
        if (v >= maps[i].lo && v < maps[i].hi) { efp("[shim]   %08x %s+%#x\n", v, maps[i].name, v - maps[i].lo + maps[i].off); return; }
}
static void on_usr1(int sig, siginfo_t *si, void *ctx) {  /* diagnóstico: PC, LR y direcciones de código halladas en la pila */
    ucontext_t *uc = ctx; unsigned *sp = (unsigned *)uc->uc_mcontext.arm_sp;
    if (!nmaps) load_maps();
    char nm[24] = {0}; syscall(SYS_prctl, 16, nm); efp("[shim] --- pila (sig %d tid %ld %s) pc/lr:\n", sig, (long)syscall(SYS_gettid), nm); efp("[shim]   raw pc=%08lx lr=%08lx\n", uc->uc_mcontext.arm_pc, uc->uc_mcontext.arm_lr); sym(uc->uc_mcontext.arm_pc); sym(uc->uc_mcontext.arm_lr);
    sym(uc->uc_mcontext.arm_pc); sym(uc->uc_mcontext.arm_lr);
    for (int i = 0; i < 300; i++) { if (((unsigned long)(sp + i) & 0xfff) == 0 || i == 0) { if (msync((void *)((unsigned long)(sp + i) & ~0xfffUL), 1, MS_ASYNC)) break; } sym(sp[i]); }  /* no cruzar el final de la pila */
    (void)sig; (void)si;
}
#include <dirent.h>
/* DUMPAT=n: a los n s manda SIGUSR1 a cada hilo (uno por segundo) para ver dónde está parado cada uno */
static int num(const char *t) { int v = 0; while (*t >= '0' && *t <= '9') v = v * 10 + *t++ - '0'; return v; }  /* sin atoi: el sysroot nuevo enlaza __isoc23_strtol, que la glibc 2.11 no tiene */
static void *dumper(void *a) {
    sleep(num(getenv("DUMPAT"))); (void)a; load_maps();
    DIR *d = opendir("/proc/self/task"); struct dirent *e; int tids[512], n = 0;
    while (d && (e = readdir(d)) && n < 512) if (e->d_name[0] != '.') tids[n++] = num(e->d_name);
    if (d) closedir(d); efp("[shim] dumper hilos=%d\n", n);
    for (int i = 0; i < n; i++) { syscall(SYS_tgkill, getpid(), tids[i], SIGUSR1); sleep(1); }
    return 0;
}
__attribute__((constructor)) static void shim_init(void) { if (getenv("DUMPAT")) { pthread_t th; pthread_create(&th, 0, dumper, 0); } struct sigaction sa; memset(&sa, 0, sizeof sa); sa.sa_sigaction = on_usr1; sa.sa_flags = SA_SIGINFO; sigaction(SIGUSR1, &sa, 0);
    sa.sa_flags = SA_SIGINFO | SA_RESETHAND; sigaction(SIGSEGV, &sa, 0); sigaction(SIGBUS, &sa, 0); sigaction(SIGILL, &sa, 0); sigaction(SIGABRT, &sa, 0); }  /* un fallo imprime la pila y se reintenta por defecto (core) */

/* Experimento (SKIPFN=717830,...): sustituye esas funciones Thumb de libObj por «movs r0,#0; bx lr» (devuelven éxito sin hacer nada). */
static unsigned long hexv(const char *s, const char **end) { unsigned long v = 0; for (;; s++) { int c = *s; if (c >= '0' && c <= '9') c -= '0'; else if (c >= 'a' && c <= 'f') c -= 'a' - 10; else break; v = v * 16 + c; } if (end) *end = s; return v; }
/* Experimento (TRACEFN=716800,6cd1e0,...): traza de una sola vez (UDF + restauración) de la entrada de esas funciones de libObj: r0-r3 y lr. */
static struct { unsigned long pc; unsigned short orig; } trc[32]; static int ntrc; static unsigned long trc_base;
static void on_trace(int sig, siginfo_t *si, void *u) {
    mcontext_t *c = &((ucontext_t *)u)->uc_mcontext; unsigned long pc = c->arm_pc & ~1UL; int i;
    for (i = 0; i < ntrc; i++) if (trc[i].pc == pc) {
        LOG("TRACE %lx r0=%lx r1=%lx r2=%lx r3=%lx lr=%lx", pc, c->arm_r0, c->arm_r1, c->arm_r2, c->arm_r3, c->arm_lr);
        for (const char *e = getenv("TRACEPEEK"); e && *e; ) { unsigned long a = hexv(e, &e); LOG("  PEEK %lx = %08x", a, *(unsigned *)(trc_base + a)); while (*e == ',') e++; }
        *(unsigned short *)pc = trc[i].orig; __builtin___clear_cache((char *)pc, (char *)pc + 2); return;
    }
    signal(SIGILL, SIG_DFL);
}
static void trace_fns(unsigned long base) {
    trc_base = base;
    struct sigaction sa; memset(&sa, 0, sizeof sa); sa.sa_sigaction = on_trace; sa.sa_flags = SA_SIGINFO | SA_NODEFER; sigaction(SIGILL, &sa, 0);
    for (const char *e = getenv("TRACEFN"); e && *e && ntrc < 32; ) {
        unsigned long a = hexv(e, &e), pc = base + a; unsigned short *p = (unsigned short *)pc;
        mprotect((void *)(pc & ~4095UL), 8192, PROT_READ | PROT_WRITE | PROT_EXEC);
        trc[ntrc].pc = pc; trc[ntrc++].orig = *p; *p = 0xde00; __builtin___clear_cache((char *)p, (char *)p + 2);
        while (*e == ',') e++;
    }
}
/* Experimento (WATCH=dir): hilo que sondea cada ms la palabra libObj+dir y registra sus cambios. */
static unsigned long watch_addr;
static void *watcher(void *a) { volatile unsigned *p = (unsigned *)watch_addr; unsigned old = *p; LOG("WATCH inicio %p = %08x", (void *)p, old); for (;;) { unsigned v = *p; if (v != old) { LOG("WATCH %p %08x -> %08x", (void *)p, old, v); old = v; } usleep(1000); } return 0; }
static void skip_fns(void) {
    char ln[256]; unsigned long base = 0; FILE *m = fopen("/proc/self/maps", "r");
    while (m && fgets(ln, sizeof ln, m)) if (strstr(ln, "libObj.so")) { base = hexv(ln, 0); break; }
    if (m) fclose(m);
    if (!base) { LOG("SKIPFN: libObj no hallada"); return; }
    if (getenv("POKE")) {  /* POKE=dir=malloc: escribe la dirección de malloc en libObj+dir (asignador del GPU de DMP, experimento) */
        const char *e = getenv("POKE"); unsigned long a = hexv(e, &e); *(void **)(base + a) = (void *)malloc; LOG("POKE libObj+%#lx = malloc (%p)", a, (void *)malloc);
    }
    if (getenv("TRACEFN")) trace_fns(base);
    if (getenv("WATCH") && !watch_addr) { pthread_t th; watch_addr = base + hexv(getenv("WATCH"), 0); pthread_create(&th, 0, watcher, 0); }
    for (const char *e = getenv("SKIPFN"); e && *e; ) {
        unsigned long a = hexv(e, &e); unsigned char *p = (unsigned char *)(base + a);
        unsigned long pg = (unsigned long)p & ~4095UL;
        mprotect((void *)pg, 8192, PROT_READ | PROT_WRITE | PROT_EXEC);
        unsigned v = 0; if (*e == '=') v = hexv(e + 1, &e) & 0xff;  /* dir=v: devuelve v (0..255) */
        p[0] = v; p[1] = 0x20; p[2] = 0x70; p[3] = 0x47; __builtin___clear_cache((char *)p, (char *)p + 4);
        LOG("SKIPFN %#lx parcheada (base %#lx, ret %u)", a, base, v);
        while (*e == ',') e++;
    }
}
void *dlopen(const char *f, int fl) {
    static void *(*d)(const char *, int);
    if (!d) d = dlsym(RTLD_NEXT, "dlopen");
    LOG("dlopen(%s) ...", f ? f : "(null)");
    void *h = d(f, fl); LOG("dlopen(%s) -> %p%s%s", f ? f : "(null)", h, h ? "" : " ERR=", h ? "" : dlerror());
    if (h && f && strstr(f, "libObj.so") && (getenv("SKIPFN") || getenv("TRACEFN") || getenv("WATCH") || getenv("POKE"))) skip_fns();
    return h;
}
int system(const char *c) {
    static int (*sy)(const char *);
    if (!sy) sy = dlsym(RTLD_NEXT, "system");
    int r = sy(c); LOG("system(%s) -> %d", c ? c : "(null)", r); return r;
}

/* mmap de dispositivos no modelados (/dev/mem, fb, ...): memoria anónima a cero */
void *mmap(void *a, size_t l, int pr, int fl, int fd, off_t o) {
    static void *(*m)(void *, size_t, int, int, int, off_t);
    if (!m) m = dlsym(RTLD_NEXT, "mmap");
    if (fd >= 0 && fd < MAXFD && kind[fd] == D_GENERIC) {
        if (!l) l = 0x1000;  /* shortcut: len 0 no es válido; el monitor de MWF lo pide sin argumentos */
        void *r = m(a, l, pr, (fl & ~MAP_SHARED) | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        LOG("mmap(%s, len=%#zx off=%#lx) -> %p (anónima)", devname[fd], l, (long)o, r); return r;
    }
    return m(a, l, pr, fl, fd, o);
}
void *mmap64(void *a, size_t l, int pr, int fl, int fd, off64_t o) { return mmap(a, l, pr, fl, fd, (off_t)o); }

FILE *fopen(const char *p, const char *m) {
    static FILE *(*f)(const char *, const char *);
    if (!f) f = dlsym(RTLD_NEXT, "fopen");
    if (!strcmp(p, "/proc/modules")) {  /* libObj (MemoryAllocator.cpp:45) exige «grm_ma » en /proc/modules: módulos de kernel de Sony simulados */
        FILE *w = f("/tmp/modules", "w");
        if (w) { fputs("grm_ma 1 0 - Live 0x0\ngrm_gles 1 0 - Live 0x0\n", w); fclose(w); p = "/tmp/modules"; }
    }
    FILE *r = f(p, m);
    if (strncmp(p, "/proc/self", 10)) LOG("fopen(%s, %s) -> %p", p, m, (void *)r);
    return r;
}
FILE *fopen64(const char *p, const char *m) { return fopen(p, m); }

/* abort(): vuelca r4-r8/lr de quien llama (los callee-saved siguen intactos al entrar) y sigue con el abort real */
__attribute__((naked)) void abort(void) {
    __asm__ volatile("push {r0-r12,lr}\n mov r0, sp\n bl abort_regs\n pop {r0-r12,lr}\n b abort_real\n");
}
void abort_regs(unsigned *r) {
    fprintf(stderr, "[shim] ABORT r4=%08x r5=%08x r6=%08x r7=%08x r8=%08x lr=%08x\n", r[4], r[5], r[6], r[7], r[8], r[13]);
    sym(r[13]);
}
void abort_real(void) { static void (*a)(void); if (!a) a = dlsym(RTLD_NEXT, "abort"); a(); for (;;); }

/* Experimento (CVWAIT=s): el solicitante de libObj+0x719ed8 (patrón «trabajador», fw 3.21) espera el fin del trabajo sin sostener su
 * cerrojo y puede perder la señal; solo ese punto de llamada espera con tope de s segundos (despertar espurio).
 * El resto de esperas (p. ej. el bucle del trabajador, que no tolera despertares espurios) queda intacto. */
#define _GNU_SOURCE
int pthread_cond_wait(pthread_cond_t *c, pthread_mutex_t *m) {
    static int tmo = -1; static int (*real)(pthread_cond_t *, pthread_mutex_t *);
    if (!real) real = dlsym(RTLD_NEXT, "pthread_cond_wait");
    if (tmo < 0) { const char *e = getenv("CVWAIT"); tmo = 0; while (e && *e >= '0' && *e <= '9') tmo = tmo * 10 + *e++ - '0'; }
    if (tmo) {
        Dl_info di; void *ra = __builtin_return_address(0);
        if (dladdr(ra, &di) && di.dli_fname && strstr(di.dli_fname, "libObj.so") && (unsigned long)ra - (unsigned long)di.dli_fbase == 0x719ee1) {
            LOG("cond_wait de grm_init: tope %d s", tmo);
            struct timespec ts; clock_gettime(CLOCK_REALTIME, &ts); ts.tv_sec += tmo;
            pthread_cond_timedwait(c, m, &ts); return 0;
        }
    }
    return real(c, m);
}
/* Registro de munmap grandes (MMapBase de libObj aborta si desmapea algo no mapeado). */
int munmap(void *a, size_t l) {
    static int (*m)(void *, size_t);
    if (!m) m = dlsym(RTLD_NEXT, "munmap");
    int r = m(a, l);
    if (l >= 0x100000 || r) LOG("munmap(%p, %#zx) -> %d", a, l, r);
    return r;
}
