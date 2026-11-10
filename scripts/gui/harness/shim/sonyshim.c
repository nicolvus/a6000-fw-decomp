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

#define LOG(...) do { fprintf(stderr, getenv("TIDLOG") ? "[shim %ld] " : "[shim] ", (long)syscall(224)); fprintf(stderr, __VA_ARGS__); fputc('\n', stderr); } while (0)

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
    case 8: break;                                                              /* write: se descarta */
    default: LOG("backup op=%u n=%u id0=%#x (sin modelar)", op, n, id[0]);
    }
    if (getenv("BKV") || !d) LOG("backup op=%u n=%u id=%#x len=%u r=%#x %s", op, n, id[0], len, m[1], d ? "" : "ausente");
}

/* Servicios de kernel por snd_sync_direct (mm 0x910042, ...). shortcut: sin modelar, responde 0 */
/* 0x90013d cmd 2 = osal_get_date (ModelRoot::getDateInfo, libObj+0x63c2bc): +0x12 estado, +0x1c tipo (0 sin hora, 1/3 asentada; DATETYPE, 1 por defecto). */
static unsigned long hexv(const char *s, const char **end);
static int direct_service(unsigned qid, unsigned *m) {
    if (m[0] == 0x28 && ((unsigned short *)m)[8] == 2 && !getenv("NODATE")) {
        unsigned short *h = (unsigned short *)m; const char *e = getenv("DATETYPE");
        h[9] = 0; h[14] = e ? (unsigned short)hexv(e, 0) : 1;
        h[10] = 2026; h[11] = 11; h[12] = 10; h[13] = 13;  /* shortcut: fecha fija; formato (+0x14: 4×u16 + tipo en +0x1c) inferido de libObj+0x63cf6c (memcpy de 10 B), sin comprobar */
        static int n; if (n++ < 3) LOG("direct %#x get_date -> tipo %u", qid, h[14]);
    }
    return 0;
}

/* Buzones de colas dinámicas de kernel (dynamic_id tipo 0x2a): el servicio 0xd9016e (registro de puerto de vídeo/OSD) se responde copiando la petición. */
static struct { unsigned q; void *msg; } mbx[16];
static unsigned dynq[64]; static int ndynq;  /* colas creadas por dynamic_id tipo 0x2a (solo ellas tienen buzón) */
static pthread_mutex_t mbx_m = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t mbx_c = PTHREAD_COND_INITIALIZER;
static void dynq_add(unsigned q) { pthread_mutex_lock(&mbx_m); if (ndynq < 64) dynq[ndynq++] = q; else LOG("dynq lleno: %#x sin buzón", q); pthread_mutex_unlock(&mbx_m); }
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
static volatile int gpu_ack;  /* GPUEMU: el controlador reconoció el aviso de fin de trabajo */
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

