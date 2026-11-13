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
#include <poll.h>
#include <sys/select.h>
#include <dirent.h>

/* getenv con tabla de cambios en caliente («E NOMBRE=valor» del anfitrión; valor vacío = quitar). setenv() desde otro hilo mientras el resto llama a getenv
 * corrompía environ (glibc 2.11, SIGSEGV en ULOGIOD_MAIN): aquí la tabla solo se rellena y nunca se reasigna. shortcut: 24 cambios, nombre ≤ 23 y valor ≤ 79. */
extern char **environ;
static struct { char n[24]; char v[80]; volatile int on; } hotenv[24];
static volatile int wl_v = -1, wla_v = -1;  /* cachés de WAITLOG/WLALL; el cambio en caliente los invalida */
static void hotenv_set(const char *n, const char *v) {
    int k, free_k = -1; if (strlen(n) > 23 || strlen(v) > 79) return;
    for (k = 0; k < 24; k++) { if (hotenv[k].on && !strcmp(hotenv[k].n, n)) break; if (!hotenv[k].on && free_k < 0) free_k = k; }
    if (k == 24) { if (free_k < 0) return; k = free_k; hotenv[k].on = 0; strcpy(hotenv[k].n, n); }
    strcpy(hotenv[k].v, v); hotenv[k].on = *v ? 1 : 2; /* 2 = ocultar */
    wl_v = wla_v = -1;
}
char *getenv(const char *n) {
    for (int k = 0; k < 24; k++) if (hotenv[k].on && !strcmp(hotenv[k].n, n)) return hotenv[k].on == 1 ? hotenv[k].v : 0;
    size_t l = strlen(n); for (char **e = environ; e && *e; e++) if (!strncmp(*e, n, l) && (*e)[l] == '=') return *e + l + 1;
    return 0;
}

#define MAXFD 1024
enum { D_NONE = 0, D_UIPC, D_GENERIC };
static unsigned char kind[MAXFD];
static char devname[MAXFD][32];

#define LOG(...) do { fprintf(stderr, getenv("TIDLOG") ? "[shim %ld] " : "[shim] ", (long)syscall(224)); fprintf(stderr, __VA_ARGS__); fputc('\n', stderr); if (wl_all()) wl_logfwd(__VA_ARGS__); } while (0)

#define E_TMOUT (-1022)
static void live_msg(const char *, const char *, int);
static void menu_track(const char *); static int wl_all(void); static void wl_logfwd(const char *, ...); static void wl_live(const char *, int); static void wl_key(unsigned); static int wl_on(void); static double wl_ts(void); static const char *tname(int, char *, size_t);
static int wl_begin(const char *k, unsigned a, int tmo, void *ra); static void wl_end(int slot);  /* WAITLOG=ms: registro de esperas largas (ver abajo) */
static pthread_mutex_t semlock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t semcond = PTHREAD_COND_INITIALIZER;
static struct { unsigned id; int cnt; } sems[16384];
static int sem_slot(unsigned id) {
    int i, f = -1;
    for (i = 0; i < 16384; i++) { if (sems[i].id == id) return i; if (!sems[i].id && f < 0) f = i; }
    if (f < 0) { LOG("tabla de semáforos llena"); abort(); }
    sems[f].id = id; sems[f].cnt = (id == 0x83037a) ? 0 : 1; return f;  /* shortcut: cuenta inicial 1 (cerrojos); 0x83037a es la señal de salida de im.elf. Mejorar si algún semáforo de señal debe empezar en 0 */
}
static int uipc_sem_wait(unsigned id, int tmo_ms) {  /* tmo: 0 = sondeo, -1 = infinito */
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
        unsigned v = 8;
        if (fd >= 0) { ftruncate(fd, 0x80000); pwrite(fd, &v, 4, 0x10); }  /* [base+0x10] = nº de hilos proxy que arranca u_osal_reg_msg_queue_cb */
    } else
        fd = real_open_call("/dev/null", O_RDWR, 0, is64);  /* dispositivo no modelado: fd inerte, queda registrado */
    if (fd >= MAXFD) { LOG("open(%s): fd %d >= MAXFD, sin modelar", p, fd); return fd; }
    if (fd >= 0) { kind[fd] = strcmp(p, "/dev/uipc") ? D_GENERIC : D_UIPC; strncpy(devname[fd], p, 31); }
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
    if (sz <= 0) { LOG("bk.tbl vacío"); syscall(SYS_close, fd); return; }
    bk = malloc(sz);
    for (long o = 0; o < sz;) { long r = syscall(SYS_read, fd, bk + o, sz - o); if (r <= 0) break; o += r; }
    bklen = sz; syscall(SYS_close, fd); LOG("bk.tbl %ld B", bklen);
}
static unsigned long hexv(const char *s, const char **end);
static unsigned *bk_find(unsigned id, unsigned *len) {
    bk_load();
    { const char *e = getenv("BKSET");  /* BKSET=id_hex=valor_hex[,…]: fuerza un registro de 1–4 bytes (p. ej. 1070140=1: reloj «asentado» para ModelRoot) */
      static unsigned ov[8][2]; static int nov = -1;
      if (nov < 0) { nov = 0; while (e && *e && nov < 8) { const char *q; ov[nov][0] = hexv(e, &q); if (*q != '=') break; ov[nov][1] = hexv(q + 1, &q); nov++; e = *q == ',' ? q + 1 : q; } }
      for (int k = 0; k < nov; k++) if (ov[k][0] == id) { *len = 1; return &ov[k][1]; } }
    for (long o = 0; o + 8 <= bklen; o += 8 + ((((unsigned *)(bk + o))[1] + 3) & ~3u))
        if (((unsigned *)(bk + o))[0] == id) { *len = ((unsigned *)(bk + o))[1]; return (unsigned *)(bk + o + 8); }
    return 0;
}
static int readable(const void *p);
static void backup_service(unsigned *m) {
    unsigned op = m[0], n = m[2], *id = m + 6, len = 0, *d = bk_find(id[0], &len);
    m[1] = 0;
    switch (op) {
    case 0: m[1] = d ? len : 0; break;                                          /* get_datasize */
    case 3: if (d && n >= 2 && id[1]) memcpy((void *)id[1], d, len); m[1] = d ? len : 0; break;     /* read(id, buf) */
    case 30: {  /* nread(id, buf, tamaño): copia min(len, tamaño) a buf y devuelve los bytes copiados (SystemImpl::initialize_setting exige == sizeof(setting)) */
        unsigned c = d ? (len < id[2] ? len : id[2]) : 0;
        if (c && n >= 3 && id[1]) memcpy((void *)id[1], d, c);
        m[1] = c; break; }
    case 4: m[1] = d ? *d : 0; break;                                           /* read_4Byte */
    case 8: {  /* Backup_write(grupo = id>>16, id, buf) medido en la UI (los argumentos van en m[6..8]; el tamaño es el del registro): se aplica a la tabla en RAM y se avisa al anfitrión («NV id hex»), que lo guarda en nvram.json del perfil y lo carga sobre bk.tbl en el siguiente arranque en frío */
        unsigned wid = id[1], wl = 0, *wd = n >= 3 ? bk_find(wid, &wl) : 0; m[1] = 0;
        if (wd && wl && wl <= 4096 && readable((void *)id[2])) {
            static char ln[8300]; static pthread_mutex_t lm = PTHREAD_MUTEX_INITIALIZER; pthread_mutex_lock(&lm);
            int o = snprintf(ln, sizeof ln, "%x ", wid); for (unsigned i = 0; i < wl; i++) o += sprintf(ln + o, "%02x", ((unsigned char *)id[2])[i]);
            memcpy(wd, (void *)id[2], wl); live_msg("NV", ln, o); if (getenv("SETLOG")) LOG("NV %s", ln); pthread_mutex_unlock(&lm); m[1] = wl;
        } else LOG("backup write id=%#x sin registro o buffer ilegible", wid);
        return;  /* sin la línea de registro genérica: id[0] no es el id */
    }
    default: LOG("backup op=%u n=%u id0=%#x (sin modelar)", op, n, id[0]);
    }
    if (getenv("BKV") || !d) LOG("backup op=%u n=%u id=%#x len=%u r=%#x %s", op, n, id[0], len, m[1], d ? "" : "ausente");
}

/* Servicios de kernel por snd_sync_direct (mm 0x910042, ...). shortcut: sin modelar, responde 0 */
/* 0x90013d cmd 2 = osal_get_date (ModelRoot::getDateInfo, libObj+0x63c2bc): +0x12 estado, +0x1c tipo (0 sin hora, 1/3 asentada; DATETYPE, 1 por defecto). */
static unsigned long hexv(const char *s, const char **end);
/* el arg de ioctl a veces es un entero (p. ej. un qid de libInfraKikiLogGenerator): solo se lee si la página está mapeada */
static int readable(const void *p) { return (unsigned long)p > 0x10000 && msync((void *)((unsigned long)p & ~4095UL), 4, MS_ASYNC) == 0; }
static volatile long long date_base, date_mono0; static volatile int date_have, date_type = -1;  /* date_type: «Y n» del anfitrión (diagnóstico) pisa DATETYPE */
static long long mono_s(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec; }
static long long date_local(void) { return date_have ? date_base + mono_s() - date_mono0 : (long long)time(0); }  /* sin «T» del anfitrión: reloj del invitado (UTC) */
static int direct_service(unsigned qid, unsigned *m) {
    /* Reloj del núcleo (libObj+0x804610, I-InputRepeat, CIFInfraIndctr): 0x910042 devuelve la hora en µs (64 bit, m[6..7]) y 0x910041 duerme hasta el plazo absoluto m[6..7]; sin esto la hora era 0, el plazo
     * (+20 ms) siempre vencido y el hilo giraba al 100 % de CPU. shortcut: unidades (µs) y época (arranque) inferidas del +0x4e20 que suma el llamador, no medidas en la cámara. */
    if (qid == 0x910042 && m[0] == 0x20 || qid == 0x910041 && m[0] == 0x28) {
        struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
        if (qid == 0x910042) { unsigned long long us = t.tv_sec * 1000000ull + t.tv_nsec / 1000; m[6] = (unsigned)us; m[7] = (unsigned)(us >> 32); }
        else { unsigned long long us = m[6] | (unsigned long long)m[7] << 32; t.tv_sec = us / 1000000; t.tv_nsec = us % 1000000 * 1000; clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t, 0); }
        return 0;
    }
    /* 0x900141 orden 3 = osal_get_init_date (libObj+0x4f5b94, desde ActionModelSuspend): fecha inicial de ModelClock (+0x84/+0x8e, INFO_INITIAL_DATE_TIME).
     * Como el callback real libObj+0xb58be8 (0xb58c60…0xb58dbe): lee la NVRAM; año = 0x90000e + 0x90000f; +0x1c y +0x22 a 0; sin registro → estado ≠ 0. */
    if (m[0] == 0x28 && qid == 0x900141 && ((unsigned short *)m)[8] == 3) {
        static const unsigned ids[] = { 0x90000e, 0x90000f, 0x900008, 0x900004, 0x900006, 0x900007, 0x900009, 0x90000a, 0x900005 };
        static const unsigned char off[] = { 0x14, 0, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1e, 0x20 };
        unsigned char *b = (unsigned char *)m; unsigned short *h = (unsigned short *)m; memset(b + 0x14, 0, 0x10);
        for (int k = 0; k < 9; k++) { unsigned l = 0, *d = bk_find(ids[k], &l);
            if (!d) { h[9] = 0xfc04; LOG("direct 0x900141 fecha inicial: falta Backup %#x", ids[k]); return 0; }
            if (k == 1) h[10] += *(unsigned char *)d; else memcpy(b + off[k], d, l > 2 ? 2 : l); }
        h[9] = 0; LOG("direct 0x900141 fecha inicial (NVRAM) -> %u-%u-%u %u:%02u:%02u área %d verano %d", h[10], b[0x16], b[0x17], b[0x18], b[0x19], b[0x1a], (short)h[15], (short)h[16]);
        return 0;
    }
    if (m[0] == 0x28 && ((unsigned short *)m)[8] == 2 && !getenv("NODATE")) {
        unsigned short *h = (unsigned short *)m; const char *e = getenv("DATETYPE");
        h[9] = 0; h[14] = date_type >= 0 ? (unsigned short)date_type : e ? (unsigned short)hexv(e, 0) : 1;
        { time_t tt = (time_t)date_local(); struct tm g; gmtime_r(&tt, &g); unsigned char *b = (unsigned char *)m;  /* formato de libObj+0x4f10dc (osal_get_date): +0x14 año u16; +0x16 mes, día, hora, min, seg (u8); +0x1c tipo */
          h[10] = g.tm_year + 1900; b[0x16] = g.tm_mon + 1; b[0x17] = g.tm_mday; b[0x18] = g.tm_hour; b[0x19] = g.tm_min; b[0x1a] = g.tm_sec; }
        static int n; if (n++ < 40) LOG("direct %#x get_date -> %u-%u-%u %u:%02u:%02u tipo %u (base %d)", qid, h[10], ((unsigned char *)m)[0x16], ((unsigned char *)m)[0x17], ((unsigned char *)m)[0x18], ((unsigned char *)m)[0x19], ((unsigned char *)m)[0x1a], h[14], date_have);
    }
    else if (m[0] == 0x28 && qid == 0x90013d) {  /* otras órdenes del servicio de fecha (¿ajuste de hora?): se registran para modelarlas */
        char b[100]; int o = 0; for (int i = 4; i < 10; i++) o += sprintf(b + o, "%08x ", m[i]);
        LOG("direct %#x fecha cmd=%u datos=%s", qid, ((unsigned short *)m)[8], b);
    }
    return 0;
}

/* Buzones de colas dinámicas de kernel (dynamic_id tipo 0x2a): el servicio 0xd9016e (registro de puerto de vídeo/OSD) se responde copiando la petición. */
static struct { unsigned q; void *msg; } mbx[16];
static unsigned long tron_base; static void trace_fns(unsigned long base);
static unsigned dynq[256]; static int ndynq;  /* colas creadas por dynamic_id tipo 0x2a (solo ellas tienen buzón) */
static pthread_mutex_t mbx_m = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t mbx_c = PTHREAD_COND_INITIALIZER;
static void dynq_add(unsigned q) { pthread_mutex_lock(&mbx_m); if (ndynq < 256) dynq[ndynq++] = q; else LOG("dynq lleno: %#x sin buzón", q); pthread_mutex_unlock(&mbx_m); }
static int is_dynq(unsigned q) { for (int k = 0; k < ndynq; k++) if (dynq[k] == q) return 1; return 0; }
static void mbx_post(unsigned q, const unsigned *req, int req_id0) {  /* req_id0: dmpNative::InternalCmd (0x61003c) espera req_id 0 en +6 (medido con TRACEFN en 0x6a2612: r2=0xe copiado, r3=0 esperado) */
    unsigned char *b = calloc(1, 0x300); unsigned *body = (unsigned *)(b + 0x20); int k;
    memcpy(body, req, 28); body[-1] = 0x61003c; ((unsigned short *)body)[1] = 0;  /* cabecera esperada por 0x6a25e0 y estado 0 */
    if (req_id0) {  /* dmpNative::InternalCmd alloc (0x61003c): petición {1, tamaño, 0, -1, cola, ?:req_id}; respuesta: req_id en +6, phys en +0x10 y
         * tamaño en +0x14 (leídos por 0x6a2626 → MMapBase::Map, que exige phys alineado). shortcut: 'tamaño' = req[1] (0xe1700 en las dos peticiones vistas) */
        static unsigned next_phys = 0xa0000000u; unsigned sz = (req[1] + 0xfffu) & ~0xfffu;
        if (getenv("VERB")) LOG("InternalCmd req [-4..8] %08x | %08x %08x %08x %08x %08x %08x %08x %08x", req[-1], req[0], req[1], req[2], req[3], req[4], req[5], req[6], req[7]);
        ((unsigned short *)body)[3] = (unsigned short)req[5]; body[4] = next_phys; body[5] = req[1]; LOG("InternalCmd alloc size %#x id %u -> phys %#x", req[1], req[5] & 0xffff, next_phys); next_phys += sz;
    }
    pthread_mutex_lock(&mbx_m);
    for (k = 0; k < 16 && mbx[k].msg; k++);
    if (k < 16) { mbx[k].q = q; mbx[k].msg = body; } else { LOG("mbx lleno: respuesta a %#x perdida", q); free(b); }
    pthread_cond_broadcast(&mbx_c); pthread_mutex_unlock(&mbx_m);
}
/* SYNCMBX=qid_hex[,…]: colas con callback síncrono (reg_sync_msg_queue_cb) a las que el propio proceso envía con snd_msg: en la cámara esos envíos
 * los lee un hilo con rcv_msg (im.elf reenvía a 0x94016a lo que recibe de upm.ko); aquí se entregaban otra vez al callback (bucle). Van a un buzón sin tocar el cuerpo. */
static int syncmbx_q(unsigned q) { const char *e = getenv("SYNCMBX"); while (e && *e) { const char *n; unsigned v = hexv(e, &n); if (n == e) break; if (v == q) return 1; e = *n == ',' ? n + 1 : n; } return 0; }
static void mbx_post_raw(unsigned q, const unsigned *req) {
    unsigned char *b = calloc(1, 0x300); unsigned *body = (unsigned *)(b + 0x20); int k;
    memcpy(body, req, 0x30);
    pthread_mutex_lock(&mbx_m);
    for (k = 0; k < 16 && mbx[k].msg; k++);
    if (k < 16) { mbx[k].q = q; mbx[k].msg = body; } else { LOG("mbx lleno: mensaje a %#x perdido", q); free(b); }
    pthread_cond_broadcast(&mbx_c); pthread_mutex_unlock(&mbx_m);
}
/* Mensajes dataflow de libBizFw2 (DataFlowInfraCh::AddDataflowHeader): {cola_resp, 0xa0a0a0a0, u16 1, u16 total, desp=0x14, total} + carga
 * {u16 cate, u16 msg, u16 len, u16 ver, …}. El receptor (URendezvous::ReceiveInfraAckCompMsg) casa remitente (cabecera −1 = cola destino),
 * cate y msg^0x8000 con lo registrado en el envío (AdfCh::SendMsgWithSeqId: 0x58003f); err en carga+8 = 0, resto a cero (p. ej. ADF GetFunc). */
static void dataflow_reply(unsigned src, unsigned q, const unsigned char *req) {
    unsigned char *b = calloc(1, 0x300), *p; unsigned *body = (unsigned *)(b + 0x20); unsigned off = ((const unsigned *)req)[3], k;
    const unsigned short *rp = (const unsigned short *)(req + (off < 0x100 ? off : 0x14));
    body[-1] = src; ((unsigned char *)body)[-8] = 2;  /* osal_msg_size (libosal_uipc+0x4a0c): bloques de 32 B en cabecera−8 → 2*32−12 = 0x34 */
    body[0] = src; body[1] = 0xa0a0a0a0; body[2] = 1 | (0x34u << 16); body[3] = 0x14; body[4] = 0x34;
    p = (unsigned char *)body + 0x14; ((unsigned short *)p)[0] = rp[0]; ((unsigned short *)p)[1] = rp[1] ^ 0x8000; ((unsigned short *)p)[2] = 0x20; ((unsigned short *)p)[3] = rp[3];
    pthread_mutex_lock(&mbx_m);
    for (k = 0; k < 16 && mbx[k].msg; k++);
    if (k < 16) { mbx[k].q = q; mbx[k].msg = body; } else { LOG("mbx lleno: dataflow a %#x perdido", q); free(b); }
    pthread_cond_broadcast(&mbx_c); pthread_mutex_unlock(&mbx_m);
    LOG("snd_msg %#x dataflow cate=%#x msg=%#x -> comp a %#x", src, rp[0], rp[1], q);
}
/* Servicio VDF 0x59000e (g22-respuestas-59000e-900141.md §1): VdfCh::sndRcvAsyncDataflowMsg espera UNA respuesta por petición en la cola
 * de origen (primera palabra del cuerpo). Tipo 2 de ReceiveASync: MSGID 0x8200 (≠ 0xc2019f/0xc20219/0x61003c/0x1590438) y cuerpo de 0x40 B
 * a cero (resultado 0 en rsp+0xc/+0x14) con cuerpo+4 ≠ 0xa0a0a0a0; se copia la cabecera VDF de 8 B (nadie la comprueba). */
static void vdf_reply(unsigned q, const unsigned char *req) {
    unsigned char *b = calloc(1, 0x300); unsigned *body = (unsigned *)(b + 0x20), k; unsigned off = ((const unsigned *)req)[3];
    body[-1] = 0x8200; ((unsigned char *)body)[-8] = 3;  /* 3 bloques de 32 B → 3*32−12 = 0x54 ≥ 0x40 */
    memcpy(body, req + (off < 0x100 ? off : 0x14), 8);
    pthread_mutex_lock(&mbx_m);
    for (k = 0; k < 16 && mbx[k].msg; k++);
    if (k < 16) { mbx[k].q = q; mbx[k].msg = body; } else { LOG("mbx lleno: VDF a %#x perdido", q); free(b); }
    pthread_cond_broadcast(&mbx_c); pthread_mutex_unlock(&mbx_m);
    LOG("snd_msg 0x59000e VDF orden %#x -> respuesta tipo 2 a %#x", ((const unsigned short *)body)[1], q);
}
/* KEYINIT=key:estado:índice,… (hex): estados iniciales que el driver de entrada informa (mensaje de 0x7a0020, receptor libObj+0x806f88: w0 clave,
 * w2 valor, w4 índice físico = palabra 9 de la entrada de evento) para la lista de InfraInput (entradas de 0x44 B: +0 clave, +4 evento, +0x14 estado,
 * 0x7fffffff = desconocido → InputService::getInputEventStatus falla); p. ej. 7000001:1:177 = jack USB (evento 0x15040010).
 * Se envían una vez a 0x7a0020 al ver KEYINITON=texto en el registro de libObj (por defecto, con el toActive de InputService). */
