// SPDX-License-Identifier: GPL-2.0
// ADICIÓN DEL EMULADOR (G22-E T5b/T6), no es el osal_uipc.ko de Sony: /dev/uipc compartido entre procesos sobre uipc_core.c.
// Interfaz según docs/gui/g22-osal-uipc-spec.md: ioctl(fd, idx [| 0x80000000], &{w0, w1}), mmap de 0x80000 B común a todos los procesos.
// Las esperas usan una sola cola de espera global (wake_up_all en cada cambio): simple; suficiente para decenas de hilos.
#include <linux/module.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/fs.h>
#include <linux/mm.h>
#include <linux/sched.h>
#include <linux/slab.h>
#include <linux/vmalloc.h>
#include <linux/uaccess.h>
#include <linux/wait.h>
#include <linux/mutex.h>
#include "uipc_core.h"

#define E_TMOUT (-1022)   /* código de tiempo agotado que ve libosal_uipc (mismo valor que el shim) */
#define NSYNC 64

static struct uc *U;
static DEFINE_MUTEX(M);
static DECLARE_WAIT_QUEUE_HEAD(WQ);
static struct { uint32_t off; int done; } pend[NSYNC];   /* snd_sync entre procesos: el emisor espera a que el dueño cierre */

static unsigned gen;   /* sube en cada cambio de estado; las esperas despiertan cuando cambia */
static void wake(void) { mutex_lock(&M); gen++; mutex_unlock(&M); wake_up_all(&WQ); }

struct fctx { int pid; pid_t tgid; uint32_t conn[4]; };

/* Espera hasta que op() deje de devolver UC_AGAIN; tmo en ms (<0 infinito, 0 sondeo). */
#define WAIT_OP(tmo, expr) ({ \
	long _t = (int)(tmo) < 0 ? MAX_SCHEDULE_TIMEOUT : msecs_to_jiffies(tmo); int _r; \
	for (;;) { unsigned _g; mutex_lock(&M); _g = gen; _r = (expr); mutex_unlock(&M); \
		if (_r != UC_AGAIN) break; \
		if (!_t) { _r = E_TMOUT; break; } \
		_t = wait_event_interruptible_timeout(WQ, READ_ONCE(gen) != _g, _t); \
		if (_t < 0) { _r = -1021; break; } } _r; })  /* señal: libosal_uipc reintenta el ioctl con −1021 (u_osal_reg_msg_queue_cb 0x58f4) */

static int sync_slot(uint32_t off)
{
	for (int i = 0; i < NSYNC; i++) if (!pend[i].off) { pend[i].off = off; pend[i].done = 0; return i; }
	return -1;
}

static int sync_done(int k) { if (!pend[k].done) return UC_AGAIN; pend[k].off = 0; return 0; }

/* entrega síncrona a otro proceso: encola al dueño y espera el cierre (2.ª llamada snd_sync_msg con cb != 0) */
static int sync_send(struct fctx *c, uint32_t qid, uint32_t uptr)
{
	uint32_t off = uptr - U->p[c->pid].base; int k, r;
	mutex_lock(&M);
	k = sync_slot(off);
	r = k < 0 ? UC_NOMEM : uc_snd(U, c->pid, qid, uptr);
	if (r && k >= 0) pend[k].off = 0;
	mutex_unlock(&M);
	if (r) return r;
	wake();
	return WAIT_OP(-1, sync_done(k));
}

static int valloc_try(int pid, u32 q, u32 size, u32 *out)
{
	int r = uc_valloc(U, pid, q, size, out);
	return r == UC_NOMEM ? UC_AGAIN : r;
}

static int owner_of(uint32_t qid)
{
	for (int i = 0; i < UC_NQ; i++) if (U->q[i].id == qid) return U->q[i].owner;
	return -1;
}

