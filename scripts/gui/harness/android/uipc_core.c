// SPDX-License-Identifier: GPL-2.0
// Núcleo de /dev/uipc compartido (ver uipc_core.h). Sin locks: el envoltorio serializa con un mutex global, como osal_lock en el .ko.
#include "uipc_core.h"
#ifdef __KERNEL__
#include <linux/string.h>
#else
#include <string.h>
#endif

void uc_init(struct uc *u, uint8_t *shm)
{
	memset(u, 0, sizeof(*u));
	u->shm = shm; u->next_dyn = 1;
	memset(u->used, 0xff, 0x1000 / UC_BLK / 8);        /* la primera página queda para la cabecera global (connect: [0x10] = nº de proxies) */
	shm[0x10] = 8;
}

/* user -> desplazamiento (misma comprobación que la rutina 0x1ae0 del .ko: ptr - base < 0x80000) */
static int u2o(struct uc *u, int pid, uint32_t p, uint32_t *off)
{
	uint32_t o = p - u->p[pid].base;
	if (pid < 0 || pid >= UC_NPROC || !u->p[pid].used || o >= UC_SHM) return UC_INVAL;
	*off = o; return 0;
}

int uc_connect(struct uc *u, uint32_t user_base, uint32_t out[4])
{
	for (int i = 0; i < UC_NPROC; i++) if (!u->p[i].used) {
		memset(&u->p[i], 0, sizeof(u->p[i])); u->p[i].used = 1; u->p[i].base = user_base;
		out[0] = UC_SHM; out[1] = 0x20000; out[2] = 0x8000;
		uc_dynamic_id(u, UC_DYN_Q, 0x3f, &out[3]);      /* __k_4u_connect: osal_dynamic_id(42, 63, &out[3]) */
		return i;
	}
	return UC_NOMEM;
}

void uc_disconnect(struct uc *u, int pid)
{
	if (pid < 0 || pid >= UC_NPROC) return;
	for (int i = 0; i < UC_NQ; i++) if (u->q[i].owner == pid) u->q[i].owner = -1;
	u->p[pid].used = 0;
}

static struct uc_q *qget(struct uc *u, uint32_t id, int make)
{
	struct uc_q *f = 0;
	for (int i = 0; i < UC_NQ; i++) { if (u->q[i].id == id) return &u->q[i]; if (!f && !u->q[i].id) f = &u->q[i]; }
	if (make && f) { memset(f, 0, sizeof(*f)); f->id = id; f->owner = -1; }
	return make ? f : 0;
}

#define UC_USED(o) (u->used[(o) / UC_BLK / 8] & (1u << ((o) / UC_BLK % 8)))
static void mark(struct uc *u, uint32_t o, unsigned n, int on)
{
	for (; n--; o += UC_BLK) { uint8_t *b = &u->used[o / UC_BLK / 8], m = 1u << (o / UC_BLK % 8); *b = on ? *b | m : *b & ~m; }
}

/* Bloques de 32 B contiguos (primer hueco), como vpool del .ko: n = ceil((size + 12) / 32). La cabecera reproduce la de 0x2d4c–0x2e1c
 * salvo que [4] nunca vale 0 (el .ko usa fblock con [4] = 0 para cuerpos ≤ 20 B; osal_msg_size da 20 en ambos casos). */
int uc_valloc(struct uc *u, int pid, uint32_t src_q, uint32_t size, uint32_t *user_ptr)
{
	unsigned n = (size + UC_HDR + UC_BLK - 1) / UC_BLK, run = 0;
	uint32_t o, a = 0, mk = 0xa5a5a5a5u;
	(void)src_q;
	if (pid < 0 || pid >= UC_NPROC || !u->p[pid].used || size > UC_MAXMSG) return UC_INVAL;
	for (o = 0; o < UC_SHM && run < n; o += UC_BLK) { if (UC_USED(o)) run = 0; else if (!run++) a = o; }
	if (run < n) return UC_NOMEM;
	mark(u, a, n, 1);
	memset(u->shm + a, 0, n * UC_BLK);
	u->shm[a + 4] = (uint8_t)n; u->shm[a + 5] = 1; u->shm[a + 6] = 1;
	memcpy(u->shm + a + 8, &mk, 4);
	*user_ptr = u->p[pid].base + a + UC_HDR; return 0;
}