int ioctl(int fd, unsigned long req, ...) {
    static int (*r)(int, unsigned long, ...);
    va_list a; va_start(a, req); void *arg = va_arg(a, void *); va_end(a);
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
        case 1: { LOG("uipc wai_sem? %#x tmo=%d", w[0], (int)w[1]); int r = sem_wait(w[0], (int)w[1]); LOG("uipc wai_sem %#x tmo=%d -> %d", w[0], (int)w[1], r); return r; }
        case 2: sem_sig(w[0]); LOG("uipc sig_sem %#x", w[0]); return 0;
        case 7: { unsigned *t = (unsigned *)w[1]; LOG("uipc rcv_msg qid=%#x tmo=%d", w[0], (int)t[1]);
            if ((int)t[1] < 0 && getenv("RCVSTACK")) { static unsigned vq[64]; static int nq; int k, ya = 0; for (k = 0; k < nq; k++) if (vq[k] == w[0]) ya = 1; if (!ya && nq < 64) { vq[nq++] = w[0]; raise(SIGUSR1); } }
            { void *mm; int rr = mbx_take(w[0], (int)t[1], &mm); if (rr == 0) { *(void **)t[0] = mm; LOG("rcv_msg qid=%#x <- respuesta", w[0]); return 0; } if (rr != 1) return rr; }
            return kernel_sleep((int)t[1]); }
        case 13: {  /* wait_cb {0, &out[4]}: el proxy espera una entrega y llama out[0](out[2], out[1]) */
            unsigned *out = (unsigned *)w[1];
            pthread_mutex_lock(&cb_m);
            while (dlv_r == dlv_w) pthread_cond_wait(&cb_c, &cb_m);
            out[0] = (unsigned)dlv[dlv_r % 256].cb; out[1] = (unsigned)dlv[dlv_r % 256].arg; out[2] = (unsigned)dlv[dlv_r % 256].msg; out[3] = 0; dlv_r++;
            pthread_mutex_unlock(&cb_m);
            if (getenv("VERB")) LOG("wait_cb -> cb %#x msg %#x", out[0], out[2]);
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
        case 3: LOG("uipc stat_msgq %#x (sin modelar: 0)", w[0]); return 0;
        case 5: {  /* snd_sync_msg {qid, &{msg, cb, arg}}: 0x8f013a es el registro de trazas (u16 + texto "%4X %s %s") */
            unsigned *t5 = (unsigned *)w[1];
            unsigned char *m = (unsigned char *)t5[0];
            if (t5[1]) return 0;  /* segunda llamada del emisor: fin del callback síncrono */
            { static int ns5; const char *e = getenv("STACKQ"); if (e && hexv(e, 0) == w[0] && ++ns5 == 3) raise(SIGUSR1); }  /* STACKQ=qid: pila del emisor en el 3.er envío */
            { pthread_mutex_lock(&cb_m); int k = cb_find(w[0]); if (k >= 0) { t5[1] = (unsigned)cbs[k].cb; t5[2] = (unsigned)cbs[k].arg; } pthread_mutex_unlock(&cb_m);
              if (k >= 0) { if (getenv("VERB")) LOG("snd_sync_msg %#x -> callback directo", w[0]); return 0; } }
            if (w[0] == 0x8f013a) { if (m[2]) LOG("LOG %s", (char *)m + 2); else if (getenv("VERB")) { char t[200]; int k, o = 0; for (k = 0; k < 40; k++) o += snprintf(t + o, sizeof t - o, "%02x", m[k]); LOG("LOGRAW %s", t); } }
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
                  if (ka && kp && is_dynq(0x7a0020)) { unsigned kc = hexv(kp + 32, 0), kmsg[6] = { kc, 0, hexv(ka, 0), 0, 0, 0 }; mbx_post(0x7a0020, kmsg, 0); LOG("KEYONACTIVE key=%#x status=%#x", kc, kmsg[2]); } }
                if (strstr(t, "MMapBase")) { char h[500]; int o = 0; for (k = 0; k < 200; k++) o += snprintf(h + o, sizeof h - o, "%02x", m[k]); LOG("TRAZAHEX %s", h); }
                return 0; }
            if (w[0] == 0x80003b && !getenv("NOVDF")) {  /* display vdf del kernel */
                unsigned cmd = ((unsigned *)m)[0], p1 = ((unsigned *)m)[1];
                if (cmd < 16 && p1 > 0x10000 && ((cmd & 1) == 0 || cmd == 9)) { vdfcb[cmd] = (void *)p1; return 0; }
                if ((cmd & 1) && cmd < 8) { pthread_t t; pthread_create(&t, 0, vdf_ack, (void *)(unsigned long)cmd); pthread_detach(t); return 0; }
            }
            if (cb_deliver(w[0], m)) { if (getenv("VERB")) LOG("snd_msg %#x -> callback", w[0]); return 0; }
            /* Servicios de kernel con acuse genérico (ACKQ=d9016e,7a0029,…; 0xd9016e registro de puerto de vídeo, 0x7a0029 input.ko): se
             * responde a la cola dinámica que viaja en el cuerpo copiando la petición con estado 0 (lo que comprueba el emisor síncrono
             * 0x6a2550 de libObj). shortcut: a 0x61003c la misma respuesta hace saltar la aserción de 0x6a25d2; modelarla cuando se conozca su formato. */
            { const char *e = getenv("ACKQ"); if (!e) e = "d9016e,7a0029,61003c"; int ack = 0;
              while (*e) { if (hexv(e, &e) == w[0]) ack = 1; while (*e == ',') e++; }
              if (ack) for (int k = 0; k < 6; k++) if (is_dynq(((unsigned *)m)[k])) { mbx_post(((unsigned *)m)[k], (unsigned *)m, w[0] == 0x61003c); LOG("snd_msg %#x -> acuse genérico a %#x (palabra %d)", w[0], ((unsigned *)m)[k], k); return 0; } }
            if (w[0] == 0x9a015a || w[0] == 0x9c015b) { static int n; if (n++ < 4) raise(SIGUSR1); if (n > 5) { usleep(20000); return 0; } }  /* bucle HDMI: pila y silencio */
            if (getenv("VERB")) { char h[200]; int k, o = 0; for (k = -32; k < 32; k++) o += snprintf(h + o, sizeof h - o, "%02x", m[k]); LOG("MSGHEX %#x %s", w[0], h); }
            LOG("uipc snd_msg a la cola de kernel %#x (descartado) cab=%02x%02x%02x%02x datos=%08x %08x", w[0], m[-12], m[-11], m[-10], m[-9],
                ((unsigned *)m)[0], ((unsigned *)m)[1]); return 0; }
        case 6: { unsigned char *m = (unsigned char *)w[1]; char h[200]; int k, o = 0;
            for (k = 0; k < 64; k++) o += snprintf(h + o, sizeof h - o, "%02x", m[k]);
            if (getenv("VERB")) LOG("uipc snd_sync_direct qid=%#x msg=%s", w[0], h); return direct_service(w[0], (unsigned *)m); }
        default: LOG("uipc ioctl idx=%u args %#x %#x (ignorada)", idx, w[0], w[1]); return 0;
        }
    }
    if (fd >= 0 && fd < MAXFD && kind[fd] == D_GENERIC) {  /* dispositivo no modelado: éxito, registrado las 5 primeras veces por (dispositivo, orden) y luego cada 4096 */
        static struct { char d[32]; unsigned long r; unsigned n; } seen[64]; static int ns; int k;
        if (!strcmp(devname[fd], "/dev/dmpgles2") && req == 0x80048206 && arg) *(unsigned *)arg = 0x20000;  /* tamaño de la ventana de registros de la GPU (rm_reg_init lo pasa a mmap de /dev/mem; con 0 se mapeaba 1 página y el código escribe en +0x1804) */
        if (!strcmp(devname[fd], "/dev/dmpgles2") && req == 0xc0048212 && arg && *(unsigned *)arg == 1) gpu_ack = 1;  /* el controlador reconoce el aviso de fin (GPUEMU) */
        if (getenv("GPUTRACE") && gpu_live && !strcmp(devname[fd], "/dev/dmpgles2")) { static int gn; if (gn++ < 600) LOG("GPU ioctl %#lx arg=%p val=%#x", req, arg, (unsigned long)arg > 0x10000 ? *(unsigned *)arg : 0u); }  /* GPUTRACE=1: cada ioctl de la GPU tras cargar las vistas (primeros 600), sin deduplicar */
        if (!strcmp(devname[fd], "/dev/dmpgles2") && req == 0xc004820d) {  /* espera de interrupción de la GPU (libObj+0x6c5320 repite hasta salida != 0) */
            const char *e = getenv("GPUIRQ_MS"); unsigned ms = e ? (unsigned)num(e) : 20;  /* GPUIRQ_MS=n: IRQ simulada cada n ms (20 por defecto, necesaria para que termine la init GL); 0 = GPU ociosa, duerme */
            if (ms && arg) { usleep(ms * 1000u); *(unsigned *)arg = 1; return 0; }
            for (;;) sleep(3600);
        }
        if (!strcmp(devname[fd], "/dev/dmpgles2") && req == 0xc0048211 && arg) *(unsigned *)arg = 0;  /* espera de la GPU de DMP (libObj+0x6c53e0): repite mientras la salida != 0 → «ya ha terminado» */
        pthread_mutex_lock(&semlock);
        for (k = 0; k < ns && (seen[k].r != req || strcmp(seen[k].d, devname[fd])); k++);
        if (k == ns && ns < 64) { strncpy(seen[ns].d, devname[fd], 31); seen[ns].r = req; seen[ns++].n = 0; }
        unsigned n = k < 64 ? seen[k].n++ : 0;
        pthread_mutex_unlock(&semlock);
        if (n == 3 && getenv("DEVSTACK")) raise(SIGUSR1);  /* pila del llamador de la 4.ª repetición */
        if (n < 5 || !(n & 4095)) { Dl_info di; void *ra = __builtin_return_address(0); int ok = dladdr(ra, &di) && di.dli_fname;
            LOG("ioctl(%s, %#lx, %p) arg0=%#x [n=%u] desde %s+%#lx", devname[fd], req, arg, (unsigned long)arg > 0x10000 ? *(unsigned *)arg : (unsigned)(unsigned long)arg, n, ok ? di.dli_fname : "?", ok ? (unsigned long)ra - (unsigned long)di.dli_fbase : 0UL); }
        return 0;
    }
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
    char nm[24] = {0}; syscall(SYS_prctl, 16, nm); efp("[shim] --- pila (sig %d tid %ld %s) pc/lr:\n", sig, (long)syscall(SYS_gettid), nm); efp("[shim]   raw pc=%08lx lr=%08lx addr=%08lx r0=%08lx r1=%08lx r2=%08lx\n", uc->uc_mcontext.arm_pc, uc->uc_mcontext.arm_lr, (unsigned long)si->si_addr, uc->uc_mcontext.arm_r0, uc->uc_mcontext.arm_r1, uc->uc_mcontext.arm_r2); sym(uc->uc_mcontext.arm_pc); sym(uc->uc_mcontext.arm_lr);
    for (int i = 0; i < 300; i++) { if (((unsigned long)(sp + i) & 0xfff) == 0 || i == 0) { if (msync((void *)((unsigned long)(sp + i) & ~0xfffUL), 1, MS_ASYNC)) break; } sym(sp[i]); }  /* no cruzar el final de la pila */
    (void)sig;
}
#include <dirent.h>
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
static void *openviewer(void *a) {
    (void)a; sleep(num(getenv("OPENVIEWAT") ? getenv("OPENVIEWAT") : "40"));
    int (*ov)(const char *, int) = lobj_h ? dlsym(lobj_h, "_ZN13viewManagerIf8openViewEPKci") : 0;
    if (!ov) { efp("[shim] OPENVIEW: sin viewManagerIf::openView\n"); return 0; }
    if (getenv("PREACQ") && lobj_h) {  /* PREACQ=modelo: pide un «execute» al modelo antes de abrir vistas (¿fuerza su creación?) */
        int (*rq)(const char *, unsigned long, void *) = dlsym(lobj_h, "_ZN13viewManagerIf19requestModelExecuteEPKcmP9ParamList");
        void (*ctor)(void *) = dlsym(RTLD_DEFAULT, "_ZN9ParamListC1Ev"); static char lb[512];
        if (rq && ctor) { ctor(lb); int rr = rq(getenv("PREACQ"), 0, lb); efp("[shim] PREACQ %s -> %d\n", getenv("PREACQ"), rr); sleep(3); }
    }
    char *spec = strdup(getenv("OPENVIEW")), *sv = 0;
    for (char *it = strtok_r(spec, ",", &sv); it; it = strtok_r(0, ",", &sv)) { efp("[shim] OPENVIEW %s ...\n", it); int r = ov(it, 0); efp("[shim] OPENVIEW %s -> %d\n", it, r); sleep(2); }
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
        if (!ok && is_dynq(q)) { mbx_post(q, m, 0); ok = 1; how = "buzón"; }  /* cola que un hilo lee con rcv_msg (p. ej. KEYQ=7a0020, el driver de entrada) */
        efp("[shim] INJECT q=%#x w0=%#x -> %s\n", q, m[0], ok ? how : "SIN CALLBACK NI BUZÓN");
    }
    return 0;
}
/* SEMSIG: semáforos que en la cámara señala otro procesador (av-cam) y aquí nadie; se dejan señalados al arrancar.
   0x83037a: el main de im.elf (antes de crear el hilo de aplicación appFw.so → UI) y luego el hilo Appframework esperan en él; se señala 4 veces. Lista hex separada por comas; vacío = ninguno. */
