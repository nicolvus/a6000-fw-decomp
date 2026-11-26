/* Llamador de funciones dentro de un proceso de la cámara (ARM EABI, kernel 3.0.27, sin libc).
 *
 *   ptcall [--dry] [--sp DIR] PID TID peek DIR LEN
 *   ptcall [--dry] [--sp DIR] PID TID call NARG VA [A0 A1 A2 A3]
 *
 * - TID = hilo al que se engancha (0 = usar PID).  --dry = no engancha: sólo imprime lo que haría.
 * - PTRACE_ATTACH + GETREGS, se escriben PC/LR/r0..r3 (LR = centinela 0xDEAD0000), PTRACE_CONT y se espera el
 *   SIGSEGV del retorno al centinela (si_addr == 0xDEAD0000); se lee r0 y se restauran los registros guardados
 *   antes de PTRACE_DETACH. No se parchea código (nada de BKPT) ni hace falta memoria ejecutable nueva.
 * - VA ya con el bit 0 si la función es Thumb (p. ej. libmpr+0x2B50D9 para el handler FBM 0x2B50D8).
 * - Con --sp se cambia también SP (recomendado: una zona de pila libre del propio proceso; sin --sp se usa la
 *   pila del hilo interrumpido, que puede quedarse sin margen).
 *
 * Compilar (host): sh tools/camera-ptrace/build.sh   (deja ptcall junto a sctrace)
 * Secuencia y riesgos: reports/film-pb-1-sub-consola-fbm-anillo-20261127.md §3-§4.
 */
#define NULL ((void *)0)
#define SENTINEL 0xDEAD0000UL /* página no mapeada: el retorno de la función cae aquí */
#define SIGSEGV_ 11
#define SIGSTOP_ 19

static long sc(long n, long a, long b, long c, long d) {
    register long r7 __asm__("r7") = n; register long r0 __asm__("r0") = a; register long r1 __asm__("r1") = b;
    register long r2 __asm__("r2") = c; register long r3 __asm__("r3") = d;
    __asm__ volatile("svc 0" : "+r"(r0) : "r"(r7), "r"(r1), "r"(r2), "r"(r3) : "memory");
    return r0;
}
#define ptrace(r, p, a, d) sc(26, r, p, a, d)
#define PEEKDATA 2
#define CONT 7
#define GETREGS 12
#define SETREGS 13
#define ATTACH 16
#define DETACH 17
#define GETSIGINFO 0x4202

static long len(const char *s) { long n = 0; while (s[n]) n++; return n; }
static void out(const char *s, long n) { sc(4, 1, (long)s, n, 0); }
static void puts_(const char *s) { out(s, len(s)); }
static char *itoa(long v, char *p, int base) {
    char t[24]; int i = 0; unsigned long u = v < 0 ? -v : v;
    if (base == 16) { do { t[i++] = "0123456789abcdef"[u & 15]; u >>= 4; } while (u); }
    else { do { unsigned long q = 0, r = 0; for (int b = 31; b >= 0; b--) { r = (r << 1) | ((u >> b) & 1); if (r >= 10) { r -= 10; q |= 1UL << b; } } t[i++] = '0' + r; u = q; } while (u); }
    if (v < 0) *p++ = '-';
    while (i) *p++ = t[--i];
    return p;
}
static char *hex2(unsigned b, char *p) { *p++ = "0123456789abcdef"[(b >> 4) & 15]; *p++ = "0123456789abcdef"[b & 15]; return p; }
static char *hexp(unsigned long v, char *p) { *p++ = '0'; *p++ = 'x'; for (int s = 28; s >= 0; s -= 4) *p++ = "0123456789abcdef"[(v >> s) & 15]; return p; }
static long atol_(const char *s) { long v = 0; while (*s == ' ') s++; while (*s >= '0' && *s <= '9') v = v * 10 + (*s++ - '0'); return v; }
static unsigned long hex(const char *s) {
    unsigned long v = 0; while (*s == ' ') s++;
    if (s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) s += 2;
    for (;; s++) {
        char c = *s; unsigned d;
        if (c >= '0' && c <= '9') d = c - '0'; else if (c >= 'a' && c <= 'f') d = c - 'a' + 10;
        else if (c >= 'A' && c <= 'F') d = c - 'A' + 10; else break;
        v = (v << 4) | d;
    }
    return v;
}
static int streq(const char *a, const char *b) { while (*a && *a == *b) { a++; b++; } return *a == *b; }