static long uipc_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
	struct fctx *c = f->private_data; u32 w[2], t[4] = { 0 }, out; unsigned idx = cmd & 0x7fffffff; int r = 0;
	void __user *p1;
	if (copy_from_user(w, (void __user *)arg, 8)) return -EFAULT;
	if (idx > 16) return -EINVAL;
	if (c->tgid != current->tgid) { pr_err("uipc: called from different process\n"); return -EINVAL; }
	p1 = (void __user *)(unsigned long)w[1];
	switch (idx) {
	case 0: mutex_lock(&M); t[0] = 0; mutex_unlock(&M); return copy_to_user(p1, t, 12) ? -EFAULT : 0;  /* NO_VERIFICADO: formato stat_sem */
	case 3: return copy_to_user(p1, t, 16) ? -EFAULT : 0;                                               /* NO_VERIFICADO: formato stat_msgq */
	case 1: return WAIT_OP(w[1], uc_wai_sem(U, w[0]));
	case 2: mutex_lock(&M); r = uc_sig_sem(U, w[0]); mutex_unlock(&M); wake(); return r;
	case 4: r = WAIT_OP(-1, uc_snd(U, c->pid, w[0], w[1])); wake(); return r;
	case 5: {                                                   /* {msg, cb, arg} */
		int ow, k;
		if (copy_from_user(t, p1, 12)) return -EFAULT;
		mutex_lock(&M);
		if (t[1]) {                                             /* cierre de una entrega síncrona */
			uint32_t off = t[0] - U->p[c->pid].base;
			for (k = 0; k < NSYNC; k++) if (pend[k].off == off) pend[k].done = 1;
			gen++; mutex_unlock(&M); wake_up_all(&WQ); return 0;
		}
		ow = owner_of(w[0]);
		if (ow == c->pid) {                                     /* mismo proceso: devuelve cb/arg y el emisor llama directo (como el shim) */
			for (k = 0; k < UC_NQ; k++) if (U->q[k].id == w[0]) { t[1] = U->q[k].cb; t[2] = U->q[k].arg; }
			mutex_unlock(&M);
			return copy_to_user(p1, t, 12) ? -EFAULT : 0;
		}
		mutex_unlock(&M);
		if (ow < 0) return E_TMOUT;                              /* nadie atiende: NO_VERIFICADO el código real */
		return sync_send(c, w[0], t[0]);
	}
	case 6: {                                                   /* snd_sync_direct: 16 B copiados a un bloque compartido */
		u32 m;
		if (copy_from_user(t, p1, 16)) return -EFAULT;
		mutex_lock(&M); r = uc_valloc(U, c->pid, 0, 16, &m); if (!r) memcpy(U->shm + (m - U->p[c->pid].base), t, 16); mutex_unlock(&M);
		if (r) return r;
		r = owner_of(w[0]) < 0 ? E_TMOUT : sync_send(c, w[0], m);
		mutex_lock(&M); memcpy(t, U->shm + (m - U->p[c->pid].base), 16); uc_free(U, c->pid, m); mutex_unlock(&M);
		return r ? r : copy_to_user(p1, t, 16) ? -EFAULT : 0;
	}
	case 7:                                                     /* {&out, tmo} */
		if (copy_from_user(t, p1, 8)) return -EFAULT;
		r = WAIT_OP(t[1], uc_rcv(U, c->pid, w[0], &out));
		return r ? r : put_user(out, (u32 __user *)(unsigned long)t[0]);
	case 8:                                                     /* {arg, cb, prio, sync} */
		if (copy_from_user(t, p1, 16)) return -EFAULT;
		mutex_lock(&M); r = uc_reg_cb(U, c->pid, w[0], t[3] == 1 ? t[2] : t[0], t[1], t[3] == 1); mutex_unlock(&M);
		wake(); return r;
	case 9: mutex_lock(&M); r = uc_unreg_cb(U, w[0]); mutex_unlock(&M); return r;
	case 0xa:                                                   /* {&out, size, tmo} */
		if (copy_from_user(t, p1, 12)) return -EFAULT;
		r = WAIT_OP(t[2], valloc_try(c->pid, w[0], t[1], &out));
		return r ? r : put_user(out, (u32 __user *)(unsigned long)t[0]);
	case 0xb: mutex_lock(&M); r = uc_free(U, c->pid, w[1]); mutex_unlock(&M); wake(); return r;
	case 0xc:                                                   /* {tipo, grupo, &id} */
		if (copy_from_user(t, p1, 12)) return -EFAULT;
		mutex_lock(&M); r = uc_dynamic_id(U, t[0], t[1], &out); mutex_unlock(&M);
		return r ? r : put_user(out, (u32 __user *)(unsigned long)t[2]);
	case 0xd: {                                                 /* out[4] = {cb, arg, msg, 0} */
		struct uc_cb cb;
		r = WAIT_OP(-1, uc_wait_cb(U, c->pid, &cb));
		return r ? r : copy_to_user(p1, &cb, 16) ? -EFAULT : 0;
	}
	case 0xe: case 0xf: return 0;                               /* modos broadcast/log: sin efecto (NO_VERIFICADO) */
	case 0x10: return copy_to_user(p1, c->conn, 16) ? -EFAULT : 0;
	}
	return -EINVAL;
}