static void keyinit_send(void) {
    static int done; if (done || !is_dynq(0x7a0020)) return; done = 1;
    for (const char *e = getenv("KEYINIT"); e && *e; ) { unsigned km[12] = { 0 }; km[0] = hexv(e, &e); if (*e == ':') km[2] = hexv(e + 1, &e); if (*e == ':') km[4] = hexv(e + 1, &e);
        mbx_post_raw(0x7a0020, km); LOG("KEYINIT key=%#x status=%#x idx=%#x", km[0], km[2], km[4]); while (*e == ',') e++; }
}
static int mbx_take(unsigned q, int tmo, void **out) {  /* 0 = recibido, 1 = cola sin buzón (no dinámica), E_TMOUT = nada en tmo ms */
    int k, r = 1; struct timespec ts;
    if (!is_dynq(q)) return 1;
    if (tmo > 0) { clock_gettime(CLOCK_REALTIME, &ts); ts.tv_sec += tmo / 1000; ts.tv_nsec += (tmo % 1000) * 1000000L;
        if (ts.tv_nsec >= 1000000000L) { ts.tv_sec++; ts.tv_nsec -= 1000000000L; } }
    pthread_mutex_lock(&mbx_m);
    for (;;) {
        for (k = 0; k < 16; k++) if (mbx[k].msg && mbx[k].q == q) { *out = mbx[k].msg; mbx[k].msg = 0; r = 0; goto fin; }
        if (tmo == 0 || (tmo > 0 && pthread_cond_timedwait(&mbx_c, &mbx_m, &ts))) { r = E_TMOUT; break; }
        if (tmo < 0) pthread_cond_wait(&mbx_c, &mbx_m);
    }
fin:
    pthread_mutex_unlock(&mbx_m); return r;
}

static volatile int gpu_live;  /* GPUEMU: la UI ya envía actualizaciones de pantalla (dlopen de viewUnified*.so): a partir de ahí los trabajos terminan con aviso */
static int num(const char *t) { int v = 0; while (*t >= '0' && *t <= '9') v = v * 10 + *t++ - '0'; return v; }  /* sin atoi: el sysroot nuevo enlaza __isoc23_strtol, que la glibc 2.11 no tiene */
/* Colas de kernel con callback de usuario (reg_msg_queue_cb, idx 8). En libosal_uipc.so: los hilos proxy bloqueados en wait_cb (idx 13)
 * reciben {cb, arg, msg, 0} y llaman cb(msg, arg); un envío síncrono (idx 5) a una cola con callback devuelve {cb, arg} al emisor en su
 * propio struct, el emisor llama cb(msg, arg) y repite el ioctl(5) para terminar. */
static struct { unsigned q; void *cb, *arg; } cbs[128]; static int ncbs;
static struct { void *cb, *arg, *msg; } dlv[256]; static unsigned dlv_r, dlv_w;
static pthread_mutex_t cb_m = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t cb_c = PTHREAD_COND_INITIALIZER;
static unsigned long hexv(const char *s, const char **end);
static int cb_find(unsigned q) { for (int k = 0; k < ncbs; k++) if (cbs[k].q == q) return k; return -1; }
static int cb_deliver(unsigned q, void *msg) {  /* 1 = encolado para un hilo proxy */
    pthread_mutex_lock(&cb_m); int k = cb_find(q);
    if (k >= 0) {
        if (dlv_w - dlv_r < 256) { dlv[dlv_w % 256].cb = cbs[k].cb; dlv[dlv_w % 256].arg = cbs[k].arg; dlv[dlv_w % 256].msg = msg; dlv_w++; pthread_cond_signal(&cb_c); }
        else LOG("dlv lleno: mensaje a %#x perdido", q);
    }
    pthread_mutex_unlock(&cb_m); return k >= 0;
}
static void cb_call(void *cb, void *arg, void *msg) {  /* entrega cb(msg, arg) a un hilo proxy (sin cola): para avisos que en la cámara hace un módulo de kernel */
    pthread_mutex_lock(&cb_m);
    if (dlv_w - dlv_r < 256) { dlv[dlv_w % 256].cb = cb; dlv[dlv_w % 256].arg = arg; dlv[dlv_w % 256].msg = msg; dlv_w++; pthread_cond_signal(&cb_c); }
    pthread_mutex_unlock(&cb_m);
}
static void *vdfcb[16];  /* vdf (cola de kernel 0x80003b): comandos pares 2,4,6,8,9 = registro de callbacks de usuario (m[1]); 5 = actualización de pantalla */
static void *vdf_ack(void *a) {  /* petición c (1 exec, 3 break, 5 update, 7 mute) → callback registrado con el comando c+1 (2 exec_cb, 4 break_cb, 6 update_cb, 8 mute_cb); VDFUPD=99: diagnóstico */
    unsigned c = (unsigned)(unsigned long)a; usleep(3000);
    if (getenv("VDFUPD") && num(getenv("VDFUPD")) == 99) { static int once; if (once++) return 0; for (int k = 0; k < 16; k++) if (vdfcb[k]) { cb_call(vdfcb[k], 0, calloc(1, 256)); LOG("vdf: prueba callback del cmd %d (%p)", k, vdfcb[k]); usleep(500000); } return 0; }
    if (c + 1 < 16 && vdfcb[c + 1]) { cb_call(vdfcb[c + 1], 0, calloc(1, 256)); LOG("vdf: petición %u terminada → callback del cmd %u (%p)", c, c + 1, vdfcb[c + 1]); }
    return 0;
}

/* Servicio de memoria grm_ma.ko (cola 0x14c0424, mensaje de 44 B). Código = u16 de m[0]; tabla de grm_ma.ko:ma_user_sync_cb (medida):
 *  1 dmm_open  in=m+4  out=m+28 {estado, phys, tamaño, handle}   2 dmm_close  out=m+8    3 create_msp in={base,tamaño,flag,nombre@m+9} out=m+32 {estado, handle}
 *  4 inválido  5/6 cache flush/invalidate in=m+8 out=m+4          7 findbyname in=nombre@m+4 out=m+20 {estado, phys, tamaño, handle}  8 findbyphys out=m+8
 *  9 malloc in={handle,tamaño,alineación} out=m+16 {estado, ptr}  10 free in={handle,ptr} out=m+16   11-13 compact out=m+8/m+16/m+8.
 * shortcut: cada área son 64 MiB anónimos con asignador de rampa; los tamaños reales vienen de DmmConfig.bin (no está en el firmware extraído). */
static struct { unsigned h, phys, size, off; char name[17]; } msps[64]; static int nmsps; static pthread_mutex_t ma_m = PTHREAD_MUTEX_INITIALIZER;
static unsigned ma_named = 0x80000000u, ma_dmm = 0xb0000000u;
static int msp_new(const char *name, unsigned phys, unsigned size) {  /* con el cerrojo tomado; devuelve el índice */
    if (nmsps >= 64) return -1;
    msps[nmsps].h = 0xca0000u + nmsps + 1; msps[nmsps].phys = phys; msps[nmsps].size = size; msps[nmsps].off = 0;
    strncpy(msps[nmsps].name, name, 16); msps[nmsps].name[16] = 0; return nmsps++;
}
static int msp_by_h(unsigned h) { for (int k = 0; k < nmsps; k++) if (msps[k].h == h) return k; return -1; }
static void ma_service(unsigned *m) {
    unsigned code = m[0] & 0xffff; int k; pthread_mutex_lock(&ma_m);
    switch (code) {
    case 1: { char nm[17]; strncpy(nm, (char *)m + 9, 16); nm[16] = 0;
        for (k = 0; k < nmsps; k++) if (!strcmp(msps[k].name, nm) && msps[k].phys >= 0xb0000000u) break;
        if (k == nmsps) { k = msp_new(nm, ma_dmm, 0x4000000); ma_dmm += 0x4000000; }
        m[7] = k < 0 ? (unsigned)-12 : 0; if (k >= 0) { m[8] = msps[k].phys; m[9] = msps[k].size; m[10] = msps[k].h; }
        LOG("MA open '%s' -> phys %#x handle %#x", nm, k >= 0 ? msps[k].phys : 0, k >= 0 ? msps[k].h : 0); break; }
    case 2: k = msp_by_h(m[1]); if (k >= 0) msps[k].off = 0; m[2] = 0; LOG("MA close %#x (libera todas sus reservas)", m[1]); break;  /* open → malloc(todo) → close → open → malloc… (hal_create) */
    case 3: { char nm[17]; strncpy(nm, (char *)m + 9, 16); nm[16] = 0; k = msp_new(nm, m[1], m[2]);
        m[8] = k < 0 ? (unsigned)-1 : 0; m[9] = k < 0 ? 0 : msps[k].h; LOG("MA create_msp '%s' base %#x size %#x -> handle %#x", nm, m[1], m[2], m[9]); break; }
    case 5: case 6: m[1] = 0; break;
    case 7: { char nm[17]; strncpy(nm, (char *)m + 4, 16); nm[16] = 0;
        for (k = 0; k < nmsps; k++) if (!strcmp(msps[k].name, nm) && msps[k].phys < 0xb0000000u) break;
        if (k == nmsps) { k = msp_new(nm, ma_named, 0x4000000); ma_named += 0x4000000; }
        m[5] = 0; m[6] = msps[k].phys; m[7] = msps[k].size; m[8] = msps[k].h; LOG("MA findbyname '%s' -> phys %#x handle %#x", nm, m[6], m[8]); break; }
    case 8: m[2] = (unsigned)-9; break;
    case 9: { unsigned al = m[3] > 16 ? m[3] : 16; k = msp_by_h(m[1]);
        if (k < 0) { m[4] = (unsigned)-9; m[5] = 0; LOG("MA malloc handle %#x desconocido", m[1]); break; }
        unsigned off = (msps[k].off + al - 1) & ~(al - 1);
        if (off + m[2] > msps[k].size) { m[4] = (unsigned)-12; m[5] = 0; LOG("MA malloc m=%#x %#x %#x en '%s' (off %#x tam %#x): sin espacio", m[1], m[2], m[3], msps[k].name, msps[k].off, msps[k].size); break; }
        m[4] = 0; m[5] = msps[k].phys + off; msps[k].off = off + m[2]; LOG("MA malloc %#x/%#x en '%s' -> %#x", m[2], al, msps[k].name, m[5]); break; }
    case 10: m[4] = 0; break;
    case 11: case 13: m[2] = 0; break;
    case 12: m[4] = 0; break;
    default: LOG("MA código %u sin modelar", code);
    }
    pthread_mutex_unlock(&ma_m);
}

/* /dev/ldec (ldec.ko, descompresor por hardware): ioctl 1 {origen virtual, longitud, destino físico, capacidad, registros, canal, 0, 0xa0}.
 * Formato LZPT de Sony (fwtool lz77, scripts/e25_27/tpzl.py): registros 0xF0 = LZ77 con banderas LSB primero (bit 1 = copia de 2 B:
 * longitud tabla[b0>>4], distancia 12 bits; distancia 0 = fin del registro) o 0x0F = almacenado (tamaño u16 en +2). */
static unsigned char *phys2pn(unsigned a, unsigned n);
/* LIVE: tiempo acumulado (µs) de dibujo de listas, relleno/copias, LDEC y nº de listas; viajan en la cabecera de cada fotograma (live.py los muestra) */
static volatile unsigned st_rast, st_gpu, st_ldec, st_lists;
static unsigned now_us(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return (unsigned)(t.tv_sec * 1000000u + t.tv_nsec / 1000); }
static unsigned ldec_inflate(const unsigned char *s, unsigned n, unsigned char *d, unsigned cap) {
    static const unsigned char lt[16] = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 32, 64};
    unsigned i = 0, o = 0;
    while (i < n && o < cap) {
        unsigned k = s[i++];
        if (k == 0x0f) { if (i + 3 > n) break; unsigned sz = s[i + 1] | s[i + 2] << 8; i += 3; while (sz-- && i < n && o < cap) d[o++] = s[i++]; continue; }
        if (k != 0xf0) break;  /* relleno a cero tras el último registro */
        for (int end = 0; !end && i < n; ) {
            unsigned f = s[i++];
            for (int b = 0; b < 8 && !end && i < n; b++) {
                if (!(f >> b & 1)) { if (o < cap) d[o++] = s[i]; i++; continue; }
                if (i + 2 > n) { end = 1; break; }
                unsigned len = lt[s[i] >> 4], dist = (s[i] & 15) << 8 | s[i + 1]; i += 2;
                if (!dist) end = 1;
                else if (dist > o) return o;  /* flujo corrupto */
                else for (unsigned t = 0; t < len && o < cap; t++, o++) d[o] = d[o - dist];
            }
        }
    }
    return o;
}
static void efp(const char *f, ...);
/* GPUEMU: timbres de la GPU y su finalización se señalan por futex (async-signal-safe: el timbre llega desde el manejador SIGSEGV de REGTRAP) en vez de sondear con usleep */
static volatile unsigned gpu_kicks, gpu_irq_seq, gpu_last_us;
static void fut_wake(volatile unsigned *a) { syscall(SYS_futex, a, 129 /* WAKE_PRIVATE */, 0x7fffffff, 0, 0, 0); }
static volatile unsigned *gw0, *gw1;
static volatile unsigned kick_list[64];
static volatile unsigned gpu_done;  /* listas ya dibujadas por gpu_thread */
/* La GPU real ejecuta en orden las listas y las transferencias; aquí las listas las dibuja gpu_thread (asíncrono) y las copias/rellenos se ejecutan en el hilo de la UI al escribir
 * el registro de inicio. Sin esperar, la copia a pantalla (0xc18) podía ir antes del dibujo de la lista ya timbrada → fotograma viejo y el cambio real no se enviaba hasta la
 * siguiente copia (una tecla «sin efecto» durante 12 s). gpu_sync espera (máx. 2 s) a que se dibujen los timbres dados hasta ahora. */

static void fut_wait(volatile unsigned *a, unsigned v, unsigned ms) { struct timespec t = { ms / 1000, ms % 1000 * 1000000L }; syscall(SYS_futex, a, 128 /* WAIT_PRIVATE */, v, ms ? &t : 0, 0, 0); }
static void gpu_kick(unsigned list) { kick_list[gpu_kicks % 64] = list; gpu_kicks++; fut_wake(&gpu_kicks); }
static void gpu_sync(void) {
    unsigned t = gpu_kicks;
    for (int i = 0; i < 200; i++) { unsigned d = gpu_done; if ((int)(t - d) <= 0) return; fut_wait(&gpu_done, d, 10); }
    efp("[shim] GPUEMU gpu_sync: %u listas sin dibujar tras 2 s\n", t - gpu_done);
}
/* SYSTAT=1: contadores de ioctl emulados por (hilo, dispositivo, orden, 1.ª palabra de uipc); cada 5 s imprime los >2000 llamadas/intervalo con el nombre del hilo → busca sondeos que giran sin bloquear */
static struct { long tid; char dev[24]; unsigned long req, w0; volatile unsigned n, last; } sst[512];
static void systat_key(const char *dv, unsigned long req, unsigned long w0) {
    long tid = syscall(224);
    for (int i = 0; i < 512; i++) {
        if (sst[i].tid == tid && sst[i].req == req && sst[i].w0 == w0 && !strcmp(sst[i].dev, dv)) { sst[i].n++; return; }
        if (!sst[i].tid && __sync_bool_compare_and_swap(&sst[i].tid, 0, tid)) { strncpy(sst[i].dev, dv, 23); sst[i].req = req; sst[i].w0 = w0; sst[i].n = 1; return; }
    }
}
static void systat_add(int fd, unsigned long req, void *arg) {
    int u = kind[fd] == D_UIPC; systat_key(u ? "uipc" : devname[fd], u ? req & 0x7fffffff : req, u && readable(arg) ? *(unsigned *)arg : 0);
}
/* libObj (grm_*, libObj+0x6170fc) calcula el plazo con clock_gettime(CLOCK_MONOTONIC) pero la condición es CLOCK_REALTIME (glibc 2.11 sin condattr_setclock efectivo): el plazo (con «infinito» = 0x7fffffff ms) cae en 1970,
 * pthread_cond_timedwait da ETIMEDOUT al instante y grm_gpe/grm_result giran al 100 %. Un plazo absoluto cercano al reloj monotónico y muy anterior al real se traslada al reloj real. */
