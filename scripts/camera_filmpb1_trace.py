#!/usr/bin/env python3
"""FILM-PB-1 — kit de captura: cuál de los TRES productores de `MPR::ER_FAILED` (0x1A) dispara.

Una orden, tres puntos de parada de un solo golpe sobre el manejador `FUN_00437BC0` de `libmpr.so`:

  0x437C0A  « Pb Disable!! ref) dsm get»  → guarda A (capacidades de la entidad; H1 arranque/WBI)
  0x437C3C  « Detect UnSupported Content » → guarda B (contenido no soportado; H2 contenido/BD)
  0x7111B0  entrada de la traducción de error de `MoviePlayerIf::PbStart` (seis sitios devuelven 0x1A)

Direcciones: **VA del ELF de `libmpr.so` (base 0)**, tal como están en los informes del 26/11 y del
27/11. La dirección de ejecución es `base + VA`, con `base` leída de `/proc/PID/maps` en esta sesión:
las bases de traspaso (libmpr 0x06B95000, libObj 0x05AB2000) NO se reutilizan; el 17-11-2026 fueron
libmpr 0x06C7E000 y libObj 0x05B9B000 (analysis/camera-dumps/20261117-traza-T1/im_elf_maps.txt).

Corrección verificada contra bytes: el informe del 26/11 llama `FUN_007211B0` (0x7211B0) a la
traducción de error, pero los dos `bl` del manejador (0x437C7E y 0x437CFC) apuntan a **0x7111B0**,
cuya primera instrucción es `and r3, r0, #0xff000000` / `cmp.w r3, #0x1c000000`, y el sitio del
`0x1C00001A → 0x1A` citado en ese informe (0x711232) cae dentro de ella. El punto T se pone en 0x7111B0.

Método (el ya usado en el proyecto, sin inventar nada):
  · transporte `scripts/camera_telnet.py` (telnet root del Tweak, probado);
  · `/proc/PID/maps` leído con `cat` (igual que la traza T1 del 17-11-2026);
  · 16 bytes por dirección leídos con `dd` + `hd` de toybox vía `chroot /android`, que es el camino
    documentado porque el busybox de la cámara no trae `od`/`hexdump` (camera_darwin_buffers.py);
  · binario auxiliar ARM estático sin libc, mismo patrón que `tools/camera-ptrace/sctrace.c`
    (clang --target=arm-linux-gnueabi -nostdlib + svc 0), que en vez de trazar syscalls planta
    UDF 0xde00 por `PTRACE_POKETEXT` (el mismo 0xde00 que usa el arnés del proyecto) y lo restaura
    antes de reanudar: un solo golpe por punto, como `scripts/swd_bp_unico.sh`.
  · el binario auxiliar solo se sube en el modo que arma; `--dry-run` y `--verify` no escriben nada.

Modos:
  (sin opción)  arma, espera a que el usuario reproduzca el vídeo, interpreta y desarma.
  --dry-run     hace todo (binario incluido) menos escribir en la cámara.
  --verify      solo mapas y hashes de 16 bytes por punto.
  --simular MAPS  ensayo sin cámara con un volcado real de `/proc/PID/maps` (prueba la aritmética y
                  los hashes; implica --dry-run).
  --autotest    prueba las reglas de interpretación con líneas sintéticas del auxiliar.
  --callsites   añade 0x437C7E y 0x437CFC (los dos `bl` a 0x7111B0) para separar precondición de PbStart.
Salidas: 0 origen observado · 2 error local · 3 cámara no accesible · 4 mapas/hash no cuadran
         5 captura completa sin golpes · 6 captura incompleta o sin origen confirmado.

Riesgo conocido y NO VERIFICADO (docs/capture/camera-reset-logs.md:14): trazar con ptrace hilos de
`im.elf` puede coincidir con una petición de reset de la cámara; `sctrace` se compiló pero nunca se
probó con éxito. Por eso: todos los hilos o ninguno, un solo golpe por punto, restauración antes de
reanudar y comprobación (y reparación) de los bytes al terminar.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import time
from dataclasses import dataclass

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from camera_telnet import run  # transporte probado del proyecto

LIBDIR321 = os.path.join(
    RAIZ, "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev",
    "nflasha15_unpacked_unpacked/lib")
LIBMPR_SHA256 = "9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30"
LIBOBJ_CFW = os.path.join(RAIZ, "build/cfw_func393/pp/files/lib/libObj.so")

HELPER_REMOTO = "/tmp/filmpb1bp"      # /tmp del sistema Linux de la cámara
LOG_REMOTO = "/tmp/filmpb1.log"

COD_OK, COD_LOCAL, COD_SIN_CAMARA, COD_HASH, COD_SIN_GOLPE = 0, 2, 3, 4, 5
COD_INCONCLUSA = 6


@dataclass(frozen=True)
class Punto:
    clave: str          # A / B / T (y C1, C2 opcionales)
    va: int             # VA del ELF de libmpr.so (base 0)
    instr: str          # instrucción verificada con capstone (libmpr.so 3.21)
    mide: str


PUNTOS_BASE = (
    Punto("A", 0x437C0A, "movs r3, #0x1a",
          "guarda de capacidades (« Pb Disable!! ref) dsm get»): si se ejecuta, el 0x1A lo pone la guarda A"),
    Punto("B", 0x437C3C, "movs r3, #0x1a",
          "guarda de contenido (« Detect UnSupported Content »): si se ejecuta, el 0x1A lo pone la guarda B"),
    Punto("T", 0x7111B0, "and r3, r0, #0xff000000",
          "entrada de la traducción de error interna→MPR llamada tras PbStart (0x437CFC) o por su precondición (0x437C7E)"),
)
PUNTOS_LLAMADAS = (
    Punto("E", 0x437BC0, "sub sp, #8",
          "entrada del manejador de PlayMovie"),
    Punto("C1", 0x437C7E, "bl #0x7111b0",
          "llamada a la traducción desde la PRECONDICIÓN (FUN_00457DA8 != 0), sin llegar a PbStart"),
    Punto("C2", 0x437CFC, "bl #0x7111b0",
          "llamada a la traducción desde el FALLO de MoviePlayerIf::PbStart"),
)
# Sitios `bl` conocidos que llaman a 0x7111B0 dentro del manejador → se decodifican desde LR.
LLAMADAS_CONOCIDAS = {0x437C7E: "C1 precondición FUN_00457DA8", 0x437CFC: "C2 fallo de PbStart"}

HELPER_C = r'''
/* filmpb1bp — puntos de parada de un solo golpe (UDF 0xde00) por ptrace en un proceso ARM32.
 * Sin libc (freestanding, mismo patrón que tools/camera-ptrace/sctrace.c: svc 0 con el nº en r7).
 * uso: filmpb1bp SEGUNDOS PID TIDS PUNTOS
 *   TIDS   "143,144,145"  hilos a trazar (todos: si uno no se puede, no se arma nada)
 *   PUNTOS "0x437c0a:0x231a,0x437c3c:0x231a"   dirección:halfword esperado
 * Solo se escribe UDF donde el halfword leído coincide con el esperado; cada punto es de un solo
 * golpe (se restaura antes de reanudar) y al salir se restauran los que queden.
 * Salida en hex: A armado | X no armado | H golpe | R restaurado | E fin.
 */
typedef unsigned long ulong;
typedef unsigned short ushort;

static long sc4(long n, long a, long b, long c, long d) {
    register long r7 __asm__("r7") = n;
    register long r0 __asm__("r0") = a;
    register long r1 __asm__("r1") = b;
    register long r2 __asm__("r2") = c;
    register long r3 __asm__("r3") = d;
    __asm__ volatile("svc 0" : "+r"(r0) : "r"(r7), "r"(r1), "r"(r2), "r"(r3) : "memory");
    return r0;
}
static long sy2(long n, long a, long b) { return sc4(n, a, b, 0, 0); }
static long sy4(long n, long a, long b, long c, long d) { return sc4(n, a, b, c, d); }

#define SYS_write 4
#define SYS_ptrace 26
#define SYS_gettimeofday 78
#define SYS_wait4 114
#define SYS_nanosleep 162

#define PT_PEEKTEXT 1
#define PT_POKETEXT 4
#define PT_CONT 7
#define PT_GETREGS 12
#define PT_SETREGS 13
#define PT_ATTACH 16
#define PT_DETACH 17
#define WALL 0x40000000L
#define WNOHANG 1
#define ESRCH 3
#define SIGILL 4
#define SIGTRAP 5
#define SIGSTOP 19
#define UDF 0xde00
#define MAXT 256
#define MAXP 6

static long tid[MAXT];
static int ntid;
static struct { ulong addr; ushort expect, orig; int ok, spent; } pt[MAXP];
static int npt, left;
static long regs[18];

static char obuf[320];
static char *puts_(char *p, const char *s) { while (*s) *p++ = *s++; return p; }
static char *puthex(char *p, ulong v) {
    char t[16]; int i = 0;
    *p++ = '0'; *p++ = 'x';
    if (!v) { *p++ = '0'; return p; }
    while (v) { t[i++] = "0123456789abcdef"[v & 15]; v >>= 4; }
    while (i) *p++ = t[--i];
    return p;
}
static char *putkv(char *p, const char *k, ulong v) { p = puts_(p, k); return puthex(p, v); }
static void emit(char *p) { sy4(SYS_write, 1, (long)obuf, (long)(p - obuf), 0); }

static long parsehex(const char *s) {
    ulong v = 0; int any = 0;
    if (s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) s += 2;
    for (;;) {
        char c = *s; ulong d;
        if (c >= '0' && c <= '9') d = (ulong)(c - '0');
        else if (c >= 'a' && c <= 'f') d = (ulong)(c - 'a' + 10);
        else if (c >= 'A' && c <= 'F') d = (ulong)(c - 'A' + 10);
        else break;
        v = (v << 4) | d; any = 1; s++;
    }
    return any ? (long)v : -1;
}
static long dec(const char *s) {
    long v = 0; int any = 0;
    while (*s >= '0' && *s <= '9') { v = v * 10 + (*s++ - '0'); any = 1; }
    return any ? v : -1;
}
static long now_ms(void) { long tv[2]; sy2(SYS_gettimeofday, (long)tv, 0); return tv[0] * 1000 + tv[1] / 1000; }
static int bad(long r) { return (ulong)r > 0xfffff000UL; }
static long err(long r) { return bad(r) ? -r : 0; }

/* ARM: PEEKTEXT devuelve 0 y escribe el dato en *data (generic_ptrace_peekdata);
 * POKETEXT lleva el valor en data. Con data=0 el kernel da -EFAULT. */
static int get_hw(long t, ulong a, ushort *out) {
    ulong w = 0;
    long r = sy4(SYS_ptrace, PT_PEEKTEXT, t, (long)(a & ~3UL), (long)&w);
    if (bad(r)) { long e = err(r); return (int)(e ? e : -1); }
    *out = (ushort)((a & 2) ? ((w >> 16) & 0xffffUL) : (w & 0xffffUL));
    return 0;
}
static int set_hw(long t, ulong a, ushort v) {
    ulong aw = a & ~3UL, w = 0;
    if (bad(sy4(SYS_ptrace, PT_PEEKTEXT, t, (long)aw, (long)&w))) return -1;
    w = (a & 2) ? ((w & 0xffffUL) | ((ulong)v << 16)) : ((w & 0xffff0000UL) | (ulong)v);
    return bad(sy4(SYS_ptrace, PT_POKETEXT, t, (long)aw, (long)w)) ? -1 : 0;
}
static int vivos(void) {
    int i, n = 0;
    for (i = 0; i < ntid; i++) if (tid[i] > 0) n++;
    return n;
}
static void desarma(long t) {
    int i;
    for (i = 0; i < npt; i++) {
        char *p;
        if (!pt[i].ok || pt[i].spent) continue;
        p = putkv(obuf, "R i=", (ulong)i);
        if (set_hw(t, pt[i].addr, pt[i].orig) == 0) { p = putkv(p, " addr=", pt[i].addr); pt[i].spent = 1; }
        else { p = puts_(p, " FALLA addr="); p = puthex(p, pt[i].addr); }
        *p++ = '\n'; emit(p);
    }
}
static void on_stop(long t, int st, long t0) {
    int sig = (st >> 8) & 0xff, i, hit = -1;
    ulong pc, cpsr;
    char *p;
    if ((st & 0xff) != 0x7f) {
        for (i = 0; i < ntid; i++) if (tid[i] == t) tid[i] = -1;
        return;
    }
    if (sig == SIGILL || sig == SIGTRAP) {
        if (bad(sy4(SYS_ptrace, PT_GETREGS, t, 0, (long)regs))) { sy4(SYS_ptrace, PT_CONT, t, 0, 0); return; }
        pc = (ulong)regs[15] & ~1UL; cpsr = (ulong)regs[16];
        for (i = 0; i < npt; i++)
            if (pt[i].ok && !pt[i].spent && pc >= pt[i].addr - 2 && pc <= pt[i].addr + 4) { hit = i; break; }
        if (hit >= 0) {
            pt[hit].spent = 1; left--;
            set_hw(t, pt[hit].addr, pt[hit].orig);
            regs[15] = (long)(pt[hit].addr | ((cpsr >> 5) & 1UL));
            sy4(SYS_ptrace, PT_SETREGS, t, 0, (long)regs);
            p = puts_(obuf, "H"); p = putkv(p, " ms=", (ulong)(now_ms() - t0));
            p = putkv(p, " i=", (ulong)hit); p = putkv(p, " tid=", (ulong)t); p = putkv(p, " pc=", pc);
            p = putkv(p, " r0=", (ulong)regs[0]); p = putkv(p, " r1=", (ulong)regs[1]);
            p = putkv(p, " r2=", (ulong)regs[2]); p = putkv(p, " r3=", (ulong)regs[3]);
            p = putkv(p, " lr=", (ulong)regs[14]); p = putkv(p, " left=", (ulong)(left < 0 ? 0 : left));
            *p++ = '\n'; emit(p);
            sy4(SYS_ptrace, PT_CONT, t, 0, 0);
            return;
        }
        sy4(SYS_ptrace, PT_CONT, t, (long)(sig == SIGILL ? SIGILL : 0), 0);
        return;
    }
    if (sig == SIGSTOP) { sy4(SYS_ptrace, PT_CONT, t, 0, 0); return; }
    sy4(SYS_ptrace, PT_CONT, t, (long)sig, 0);
}
int main_c(long *sp) {
    long argc = sp[0], t0, secs;
    char **argv = (char **)(sp + 1), *q, *p;
    int i, st, fallo = 0;
    if (argc < 5) {
        p = puts_(obuf, "uso: filmpb1bp SEGUNDOS PID TIDS PUNTOS\n"
                        "  TIDS 143,144,145   PUNTOS 0x437c0a:0x231a,0x437c3c:0x231a\n");
        emit(p); return 1;
    }
    secs = dec(argv[1]); if (secs <= 0) secs = 30;
    q = argv[3];
    while (*q && ntid < MAXT) {
        long v = dec(q);
        if (v <= 0) break;
        tid[ntid++] = v;
        while (*q && *q != ',') q++;
        if (*q == ',') q++;
    }
    q = argv[4];
    while (*q && npt < MAXP) {
        long a = parsehex(q), e;
        if (a < 0) break;
        while (*q && *q != ':') q++;
        if (*q != ':') break;
        e = parsehex(q + 1);
        if (e < 0) break;
        pt[npt].addr = (ulong)a; pt[npt].expect = (ushort)e; pt[npt].ok = 0; pt[npt].spent = 0; npt++;
        while (*q && *q != ',') q++;
        if (*q == ',') q++;
    }
    if (!ntid || !npt) { p = puts_(obuf, "E args\n"); emit(p); return 1; }
    for (i = 0; i < ntid; i++) {
        long r = sy4(SYS_ptrace, PT_ATTACH, tid[i], 0, 0);
        if (bad(r)) {
            p = putkv(obuf, "X tid=", (ulong)tid[i]); p = putkv(p, " err=", (ulong)err(r)); *p++ = '\n'; emit(p);
            if (err(r) != ESRCH) fallo = 1;
            tid[i] = -1;
        } else {
            /* sin recoger el SIGSTOP, PEEK/POKE devuelve -1 (leido=0x0 en la 1ª prueba) */
            if (bad(sy4(SYS_wait4, tid[i], (long)&st, WALL, 0))) { p = putkv(obuf, "X wait tid=", (ulong)tid[i]); *p++ = '\n'; emit(p); }
        }
    }
    if (fallo || vivos() == 0) {
        p = puts_(obuf, "E attach fallido (no se arma nada)\n"); emit(p);
        for (i = 0; i < ntid; i++) if (tid[i] > 0) sy4(SYS_ptrace, PT_DETACH, tid[i], 0, 0);
        return 1;
    }
    left = 0;
    for (i = 0; i < npt; i++) {
        ushort hw = 0;
        int gr = get_hw(tid[0], pt[i].addr, &hw);
        if (gr == 0 && hw == pt[i].expect && set_hw(tid[0], pt[i].addr, UDF) == 0) {
            pt[i].orig = hw; pt[i].ok = 1; left++;
        } else {
            p = puts_(obuf, "X i="); p = puthex(p, (ulong)i); p = putkv(p, " addr=", pt[i].addr);
            p = putkv(p, " leido=", (ulong)hw); p = putkv(p, " esperado=", (ulong)pt[i].expect);
            p = putkv(p, " err=", (ulong)(gr < 0 ? -gr : 0));
            *p++ = '\n'; emit(p);
        }
    }
    t0 = now_ms();
    p = puts_(obuf, "A ms="); p = puthex(p, 0); p = putkv(p, " armados=", (ulong)left);
    p = putkv(p, " hilos=", (ulong)vivos()); p = putkv(p, " pid=", (ulong)dec(argv[2])); *p++ = '\n'; emit(p);
    for (i = 0; i < ntid; i++) if (tid[i] > 0) sy4(SYS_ptrace, PT_CONT, tid[i], 0, 0);
    while (left > 0 && vivos() > 0) {
        long w;
        if (now_ms() - t0 > secs * 1000) break;
        w = sy4(SYS_wait4, -1, (long)&st, WALL | WNOHANG, 0);
        if (w < 0) break;
        if (w == 0) { long ts[2]; ts[0] = 0; ts[1] = 50000000L; sy2(SYS_nanosleep, (long)ts, 0); continue; }
        on_stop(w, st, t0);
    }
    for (i = 0; i < ntid; i++) if (tid[i] > 0) { desarma(tid[i]); break; }
    for (i = 0; i < ntid; i++) if (tid[i] > 0) sy4(SYS_ptrace, PT_DETACH, tid[i], 0, 0);
    p = puts_(obuf, "E ms="); p = puthex(p, (ulong)(now_ms() - t0));
    p = putkv(p, " left=", (ulong)(left < 0 ? 0 : left)); *p++ = '\n'; emit(p);
    return 0;
}
__attribute__((naked)) void _start(void) { __asm__ volatile("mov r0, sp\n bl main_c\n mov r7, #1\n svc 0"); }
'''


# ---------------------------------------------------------------- utilidades locales
class ErrorLocal(Exception):
    pass


class SinCamara(Exception):
    pass


class NoCuadra(Exception):
    pass


def say(linea: str = "") -> None:
    print(linea, flush=True)
    TRANSCRIPCION.append(linea)


def paso(titulo: str) -> None:
    """Encabezado numerado; la numeración no salta aunque un modo omita pasos."""
    PASO[0] += 1
    say(f"{PASO[0]}) {titulo}")


def segmentos_ptload(ruta: str) -> tuple[bytes, list[tuple[int, int, int]]]:
    """Devuelve el contenido y los PT_LOAD (offset, vaddr, filesz) de un ELF32 LE."""
    with open(ruta, "rb") as f:
        b = f.read()
    if b[:4] != b"\x7fELF" or b[4] != 1 or b[5] != 1:
        raise ErrorLocal(f"{ruta}: no es un ELF32 little-endian")
    e_phoff, = struct.unpack_from("<I", b, 0x1C)
    e_phentsize, e_phnum = struct.unpack_from("<HH", b, 0x2A)
    segs = []
    for i in range(e_phnum):
        o = e_phoff + i * e_phentsize
        e_type, e_off, e_va, _pa, e_filesz = struct.unpack_from("<5I", b, o)
        if e_type == 1:
            segs.append((e_off, e_va, e_filesz))
    if not segs:
        raise ErrorLocal(f"{ruta}: sin PT_LOAD")
    return b, segs


def ventana(b: bytes, segs: list[tuple[int, int, int]], va: int, n: int = 16) -> bytes:
    for off, vaddr, filesz in segs:
        if vaddr <= va < vaddr + filesz:
            fo = off + (va - vaddr)
            w = b[fo:fo + n]
            if len(w) != n:
                raise ErrorLocal(f"VA 0x{va:08x}: la ventana de {n} B sale del fichero")
            return w
    raise ErrorLocal(f"VA 0x{va:08x}: fuera de los PT_LOAD")


def md5(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def halfword(b: bytes) -> int:
    return b[0] | (b[1] << 8)


def rutas_libs() -> tuple[str, str]:
    return os.path.join(LIBDIR321, "libmpr.so"), os.path.join(LIBDIR321, "libObj.so")


def prepara_local() -> tuple[dict, list[tuple[int, int, int]], list[tuple[int, int, int]]]:
    """Valida libmpr/libObj locales y devuelve las ventanas esperadas de cada punto."""
    libmpr = os.path.join(LIBDIR321, "libmpr.so")
    if not os.path.isfile(libmpr):
        raise ErrorLocal(f"no existe {libmpr}")
    b, segs = segmentos_ptload(libmpr)
    sha = hashlib.sha256(b).hexdigest()
    say(f"libmpr   {libmpr}")
    say(f"         {len(b)} B  sha256 {sha}")
    if sha != LIBMPR_SHA256:
        raise ErrorLocal("libmpr.so local distinto del auditado (9a74a3bb…4c30): no se arma nada")
    say("         sha256 = el auditado (3.21 de fábrica)  OK")
    say("")
    say("puntos (VA del ELF de libmpr.so, base 0) y 16 B esperados en memoria:")
    say(f"  {'pto':<4} {'VA ELF':<10} {'instrucción':<25} md5(16 B)  bytes")
    ventanas = {}
    for p in PUNTOS_BASE + PUNTOS_LLAMADAS:
        w = ventana(b, segs, p.va)
        ventanas[p.clave] = w
        say(f"  {p.clave:<4} 0x{p.va:08X} {p.instr:<25} {md5(w)}  {w.hex(' ')}")
    libobj = os.path.join(LIBDIR321, "libObj.so")
    ob, osegs = segmentos_ptload(libobj)
    wobj = ventana(ob, osegs, 0x8E95B0)
    ventanas["OBJ"] = wobj
    say("")
    say(f"libObj   {len(ob)} B  sha256 {hashlib.sha256(ob).hexdigest()[:16]}…")
    say(f"  testigo  0x008E95B0 (ObjPlayerCore::PlayMovieCmp) md5 {md5(wobj)}  {wobj.hex(' ')}")
    if os.path.isfile(LIBOBJ_CFW):
        cb, csegs = segmentos_ptload(LIBOBJ_CFW)
        cw = ventana(cb, csegs, 0x8E95B0)
        say(f"  el libObj del CFW 3.93 tiene los mismos 16 B ahí: {'sí' if cw == wobj else 'NO'} "
            "(prueba la base, no la variante)")
    return ventanas, segs, osegs


def compila_helper() -> bytes:
    """Compila el binario auxiliar ARM estático con la receta de tools/camera-ptrace/build.sh."""
    src = os.path.join("/tmp", "filmpb1bp.c")
    dst = os.path.join("/tmp", "filmpb1bp")
    with open(src, "w") as f:
        f.write(HELPER_C)
    cmd = ["clang", "--target=arm-linux-gnueabi", "-march=armv7-a", "-marm", "-Os",
           "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-nostdlib", "-static",
           "-fuse-ld=lld", "-Wl,--no-dynamic-linker", "-Wl,--strip-all",
           "-Wl,-z,noseparate-code", "-Wall", "-Wextra", src, "-o", dst]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise ErrorLocal("clang no compiló el binario auxiliar:\n" + (r.stderr or r.stdout)[-1500:])
    with open(dst, "rb") as f:
        data = f.read()
    if data[:4] != b"\x7fELF" or struct.unpack_from("<H", data, 0x12)[0] != 40:
        raise ErrorLocal("el binario auxiliar no es un ELF ARM (e_machine != 40)")
    say(f"  binario auxiliar /tmp/filmpb1bp: {len(data)} B, ELF32 ARM estático, sha256 {hashlib.sha256(data).hexdigest()[:16]}…")
    return data


# ---------------------------------------------------------------- cámara
class Camara:
    """Telnet de la cámara. `nivel`: verify (solo lectura) | dry-run (imprime) | run (envía todo)."""

    LECTURA = ("cat", "ls", "chroot", "dd", "rm", "pgrep", "pidof")
    simulada = False

    def __init__(self, host: str, nivel: str):
        self.host, self.nivel = host, nivel
        self.enviados: list[str] = []

    def prueba(self) -> None:
        try:
            socket.create_connection((self.host, 23), timeout=3.0).close()
        except OSError as e:
            raise SinCamara(f"{self.host}:23 ({e.__class__.__name__})") from None

    def mem(self, pid: int, addr: int, n: int = 16) -> bytes:
        """n bytes de /proc/PID/mem con dd + hd de toybox (el busybox no trae od/hexdump)."""
        self.lee(f"dd if=/proc/{pid}/mem bs=1 skip={addr} count={n} of=/android/dev/fpb1 2>/dev/null", timeout=30)
        out = self.lee("chroot /android /system/bin/hd /dev/fpb1", timeout=30)
        self.lee("rm -f /android/dev/fpb1")
        datos = bytearray()
        for ln in out.splitlines():
            partes = ln.replace(":", " ").split()
            if partes and len(partes[0]) >= 8 and all(c in "0123456789abcdef" for c in partes[0]):
                datos += bytes(int(x, 16) for x in partes[1:17] if len(x) == 2)
        if len(datos) < n:
            raise SinCamara(f"lectura corta en 0x{addr:08x} ({len(datos)} B)")
        return bytes(datos[:n])

    def lee(self, cmd: str, timeout: float = 25.0) -> str:
        if self.nivel == "verify" and cmd.split()[0] not in self.LECTURA:
            raise ErrorLocal(f"--verify no debe ejecutar «{cmd}»")
        return run(self.host, [cmd], timeout=timeout)[0]

    def escribe(self, cmd: str, timeout: float = 30.0) -> str:
        self.enviados.append(cmd)
        if self.nivel == "run":
            return run(self.host, [cmd], timeout=timeout)[0]
        say(f"    [{self.nivel}: no se envía] {cmd[:160]}{'…' if len(cmd) > 160 else ''}")
        return ""


class CamaraSimulada(Camara):
    """Cámara de mentira para probar el kit entero sin cámara: mapas de un volcado real y bytes de
    los .so locales. Comprueba la aritmética base+VA y los hashes, no ejecuta nada."""

    def __init__(self, ruta_maps: str, libs: dict[str, tuple[bytes, list[tuple[int, int, int]]]]):
        super().__init__("simulado", "dry-run")
        with open(ruta_maps) as f:
            self.maps_txt = f.read()
        self.filas = interpreta_maps(self.maps_txt)
        self.libs = libs
        self.tids = [143, 144, 145, 146]
        self.log_forzado = ""

    simulada = True

    def prueba(self) -> None:
        pass

    def escribe(self, cmd: str, timeout: float = 0) -> str:
        self.enviados.append(cmd)
        say(f"   [simulado: no se envía] {cmd[:110]}{'…' if len(cmd) > 110 else ''}")
        return ""

    def lee(self, cmd: str, timeout: float = 0) -> str:
        if cmd.startswith("chroot /android /system/bin/pidof"):
            return "143\n"
        if cmd.startswith("cat /proc/"):
            return self.maps_txt
        if cmd.startswith("ls /proc/"):
            return "\n".join(str(t) for t in self.tids)
        if cmd.startswith("cat " + LOG_REMOTO):
            return self.log_forzado
        raise ErrorLocal(f"simulador: orden no prevista «{cmd}»")

    def mem(self, pid: int, addr: int, n: int = 16) -> bytes:
        for ini, fin, off, ruta in self.filas:
            if ini <= addr < fin:
                for nombre, (b, _segs) in self.libs.items():
                    if ruta.endswith("/" + nombre):
                        fo = off + (addr - ini)
                        return b[fo:fo + n]
        raise NoCuadra(f"simulado: 0x{addr:08x} fuera de los mapeos de los .so del volcado")


def pid_de_im(cam: Camara) -> int:
    pruebas = (
        ("chroot /android /system/bin/pidof im.elf", r"(?<![\d.])(\d{1,6})(?![\d.])", "pidof (toybox)"),
        ("ls -l /proc/*/exe 2>/dev/null", r"/proc/(\d+)/exe -> .*im\.elf", "ls -l /proc/*/exe"),
    )
    for cmd, patron, nombre in pruebas:
        out = cam.lee(cmd)
        m = re.findall(patron, out)
        if m:
            say(f"   PID de im.elf = {m[0]}  (por {nombre})")
            return int(m[0])
        say(f"   {nombre}: sin resultado")
    raise SinCamara("no se encontró el proceso im.elf (¿Tweak sin telnet root?)")


def maps_de(cam: Camara, pid: int) -> list[tuple[int, int, int, str]]:
    return interpreta_maps(cam.lee(f"cat /proc/{pid}/maps", timeout=30))


def interpreta_maps(txt: str) -> list[tuple[int, int, int, str]]:
    filas = []
    for ln in txt.splitlines():
        m = re.match(r"([0-9a-f]{8})-([0-9a-f]{8})\s+(\S{4})\s+([0-9a-f]+)\s+\S+\s+\d+\s*(.*)$", ln)
        if m:
            filas.append((int(m.group(1), 16), int(m.group(2), 16), int(m.group(4), 16), m.group(5).strip()))
    if not filas:
        raise SinCamara("mapas sin líneas legibles")
    return filas


def mapeos_de(filas, nombre: str) -> list[tuple[int, int, int]]:
    """(inicio, fin, offset de fichero) de cada mapeo del fichero pedido."""
    return [(s, e, off) for s, e, off, ruta in filas if ruta.endswith("/" + nombre)]


def candidatos(va: int, segs, mapeos) -> list[int]:
    """Direcciones de ejecución posibles de una VA del ELF para los mapeos dados (off de fichero)."""
    out = []
    for off, vaddr, filesz in segs:
        if not (vaddr <= va < vaddr + filesz):
            continue
        f_va = off + (va - vaddr)
        for inicio, fin, m_off in mapeos:
            if m_off <= f_va < m_off + (fin - inicio):
                out.append(inicio + (f_va - m_off))
    return out


def lee_mem(cam: Camara, pid: int, addr: int, n: int = 16) -> bytes:
    """n bytes de /proc/PID/mem (método del transporte; la cámara simulada lo sustituye)."""
    return cam.mem(pid, addr, n)


def resuelve(cam: Camara, pid: int, filas, lib: str, segs, puntos, ventanas) -> tuple[int, dict, dict]:
    """Base del mapeo y dirección de ejecución de cada punto, comprobando 16 B contra el .so local."""
    mapeos = mapeos_de(filas, lib)
    if not mapeos:
        raise NoCuadra(f"{lib} no aparece en /proc/{pid}/maps")
    # La base es la dirección de ejecución de la VA 0 del ELF (los mapeos de datos no la comparten
    # tal cual porque el cargador alinea p_offset y p_vaddr por página).
    cand0 = candidatos(0, segs, mapeos)
    base = cand0[0] if cand0 else mapeos[0][0] - mapeos[0][2]
    say(f"   {lib}: base 0x{base:08x}  ({len(mapeos)} mapeos, el de código en 0x{mapeos[0][0]:08x})")
    direcciones, vistos = {}, {}
    for p in puntos:
        cands = candidatos(p.va, segs, mapeos)
        if not cands:
            raise NoCuadra(f"{p.clave}: VA 0x{p.va:08x} sin mapeo que la contenga")
        for c in cands:
            datos = lee_mem(cam, pid, c)
            if datos == ventanas[p.clave]:
                direcciones[p.clave], vistos[p.clave] = c, datos
                break
            vistos.setdefault("fallo_" + p.clave, datos)
        if p.clave not in direcciones:
            malo = vistos.get("fallo_" + p.clave, b"")
            raise NoCuadra(f"{p.clave} 0x{p.va:08x}: candidatos {[hex(c) for c in cands]} no cuadran "
                           f"con los 16 B locales; en cámara se leyó {malo.hex(' ')}")
    return base, direcciones, vistos


def tabula(puntos, direcciones, vistos, ventanas) -> None:
    say(f"   {'pto':<4} {'VA ELF':<11} {'ejecución':<11} 16 B en cámara                    md5 cam    md5 local  ¿igual?")
    for p in puntos:
        d, v = direcciones[p.clave], vistos[p.clave]
        say(f"   {p.clave:<4} 0x{p.va:08X}  0x{d:08X}  {v.hex(' ')}  {md5(v)}  {md5(ventanas[p.clave])}  "
            f"{'SÍ' if v == ventanas[p.clave] else 'NO'}")


def hilos(cam: Camara, pid: int) -> list[int]:
    out = cam.lee(f"ls /proc/{pid}/task")
    tids = sorted({int(x) for x in re.findall(r"\b(\d{1,6})\b", out)} - {pid})
    lista = [pid] + tids
    if len(lista) > 255:
        say(f"   aviso: {len(lista)} hilos; se trazan los 127 primeros")
        lista = lista[:255]
    return lista


def _adb() -> str:
    """adb del sistema o el de ~/.local (el de apt no está instalado en este host)."""
    for c in (os.environ.get("ADB", ""), shutil.which("adb") or "",
              os.path.expanduser("~/.local/platform-tools/adb")):
        if c and os.access(c, os.X_OK):
            return c
    return ""


def sube_helper(cam: Camara, datos: bytes) -> None:
    if cam.simulada:
        say(f"   [simulado] se subirían {len(datos)} B en {(len(datos) + 95) // 96} trozos de 96 B")
        return
    adb = _adb()
    if adb:
        r = subprocess.run([adb, "-s", f"{cam.host}:5555", "push", "/tmp/filmpb1bp",
                            "/data/local/tmp/filmpb1bp"], capture_output=True, text=True, check=False)
        if r.returncode == 0:
            cam.escribe(f"cp /android/data/local/tmp/filmpb1bp {HELPER_REMOTO}; chmod 755 {HELPER_REMOTO}")
            say(f"   auxiliar subido por adb push → cp a {HELPER_REMOTO} ({len(datos)} B)")
            return
        say(f"   adb push no sirvió ({r.stderr.strip()[:80]}); se sube por telnet")
    cam.escribe(f": > {HELPER_REMOTO}")
    for i in range(0, len(datos), 96):
        esc = "".join(f"\\0{b:03o}" for b in datos[i:i + 96])
        cam.escribe(f"echo -ne '{esc}' >> {HELPER_REMOTO}")
    cam.escribe(f"chmod 755 {HELPER_REMOTO}")
    ls = cam.lee(f"ls -l {HELPER_REMOTO}")
    if str(len(datos)) not in ls:
        raise ErrorLocal(f"el binario auxiliar no llegó entero: {ls.strip()!r}")
    local = hashlib.md5(datos).hexdigest()
    md5_cam = cam.lee(f"/bin/busybox md5sum {HELPER_REMOTO} 2>/dev/null")
    if local in md5_cam:
        say(f"   auxiliar en {HELPER_REMOTO}: {len(datos)} B, md5 {local} coincide  OK")
    else:
        say(f"   auxiliar en {HELPER_REMOTO}: {len(datos)} B (md5 NO_VERIFICADO: busybox sin md5sum; "
            "el tamaño sí cuadra)")


def restaura_y_verifica(cam: Camara, pid: int, puntos, direcciones, ventanas) -> bool:
    say("")
    paso("estado del código en memoria tras la traza")
    sano = True
    for p in puntos:
        d = direcciones[p.clave]
        try:
            ahora = lee_mem(cam, pid, d)
        except SinCamara as err_lectura:
            say(f"   {p.clave:<4} 0x{d:08X} no se pudo leer ({err_lectura}) → ¿im.elf cambió de PID?")
            sano = False
            continue
        if ahora == ventanas[p.clave]:
            say(f"   {p.clave:<4} 0x{d:08X} intacto")
            continue
        sano = False
        say(f"   {p.clave:<4} 0x{d:08X} ALTERADO {ahora.hex(' ')} ≠ {ventanas[p.clave].hex(' ')} → se reescribe")
        esc = "".join(f"\\0{b:03o}" for b in ventanas[p.clave])
        cam.escribe(f"echo -ne '{esc}' | dd of=/proc/{pid}/mem bs=1 seek={d} conv=notrunc 2>/dev/null")
        ahora = lee_mem(cam, pid, d)
        say(f"   {p.clave:<4} 0x{d:08X} tras reescribir: {'OK' if ahora == ventanas[p.clave] else 'SIGUE MAL'}")
    return sano


def parsea_eventos(salida: str, puntos) -> tuple[list[dict], list[str]]:
    evs, notas = [], []
    for ln in salida.splitlines():
        t = ln.strip()
        m = re.match(r"H\s+(.*)$", t)
        if m:
            kv = dict(re.findall(r"(\w+)=(0x[0-9a-f]+)", m.group(1)))
            i = int(kv.get("i", "0xff"), 16)
            if i >= len(puntos) or not {"ms", "tid", "pc", "lr", "r0", "r1", "left"} <= kv.keys():
                notas.append(f"X evento incompleto: {t}")
                continue
            evs.append({**kv, "i": i, "punto": puntos[i], "ms": int(kv["ms"], 16)})
        elif t.startswith(("A ", "X ", "R ", "E ")):
            notas.append(t)
    return evs, notas


def interpreta(
    evs: list[dict], notas: list[str], n_puntos: int, base: int, restaurado: bool
) -> tuple[str, str, int]:
    armado = any(re.fullmatch(rf"A ms=0x0 armados=0x{n_puntos:x} hilos=0x[1-9a-f][0-9a-f]* pid=0x[0-9a-f]+",
                              nota) for nota in notas)
    restantes = n_puntos - len(evs)
    fin = any(re.fullmatch(rf"E ms=0x[0-9a-f]+ left=0x{restantes:x}", nota) for nota in notas)
    errores = any(n.startswith("X ") or n.startswith("R ") and " FALLA " in n for n in notas)
    if not armado or not fin or not restaurado or errores:
        return ("CAPTURA INCOMPLETA",
                "Requiere armado completo, cierre coherente y restauración verificada.", COD_INCONCLUSA)
    if not evs:
        return ("SIN GOLPES",
                "No se registraron golpes durante la ventana de captura.",
                COD_SIN_GOLPE)
    claves = [e["punto"].clave for e in evs]
    orden = " → ".join(claves)
    if "A" in claves:
        return ("GUARDA A · capacidades/«dsm»  ⇒ H1 (estado de arranque, WBI/nflasha5)",
                (f"orden de impacto: {orden}. El 0x1A es el de la guarda A: una capacidad exigida por el "
                "bitmap [core+0xDB8] está deshabilitada. Contrastar con «Recuperar BD imág.» y con el "
                "3.21 oficial (E2/E3 del informe de auditoría)."), COD_OK)
    if "B" in claves:
        return ("GUARDA B · contenido no soportado  ⇒ H2 (contenido / base de datos de imágenes)",
                (f"orden de impacto: {orden}. El 0x1A es el de «Detect UnSupported Content»: el contenido "
                "no está soportado para la entidad (catálogo/entrada de la tarjeta). Contrastar con "
                "«Recuperar BD imág.» antes de tocar el firmware."), COD_OK)
    t = next((e for e in evs if e["punto"].clave == "T"), None)
    if t is not None:
        llamada = (int(t["lr"], 16) & ~1) - base - 4
        if int(t["r0"], 16) == 0x1C00001A and llamada in LLAMADAS_CONOCIDAS:
            origen = "MOTOR" if llamada == 0x437CFC else "PRECONDICIÓN"
            return (origen, f"{LLAMADAS_CONOCIDAS[llamada]} entró al traductor con 0x1C00001A.", COD_OK)
    if "E" in claves:
        return ("MANEJADOR EJECUTADO", f"Orden de impacto: {orden}. Origen del 0x1A pendiente.", COD_INCONCLUSA)
    if t is not None and int(t["r0"], 16) == 0:
        return ("TRADUCCIÓN DE UN ÉXITO", "El traductor recibió r0=0.", COD_INCONCLUSA)
    return ("ORIGEN SIN CONFIRMAR", f"Orden de impacto: {orden}.", COD_INCONCLUSA)


# ---------------------------------------------------------------- modos
def ejecuta(args) -> int:
    say("FILM-PB-1 · kit de captura: cuál de los tres productores de MPR::ER_FAILED (0x1A) dispara")
    modo = "--verify (solo mapas y hashes)" if args.verify else \
        "--dry-run (todo menos escribir en la cámara)" if args.dry_run else "traza real"
    say(f"modo: {modo}   host: {args.host}   ventana armada: {args.secs} s")
    say("")

    paso("comprobación local de los .so auditados")
    ventanas, mpr_segs, obj_segs = prepara_local()
    activos = tuple(PUNTOS_BASE) + (tuple(PUNTOS_LLAMADAS) if args.callsites else ())
    say("")
    say("   qué mide cada punto:")
    for p in activos:
        say(f"     {p.clave:<4} 0x{p.va:08X}  {p.mide}")

    datos_helper = b""
    if not args.verify:
        say("")
        paso("binario auxiliar (se compila aquí; solo se sube en la traza real)")
        say("   receta de tools/camera-ptrace/build.sh, extendida de trazar syscalls a plantar UDF 0xde00")
        datos_helper = compila_helper()

    say("")
    paso("cámara")
    cam: Camara
    if args.simular:
        mpr_p, obj_p = rutas_libs()
        bm, sm = segmentos_ptload(mpr_p)
        bo, so = segmentos_ptload(obj_p)
        cam = CamaraSimulada(args.simular, {"libmpr.so": (bm, sm), "libObj.so": (bo, so)})
        say(f"   MODO SIMULADO: mapas de {args.simular} + bytes de los .so locales; sin red y sin cámara")
    else:
        cam = Camara(args.host, "verify" if args.verify else "dry-run" if args.dry_run else "run")
    try:
        cam.prueba()
    except SinCamara as e:
        say(f"   cámara no accesible: {e}")
        say("")
        say("   el kit queda completo y probado en seco. Para armar hace falta:")
        say("     · la cámara encendida, con el Tweak que abre telnet root en el 23")
        say("     · su IP en --host (o A6000_HOST); el proyecto la ha visto en 192.168.1.29/30")
        say("     · que /proc/PID/mem sea legible como root (lo fue el 17-11-2026: traza T1)")
        return COD_SIN_CAMARA
    say("   simulado: no se usa la red" if cam.simulada else f"   telnet {args.host}:23 contesta  OK")

    pid = args.pid or pid_de_im(cam)
    filas = maps_de(cam, pid)
    say(f"   /proc/{pid}/maps: {len(filas)} líneas")

    base_mpr, dir_mpr, vis_mpr = resuelve(cam, pid, filas, "libmpr.so", mpr_segs, activos, ventanas)
    tabula(activos, dir_mpr, vis_mpr, ventanas)
    p_obj = Punto("OBJ", 0x8E95B0, "…", "ObjPlayerCore::PlayMovieCmp (testigo: la base de libObj)")
    base_obj, dir_obj, vis_obj = resuelve(cam, pid, filas, "libObj.so", obj_segs, (p_obj,), ventanas)
    tabula((p_obj,), dir_obj, vis_obj, ventanas)
    if args.verify:
        say("")
        say(f"VERIFICADO: bases de esta sesión libmpr=0x{base_mpr:08x} libObj=0x{base_obj:08x} y 16 B por "
            "punto idénticos a los .so locales; no se ha trazado ni escrito código.")
        return COD_OK

    if isinstance(cam, CamaraSimulada) and args.simular_hit:
        claves = [p.clave for p in activos]
        i = claves.index(args.simular_hit) if args.simular_hit in claves else -1
        lr = base_mpr + {"A": 0x437D0E, "B": 0x437C40, "T": 0x437D00}.get(args.simular_hit, 0x437D0E)
        restantes = len(activos) - int(i >= 0)
        cam.log_forzado = f"A ms=0x0 armados=0x{len(activos):x} hilos=0x{len(cam.tids):x} pid=0x8f\n"
        if i >= 0:
            cam.log_forzado += (f"H ms=0x21 i=0x{i:x} tid=0x8f pc=0x{dir_mpr[activos[i].clave]:x} "
                                f"r0=0x1c00001a r1=0x0 r2=0x0 r3=0x1c000000 lr=0x{lr:x} "
                                f"left=0x{restantes:x}\n")
        cam.log_forzado += f"E ms=0x22 left=0x{restantes:x}\n"
        say("   ENSAYO: el golpe que se simula es el del punto " + (args.simular_hit or "ninguno"))

    tids = hilos(cam, pid)
    puntos_arg = ",".join(
        f"0x{dir_mpr[p.clave]:08x}:0x{halfword(ventanas[p.clave]):04x}" for p in activos)
    say("")
    paso(f"traza: {len(activos)} puntos, {len(tids)} hilos de im.elf")
    if args.dry_run:
        say("   se subiría el auxiliar en 96 B por `echo -ne` y se ejecutaría:")
        say(f"     {HELPER_REMOTO} {args.secs} {pid} {','.join(str(t) for t in tids[:8])}"
            f"{',…' if len(tids) > 8 else ''} {puntos_arg} > {LOG_REMOTO} 2>&1 &")
        say("   y al terminar: cat del registro, comprobación de los 16 B y `rm -f` del auxiliar y del registro.")
        say(f"   (bases de esta sesión: libmpr=0x{base_mpr:08x} libObj=0x{base_obj:08x})")
        say("")
        say("DRY-RUN: nada escrito en la cámara; el kit (binario + direcciones verificadas) está listo.")
        return COD_OK

    sube_helper(cam, datos_helper)
    orden = (f"{HELPER_REMOTO} {args.secs} {pid} {','.join(str(t) for t in tids)} {puntos_arg} "
             f"> {LOG_REMOTO} 2>&1 &")
    say(f"   se lanza: {orden}")
    say("   AHORA reproduce el vídeo en la cámara (el clip del error «No se puede visualizar»).")
    cam.escribe(orden)
    vistos, salida, acumuladas = 0, "", []
    t0 = time.time()
    while time.time() - t0 < args.secs + 20:
        time.sleep(1.0)
        txt = cam.lee(f"cat {LOG_REMOTO} 2>/dev/null")
        lineas = [ln for ln in txt.splitlines() if ln.strip()]
        for ln in lineas[vistos:]:
            say("   > " + ln)
            acumuladas.append(ln)
        vistos = max(vistos, len(lineas))
        salida = "\n".join(acumuladas)   # acumula: una lectura vacía al final no borra los golpes
        if any(ln.startswith("E ") for ln in lineas):
            break
    cam.escribe("killall filmpb1bp 2>/dev/null")
    sano = restaura_y_verifica(cam, pid, activos, dir_mpr, ventanas)
    cam.escribe(f"rm -f {HELPER_REMOTO}")   # el registro se conserva para releerlo

    evs, notas = parsea_eventos(salida, activos)
    veredicto, detalle, codigo = interpreta(evs, notas, len(activos), base_mpr, sano)
    say("")
    say("resultado")
    say(f"   productores que dispararon: {[ev['punto'].clave for ev in evs] or 'ninguno'}")
    if evs:
        for n, ev in enumerate(evs, 1):
            say(f"   {n}º  {ev['punto'].clave}  0x{ev['punto'].va:08X}  ms={ev['ms']} tid={ev['tid']} "
                f"pc={ev['pc']} lr={ev['lr']} r0={ev['r0']} r1={ev['r1']}")
    for nota in notas:
        say(f"   nota {nota}")
    say(f"   código en memoria: {'verificado' if sano else 'integridad sin verificar'}")
    say("")
    say(f"VEREDICTO: {veredicto}")
    say(f"   {detalle}")
    return codigo


def autotest() -> int:
    """Comprueba los resultados y la calidad de la captura con líneas del auxiliar."""
    say("autotest de la interpretación (líneas sintéticas del auxiliar)")
    casos = [
        ("A", "H ms=0x1f i=0x0 tid=0x8f pc=0x70f5c0a r0=0x1 r1=0x2 r2=0x3 r3=0x4 lr=0x437d0e left=0x2",
         "GUARDA A"),
        ("B", "H ms=0x20 i=0x1 tid=0x8f pc=0x70f5c3c r0=0x1 r1=0x2 r2=0x3 r3=0x4 lr=0x437c40 left=0x1",
         "GUARDA B"),
        ("T", ("H ms=0x21 i=0x2 tid=0x8f pc=0x70f611b0 r0=0x1c00001a r1=0x0 r2=0x0 r3=0x1c000000 "
               "lr=0x437d00 left=0x0"), "MOTOR"),
        ("T", ("H ms=0x21 i=0x2 tid=0x8f pc=0x728d1b0 r0=0x0 r1=0x0 r2=0x0 r3=0x0 "
               "lr=0x6fb4197 left=0x2"), "TRADUCCIÓN DE UN ÉXITO"),
    ]
    activos = tuple(PUNTOS_BASE)
    mal = 0
    cabecera = "A ms=0x0 armados=0x3 hilos=0x1 pid=0x8f"
    for clave, linea, esperado in casos:
        evs, notas = parsea_eventos(f"{cabecera}\n{linea}\nE ms=0x30 left=0x2", activos)
        veredicto, detalle, codigo = interpreta(evs, notas, len(activos), 0, True)
        esperado_codigo = COD_INCONCLUSA if esperado == "TRADUCCIÓN DE UN ÉXITO" else COD_OK
        ok = esperado in veredicto and codigo == esperado_codigo and evs and evs[0]["punto"].clave == clave
        say(f"   {clave}: {'OK' if ok else 'MAL'}  {veredicto}")
        if clave == "T":
            say(f"       {detalle}")
        mal += 0 if ok else 1
    fin = "E ms=0x30 left=0x3"
    for etiqueta, log, limpio, esperado_codigo in (
        ("sin golpes", f"{cabecera}\n{fin}", True, COD_SIN_GOLPE),
        ("sin armar", f"{cabecera.replace('armados=0x3', 'armados=0x0')}\nE ms=0xe left=0x0", True, COD_INCONCLUSA),
        ("sin cierre", f"{cabecera}\n{casos[-1][1]}", True, COD_INCONCLUSA),
        ("restauración no verificada", f"{cabecera}\n{fin}", False, COD_INCONCLUSA),
        ("evento truncado", f"{cabecera}\nH ms=0x21\n{fin}", True, COD_INCONCLUSA),
    ):
        evs, notas = parsea_eventos(log, activos)
        veredicto, _, codigo = interpreta(evs, notas, len(activos), 0, limpio)
        ok = codigo == esperado_codigo
        say(f"   {etiqueta}: {'OK' if ok else 'MAL'}  {veredicto}")
        mal += 0 if ok else 1
    say(f"autotest: {'OK' if not mal else f'{mal} fallo(s)'}")
    return COD_OK if not mal else COD_LOCAL


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="FILM-PB-1: traza de los tres productores de MPR::ER_FAILED (0x1A).")
    ap.add_argument("--verify", action="store_true", help="solo mapas y hashes de 16 bytes (no escribe)")
    ap.add_argument("--dry-run", action="store_true", help="todo menos escribir en la cámara")
    ap.add_argument("--host", default=os.environ.get("A6000_HOST", "192.168.1.30"))
    ap.add_argument("--pid", type=int, default=0, help="PID de im.elf (por defecto se busca)")
    ap.add_argument("--secs", type=int, default=30, help="segundos con los puntos armados (defecto 30)")
    ap.add_argument("--callsites", action="store_true", help="añade 0x437C7E y 0x437CFC (llamadas a 0x7111B0)")
    ap.add_argument("--simular", default="", metavar="MAPS",
                    help="prueba sin cámara con un volcado de /proc/PID/maps (implica --dry-run)")
    ap.add_argument("--simular-hit", default="", choices=("", "A", "B", "T", "none"),
                    help="con --simular: ensaya la traza completa con un golpe en ese punto")
    ap.add_argument("--autotest", action="store_true", help="prueba las reglas de interpretación sin cámara")
    ap.add_argument("--log", default="", help="guarda la transcripción en este fichero")
    args = ap.parse_args(argv)
    if args.autotest:
        return autotest()
    if args.verify and args.dry_run:
        raise ErrorLocal("--verify y --dry-run son excluyentes")
    if args.simular:
        args.dry_run = True
        if args.simular_hit:
            args.dry_run = False          # ensayo de la traza completa, contra la cámara simulada
    codigo = ejecuta(args)
    if args.log:
        with open(args.log, "w") as f:
            f.write("\n".join(TRANSCRIPCION) + "\n")
        say(f"(transcripción en {args.log})")
    return codigo


TRANSCRIPCION: list[str] = []
PASO = [0]


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except NoCuadra as e:
        say(f"\nERROR (mapas/hashes): {e}")
        sys.exit(COD_HASH)
    except (ErrorLocal, SinCamara) as e:
        say(f"\nERROR: {e}")
        sys.exit(COD_LOCAL)
    except Exception as e:                          # noqa: BLE001  nunca una traza hacia arriba
        say(f"\nERROR interno: {e.__class__.__name__}: {e}")
        sys.exit(COD_LOCAL)