static int uipc_mmap(struct file *f, struct vm_area_struct *vma)
{
	struct fctx *c = f->private_data; int r;
	if (vma->vm_end - vma->vm_start != UC_SHM) return -EINVAL;
	r = remap_vmalloc_range(vma, U->shm, 0);
	if (!r) { mutex_lock(&M); U->p[c->pid].base = vma->vm_start; mutex_unlock(&M); }
	return r;
}

static int uipc_open(struct inode *i, struct file *f)
{
	struct fctx *c = kzalloc(sizeof(*c), GFP_KERNEL);
	if (!c) return -ENOMEM;
	mutex_lock(&M); c->pid = uc_connect(U, 0, c->conn); mutex_unlock(&M);   /* la base llega con el mmap */
	if (c->pid < 0) { kfree(c); return -EMFILE; }
	c->tgid = current->tgid; f->private_data = c;
	return 0;
}

static int uipc_release(struct inode *i, struct file *f)
{
	struct fctx *c = f->private_data;
	mutex_lock(&M); uc_disconnect(U, c->pid); mutex_unlock(&M);
	kfree(c); return 0;
}

static const struct file_operations fops = {
	.owner = THIS_MODULE, .open = uipc_open, .release = uipc_release, .unlocked_ioctl = uipc_ioctl, .mmap = uipc_mmap,
};
/* c 251,207 como el osal_uipc.ko real: el /init de Sony crea /dev/uipc con ese número fijo (medido 13-11-2026) */
#define UIPC_DEV MKDEV(251, 207)
static struct cdev cd;
static struct class *cls;
static char *uipc_devnode(const struct device *d, umode_t *mode) { if (mode) *mode = 0666; return NULL; }

static int __init uipc_init(void)
{
	void *shm = vmalloc_user(UC_SHM); int r;
	U = vzalloc(sizeof(*U));
	if (!U || !shm) { vfree(U); vfree(shm); return -ENOMEM; }
	uc_init(U, shm);
	r = register_chrdev_region(UIPC_DEV, 1, "uipc");
	if (r) goto e_mem;
	cdev_init(&cd, &fops); r = cdev_add(&cd, UIPC_DEV, 1);
	if (r) goto e_reg;
	cls = class_create("uipc");
	if (IS_ERR(cls)) { r = PTR_ERR(cls); goto e_cdev; }
	cls->devnode = uipc_devnode;
	if (IS_ERR(device_create(cls, NULL, UIPC_DEV, NULL, "uipc"))) { r = -ENODEV; goto e_cls; }
	return 0;
e_cls: class_destroy(cls);
e_cdev: cdev_del(&cd);
e_reg: unregister_chrdev_region(UIPC_DEV, 1);
e_mem: vfree(U->shm); vfree(U); return r;
}
static void __exit uipc_exit(void) { device_destroy(cls, UIPC_DEV); class_destroy(cls); cdev_del(&cd); unregister_chrdev_region(UIPC_DEV, 1); vfree(U->shm); vfree(U); }
module_init(uipc_init);
module_exit(uipc_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("osal_uipc compartido entre procesos (emulador A6000, no Sony)");