static int cond_timedwait_in(pthread_cond_t *c, pthread_mutex_t *m, const struct timespec *t, void *ra);
int pthread_cond_timedwait(pthread_cond_t *c, pthread_mutex_t *m, const struct timespec *t) { return cond_timedwait_in(c, m, t, __builtin_return_address(0)); }
static int cond_timedwait_in(pthread_cond_t *c, pthread_mutex_t *m, const struct timespec *t, void *ra) {
    static int (*real)(pthread_cond_t *, pthread_mutex_t *, const struct timespec *); if (!real) real = dlsym(RTLD_NEXT, "pthread_cond_timedwait");
    struct timespec rt = {0}, mt = {0}, fix;
    if (t && clock_gettime(CLOCK_REALTIME, &rt) == 0 && clock_gettime(CLOCK_MONOTONIC, &mt) == 0 && rt.tv_sec > mt.tv_sec + 86400 && t->tv_sec >= mt.tv_sec - 86400 && t->tv_sec < mt.tv_sec + 2200000) {
        long long rel = (long long)(t->tv_sec - mt.tv_sec) * 1000000000LL + (t->tv_nsec - mt.tv_nsec);
        /* shortcut: tope de 20 ms; con la espera larga (10 s) un aviso perdido retrasaba la tecla 12 s (grm_* esperaba sin sondear). Sondeo barato; quitar si se halla el emisor que no avisa */
        if (rel > 20000000LL) rel = 20000000LL; if (rel < 0) rel = 0;
        rel += rt.tv_nsec; fix.tv_sec = rt.tv_sec + rel / 1000000000LL; fix.tv_nsec = rel % 1000000000LL;
        t = &fix;
    }
    { int ws = wl_begin("cond_timedwait", (unsigned)(unsigned long)c, -2, ra); int rr = real(c, m, t); wl_end(ws); return rr; }
}
static void *systat_thread(void *a) {
    (void)a; for (;;) { sleep(5);
        for (int i = 0; i < 512; i++) if (sst[i].tid && sst[i].n - sst[i].last > 2000) { char nm[32] = "?", p[64]; snprintf(p, sizeof p, "/proc/self/task/%ld/comm", sst[i].tid); FILE *f = fopen(p, "r"); if (f) { if (fgets(nm, sizeof nm, f)) nm[strcspn(nm, "\n")] = 0; fclose(f); }
            Dl_info di; int lib = sst[i].dev[0] != '/' && strcmp(sst[i].dev, "uipc") && dladdr((void *)sst[i].req, &di) && di.dli_fname;
            efp("[shim] SYSTAT %ld %s %s req=%#lx w0=%#lx %u/5s %s\n", sst[i].tid, nm, sst[i].dev, lib ? sst[i].req - (unsigned long)di.dli_fbase : sst[i].req, sst[i].w0, sst[i].n - sst[i].last, lib ? di.dli_fname : ""); }
        for (int i = 0; i < 512; i++) sst[i].last = sst[i].n; }
    return 0;
}
/* read/poll/select sobre dispositivos «genéricos» (= /dev/null): sin esto devuelven al instante (EOF/listo) y el hilo del driver (UsbControl, I-InputRepeat…) gira al 100 % */
ssize_t read(int fd, void *b, size_t n) {
    static ssize_t (*real)(int, void *, size_t); if (!real) real = dlsym(RTLD_NEXT, "read");
    if (fd >= 0 && fd < MAXFD && kind[fd] == D_GENERIC) { if (getenv("SYSTAT")) systat_add(fd, 0x100000, 0); if (!getenv("NOBLOCKDEV")) for (;;) sleep(3600); }
    return real(fd, b, n);
}
/* WAITLOG: esperas del sistema (no UIPC) que también pueden frenar una tecla */
#define WL_CALL(kind, id, tmo, call) ({ int ws_ = wl_begin(kind, id, tmo, __builtin_return_address(0)); __typeof__(call) r_ = (call); wl_end(ws_); r_; })
int usleep(useconds_t us) { static int (*real)(useconds_t); if (!real) real = dlsym(RTLD_NEXT, "usleep"); return WL_CALL("usleep", 0, (int)(us / 1000), real(us)); }
unsigned int sleep(unsigned int s) { static unsigned (*real)(unsigned); if (!real) real = dlsym(RTLD_NEXT, "sleep"); return WL_CALL("sleep", 0, (int)(s * 1000), real(s)); }
int nanosleep(const struct timespec *t, struct timespec *r) { static int (*real)(const struct timespec *, struct timespec *); if (!real) real = dlsym(RTLD_NEXT, "nanosleep"); return WL_CALL("nanosleep", 0, t ? (int)(t->tv_sec * 1000 + t->tv_nsec / 1000000) : 0, real(t, r)); }
int select(int n, fd_set *r, fd_set *w, fd_set *e, struct timeval *t) { static int (*real)(int, fd_set *, fd_set *, fd_set *, struct timeval *); if (!real) real = dlsym(RTLD_NEXT, "select"); return WL_CALL("select", 0, t ? (int)(t->tv_sec * 1000 + t->tv_usec / 1000) : -1, real(n, r, w, e, t)); }
int poll(struct pollfd *f, nfds_t n, int tmo) {
    static int (*real)(struct pollfd *, nfds_t, int); if (!real) real = dlsym(RTLD_NEXT, "poll");
    for (nfds_t i = 0; i < n; i++) if (f[i].fd >= 0 && f[i].fd < MAXFD && kind[f[i].fd] == D_GENERIC) { if (getenv("SYSTAT")) systat_add(f[i].fd, 0x100001, 0); break; }
    return WL_CALL("poll", n ? (unsigned)f[0].fd : 0, tmo, real(f, n, tmo));
}
static int ioctl_in(int fd, unsigned long req, ...) {
    static int (*r)(int, unsigned long, ...);
    va_list a; va_start(a, req); void *arg = va_arg(a, void *); va_end(a);
    if (fd >= 0 && fd < MAXFD && kind[fd] && getenv("SYSTAT")) { static int th; if (!th++) { pthread_t t; pthread_create(&t, 0, systat_thread, 0); } systat_add(fd, req, arg); }
    if (fd >= 0 && fd < MAXFD && kind[fd] == D_UIPC) {
        unsigned idx = req & 0x7fffffff;  /* índices según u_osal_* de libosal_uipc.so: 0 stat_sem 1 wai_sem 2 sig_sem 3 stat_msgq 4 snd_msg
            5 snd_sync_msg 6 snd_sync_direct 7 rcv_msg 8 reg_msg_queue_cb 9 unreg 0xa valloc 0xb free 0xc dynamic_id 0xd wait_cb 0xe/0xf modos de cola 0x10 connect */
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
        case 1: { LOG("uipc wai_sem? %#x tmo=%d", w[0], (int)w[1]); int r = uipc_sem_wait(w[0], (int)w[1]); LOG("uipc wai_sem %#x tmo=%d -> %d", w[0], (int)w[1], r); return r; }
        case 2: sem_sig(w[0]); LOG("uipc sig_sem %#x", w[0]); return 0;
        case 7: { unsigned *t = (unsigned *)w[1]; LOG("uipc rcv_msg qid=%#x tmo=%d", w[0], (int)t[1]);
            if ((int)t[1] < 0 && getenv("RCVSTACK")) { static unsigned vq[64]; static int nq; int k, ya = 0; for (k = 0; k < nq; k++) if (vq[k] == w[0]) ya = 1; if (!ya && nq < 64) { vq[nq++] = w[0]; raise(SIGUSR1); } }
            { void *mm; int rr = mbx_take(w[0], (int)t[1], &mm); if (rr == 0) { *(void **)t[0] = mm; LOG("rcv_msg qid=%#x <- respuesta", w[0]); return 0; } if (rr != 1) return rr; }
            if ((int)t[1] < 0) {  /* espera indefinida en una cola estática: se le da buzón para que una respuesta posterior (ACKQ0) la despierte */
                void *mm; dynq_add(w[0]); if (mbx_take(w[0], -1, &mm) == 0) { *(void **)t[0] = mm; LOG("rcv_msg qid=%#x <- respuesta (cola estática)", w[0]); return 0; } }
            return kernel_sleep((int)t[1]); }
        case 13: {  /* wait_cb {0, &out[4]}: el proxy espera una entrega y llama out[0](out[2], out[1]) */
            unsigned *out = (unsigned *)w[1];
            pthread_mutex_lock(&cb_m);
            while (dlv_r == dlv_w) pthread_cond_wait(&cb_c, &cb_m);
            out[0] = (unsigned)dlv[dlv_r % 256].cb; out[1] = (unsigned)dlv[dlv_r % 256].arg; out[2] = (unsigned)dlv[dlv_r % 256].msg; out[3] = 0; dlv_r++;
            pthread_mutex_unlock(&cb_m);
            if (getenv("VERB") || getenv("CBLOG")) LOG("wait_cb -> cb %#x msg %#x w0=%#x", out[0], out[2], out[2] ? *(unsigned *)out[2] : 0);  /* CBLOG=1: solo las entregas a callbacks (sin el ruido de VERB) */
            return 0; }
        case 8: {  /* reg_msg_queue_cb(qid, arg, cb, prio) → {qid, &{arg, cb, prio, 0}}: t[0] es un puntero a objeto (par), t[1] código Thumb (impar) */
            unsigned *t = (unsigned *)w[1];
            pthread_mutex_lock(&cb_m);
            int k = cb_find(w[0]); if (k < 0 && ncbs < 128) k = ncbs++;
            if (k >= 0) { cbs[k].q = w[0]; cbs[k].cb = (void *)t[1]; cbs[k].arg = (void *)(t[3] == 1 ? t[2] : t[0]); }  /* t[3]==1: registro síncrono, el argumento va en t[2] (EventWrapper de libMWF) */
            pthread_mutex_unlock(&cb_m);
            { Dl_info di; const char *fn = "?"; unsigned long off = 0; if (dladdr((void *)(t[1] & ~1u), &di) && di.dli_fname) { fn = strrchr(di.dli_fname, '/') ? strrchr(di.dli_fname, '/') + 1 : di.dli_fname; off = (t[1] & ~1u) - (unsigned long)di.dli_fbase; }
              LOG("uipc reg_%smsg_queue_cb qid=%#x arg=%#x cb=%#x (%s+%#lx) t2=%#x%s", t[3] == 1 ? "sync_" : "", w[0], t[0], t[1], fn, off, t[2], k < 0 ? " (tabla llena)" : ""); } return 0; }
        case 9: { pthread_mutex_lock(&cb_m); int k = cb_find(w[0]); if (k >= 0) cbs[k].q = 0; pthread_mutex_unlock(&cb_m); LOG("uipc unreg_msg_queue_cb qid=%#x", w[0]); return 0; }
        case 3: {  /* stat_msgq: 16 B, palabra 0 = mensajes pendientes. libBizFw DataflowInfraCh::freeOsalId (0x34dc8) vacía la cola con rcv
                      bloqueante mientras sea > 0: sin rellenarla quedaba basura y ObjRenderer se colgaba tras cada orden VDF (§5.18z⁸). shortcut: resto de campos a 0 (formato NO_VERIFICADO) */
            unsigned n = 0, *o = (unsigned *)w[1];
            pthread_mutex_lock(&mbx_m); for (int k = 0; k < 16; k++) if (mbx[k].msg && mbx[k].q == w[0]) n++; pthread_mutex_unlock(&mbx_m);
            if (readable(o)) { o[0] = n; o[1] = o[2] = o[3] = 0; }
            if (getenv("VERB")) LOG("uipc stat_msgq %#x -> %u pendientes", w[0], n); return 0; }
        case 5: {  /* snd_sync_msg {qid, &{msg, cb, arg}}: 0x8f013a es el registro de trazas (u16 + texto "%4X %s %s") */
            unsigned *t5 = (unsigned *)w[1];
            if (getenv("VERB5") && w[0] != 0x8f013a && w[0] != 0x720018) LOG("sync5 qid=%#x t5[1]=%#x", w[0], ((unsigned *)w[1])[1]);
            unsigned char *m = (unsigned char *)t5[0];
            if (t5[1]) return 0;  /* segunda llamada del emisor: fin del callback síncrono */
            { static int ns5; const char *e = getenv("STACKQ"); if (e && hexv(e, 0) == w[0] && ++ns5 == 3) raise(SIGUSR1); }  /* STACKQ=qid: pila del emisor en el 3.er envío */
            { pthread_mutex_lock(&cb_m); int k = cb_find(w[0]); if (k >= 0) { t5[1] = (unsigned)cbs[k].cb; t5[2] = (unsigned)cbs[k].arg; } pthread_mutex_unlock(&cb_m);
              if (k >= 0) { if (getenv("VERB")) LOG("snd_sync_msg %#x -> callback directo", w[0]);
                  if (getenv("MSGBODY") && readable(m)) { char h[400]; int o = 0; for (int q = 0; q < 24; q++) o += snprintf(h + o, sizeof h - o, "%08x ", ((unsigned *)m)[q]); LOG("MSGBODY sync %#x %s", w[0], h); }
                  return 0; } }
            if (w[0] == 0x8f013a) { if (m[2] && getenv("KEYINITON") && strstr((char *)m + 2, getenv("KEYINITON"))) keyinit_send();
              if (m[2] && tron_base && strstr((char *)m + 2, getenv("TRACEON"))) { unsigned long b = tron_base; tron_base = 0; trace_fns(b); LOG("TRACEON: trazas armadas"); } if (m[2]) { menu_track((char *)m + 2); LOG("LOG %s", (char *)m + 2); } else if (getenv("VERB")) { char t[200]; int k, o = 0; for (k = 0; k < 40; k++) o += snprintf(t + o, sizeof t - o, "%02x", m[k]); LOG("LOGRAW %s", t); } }
            else if (w[0] == 0x3e014d) backup_service((unsigned *)m);
            else if (w[0] == 0x924127 && ((unsigned *)m)[0] == 0x920111 && getenv("BOOTINFO")) {  /* BOOTINFO=a,b,c,d,e (hex): respuesta de arranque (ObjHandover, libObj+0x41b158) → palabras 1–5 */
                const char *e = getenv("BOOTINFO"); for (int k = 1; k <= 5 && *e; k++) { ((unsigned *)m)[k] = hexv(e, &e); if (*e == ',') e++; }
                static int nb; if (nb++ < 2) LOG("BOOTINFO responde %s", getenv("BOOTINFO")); }
            else if (w[0] == 0x14c0424) { ma_service((unsigned *)m); return 0; }
            else { char h[200]; int k, o = 0; for (k = 0; k < 16; k++) o += snprintf(h + o, sizeof h - o, "%08x ", ((unsigned *)m)[k]);
                LOG("uipc snd_sync_msg qid=%#x datos=%s", w[0], h); }
            return 0; }
        case 12: {  /* dynamic_id {0, &{tipo, grupo, &id}}: tipo 0x32 = semáforo nuevo */
            static unsigned next = 0x4000;
            unsigned *t = (unsigned *)w[1];
            if (t[0] == 0x2a && t[2]) { unsigned id = (t[1] << 16) | next++; *(unsigned *)t[2] = id; dynq_add(id); LOG("uipc dynamic_id cola -> %#x", id); }
            else if (t[0] == 0x32 && t[2]) { unsigned id = (t[1] << 16) | next++; *(unsigned *)t[2] = id; LOG("uipc dynamic_id sem -> %#x", id); }
            else LOG("uipc dynamic_id tipo=%#x grupo=%#x (sin salida)", t[0], t[1]);
            return 0; }
        case 11: if (getenv("VERB")) LOG("uipc free qid=%#x msg=%#x", w[0], w[1]); return 0;
        case 4: { unsigned char *m = (unsigned char *)w[1];
            if (w[0] == 0x8f0139 || w[0] == 0x8f013a) {  /* registro de trazas asíncrono: texto ASCII dentro del mensaje */
                char t[420]; int k; for (k = 0; k < 410; k++) t[k] = (m[k] >= 32 && m[k] < 127) ? m[k] : '.'; t[410] = 0;
                { char c[420]; int o = 0, pd = 1; for (k = 0; t[k]; k++) { if (t[k] == '.') { if (!pd) c[o++] = ' '; pd = 1; } else { c[o++] = t[k]; pd = 0; } } c[o] = 0; if (o > 6) LOG("TRAZA %s", c); }
                { const char *ka = getenv("KEYONACTIVE"), *kp = strstr(t, "toActive:3515 insert key_code=0x");  /* KEYONACTIVE=estado_hex: el driver de entrada de la cámara informa el estado inicial de cada tecla cuando InputService la activa (aquí, la tecla de encendido) */
                  if (ka && kp && is_dynq(0x7a0020)) { unsigned kc = hexv(kp + 32, 0), kmsg[6] = { kc, 0, hexv(ka, 0), 0, 0, 0 }; mbx_post(0x7a0020, kmsg, 0); LOG("KEYONACTIVE key=%#x status=%#x", kc, kmsg[2]); }
                  if (kp && !getenv("KEYINITON")) keyinit_send(); }
                if (getenv("STACKTXT") && strstr(t, getenv("STACKTXT"))) { static int ns; if (ns++ < 2) raise(SIGUSR1); }  /* STACKTXT=texto: pila del hilo que emite esa traza */
                if (strstr(t, "MMapBase")) { char h[500]; int o = 0; for (k = 0; k < 200; k++) o += snprintf(h + o, sizeof h - o, "%02x", m[k]); LOG("TRAZAHEX %s", h); }
                return 0; }
            if (w[0] == 0x80003b && !getenv("NOVDF")) {  /* display vdf del kernel */
                unsigned cmd = ((unsigned *)m)[0], p1 = ((unsigned *)m)[1];
                if (cmd < 16 && p1 > 0x10000 && ((cmd & 1) == 0 || cmd == 9)) { vdfcb[cmd] = (void *)p1; return 0; }
                if ((cmd & 1) && cmd < 8) { pthread_t t; pthread_create(&t, 0, vdf_ack, (void *)(unsigned long)cmd); pthread_detach(t); return 0; }
            }
            /* UPMON=1: respuesta de upm.ko a ON_CMP (0x92015b en 0x920021; upm.ko 0xf638→0xf6fc): envía APP_ON = {0x92015a, estado, 0x1d, 0x1e} a la cola 0x920168 */
            if (getenv("UPMON") && w[0] == 0x920021 && ((unsigned *)m)[0] == 0x92015b) {
                unsigned *a = calloc(64, 4); a[0] = 0x92015a; a[2] = 0x1d; a[3] = 0x1e; int ok = cb_deliver(0x920168, a), mb = 0;
                if (!ok && getenv("UPMON")[0] == '2') { if (!is_dynq(0x920168)) dynq_add(0x920168); mbx_post_raw(0x920168, a); mb = 1; }
                LOG("UPMON: ON_CMP -> APP_ON a 0x920168: %s", ok ? "callback" : mb ? "buzón" : "SIN CALLBACK"); return 0; }
            if (syncmbx_q(w[0])) { if (!is_dynq(w[0])) dynq_add(w[0]); mbx_post_raw(w[0], (unsigned *)m); LOG("snd_msg %#x -> buzón (SYNCMBX) w0=%#x", w[0], ((unsigned *)m)[0]); return 0; }
            if (getenv("MSGBODY") && readable(m)) { char h[400]; int o = 0; for (int q = -4; q < 20; q++) o += snprintf(h + o, sizeof h - o, "%08x ", ((unsigned *)m)[q]); LOG("MSGBODY snd %#x %s", w[0], h); }
            if (cb_deliver(w[0], m)) { if (getenv("VERB")) LOG("snd_msg %#x -> callback", w[0]); return 0; }
            /* Servicios de kernel con acuse genérico (ACKQ=d9016e,7a0029,…; 0xd9016e registro de puerto de vídeo, 0x7a0029 input.ko): se
             * responde a la cola dinámica que viaja en el cuerpo copiando la petición con estado 0 (lo que comprueba el emisor síncrono
             * 0x6a2550 de libObj). shortcut: a 0x61003c la misma respuesta hace saltar la aserción de 0x6a25d2; modelarla cuando se conozca su formato. */
            if (w[0] == 0x4015e && !getenv("NO4015E") && is_dynq(((unsigned *)m)[-1])) {  /* libObj+0x8138b8 (ObjStillRecorder…): petición {0, orden, …} con la cola de respuesta en la cabecera (m[-1]); exige {1, orden, 0, …} y, para 0x1000, +0xc = phys de un área de 0xc40 B que mapea de /dev/mem (aquí anónima a cero) */
                unsigned *rq = (unsigned *)m, rp[12] = { 1, rq[1], 0, rq[1] == 0x1000 ? 0x8f000000u : 0 };
                mbx_post_raw(rq[-1], rp); LOG("snd_msg 0x4015e orden %#x -> respuesta a %#x", rq[1], rq[-1]); return 0; }
            if (w[0] == 0x59000e && !getenv("NOVDF59") && ((unsigned *)m)[0] > 0x10000 && ((unsigned *)m)[0] < 0x2000000) {
                unsigned rq = ((unsigned *)m)[0]; if (!is_dynq(rq)) dynq_add(rq); vdf_reply(rq, (unsigned char *)m); return 0; }
            { const char *e = getenv("ACKQ0"); int ack = 0;  /* ACKQ0=qid,…: la cola de respuesta va en la palabra 0 y es estática (p. ej. ObjMic → 0x58003f {0x2d0117, 0xa0a0a0a0}); se crea su buzón y se responde con eco y estado 0 */
              while (e && *e) { if (hexv(e, &e) == w[0]) ack = 1; while (*e == ',') e++; }
              unsigned rq = ((unsigned *)m)[0];
              if (ack && rq > 0x10000 && rq < 0x2000000) { if (!is_dynq(rq)) dynq_add(rq);
                  if (((unsigned *)m)[1] == 0xa0a0a0a0) { dataflow_reply(w[0], rq, (unsigned char *)m); return 0; }
                  mbx_post(rq, (unsigned *)m, 0); LOG("snd_msg %#x -> acuse ACKQ0 a %#x", w[0], rq); return 0; } }
            { const char *e = getenv("ACKQ"); if (!e) e = "d9016e,7a0029,61003c"; int ack = 0;
              while (*e) { if (hexv(e, &e) == w[0]) ack = 1; while (*e == ',') e++; }
              if (getenv("MSGHEXQ") && hexv(getenv("MSGHEXQ"), 0) == w[0]) {  /* MSGHEXQ=qid: vuelca 4+16 palabras del mensaje y la pila del emisor (2 primeras veces) */
                  static int nh; char h[300]; int o = 0; for (int k = -4; k < 16; k++) o += snprintf(h + o, sizeof h - o, "%08x ", ((unsigned *)m)[k]);
                  LOG("MSGHEXQ %#x %s", w[0], h); if (nh++ < 2) raise(SIGUSR1); }
              if (ack) for (int k = 0; k < 6; k++) if (is_dynq(((unsigned *)m)[k])) { mbx_post(((unsigned *)m)[k], (unsigned *)m, w[0] == 0x61003c); LOG("snd_msg %#x -> acuse genérico a %#x (palabra %d)", w[0], ((unsigned *)m)[k], k); return 0; } }
            if (w[0] == 0x9a015a || w[0] == 0x9c015b) { static int n; if (n++ < 4) raise(SIGUSR1); if (n > 5) { usleep(20000); return 0; } }  /* bucle HDMI: pila y silencio */
            if (getenv("VERB")) { char h[200]; int k, o = 0; for (k = -32; k < 32; k++) o += snprintf(h + o, sizeof h - o, "%02x", m[k]); LOG("MSGHEX %#x %s", w[0], h); }
            LOG("uipc snd_msg a la cola de kernel %#x (descartado) cab=%02x%02x%02x%02x datos=%08x %08x", w[0], m[-12], m[-11], m[-10], m[-9],
                ((unsigned *)m)[0], ((unsigned *)m)[1]); return 0; }
        case 6: { unsigned char *m = (unsigned char *)w[1]; char h[200]; int k, o = 0;
            for (k = 0; k < 64; k++) o += snprintf(h + o, sizeof h - o, "%02x", m[k]);
            if (getenv("VERB") || (getenv("MSGBODY") && w[0] != 0x910041 && w[0] != 0x910042)) LOG("uipc snd_sync_direct qid=%#x msg=%s", w[0], h); return direct_service(w[0], (unsigned *)m); }
        default: LOG("uipc ioctl idx=%u args %#x %#x (ignorada)", idx, w[0], w[1]); return 0;
        }
    }
    if (fd >= 0 && fd < MAXFD && kind[fd] == D_GENERIC) {  /* dispositivo no modelado: éxito, registrado las 5 primeras veces por (dispositivo, orden) y luego cada 4096 */
        static struct { char d[32]; unsigned long r; unsigned n; } seen[64]; static int ns; int k;
        if (!strcmp(devname[fd], "/dev/dmpgles2") && req == 0x80048206 && arg) *(unsigned *)arg = 0x20000;  /* tamaño de la ventana de registros de la GPU (rm_reg_init lo pasa a mmap de /dev/mem; con 0 se mapeaba 1 página y el código escribe en +0x1804) */
        if (getenv("GPUTRACE") && gpu_live && !strcmp(devname[fd], "/dev/dmpgles2")) { static int gn; if (gn++ < 600) LOG("GPU ioctl %#lx arg=%p val=%#x", req, arg, readable(arg) ? *(unsigned *)arg : 0u); }  /* GPUTRACE=1: cada ioctl de la GPU tras cargar las vistas (primeros 600), sin deduplicar */
        if (!strcmp(devname[fd], "/dev/dmpgles2") && req == 0xc004820d) {  /* espera de interrupción de la GPU (libObj+0x6c5320 repite hasta salida != 0) */
            const char *e = getenv("GPUIRQ_MS"); unsigned ms = e ? (unsigned)num(e) : 20;  /* GPUIRQ_MS=n: IRQ simulada cada n ms (20 por defecto, necesaria para que termine la init GL); 0 = GPU ociosa, duerme */
            if (ms && arg) {  /* la IRQ llega al acabar un trabajo (gpu_thread despierta el futex); sin trabajo, cada ms (init GL) y, con la GPU ociosa >2 s, cada 200 ms */
                unsigned seq = gpu_irq_seq, idle = gpu_kicks && now_us() - gpu_last_us > 2000000u;
                fut_wait(&gpu_irq_seq, seq, idle ? 200 : ms); *(unsigned *)arg = 1; return 0; }
            for (;;) sleep(3600);
        }
        if (!strcmp(devname[fd], "/dev/dmpgles2") && (req == 0xc0048211 || req == 0xc0048212) && arg) {  /* cerrojos del núcleo de la GPU (libObj 0x6c53e0 toma: repite
            mientras la salida ≠ 0; 0x6c5450 suelta), id 1 = cola de trabajos, 2 = …; antes la toma siempre «acertaba» y productor (0x6c58c0) y planificador (0x6c6680)
            corrían a la vez: callbacks basura y SIGSEGV en libObj+0x6c51a0 (§5.18z) */
            static volatile int held[8]; unsigned id = *(unsigned *)arg & 7;
            if (req == 0xc0048212) { __sync_lock_release(&held[id]); return 0; }
            if (__sync_lock_test_and_set(&held[id], 1)) { usleep(200); *(unsigned *)arg = 1; } else *(unsigned *)arg = 0;
            return 0;
        }
        if (!strcmp(devname[fd], "/dev/ldec") && req == 1 && readable(arg)) {  /* descompresión LZPT de las imágenes de la UI (§5.18z′) */
            unsigned *q = (unsigned *)arg; unsigned char *d = phys2pn(q[2], q[3]); const unsigned char *src = (const unsigned char *)(unsigned long)q[0];
            unsigned t0 = now_us(), o = d && readable(src) ? ldec_inflate(src, q[1], d, q[3]) : 0; static int nl; st_ldec += now_us() - t0;
            if (!o || (getenv("LDECLOG") && nl++ < 400)) LOG("LDEC %#x B → %#x (cap %#x) r=%#x c=%#x %#x %#x: %#x B", q[1], q[2], q[3], q[4], q[5], q[6], q[7], o);
            return 0;
        }
        pthread_mutex_lock(&semlock);
        for (k = 0; k < ns && (seen[k].r != req || strcmp(seen[k].d, devname[fd])); k++);
        if (k == ns && ns < 64) { strncpy(seen[ns].d, devname[fd], 31); seen[ns].r = req; seen[ns++].n = 0; }
        unsigned n = k < 64 ? seen[k].n++ : 0;
        pthread_mutex_unlock(&semlock);
        if (n == 3 && getenv("DEVSTACK")) raise(SIGUSR1);  /* pila del llamador de la 4.ª repetición */
        if (n < 5 || !(n & 4095)) { Dl_info di; void *ra = __builtin_return_address(0); int ok = dladdr(ra, &di) && di.dli_fname;
            LOG("ioctl(%s, %#lx, %p) arg0=%#x [n=%u] desde %s+%#lx", devname[fd], req, arg, readable(arg) ? *(unsigned *)arg : (unsigned)(unsigned long)arg, n, ok ? di.dli_fname : "?", ok ? (unsigned long)ra - (unsigned long)di.dli_fbase : 0UL); }
        return 0;
    }
    if (!r) r = dlsym(RTLD_NEXT, "ioctl");
    return r(fd, req, arg);
}
int ioctl(int fd, unsigned long req, ...) {  /* envoltorio: con WAITLOG registra las esperas UIPC largas (sem 1: w[0]=id,w[1]=tmo; rcv_msg 7: w[0]=qid,t[1]=tmo) */
    va_list a; va_start(a, req); void *arg = va_arg(a, void *); va_end(a);
    unsigned idx = req & 0x7fffffff;
    if (!wl_on() || fd < 0 || fd >= MAXFD || kind[fd] != D_UIPC || (idx != 1 && idx != 7 && idx != 5 && idx != 6)) return ioctl_in(fd, req, arg);
    unsigned *w = arg; char k[16]; snprintf(k, sizeof k, "uipc%u", idx);
    int ws = wl_begin(k, w[0], idx == 1 ? (int)w[1] : idx == 7 ? (int)((unsigned *)w[1])[1] : -2, __builtin_return_address(0));
    int rr = ioctl_in(fd, req, arg); wl_end(ws); return rr;
}