static void keyq_init(void) {  /* KEYQ=qid_hex[,…]: colas del kernel que un hilo de usuario lee con rcv_msg: se les da buzón (para INJECT) */
    const char *p = getenv("KEYQ"); while (p && *p) { const char *q; unsigned id = hexv(p, &q); if (q == p) break; dynq_add(id); p = *q == ',' ? q + 1 : q; }
}
static void presignal(void) {
    const char *e = getenv("SEMSIG"), *p = e ? e : "83037a,83037a,83037a,83037a";
    while (*p) { const char *q; unsigned id = hexv(p, &q); if (q == p) break; sem_sig(id); p = *q == ',' ? q + 1 : q; }
}
__attribute__((constructor)) static void shim_init(void) { presignal(); keyq_init(); if (getenv("INJECT")) { pthread_t th; pthread_create(&th, 0, injector, 0); } if (getenv("OPENVIEW")) { pthread_t th; pthread_create(&th, 0, openviewer, 0); } if (getenv("DUMPAT")) { pthread_t th; pthread_create(&th, 0, dumper, 0); } struct sigaction sa; memset(&sa, 0, sizeof sa); sa.sa_sigaction = on_usr1; sa.sa_flags = SA_SIGINFO; sigaction(SIGUSR1, &sa, 0);
    sa.sa_flags = SA_SIGINFO | SA_RESETHAND; sigaction(SIGSEGV, &sa, 0); sigaction(SIGBUS, &sa, 0); sigaction(SIGILL, &sa, 0); sigaction(SIGABRT, &sa, 0); }  /* un fallo imprime la pila y se reintenta por defecto (core) */