static unsigned long g_si[8];  /* siginfo crudo del ultimo stop: [0]=signo [2]=codigo [3]=si_addr */
static void wait_stop(long tid, int *sig, unsigned long *fault) {
    int st = 0; *sig = 0; *fault = 0;
    if (sc(114, tid, (long)&st, 0x40000000, 0) < 0) return;
    *sig = (st >> 8) & 0xff;
    if (*sig == SIGSEGV_) {
        /* siginfo_t son 128 B: con 16 B el kernel escribe fuera del marco y el trazador se cae
         * (SIGSEGV de ptcall, exit 139). si_addr = siginfo[3] (offset 12: tras signo/errno/código). */
        static unsigned long si[32];
        for (int k = 0; k < 32; k++) si[k] = 0;
        if (ptrace(GETSIGINFO, tid, 0, (long)si) == 0) { *fault = si[3]; for (int k = 0; k < 8; k++) g_si[k] = si[k]; }
    }
}

/* palabra de 32 bits del tracee (ARM: PEEKDATA escribe el dato en *data, no en r0) */
static long pw(long tid, unsigned long a) { long w = 0; if (ptrace(PEEKDATA, tid, a, (long)&w) < 0) return -1; return w; }
static int pput(long tid, unsigned long a, long w) { return ptrace(5 /*POKEDATA*/, tid, a, w) == 0 ? 0 : -1; }

/* escribe b en la dirección a conservando los otros 3 bytes de la palabra */
static int pputb(long tid, unsigned long a, unsigned char b) {
    unsigned long base = a & ~3UL; int sh = (int)((a & 3) * 8);
    long w = pw(tid, base);
    if (w < 0) return -1;
    w = (w & ~(0xffL << sh)) | ((long)b << sh);
    return pput(tid, base, w);
}