static unsigned hex(const char *p, char **end) {
    unsigned v = 0;
    for (;; p++) { int c = *p; if (c >= '0' && c <= '9') v = v * 16 + c - '0'; else if (c >= 'a' && c <= 'f') v = v * 16 + c - 'a' + 10; else break; }
    *end = (char *)p; return v;
}
static void efp(const char *f, ...) {  /* escritura sin cerrojo de stderr: usable desde el manejador de señal */
    char b[300]; va_list v; va_start(v, f); int n = vsnprintf(b, sizeof b, f, v); va_end(v);
    if (n > 0) { if (n > (int)sizeof b - 1) n = sizeof b - 1; write(2, b, n); if (wl_on()) wl_live(b, n); }  /* WAITLOG: también al anfitrión por el canal live (shim.log; la consola del invitado frenaba el proceso) */
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
    char nm[24] = {0}; syscall(SYS_prctl, 16, nm); efp("[shim] --- pila (sig %d tid %ld %s) pc/lr:\n", sig, (long)syscall(SYS_gettid), nm); efp("[shim]   raw pc=%08lx lr=%08lx addr=%08lx r0=%08lx r1=%08lx r2=%08lx\n", uc->uc_mcontext.arm_pc, uc->uc_mcontext.arm_lr, (unsigned long)si->si_addr, uc->uc_mcontext.arm_r0, uc->uc_mcontext.arm_r1, uc->uc_mcontext.arm_r2); sym(uc->uc_mcontext.arm_pc); sym(uc->uc_mcontext.arm_lr);
    for (int i = 0; i < 300; i++) { if (((unsigned long)(sp + i) & 0xfff) == 0 || i == 0) { if (msync((void *)((unsigned long)(sp + i) & ~0xfffUL), 1, MS_ASYNC)) break; } sym(sp[i]); }  /* no cruzar el final de la pila */
    (void)sig;
}

/* WAITLOG=ms (diagnóstico, apagado por defecto; con live.py: SHIMEXTRA="WAITLOG=1500"): registra toda espera que supere ms en UIPC (sem, rcv_msg, envíos síncronos),
 * condiciones, poll/select/sleep/usleep/nanosleep: hilo, primitiva, id/qid, plazo y dirección de retorno (módulo+offset). Las esperas infinitas solo salen al terminar
 * (despertar tardío). Las líneas van a stderr y, por el canal live, a DIR/live/<vm>/shim.log del anfitrión (con su hora delante), junto con «tecla», «copia a pantalla»
 * y «fotograma enviado» (hora del invitado = CLOCK_MONOTONIC). WLALL=1 reenvía además cada LOG del shim; WAITSTACK=1 manda SIGUSR1 al hilo que espera (pila; puede
 * dar EINTR a la aplicación). */
static struct { long tid; const char *k; unsigned a; int tmo; void *ra; struct timespec t0; int dumped, used; } wls[128];
static pthread_mutex_t wl_m = PTHREAD_MUTEX_INITIALIZER;
static int wl_ms(void) { if (wl_v < 0) wl_v = getenv("WAITLOG") ? num(getenv("WAITLOG")) : 0; return wl_v; }
static int wl_on(void) { return wl_ms() > 0; }
static long wl_el(struct timespec *t0) { struct timespec n; clock_gettime(CLOCK_MONOTONIC, &n); return (n.tv_sec - t0->tv_sec) * 1000 + (n.tv_nsec - t0->tv_nsec) / 1000000; }
static double wl_ts(void) { struct timespec n; clock_gettime(CLOCK_MONOTONIC, &n); return n.tv_sec + n.tv_nsec / 1e9; }
static void wl_desc(void *ra, char *o, int n) { Dl_info di; if (dladdr(ra, &di) && di.dli_fname) snprintf(o, n, "%s+%#lx", strrchr(di.dli_fname, '/') ? strrchr(di.dli_fname, '/') + 1 : di.dli_fname, (unsigned long)ra - (unsigned long)di.dli_fbase); else snprintf(o, n, "%p", ra); }
static void *wl_watch(void *x) {
    (void)x; for (;;) { usleep(250000);
        for (int i = 0; i < 128; i++) {
            pthread_mutex_lock(&wl_m); typeof(wls[0]) e = wls[i]; int hit = e.used && !e.dumped && wl_el(&e.t0) >= wl_ms(); if (hit) wls[i].dumped = 1; pthread_mutex_unlock(&wl_m);
            if (!hit) continue;  /* dladdr/fopen fuera del cerrojo: dladdr toma el cerrojo del cargador y se cruzaría con un dlopen */
            char d[96], nm[32]; wl_desc(e.ra, d, sizeof d); tname((int)e.tid, nm, sizeof nm);
            if (e.tmo != -1) efp("[shim] WAITLOG %.2f espera>%dms tid %ld %s %s id=%#x tmo=%d ra=%s\n", wl_ts(), wl_ms(), e.tid, nm, e.k, e.a, e.tmo, d);
            if (getenv("WAITSTACK")) syscall(SYS_tgkill, getpid(), (int)e.tid, SIGUSR1); } }
    return 0;
}
static int wl_begin(const char *k, unsigned a, int tmo, void *ra) {
    if (!wl_on()) return -1;
    if ((unsigned long)ra - (unsigned long)&wl_on < 0x30000UL || (unsigned long)&wl_on - (unsigned long)ra < 0x30000UL) return -1;  /* esperas internas del shim: ya las cubre el ioctl */
    static int th; if (!th++) { pthread_t t; pthread_create(&t, 0, wl_watch, 0); }
    int s = -1; pthread_mutex_lock(&wl_m);
    for (int i = 0; i < 128 && s < 0; i++) if (!wls[i].used) s = i;
    if (s >= 0) { wls[s].used = 1; wls[s].dumped = 0; wls[s].tid = syscall(224); wls[s].k = k; wls[s].a = a; wls[s].tmo = tmo; wls[s].ra = ra; clock_gettime(CLOCK_MONOTONIC, &wls[s].t0); }
    pthread_mutex_unlock(&wl_m); return s;
}
static void wl_end(int s) {
    if (s < 0) return;
    pthread_mutex_lock(&wl_m); typeof(wls[0]) e = wls[s]; long ms = wl_el(&e.t0); wls[s].used = 0; pthread_mutex_unlock(&wl_m);
    if (!e.dumped) return;
    char d[96], nm[32]; wl_desc(e.ra, d, sizeof d); tname((int)e.tid, nm, sizeof nm);
    efp("[shim] WAITLOG %.2f fin tid %ld %s %s id=%#x tmo=%d tras %ld ms ra=%s\n", wl_ts(), e.tid, nm, e.k, e.a, e.tmo, ms, d);
}
static void wl_key(unsigned k) { efp("[shim] WAITLOG %.2f tecla %#x\n", wl_ts(), k); }
/* DUMPAT=n: a los n s manda SIGUSR1 a cada hilo (uno por segundo) para ver dónde está parado cada uno */
static struct { void *p; size_t len; long off; char dev[32]; } amaps[64]; static int nam;
static void memscan(void);
static void *dumper(void *a) {
    sleep(num(getenv("DUMPAT"))); (void)a; load_maps();
    if (getenv("MEMSCAN")) memscan();
    if (getenv("GLOBDUMP")) {  /* GLOBDUMP="off_hex,…": valor de variables globales de libObj (+off) y su posición respecto a las ventanas de la GPU */
        unsigned long base = 0; { FILE *m = fopen("/proc/self/maps", "r"); char ln[300]; while (m && fgets(ln, sizeof ln, m)) if (strstr(ln, "libObj.so")) { base = hexv(ln, 0); break; } if (m) fclose(m); }
        /* la base del mapa con offset 0 */
        char *spec = strdup(getenv("GLOBDUMP")), *sv = 0;
        for (char *it = strtok_r(spec, ",", &sv); it; it = strtok_r(0, ",", &sv)) {
            unsigned long off = hexv(it, 0); unsigned v = *(unsigned *)(base + off); char r[120] = "";
            for (int k = 0; k < nam; k++) if ((unsigned long)v >= (unsigned long)amaps[k].p && (unsigned long)v < (unsigned long)amaps[k].p + amaps[k].len) snprintf(r, sizeof r, " = ventana %s off=%#lx +%#lx", amaps[k].dev, amaps[k].off, (unsigned long)v - (unsigned long)amaps[k].p);
            efp("[shim] GLOBDUMP libObj+%#lx = %#x%s\n", off, v, r);
        }
    }
    if (getenv("AREADUMP")) {  /* AREADUMP="dev@off_hex[,dev@off_hex…]" (p. ej. stream@b4000000,dmpgles2@0,mem@80000000): vuelca cada área (máx. 8 MiB) a /tmp/area_<dev>_<off>.bin */
        char *spec = strdup(getenv("AREADUMP")), *sv = 0;
        for (char *it = strtok_r(spec, ",", &sv); it; it = strtok_r(0, ",", &sv)) {
            char *at = strchr(it, '@'); if (!at) continue; *at = 0; long off = (long)hexv(at + 1, 0);
            for (int k = 0; k < nam; k++) if (strstr(amaps[k].dev, it) && amaps[k].off == off) {
                size_t n = amaps[k].len < 0x800000 ? amaps[k].len : 0x800000; char fn[96]; snprintf(fn, sizeof fn, "/tmp/area_%s_%lx.bin", it, off);
                int fd = open(fn, O_WRONLY | O_CREAT | O_TRUNC, 0644);
                if (fd >= 0) { write(fd, amaps[k].p, n); close(fd); efp("[shim] AREADUMP %s %zu B\n", fn, n); }
                break;
            }
        }
    }
    DIR *d = opendir("/proc/self/task"); struct dirent *e; int tids[512], n = 0;
    while (d && (e = readdir(d)) && n < 512) if (e->d_name[0] != '.') tids[n++] = num(e->d_name);
    if (d) closedir(d); efp("[shim] dumper hilos=%d\n", n);
    const char *only = getenv("DUMPTHR");  /* DUMPTHR=subcadena: solo los hilos cuyo nombre la contiene (p. ej. Appframework,UX) */
    for (int i = 0; i < n; i++) { char fn[64], nm[32] = ""; snprintf(fn, sizeof fn, "/proc/self/task/%d/comm", tids[i]); FILE *f = fopen(fn, "r"); if (f) { if (!fgets(nm, sizeof nm, f)) nm[0] = 0; fclose(f); } nm[strcspn(nm, "\n")] = 0; efp("[shim] HILO %d %s\n", tids[i], nm); }
    for (int i = 0; i < n; i++) {
        if (only) { char fn[64], nm[32] = ""; snprintf(fn, sizeof fn, "/proc/self/task/%d/comm", tids[i]); FILE *f = fopen(fn, "r"); if (f) { if (!fgets(nm, sizeof nm, f)) nm[0] = 0; fclose(f); } { char *l = strdup(only), *sv2 = 0; int ok = 0; for (char *t = strtok_r(l, ",", &sv2); t; t = strtok_r(0, ",", &sv2)) if (strstr(nm, t)) ok = 1; free(l); if (!ok) continue; } }
        syscall(SYS_tgkill, getpid(), tids[i], SIGUSR1); sleep(1);
    }
    return 0;
}

/* IMDB_TRACE=1: registra las consultas de im.elf a libIMDB (tabla de etapas) para ver qué entradas/destino elige */
typedef unsigned (*imdb_fn)(unsigned, unsigned, unsigned, unsigned);
static unsigned imdb_call(const char *nm, unsigned a, unsigned b, unsigned c, unsigned d) {
    imdb_fn f = (imdb_fn)dlsym(RTLD_NEXT, nm); unsigned r = f ? f(a, b, c, d) : 0;
    if (getenv("IMDB_TRACE")) {
        char sa[48] = ""; if (a > 0x10000 && a < 0xbf000000u) snprintf(sa, sizeof sa, " \"%.40s\"", (const char *)a);
        efp("[shim] %s(%#x%s, %#x) -> %#x\n", nm, a, sa, b, r);
    }
    return r;
}
unsigned IMDB_find_target_bit(unsigned a, unsigned b, unsigned c, unsigned d) { return imdb_call("IMDB_find_target_bit", a, b, c, d); }
unsigned IMDB_find_entry(unsigned a, unsigned b, unsigned c, unsigned d) { return imdb_call("IMDB_find_entry", a, b, c, d); }
unsigned IMDB_get_entries(unsigned a, unsigned b, unsigned c, unsigned d) { return imdb_call("IMDB_get_entries", a, b, c, d); }
/* INJECT="seg:qid:w0,w1,..;seg:qid:.." (todo en hex; sin strtoul: la glibc 2.11 no tiene __isoc23_*): a los seg s entrega un mensaje a la cola síncrona con callback, como haría av-cam */
/* OPENVIEW="Vista[,Vista…]" OPENVIEWAT=s: llama a viewManagerIf::openView(nombre, 0) de libObj desde un hilo propio (abrir la vista raíz sin el evento de arranque de av-cam) */
static void *lobj_h;
/* MENU: con la vista de disparo ausente nadie abre el menú al pulsar MENU (en la cámara DefRootView::ActionOpenSettingMenu pide «@V00E» = BASE_MENU 0x0E → SETTINGMENUX 0x7C).
 * Se sigue por las trazas de la UI si hay menú abierto (Vn/Vd de 07C o 039); con el menú cerrado la pulsación de MENU abre «@V00E» en vez de ir a la cola de teclas. */
static volatile int menu_open;
static void menu_track(const char *t) {
    const char *p = strstr(t, " Vn "); if (!p) p = strstr(t, " Vd "); if (!p) return;
    if (strncmp(p + 4, "07C_", 4) && strncmp(p + 4, "039_", 4)) return;
    menu_open = p[2] == 'n';
}

