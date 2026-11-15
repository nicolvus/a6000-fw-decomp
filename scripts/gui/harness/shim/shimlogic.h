/* Lógica pura del shim, probada en el anfitrión (tests/test_shim_logic.py, §5.37).
 * 1) Prioridades RT de la cámara -> anfitrión.
 * El kernel de la cámara (Linux 3.0.27_nl-rt106, cxd90014_set_defconfig) se compila con CONFIG_MAX_USER_RT_PRIO=160: sched_priority válido 1..159, sin traducción
 * en libosal_utm (modo 4 de osal_create_waitable_thread pasa la prioridad tal cual a sched_setscheduler(SCHED_RR); modos 1/2/3/5 = 7/8/9/6). El kernel de Debian del
 * arnés solo admite 1..99, con lo que los hilos de libmpr (117/120/123) fallaban con EINVAL.
 * shortcut: identidad hasta host_max/2 (los hilos bajos conservan su valor) y, por encima, tramo lineal monótono hasta 159 -> host_max (pares vecinos pueden coincidir; con 99
 * los valores medidos 117/120/123 dan 80/81/82);
 * mejorar con un kernel de invitado con CONFIG_MAX_USER_RT_PRIO=160, donde el mapeo es la identidad. */
#include <string.h>
#define CAM_RT_PRIO_MAX 159
static inline int rtprio_map(int p, int host_max) {
    int k = host_max / 2;
    if (p <= k || host_max >= CAM_RT_PRIO_MAX) return p;
    if (p > CAM_RT_PRIO_MAX) p = CAM_RT_PRIO_MAX;
    return k + (p - k) * (host_max - k) / (CAM_RT_PRIO_MAX - k);
}

/* 2) Contexto que recibe el callback de osal_reg_msg_queue_cb(qid, &asa, cb, ctx): ruta u_ = t {r1, cb, r3, 0}. Si t[0] cae dentro del objeto t[2]
 * (0 < t[0]-t[2] < 0x400; UpmWrapper registra this+0x2c con this) el contexto es t[2], no t[0]. shortcut: heurística por forma, no por la API del kernel;
 * mejorar si un registro con t[0] dentro de t[2] espera de verdad &miembro. */
static inline int reg_ctx_is_t2(const unsigned *t) { return t[2] && t[0] > t[2] && t[0] - t[2] < 0x400; }

/* 3) ioctl 0x104 de /dev/mmca (SD emulada, §5.39): libInfraMediaCommon+0xeac0 copia a[2..0x14) (0x48 B) y +0x10702 saca de ellos el nº de sectores como `a[0x24/4] + 1`
 * (último LBA + 1), que libInfraFsys (PDM) usa como tamaño de la partición: con 0 el PDM veía 1 sector y rechazaba toda lectura de FAT (pdm_part_logical_read -> 0x12).
 * a[0x38/4] (+0x10: out[0x30], cuyo uso es un resto de división con alineación) se deja en `tot` como estaba: shortcut: sin dato verificado del valor real (¿4 MiB de AU?),
 * mejorar cuando se mida en una cámara. */
static inline void sd_partinfo_fill(unsigned *a, unsigned tot) { memset(a, 0, 0x50); a[0x24 / 4] = tot - 1; a[0x38 / 4] = tot; }

/* 4) ioctl 5 de /dev/mmca-char (info de la tarjeta, §5.40): libInfraMediaCommon+0x1024a hace ioctl(fd, 5, ctx+0x24), así que a[k] cae en ctx+0x24+k. Medido en el código: byte 0 = tipo (3 = SD,
 * test en +0x10668/+0x10752), a[0x20] = último LBA (ctx+0x44, "max_lba"), a[0x24..0x2c] = capacidad u64 en bytes (ctx+0x48, "card_capacity"), a[0x2c] = erase_unit en sectores (ctx+0x50),
 * a[0x34] = tamaño de sector. shortcut: erase_unit 8192 sectores (4 MiB, AU típica de SDHC 4 GB) sin dato real de cámara; mejorar al medirlo. */
static inline void sd_cardinfo_fill(unsigned *a, unsigned tot) {
    unsigned long long by = (unsigned long long)tot * 512;
    memset(a, 0, 0xc0); ((unsigned char *)a)[0] = 3; a[0x20 / 4] = tot - 1; a[0x2c / 4] = 8192; a[0x34 / 4] = 512; a[0x24 / 4] = (unsigned)by; a[0x28 / 4] = (unsigned)(by >> 32);
}
/* libInfraMediaCommon+0x10776..0x107a2: capacidad (hi:lo) >= 0x800000001 -> 0x8202 (SDXC); > 0x80000000 -> 0x8201 (SDHC); si no 0x8200 (SDSC). */
static inline unsigned sd_media_class(unsigned lo, unsigned hi) {
    unsigned long long c = ((unsigned long long)hi << 32) | lo;
    return c >= 0x800000001ULL ? 0x8202 : c > 0x80000000ULL ? 0x8201 : 0x8200;
}
/* libInfraFsys+0x24d14 (solo las clases SD): 0x8200 -> 0x8400, 0x8201 -> 0x8401, 0x8202 -> 0x8402 (§5.39). */
static inline unsigned sd_fsys_class(unsigned c) { return 0x8400 + (c - 0x8200); }

/* §5.42: colas síncronas cuyo callback se está ejecutando en este hilo (el shim entrega el callback en el hilo emisor). Un envío a una cola que ya está en curso no se entrega otra vez:
 * libObj+0x7ddd88 (callback de 0x924126) vuelve a enviar a 0x924126 y la recursión agotaba la pila. shortcut: tope de 8 colas anidadas distintas; las demás se entregan sin guardar. */
typedef struct { unsigned q[8]; int n; } sync_nest;
static inline int sync_nest_enter(sync_nest *s, unsigned qid) {
    for (int i = 0; i < s->n; i++) if (s->q[i] == qid) return 0;
    if (s->n < 8) s->q[s->n++] = qid;
    return 1;
}
static inline void sync_nest_leave(sync_nest *s, unsigned qid) { if (s->n && s->q[s->n - 1] == qid) s->n--; }

/* §5.43: /dev/nflasha4 = partición «MPR» (0x3140000, 10 MiB) que libmpr usa como DFB (DVD Flash Backup: FlashLib/DFA). DFA::GetDeviceInfo (libmpr+0x2a40c0) hace ioctl(fd, 0x6e07, &b) con b = {?, lblk_size,
 * num_of_lblks, ltu_size} (solo los registra), y lee el inicio de la partición (sectores de 512 B) de /sys/block/nflasha0/nflasha0p4/start; el tamaño sale de lseek(SEEK_END) y los bloques son de 0x20000 B
 * (dirección = bloque * 0x20000 + desplazamiento; paso medido entre cabeceras del volcado). shortcut: lblk_size 0x20000 y ltu_size 0x200 son los valores previos de libmpr/el paso del volcado, no medidos en el ioctl
 * real de la cámara; mejorar si un volcado del driver los da. */
#include <stdio.h>
static inline void nflash_lblkinfo_fill(unsigned *a, unsigned nbytes) { memset(a, 0, 0x10); a[1] = 0x20000; a[2] = nbytes / 0x20000; a[3] = 0x200; }
static inline void nflash_start_text(char *s, unsigned n) { snprintf(s, n, "%u\n", 0x3140000u / 512); }
