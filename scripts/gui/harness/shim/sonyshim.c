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
static struct { unsigned id; int cnt; } sems[256];
static int sem_slot(unsigned id) {
    int i, f = -1;
    for (i = 0; i < 256; i++) { if (sems[i].id == id) return i; if (!sems[i].id && f < 0) f = i; }
    sems[f].id = id; sems[f].cnt = 0; return f;
}
static int sem_wait(unsigned id, int tmo_ms) {  /* tmo: 0 = sondeo, -1 = infinito */
    struct timespec ts; int r = 0;
    pthread_mutex_lock(&semlock);
    int i = sem_slot(id);
    if (tmo_ms > 0) { clock_gettime(CLOCK_REALTIME, &ts); ts.tv_sec += tmo_ms / 1000; ts.tv_nsec += (tmo_ms % 1000) * 1000000L;
        if (ts.tv_nsec >= 1000000000L) { ts.tv_sec++; ts.tv_nsec -= 1000000000L; } }
    while (sems[i].cnt <= 0) {
        if (tmo_ms == 0) { r = E_TMOUT; break; }
        if (tmo_ms < 0) pthread_cond_wait(&semcond, &semlock);
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
            unsigned char *b = calloc(1, t[1] + 0x40);
            *(void **)t[0] = b + 0x20;
            LOG("uipc valloc qid=%#x size=%u -> %p", w[0], t[1], b + 0x20);
            return 0; }
        case 0: LOG("uipc stat_sem %#x", w[0]); return 0;
        case 1: { int r = sem_wait(w[0], (int)w[1]); LOG("uipc wai_sem %#x tmo=%d -> %d", w[0], (int)w[1], r); return r; }
        case 2: sem_sig(w[0]); LOG("uipc sig_sem %#x", w[0]); return 0;
        case 7: { unsigned *t = (unsigned *)w[1]; LOG("uipc rcv_msg qid=%#x tmo=%d", w[0], (int)t[1]); return kernel_sleep((int)t[1]); }
        case 13: LOG("uipc wait_cb (proxy bloqueado)"); return kernel_sleep(-1);
        case 11: LOG("uipc free qid=%#x msg=%#x", w[0], w[1]); return 0;
        case 4: { unsigned char *m = (unsigned char *)w[1];
            LOG("uipc snd_msg a la cola de kernel %#x (descartado) cab=%02x%02x%02x%02x datos=%08x %08x", w[0], m[-12], m[-11], m[-10], m[-9],
                ((unsigned *)m)[0], ((unsigned *)m)[1]); return 0; }
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
        if (v >= maps[i].lo && v < maps[i].hi) { fprintf(stderr, "[shim]   %08x %s+%#x\n", v, maps[i].name, v - maps[i].lo + maps[i].off); return; }
}
static void on_usr1(int sig, siginfo_t *si, void *ctx) {  /* diagnóstico: PC, LR y direcciones de código halladas en la pila */
    ucontext_t *uc = ctx; unsigned *sp = (unsigned *)uc->uc_mcontext.arm_sp;
    load_maps();
    fprintf(stderr, "[shim] --- pila (SIGUSR1) ---\n");
    sym(uc->uc_mcontext.arm_pc); sym(uc->uc_mcontext.arm_lr);
    for (int i = 0; i < 300; i++) sym(sp[i]);
    (void)sig; (void)si;
}
__attribute__((constructor)) static void shim_init(void) { struct sigaction sa; memset(&sa, 0, sizeof sa); sa.sa_sigaction = on_usr1; sa.sa_flags = SA_SIGINFO; sigaction(SIGUSR1, &sa, 0); }