/* PRECREATE=modelo o «M modelo» en caliente: publica el evento «solicitar modelo» (libObj+0x7eb9e8: mm, {?,?,id}) para que Appframework cree el modelo (p. ej. @M00F = ModelStillRec, el que atiende los ajustes de disparo) */
/* PREACQST=i,j,… o «A i» en caliente: ModelManager::acquireStatus(i) (índice de estado; libObj+0x7eb0a2) */
static void acquire_status(int i) {
    void **pvm = dlsym(lobj_h, "pViewManager"); unsigned char *base = (unsigned char *)dlsym(lobj_h, "_ZN13viewManagerIf8openViewEPKci") - 0x1251fd;
    if (pvm && *pvm) { void *mm = *(void **)((char *)*pvm + 0x18); int (*aq)(void *, int) = (int (*)(void *, int))(base + 0x7eb0a2 + 1); int rr = aq(mm, i); efp("[shim] PREACQST acquireStatus(%d) -> %d\n", i, rr); }
}
static void model_create(const char *nm) {
    int (*ov)(const char *, int) = dlsym(lobj_h, "_ZN13viewManagerIf8openViewEPKci"); unsigned char *base = (unsigned char *)ov - 0x1251fd; void **pvm = dlsym(lobj_h, "pViewManager");
    unsigned (*idget)(const char *) = dlsym(lobj_h, "_ZN11IdGenerator3GetEPKc");
    if (pvm && *pvm && idget) {
        void *mm = *(void **)((char *)*pvm + 0x18); unsigned fake[4] = { 0, 0, idget(nm), 0 };
        int (*rq)(void *, void *) = (int (*)(void *, void *))(base + 0x7eb9e8 + 1);
        efp("[shim] PRECREATE mm=%p id=%#x\n", mm, fake[2]); int rr = rq(mm, fake); efp("[shim] PRECREATE -> %d\n", rr); sleep(3);
    } else efp("[shim] PRECREATE: sin pViewManager/IdGenerator\n");
}
/* STARTEV=id,id,… (o «S id[:modelo[:clave]],…» en caliente): construye Event(id,2,0) como en libObj+0x7f25f0 y lo publica con ModelManager::pushEvent (p. ej. 11004002=Tc, 11004012=Ts, 11004013=→estado 7) */
static void startev(const char *spec) {
        void **pvm = dlsym(lobj_h, "pViewManager");
        void (*ector)(void *, unsigned long, unsigned char, unsigned char) = dlsym(RTLD_DEFAULT, "_ZN5EventC1Emhh");
        int (*push)(void *, void *) = dlsym(RTLD_DEFAULT, "_ZN12ModelManager9pushEventEP5Event");
        for (int k = 0; pvm && !*pvm && k < 600; k++) usleep(100000);
        if (pvm && *pvm && ector && push) {
            void *mm = *(void **)((char *)*pvm + 0x18); unsigned char *base = (unsigned char *)dlsym(lobj_h, "_ZN13viewManagerIf8openViewEPKci") - 0x1251fd;
            for (const char *e = spec; e && *e; ) { unsigned long id = hexv(e, &e); void *ev = calloc(1, 0x10);  /* Event ocupa 0x10 (operator new(0x10) en el original); lo posee el ModelManager */
                ector(ev, id, 2, 0);
                if (*e == ':') { int mid = (int)hexv(e + 1, &e); unsigned long pk = 0x18; if (*e == ':') pk = hexv(e + 1, &e);  /* id:valor[:clave] */ void *pr = calloc(1, 0x10); ((void (*)(void *, int))(base + 0xf0fb0 + 1))(pr, mid);  /* STARTEV=id:modelo → parámetro 0x18 = Param<int>(modelo), como 0x7f2618 */
                    void (*addp)(void *, unsigned long, void *) = dlsym(RTLD_DEFAULT, "_ZN5Event12addParameterEmP9ParamBase"); if (addp) addp(ev, pk, pr); }
                int rr = push(mm, ev); efp("[shim] STARTEV %#lx -> %d\n", id, rr); sleep(getenv("STARTGAP") ? (unsigned)hexv(getenv("STARTGAP"), 0) : 2); while (*e && *e != ',') e++; while (*e == ',') e++; }  /* avanza siempre: hexv no acepta mayúsculas */
        } else efp("[shim] STARTEV: faltan pViewManager/Event::Event/ModelManager::pushEvent\n");
}
static void *openviewer(void *a) {
    (void)a; sleep(num(getenv("OPENVIEWAT") ? getenv("OPENVIEWAT") : "40"));
    int (*ov)(const char *, int) = lobj_h ? dlsym(lobj_h, "_ZN13viewManagerIf8openViewEPKci") : 0;
    if (!ov) { efp("[shim] OPENVIEW: sin viewManagerIf::openView\n"); return 0; }
    if (getenv("PREACQ") && lobj_h) {  /* PREACQ=modelo: pide un «execute» al modelo antes de abrir vistas (¿fuerza su creación?) */
        int (*rq)(const char *, unsigned long, void *) = dlsym(lobj_h, "_ZN13viewManagerIf19requestModelExecuteEPKcmP9ParamList");
        void (*ctor)(void *) = dlsym(RTLD_DEFAULT, "_ZN9ParamListC1Ev"); static char lb[512];
        if (rq && ctor) { ctor(lb); int rr = rq(getenv("PREACQ"), 0, lb); efp("[shim] PREACQ %s -> %d\n", getenv("PREACQ"), rr); sleep(3); }
    }
    if (getenv("PREACQST") && lobj_h) {  /* PREACQST=i,j,…: llama a ModelManager::acquireStatus(i) (índice de estado) antes de abrir vistas */
        for (const char *e = getenv("PREACQST"); e && *e; ) { int i = (int)hexv(e, &e); acquire_status(i); sleep(2); while (*e == ',') e++; }
    }
    if (getenv("PRECREATE") && lobj_h) model_create(getenv("PRECREATE"));
    if (getenv("STARTEV") && lobj_h) startev(getenv("STARTEV"));
    { void **pv = dlsym(lobj_h, "pViewManager"); for (int k = 0; pv && !*pv && k < 600; k++) usleep(100000); }  /* openView con ViewManager aún NULL = SIGSEGV (arranque lento) */
    char *spec = strdup(getenv("OPENVIEW")), *sv = 0;
    for (char *it = strtok_r(spec, ",", &sv); it; it = strtok_r(0, ",", &sv)) { efp("[shim] OPENVIEW %s ...\n", it); int r = ov(it, 0); efp("[shim] OPENVIEW %s -> %d\n", it, r); if (getenv("POSTROOTEV") && !strcmp(it, "view/ROOT")) { sleep(8); startev(getenv("POSTROOTEV")); }  /* POSTROOTEV: tras abrir view/ROOT (su @T100 termina antes) la vista raíz pide @T0E3 (viewUnified2+0x16c58c) */ sleep(getenv("OPENVIEWGAP") ? (unsigned)hexv(getenv("OPENVIEWGAP"), 0) : 2); }
    return 0;
}
static void *injector(void *a) {
    char *spec = strdup(getenv("INJECT")), *sp1 = 0; (void)a; unsigned long t0 = 0;
    for (char *it = strtok_r(spec, ";/", &sp1); it; it = strtok_r(0, ";/", &sp1)) {
        const char *e; unsigned long at = hexv(it, &e); unsigned q = hexv(e + 1, &e);
        unsigned *m = calloc(64, 4); int n = 0;
        while (*e == ':' || *e == ',') { m[n++] = hexv(e + 1, &e); if (n >= 60) break; }
        if (at > t0) { sleep(at - t0); t0 = at; }
        int ok = cb_deliver(q, m); const char *how = "callback";
        if (!ok && is_dynq(q)) { if (q == 0x7a0020) mbx_post_raw(q, m); else mbx_post(q, m, 0); ok = 1; how = "buzón"; }  /* cola que un hilo lee con rcv_msg; 0x7a0020 (driver de entrada: {clave, 0, valor, 0, índice físico}) sin tocar w0 (§5.18w) */
        efp("[shim] INJECT q=%#x w0=%#x -> %s\n", q, m[0], ok ? how : "SIN CALLBACK NI BUZÓN");
    }
    return 0;
}
/* SEMSIG: semáforos que en la cámara señala otro procesador (av-cam) y aquí nadie; se dejan señalados al arrancar.
   0x83037a: el main de im.elf (antes de crear el hilo de aplicación appFw.so → UI) y luego el hilo Appframework esperan en él; se señala 4 veces. Lista hex separada por comas; vacío = ninguno. */
static void live_init(void);
static void keyq_init(void) {  /* KEYQ=qid_hex[,…]: colas del kernel que un hilo de usuario lee con rcv_msg: se les da buzón (para INJECT) */
    for (const char *s = getenv("SYNCMBX"); s && *s; ) { const char *n; unsigned v = hexv(s, &n); if (n == s) break; dynq_add(v); s = *n == ',' ? n + 1 : n; }  /* el hilo lector ya espera en rcv_msg al arrancar: el buzón debe existir desde el principio */
    const char *p = getenv("KEYQ"); while (p && *p) { const char *q; unsigned id = hexv(p, &q); if (q == p) break; dynq_add(id); p = *q == ',' ? q + 1 : q; }
}
static void presignal(void) {
    const char *e = getenv("SEMSIG"), *p = e ? e : "83037a,83037a,83037a,83037a";
    while (*p) { const char *q; unsigned id = hexv(p, &q); if (q == p) break; sem_sig(id); p = *q == ',' ? q + 1 : q; }
}
__attribute__((constructor)) static void shim_init(void) { presignal(); keyq_init(); live_init(); if (getenv("INJECT")) { pthread_t th; pthread_create(&th, 0, injector, 0); } if (getenv("OPENVIEW")) { pthread_t th; pthread_create(&th, 0, openviewer, 0); } if (getenv("DUMPAT")) { pthread_t th; pthread_create(&th, 0, dumper, 0); } struct sigaction sa; memset(&sa, 0, sizeof sa); sa.sa_sigaction = on_usr1; sa.sa_flags = SA_SIGINFO; sigaction(SIGUSR1, &sa, 0);
    sa.sa_flags = SA_SIGINFO | SA_RESETHAND; sigaction(SIGSEGV, &sa, 0); sigaction(SIGBUS, &sa, 0); sigaction(SIGILL, &sa, 0); sigaction(SIGABRT, &sa, 0); }  /* un fallo imprime la pila y se reintenta por defecto (core) */