int main_c(long *sp) {
    int argc = sp[0]; char **argv = (char **)(sp + 1);
    int dry = 0; unsigned long sp_nuevo = 0; int i = 1;
    while (i < argc && argv[i][0] == '-' && argv[i][1] == '-') {
        if (streq(argv[i], "--dry")) dry = 1;
        else if (streq(argv[i], "--sp") && i + 1 < argc) sp_nuevo = hex(argv[++i]);
        else break;
        i++;
    }
    if (argc - i < 4) {
        puts_("uso: ptcall [--dry] [--sp DIR] PID TID peek DIR LEN\n"
              "     ptcall [--dry] [--sp DIR] PID TID poke DIR BYTE...   (BYTE en hex, 01..ff; se escribe de 4 en 4)\n"
              "     ptcall [--dry] [--sp DIR] PID TID call NARG VA [A0 A1 A2 A3]\n");
        return 2;
    }
    long pid = atol_(argv[i]), tid = atol_(argv[i + 1]);
    const char *modo = argv[i + 2];
    if (tid == 0) tid = pid;

    if (streq(modo, "peek")) {
        unsigned long addr = hex(argv[i + 3]), n = hex(argv[i + 4]);
        char b[300]; char *p;
        if (dry) {
            p = b; *p++ = '('; *p++ = 'd'; *p++ = 'r'; *p++ = 'y'; *p++ = ')'; *p++ = ' ';
            p = hexp(addr, p); *p++ = ' '; p = itoa((long)n, p, 10); *p++ = ' '; *p++ = 'B'; *p++ = '\n';
            out(b, p - b); puts_("(dry) no se engancha\n"); return 0;
        }
        if (ptrace(ATTACH, tid, 0, 0) != 0) { puts_("ATTACH falló (¿mismo uid / CAP_SYS_PTRACE?)\n"); return 1; }
        int sig; unsigned long f; wait_stop(tid, &sig, &f);
        { char s2[40]; char *q = s2; *q++ = 's'; *q++ = 'i'; *q++ = 'g'; *q++ = '='; q = itoa(sig, q, 10);
          *q++ = ' '; *q++ = 'f'; *q++ = 'a'; *q++ = 'u'; *q++ = 'l'; *q++ = 't'; *q++ = '='; q = hexp(f, q);
          *q++ = '\n'; out(s2, q - s2); }
        unsigned long k = 0;
        while (k < n) {
            p = b; p = hexp(addr + k, p); *p++ = ':'; *p++ = ' ';
            for (int c = 0; c < 16 && k < n; c++, k += 4) {
                /* ARM (arch/arm/kernel/ptrace.c): PTRACE_PEEKDATA no devuelve el dato en r0, hace
                 * put_user(tmp, (unsigned long __user *)data) => hay que pasar un puntero válido
                 * (con data=0 el kernel devuelve -EFAULT = -14, que es lo que salía antes). */
                long w = 0; long rr = ptrace(PEEKDATA, tid, addr + k, (long)&w);
                if (rr < 0) { p = hex2((unsigned)(-rr) & 0xff, p); *p++ = '!'; *p++ = '\n'; out(b, p - b); break; }
                for (int q = 0; q < 4 && (unsigned long)q < n - k; q++) { p = hex2((w >> (8 * q)) & 0xff, p); *p++ = ' '; }
            }
            *p++ = '\n'; out(b, p - b);
        }
        ptrace(DETACH, tid, 0, 0);
        return 0;
    }
    if (streq(modo, "poke")) {
        unsigned long addr = hex(argv[i + 3]);
        unsigned char bb[256]; long n = 0;
        for (int k = i + 4; k < argc && n < (long)sizeof bb; k++) bb[n++] = (unsigned char)hex(argv[k]);
        char b2[300]; char *p2;
        if (dry) { p2 = b2; *p2++ = '('; *p2++ = 'd'; *p2++ = 'r'; *p2++ = 'y'; *p2++ = ')'; *p2++ = ' ';
            p2 = hexp(addr, p2); *p2++ = ' '; p2 = itoa(n, p2, 10); *p2++ = ' '; *p2++ = 'B'; *p2++ = '\n';
            out(b2, p2 - b2); puts_("(dry) no se engancha\n"); return 0; }
        if (ptrace(ATTACH, tid, 0, 0) != 0) { puts_("ATTACH falló (¿mismo uid / CAP_SYS_PTRACE?)\n"); return 1; }
        int sig2; unsigned long f2; wait_stop(tid, &sig2, &f2);
        for (long k = 0; k < n; k += 4) {
            long w = ptrace(PEEKDATA, tid, addr + k, 0);   /* leer para conservar la cola */
            for (long q = 0; q < 4 && k + q < n; q++) w = (w & ~(0xffL << (8 * q))) | ((long)bb[k + q] << (8 * q));
            ptrace(5 /*POKEDATA*/, tid, addr + k, w);
        }
        ptrace(DETACH, tid, 0, 0);
        puts_("poke ok\n");
        return 0;
    }
    if (streq(modo, "ring")) {   /* PID TID ring BASE "TEXTO": deposita TEXTO+CR en el anillo del monitor EX-PC */
        unsigned long base = hex(argv[i + 3]);
        const char *txt = argv[i + 4];
        char b[200]; char *p;
        if (base == 0) { puts_("uso: ptcall PID TID ring BASE \"TEXTO\"\n"); return 2; }
        if (dry) {
            p = b; *p++ = '('; *p++ = 'd'; *p++ = 'r'; *p++ = 'y'; *p++ = ')'; *p++ = ' ';
            *p++ = 'b'; *p++ = 'a'; *p++ = 's'; *p++ = 'e'; *p++ = '='; p = hexp(base, p);
            *p++ = ' '; *p++ = 'l'; *p++ = 'i'; *p++ = 'n'; *p++ = 'e'; *p++ = 'a'; *p++ = '=';
            for (const char *q = txt; *q && p < b + 150; q++) *p++ = *q;
            *p++ = '\n'; out(b, p - b); puts_("(dry) no se engancha\n"); return 0;
        }
        if (ptrace(ATTACH, tid, 0, 0) != 0) { puts_("ATTACH falló (¿mismo uid / CAP_SYS_PTRACE?)\n"); return 1; }
        int sig; unsigned long f; wait_stop(tid, &sig, &f);
        long X = pw(tid, base + 0xA4FD88);            /* descriptor: +0 = VA del anillo */
        if ((unsigned long)X < 0x1000UL || (unsigned long)X > 0xffff0000UL) {  /* ojo: las VA del invitado son negativas como long con signo */
            puts_("no pude leer libmpr+0xA4FD88 (¿BASE correcta?)\n"); ptrace(DETACH, tid, 0, 0); return 1; }
        long A = pw(tid, (unsigned long)X), B = pw(tid, (unsigned long)X + 4);
        if (A < 0 || B < 0) { puts_("no pude leer A/B del anillo\n"); ptrace(DETACH, tid, 0, 0); return 1; }
        unsigned n = 0; while (txt[n]) n++;
        n++;                                          /* + el CR final */
        unsigned libres = (unsigned)((A - B - 1) & 0x3ff);
        p = b; *p++ = 'X'; *p++ = '='; p = hexp(( unsigned long)X, p);
        *p++ = ' '; *p++ = 'A'; *p++ = '='; p = itoa(A, p, 10);
        *p++ = ' '; *p++ = 'B'; *p++ = '='; p = itoa(B, p, 10);
        *p++ = ' '; *p++ = 'l'; *p++ = 'i'; *p++ = 'b'; *p++ = 'r'; *p++ = 'e'; *p++ = 's'; *p++ = '='; p = itoa(libres, p, 10);
        *p++ = '\n'; out(b, p - b);
        if (n == 1) { puts_("(sin linea: no se escribe nada)\n"); ptrace(DETACH, tid, 0, 0); return 0; }  /* sólo estado */
        if (n > libres) { puts_("no cabe la linea en el anillo\n"); ptrace(DETACH, tid, 0, 0); return 1; }
        for (unsigned k = 0; k < n; k++) {            /* bytes: TEXTO y CR, con vuelta al principio */
            unsigned off = (unsigned)((B + k) & 0x3ff);
            unsigned char ch = (k + 1 == n) ? 0x0d : (unsigned char)txt[k];
            if (pputb(tid, (unsigned long)X + 0x10 + off, ch) != 0) { puts_("fallo al escribir el bufer\n"); ptrace(DETACH, tid, 0, 0); return 1; }
        }
        unsigned NB = (unsigned)((B + n) & 0x3ff);    /* un solo store: el monitor ve la linea entera */
        if (pput(tid, (unsigned long)X + 4, NB) != 0) { puts_("fallo al publicar B\n"); ptrace(DETACH, tid, 0, 0); return 1; }
        ptrace(DETACH, tid, 0, 0);
        p = b; *p++ = 'o'; *p++ = 'k'; *p++ = ' '; *p++ = 'B'; *p++ = ':'; *p++ = ' '; p = itoa(B, p, 10);
        *p++ = ' '; *p++ = '-'; *p++ = '>'; *p++ = ' '; p = itoa(NB, p, 10);
        *p++ = ' '; *p++ = '('; p = itoa(n, p, 10); *p++ = ' '; *p++ = 'B'; *p++ = ')'; *p++ = '\n'; out(b, p - b);
        return 0;
    }
    if (!streq(modo, "call")) { puts_("modo desconocido (peek|poke|call|ring)\n"); return 2; }
    long narg = atol_(argv[i + 3]);
    unsigned long va = hex(argv[i + 4]);
    unsigned long a[4] = {0, 0, 0, 0};
    for (long k = 0; k < narg && k < 4 && i + 5 + k < argc; k++) a[k] = hex(argv[i + 5 + k]);
    char b[260]; char *p = b;
    if (dry) {
        p = b; *p++ = '('; *p++ = 'd'; *p++ = 'r'; *p++ = 'y'; *p++ = ')'; *p++ = ' ';
        *p++ = 'p'; *p++ = 'c'; *p++ = '='; p = hexp(va, p); *p++ = ' ';
        for (int k = 0; k < 4; k++) { *p++ = 'r'; *p++ = '0' + k; *p++ = '='; p = hexp(a[k], p); *p++ = ' '; }
        *p++ = 'l'; *p++ = 'r'; *p++ = '='; p = hexp(SENTINEL, p);
        if (sp_nuevo) { *p++ = ' '; *p++ = 's'; *p++ = 'p'; *p++ = '='; p = hexp(sp_nuevo, p); }
        *p++ = '\n'; out(b, p - b); puts_("(dry) no se engancha\n"); return 0;
    }
    if (ptrace(ATTACH, tid, 0, 0) != 0) { puts_("ATTACH falló (¿mismo uid / CAP_SYS_PTRACE?)\n"); return 1; }
    int sig; unsigned long f; long r[18], sv[18];
    wait_stop(tid, &sig, &f);
    if (sig != SIGSTOP_) { p = b; *p++ = 's'; *p++ = 'i'; *p++ = 'g'; *p++ = '='; p = itoa(sig, p, 10); *p++ = '\n'; out(b, p - b);
        ptrace(DETACH, tid, 0, 0); return 1; }
    if (ptrace(GETREGS, tid, 0, (long)r) != 0) { puts_("GETREGS falló\n"); ptrace(DETACH, tid, 0, 0); return 1; }
    for (int k = 0; k < 18; k++) sv[k] = r[k];
    r[0] = (long)a[0]; r[1] = (long)a[1]; r[2] = (long)a[2]; r[3] = (long)a[3];
    r[14] = (long)SENTINEL; r[15] = (long)va;
    if (va & 1) r[16] |= 0x20; else r[16] &= ~0x20L;   /* CPSR.T: el estado (ARM/Thumb) lo fija el bit 0 de la VA */
    if (sp_nuevo) r[13] = (long)sp_nuevo;
    if (ptrace(SETREGS, tid, 0, (long)r) != 0) { puts_("SETREGS falló\n"); ptrace(DETACH, tid, 0, 0); return 1; }
    ptrace(CONT, tid, 0, 0);
    wait_stop(tid, &sig, &f);
    long ret = -1; int vio_centinela = (sig == SIGSEGV_ && f == SENTINEL);
    if (ptrace(GETREGS, tid, 0, (long)r) == 0) {
        ret = r[0];
        p = b; *p++ = 's'; *p++ = 'i'; *p++ = 'g'; *p++ = '='; p = itoa(sig, p, 10);
        *p++ = ' '; *p++ = 'c'; *p++ = 'o'; *p++ = 'd'; *p++ = 'e'; *p++ = '='; p = hexp(g_si[2], p);
        *p++ = ' '; *p++ = 'f'; *p++ = 'a'; *p++ = 'u'; *p++ = 'l'; *p++ = 't'; *p++ = '='; p = hexp(f, p);
        *p++ = ' '; *p++ = 'r'; *p++ = 'e'; *p++ = 't'; *p++ = '='; p = hexp(ret, p);
        *p++ = ' '; *p++ = 'c'; *p++ = 'e'; *p++ = 'n'; *p++ = 't'; *p++ = 'i'; *p++ = 'n'; *p++ = 'e'; *p++ = 'l'; *p++ = 'a'; *p++ = '=';
        *p++ = '0' + (vio_centinela ? 1 : 0); *p++ = '\n'; out(b, p - b);
        /* si el retorno parece un puntero al espacio del proceso, se leen 24 B y se muestran: así se ve
         * el texto devuelto (p. ej. GetErrorString(7) -> "FBS_INVALID_PROCESS") */
        if ((unsigned long)ret > 0x10000UL && (unsigned long)ret < 0xffff0000UL) {
            char txt[26]; int j = 0;
            for (int q = 0; q < 6; q++) {
                long ww = 0;
                if (ptrace(PEEKDATA, tid, (ret & ~1L) + q * 4, (long)&ww) < 0) break;
                for (int z = 0; z < 4; z++) { char ch = (char)((ww >> (8 * z)) & 0xff);
                    if (!ch) { q = 6; break; } if (ch < 32 || ch > 126) ch = '.'; txt[j++] = ch; }
            }
            txt[j] = 0; p = b; *p++ = 't'; *p++ = 'e'; *p++ = 'x'; *p++ = 't'; *p++ = '=';
            for (int z = 0; z < j; z++) *p++ = txt[z];
            *p++ = '\n'; out(b, p - b);
        }
    }
    for (int k = 0; k < 18; k++) r[k] = sv[k];
    ptrace(SETREGS, tid, 0, (long)r);
    ptrace(DETACH, tid, 0, 0);
    return vio_centinela ? 0 : 1;
}

__attribute__((naked)) void _start(void) { __asm__ volatile("mov r0, sp\n bl main_c\n mov r7, #1\n svc 0"); }
