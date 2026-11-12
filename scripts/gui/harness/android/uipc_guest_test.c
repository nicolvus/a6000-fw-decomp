// Prueba en el invitado de uipc_shared.ko (sin libc: ARM EABI, syscalls directas). La compila build_uipc.sh; la lanza prueba_uipc.sh.
// Dos procesos (fork) con su propio descriptor y mmap: el hijo registra una cola con callback y espera con wait_cb; el padre envía un
// mensaje de 5000 B (> 4 KiB). Después: rcv con tiempo agotado (E_TMOUT) y semáforo entre procesos. Imprime «UIPC OK» o «FALLO n».
typedef unsigned u32;
static long sc(long n, long a, long b, long c, long d, long e, long f)
{
	register long r7 __asm__("r7") = n, r0 __asm__("r0") = a, r1 __asm__("r1") = b, r2 __asm__("r2") = c,
		r3 __asm__("r3") = d, r4 __asm__("r4") = e, r5 __asm__("r5") = f;
	__asm__ volatile("svc 0" : "+r"(r0) : "r"(r7), "r"(r1), "r"(r2), "r"(r3), "r"(r4), "r"(r5) : "memory");
	return r0;
}
#define WR(s) sc(4, 1, (long)(s), sizeof(s) - 1, 0, 0, 0)
static void die(int n) { char m[] = "FALLO 00\n"; m[6] = '0' + n / 10; m[7] = '0' + n % 10; WR(m); sc(1, 1, 0, 0, 0, 0, 0); }
static long io(int fd, u32 idx, u32 w0, u32 w1) { u32 w[2] = { w0, w1 }; return sc(54, fd, 0x80000000u | idx, (long)w, 0, 0, 0); }
static unsigned char *conn(int *fd)
{
	u32 o[4] = { 0 };
	*fd = sc(5, (long)"/dev/uipc", 2, 0, 0, 0, 0);
	if (*fd < 0) die(1);
	if (io(*fd, 0x10, 0, (u32)o) || o[0] != 0x80000 || (o[3] >> 16) != 0x3f) die(2);
	long p = sc(192, 0, 0x80000, 3, 1, *fd, 0);   /* mmap2(PROT_RW, MAP_SHARED) */
	if (p < 0 && p > -4096) die(3);
	return (unsigned char *)p;
}

void _start(void)
{
	int fd, st = 0; unsigned char *b;
	enum { Q = 0x3e014d, SEM = 0x120001 };
	long pid = sc(2, 0, 0, 0, 0, 0, 0);            /* fork antes de abrir: cada proceso abre el suyo */
	b = conn(&fd);
	if (pid == 0) {
		u32 reg[4] = { 0x1111, 0x2223, 0, 0 }, out[4];
		if (io(fd, 8, Q, (u32)reg)) die(4);
		if (io(fd, 2, SEM, 0)) die(5);         /* avisa al padre de que ya está registrado */
		if (io(fd, 0xd, 0, (u32)out) || out[0] != 0x2223 || out[1] != 0x1111) die(6);
		unsigned char *m = (unsigned char *)out[2];
		if (m < b || m >= b + 0x80000 || m[0] != 0x5a || m[4999] != 0xa5 || m[-8] != (5000 + 12 + 31) / 32) die(7);
		if (io(fd, 0xb, Q, out[2])) die(8);
		sc(1, 0, 0, 0, 0, 0, 0);
	}
	if (io(fd, 1, SEM, 5000)) die(9);              /* espera real con tiempo máximo de 5 s */
	u32 m = 0, a[3] = { (u32)&m, 5000, 0 };
	if (io(fd, 0xa, Q, (u32)a) || (unsigned char *)m < b) die(10);
	((unsigned char *)m)[0] = 0x5a; ((unsigned char *)m)[4999] = 0xa5;
	if (io(fd, 4, Q, m)) die(11);
	sc(114, pid, (long)&st, 0, 0, 0, 0);           /* wait4 */
	if (st) die(12);
	u32 r[2] = { (u32)&m, 100 };
	if (io(fd, 7, 0x7f0001, (u32)r) != -1022) die(13);
	WR("UIPC OK\n");
	sc(1, 0, 0, 0, 0, 0, 0);
}
