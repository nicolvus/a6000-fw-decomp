/* Trazador mínimo de syscalls para la cámara (ARM EABI, kernel 3.0.27, sin libc ni strace).
 * Uso: sctrace SEGUNDOS PID TID1 [TID2 ...]  >  /tmp/trace.txt
 * Hace PTRACE_ATTACH a cada TID y PTRACE_SYSCALL; registra entradas de syscall: "ms tid nr a0 a1 a2 [ruta]".
 * Al agotar el tiempo (o al salir) el kernel suelta a los hilos trazados. Hilos creados después no se trazan.
 * Compilar: ./build.sh */
#define NULL ((void*)0)
static long sc(long n, long a, long b, long c, long d) {
    register long r7 __asm__("r7") = n; register long r0 __asm__("r0") = a; register long r1 __asm__("r1") = b;
    register long r2 __asm__("r2") = c; register long r3 __asm__("r3") = d;
    __asm__ volatile("svc 0" : "+r"(r0) : "r"(r7), "r"(r1), "r"(r2), "r"(r3) : "memory");
    return r0;
}
#define ptrace(r, p, a, d) sc(26, r, p, a, d)
static long len(const char *s) { long n = 0; while (s[n]) n++; return n; }
static void out(const char *s, long n) { sc(4, 1, (long)s, n, 0); }
static char *itoa(long v, char *p, int base) { /* escribe v al final de p y devuelve el inicio */
    char t[24]; int i = 0; unsigned long u = v < 0 ? -v : v;
    if (base == 16) { do { t[i++] = "0123456789abcdef"[u & 15]; u >>= 4; } while (u); }
    else { do { unsigned long q = 0, r = 0; for (int b = 31; b >= 0; b--) { r = (r << 1) | ((u >> b) & 1); if (r >= 10) { r -= 10; q |= 1UL << b; } } t[i++] = '0' + r; u = q; } while (u); }
    if (v < 0) *p++ = '-';
    while (i) *p++ = t[--i];
    return p;
}
static long atol_(const char *s) { long v = 0; while (*s >= '0' && *s <= '9') v = v * 10 + (*s++ - '0'); return v; }
static long now_ms(void) { long tv[2]; sc(78, (long)tv, 0, 0, 0); return tv[0] * 1000 + tv[1] / 1000; }

/* lee una cadena de la memoria del tracee, máx. n-1 bytes */
static void peekstr(long tid, unsigned long addr, char *dst, int n) {
    int i = 0;
    while (i < n - 1) {
        long w = 0; long r = ptrace(2, tid, addr + i, (long)&w);
        if (r < 0) break;
        for (int k = 0; k < 4 && i < n - 1; k++) { char c = (w >> (8 * k)) & 255; dst[i++] = c; if (!c) { return; } }
    }
    dst[i] = 0;
}

static int ignore(long nr) { /* ruido: futex, relojes, esperas */
    return nr == 240 || nr == 263 || nr == 78 || nr == 162 || nr == 265 || nr == 142 || nr == 168 || nr == 336 || nr == 369 || nr == 114 || nr == 119;
}

int main_c(long *sp) {
    int argc = sp[0]; char **argv = (char **)(sp + 1);
    if (argc < 4) { const char u[] = "uso: sctrace SEGUNDOS PID TID...\n"; out(u, sizeof u - 1); return 1; }
    long secs = atol_(argv[1]), pid = atol_(argv[2]), t0 = now_ms(), alive = 0;
    sc(27, secs + 2, 0, 0, 0); /* alarm: SIGALRM mata al trazador y el kernel suelta a los hilos aunque no haya eventos */
    for (int i = 3; i < argc; i++) {
        long tid = atol_(argv[i]);
        if (ptrace(16, tid, 0, 0) == 0) alive++;
    }
    /* esperar la parada inicial de cada hilo y activar SYSGOOD */
    for (long n = 0; n < alive; n++) {
        int st; long w = sc(114, -1, (long)&st, 0x40000000, 0);
        if (w < 0) break;
        ptrace(0x4200, w, 0, 1); /* SETOPTIONS: TRACESYSGOOD */
        ptrace(24, w, 0, 0);     /* SYSCALL */
    }
    char line[300]; static unsigned char mask[1 << 16]; (void)mask;
    while (alive > 0) {
        long ms = now_ms() - t0;
        if (ms > secs * 1000) { const char e[] = "# fin por tiempo\n"; out(e, sizeof e - 1); return 0; }
        int st; long w = sc(114, -1, (long)&st, 0x40000000, 0);
        if (w < 0) break;
        if ((st & 0x7f) != 0x7f) { alive--; continue; } /* hilo terminado */
        int sig = (st >> 8) & 255, inject = 0;
        if (sig == (5 | 0x80)) {
            long r[18]; ptrace(12, w, 0, (long)r);
            if (r[12] == 0) { /* entrada */
                long nr = r[7];
                if (!ignore(nr)) {
                    char *p = line; p = itoa(ms, p, 10); *p++ = ' '; p = itoa(w, p, 10); *p++ = ' '; p = itoa(nr, p, 10);
                    for (int k = 0; k < 4; k++) { *p++ = ' '; *p++ = '0'; *p++ = 'x'; p = itoa((unsigned long)r[k] & 0xffffffffUL, p, 16); }
                    if (nr == 5 || nr == 322 || nr == 33 || nr == 11) { /* open, openat, access, execve */
                        char s[96]; peekstr(w, nr == 322 ? r[1] : r[0], s, sizeof s); *p++ = ' '; for (char *q = s; *q; ) *p++ = *q++;
                    } else if (nr == 3 || nr == 4 || nr == 54 || nr == 192 || nr == 6 || nr == 91) { /* read write ioctl mmap2 close munmap: ruta del fd */
                        char path[40] = "/proc/"; char *q = path + 6; q = itoa(pid, q, 10); const char f[] = "/fd/"; for (int k = 0; k < 4; k++) *q++ = f[k];
                        q = itoa(nr == 192 ? (long)(int)r[4] : r[0], q, 10); *q = 0;
                        char dst[80]; long l = sc(85, (long)path, (long)dst, 79, 0);
                        if (l > 0) { dst[l] = 0; *p++ = ' '; *p++ = '['; for (long k = 0; k < l; k++) *p++ = dst[k]; *p++ = ']'; }
                    }
                    *p++ = '\n'; out(line, p - line);
                }
            }
        } else if (sig != 19 && sig != 5) inject = sig; /* reinyectar señales ajenas, no SIGSTOP/SIGTRAP */
        ptrace(24, w, 0, inject);
    }
    return 0;
}

__attribute__((naked)) void _start(void) {
    __asm__ volatile("mov r0, sp\n bl main_c\n mov r7, #1\n svc 0");
}
