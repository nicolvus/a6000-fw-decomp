// T6 (invitado, emulador): sustituye lo que el init de Android da al zygote. Crea el socket /dev/socket/zygote (stream, 0666),
// exporta ANDROID_SOCKET_zygote=<fd> y hace execve de argv[1..] (p. ej. /system/bin/app_process -Xzygote ...). Sin libc, ARM EABI.
// Uso: zygote_launch /system/bin/app_process -Xzygote /system/bin --zygote --start-system-server
typedef unsigned long ul;
static long sc(long n, long a, long b, long c)
{
	register long r7 __asm__("r7") = n, r0 __asm__("r0") = a, r1 __asm__("r1") = b, r2 __asm__("r2") = c;
	__asm__ volatile("svc 0" : "+r"(r0) : "r"(r7), "r"(r1), "r"(r2) : "memory");
	return r0;
}

__attribute__((used)) void cmain(long *sp)
{
	long argc = sp[0]; char **argv = (char **)(sp + 1), **envp = argv + argc + 1, *env[64];
	static char var[] = "ANDROID_SOCKET_zygote=0000";
	static struct { unsigned short f; char p[108]; } a = { 1, "/dev/socket/zygote" };   /* AF_UNIX */
	int n = 0, fd;
	sc(10, (long)a.p, 0, 0);                               /* unlink */
	fd = sc(281, 1, 1, 0);                                 /* socket(AF_UNIX, SOCK_STREAM) */
	if (fd < 0 || sc(282, fd, (long)&a, sizeof(a)) < 0 || sc(284, fd, 10, 0) < 0) sc(1, 2, 0, 0);
	sc(15, (long)a.p, 0666, 0);                            /* chmod */
	for (int i = 0, v = fd; i < 4; i++, v /= 10) var[25 - i] = '0' + v % 10;
	while (*envp && n < 62) env[n++] = *envp++;
	env[n++] = var; env[n] = 0;
	if (argc > 1) sc(11, (long)argv[1], (long)(argv + 1), (long)env);   /* execve */
	sc(1, 3, 0, 0);
}

__asm__(".global _start\n_start:\n mov r0, sp\n bl cmain\n");