/* Experimento (SKIPFN=717830,...): sustituye esas funciones Thumb de libObj por «movs r0,#0; bx lr» (devuelven éxito sin hacer nada). */
static unsigned long hexv(const char *s, const char **end) { unsigned long v = 0; for (;; s++) { int c = *s; if (c >= '0' && c <= '9') c -= '0'; else if (c >= 'a' && c <= 'f') c -= 'a' - 10; else break; v = v * 16 + c; } if (end) *end = s; return v; }
static unsigned long gpu_pc;  /* libObj+0x6c4c46: «str r1,[r3,r0]» de rm_reg_write (off=r0, valor=r1, base=r3); se sustituye por UDF para ver cada escritura */
static volatile unsigned gpu_kicks;
/* Experimento (TRACEFN=716800,6cd1e0,...): traza de una sola vez (UDF + restauración) de la entrada de esas funciones de libObj: r0-r3 y lr. */
static struct { unsigned long pc; unsigned short orig; } trc[32]; static int ntrc; static unsigned long trc_base;
static void on_trace(int sig, siginfo_t *si, void *u) {
    mcontext_t *c = &((ucontext_t *)u)->uc_mcontext; unsigned long pc = c->arm_pc & ~1UL; int i;
    if (gpu_pc && pc == gpu_pc) {  /* rm_reg_write: se hace el almacenamiento y se salta la instrucción; 0x1804 = timbre de la GPU (GPUEMU) */
        *(volatile unsigned *)(c->arm_r3 + c->arm_r0) = c->arm_r1; if (c->arm_r0 == 0x1804) gpu_kicks++;
        { static int nw; if (getenv("GPUTRACE") && nw++ < 200) efp("[shim] REGW off=%#lx val=%#lx kicks=%u\n", c->arm_r0, c->arm_r1, gpu_kicks); }
        c->arm_pc += 2; return;
    }
    for (i = 0; i < ntrc; i++) if (trc[i].pc == pc) {  /* efp, no LOG: fprintf en un manejador de señal puede bloquearse con el cerrojo de stderr de otro hilo */
        efp("[shim] TRACE %lx r0=%lx r1=%lx r2=%lx r3=%lx lr=%lx\n", pc, c->arm_r0, c->arm_r1, c->arm_r2, c->arm_r3, c->arm_lr);
        for (const char *e = getenv("TRACEPEEK"); e && *e; ) { unsigned long a = hexv(e, &e); efp("[shim]   PEEK %lx = %08x\n", a, *(unsigned *)(trc_base + a)); while (*e == ',') e++; }
        { const char *e = getenv("TRACEDEREF");  /* «reg:off:palabras» (hex): vuelca palabras en *(reg+off), p. ej. 4:24:90 = tabla de teclas de InfraInput; con «d» delante («d0:a0:20») vuelca desde reg+off sin desreferenciar */
          if (e && *e) { int dr = *e == 'd'; e += dr; unsigned long rg = hexv(e, &e), off = hexv(e + 1, &e), n = hexv(e + 1, 0), *rv = &c->arm_r0; unsigned *q = dr ? (unsigned *)(rv[rg] + off) : (unsigned *)*(unsigned long *)(rv[rg] + off);
            for (unsigned long k = 0; k < n && q; k += 9) efp("[shim]   DEREF %p+%lx: %08x %08x %08x %08x %08x %08x %08x %08x %08x\n", q, k * 4, q[k], q[k+1], q[k+2], q[k+3], q[k+4], q[k+5], q[k+6], q[k+7], q[k+8]); } }
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
static volatile unsigned *gw0, *gw1;
static unsigned libobj_off(void *ra);
static struct { unsigned char *p; size_t len; unsigned snap[0x8000]; } rtw[2]; static int nrtw; static struct sigaction rt_old;
static void rt_segv(int sig, siginfo_t *si, void *ctx) {
    ucontext_t *uc = ctx; unsigned char *a = si->si_addr; static int n;
    for (int k = 0; k < nrtw; k++) if (a >= rtw[k].p && a < rtw[k].p + rtw[k].len) {
        static unsigned long seenk[512]; static int nseen; unsigned long key = ((unsigned long)k << 28) ^ ((unsigned long)(a - rtw[k].p) << 12) ^ (uc->uc_mcontext.arm_pc & 0xfff) ^ (((uc->uc_mcontext.error_code >> 11) & 1) << 27); int dup = 0;
        for (int q = 0; q < nseen; q++) if (seenk[q] == key) dup = 1;
        if (!dup && nseen < 512) { seenk[nseen++] = key; n = 0; } else n = 2000;
        if (n++ < 1500) efp("[shim] REGTRAP tid %ld %s w%d+%#lx pc=libObj+%#x lr=libObj+%#x\n", (long)syscall(224), (uc->uc_mcontext.error_code & (1 << 11)) ? "ESC" : "LEC", k, (unsigned long)(a - rtw[k].p), libobj_off((void *)uc->uc_mcontext.arm_pc), libobj_off((void *)uc->uc_mcontext.arm_lr));
        if (k == 0 && a >= rtw[0].p + 0x1000 && a < rtw[0].p + 0x2000) gpu_kicks++;  /* timbre de la GPU (GPUEMU) visto desde REGTRAP */
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
/* GPUEMU (activo por defecto; GPUEMU=0 lo desactiva): GPU de DMP mínima. Ventanas: gw0 = motor (/dev/mem off=1; el controlador empuja la dirección de la lista de
 * órdenes en +0x1804), gw1 = registros de /dev/dmpgles2 (+4 índice del trabajo terminado, 0xffffffff = ninguno; +0x10 resultados pendientes; +0x14 estado, 2 = inactiva).
 * Al cambiar +0x1804: estado «ocupada» (1) unos GPUEMU_MS ms, luego se avisa del fin (+4 = GPUEMU_JOB, +0x10 = 1) y la GPU vuelve a 2; el aviso se retira cuando el
 * controlador lo reconoce con ioctl 0xc0048212 (arg 1). shortcut: no se ejecuta ninguna orden (no hay dibujo); solo desbloquea los hilos que esperan a la GPU. */
static unsigned char *phys2p(unsigned phys) {  /* fase → dirección en nuestras áreas anónimas de /dev/stream y /dev/mem */
    for (int k = 0; k < nam; k++) { unsigned long o = (unsigned long)amaps[k].off; if ((!strstr(amaps[k].dev, "stream") && !strstr(amaps[k].dev, "mem")) || o < 0x80000000ul) continue; if (phys >= o && phys < o + amaps[k].len) return (unsigned char *)amaps[k].p + (phys - o); }
    return 0;
}
/* GPUDUMP=fichero: cada lista de órdenes (pares {reg<<16|0xf000, valor} hasta la marca 0x12345678) se anexa en texto: «JOB n lista=… » + «reg valor» */
static void gpu_dumplist(unsigned list, int n) {
    const char *fn = getenv("GPUDUMP"); if (!fn || !list) return;
    unsigned *w = (unsigned *)phys2p(list); if (!w) { efp("[shim] GPUDUMP lista %#x sin área\n", list); return; }
    FILE *f = fopen(fn, "a"); if (!f) return; fprintf(f, "JOB %d lista=%#x\n", n, list);
    if (gw1) { fprintf(f, "TABLA"); for (int i = 0xe8 / 4; i < (0xe8 + 0x100) / 4; i++) fprintf(f, " %x:%08x", i * 4, gw1[i]); fprintf(f, "\n"); }
    for (int i = 0; i < 20000; i += 2) { unsigned h = w[i], v = w[i + 1]; fprintf(f, "%04x %08x %08x\n", h >> 16, h & 0xffff, v); if ((h >> 16) == 0x10 && v == 0x12345678) break; if (!h && !v) { fprintf(f, "FIN-NULO\n"); break; } }
    fclose(f);
}
static void *gpu_thread(void *a) {
    (void)a; unsigned done = 0; const char *e = getenv("GPUEMU_MS"), *j = getenv("GPUEMU_JOB"); unsigned ms = e ? (unsigned)num(e) : 3, job = j ? (unsigned)num(j) : 0; int n = 0;
    for (;;) {
        usleep(100);
        if (getenv("RINGWATCH") && gw1) {  /* RINGWATCH=1: cada ~2 s, entradas de la tabla de trabajos (ventana +0xe8, 0x8c B) con algún dato; byte 0 = en curso */
            static unsigned tick; if (++tick % 20000 == 0) {
                char b[800]; int o = 0, c = 0; for (unsigned q = 0; q < 0x320 && c < 6 && 0xe8 + (q + 1) * 0x8c <= 0x20000; q++) { volatile unsigned *e = gw1 + (0xe8 + q * 0x8c) / 4; int nz = 0; for (int i = 0; i < 35; i++) if (e[i]) nz = 1; if (nz) { c++; o += snprintf(b + o, sizeof b - o, " [%u: b0=%u w1=%#x w2=%#x w3=%#x w4=%#x w5=%#x w6=%#x]", q, (unsigned)(e[0] & 0xff), e[1], e[2], e[3], e[4], e[5], e[6]); } }
                efp("[shim] RING kicks=%u +4=%#x +c=%#x +10=%#x +14=%#x:%s\n", gpu_kicks, gw1[1], gw1[3], gw1[4], gw1[5], b);
            }
        }
        if (gpu_kicks == done) continue;
        done = gpu_kicks; unsigned v = gw0 ? gw0[0x1804 / 4] : 0;
        gw1[5] = 1; usleep(ms * 1000u); gw1[5] = 2;  /* ocupada → inactiva: grm_init lo necesita en cada trabajo */
        if (!gpu_live) continue;  /* durante el arranque los trabajos no generan aviso de fin: el controlador no lo espera */
        usleep(ms * 1000u);
        unsigned idx = 0xffffffffu;  /* el controlador anota el trabajo en la tabla de la ventana (+0xe8, entradas de 0x8c B, [+0x14] = id) antes de empujar la lista */
        for (unsigned q = 0; q < 0x320 && 0xe8 + (q + 1) * 0x8c <= 0x20000; q++) if (gw1[(0xe8 + q * 0x8c + 0x14) / 4]) { idx = q; break; }
        if (idx == 0xffffffffu && j) idx = job;
        if (idx != 0xffffffffu) { gpu_ack = 0; gw1[4] = 1; gw1[1] = idx; }
        if (n++ < 40) efp("[shim] GPUEMU trabajo %d: lista %#x terminada (+4=%#x)\n", n, v, idx);
        gpu_dumplist(v, n);
        if (idx != 0xffffffffu) { for (int k = 0; k < 2000 && !gpu_ack; k++) usleep(500); gw1[1] = 0xffffffffu; gw1[4] = 0; }
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
        if (r != MAP_FAILED && !strcmp(devname[fd], "/dev/dmpgles2") && l == 0x20000) { ((unsigned *)r)[1] = 0xffffffffu; ((unsigned *)r)[5] = 2; }  /* reg +4 = índice del trabajo terminado (libObj+0x6c61b0); 0xffffffff = ninguno; reg +0x14 = estado de la GPU (el bucle del hilo GL, libObj+0x6c35a0/0x6c66c4, gira hasta que vale 2 = inactiva). A 0 el controlador cree que el trabajo 0 acaba de terminar y gira reteniendo su cerrojo */
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
    return real(c, m);
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
