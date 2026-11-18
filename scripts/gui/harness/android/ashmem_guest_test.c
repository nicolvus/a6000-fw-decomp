// T6 (invitado, emulador): prueba de ashmem.ko como lo usa el Dalvik de 2.3 (dvmAllocRegion: ashmem_create_region + mmap MAP_PRIVATE).
// Sin libc, ARM EABI. Imprime «ASHMEM <caso> errno=<n>» por caso y «ASHMEM OK» si todos pasan.
typedef unsigned u32;
static long sc(long n, long a, long b, long c, long d, long e, long f)
{
	register long r7 __asm__("r7") = n, r0 __asm__("r0") = a, r1 __asm__("r1") = b, r2 __asm__("r2") = c,
		r3 __asm__("r3") = d, r4 __asm__("r4") = e, r5 __asm__("r5") = f;
	__asm__ volatile("svc 0" : "+r"(r0) : "r"(r7), "r"(r1), "r"(r2), "r"(r3), "r"(r4), "r"(r5) : "memory");
	return r0;
}
static void out(const char *s, long v)
{
	char b[64]; int n = 0; unsigned long u = v < 0 ? -v : v; char t[12]; int k = 0;
	while (*s) b[n++] = *s++;
	b[n++] = ' '; b[n++] = 'e'; b[n++] = '='; if (v < 0) b[n++] = '-';
	do t[k++] = '0' + u % 10; while (u /= 10);
	while (k) b[n++] = t[--k];
	b[n++] = '\n'; sc(4, 1, (long)b, n, 0, 0, 0);
}
/* región como dvmAllocRegion: devuelve dirección o -errno */
static long region(u32 size, int flags, const char *name)
{
	static char nm[256]; int i;
	for (i = 0; name[i] && i < 255; i++) nm[i] = name[i];
	nm[i] = 0;
	long fd = sc(5, (long)"/dev/ashmem", 2, 0, 0, 0, 0);
	if (fd < 0) return fd;
	if (sc(54, fd, 0x41007701, (long)nm, 0, 0, 0) < 0 || sc(54, fd, 0x40047703, size, 0, 0, 0) < 0) return -1000;
	long p = sc(192, 0, size, 3, flags, fd, 0);      /* mmap2(PROT_READ|PROT_WRITE) */
	sc(6, fd, 0, 0, 0, 0, 0);
	if (p < 0 && p > -4096) return p;
	((volatile char *)p)[0] = 1; ((volatile char *)p)[size - 1] = 2;   /* tocar primera y última página */
	return p;
}

void _start(void)
{
	int bad = 0; long r;
	r = region(1748992, 2, "dalvik-mark-stack"); out("ASHMEM privada-1748992", r < 0 ? r : 0); bad |= r < 0 && r > -4096;
	r = region(16 << 20, 2, "dalvik-heap");      out("ASHMEM privada-16M", r < 0 ? r : 0);     bad |= r < 0 && r > -4096;
	r = region(65536, 1, "compartida");          out("ASHMEM compartida-64K", r < 0 ? r : 0);  bad |= r < 0 && r > -4096;
	for (int i = 0; i < 40 && !bad; i++) { r = region(1748992, 2, "repetida"); if (r < 0 && r > -4096) { out("ASHMEM repetida", r); bad = 1; } }
	sc(4, 1, (long)(bad ? "ASHMEM FALLO\n" : "ASHMEM OK\n"), bad ? 13 : 10, 0, 0, 0);
	sc(1, bad, 0, 0, 0, 0, 0);
}
