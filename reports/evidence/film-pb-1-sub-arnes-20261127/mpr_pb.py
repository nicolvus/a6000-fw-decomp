"""Escenario mínimo FILM-PB-1: el manejador de PlayMovie de libmpr 3.21 ejecutado en Unicorn.

Carga `libmpr.so` de fábrica (VA del ELF = dirección de ejecución, base 0), arma el `FeaCore`,
la entidad «dsm», la cola y el `PlayMovieCtrl` falsos, y ejecuta el **código real** de la
cadena: `FeaIf::PlayMovie` (`0x44EE9C`, que construye el mensaje de 0x8C) y el manejador
`0x437BC0` con sus guardas (`0x447A1E`, `0x447F26`, `0x447DA8`), el traductor de error
(`0x7111B0`) y el arranque del motor (`0x307F54`).

Se sustituyen, parcheando su primera instrucción, solo las hojas que en la cámara dependen de
estado de arranque que aquí no existe:

  - `0x66D0C8` (entidad por media) → devuelve la entidad falsa;
  - los logs `0x712938`/`0x712960`, el reinicio `0x447DC8` y el refresco `0x447EE2`;
  - `0x12111C` (copia del `RSMPoint` al marco del manejador, veneer ARM) y `0x711A4C`
    (conversión del `EntryId`);
  - el retorno del motor `MoviePlayerIf::PbStart` (`0x307F54`).

El parcheo —y no hooks que salten la llamada— es deliberado: Unicorn 2.1.4 pierde el estado del
bloque `IT` de Thumb cuando un hook reescribe `PC`, y el manejador lo usa. La finalización
(`vtable+0x1C` del core) se captura llamando a una dirección sin mapear.
"""
from __future__ import annotations

import struct
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
LIB = RAIZ / ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
              "nflasha15_unpacked_unpacked/lib/libmpr.so")

# --- VA del ELF de libmpr.so 3.21 (base 0) --------------------------------------------
MANEJADOR = 0x437BC0      # FUN_00437BC0: case 0x4000001D del despachador (llamada en 0x42A37A)
FEAF_PLAY = 0x44EE9C      # FeaIf::PlayMovie (símbolo .dynsym); arma el mensaje de 0x8C
GUARDA_A = 0x447A1E       # capacidades («Pb Disable!! ref) dsm get»)
GUARDA_B = 0x447F26       # contenido («Detect UnSupported Content »)
PREVIO = 0x447DA8         # comprobación previa al motor
REANUDA = 0x447EE2        # «ResumeInfo is updated»
ENTIDAD = 0x66D0C8        # FUN_0066D0C8(media) -> entidad (llamada desde 0x447810)
MOTOR = 0x307F54          # MoviePlayerIf::PbStart
UL_TIMEO = 0x7111B0       # traductor del código interno de error a código MPR
REINICIO = 0x447DC8
LOG_STR = 0x712938
LOG_STATUS = 0x712960
MEMCPY = 0x12111C         # copia del RSMPoint (entra en un veneer ARM)
MSG_PUT = 0x4296D0        # copia el mensaje al anillo de la cola
MENSAGE_ID = 0x4000001D
TAM_MSG = 0x8C

# --- andamio --------------------------------------------------------------------------
CORE, ENT = 0x20000000, 0x20001000
VT_CORE, VT_ENT = 0x20002000, 0x20002080
STUBS = 0x20003000
PILA, PILA_TOP = 0x30000000, 0x30008000
FIN, RETORNO = 0x50000010, 0x50000000      # destinos sin mapear: finalización y retorno
BUF_MSG = 0x40000000

C_VT, C_LOG, C_ENTRY, C_ESTADO, C_MASCARA, C_MEDIA, C_MOTOR = 0x0, 0x8, 0x1EC, 0x1F0, 0xDB8, 0xDC0, 0xD94


def ret(mu, va: int, valor: int) -> None:
    """Escribe en `va` un retorno inmediato: r0 = valor ; bx lr."""
    if valor <= 0xFF:
        mu.mem_write(va, bytes([valor & 0xFF, 0x20, 0x70, 0x47]))
    else:
        mu.mem_write(va, struct.pack("<HHI", 0x4800, 0x4770, valor))  # ldr r0,[pc,#0] ; bx lr ; .word