/* Experimento (SKIPFN=717830,...): sustituye esas funciones Thumb de libObj por «movs r0,#0; bx lr» (devuelven éxito sin hacer nada). */
static unsigned long hexv(const char *s, const char **end) { unsigned long v = 0; for (;; s++) { int c = *s; if (c >= '0' && c <= '9') c -= '0'; else if (c >= 'a' && c <= 'f') c -= 'a' - 10; else break; v = v * 16 + c; } if (end) *end = s; return v; }
static unsigned long gpu_pc;  /* libObj+0x6c4c46: «str r1,[r3,r0]» de rm_reg_write (off=r0, valor=r1, base=r3); se sustituye por UDF para ver cada escritura */
/* GPUEMU: timbres (0x1804) y lista de cada uno */
/* Experimento (TRACEFN=716800,6cd1e0,...): traza de una sola vez (UDF + restauración) de la entrada de esas funciones de libObj: r0-r3 y lr. */
static struct { unsigned long pc, step; unsigned short orig, orig2; unsigned hits; } trc[32]; static int ntrc; static unsigned long trc_base; static volatile unsigned long app_sys;  /* app_sys: r0 de AppSystem::dispatch (libObj+0x7eed0c) en su primera traza */
static void gpu_exec(unsigned off, unsigned val);
static void on_trace(int sig, siginfo_t *si, void *u) {
    mcontext_t *c = &((ucontext_t *)u)->uc_mcontext; unsigned long pc = c->arm_pc & ~1UL; int i;
    if (gpu_pc && pc == gpu_pc) {  /* rm_reg_write: se hace el almacenamiento y se salta la instrucción; 0x1804 = timbre de la GPU (GPUEMU) */
        *(volatile unsigned *)(c->arm_r3 + c->arm_r0) = c->arm_r1;
        if (c->arm_r0 == 0x1804) gpu_kick(c->arm_r1);
        gpu_exec(c->arm_r0, c->arm_r1);
        { static int nw; if (getenv("GPUTRACE") && gpu_live && nw++ < 3000) efp("[shim] REGW off=%#lx val=%#lx kicks=%u\n", c->arm_r0, c->arm_r1, gpu_kicks); }
        c->arm_pc += 2; return;
    }
    for (i = 0; i < ntrc; i++) if (trc[i].step && trc[i].step == pc) {  /* TRACEREP: paso hecho; se restaura la instrucción siguiente y se rearma la entrada */
        *(unsigned short *)pc = trc[i].orig2; trc[i].step = 0; *(unsigned short *)trc[i].pc = 0xde00;
        __builtin___clear_cache((char *)pc, (char *)pc + 2); __builtin___clear_cache((char *)trc[i].pc, (char *)trc[i].pc + 2); return;
    }
    for (i = 0; i < ntrc; i++) if (trc[i].pc == pc) {  /* efp, no LOG: fprintf en un manejador de señal puede bloquearse con el cerrojo de stderr de otro hilo */
        if (pc == trc_base + 0x7eed0c) app_sys = c->arm_r0;
        unsigned h = ++trc[i].hits, mx = getenv("TRACEMAX") ? (unsigned)hexv(getenv("TRACEMAX"), 0) : 4;
        int show = h <= mx || !(h & (h - 1));  /* TRACEREP: las mx primeras y luego en potencias de 2 */
        if (show) efp("[shim] TRACE %lx n=%u r0=%lx r1=%lx r2=%lx r3=%lx lr=%lx\n", pc - trc_base, h, c->arm_r0, c->arm_r1, c->arm_r2, c->arm_r3, c->arm_lr);
        if (show) {
        for (const char *e = getenv("TRACEPEEK"); e && *e; ) { unsigned long a = hexv(e, &e); efp("[shim]   PEEK %lx = %08x\n", a, *(unsigned *)(trc_base + a)); while (*e == ',') e++; }
        { const char *e = getenv("TRACEDEREF");  /* «reg:off:palabras» (hex): vuelca palabras en *(reg+off), p. ej. 4:24:90 = tabla de teclas de InfraInput; con «d» delante («d0:a0:20») vuelca desde reg+off sin desreferenciar */
          if (e && *e) { int dr = *e == 'd'; e += dr; unsigned long rg = hexv(e, &e), off = hexv(e + 1, &e), n = hexv(e + 1, 0), *rv = &c->arm_r0; unsigned *q = dr ? (unsigned *)(rv[rg] + off) : (unsigned *)*(unsigned long *)(rv[rg] + off);
            for (unsigned long k = 0; k < n && q; k += 9) efp("[shim]   DEREF %p+%lx: %08x %08x %08x %08x %08x %08x %08x %08x %08x\n", q, k * 4, q[k], q[k+1], q[k+2], q[k+3], q[k+4], q[k+5], q[k+6], q[k+7], q[k+8]); } } }
        *(unsigned short *)pc = trc[i].orig; __builtin___clear_cache((char *)pc, (char *)pc + 2);
        if (getenv("TRACEREP")) {  /* TRACEREP=1: trampa repetible; UDF temporal en la instrucción siguiente (solo válido si la trazada no salta: entradas de función).
                                      shortcut: otro hilo que pase por la entrada mientras está desarmada no se cuenta; si hace falta exactitud, usar un contador en el código */
            unsigned long nx = pc + (((trc[i].orig >> 11) >= 0x1d) ? 4 : 2); trc[i].step = nx; trc[i].orig2 = *(unsigned short *)nx; *(unsigned short *)nx = 0xde00; __builtin___clear_cache((char *)nx, (char *)nx + 2); }
        return;
    }
    signal(SIGILL, SIG_DFL);
}
static int trc_lib_done; static const char *trc_env = "TRACEFN";  /* TRACELIB=lib: TRACEFN2 = entradas relativas a esa biblioteca (p. ej. cmn_view_processDataMgr.so; cubre llamadas virtuales que SETHOOK no ve) */
static void trace_fns(unsigned long base) {
    trc_base = base;
    struct sigaction sa; memset(&sa, 0, sizeof sa); sa.sa_sigaction = on_trace; sa.sa_flags = SA_SIGINFO | SA_NODEFER; sigaction(SIGILL, &sa, 0);
    for (const char *e = getenv(trc_env); e && *e && ntrc < 32; ) {
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
    if (getenv("TRACEFN")) { if (getenv("TRACEON")) tron_base = base; else trace_fns(base); }  /* TRACEON=texto: arma las trazas cuando el registro de libObj emite ese texto (las trazas son de un solo disparo) */
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
static void on_trace(int sig, siginfo_t *si, void *u);
static void gpu_patch(void) {  /* GPUEMU: ver arriba (gpu_thread); libObj 3.21: rm_reg_write en 0x6c4c20, instrucción en 0x6c4c46 */
    static int done; const char *g = getenv("GPUEMU"); if (done || (g && g[0] == '0')) return;
    unsigned long base = 0; char ln[256]; FILE *m = fopen("/proc/self/maps", "r");
    while (m && fgets(ln, sizeof ln, m)) if (strstr(ln, "libObj.so")) { base = hexv(ln, 0); break; }
    if (m) fclose(m);
    if (!base) return;
    unsigned short *p = (unsigned short *)(base + 0x6c4c46);
    if (*p != 0x5019) { LOG("GPUEMU: libObj+0x6c4c46 no es «str r1,[r3,r0]» (%#x): sin timbre", *p); done = 1; return; }
    mprotect((void *)((unsigned long)p & ~4095UL), 8192, PROT_READ | PROT_WRITE | PROT_EXEC);
    gpu_pc = (unsigned long)p; *p = 0xde00; __builtin___clear_cache((char *)p, (char *)p + 2); done = 1;
    struct sigaction sa; memset(&sa, 0, sizeof sa); sa.sa_sigaction = on_trace; sa.sa_flags = SA_SIGINFO | SA_NODEFER; sigaction(SIGILL, &sa, 0);
    LOG("GPUEMU: timbre de la GPU en libObj+0x6c4c46 (%p)", (void *)p);
}
void *dlopen(const char *f, int fl) {
    static void *(*d)(const char *, int);
    if (!d) d = dlsym(RTLD_NEXT, "dlopen");
    if (f && strstr(f, "viewUnified")) gpu_live = 1;
    LOG("dlopen(%s) ...", f ? f : "(null)");
    void *h = d(f, fl); LOG("dlopen(%s) -> %p%s%s", f ? f : "(null)", h, h ? "" : " ERR=", h ? "" : dlerror());
    if (h && f && strstr(f, "libObj.so")) { gpu_patch(); lobj_h = h; }
    if (h && f && getenv("TRACELIB") && (strstr(f, getenv("TRACELIB")) || strstr(f, "viewUnified")) && !trc_lib_done) {  /* la biblioteca puede entrar como dependencia de viewUnified*: se busca en /proc/self/maps tras cada dlopen hasta hallarla */
        char ln[256]; unsigned long base = 0; FILE *m = fopen("/proc/self/maps", "r");
        while (m && fgets(ln, sizeof ln, m)) if (strstr(ln, getenv("TRACELIB"))) { base = hexv(ln, 0); break; }
        if (m) fclose(m);
        if (base) { trc_lib_done = 1; trc_env = "TRACEFN2"; trace_fns(base); LOG("TRACELIB %s base %#lx", getenv("TRACELIB"), base); }
    }
    if (h && f && strstr(f, "libObj.so") && (getenv("SKIPFN") || getenv("TRACEFN") || getenv("WATCH") || getenv("POKE"))) skip_fns();
    if (h && f && getenv("PATCHFN")) {  /* PATCHFN="lib.so:off_hex=val_hex[,…]": sustituye la función Thumb en lib+off por «movs r0,#val; bx lr» (p. ej. viewUnified2.so:17094c=3) */
        char *spec = strdup(getenv("PATCHFN")), *sv = 0; unsigned long base = *(unsigned long *)h;  /* link_map.l_addr */
        for (char *it = strtok_r(spec, ",", &sv); it; it = strtok_r(0, ",", &sv)) {
            char *c = strchr(it, ':'); if (!c) continue; *c = 0; if (!strstr(f, it)) continue;
            const char *q; unsigned long off = hexv(c + 1, &q), val = *q == '=' ? hexv(q + 1, 0) : 0;
            unsigned short *p = (unsigned short *)((base + off) & ~1UL);
            mprotect((void *)((unsigned long)p & ~4095UL), 8192, PROT_READ | PROT_WRITE | PROT_EXEC);
            if (*q == '=' && q[1] == '#') {  /* «=#2302.600b.2001.4770»: halfwords Thumb literales (p. ej. «model/ROOT: tiempo asentado = 2») */
                int n = 0; const char *r = q + 2;
                for (;;) { p[n++] = (unsigned short)hexv(r, &r); if (*r != '.') break; r++; }
                __builtin___clear_cache((char *)p, (char *)(p + n)); LOG("PATCHFN %s+%#lx -> %d halfwords", it, off, n); continue;
            }
            p[0] = 0x2000 | (val & 0xff); p[1] = 0x4770; __builtin___clear_cache((char *)p, (char *)(p + 2));
            LOG("PATCHFN %s+%#lx -> movs r0,#%lu; bx lr", it, off, val);
        }
    }
    return h;
}
/* testmode_debugPrint(nivel, cat, ?, fmt, ...) de libObj (+0x7f0cb8; fmt en r3, varargs detrás): DBGPRINT=1 registra cada llamada
   (errores de las envolturas WRPPR/ObjHandover que en la cámara van a un registro de pruebas). Sin DBGPRINT reenvía 8 palabras al original. */
int testmode_debugPrint(int lvl, int cat, int x, const char *fmt, ...) {
    va_list ap; va_start(ap, fmt);
    if (getenv("DBGPRINT")) { static int n; char b[300]; vsnprintf(b, sizeof b, fmt ? fmt : "(null)", ap); va_end(ap);
        if (n++ < 3000) { void *lr = __builtin_return_address(0); Dl_info di; int ok = dladdr(lr, &di);
            LOG("DBG %d/%#x %s+%#lx: %s", lvl, cat, ok ? strrchr(di.dli_fname, '/') + 1 : "?", ok ? (unsigned long)((char *)lr - (char *)di.dli_fbase) : 0UL, b); }
        return 0; }
    static int (*real)(int, int, int, const char *, ...); if (!real) real = dlsym(RTLD_NEXT, "testmode_debugPrint");
    unsigned w[8]; for (int k = 0; k < 8; k++) w[k] = va_arg(ap, unsigned); va_end(ap);
    return real ? real(lvl, cat, x, fmt, w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7]) : 0;
}
/* SALVAGE=n (hex): la petición 0x1003 de información de salvamento (libObj+0x41e098 → cola 0xae8114, servida por otro proceso en la cámara)
   recibe su respuesta 0x1004 {+0x14 = n entradas}: se entrega al callback real libObj+0x41e420 desde otro hilo (el emisor tiene tomado
   el cerrojo 0x41db30), que fija el estado global libObj+0x10aa698 (n=0 → 2, n>0 → 1) y publica el Event 0x16050001 a ModelManager. */
static void *salvage_reply(void *a) {
    static unsigned buf[0x80]; usleep(200000);
    Dl_info di; void *sym = dlsym(RTLD_DEFAULT, "ModelSalvageToInstance"); unsigned long base = sym && dladdr(sym, &di) ? (unsigned long)di.dli_fbase : 0;
    if (!base) { LOG("SALVAGE: libObj no hallada"); return 0; }
    buf[0] = 0x1004; buf[5] = (unsigned)(unsigned long)a;
    LOG("SALVAGE respuesta 0x1004 n=%u -> libObj+0x41e420", buf[5]);
    ((void (*)(void *))(base + 0x41e421))(buf);
    LOG("SALVAGE estado libObj+0x10aa698 = %u", *(unsigned *)(base + 0x10aa698));
    return 0;
}
/* MWF::ObjIf::IssueCommandAsync(objeto, ObjMsg*): la UI emite así los cambios de ajustes (p. ej. EFCS = ObjMsg(0x3100, 0x75fa) + param 0x9776); IMCMDLOG=1 registra destino, cabecera del mensaje y retorno */
int _ZN3MWF5ObjIf17IssueCommandAsyncEPvPNS_6ObjMsgE(void *h, void *msg) {
    static int (*real)(void *, void *); if (!real) real = dlsym(RTLD_NEXT, "_ZN3MWF5ObjIf17IssueCommandAsyncEPvPNS_6ObjMsgE");
    void *ra = __builtin_return_address(0); int r = real(h, msg);
    if (getenv("IMCMDLOG")) { char t[400]; int o = 0; if (readable(msg)) for (int q = 0; q < 24; q++) o += snprintf(t + o, sizeof t - o, "%08x ", ((unsigned *)msg)[q]); t[o] = 0;
        Dl_info di = {0}; dladdr(ra, &di);  /* llamante como biblioteca+desplazamiento: identifica la rutina emisora (p. ej. libObj+0x6896ac = EFCS 0x75fa) */
        LOG("IssueCommandAsync obj=%p msg=%p -> %d ra=%s+%#lx : %s", h, msg, r, di.dli_fname ? strrchr(di.dli_fname, '/') ? strrchr(di.dli_fname, '/') + 1 : di.dli_fname : "?", (unsigned long)ra - (unsigned long)di.dli_fbase, t); }
    return r;
}
/* SETLOG=1: registra (con retorno) los eslabones de un cambio de ajuste del menú en cmn_view_processDataMgr / wrapperSettingUtil (≤ 4 argumentos de registro); reenvía a la implementación real */
#define SETHOOK(sym) int sym(unsigned a, unsigned b, unsigned c, unsigned d) { static int (*r)(unsigned, unsigned, unsigned, unsigned); if (!r) r = dlsym(RTLD_NEXT, #sym); \
    if (getenv("SETLOG")) LOG("SET> " #sym " %x %x %x %x", a, b, c, d); int x = r(a, b, c, d); if (getenv("SETLOG")) LOG("SET< " #sym " -> %#x", x); return x; }
/* SETLOG=1 también registra las peticiones de modelo de las vistas (primer argumento = nombre «@Mxxx»/«model/…»): el ajuste EFCS pasa por @M00F (process-bindings-a6000.json) */
#define MODHOOK(sym) int sym(const char *a, unsigned b, unsigned c, unsigned d) { static int (*r)(const char *, unsigned, unsigned, unsigned); if (!r) r = dlsym(RTLD_NEXT, #sym); \
    int x = r(a, b, c, d); if (getenv("SETLOG")) LOG("SETMOD " #sym " %s %x %x %x -> %#x", readable(a) ? a : "?", b, c, d, x); return x; }
MODHOOK(_ZN13viewManagerIf12getModelInfoEPKciP9ParamListPKS2_)
MODHOOK(_ZN13viewManagerIf19requestModelExecuteEPKcmP9ParamList)
SETHOOK(_ZN21CmnViewProcessDataMgr8setValueEii)
SETHOOK(_ZN21CmnViewProcessDataMgr8execProcEi)
SETHOOK(_ZN31CmnViewProcessDataElementNormal8setValueEi)
SETHOOK(_ZN31CmnViewProcessDataElementNormal8execProcEv)
SETHOOK(_ZN31CmnViewProcessDataElementNormal15setValueToModelEh)
SETHOOK(_ZN31CmnViewProcessDataElementNormal16setValueToBackupEh)
SETHOOK(_ZN31CmnViewProcessDataElementNormal22getDataModelSetEventIdEhRm)
SETHOOK(_ZN31CmnViewProcessDataElementNormal22getDataModelSetParamIdEhhRm)
SETHOOK(_ZN18WrapperSettingUtil11writeBackupEP15ViewBaseProductja)
SETHOOK(_ZN18WrapperSettingUtil11writeBackupEP15ViewBaseProductjaa)
/* osal_snd_sync_msg(qid, msg, cb, arg): SYNCLOG=1 registra los envíos síncronos que fallan (p. ej. 0xFFFFFC04 = cola local sin manejador registrado) */
int osal_snd_sync_msg(int qid, void *msg, void *cb, void *arg) {
    static int (*real)(int, void *, void *, void *);
    if (!real) real = dlsym(RTLD_NEXT, "osal_snd_sync_msg");
    int r = real ? real(qid, msg, cb, arg) : -1;
    if (r && qid == 0xae8114 && getenv("SALVAGE") && ((unsigned *)msg)[0] == 0x1003) {
        pthread_t t; pthread_create(&t, 0, salvage_reply, (void *)hexv(getenv("SALVAGE"), 0)); pthread_detach(t); r = 0; }
    { const char *e = getenv("SYNCOK"); while (r && e && *e) { unsigned q = hexv(e, &e); if (*e == ',') e++; if (q == (unsigned)qid) { LOG("SYNCOK qid=%#x -> 0", qid); r = 0; } } }  /* SYNCOK=qid,…: colas locales sin manejador (servicio de otro proceso) que responden «bien» */
    if (r && getenv("SYNCLOG")) { static int n; if (n++ < 200) { void *lr = __builtin_return_address(0); Dl_info di; int ok = dladdr(lr, &di); LOG("osal_snd_sync_msg qid=%#x ret=%#x lr=%p %s+%#lx msg=%08x %08x %08x", qid, r, lr, ok ? di.dli_fname : "?", ok ? (unsigned long)((char *)lr - (char *)di.dli_fbase) : 0, ((unsigned *)msg)[0], ((unsigned *)msg)[1], ((unsigned *)msg)[2]); } }
    return r;
}
/* ModelManager::pushEvent(Event*): PUSHLOG=1 registra quién publica eventos de modelo (lr y primeras palabras del Event) */
int _ZN12ModelManager9pushEventEP5Event(void *mm, unsigned *ev) {
    static int (*real)(void *, void *);
    if (!real) real = dlsym(RTLD_NEXT, "_ZN12ModelManager9pushEventEP5Event");
    if (getenv("PUSHLOG")) { static int n; if (n++ < 600) { unsigned long lr = (unsigned long)__builtin_return_address(0); Dl_info di; const char *lib = dladdr((void *)lr, &di) ? di.dli_fname : "?"; LOG("pushEvent lr=%lx (%s+%lx) ev=%08x %08x %08x %08x %08x", lr, lib, dladdr((void *)lr, &di) ? lr - (unsigned long)di.dli_fbase : 0, ev[0], ev[1], ev[2], ev[3], ev[4]); } }
    return real ? real(mm, ev) : 0;
}
/* ModelManager::acquireStatus/releaseStatus(int): PUSHLOG=1 registra quién fija el «estado» del sistema (0x4/0x5/0x7 0000…) */
int _ZN12ModelManager13acquireStatusEi(void *mm, int st) {
    static int (*real)(void *, int); if (!real) real = dlsym(RTLD_NEXT, "_ZN12ModelManager13acquireStatusEi");
    if (getenv("PUSHLOG")) { unsigned long lr = (unsigned long)__builtin_return_address(0); Dl_info di; int ok = dladdr((void *)lr, &di); LOG("acquireStatus(%#x) lr=%lx (+%lx)", st, lr, ok ? lr - (unsigned long)di.dli_fbase : 0); }
    return real ? real(mm, st) : 0;
}
int _ZN12ModelManager13releaseStatusEi(void *mm, int st) {
    static int (*real)(void *, int); if (!real) real = dlsym(RTLD_NEXT, "_ZN12ModelManager13releaseStatusEi");
    if (getenv("PUSHLOG")) { unsigned long lr = (unsigned long)__builtin_return_address(0); Dl_info di; int ok = dladdr((void *)lr, &di); LOG("releaseStatus(%#x) lr=%lx (+%lx)", st, lr, ok ? lr - (unsigned long)di.dli_fbase : 0); }
    return real ? real(mm, st) : 0;
}
/* ViewBase::getModelInfo(nombre, info, lista, filtro): las vistas piden datos de modelo por aquí (PLT → este símbolo antes que libObj). GMILOG=1 registra cada petición y su resultado. */
int _ZN8ViewBase12getModelInfoEPKciP9ParamListPKS2_(void *self, const char *name, int info, void *list, const void *flt) {
    static int (*real)(void *, const char *, int, void *, const void *);
    if (!real) real = dlsym(RTLD_NEXT, "_ZN8ViewBase12getModelInfoEPKciP9ParamListPKS2_");
    int r = real ? real(self, name, info, list, flt) : 0;
    if (real && r && getenv("GMIPROBE2") && !strcmp(name, "model/ROOT") && info == 6) {  /* misma lista que la vista: info 1 y 7, y se restaura la 6 */
        static int n2; if (n2++ < 3) { int a = real(self, name, 1, list, flt), b = real(self, name, 7, list, flt), c = real(self, name, 6, list, flt); LOG("GMIPROBE2 misma lista: info1=%d info7=%d info6=%d", a, b, c); }
    }
    if (real && getenv("GMIPROBE") && !strcmp(name, "model/ROOT") && info == 6) {  /* una vez: prueba info 0..10 de model/ROOT con una lista propia */
        static int done; if (!done++) { void (*ctor)(void *) = dlsym(RTLD_DEFAULT, "_ZN9ParamListC1Ev"), (*dtor)(void *) = dlsym(RTLD_DEFAULT, "_ZN9ParamListD1Ev");
            if (ctor && dtor) for (int i = 0; i <= 10; i++) { char buf[256] = {0}; ctor(buf); int rr = real(self, name, i, buf, 0); LOG("GMIPROBE model/ROOT info %d -> %d", i, rr); dtor(buf); } }
    }
    if (!r && real && getenv("GMIDRAIN") && !strcmp(name, "model/ROOT")) {  /* GMIDRAIN=1: la vista pide un modelo que aún no existe → se vacía reentrantemente la cola de Appframework (hasPending 0x7eec8c / pop 0x7ef940 / dispatch 0x7eed0c) y se reintenta */
        static unsigned char *app; static int tries; void **pvm = lobj_h ? dlsym(lobj_h, "pViewManager") : 0;
        unsigned char *base = lobj_h ? (unsigned char *)dlsym(lobj_h, "_ZN13viewManagerIf8openViewEPKci") - 0x1251fd : 0;
        if (base && pvm && *pvm && tries++ < 3) {
            void *vm = *pvm, *mm = *(void **)((char *)vm + 0x18);
            if (!app) { app = (unsigned char *)app_sys; LOG("GMIDRAIN AppSystem=%p (hace falta TRACEFN=7eed0c)", app); }
            if (app) { int (*pend)(void *) = (int (*)(void *))(base + 0x7eec8c + 1); void *(*pop)(void *) = (void *(*)(void *))(base + 0x7ef940 + 1); void (*disp)(void *, void *) = (void (*)(void *, void *))(base + 0x7eed0c + 1);
                unsigned (*gdest)(void *) = dlsym(lobj_h, "_ZN5Event7getDestEv"); void *stash[256]; int ns = 0, n = 0, nd = 0;
                while (n < 400 && pend(app)) { void *ev = pop(*(void **)(app + 0x10)); n++; unsigned d = gdest ? gdest(ev) : 0xff;
                    if (d == 2) { disp(app, ev); nd++; } else if (ns < 256) stash[ns++] = ev; }  /* solo eventos puros de ModelManager (dest 2): los de ViewManager reentrantes derriban el proceso */
                { int (*pe)(void *, void *) = dlsym(RTLD_NEXT, "_ZN12ModelManager9pushEventEP5Event"); for (int k = 0; k < ns; k++) pe(mm, stash[k]); }
                LOG("GMIDRAIN despachados=%d reencolados=%d", nd, ns);
                r = real(self, name, info, list, flt); LOG("GMIDRAIN %d eventos; getModelInfo(%s,%d) -> %d", n, name, info, r); }
        }
    }
    if (!r && real && getenv("GMIRETRY")) for (int k = 0; k < 20 && !r; k++) { usleep(50000); r = real(self, name, info, list, flt); if (r) LOG("getModelInfo(%s, %d) acierta en el reintento %d", name, info, k + 1); }  /* ¿carrera con la inicialización del modelo? */
    if (getenv("GMILOG")) { static int n; if (n++ < 400) LOG("getModelInfo(%s, %d) -> %d", name, info, r); }
    return r;
}
void *dlsym(void *h, const char *n) {  /* DLSYMLOG=1: símbolos que pide la UI (p. ej. «<Vista>ToInstance», initializeViewConfig) */
    static void *(*d)(void *, const char *); static int lg = -1;
    if (!d) d = dlvsym(RTLD_NEXT, "dlsym", "GLIBC_2.4");
    if (lg < 0) lg = getenv("DLSYMLOG") != 0;
    void *r = d(h, n);
    if (lg && n && h != RTLD_NEXT) LOG("dlsym(%s) -> %p", n, r);
    { const char *e = getenv("DLSYMSTACK"); if (e && n && strstr(n, e)) raise(SIGUSR1); }  /* pila del que pide ese símbolo */
    return r;
}
int system(const char *c) {
    static int (*sy)(const char *);
    if (!sy) sy = dlsym(RTLD_NEXT, "system");
    int r = sy(c); LOG("system(%s) -> %d", c ? c : "(null)", r); return r;
}

/* Mapeos anónimos de dispositivos no modelados (para MEMSCAN: qué áreas ha escrito la UI) */
static void memscan(void) {
    for (int k = 0; k < nam; k++) {
        unsigned char *b = amaps[k].p; size_t nz = 0, first = (size_t)-1, last = 0;
        for (size_t o = 0; o < amaps[k].len; o += 4096) {
            size_t n = amaps[k].len - o < 4096 ? amaps[k].len - o : 4096, j = 0;
            while (j < n && !b[o + j]) j++;
            if (j < n) { nz++; if (first == (size_t)-1) first = o; last = o; }
        }
        efp("[shim] MEMSCAN %s off=%#lx len=%#zx base=%p págs no nulas=%zu [%#zx..%#zx]\n", amaps[k].dev, amaps[k].off, amaps[k].len, amaps[k].p, nz, first == (size_t)-1 ? 0 : first, last);
    }
}
/* REGTRAP=1: las ventanas de registros de la GPU (/dev/dmpgles2 y /dev/mem off=1, 0x20000 B) se mantienen en PROT_NONE; cada acceso falla, se registra
 * (tid, PC, dirección, lectura/escritura) y se abre la ventana 1,5 ms; el hilo de trampa registra además los cambios de contenido (escrituras con su valor).
 * Sirve para saber qué registros consulta el controlador de libObj (p. ej. para decidir que un trabajo terminó). */

static unsigned libobj_off(void *ra);
static struct { unsigned char *p; size_t len; unsigned snap[0x8000]; } rtw[2]; static int nrtw; static struct sigaction rt_old;
static void rt_segv(int sig, siginfo_t *si, void *ctx) {
    ucontext_t *uc = ctx; unsigned char *a = si->si_addr; static int n;
    for (int k = 0; k < nrtw; k++) if (a >= rtw[k].p && a < rtw[k].p + rtw[k].len) {
        static unsigned long seenk[512]; static int nseen; unsigned long key = ((unsigned long)k << 28) ^ ((unsigned long)(a - rtw[k].p) << 12) ^ (uc->uc_mcontext.arm_pc & 0xfff) ^ (((uc->uc_mcontext.error_code >> 11) & 1) << 27); int dup = 0;
        for (int q = 0; q < nseen; q++) if (seenk[q] == key) dup = 1;
        if (!dup && nseen < 512) { seenk[nseen++] = key; n = 0; } else n = 2000;
        if (n++ < 1500) efp("[shim] REGTRAP tid %ld %s w%d+%#lx pc=libObj+%#x lr=libObj+%#x\n", (long)syscall(224), (uc->uc_mcontext.error_code & (1 << 11)) ? "ESC" : "LEC", k, (unsigned long)(a - rtw[k].p), libobj_off((void *)uc->uc_mcontext.arm_pc), libobj_off((void *)uc->uc_mcontext.arm_lr));
        if (k == 0 && a >= rtw[0].p + 0x1000 && a < rtw[0].p + 0x2000) gpu_kick(gw0 ? gw0[0x1804 / 4] : 0);  /* timbre de la GPU (GPUEMU) visto desde REGTRAP */
        mprotect(rtw[k].p, rtw[k].len, PROT_READ | PROT_WRITE); return;
    }
    sigaction(SIGSEGV, &rt_old, 0);  /* no es nuestra: el manejador previo (pila) al reintentar */
}
static void *rt_thread(void *a) {
    (void)a; for (;;) {
        usleep(60);
        for (int k = 0; k < nrtw; k++) {
            unsigned *w = (unsigned *)rtw[k].p; size_t nw = rtw[k].len / 4;
            for (size_t i = 0; i < nw; i++) if (w[i] != rtw[k].snap[i]) { static int m; if (m++ < 800) efp("[shim] REGTRAP w%d+%#zx: %#x -> %#x\n", k, i * 4, rtw[k].snap[i], w[i]); rtw[k].snap[i] = w[i]; }
            mprotect(rtw[k].p, rtw[k].len, PROT_NONE);
        }
    }
    return 0;
}
/* GPUEMU (activo por defecto; GPUEMU=0 lo desactiva): GPU de DMP mínima. Ventanas: gw0 = registros del motor (/dev/mem off=1, mapa externo de la PICA:
 * 0x10–0x1c relleno de memoria, 0xc00–0xc28 display transfer/TextureCopy, 0x1800/0x1804 lista de órdenes), gw1 = página compartida de /dev/dmpgles2
 * (+4 cabeza y +0x10 cuenta de la cola de ejecución que vacía el planificador de libObj, 0x6c60e0; +0xc trabajo en curso; +0x14 estado, 2 = inactiva;
 * +0xe8 tabla de 0x320 trabajos de 0x8c B). Relleno y transferencias se ejecutan al escribir el registro de inicio (gpu_exec); por cada lista
 * (+0x1804) el estado pasa a «ocupada» (1) GPUEMU_MS ms y vuelve a 2. Hasta §5.18y se «avisaba del fin» escribiendo +4/+0x10: eso reencolaba el
 * trabajo 0 (un relleno) y atascaba o rompía la cola (§5.18z). Las listas se dibujan aquí solo con GPURAST/LIVE (gpu_draw); si no, GPUDUMP + gpu_raster.py. */
static unsigned char *phys2p(unsigned phys) {  /* fase → dirección en nuestras áreas anónimas de /dev/stream y /dev/mem */
    for (int k = 0; k < nam; k++) { unsigned long o = (unsigned long)amaps[k].off; if ((!strstr(amaps[k].dev, "stream") && !strstr(amaps[k].dev, "mem")) || o < 0x80000000ul) continue; if (phys >= o && phys < o + amaps[k].len) return (unsigned char *)amaps[k].p + (phys - o); }
    return 0;
}
static unsigned char *phys2pn(unsigned a, unsigned n) { unsigned char *p = phys2p(a), *q = n ? phys2p(a + n - 1) : p; return p && q == p + n - 1 ? p : 0; }  /* área contigua de n B */
static long long fdiv_ll(long long a, long long b) {  /* ⌊a/b⌋ con b > 0 sin libgcc (no hay __aeabi_ldivmod): estimación en double y ajuste exacto */
    long long q = (long long)((double)a / (double)b); while (q * b > a) q--; while ((q + 1) * b <= a) q++; return q;
}
static const unsigned char tile_mx[8] = {0, 1, 4, 5, 16, 17, 20, 21}, tile_my[8] = {0, 2, 8, 10, 32, 34, 40, 42};  /* bits de x en 0,2,4 y de y en 1,3,5 del orden de Morton */
static unsigned tile_off(unsigned x, unsigned y, unsigned w) {  /* mosaico 8×8 en orden de Morton (PICA), en píxeles */
    return ((y >> 3) * (w >> 3) + (x >> 3)) * 64 + tile_mx[x & 7] + tile_my[y & 7];
}
/* Relleno: 0x10 inicio>>3, 0x14 fin>>3, 0x18 valor, 0x1c control (bit 0 inicio; bits 8-9 ancho 0=16, 1=24, 2=32 bits).
 * Transferencia: 0xc00 origen>>2, 0xc04 destino>>2, 0xc08/0xc0c tamaño de salida/entrada (w | h<<16), 0xc10 indicadores (bit 0 volteo vertical,
 * bit 1 entrada lineal → salida en mosaico, si no mosaico → lineal; bit 3 TextureCopy; bits 8-10/12-14 formato de entrada/salida, 0 RGBA8,
 * 1 RGB8, resto 16 bits), 0xc18 bit 0 inicio; TextureCopy: 0xc20 bytes, 0xc24/0xc28 línea de entrada/salida = ancho | hueco<<16 en unidades de 16 B. */
static volatile unsigned live_da, live_w, live_h, live_seq;
static void gpu_exec1(unsigned off, unsigned val);
static void gpu_exec(unsigned off, unsigned val) { if (gw0 && (val & 1) && !getenv("NOGPUSYNC")) gpu_sync(); unsigned t0 = now_us(); gpu_exec1(off, val); st_gpu += now_us() - t0; }
static void gpu_exec1(unsigned off, unsigned val) {
    volatile unsigned *r = gw0; if (!r || !(val & 1)) return;
    if (off == 0x1c) {
        unsigned a = r[0x10 / 4] << 3, n = (r[0x14 / 4] << 3) - a, v = r[0x18 / 4], wd = (val >> 8) & 3; unsigned char *p = phys2pn(a, n);
        if (!p || n > 0x4000000) { efp("[shim] GPUEMU relleno %#x+%#x fuera de área\n", a, n); return; }
        if (wd == 0 && !((unsigned long)p & 1)) for (unsigned i = 0; i < n / 2; i++) ((unsigned short *)p)[i] = v;  /* 16 y 32 bits por palabras (TCG) */
        else if (wd == 2 && !((unsigned long)p & 3)) for (unsigned i = 0; i < n / 4; i++) ((unsigned *)p)[i] = v;
        else for (unsigned i = 0; i < n; i += wd + 2) for (unsigned b = 0; b < wd + 2 && i + b < n; b++) p[i + b] = v >> (8 * b);
    } else if (off == 0xc18) {
        unsigned fl = r[0xc10 / 4], sa = r[0xc00 / 4] << 2, da = r[0xc04 / 4] << 2;
        if (fl & 8) {
            unsigned n = r[0xc20 / 4], iw = (r[0xc24 / 4] & 0xffff) * 16, ig = (r[0xc24 / 4] >> 16) * 16, ow = (r[0xc28 / 4] & 0xffff) * 16, og = (r[0xc28 / 4] >> 16) * 16;
            if (!iw) iw = n; if (!ow) ow = n;
            unsigned char *s = phys2pn(sa, n / iw * (iw + ig)), *d = phys2pn(da, n / ow * (ow + og));
            if (!s || !d) { efp("[shim] GPUEMU TextureCopy %#x→%#x (%#x B) fuera de área\n", sa, da, n); return; }
            if (getenv("GPUTRACE")) { unsigned nz = 0; for (unsigned i = 0; i < n; i++) nz += s[i] != 0; efp("[shim] GPUEMU TextureCopy %#x→%#x %#x B (origen no nulo %u B)\n", sa, da, n, nz); }
            if (iw == ow) { for (unsigned k = 0; k < n; k += iw, s += iw + ig, d += ow + og) memcpy(d, s, n - k < iw ? n - k : iw); }  /* mismo ancho de línea: una copia por línea */
            else for (unsigned k = 0, si = 0, di = 0; k < n; k++) { d[di++] = s[si++]; if ((k + 1) % iw == 0) si += ig; if ((k + 1) % ow == 0) di += og; }
            return;
        }
        static const unsigned char bpp[8] = {4, 3, 2, 2, 2, 2, 2, 2};
        unsigned iw = r[0xc0c / 4] & 0xffff, ih = r[0xc0c / 4] >> 16, ow = r[0xc08 / 4] & 0xffff, oh = r[0xc08 / 4] >> 16, b = bpp[(fl >> 8) & 7];
        unsigned char *s = phys2pn(sa, iw * ih * b), *d = phys2pn(da, ow * oh * b);
        if (!s || !d || b != bpp[(fl >> 12) & 7]) { efp("[shim] GPUEMU transferencia %#x→%#x fl=%#x sin modelar\n", sa, da, fl); return; }  /* shortcut: sin conversión de formato ni escalado */
        if (getenv("GPUTRACE")) { unsigned nz = 0; for (unsigned i = 0; i < iw * ih * b; i++) nz += s[i] != 0; efp("[shim] GPUEMU DT %#x→%#x %ux%u→%ux%u fl=%#x origen no nulo=%u B\n", sa, da, iw, ih, ow, oh, fl, nz); }
        unsigned w = iw < ow ? iw : ow, h = ih < oh ? ih : oh;
        for (unsigned y = 0; y < h; y++) {  /* una fila: lado en mosaico por (y>>3) y tablas de Morton, lado lineal por filas; 16 y 32 bits por palabras */
            unsigned ly = fl & 1 ? h - 1 - y : y, tb = (y >> 3) * ((fl & 2 ? ow : iw) >> 3) * 64 + tile_my[y & 7];
            unsigned short *d2 = (unsigned short *)d, *s2 = (unsigned short *)s; unsigned *d4 = (unsigned *)d, *s4 = (unsigned *)s;
            for (unsigned x = 0; x < w; x++) {
                unsigned t = tb + (x >> 3) * 64 + tile_mx[x & 7], di = fl & 2 ? t : ly * ow + x, si = fl & 2 ? ly * iw + x : t;
                if (b == 2) d2[di] = s2[si]; else if (b == 4) d4[di] = s4[si]; else memcpy(d + di * b, s + si * b, b);
            }
        }
        if (da >> 24 == 0xb4 && !(fl & 2)) { live_da = da; live_w = w; live_h = h; live_seq++; fut_wake(&live_seq); if (wl_on()) efp("[shim] WAITLOG %.2f copia a pantalla seq=%u\n", wl_ts(), live_seq); }  /* LIVE: copia a la pantalla (0xb4000000/0xb4096000) = fotograma presentado */
    }
}
/* GPURAST=1 (o LIVE): dibuja cada lista en el búfer de color como gpu_raster.py (§5.18z): estado hasta el primer 0x202, tira de N vértices de 0x40 B
 * (pos f0-f1, color f3-f6, UV f7-f8, afín f9-f14), textura 0x589/0x586/0x58f (4 RGBA4444, 8 A8; Morton 8×8), scissor 0x47/0x48, mezcla «sobre».
 * Búfer de color: 0x112 = dirección>>4, 0x113 = alto<<16 | ancho, RGBA4444 en mosaico con la y invertida (la copia 0x4401 voltea al presentar).
 * Bucle interno solo con enteros (en TCG la coma flotante de ARM se emula con softfloat); regla arriba-izquierda: sin doble mezcla en aristas compartidas.
 * shortcut: sin shaders ni combinadores (el marco de foco naranja sale aproximado), muestreo al más cercano; ampliar si una pantalla sale mal. */
#define DIV255(x) (((x) + 128 + (((x) + 128) >> 8)) >> 8)  /* x/255 redondeado, exacto en 0..65535, sin división (TCG) */
static void gpu_draw(unsigned list) {
    unsigned *w = (unsigned *)phys2p(list); if (!w) return;
    static unsigned r[0x800], cba, cbw = 640, cbh = 480; unsigned char set[0x800]; memset(set, 0, sizeof set);
    for (int i = 0; i < 20000; ) {
        unsigned h = w[i], v = w[i + 1], reg = h >> 16, ne = ((h >> 12) & 0xf) && (h & 0xfff) == 0x026 ? 5 : 1;
        if (((h >> 12) & 0xf) && reg < 0x800) { r[reg] = v; set[reg] = 1; if (reg == 0x202) break; }
        i += 1 + ne;
        if ((reg == 0x10 && v == 0x12345678) || (!h && !v)) return;
    }
    if (set[0x112]) cba = r[0x112] << 4;
    if (set[0x113]) { cbw = r[0x113] & 0xffff; cbh = r[0x113] >> 16; }
    unsigned n = r[0x202] & 0xfff;
    if (getenv("GPUDRAWLOG")) LOG("gpu_draw lista %#x: 202=%#x(set %d) n=%u 203=%d 216=%d 586=%#x(%d) 58f=%#x(%d) 589=%#x scissor %#x %#x", list, r[0x202], set[0x202], n, set[0x203], set[0x216], r[0x586], set[0x586], r[0x58f], set[0x58f], r[0x589], r[0x47], r[0x48]);
    if (!set[0x202] || r[0x202] >> 24 != 0x90 || n < 3 || n > 4095 || !set[0x203] || !set[0x216] || !cba || cbw > 2048 || cbh > 2048) return;
    unsigned short *cb = (unsigned short *)phys2pn(cba, cbw * cbh * 2), *ix = (unsigned short *)phys2p(r[0x203]); unsigned char *vx = phys2p(r[0x216]);
    if (!cb || !ix || !vx) return;
    unsigned tw = set[0x586] ? r[0x586] >> 16 : 0, th = set[0x586] ? r[0x586] & 0xffff : 0, fmt = set[0x58f] ? r[0x58f] : 0;
    unsigned tbpp = fmt == 4 ? 2 : fmt == 8 ? 1 : 0;
    unsigned char *tex = tw && th && tbpp ? phys2pn((r[0x589] << 3), tw * th * tbpp) : 0;
    int cx0 = 0, cy0 = 0, cx1 = (int)cbw, cy1 = (int)cbh;
    if (set[0x47] && set[0x48]) {
        short a = (short)(r[0x47] & 0xffff), b = (short)(r[0x47] >> 16), c = (short)(r[0x48] & 0xffff), d = (short)(r[0x48] >> 16);
        cx0 = 320 + a / 2; cy0 = 240 - d / 2; cx1 = 320 + c / 2; cy1 = 240 - b / 2;
        if (cx0 < 0) cx0 = 0; if (cy0 < 0) cy0 = 0; if (cx1 > (int)cbw) cx1 = cbw; if (cy1 > (int)cbh) cy1 = cbh;
    }
    static float sx[4096], sy[4096], at[4096][6];  /* u y v en texeles, r g b a en 0..255; solo gpu_thread dibuja. Las listas de marcos/9-slice llevan hasta ~450 vértices (con >64 se omitían: sin marco de foco) */
    for (unsigned k = 0; k < n; k++) {
        float *q = (float *)(vx + ix[k] * 0x40u);
        sx[k] = q[9] * q[0] + q[10] * q[1] + q[11]; sy[k] = q[12] * q[0] + q[13] * q[1] + q[14];
        at[k][0] = q[7] * tw; at[k][1] = q[8] * th; for (int c = 0; c < 4; c++) at[k][2 + c] = q[3 + c] * 255.f;
    }
    for (unsigned t = 0; t + 2 < n; t++) {
        int A = t, B = t + 1, C = t + 2;
        long long ax = (long long)(sx[A] * 16), ay = (long long)(sy[A] * 16), bx = (long long)(sx[B] * 16), by = (long long)(sy[B] * 16), qx = (long long)(sx[C] * 16), qy = (long long)(sy[C] * 16);
        long long area = (bx - ax) * (qy - ay) - (by - ay) * (qx - ax);
        if (!area) continue;
        if (area < 0) { long long tx = bx, ty = by; bx = qx; by = qy; qx = tx; qy = ty; int ti = B; B = C; C = ti; area = -area; }
        float fx0 = sx[A], fx1 = sx[A], fy0 = sy[A], fy1 = sy[A];
        if (sx[B] < fx0) fx0 = sx[B]; if (sx[C] < fx0) fx0 = sx[C]; if (sx[B] > fx1) fx1 = sx[B]; if (sx[C] > fx1) fx1 = sx[C];
        if (sy[B] < fy0) fy0 = sy[B]; if (sy[C] < fy0) fy0 = sy[C]; if (sy[B] > fy1) fy1 = sy[B]; if (sy[C] > fy1) fy1 = sy[C];
        int x0 = (int)fx0 - 1, x1 = (int)fx1 + 2, y0 = (int)fy0 - 1, y1 = (int)fy1 + 2;
        if (x0 < cx0) x0 = cx0; if (y0 < cy0) y0 = cy0; if (x1 > cx1) x1 = cx1; if (y1 > cy1) y1 = cy1;
        if (x0 >= x1 || y0 >= y1) continue;
        /* aristas BC, CA, AB: E(P) = (q−p)×(P−p); dentro si las tres ≥ 0 (> 0 en aristas que no son arriba-izquierda) */
        long long ex[3] = {qx - bx, ax - qx, bx - ax}, ey[3] = {qy - by, ay - qy, by - ay}, ox[3] = {bx, qx, ax}, oy[3] = {by, qy, ay}, e0[3]; int bias[3];
        long long px0 = x0 * 16 + 8, py0 = y0 * 16 + 8;
        for (int e = 0; e < 3; e++) { e0[e] = ex[e] * (py0 - oy[e]) - ey[e] * (px0 - ox[e]); bias[e] = (ey[e] < 0 || (ey[e] == 0 && ex[e] > 0)) ? 0 : -1; }
        /* atributos: plano a + gx·x + gy·y en 16.16 desde el centro del píxel (x0, y0) */
        int base[6], gx[6], gy[6]; float fa = (float)area;
        for (int c = 0; c < 6; c++) {
            float va = at[A][c], vb = at[B][c], vc = at[C][c];
            float dx = (-(float)ey[0] * va - (float)ey[1] * vb - (float)ey[2] * vc) * 16 / fa, dy = ((float)ex[0] * va + (float)ex[1] * vb + (float)ex[2] * vc) * 16 / fa;
            float v0 = ((float)e0[0] * va + (float)e0[1] * vb + (float)e0[2] * vc) / fa;
            base[c] = (int)(v0 * 65536); gx[c] = (int)(dx * 65536); gy[c] = (int)(dy * 65536);
        }
        for (int y = y0; y < y1; y++) {
            /* tramo [i0, i1] de píxeles dentro de la fila: cada arista es lineal (e + bias − ey·16·i ≥ 0), se resuelve en vez de probar los píxeles del rectángulo envolvente */
            long long i0 = 0, i1 = x1 - x0 - 1;
            for (int k = 0; k < 3 && i0 <= i1; k++) {
                long long st = -ey[k] * 16, c0 = e0[k] + bias[k];
                if (st == 0) { if (c0 < 0) i1 = -1; }
                else if (st > 0) { if (c0 < 0) { long long l = fdiv_ll(-c0 + st - 1, st); if (l > i0) i0 = l; } }
                else if (c0 < 0) i1 = -1; else { long long h = fdiv_ll(c0, -st); if (h < i1) i1 = h; }
            }
            if (i0 <= i1) {
                unsigned a[6]; for (int c = 0; c < 6; c++) a[c] = (unsigned)base[c] + (unsigned)gx[c] * (unsigned)i0;
                unsigned short *row = cb; unsigned ty = cbh - 1 - y, rbase = (ty >> 3) * (cbw >> 3) * 64 + tile_my[ty & 7];
                /* textura RGBA4444 con color de vértice constante 255: modular por 255 es la identidad (DIV255(255·17·n) = 17·n) y un texel opaco se copia tal cual (DIV255(17·n·15) = n) */
                int wh = fmt == 4 && tex && !gx[2] && !gx[3] && !gx[4] && !gx[5] && (int)a[2] >> 16 == 255 && (int)a[3] >> 16 == 255 && (int)a[4] >> 16 == 255 && (int)a[5] >> 16 == 255;
                for (int x = x0 + (int)i0; x <= x0 + (int)i1; x++) {
                    unsigned tv = 0;
                    int sr = (int)a[2] >> 16, sg = (int)a[3] >> 16, sb = (int)a[4] >> 16, sa = (int)a[5] >> 16;
                    if (tex) {
                        int u = (int)a[0] >> 16, v = (int)a[1] >> 16; if (u < 0) u = 0; if (u >= (int)tw) u = tw - 1; if (v < 0) v = 0; if (v >= (int)th) v = th - 1;
                        unsigned o = tile_off(u, v, tw);
                        if (fmt == 8) sa = DIV255(sa * tex[o]);
                        else if (wh) { tv = ((unsigned short *)tex)[o]; sr = (tv >> 12) * 17; sg = ((tv >> 8) & 15) * 17; sb = ((tv >> 4) & 15) * 17; sa = (tv & 15) * 17; }
                        else { tv = ((unsigned short *)tex)[o]; sr = DIV255(sr * (int)(tv >> 12) * 17); sg = DIV255(sg * (int)((tv >> 8) & 15) * 17); sb = DIV255(sb * (int)((tv >> 4) & 15) * 17); sa = DIV255(sa * (int)(tv & 15) * 17); }
                    }
                    if (sa > 0) {
                        unsigned short *d = row + rbase + (x >> 3) * 64 + tile_mx[x & 7]; unsigned dv = *d;
                        if (wh && sa == 255) { *d = (unsigned short)tv; for (int c = 0; c < 6; c++) a[c] += gx[c]; continue; }
                        if (sa > 255) sa = 255;
                        if (sr > 255) sr = 255; if (sg > 255) sg = 255; if (sb > 255) sb = 255; if (sr < 0) sr = 0; if (sg < 0) sg = 0; if (sb < 0) sb = 0;
                        int orr = sr, og = sg, ob = sb, oa = 255;
                        if (sa < 255) {
                            int ia = 255 - sa, dr = (dv >> 12) * 17, dg = ((dv >> 8) & 15) * 17, db = ((dv >> 4) & 15) * 17, dA = (dv & 15) * 17;
                            orr = DIV255(sr * sa + dr * ia); og = DIV255(sg * sa + dg * ia); ob = DIV255(sb * sa + db * ia); oa = sa + DIV255(dA * ia);
                        }
                        *d = (unsigned short)(DIV255(orr * 15) << 12 | DIV255(og * 15) << 8 | DIV255(ob * 15) << 4 | DIV255(oa * 15));
                    }
                    for (int c = tex ? 0 : 2; c < 6; c++) a[c] += gx[c];
                }
            }
            for (int k = 0; k < 3; k++) e0[k] += ex[k] * 16;
            for (int c = 0; c < 6; c++) base[c] += gy[c];
        }
    }
}
/* LIVE=/dev/vportNp1 (G22-D, live.py): puerto virtio-serial con el anfitrión. Salida: cada fotograma presentado que cambia, cabecera
 * {«A6KF», ancho | alto << 16, listas, µs de dibujo, µs de relleno/copias, µs de LDEC (acumulados)} + RGBA4444 lineal. Entrada: «R» reenvía el fotograma; líneas «K clave valor índice» (hex) → mensaje {clave, 0, valor, 0, índice} a la cola del driver de entrada 0x7a0020 (§5.18z′). */
static int live_fd = -1; static volatile int live_force;
static pthread_mutex_t live_wm = PTHREAD_MUTEX_INITIALIZER;  /* los fotogramas y las líneas de WAITLOG comparten el puerto: no se mezclan */
static int wl_all(void) { if (wla_v < 0) wla_v = getenv("WAITLOG") && getenv("WLALL") ? 1 : 0; return wla_v; }  /* WLALL=1 (con WAITLOG): cada LOG del shim también va a shim.log, con hora */
static void wl_logfwd(const char *f, ...) {
    char b[400]; int o = snprintf(b, sizeof b, "%.2f ", wl_ts()); va_list v; va_start(v, f); o += vsnprintf(b + o, sizeof b - o - 2, f, v); va_end(v);
    if (o > (int)sizeof b - 2) o = sizeof b - 2; b[o++] = '\n';
    if (live_fd < 0) return; pthread_mutex_lock(&live_wm); write(live_fd, "\x01WL ", 4); write(live_fd, b, o); pthread_mutex_unlock(&live_wm);
}
static void wl_live(const char *b, int n) {  /* «\x01WL texto\n» ; trylock: efp se usa también en manejadores de señal */
    if (live_fd < 0) return;
    { int k = 0; while (pthread_mutex_trylock(&live_wm)) if (++k > 50) return; else usleep(1000); }  /* hasta 50 ms: un fotograma en curso retiene el puerto; así no se pierden líneas ni se bloquea un manejador de señal */
    write(live_fd, "\x01WL ", 4); write(live_fd, b, n); pthread_mutex_unlock(&live_wm);
}
static void live_msg(const char *tag, const char *txt, int n) {  /* «\x01TAG texto\n» al anfitrión; bloquea hasta tener el puerto (no se pierden cambios) */
    if (live_fd < 0) return;
    pthread_mutex_lock(&live_wm); write(live_fd, "\x01", 1); write(live_fd, tag, strlen(tag)); write(live_fd, " ", 1); write(live_fd, txt, n); write(live_fd, "\n", 1); pthread_mutex_unlock(&live_wm);
}
static void *startevhot(void *a) { startev(a); free(a); return 0; }
static void *acqhot(void *a) { acquire_status((int)hexv(a, 0)); free(a); return 0; }
static void *modelhot(void *a) { model_create(a); free(a); return 0; }
static void *openhot(void *a) {
    int (*ov)(const char *, int) = lobj_h ? dlsym(lobj_h, "_ZN13viewManagerIf8openViewEPKci") : 0;
    char *nm = a; int r = ov ? ov(nm, 0) : -99; LOG("OPENHOT %s -> %d", nm, r); free(nm); return 0;
}
static void *live_keys(void *a) {
    (void)a; char buf[256]; int n = 0;
    for (;;) {
        int k = read(live_fd, buf + n, sizeof buf - 1 - n); if (k <= 0) { usleep(20000); continue; }
        n += k; buf[n] = 0; char *ln = buf, *nl;
        while ((nl = strchr(ln, '\n'))) {
            *nl = 0; const char *e;
            if (ln[0] == 'T') { LOG("hora del anfitrión %s", ln + 2); date_base = (long long)hexv(ln + 2, &e); date_mono0 = mono_s(); date_have = 1; }  /* «T epoch_local_hex»: hora local del anfitrión (+ desfase del usuario); se avanza con el reloj monotónico */
            if (ln[0] == 'E') { char *eq = strchr(ln + 2, '='); if (eq) { *eq = 0; hotenv_set(ln + 2, eq + 1); LOG("env %s=%s", ln + 2, eq + 1); } }  /* «E NOMBRE=valor»: diagnóstico en caliente (VERB, GPUDRAWLOG…) sin arranque en frío */
            if (ln[0] == 'S' && ln[1] == ' ') { pthread_t th; char *nm = strdup(ln + 2); pthread_create(&th, 0, startevhot, nm); pthread_detach(th); }  /* «S id[:modelo]»: publica un evento del ModelManager en caliente */
            if (ln[0] == 'A' && ln[1] == ' ') { pthread_t th; char *nm = strdup(ln + 2); pthread_create(&th, 0, acqhot, nm); pthread_detach(th); }  /* «A i»: acquireStatus(i) en caliente */
            if (ln[0] == 'M' && ln[1] == ' ') { pthread_t th; char *nm = strdup(ln + 2); pthread_create(&th, 0, modelhot, nm); pthread_detach(th); }  /* «M @Mxxx»: crea el modelo en caliente */
            if (ln[0] == 'O') { pthread_t th; char *nm = strdup(ln + 2); pthread_create(&th, 0, openhot, nm); pthread_detach(th); }  /* «O vista»: viewManagerIf::openView(vista, 0) en caliente */
            if (ln[0] == 'Y') date_type = (int)hexv(ln + 2, &e);
            if (ln[0] == 'R') live_force = 1;  /* el anfitrión se acaba de conectar (p. ej. tras restaurar el estado): reenviar el fotograma actual */
            if (ln[0] == 'K') { unsigned m[12] = {0}; static int swallow; m[0] = hexv(ln + 2, &e); m[2] = hexv(e + 1, &e); m[4] = hexv(e + 1, &e);
                if (m[0] == 0x1ab && m[2] == 1 && !menu_open) { swallow = 1; menu_open = 1; pthread_t th; pthread_create(&th, 0, openhot, strdup("@V00E")); pthread_detach(th); LOG("MENU con el menú cerrado: openView @V00E"); }
                else if (m[0] == 0x1ab && swallow) { if (m[2] == 0) swallow = 0; }  /* la suelta de la pulsación que abrió el menú no llega a la UI */
                else { mbx_post_raw(0x7a0020, m); if (wl_on()) wl_key(m[0]); } }
            ln = nl + 1;
        }
        n = strlen(ln); memmove(buf, ln, n);
    }
    return 0;
}
static void *live_frames(void *a) {
    (void)a; unsigned seen = 0; unsigned char *last = 0, *cur = 0; size_t cap = 0;
    for (;;) {
        if (live_seq == seen && !live_force) { fut_wait(&live_seq, seen, 100); if (live_seq == seen && !live_force) continue; }  /* despierta con cada copia a pantalla; 100 ms por si llega «R» (live_force) */
        int force = live_force; live_force = 0; seen = live_seq; unsigned wd = live_w, ht = live_h; size_t len = (size_t)wd * ht * 2;
        unsigned char *p = phys2pn(live_da, len); if (!p || !len) continue;
        if (len > cap) { free(last); free(cur); last = calloc(1, len + 24); cur = malloc(len + 24); cap = len; }
        memcpy(cur + 24, p, len);
        if (!force && !memcmp(cur + 24, last + 24, len)) continue;
        unsigned hd[6] = {0x464b3641, wd | ht << 16, st_lists, st_rast, st_gpu, st_ldec};  /* «A6KF», ancho | alto << 16, contadores */
        memcpy(cur, hd, 24);
        pthread_mutex_lock(&live_wm);
        for (size_t o = 0; o < len + 24; ) { ssize_t k = write(live_fd, cur + o, len + 24 - o); if (k <= 0) { usleep(10000); continue; } o += k; }
        pthread_mutex_unlock(&live_wm);
        if (wl_on()) efp("[shim] WAITLOG %.2f fotograma enviado seq=%u\n", wl_ts(), seen);
        unsigned char *t = last; last = cur; cur = t;
    }
    return 0;
}
static void live_init(void) {
    const char *dev = getenv("LIVE"); if (!dev) return;
    static int (*op)(const char *, int, ...); if (!op) op = dlsym(RTLD_NEXT, "open");
    live_fd = op(dev, O_RDWR); if (live_fd < 0) { efp("[shim] LIVE %s no se abre\n", dev); return; }
    pthread_t t; pthread_create(&t, 0, live_keys, 0); pthread_create(&t, 0, live_frames, 0); efp("[shim] LIVE %s listo\n", dev);
}
/* GPUDUMP=fichero: cada lista de órdenes (pares {reg<<16|0xf000, valor} hasta la marca 0x12345678) se anexa en texto: «JOB n lista=… » + «reg valor» */
static void gpu_dumplist(unsigned list, int n) {
    const char *fn = getenv("GPUDUMP"); if (!fn || !list) return;
    unsigned *w = (unsigned *)phys2p(list); if (!w) { efp("[shim] GPUDUMP lista %#x sin área\n", list); return; }
    FILE *f = fopen(fn, "a"); if (!f) return; fprintf(f, "JOB %d lista=%#x\n", n, list);
    if (gw1) { fprintf(f, "TABLA"); for (int i = 0xe8 / 4; i < (0xe8 + 0x100) / 4; i++) fprintf(f, " %x:%08x", i * 4, gw1[i]); fprintf(f, "\n"); }
    unsigned ib = 0, vb = 0, drawn = 0;  /* 0x203 = índices (u16), 0x216 = vértices (0x40 B: pos 3f, color 4f, uv 2f…), §5.18z */
    for (int i = 0; i < 20000; ) {
        unsigned h = w[i], v = w[i + 1], ne = ((h >> 12) & 0xf) && (h & 0xfff) == 0x026 ? 5 : 1;  /* 0x026: valor + 4 palabras (uniformes 0x450) */
        fprintf(f, "%04x %08x", h >> 16, h & 0xffff); for (unsigned k = 1; k <= ne; k++) fprintf(f, " %08x", w[i + k]); fprintf(f, "\n");
        if ((h >> 12) & 0xf && !drawn) { if ((h >> 16) == 0x203) ib = v; if ((h >> 16) == 0x216) vb = v; if ((h >> 16) == 0x202) drawn = v & 0xfff; }  /* estado del primer disparo: después la lista redefine 0x216 (sublistas 0x281) */
        i += 1 + ne;
        if ((h >> 16) == 0x10 && v == 0x12345678) break;
        if (!h && !v) { fprintf(f, "FIN-NULO\n"); break; }
    }
    /* shortcut: copia hecha en el hilo de GPUEMU unos ms después del timbre, no en el timbre; vale mientras la UI no reescriba el búfer antes */
    unsigned short *ix = ib ? (unsigned short *)phys2p(ib) : 0; unsigned char *vx = vb ? phys2p(vb) : 0;
    if (ix && vx) for (unsigned k = 0; k < (drawn && drawn <= 64 ? drawn : 4); k++) {  /* nº de vértices = 0x202 & 0xfff (4 cuadrilátero, 16 marco de 9 trozos) */ float *q = (float *)(vx + ix[k] * 0x40u); fprintf(f, "VTX %u", ix[k]); for (int c = 0; c < 16; c++) fprintf(f, " %g", q[c]); fprintf(f, "\n"); }
    fclose(f);
}
static void *gpu_thread(void *a) {
    (void)a; unsigned done = 0; const char *e = getenv("GPUEMU_MS"); unsigned ms = e ? (unsigned)num(e) : 3; int n = 0, rast = getenv("GPURAST") || getenv("LIVE");
    for (;;) {
        if (getenv("RINGWATCH")) usleep(100); else if (gpu_kicks == done) fut_wait(&gpu_kicks, done, 0);  /* RINGWATCH necesita el pulso de 100 µs; si no, duerme hasta el timbre */
        if (getenv("RINGWATCH") && gw1) {  /* RINGWATCH=1: cada ~2 s, entradas de la tabla de trabajos (ventana +0xe8, 0x8c B) con algún dato; byte 0 = en curso */
            static unsigned tick; if (++tick % 20000 == 0) {
                char b[800]; int o = 0, c = 0; for (unsigned q = 0; q < 0x320 && c < 6 && 0xe8 + (q + 1) * 0x8c <= 0x20000; q++) { volatile unsigned *e = gw1 + (0xe8 + q * 0x8c) / 4; int nz = 0; for (int i = 0; i < 35; i++) if (e[i]) nz = 1; if (nz) { c++; o += snprintf(b + o, sizeof b - o, " [%u: b0=%u w1=%#x w2=%#x w3=%#x w4=%#x w5=%#x w6=%#x]", q, (unsigned)(e[0] & 0xff), e[1], e[2], e[3], e[4], e[5], e[6]); } }
                efp("[shim] RING kicks=%u +4=%#x +c=%#x +10=%#x +14=%#x:%s\n", gpu_kicks, gw1[1], gw1[3], gw1[4], gw1[5], b);
            }
        }
        if (gpu_kicks == done) continue;
        unsigned k = done++, v = kick_list[k % 64];  /* una vuelta por timbre, en orden */
        gw1[5] = 1;  /* ocupada → inactiva: el hilo GL espera el 2 (libObj+0x6c35a0/0x6c66c4) */
        if (rast) { unsigned t0 = now_us(); gpu_draw(v); st_rast += now_us() - t0; st_lists++; } else usleep(ms * 1000u);
        gpu_done = done; fut_wake(&gpu_done);
        gw1[5] = 2; gpu_last_us = now_us(); gpu_irq_seq++; fut_wake(&gpu_irq_seq);
        if (!gpu_live) continue;
        if (n++ < 40) efp("[shim] GPUEMU lista %d: %#x\n", n, v);
        gpu_dumplist(v, n);
    }
    return 0;
}
static void gpuemu_add(const char *dev, off_t off, void *p, size_t len) {
    const char *g = getenv("GPUEMU"); if (g && g[0] == '0') return;
    if (len != 0x20000) return;
    if (!strcmp(dev, "/dev/mem") && off == 1) gw0 = p; else if (!strcmp(dev, "/dev/dmpgles2")) gw1 = p; else return;
    static int th; if (gw0 && gw1 && !th++) {
        pthread_t t; pthread_create(&t, 0, gpu_thread, 0);
    }
}
static void regtrap_add(void *p, size_t len) {
    if (nrtw >= 2 || len > 0x20000) return;
    rtw[nrtw].p = p; rtw[nrtw].len = len; efp("[shim] REGTRAP ventana w%d = %p\n", nrtw, p); nrtw++;
    if (nrtw == 1) { struct sigaction sa; memset(&sa, 0, sizeof sa); sa.sa_sigaction = rt_segv; sa.sa_flags = SA_SIGINFO | SA_NODEFER; sigaction(SIGSEGV, &sa, &rt_old); }
    if (nrtw == 2 || 1) { static int th; if (!th++) { pthread_t t; pthread_create(&t, 0, rt_thread, 0); } }
}
/* mmap de dispositivos no modelados (/dev/mem, fb, ...): memoria anónima a cero */
void *mmap(void *a, size_t l, int pr, int fl, int fd, off_t o) {
    static void *(*m)(void *, size_t, int, int, int, off_t);
    if (!m) m = dlsym(RTLD_NEXT, "mmap");
    if (fd >= 0 && fd < MAXFD && kind[fd] == D_GENERIC) {
        if (!l) l = 0x1000;  /* shortcut: len 0 no es válido; el monitor de MWF lo pide sin argumentos */
        void *r = m(a, l, pr, (fl & ~MAP_SHARED) | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (r != MAP_FAILED && nam < 64) { amaps[nam].p = r; amaps[nam].len = l; amaps[nam].off = o; strncpy(amaps[nam].dev, devname[fd], 31); nam++; }
        if (r != MAP_FAILED && !strcmp(devname[fd], "/dev/dmpgles2") && l == 0x20000) { ((unsigned *)r)[1] = 0xffffffffu; ((unsigned *)r)[5] = 2; }  /* reg +4 = cabeza de la cola de ejecución (libObj+0x6c60e0/0x6c61b0); 0xffffffff = vacía; reg +0x14 = estado de la GPU (el bucle del hilo GL, libObj+0x6c35a0/0x6c66c4, gira hasta que vale 2 = inactiva). A 0 el planificador sacaría una y otra vez el trabajo 0 de la cola */
        if (r != MAP_FAILED) gpuemu_add(devname[fd], o, r, l);
        if (getenv("REGTRAP") && r != MAP_FAILED && ((!strcmp(devname[fd], "/dev/dmpgles2") && l == 0x20000) || (!strcmp(devname[fd], "/dev/mem") && l == 0x20000 && o == 1))) regtrap_add(r, l);
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

static int mw_secs(void); static const char *tname(int, char *, size_t); static unsigned libobj_off(void *);
/* Experimento (CVWAIT=s): el solicitante de libObj+0x719ed8 (patrón «trabajador», fw 3.21) espera el fin del trabajo sin sostener su
 * cerrojo y puede perder la señal; solo ese punto de llamada espera con tope de s segundos (despertar espurio).
 * El resto de esperas (p. ej. el bucle del trabajador, que no tolera despertares espurios) queda intacto. */
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
    if (mw_secs()) {  /* espera con tope para poder registrar quién se queda esperando una condición */
        static void *seen[64]; static int ns; void *ra = __builtin_return_address(0); struct timespec ts; int k, ya = 0;
        clock_gettime(CLOCK_REALTIME, &ts); ts.tv_sec += mw_secs();
        int r = pthread_cond_timedwait(c, m, &ts);
        if (r == 110) {
            for (k = 0; k < ns; k++) if (seen[k] == ra) ya = 1;
            if (!ya && ns < 64) { char a[32]; seen[ns++] = ra; efp("[shim] MUTEXWATCH %s (tid %ld) espera condición %p (cerrojo %p) > %d s; llamador libObj+%#x\n", tname((int)syscall(224), a, sizeof a), (long)syscall(224), (void *)c, (void *)m, mw_secs(), libobj_off(ra)); }
            return real(c, m);
        }
        return r;
    }
    { int ws = wl_begin("cond_wait", (unsigned)(unsigned long)c, -1, __builtin_return_address(0)); int rr = real(c, m); wl_end(ws); return rr; }
}
/* MUTEXWATCH=s: un pthread_mutex_lock que espera más de s segundos registra quién lo retiene (glibc 2.11 ARM: __owner en +8) y manda
 * SIGUSR1 al dueño y al solicitante (pila). pthread_cond_wait con MUTEXWATCH registra una vez por llamador las esperas > s con dirección
 * de la condición y del cerrojo. Solo se activa con la variable (coste cero sin ella). */
static int mw_secs(void) { static int v = -1; if (v < 0) { const char *e = getenv("MUTEXWATCH"); v = 0; while (e && *e >= '0' && *e <= '9') v = v * 10 + *e++ - '0'; } return v; }
static const char *tname(int tid, char *b, size_t n) { char fn[64]; snprintf(fn, sizeof fn, "/proc/self/task/%d/comm", tid); FILE *f = fopen(fn, "r"); b[0] = 0; if (f) { if (!fgets(b, n, f)) b[0] = 0; fclose(f); } for (char *c = b; *c; c++) if (*c == '\n') *c = 0; return b; }
static unsigned libobj_off(void *ra) { Dl_info di; return (dladdr(ra, &di) && di.dli_fname && strstr(di.dli_fname, "libObj.so")) ? (unsigned)((unsigned long)ra - (unsigned long)di.dli_fbase) : 0; }
static int mt_suffix(void) { static int v = -2; if (v == -2) { const char *e = getenv("MUTEXTRACE"); v = e ? (int)hexv(e, 0) : -1; } return v; }
static void mt_log(const char *what, pthread_mutex_t *m, void *ra) { static int n; if (mt_suffix() >= 0 && (((unsigned long)m & 0xfff) == (unsigned long)mt_suffix()) && n < 6000) { n++; char a[32]; efp("[shim] MUTEXTRACE %s %p tid %ld %s libObj+%#x\n", what, (void *)m, (long)syscall(224), tname((int)syscall(224), a, sizeof a), libobj_off(ra)); if (getenv("MUTEXSTACK") && what[0] == 'l' && strstr(a, getenv("MUTEXSTACK"))) raise(SIGUSR1); } }
int pthread_mutex_lock(pthread_mutex_t *m) {
    static int (*real)(pthread_mutex_t *), (*tl)(pthread_mutex_t *, const struct timespec *);
    if (!real) { real = dlsym(RTLD_NEXT, "pthread_mutex_lock"); tl = dlsym(RTLD_NEXT, "pthread_mutex_timedlock"); }
    mt_log("lock", m, __builtin_return_address(0));
    int w = mw_secs(); if (!w || !tl) return real(m);
    struct timespec ts; clock_gettime(CLOCK_REALTIME, &ts); ts.tv_sec += w;
    int r = tl(m, &ts);
    if (r != 110 /* ETIMEDOUT */) return r;
    int owner = ((int *)m)[2]; char a[32], b[32]; unsigned off = libobj_off(__builtin_return_address(0));
    efp("[shim] MUTEXWATCH %s (tid %ld) espera cerrojo %p > %d s; dueño tid %d (%s); llamador libObj+%#x\n", tname((int)syscall(224), a, sizeof a), (long)syscall(224), (void *)m, w, owner, tname(owner, b, sizeof b), off);
    if (owner > 0 && !getenv("LOCKSTEAL")) syscall(SYS_tgkill, getpid(), owner, SIGUSR1);
    if (getenv("LOCKSTEAL")) { efp("[shim] LOCKSTEAL: se libera a la fuerza el cerrojo %p (dueño %d)\n", (void *)m, owner); ((int *)m)[2] = 0; ((int *)m)[0] = 0; __sync_synchronize(); }  /* LOCKSTEAL=1: experimento, carrera de datos asumida */
    return real(m);
}
/* FAIRMUTEX=us: tras soltar un cerrojo con esperadores (glibc 2.11: __lock == 2) el hilo duerme us µs para que un esperador lo tome; los mutex de glibc no son
 * justos y el hilo trabajador de la GPU (que lo vuelve a tomar enseguida) deja sin cerrojo al hilo de la aplicación. */
int pthread_mutex_unlock(pthread_mutex_t *m) {
    static int (*real)(pthread_mutex_t *); static int us = -1;
    if (!real) real = dlsym(RTLD_NEXT, "pthread_mutex_unlock");
    if (us < 0) { const char *e = getenv("FAIRMUTEX"); us = 0; while (e && *e >= '0' && *e <= '9') us = us * 10 + *e++ - '0'; }
    mt_log("unlock", m, __builtin_return_address(0));
    int w = us ? ((int *)m)[0] : 0, r = real(m);
    if (w == 2) usleep(us);
    return r;
}
/* Registro de munmap grandes (MMapBase de libObj aborta si desmapea algo no mapeado). */
int munmap(void *a, size_t l) {
    static int (*m)(void *, size_t);
    if (!m) m = dlsym(RTLD_NEXT, "munmap");
    int r = m(a, l);
    if (l >= 0x100000 || r) LOG("munmap(%p, %#zx) -> %d", a, l, r);
    return r;
}

/* THRLOG=1: registra pthread_create (hilo, rutina inicial) y pthread_join (objetivo) para saber a qué hilo espera el hilo principal de im.elf. */
static void thr_desc(void *f, char *o, int n) { Dl_info di; if (dladdr(f, &di) && di.dli_fname) snprintf(o, n, "%s+%#lx", strrchr(di.dli_fname, '/') ? strrchr(di.dli_fname, '/') + 1 : di.dli_fname, (unsigned long)f - (unsigned long)di.dli_fbase); else snprintf(o, n, "%p", f); }
int pthread_create(pthread_t *t, const pthread_attr_t *a, void *(*f)(void *), void *arg) {
    static int (*r)(pthread_t *, const pthread_attr_t *, void *(*)(void *), void *);
    if (!r) r = dlsym(RTLD_NEXT, "pthread_create");
    int rc = r(t, a, f, arg);
    if (getenv("THRLOG")) { char d[96]; thr_desc((void *)f, d, sizeof d); LOG("pthread_create %lx fn=%s (desde tid %ld)", (unsigned long)*t, d, (long)syscall(224)); }
    return rc;
}
int pthread_join(pthread_t t, void **v) {
    static int (*r)(pthread_t, void **); static int nmj;
    if (!r) r = dlsym(RTLD_NEXT, "pthread_join");
    if (getenv("THRLOG")) LOG("pthread_join %lx (tid %ld)", (unsigned long)t, (long)syscall(224));
    /* NOJOIN=N: desde el N-ésimo join del hilo principal (1 = todos) no espera; el hilo principal de im.elf no espera a los hilos de infra (en la cámara los procesos im.elf van por letras y el último solo atiende mensajes; aquí un único proceso
     * ejecuta las fases y THREAD_INFRA1 queda en el bucle de MWF para siempre): así llega a su bucle de recepción (0x9e94). shortcut: afecta a todo join del hilo principal. */
    if (getenv("NOJOIN") && syscall(224) == getpid() && ++nmj >= (int)num(getenv("NOJOIN"))) { LOG("pthread_join %lx omitido (NOJOIN)", (unsigned long)t); return 0; }
    return r(t, v);
}
