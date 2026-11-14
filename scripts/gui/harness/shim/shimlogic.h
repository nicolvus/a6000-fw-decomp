/* Lógica pura del shim, probada en el anfitrión (tests/test_shim_logic.py, §5.37).
 * 1) Prioridades RT de la cámara -> anfitrión.
 * El kernel de la cámara (Linux 3.0.27_nl-rt106, cxd90014_set_defconfig) se compila con CONFIG_MAX_USER_RT_PRIO=160: sched_priority válido 1..159, sin traducción
 * en libosal_utm (modo 4 de osal_create_waitable_thread pasa la prioridad tal cual a sched_setscheduler(SCHED_RR); modos 1/2/3/5 = 7/8/9/6). El kernel de Debian del
 * arnés solo admite 1..99, con lo que los hilos de libmpr (117/120/123) fallaban con EINVAL.
 * shortcut: identidad hasta host_max/2 (los hilos bajos conservan su valor) y, por encima, tramo lineal monótono hasta 159 -> host_max (pares vecinos pueden coincidir; con 99
 * los valores medidos 117/120/123 dan 80/81/82);
 * mejorar con un kernel de invitado con CONFIG_MAX_USER_RT_PRIO=160, donde el mapeo es la identidad. */
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
