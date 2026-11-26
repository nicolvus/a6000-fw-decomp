#!/usr/bin/env python3
"""Arreglo del sector FBM 0x31 en la cámara desde el PC, por telnet, con vuelta atrás.

Aplica el arreglo medido en el arnés: `FBM EWBDFD 4 3 0` (escribe en la entrada (userID 4,
mediaID 3) de la tabla 0x9D23FC la función dummy 0x2B5184, que sólo hace log y `return 0`) y
después `FBM InitB 6 3` (crea el sector 0x31 = idx 10 de la tabla 0xA3699C).
NO se usa `FBM LTC 1`: es un test de fábrica y sus escritores (0x2B5724/0x2B5658) meten texto de
prueba («MS »/«HDD » + «packData») en la página de datos base (reports/grabacion-bd-fbm-20261126.md §17).
Las dos líneas no van por tty: se depositan en el anillo en memoria del monitor EX-PC del
proceso MPR (X = u32 en libmpr+0xA4FD88; [X]=A lectura, [X+4]=B escritura, datos en X+0x10,
0x400 B, terminador CR, capacidad útil 0x3FF).

Informes: reports/film-pb-1-sub-consola-sector31-20261126.md (la cadena que crea)
          reports/film-pb-1-sub-consola-fbm-anillo-20261127.md (formato del anillo)
Runbook:  reports/film-pb-1-sector31-runbook-20261126.md

uso:
  python3 scripts/film_pb1_sector31.py --verifica                    # SÓLO lectura (por defecto)
  python3 scripts/film_pb1_sector31.py --aplica                      # en seco: comprueba y enseña el plan
  python3 scripts/film_pb1_sector31.py --aplica --escribe            # aplica de verdad
  python3 scripts/film_pb1_sector31.py --restaurar FICHERO --escribe # vuelta atrás (dd a nflasha4)

Sin `--escribe` no se escribe nada en la cámara: ni volcado, ni /tmp/ptcall, ni el anillo.
Si falla cualquier comprobación previa, tampoco. Código de salida: 0 OK, 1 NO/abortado, 2 uso.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from camera_telnet import run as telnet

REPO = Path(__file__).resolve().parent.parent
PTCALL_LOCAL = REPO / "tools/camera-ptrace/ptcall"

# libmpr.so: offsets del ELF (base = primer mapeo r-xp de /proc/PID/maps)
OFF_DESCRIPTOR = 0xA4FD88   # u32 -> X (puntero al área del anillo)
OFF_TABLA = 0xA3699C        # tabla de sectores: 30 entradas de 0x14 B
N_ENTRADAS = 30
TAM_ENTRADA = 0x14
IDX_SECTOR31 = 10           # 0x9D23FC[13] u04/m3/ft031/om6 -> sector 0x31
SECTOR = 0x31
RING_HDR = 0x10
RING_BUF = 0x400
RING_CAP = 0x3FF            # un hueco siempre libre

# Las dos líneas que se depositan, en orden. `LTC 1` NO: es un test de fábrica que escribe datos de
# prueba en la página de datos base (reports/grabacion-bd-fbm-20261126.md §17-18).
LINEA_1 = "FBM EWBDFD 4 3 0"   # 0x2B1DEC con el dummy 0x2B5184 para (userID 4, mediaID 3)
LINEA_2 = "FBM InitB 6 3"      # BackupMgr::InitBackupData(OM 6, media 3) -> sector 0x31 (idx 10)

NFLASHA4_BYTES = 10485760   # 10 MiB; un volcado de otra medida no sirve de rollback
MARGEN_SD_KB = 20480        # 20 MiB libres en la tarjeta antes de volcar
DESTINOS_SD = ("/mnt/sdcard", "/android/mnt/sdcard", "/mnt/sd", "/media/sdcard", "/mnt/extcard")


class Fallo(Exception):
    """Comprobación previa que no pasa: se aborta sin escribir."""


# ---------------------------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------------------------
def u32(mem: dict[int, int], addr: int) -> int:
    return sum(mem.get(addr + i, 0) << (8 * i) for i in range(4))


def lee_peek(texto: str) -> dict[int, int]:
    """Memoria de la salida de `ptcall peek`: líneas `0x82df9000: 00 40 88 8f`."""
    mem: dict[int, int] = {}
    for m in re.finditer(r"(?m)^\s*(0x[0-9a-fA-F]{8}):\s*((?:[0-9a-fA-F]{2}\s*)*)$", texto):
        base = int(m.group(1), 16)
        for i, b in enumerate(m.group(2).split()):
            mem[base + i] = int(b, 16)
    if not mem:
        raise Fallo(f"no pude interpretar la salida de peek: {texto.strip()[:300]}")
    return mem


def entrada(mem: dict[int, int], base: int, idx: int) -> dict[str, int]:
    e = base + idx * TAM_ENTRADA
    return {"idx": idx, "sector": u32(mem, e), "handle": u32(mem, e + 4),
            "valido": u32(mem, e + 8), "om": u32(mem, e + 0xC)}


def fmt(e: dict[str, int]) -> str:
    return (f"idx {e['idx']:2d}: sector=0x{e['sector']:02x} handle={e['handle']} "
            f"valido={e['valido']} OM={e['om']}")


class Camara:
    """Telnet del Tweak (root, sin login). Cada orden abre y cierra su propia sesión."""

    def __init__(self, host: str, port: int = 23, ptcall: str = "/tmp/ptcall", timeout: float = 30.0):
        self.host, self.port, self.timeout = host, port, timeout
        self.ptcall = ptcall

    def sh(self, cmd: str, timeout: float | None = None) -> str:
        return telnet(self.host, [cmd], port=self.port, timeout=timeout or self.timeout)[0]

    # -- identidad ---------------------------------------------------------------------------
    def uid(self) -> str:
        """uid efectivo: `id -u` y, si el busybox no trae el applet, /proc/self/status."""
        cmd = ("id -u 2>/dev/null || busybox id -u 2>/dev/null || "
               "{ grep -q '^Uid:.*0' /proc/self/status && echo 0 || echo ?; }")
        out = self.sh(cmd).strip().split()
        return out[-1] if out else "?"

    def herramientas(self) -> str:
        cmd = ("for c in pidof awk sed df dd chmod md5sum grep cat sync; do "
               "e=$(type $c 2>/dev/null); [ -n \"$e\" ] || e=NO; echo -n \"$c=$e  \"; done")
        return self.sh(cmd).strip()

    def pid(self) -> int:
        cmd = ('P=$(pidof im.elf 2>/dev/null); [ -n "$P" ] && echo "$P" || '
               'for d in /proc/[0-9]*; do grep -qa im.elf $d/cmdline 2>/dev/null && '
               '{ echo ${d#/proc/}; break; }; done')
        out = self.sh(cmd)
        pids = re.findall(r"\b\d+\b", out)
        if not pids:
            raise Fallo(f"no encuentro im.elf (¿MPR arrancado?): {out.strip()[:200]}")
        return int(pids[0])

    def base_libmpr(self, pid: int) -> int:
        maps = f"/proc/{pid}/maps"
        cmd = (f"awk '/libmpr\\.so/ && /r-xp/ {{print $1; exit}}' {maps} 2>/dev/null; "
               f"grep -aF libmpr.so {maps} 2>/dev/null | grep -aF r-xp | cut -d' ' -f1 | cut -d- -f1")
        m = re.search(r"\b([0-9a-fA-F]{8})\b", self.sh(cmd))
        if not m:
            raise Fallo(f"libmpr.so no está mapeado en {pid} (¿root?): falta /proc/{pid}/maps")
        return int(m.group(1), 16)

    def tiene_ptcall(self) -> bool:
        return self.sh(f"[ -x {self.ptcall} ] && echo si || echo no").strip().endswith("si")

    # -- memoria -----------------------------------------------------------------------------
    def peek(self, pid: int, addr: int, n: int) -> dict[int, int]:
        out = self.sh(f"{self.ptcall} {pid} 0 peek {addr:#x} {n:#x}")
        if "ATTACH" in out or "desconocido" in out or "uso:" in out:
            raise Fallo(f"ptcall peek falló en {addr:#x}: {out.strip()[:300]}")
        return lee_peek(out)

    def poke(self, pid: int, addr: int, datos: bytes) -> None:
        hexs = " ".join(f"{b:02x}" for b in datos)
        out = self.sh(f"{self.ptcall} {pid} 0 poke {addr:#x} {hexs}")
        if "poke ok" not in out:
            raise Fallo(f"ptcall poke falló en {addr:#x}: {out.strip()[:300]}")

    # -- anillo ------------------------------------------------------------------------------
    def anillo(self, pid: int, base: int) -> tuple[int, int, int]:
        """(X, A, B) del anillo del monitor EX-PC."""
        d = base + OFF_DESCRIPTOR
        x = u32(self.peek(pid, d, 4), d)
        if x == 0:
            raise Fallo(f"el descriptor {d:#x} vale 0: el monitor EX-PC no ha arrancado")
        hdr = self.peek(pid, x, 8)
        a, b = u32(hdr, x), u32(hdr, x + 4)
        if not (0 <= a < RING_BUF and 0 <= b < RING_BUF):
            raise Fallo(f"cabecera del anillo imposible: A={a} B={b} en X={x:#x}")
        return x, a, b

    def deposita(self, pid: int, base: int, linea: str, espera: float) -> tuple[int, int]:
        """Deposita `linea` + CR y espera al monitor. Devuelve (A_antes, A_despues)."""
        x, a, b = self.anillo(pid, base)
        datos = linea.encode() + b"\r"
        libres = (a - b - 1) & RING_CAP
        if libres < len(datos):
            raise Fallo(f"no caben {len(datos)} B en el anillo (libres {libres})")
        tramo1 = min(RING_BUF - b, len(datos))
        self.poke(pid, x + RING_HDR + b, datos[:tramo1])          # primero los bytes
        if tramo1 < len(datos):
            self.poke(pid, x + RING_HDR, datos[tramo1:])
        nb = (b + len(datos)) & RING_CAP
        self.poke(pid, x + 4, struct.pack("<I", nb))              # y B de una vez
        t0 = time.time()
        while time.time() - t0 < espera:
            time.sleep(1.0)
            if self.anillo(pid, base)[1] in (nb, nb - RING_BUF):
                return a, nb
        a2 = self.anillo(pid, base)[1]
        raise Fallo(f"el monitor no consumió «{linea}» (A={a2}, esperaba {nb}); no se sigue")

    def tabla(self, pid: int, base: int) -> dict[int, int]:
        return self.peek(pid, base + OFF_TABLA, N_ENTRADAS * TAM_ENTRADA)

    # -- tarjeta -----------------------------------------------------------------------------
    def destino_sd(self, preferido: str = "") -> tuple[str, int]:
        """(directorio, KiB libres) de la tarjeta, o Fallo si no hay uno escribible con sitio."""
        candidatos = (preferido,) if preferido else DESTINOS_SD
        cmd = "; ".join(f"[ -w {d} ] && {{ df -k {d} 2>/dev/null || df {d}; }}" for d in candidatos)
        lineas = self.sh(cmd).splitlines()
        if preferido and not any(l.split()[-1:] == [preferido] for l in lineas if l.split()):
            print(f"  AVISO: no puedo leer el espacio libre con df; --destino {preferido} se da por bueno")
            return preferido, -1
        for linea in lineas:
            campos = linea.split()
            if len(campos) < 6:
                continue
            try:
                libres = int(campos[3])
            except ValueError:
                continue
            if campos[-1] in candidatos and libres >= MARGEN_SD_KB:
                return campos[-1], libres
        raise Fallo(f"ningún destino escribible con {MARGEN_SD_KB} KiB libres en {list(candidatos)}"
                    " (¿tarjeta montada? ¿--destino?)")

    # -- subida de ptcall --------------------------------------------------------------------
    def sube_ptcall(self, local: Path) -> None:
        datos = local.read_bytes()
        if len(datos) > 64 * 1024:
            raise Fallo(f"{local} es demasiado grande para subirlo por telnet ({len(datos)} B)")
        self.sh(f": > {self.ptcall}")
        trozos = [datos[i:i + 96] for i in range(0, len(datos), 96)]
        for lote in range(0, len(trozos), 10):                    # 10 trozos por sesión
            cmds = [f"echo -ne '{''.join(f'\\0{b:03o}' for b in t)}' >> {self.ptcall}"
                    for t in trozos[lote:lote + 10]]
            telnet(self.host, cmds, port=self.port, timeout=self.timeout)
        self.sh(f"chmod 755 {self.ptcall}")
        out = self.sh(f"ls -l {self.ptcall}; busybox md5sum {self.ptcall} 2>/dev/null || md5sum {self.ptcall}")
        md5 = hashlib.md5(datos).hexdigest()
        if str(len(datos)) not in out or md5 not in out:
            raise Fallo(f"la subida de ptcall no cuadra (esperaba {len(datos)} B / {md5}): "
                        f"{out.strip()[-300:]}")
        print(f"  ptcall subido: {self.ptcall} ({len(datos)} B, md5 {md5})")


# ---------------------------------------------------------------------------------------------
# lectura del estado y veredicto
# ---------------------------------------------------------------------------------------------
def estado(cam: Camara, pid: int, base: int, etiqueta: str) -> dict:
    mem = cam.tabla(pid, base)
    idx10 = entrada(mem, base + OFF_TABLA, IDX_SECTOR31)
    con_handle = [entrada(mem, base + OFF_TABLA, i) for i in range(N_ENTRADAS)
                  if u32(mem, base + OFF_TABLA + i * TAM_ENTRADA + 4) != 0]
    print(f"  {etiqueta}: {fmt(idx10)}")
    print(f"  {etiqueta}: con handle != 0: {len(con_handle)}/{N_ENTRADAS}"
          + (" -> " + ", ".join(f"idx {e['idx']}(0x{e['sector']:02x} h{e['handle']})" for e in con_handle)
             if con_handle else " (ninguna)"))
    return {"idx10": idx10, "con_handle": con_handle}


def existe(e: dict) -> bool:
    return e["handle"] != 0 and e["valido"] == 1


def resumen(e: dict) -> str:
    return (f"sector=0x{e['sector']:02x} handle={e['handle']} valido={e['valido']} OM={e['om']}  "
            f"-> {'EXISTE' if existe(e) else 'NO existe'}")


def veredicto(antes: dict, despues: dict | None) -> bool:
    e = (despues or antes)["idx10"]
    if e["sector"] not in (SECTOR, 0):
        print(f"  AVISO: el idx {IDX_SECTOR31} no es el sector 0x{SECTOR:02x} (dice 0x{e['sector']:02x})")
    print()
    print(f"  ANTES  : {resumen(antes['idx10'])}   ({len(antes['con_handle'])}/30 con handle)")
    if despues is not None:
        print(f"  DESPUÉS: {resumen(despues['idx10'])}   ({len(despues['con_handle'])}/30 con handle)")
    print()
    ok = existe(e)
    if despues is None:
        print(f"  VEREDICTO: sector 0x{SECTOR:02x} " + ("EXISTE" if ok
                                                       else "NO EXISTE -> falta --aplica --escribe"))
    else:
        print(f"  VEREDICTO: {'OK' if ok else 'NO'} — sector 0x{SECTOR:02x} en el idx {IDX_SECTOR31} "
              + (f"con handle={e['handle']} y valido={e['valido']}" if ok
                 else "sin handle: el arreglo no ha cuajado (mira el log de FBM del MPR)"))
    print()
    return ok


# ---------------------------------------------------------------------------------------------
# modos
# ---------------------------------------------------------------------------------------------
def mats(cam: Camara) -> tuple[int, int]:
    """(PID de im.elf, base de libmpr) con las comprobaciones de root y de mapa."""
    if cam.uid() != "0":
        raise Fallo("el telnet no da root (id -u != 0)")
    pid = cam.pid()
    base = cam.base_libmpr(pid)
    print(f"  PID im.elf={pid}  libmpr base={base:#010x}")
    return pid, base


def pasa_verifica(cam: Camara, a: argparse.Namespace) -> int:
    print(f"== alcance y proceso ({a.host}:{a.port}) ==")
    print(f"  herramientas: {cam.herramientas()}")
    pid, base = mats(cam)
    if not cam.tiene_ptcall():
        raise Fallo(f"{a.ptcall} no está en la cámara: pásalo con scripts/camera_push_file.py "
                    "o deja que lo suba --aplica --escribe")
    x, va, vb = cam.anillo(pid, base)
    print(f"== anillo del monitor (sólo lectura) ==\n  X={x:#010x}  A={va}  B={vb}  "
          f"libres={(va - vb - 1) & RING_CAP} de {RING_CAP}")
    print("== tabla de sectores (base+0xA3699C, 30 x 0x14) ==")
    return 0 if veredicto(estado(cam, pid, base, "ahora"), None) else 1


def pasa_aplica(cam: Camara, a: argparse.Namespace) -> int:
    escribir = a.escribe
    print(f"== 1. alcance y proceso ({a.host}:{a.port}) ==")
    print(f"  telnet ok, uid={cam.uid()}  herramientas: {cam.herramientas()}")
    pid, base = mats(cam)
    pt_ok = cam.tiene_ptcall()
    print(f"  {a.ptcall}: " + ("ya está" if pt_ok else "no está (se subiría en la fase de escritura)"))
    if pt_ok:
        x, va, vb = cam.anillo(pid, base)
        print(f"== 2. anillo del monitor (sólo lectura) ==\n  X={x:#010x}  A={va}  B={vb}  "
              f"libres={(va - vb - 1) & RING_CAP} de {RING_CAP}")
        print("== 3. tabla de sectores: antes ==")
        antes = estado(cam, pid, base, "antes")
    else:
        antes = {"idx10": {"idx": IDX_SECTOR31, "sector": 0, "handle": 0, "valido": 0, "om": 0},
                 "con_handle": []}

    print("== 4. comprobaciones de escritura ==")
    origen = a.origen_volcado
    tam = cam.sh(f"ls -l {origen} 2>&1").strip()
    if "No such" in tam or "no such" in tam or not tam:
        raise Fallo(f"no existe {origen} (¿es la cámara? ¿--origen-volcado?)")
    print(f"  origen del volcado: {tam}")
    destino, libres_kb = cam.destino_sd(a.destino)
    print(f"  tarjeta: {destino} " + (f"con {libres_kb} KiB libres" if libres_kb >= 0 else "(espacio sin comprobar)")
          + f" (necesito {MARGEN_SD_KB} KiB)")
    sello = time.strftime("%Y%m%d-%H%M%S")
    fichero = f"{destino}/nflasha4-{sello}.bin"

    if not escribir:
        print("\n== PLAN (en seco: NO se ha escrito nada) ==")
        print(f"  1. subir {PTCALL_LOCAL.name} ({PTCALL_LOCAL.stat().st_size if PTCALL_LOCAL.exists() else '?'} B)"
              f" -> {a.ptcall}" + ("" if pt_ok else "  [pendiente]"))
        print(f"  2. dd if={origen} of={fichero} bs=1024      # rollback, {NFLASHA4_BYTES} B")
        print(f"  3. depositar en el anillo «FBM EWBDFD 4 3 0» (espera {a.espera:.0f} s)")
        print(f"  4. depositar en el anillo «FBM InitB 6 3» (espera {a.espera:.0f} s)")
        print(f"  5. releer el idx {IDX_SECTOR31} y dictar veredicto")
        print("  Añade --escribe para hacerlo de verdad.")
        return 1

    print(f"== 5. volcado de rollback -> {fichero} ==")
    out = cam.sh(f"type dd >/dev/null 2>&1 && dd if={origen} of={fichero} bs=1024 2>&1 "
                 f"|| cat {origen} > {fichero}; ls -l {fichero}", timeout=240)
    print("  " + out.strip().replace("\n", "\n  ")[-400:])
    tam_v = re.search(r"\s(\d{6,})\s", out)
    if not tam_v or int(tam_v.group(1)) != NFLASHA4_BYTES:
        raise Fallo(f"el volcado {fichero} no mide {NFLASHA4_BYTES} B: no sirve de rollback")
    md5 = cam.sh(f"busybox md5sum {fichero} 2>/dev/null || md5sum {fichero}").strip()
    print(f"  md5: {md5}")
    if not md5 or len(md5.split()[0]) != 32:
        raise Fallo(f"no pude comprobar el volcado {fichero}: no se escribe nada más")
    print(f"  vuelta atrás: dd if={fichero} of={origen} bs=1024   (y reiniciar el MPR)")

    if not pt_ok:
        print(f"== 6. subida de ptcall -> {a.ptcall} ==")
        if not PTCALL_LOCAL.exists():
            raise Fallo(f"falta {PTCALL_LOCAL}: compílalo con `sh tools/camera-ptrace/build.sh`")
        cam.sube_ptcall(PTCALL_LOCAL)
        x, va, vb = cam.anillo(pid, base)
        print(f"  anillo: X={x:#010x} A={va} B={vb} libres={(va - vb - 1) & RING_CAP}")
        print("== tabla de sectores: antes ==")
        antes = estado(cam, pid, base, "antes")

    print(f"== 7. línea 1: «{LINEA_1}» (dar función a (userID 4, mediaID 3) con el dummy 0x2B5184) ==")
    a0, a1 = cam.deposita(pid, base, LINEA_1, a.espera)
    print(f"  consumida por el monitor (A {a0} -> {a1})")
    time.sleep(a.espera)

    print(f"== 8. línea 2: «{LINEA_2}» (crear el sector 0x31: OM 6 = M2PS, media 3 = MS1) ==")
    a0, a1 = cam.deposita(pid, base, LINEA_2, a.espera)
    print(f"  consumida por el monitor (A {a0} -> {a1})")
    time.sleep(a.espera)

    if a.comprobar_persistencia:
        print("== 8-bis. «FBM WBI»: reconstruye la tabla desde el flash (que persista) ==")
        cam.deposita(pid, base, "FBM WBI", a.espera)
        time.sleep(a.espera)

    print("== 9. nueva lectura de la tabla ==")
    despues = estado(cam, pid, base, "después")
    if not veredicto(antes, despues):
        print("  Qué mirar: el log de FBM del MPR ([FBM] BackupMgr::InitBackupData…), que")
        print(f"  {origen} sea escribible y que la línea 1 se consumiera antes de la 2.")
        print(f"  Rollback en la tarjeta: {fichero}")
        return 1
    print("  Siguiente: plan de prueba (reports/film-pb-1-sector31-runbook-20261126.md §5).")
    return 0


def pasa_restaurar(cam: Camara, a: argparse.Namespace) -> int:
    fichero = a.restaurar
    print(f"== vuelta atrás: restaurar {fichero} sobre {a.origen_volcado} ==")
    print("  OJO: escribir nflasha4 a mano salta el asignador del FBS y su libro de bloques.")
    pid = cam.pid()
    print(f"  PID im.elf={pid} (sigue vivo: reinícialo DESPUÉS para que relea el flash)")
    tam = cam.sh(f"ls -l {fichero} 2>&1").strip()
    print(f"  fichero: {tam}")
    m = re.search(r"\s(\d{6,})\s", tam)
    if not m or int(m.group(1)) != NFLASHA4_BYTES:
        raise Fallo(f"{fichero} no mide {NFLASHA4_BYTES} B: no sirve como volcado")
    if not a.escribe:
        print(f"  (en seco) dd if={fichero} of={a.origen_volcado} bs=1024 && sync")
        print("  Añade --escribe para hacerlo de verdad.")
        return 1
    out = cam.sh(f"(type dd >/dev/null 2>&1 && dd if={fichero} of={a.origen_volcado} bs=1024 "
                 f"|| cat {fichero} > {a.origen_volcado}) 2>&1; sync; "
                 f"busybox md5sum {fichero} {a.origen_volcado} 2>/dev/null", timeout=300)
    print("  " + out.strip().replace("\n", "\n  ")[-600:])
    md5s = re.findall(r"\b([0-9a-f]{32})\b", out)
    ok = len(md5s) >= 2 and md5s[0] == md5s[1]
    print(f"  VEREDICTO: {'OK' if ok else 'NO'} — "
          + ("el dispositivo devuelve el mismo md5 que el fichero" if ok
             else "no pude confirmar md5 iguales; compruébalo a mano"))
    print("  Reinicia el MPR para que FlashLib relea la partición.")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Aplica y verifica el arreglo del sector FBM 0x31 "
                                             "por telnet, con vuelta atrás.",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--host", default=os.environ.get("A6000_HOST", "192.168.1.29"))
    p.add_argument("--port", type=int, default=int(os.environ.get("A6000_TELNET_PORT", "23")))
    modo = p.add_mutually_exclusive_group()
    modo.add_argument("--verifica", action="store_true", help="sólo lectura (por defecto)")
    modo.add_argument("--aplica", action="store_true", help="aplica el arreglo (en seco salvo --escribe)")
    modo.add_argument("--restaurar", metavar="FICHERO", help="vuelta atrás: dd del volcado a nflasha4")
    p.add_argument("--escribe", action="store_true", help="permiso explícito de escritura (por defecto: en seco)")
    p.add_argument("--ptcall", default="/tmp/ptcall", help="ruta de ptcall en la cámara (/tmp/ptcall)")
    p.add_argument("--origen-volcado", default="/dev/nflasha4", help="dispositivo a volcar (/dev/nflasha4)")
    p.add_argument("--destino", default="", help="directorio de la tarjeta (por defecto: se busca)")
    p.add_argument("--espera", type=float, default=3.0, help="segundos de espera por línea (3)")
    p.add_argument("--comprobar-persistencia", action="store_true",
                   help="tras el arreglo, FBM WBI (reconstruye la tabla desde el flash)")
    a = p.parse_args()

    cam = Camara(a.host, a.port, a.ptcall)
    try:
        try:
            cam.sh("echo listo", timeout=8)
        except OSError as e:
            raise Fallo(f"no hay telnet en {a.host}:{a.port} ({e}). ¿Cámara encendida, Tweak con "
                        "telnetd activo y en la misma red?")
        if a.restaurar:
            return pasa_restaurar(cam, a)
        if a.aplica:
            return pasa_aplica(cam, a)
        return pasa_verifica(cam, a)
    except Fallo as e:
        print(f"\nABORTADO (no se escribe nada): {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