int uc_free(struct uc *u, int pid, uint32_t user_ptr)
{
	uint32_t o; int r = u2o(u, pid, user_ptr, &o);
	if (r) return r;
	o -= UC_HDR;
	if (o % UC_BLK || o < 0x1000 || !UC_USED(o) || !u->shm[o + 4] || o + u->shm[o + 4] * UC_BLK > UC_SHM) return UC_INVAL;
	mark(u, o, u->shm[o + 4], 0); return 0;
}

int uc_snd(struct uc *u, int pid, uint32_t qid, uint32_t user_ptr)
{
	uint32_t o; int r = u2o(u, pid, user_ptr, &o);
	struct uc_q *q;
	if (r) return r;
	q = qget(u, qid, 1);
	if (!q) return UC_NOMEM;
	if (q->owner >= 0) {                                /* cola con callback: entrega al proxy del proceso dueño, con su propia base */
		struct uc_proc *p = &u->p[q->owner];
		if (p->w - p->r >= UC_DEPTH) return UC_AGAIN;
		p->dlv[p->w++ % UC_DEPTH] = (struct uc_cb){ q->cb, q->arg, p->base + o, 0 };
		return 0;
	}
	if (q->w - q->r >= UC_DEPTH) return UC_AGAIN;
	q->fifo[q->w++ % UC_DEPTH] = o; return 0;
}

int uc_rcv(struct uc *u, int pid, uint32_t qid, uint32_t *user_ptr)
{
	struct uc_q *q = qget(u, qid, 0);
	if (pid < 0 || pid >= UC_NPROC || !u->p[pid].used) return UC_INVAL;
	if (!q || q->r == q->w) return UC_AGAIN;
	*user_ptr = u->p[pid].base + q->fifo[q->r++ % UC_DEPTH]; return 0;
}

int uc_reg_cb(struct uc *u, int pid, uint32_t qid, uint32_t arg, uint32_t cb, int sync)
{
	struct uc_q *q = qget(u, qid, 1);
	if (!q || pid < 0 || pid >= UC_NPROC || !u->p[pid].used) return q ? UC_INVAL : UC_NOMEM;
	q->owner = pid; q->cb = cb; q->arg = arg; q->sync = sync;
	while (q->r != q->w) {                              /* lo encolado antes del registro se entrega ahora */
		uint32_t o = q->fifo[q->r++ % UC_DEPTH]; struct uc_proc *p = &u->p[pid];
		p->dlv[p->w++ % UC_DEPTH] = (struct uc_cb){ cb, arg, p->base + o, 0 };
	}
	return 0;
}

int uc_unreg_cb(struct uc *u, uint32_t qid)
{
	struct uc_q *q = qget(u, qid, 0);
	if (!q) return UC_INVAL;
	q->owner = -1; return 0;
}

int uc_wait_cb(struct uc *u, int pid, struct uc_cb *out)
{
	struct uc_proc *p;
	if (pid < 0 || pid >= UC_NPROC || !u->p[pid].used) return UC_INVAL;
	p = &u->p[pid];
	if (p->r == p->w) return UC_AGAIN;
	*out = p->dlv[p->r++ % UC_DEPTH]; return 0;
}

/* NO_VERIFICADO: numeración real de osal_dynamic_id; se usa grupo<<16 | 0x8000 | n (el .ko trata aparte los índices con bit 0x8000) */
int uc_dynamic_id(struct uc *u, uint32_t type, uint32_t group, uint32_t *id)
{
	if (type != UC_DYN_Q && type != UC_DYN_SEM) return UC_INVAL;
	if (u->next_dyn >= 0x800) return UC_NOMEM;          /* osal_valloc_msg_wait rechaza índices ≥ 0x800 */
	*id = (group << 16) | 0x8000 | u->next_dyn++;
	return 0;
}

static struct uc_sem *sget(struct uc *u, uint32_t id)
{
	struct uc_sem *f = 0;
	for (int i = 0; i < UC_NSEM; i++) { if (u->s[i].id == id) return &u->s[i]; if (!f && !u->s[i].id) f = &u->s[i]; }
	if (f) { f->id = id; f->count = 0; }
	return f;
}

int uc_sig_sem(struct uc *u, uint32_t id) { struct uc_sem *s = sget(u, id); if (!s) return UC_NOMEM; s->count++; return 0; }

int uc_wai_sem(struct uc *u, uint32_t id)
{
	struct uc_sem *s = sget(u, id);
	if (!s) return UC_NOMEM;
	if (!s->count) return UC_AGAIN;
	s->count--; return 0;
}
