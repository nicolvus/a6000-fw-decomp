"""Carga y ejecución de los inicializadores estáticos (.init_array) de libObj.so en Unicorn.

Compara el `libObj.so` de fábrica (fw 3.21) con el parcheado del CFW 3.93 cargándolos con un
cargador ELF32 ARM propio (PT_LOAD + JUMP_SLOT/GLOB_DAT/ABS32; `R_ARM_RELATIVE` es no-op con
base 0) y ejecutando las 263 entradas de `.init_array` en orden, como hace el cargador de la
cámara.

Los símbolos **indefinidos** (1801: libc, libstdc++, libmpr y otras .so de Sony) se resuelven a
stubs propios, uno por símbolo: `movs r0,#0; bx lr` para funciones y `udf #0` + relleno para
objetos (si el código *ejecuta* uno, el fallo es inmediato y delata qué símbolo es). El andamio
no reproduce la cámara: mide si el código propio de libObj hace lo mismo en las dos versiones.

Se registran por entrada: retorno o fallo, número de escrituras, hash de las escrituras y si se
ejecutó alguna instrucción de los rangos .text parcheados. Al final se compara el segmento RW
completo y se listan los rangos de bytes distintos.

Uso:  python3 init_emu.py [--json SALIDA] [--per-entry]
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
ORIG = (RAIZ / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
        "nflasha15_unpacked_unpacked/lib/libObj.so")
PATCH = RAIZ / "build/cfw_func393/pp/files/lib/libObj.so"

STUB_FUN = 0x60000000        # stubs de funciones importadas (0x40 B por símbolo)
STUB_OBJ = 0x60200000        # objetos importados (0x40 B por símbolo)
HUECO = 0x40                 # bytes por símbolo: absorbe los sumandos de las ABS32 (vtable+8, …)
PILA = 0x70000000
PILA_TOP = 0x70020000
SENTINELA = 0x700F0000       # sin mapear: retorno normal de cada inicializador
RW_VA = 0xFD25A4             # segmento RW de libObj (VA y tamaño de los phdr)

# Rangos de .text distintos entre las dos versiones (fichero = VA, 26 rangos)
RANGOS_PARCHEADOS = (
    (0x4A784C, 0x4A7850), (0x4A7860, 0x4A7861), (0x4B4184, 0x4B4185), (0x4B42FA, 0x4B433A),
    (0x4B4390, 0x4B4394), (0x4B471C, 0x4B471D), (0x4B4722, 0x4B475E), (0x4B4774, 0x4B4775),
    (0x4B477A, 0x4B47C4), (0x4B73DE, 0x4B73DF), (0x4C0AE2, 0x4C0AE3), (0x4C0B0A, 0x4C0B0B),
    (0x4C0BE2, 0x4C0BE8), (0x4C0D6C, 0x4C0D70), (0x4C0E62, 0x4C0E66), (0x4C0EA2, 0x4C0EAA),
    (0x4DB4B6, 0x4DB4B7), (0x4DB4DE, 0x4DB4DF), (0x686DE6, 0x686DEB), (0x686DEC, 0x686DF4),
    (0x686DFA, 0x686E0E), (0x9B325E, 0x9B32BC), (0x9B32BD, 0x9B32C0), (0x9B36DE, 0x9B373E),
    (0x9B373F, 0x9B3740), (0x9B3741, 0x9B3744),
)


class Imagen:
    """Vista mínima de un .so ELF32 ARM preenlazado (VA del fichero = dirección de ejecución)."""

    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta
        self.d = ruta.read_bytes()
        d = self.d
        phoff = struct.unpack_from("<I", d, 0x1C)[0]
        phnum = struct.unpack_from("<H", d, 0x2C)[0]
        self.segs = []
        for i in range(phnum):
            t, off, va, _pa, fsz, msz, fl, _al = struct.unpack_from("<8I", d, phoff + i * 32)
            if t == 1:
                self.segs.append((off, va, fsz, msz, fl))
        shoff = struct.unpack_from("<I", d, 0x20)[0]
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", d, 0x2E)
        crudas = [struct.unpack_from("<10I", d, shoff + i * shentsize) for i in range(shnum)]
        nombres = d[crudas[shstrndx][4]:]
        self.sec = {}
        for s in crudas:
            o = s[0]
            self.sec[nombres[o:nombres.index(b"\0", o)].decode()] = (s[3], s[4], s[5])
        _va, off, size = self.sec[".dynsym"]
        str_off = self.sec[".dynstr"][1]
        self.syms = []
        for i in range(size // 16):
            nom, valor, _sz, info, _otro, shndx = struct.unpack_from("<IIIBBH", d, off + i * 16)
            e = d.index(b"\0", str_off + nom)
            self.syms.append({"valor": valor, "tipo": info & 0xF, "def": shndx != 0,
                              "nombre": d[str_off + nom:e].decode("latin1")})
        self._mapa = [(va, off, fsz) for off, va, fsz, _msz, _fl in self.segs]

    def entradas_init(self) -> list[int]:
        va, _off, size = self.sec[".init_array"]
        return list(struct.unpack("<%dI" % (size // 4), self.leer(va, size)))

    def leer(self, va: int, n: int) -> bytes:
        for va0, off, fsz in self._mapa:
            if va0 <= va < va0 + fsz:
                return self.d[off + va - va0:off + va - va0 + n]
        raise ValueError("VA fuera de PT_LOAD: %#x" % va)

    def relocs(self) -> list[tuple[int, int, int]]:
        """[(destino, tipo, idx)] de .rel.dyn y .rel.plt (lo mismo que leen DT_REL/DT_JMPREL)."""
        out = []
        for nombre in (".rel.dyn", ".rel.plt"):
            _va, off, size = self.sec[nombre]
            for i in range(size // 8):
                destino, info = struct.unpack_from("<II", self.d, off + i * 8)
                out.append((destino, info & 0xFF, info >> 8))
        return out


class Montaje:
    """Unicorn con la biblioteca cargada y los símbolos indefinidos resueltos a stubs."""

    def __init__(self, imagen: Imagen) -> None:
        from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc

        self.imagen = imagen
        self.mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.mu.mem_map(STUB_FUN, 0x200000)
        self.mu.mem_map(STUB_OBJ, 0x200000)
        self.mu.mem_map(PILA, 0x20000)
        for off, va, fsz, msz, _fl in imagen.segs:
            ini = va & ~0xFFF
            self.mu.mem_map(ini, ((va + msz - ini) + 0xFFF) & ~0xFFF)
            self.mu.mem_write(va, imagen.d[off:off + fsz])
        self.stub_nombre = {}
        self.n_relocs = 0
        self.n_imports = 0
        self._aplica_relocs()

    def _stub_de(self, idx: int) -> int:
        """Un hueco de 0x40 B por símbolo.

        FUNC: `movs r0,#0 ; bx lr` repetido → cualquier entrada (también símbolo+sumando, que es
        como se construyen los punteros a método) devuelve 0 en vez de caer en relleno.
        OBJETO: cada palabra apunta a un «return 0» → leer un slot de una vtable importada y
        llamarlo devuelve 0, en vez de saltar a la dirección 0.
        """
        s = self.imagen.syms[idx]
        if s["tipo"] == 2:                                    # STT_FUNC: Thumb (bit 0)
            base = STUB_FUN + self.n_imports * HUECO
            self.mu.mem_write(base, b"\x00\x20\x70\x47" * (HUECO // 4))
            direccion = base | 1
        else:                                                 # objeto/no tipo
            base = STUB_OBJ + self.n_imports * HUECO
            self.mu.mem_write(base, struct.pack("<I", STUB_FUN | 1) * (HUECO // 4))
            direccion = base
        self.stub_nombre[base] = s["nombre"]
        self.n_imports += 1
        return direccion

    def simbolo_en(self, direccion: int) -> str | None:
        return self.stub_nombre.get(direccion & ~1)

    def simbolo_mas_cercano(self, direccion: int) -> str | None:
        mejor = None
        for va in self.stub_nombre:
            if va <= direccion and (mejor is None or va > mejor):
                mejor = va
        return self.stub_nombre.get(mejor) if mejor is not None else None

    def _aplica_relocs(self) -> None:
        mu, imagen = self.mu, self.imagen
        cache: dict[int, int] = {}
        for destino, tipo, idx in imagen.relocs():
            if tipo == 23:                                    # R_ARM_RELATIVE: base 0 → no-op
                self.n_relocs += 1
                continue
            if idx == 0:
                continue
            s = imagen.syms[idx]
            if s["def"]:
                base = s["valor"]
            else:
                if idx not in cache:
                    cache[idx] = self._stub_de(idx)
                base = cache[idx]
            if tipo in (21, 22):                              # GLOB_DAT / JUMP_SLOT
                mu.mem_write(destino, struct.pack("<I", base))
            elif tipo == 2:                                   # ABS32: símbolo + sumando
                sumando = struct.unpack("<I", mu.mem_read(destino, 4))[0]
                mu.mem_write(destino, struct.pack("<I", (base + sumando) & 0xFFFFFFFF))
            else:
                raise ValueError("tipo de reloc %d sin soporte" % tipo)
            self.n_relocs += 1


def _en_rango_parchado(pc: int) -> bool:
    return any(a <= pc < b for a, b in RANGOS_PARCHEADOS)


def ejecuta(ruta: Path, *, max_insn: int = 2_000_000) -> dict:
    """Ejecuta `.init_array` en orden y devuelve el detalle por entrada y la imagen RW final."""
    import hashlib
    import time
    from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
    from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1,
                                   UC_ARM_REG_R2, UC_ARM_REG_SP)

    imagen = Imagen(ruta)
    entradas = imagen.entradas_init()
    t0 = time.time()
    montaje = Montaje(imagen)
    t_carga = time.time() - t0
    mu = montaje.mu
    estado = {"n": 0, "hash": 0, "parche": None, "llamadas": 0, "datos": None, "raro": None,
              "insn": 0}

    def h_escribe(_uc, _access, address, size, value, _u):
        estado["n"] += 1
        h = estado["hash"]
        for b in struct.pack("<III", address & 0xFFFFFFFF, size, value & 0xFFFFFFFF):
            h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
        estado["hash"] = h

    def h_codigo(_uc, address, _size, _u):
        estado["insn"] += 1
        if estado["parche"] is None and _en_rango_parchado(address):
            estado["parche"] = address

    def h_stub_fun(_uc, address, _size, _u):
        if (address & ~1) in montaje.stub_nombre:         # llamada al stub de un símbolo
            estado["llamadas"] += 1

    def h_stub_obj(uc, address, _size, _u):
        if (address & ~1) in montaje.stub_nombre:         # ejecutar un objeto importado: límite
            estado["datos"] = address
        uc.emu_stop()

    mu.hook_add(UC_HOOK_MEM_WRITE, h_escribe)
    mu.hook_add(UC_HOOK_CODE, h_codigo)
    mu.hook_add(UC_HOOK_CODE, h_stub_fun, begin=STUB_FUN, end=STUB_FUN + 0x200000 - 1)
    mu.hook_add(UC_HOOK_CODE, h_stub_obj, begin=STUB_OBJ, end=STUB_OBJ + 0x200000 - 1)

    detalle = []
    for i, entrada in enumerate(entradas):
        estado.update(n=0, hash=0, parche=None, llamadas=0, datos=None, raro=None, insn=0)
        mu.reg_write(UC_ARM_REG_SP, PILA_TOP)
        mu.reg_write(UC_ARM_REG_LR, SENTINELA)
        for reg in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2):
            mu.reg_write(reg, 0)
        fallo = None
        truncado = False
        try:
            mu.emu_start(entrada | 1, SENTINELA, count=max_insn)
            truncado = (mu.reg_read(UC_ARM_REG_PC) & ~1) != (SENTINELA & ~1)
        except Exception as exc:                              # noqa: BLE001
            pc = mu.reg_read(UC_ARM_REG_PC) & ~1
            if pc != (SENTINELA & ~1):
                fallo = {"pc": pc, "err": type(exc).__name__}
        datos, raro = estado["datos"], estado["raro"]
        if fallo:
            resultado, pc, simbolo = "fallo", fallo["pc"], montaje.simbolo_en(fallo["pc"])
        elif datos is not None:
            resultado, pc, simbolo = "import_datos", datos, montaje.simbolo_en(datos)
        elif raro is not None:
            resultado, pc, simbolo = "import_off", raro, montaje.simbolo_mas_cercano(raro)
        elif truncado:
            resultado, pc, simbolo = "truncado", None, None
        else:
            resultado, pc, simbolo = "ok", None, None
        detalle.append({
            "i": i, "va": entrada, "resultado": resultado, "pc": pc, "simbolo": simbolo,
            "escrituras": estado["n"], "hash": "%08x" % estado["hash"],
            "llamadas_import": estado["llamadas"], "instrucciones": estado["insn"],
            "pc_parcheado": estado["parche"]})

    rw = None
    for off, va, _fsz, msz, _fl in imagen.segs:
        if va == RW_VA:
            rw = hashlib.sha256(mu.mem_read(va, msz)).hexdigest()
            self_rw = bytes(mu.mem_read(va, msz))
    return {"ruta": str(ruta), "entradas": len(entradas), "relocs": montaje.n_relocs,
            "imports": montaje.n_imports, "t_carga": round(t_carga, 3),
            "t_total": round(time.time() - t0, 3), "rw_sha": rw, "rw": self_rw,
            "detalle": detalle}


def _imagen_rw(ruta: Path) -> bytes:
    """Segmento RW tal como queda *antes* de ejecutar nada (solo reubicaciones)."""
    from unicorn import UC_MODE_THUMB  # noqa: F401
    m = Montaje(Imagen(ruta))
    for off, va, _fsz, msz, _fl in m.imagen.segs:
        if va == RW_VA:
            return bytes(m.mu.mem_read(va, msz))
    raise ValueError("sin segmento RW")


def compara(*, con_ejecucion: bool = True) -> dict:
    """Compara las dos versiones: estático de .data.rel.ro y ejecución de .init_array."""
    a = ejecuta(ORIG) if con_ejecucion else None
    b = ejecuta(PATCH) if con_ejecucion else None
    rw_a = a["rw"] if a else _imagen_rw(ORIG)
    rw_b = b["rw"] if b else _imagen_rw(PATCH)
    n = min(len(rw_a), len(rw_b))
    rangos, i = [], 0
    while i < n:
        if rw_a[i] != rw_b[i]:
            j = i
            while j < n and rw_a[j] != rw_b[j]:
                j += 1
            rangos.append((RW_VA + i, j - i))
            i = j
        else:
            i += 1
    res = {"rangos_rw": rangos, "rw_iguales": rw_a == rw_b,
           "diferencias_init": []}
    if a and b:
        for x, y in zip(a["detalle"], b["detalle"]):
            if x != y:
                res["diferencias_init"].append({"orig": x, "patch": y})
        res["resumen"] = {
            "entradas": a["entradas"],
            "ok": sum(1 for x in a["detalle"] if x["resultado"] == "ok"),
            "fallo": sum(1 for x in a["detalle"] if x["resultado"] == "fallo"),
            "import_datos": sum(1 for x in a["detalle"] if x["resultado"] == "import_datos"),
            "import_off": sum(1 for x in a["detalle"] if x["resultado"] == "import_off"),
            "truncado": sum(1 for x in a["detalle"] if x["resultado"] == "truncado"),
            "llamadas_import": sum(x["llamadas_import"] for x in a["detalle"]),
            "instrucciones": sum(x["instrucciones"] for x in a["detalle"]),
            "escrituras": sum(x["escrituras"] for x in a["detalle"]),
            "entradas_en_codigo_parchado": sum(1 for x in a["detalle"] if x["pc_parcheado"]),
            "relocs": a["relocs"], "imports": a["imports"],
            "rw_sha_orig": a["rw_sha"], "rw_sha_patch": b["rw_sha"],
            "t_total": (a["t_total"], b["t_total"]),
        }
    return res


if __name__ == "__main__":
    import json

    salida = None
    if "--json" in sys.argv:
        salida = sys.argv[sys.argv.index("--json") + 1]
    res = compara()
    r = res["resumen"]
    print("entradas=%d ok=%d import_datos=%d import_off=%d fallo=%d truncado=%d escrituras=%d "
          "llamadas_import=%d instrucciones=%d en_codigo_parchado=%d" % (
              r["entradas"], r["ok"], r["import_datos"], r["import_off"], r["fallo"],
              r["truncado"], r["escrituras"], r["llamadas_import"], r["instrucciones"],
              r["entradas_en_codigo_parchado"]))
    print("relocs=%d imports=%d  t=%s" % (r["relocs"], r["imports"], r["t_total"]))
    print("rw_sha orig=%s" % r["rw_sha_orig"])
    print("rw_sha patch=%s" % r["rw_sha_patch"])
    print("entradas de .init_array con resultado distinto: %d" % len(res["diferencias_init"]))
    print("rangos distintos en el segmento RW tras la ejecución: %d" % len(res["rangos_rw"]))
    for va, tam in res["rangos_rw"]:
        print("  VA %#x  %d B" % (va, tam))
    if salida:
        Path(salida).write_text(json.dumps(
            {k: v for k, v in res.items() if k != "rangos_rw"} | {"rangos_rw": res["rangos_rw"]},
            ensure_ascii=False, indent=1))
        print("json ->", salida)
