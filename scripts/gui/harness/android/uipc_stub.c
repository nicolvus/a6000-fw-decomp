// SPDX-License-Identifier: GPL-2.0
// ADICIÓN DEL EMULADOR (T6), no es el osal_uipc.ko de la cámara: /dev/uipc mínimo para que los procesos Android 2.3 (libosal_uipc.so, cargada por
// libhardware_legacy) puedan abrirlo. Solo replica lo que el shim del arnés ya modela de u_uipc_init (libosal_uipc.so, do_init en 0x6180):
//   ioctl 0x80000010 {0, &o[4]} -> o = {0x80000, 0x20000, 0x8000, 0}; mmap compartido de 0x80000 B con [0x10] = 8.
// Cualquier otro ioctl devuelve 0 sin hacer nada (colas/semáforos NO modelados entre procesos: NO_VERIFICADO el protocolo real).
#include <linux/module.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/mm.h>
#include <linux/vmalloc.h>
#include <linux/uaccess.h>

#define UIPC_SIZE 0x80000
static void *shm;

static long uipc_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
	u32 o[4] = { UIPC_SIZE, 0x20000, 0x8000, 0 };
	unsigned long out;

	if (cmd != 0x80000010)
		return 0;
	if (get_user(out, (unsigned long __user *)(arg + 4)) || copy_to_user((void __user *)out, o, sizeof(o)))
		return -EFAULT;
	return 0;
}

static int uipc_mmap(struct file *f, struct vm_area_struct *vma)
{
	return remap_vmalloc_range(vma, shm, 0);
}

static const struct file_operations uipc_fops = {
	.owner = THIS_MODULE, .unlocked_ioctl = uipc_ioctl, .mmap = uipc_mmap,
};
static struct miscdevice uipc_dev = { MISC_DYNAMIC_MINOR, "uipc", &uipc_fops, .mode = 0666 };

static int __init uipc_init(void)
{
	shm = vmalloc_user(UIPC_SIZE);
	if (!shm)
		return -ENOMEM;
	*(u32 *)(shm + 0x10) = 8;	/* nº de hilos proxy que arranca u_osal_reg_msg_queue_cb (mismo valor que el shim) */
	return misc_register(&uipc_dev);
}
static void __exit uipc_exit(void) { misc_deregister(&uipc_dev); vfree(shm); }
module_init(uipc_init);
module_exit(uipc_exit);
MODULE_LICENSE("GPL");