class Cargador:
    """Carga mínima de un .so ELF32 ARM: PT_LOAD + JUMP_SLOT/GLOB_DAT/ABS32 (base 0)."""

    def __init__(self, ruta: Path) -> None:
        self.d = ruta.read_bytes()
        d = self.d
        phnum = struct.unpack_from("<H", d, 0x2C)[0]
        phoff = struct.unpack_from("<I", d, 0x1C)[0]
        self.segs = []
        for i in range(phnum):
            t, off, va, _pa, fsz, msz, _fl, _al = struct.unpack_from("<8I", d, phoff + i * 32)
            if t == 1:
                self.segs.append((off, va, fsz, msz))
        shoff = struct.unpack_from("<I", d, 0x20)[0]
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", d, 0x2E)
        crudas = [struct.unpack_from("<10I", d, shoff + i * shentsize) for i in range(shnum)]
        base_nombres = crudas[shstrndx][4]
        self.sec = {}
        for s in crudas:
            o = base_nombres + s[0]
            self.sec[d[o:d.index(b"\0", o)].decode()] = (s[3], s[4], s[5])
        self.syms = []
        _va, off, size = self.sec[".dynsym"]
        for i in range(size // 16):
            self.syms.append(struct.unpack_from("<I", d, off + i * 16 + 4)[0])

    def aplica(self, mu) -> int:
        for off, va, fsz, msz in self.segs:
            ini = va & ~0xFFF
            mu.mem_map(ini, ((va + msz - ini) + 0xFFF) & ~0xFFF)
            mu.mem_write(va, self.d[off:off + fsz])
        n = 0
        for nombre in (".rel.plt", ".rel.dyn"):
            if nombre not in self.sec:
                continue
            _va, off, size = self.sec[nombre]
            for i in range(size // 8):
                destino, info = struct.unpack_from("<II", self.d, off + i * 8)
                tipo = info & 0xFF
                if tipo in (21, 22):                   # GLOB_DAT / JUMP_SLOT (símbolo definido)
                    mu.mem_write(destino, struct.pack("<I", self.syms[info >> 8]))
                    n += 1
                elif tipo == 2:                        # ABS32: símbolo + sumando
                    sumando = struct.unpack("<I", mu.mem_read(destino, 4))[0]
                    mu.mem_write(destino, struct.pack("<I", self.syms[info >> 8] + sumando))
                    n += 1
                # R_ARM_RELATIVE (128 507): con base 0 el valor del fichero ya es el bueno
        return n


def _r1(mu):
    from unicorn.arm_const import UC_ARM_REG_R1
    return mu.reg_read(UC_ARM_REG_R1)


def _r2(mu):
    from unicorn.arm_const import UC_ARM_REG_R2
    return mu.reg_read(UC_ARM_REG_R2)


def _r3(mu):
    from unicorn.arm_const import UC_ARM_REG_R3
    return mu.reg_read(UC_ARM_REG_R3)


def escenario(*, estado: int = 5, capacidad: int = 1, contenido: int = 1, motor: int = 0,
              fallo_motor: int = 0x1A, mascara: int = 1, media: int = 2, ctrl: bool = True,
              mensaje: bytes | None = None, traza: list | None = None,
              traductor_real: bool = True) -> dict:
    """Ejecuta el manejador con las respuestas indicadas y devuelve lo observado.

    estado: `[core+0x1F0]` (5 en la cámara). mascara: `[core+0xDB8]` que lee la guarda A.
    capacidad / contenido: lo que devuelven `vtable+0x60/+0x5C` y `vtable+0x58` de la entidad.
    motor: lo que devuelve `PbStart` (0 = éxito); el traductor `0x7111B0` se ejecuta de verdad
    sobre ese valor (0x1C00001A -> 0x1A).
    """
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1,
                                   UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP)

    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for base in (CORE, PILA, BUF_MSG):
        mu.mem_map(base, 0x10000)
    visto = {"ramas": [], "completado": None, "pc_error": None}

    def registra(nombre):
        def h(uc, addr, size, _):
            visto["ramas"].append(nombre)
        return h

    mu.hook_add(UC_HOOK_CODE, registra("guarda A"), begin=GUARDA_A, end=GUARDA_A)
    mu.hook_add(UC_HOOK_CODE, registra("guarda B"), begin=GUARDA_B, end=GUARDA_B)
    if traza is not None:
        mu.hook_add(UC_HOOK_CODE, lambda uc, addr, size, _: traza.append(addr))

    visto["relocs"] = Cargador(LIB).aplica(mu)

    # retornos sustitutos
    ret(mu, ENTIDAD, ENT)
    for va in (LOG_STR, LOG_STATUS, REINICIO, REANUDA, PREVIO, MEMCPY):
        ret(mu, va, 0)
    ret(mu, MOTOR, motor)
    if not traductor_real:
        ret(mu, UL_TIMEO, fallo_motor)
    ret(mu, STUBS, capacidad)            # vtable+0x60 / vtable+0x5C (capacidades)
    ret(mu, STUBS + 8, contenido)        # vtable+0x58 (contenido soportado)

    # objetos falsos: core, entidad y sus tablas
    mu.mem_write(VT_CORE, b"\0" * 0x1C + struct.pack("<I", FIN))
    mu.mem_write(VT_ENT, b"\0" * 0x60)
    for desp, valor in ((0x58, STUBS + 9), (0x5C, STUBS + 1), (0x60, STUBS + 1), (0xB4, STUBS + 1)):
        mu.mem_write(VT_ENT + desp, struct.pack("<I", valor))
    mu.mem_write(ENT, struct.pack("<I", VT_ENT))
    mu.mem_write(CORE + C_VT, struct.pack("<I", VT_CORE))
    mu.mem_write(CORE + C_LOG, struct.pack("<I", 0x20004000))
    for desp, valor in ((C_ENTRY, 0x00010001), (C_ESTADO, estado), (C_MASCARA, mascara),
                        (C_MEDIA, media), (C_MOTOR, 0x20005000)):
        mu.mem_write(CORE + desp, struct.pack("<I", valor))

    # mensaje de 0x8C en la forma que arma FeaIf::PlayMovie (se puede pasar el real)
    if mensaje is None:
        msg = bytearray(TAM_MSG)
        struct.pack_into("<III", msg, 0, 0x2A, 0x00010001, 0x00020002)
        msg[0x1C] = 1
        msg[0x20:0x30] = bytes(range(0x10))
        msg[0x60] = 1
        msg[0x64] = 1
        mu.mem_write(BUF_MSG, bytes(msg))
        mensaje = bytes(msg)
    else:
        mu.mem_write(BUF_MSG, mensaje)

    # argumentos del manejador tal como los pone el despachador (0x42A354-0x42A37E)
    mu.mem_write(PILA_TOP - 0x20, struct.pack("<4I", BUF_MSG + 0xC, BUF_MSG + 0x10,
                                              BUF_MSG + 0x14, BUF_MSG + 0x18))
    mu.mem_write(PILA_TOP - 0x10, struct.pack("<2I", BUF_MSG + 0x20, BUF_MSG + 0x64 if ctrl else 0))
    for reg, valor in ((UC_ARM_REG_R0, CORE), (UC_ARM_REG_R1, 0x00010001),
                       (UC_ARM_REG_R2, int.from_bytes(mensaje[4:8], "little")),
                       (UC_ARM_REG_R3, int.from_bytes(mensaje[8:12], "little")),
                       (UC_ARM_REG_SP, PILA_TOP - 0x20), (UC_ARM_REG_LR, RETORNO)):
        mu.reg_write(reg, valor)

    try:
        mu.emu_start(MANEJADOR | 1, 0, count=200000)
    except Exception:
        pc = mu.reg_read(UC_ARM_REG_PC) & ~1
        if pc == FIN:
            visto["completado"] = {"orden": _r1(mu), "tam": _r3(mu),
                                   "status": struct.unpack("<I", mu.mem_read(_r2(mu), 4))[0]}
        elif pc != RETORNO:
            visto["pc_error"] = pc
    return visto


def traduce(codigo: int) -> int:
    """Ejecuta el traductor real FUN_007211B0(r0) y devuelve su resultado (tabla de errores MPR)."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP

    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for base in (STUBS, PILA):
        mu.mem_map(base, 0x10000)
    Cargador(LIB).aplica(mu)
    mu.reg_write(UC_ARM_REG_R0, codigo)
    mu.reg_write(UC_ARM_REG_SP, PILA_TOP)
    mu.reg_write(UC_ARM_REG_LR, RETORNO)
    try:
        mu.emu_start(UL_TIMEO | 1, RETORNO, count=20000)
    except Exception:
        pass
    return mu.reg_read(UC_ARM_REG_R0)


def mensaje_real(*, group_typ: int = 1, ident: int = 0x00010001, ctrl: bool = True) -> bytes:
    """Ejecuta FeaIf::PlayMovie (0x44EE9C) real y devuelve el mensaje de 0x8C bytes que encola."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1,
                                   UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP)

    FEA, COLA, VT_COLA, BUF = 0x20006000, 0x20006100, 0x20006200, 0x40010000
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for base, tam in ((CORE, 0x10000), (PILA, 0x10000), (BUF, 0x1000)):
        mu.mem_map(base, tam)
    Cargador(LIB).aplica(mu)
    for va in (LOG_STR, LOG_STATUS, REINICIO, REANUDA, PREVIO, MEMCPY, 0x7128F4, 0x68323C,
               0x6831B8, 0x683118, 0x7168E4, 0x449D84, 0x4395B0, 0x711A4C):
        ret(mu, va, 0)
    ret(mu, STUBS, 1)                       # vtable+0x18 de la cola: acepta la orden
    ret(mu, STUBS + 8, 1)                   # vtable+0x20 de la cola: «push» aceptado
    mu.mem_write(VT_COLA, b"\0" * 0x18 + struct.pack("<II", STUBS + 1, STUBS + 9))
    mu.mem_write(COLA, struct.pack("<I", VT_COLA) + b"\0" * 0x9C)
    mu.mem_write(FEA, b"\0" * 0x98)
    mu.mem_write(FEA + 4, struct.pack("<I", COLA))
    mu.mem_write(FEA + 0x94, struct.pack("<I", 0x20004000))
    mu.mem_write(PILA_TOP - 0x20, struct.pack("<4I", 0x00020002, 0x00030003,
                                              BUF + 0x200, BUF + 0x240 if ctrl else 0))
    mu.mem_write(BUF + 0x200, bytes(range(0x40)))            # RSMPoint de prueba
    mu.mem_write(BUF + 0x240, struct.pack("<8I", 1, 0x11, 0x22, 0x33, 0, 0, 0, 0)
                 + b"\0" * 0x20)                            # PlayMovieCtrl de prueba
    visto = {"msg": None}

    def captura(uc, addr, size, _):
        visto["msg"] = bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1), TAM_MSG))
        uc.reg_write(UC_ARM_REG_R0, 0)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) & ~1)
    mu.hook_add(UC_HOOK_CODE, captura, begin=MSG_PUT, end=MSG_PUT)

    for reg, valor in ((UC_ARM_REG_R0, FEA), (UC_ARM_REG_R1, 0x0000002A),
                       (UC_ARM_REG_R2, group_typ), (UC_ARM_REG_R3, ident),
                       (UC_ARM_REG_SP, PILA_TOP - 0x20), (UC_ARM_REG_LR, RETORNO)):
        mu.reg_write(reg, valor)
    try:
        mu.emu_start(FEAF_PLAY | 1, 0, count=50000)
    except Exception:
        pass
    if visto["msg"] is None:
        raise RuntimeError("FeaIf::PlayMovie no llegó a 0x4296D0 (PC=%#x)" % mu.reg_read(UC_ARM_REG_PC))
    return visto["msg"]


if __name__ == "__main__":
    for nombre, kw in (("estado≠5", {"estado": 0}), ("guarda A", {"capacidad": 0}),
                       ("guarda B", {"contenido": 0}), ("motor falla", {"motor": 0x1C00001A}),
                       ("todo bien", {})):
        r = escenario(**kw)
        print(f"{nombre:12} ramas={r['ramas']} final={r['completado']} err={r['pc_error']}")
