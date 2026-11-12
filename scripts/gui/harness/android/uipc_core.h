/* SPDX-License-Identifier: GPL-2.0 */
/* Núcleo sin dependencias de /dev/uipc compartido entre procesos (G22-E T5b/T6, ver docs/gui/g22-osal-uipc-spec.md).
 * ADICIÓN DEL EMULADOR, no código de Sony: replica la semántica medida de osal_uipc.ko (kernel 3.0.27) que hace falta entre procesos
 * (memoria compartida de 0x80000 B, colas, semáforos, callbacks de usuario, ids dinámicos). No bloquea: devuelve UC_AGAIN y el
 * envoltorio (módulo de kernel) duerme y reintenta. Compila igual en el kernel y en el anfitrión (prueba: uipc_core_test.c). */
#ifndef UIPC_CORE_H
#define UIPC_CORE_H
#ifdef __KERNEL__
#include <linux/types.h>
#else
#include <stdint.h>
#endif

#define UC_SHM      0x80000u   /* __k_uipc_cdev_mmap exige exactamente este tamaño */
#define UC_HDR      12u        /* cabecera verificada en osal_uipc.ko (0x2d4c–0x2e1c, osal_msg_size 0x475c): [0] enlace, [4] nº de bloques de 32 B,
                                  [5] banderas (bits 0–5 = 1; bit 6 = cabecera extendida +24), [6] u16 = 1, [8] 0xa5a5a5a5; cuerpo en +12 */
#define UC_BLK      32u
#define UC_NBLK     (UC_SHM / UC_BLK)
#define UC_MAXMSG   (255 * UC_BLK - UC_HDR)   /* el nº de bloques es un byte: 8148 B */
#define UC_NQ       256
#define UC_NSEM     256
#define UC_DEPTH    64
#define UC_NPROC    32
#define UC_AGAIN    (-11)
#define UC_INVAL    (-22)
#define UC_NOMEM    (-12)
#define UC_DYN_Q    0x2a       /* tipos de osal_dynamic_id */
#define UC_DYN_SEM  0x32

struct uc_cb { uint32_t cb, arg, msg, pad; };          /* salida de wait_cb (idx 13): el proxy llama cb(msg, arg) */
struct uc_q {
	uint32_t id; int owner;                             /* owner = proceso con callback registrado, -1 = buzón */
	uint32_t cb, arg; int sync;
	uint32_t fifo[UC_DEPTH]; unsigned r, w;             /* desplazamientos de cuerpo dentro de la memoria compartida */
};
struct uc_proc { int used; uint32_t base; struct uc_cb dlv[UC_DEPTH]; unsigned r, w; };
struct uc_sem { uint32_t id; int count; };
struct uc {
	uint8_t *shm;                                       /* UC_SHM bytes, mapeados en todos los procesos */
	uint8_t used[UC_NBLK / 8];                          /* mapa de bloques de 32 B */
	struct uc_q q[UC_NQ]; struct uc_sem s[UC_NSEM]; struct uc_proc p[UC_NPROC];
	uint32_t next_dyn;
};

void uc_init(struct uc *u, uint8_t *shm);
int  uc_connect(struct uc *u, uint32_t user_base, uint32_t out[4]);   /* idx 0x10; devuelve nº de proceso */
void uc_disconnect(struct uc *u, int pid);                            /* cierre del descriptor */
int  uc_valloc(struct uc *u, int pid, uint32_t src_q, uint32_t size, uint32_t *user_ptr); /* idx 0xa */
int  uc_free(struct uc *u, int pid, uint32_t user_ptr);                /* idx 0xb */
int  uc_snd(struct uc *u, int pid, uint32_t qid, uint32_t user_ptr);   /* idx 4 */
int  uc_rcv(struct uc *u, int pid, uint32_t qid, uint32_t *user_ptr);  /* idx 7 (sin espera) */
int  uc_reg_cb(struct uc *u, int pid, uint32_t qid, uint32_t arg, uint32_t cb, int sync); /* idx 8 */
int  uc_unreg_cb(struct uc *u, uint32_t qid);                          /* idx 9 */
int  uc_wait_cb(struct uc *u, int pid, struct uc_cb *out);             /* idx 0xd (sin espera) */
int  uc_dynamic_id(struct uc *u, uint32_t type, uint32_t group, uint32_t *id); /* idx 0xc */
int  uc_sig_sem(struct uc *u, uint32_t id);                            /* idx 2 */
int  uc_wai_sem(struct uc *u, uint32_t id);                            /* idx 1 (sin espera) */
#endif
