#!/usr/bin/env python3
"""Valida desplazamientos TRACEFN2 antes de armar trampas en el arnés (regla: solo en entrada de función).

uso: chequea_trampas.py LIB.so off[,off…]
  LIB.so = biblioteca del invitado vista desde el anfitrión (p. ej. …/nflasha15_unpacked_unpacked/lib/libmpr.so);
  los off son los mismos hexadecimales que se pasan a TRACEFN2 (VA del ELF, sin el 1 de Thumb).
Por cada off imprime: par/impar, dentro de un PT_LOAD ejecutable, llamadores `bl` (una pasada por .text),
punteros literales (u32 igual a off o a off|1, de donde salen los vtables) y los bytes previos.
Veredicto: ENTRADA (hay `bl` o puntero + frontera), DUDOSA (solo frontera), NO (ni una cosa ni otra).
Salida: 0 si todos son ENTRADA; 1 si alguno es DUDOSA o NO (entonces NO se debe armar en caliente).
Motivo: armar en caliente fuera de una entrada de función mata im.elf (IMEXIT im_s 139, §5.41 y
reports/film-pb-1-sub-arnes-estable-20261126.md §3): el UDF 0xde00 cae dentro de una instrucción o en un
pool de literales, y con TRACEREP se escribe otro UDF en «la instrucción siguiente», que ahí no existe.
"""
import struct
import sys

TERMINADORES = {  # último halfword de una función (Thumb/Thumb-2), o relleno entre funciones
    0x4770: "bx lr", 0x46C0: "nop", 0xBF00: "nop", 0x0000: "relleno",
}


class Elf32:
    def __init__(self, ruta: str) -> None:
        self.d = open(ruta, "rb").read()
        d = self.d
        if d[:4] != b"\x7fELF" or d[4] != 1:
            raise SystemExit(f"{ruta}: no es un ELF32")
        e_phoff, e_shoff = struct.unpack_from("<I", d, 28)[0], struct.unpack_from("<I", d, 32)[0]
        e_phentsize, e_phnum = struct.unpack_from("<H", d, 42)[0], struct.unpack_from("<H", d, 44)[0]
        e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<H", d, 46)[0], struct.unpack_from("<H", d, 48)[0], struct.unpack_from("<H", d, 50)[0]
        self.segs = []  # (off, va, filesz, flags)
        for i in range(e_phnum):
            t, off, va, _pa, fsz, _msz, fl, _al = struct.unpack_from("<8I", d, e_phoff + i * e_phentsize)
            if t == 1:
                self.segs.append((off, va, fsz, fl))
        secs = [struct.unpack_from("<10I", d, e_shoff + i * e_shentsize) for i in range(e_shnum)]
        nom = d[secs[e_shstrndx][4]:]
        self.sec = {}
        for s in secs:
            nombre = nom[s[0]:nom.index(b"\0", s[0])].decode("latin1")
            self.sec[nombre] = (s[3], s[4], s[5])  # va, off, size

    def va2off(self, va: int):
        for po, base, fsz, _fl in self.segs:
            if base <= va < base + fsz:
                return po + va - base
        return None

    def ejecutable(self, va: int) -> bool:
        return any(base <= va < base + fsz and fl & 1 for _po, base, fsz, fl in self.segs)

    def leer(self, va: int, n: int) -> bytes:
        o = self.va2off(va)
        return self.d[o:o + n] if o is not None else b""

    def llamadores(self) -> dict:
        """Una pasada por .text: destino de cada bl (Thumb-2 T4, como elfhelper.calls) → direcciones que llaman."""
        va, off, sz = self.sec[".text"]
        d, out = self.d, {}
        for o in range(off, off + sz - 3, 2):
            hw1, hw2 = struct.unpack_from("<HH", d, o)
            if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xC000) != 0xC000:
                continue
            s = (hw1 >> 10) & 1
            j1, j2 = (hw2 >> 13) & 1, (hw2 >> 11) & 1
            i1, i2 = (~(j1 ^ s)) & 1, (~(j2 ^ s)) & 1
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((hw1 & 0x3FF) << 12) | ((hw2 & 0x7FF) << 1)
            if s:
                imm -= 1 << 25
            pc = va + (o - off)
            out.setdefault(pc + 4 + imm, []).append(pc)
        return out

    def literales(self, valor: int) -> list[int]:
        pat, out, i = struct.pack("<I", valor), [], 0
        while (i := self.d.find(pat, i)) >= 0:
            o = self.va2off_to(i)
            if o:
                out.append(o)
            i += 1
        return out

    def va2off_to(self, off: int):
        for po, base, fsz, _fl in self.segs:
            if po <= off < po + fsz:
                return base + off - po
        return None


def es_prologo(e: Elf32, va: int) -> bool:
    """Primera instrucción típica de función Thumb: push/push.w, sub sp (con push.w detrás), str …[sp,#-n]!."""
    hw = struct.unpack_from("<H", e.leer(va, 2) or b"\0\0")[0]
    return (hw & 0xFE00) == 0xB400 or (hw & 0xF800) == 0xB000 or hw == 0xE92D or hw == 0xF84D or hw == 0xF1AD


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__.strip().splitlines()[0] + "\nuso: chequea_trampas.py LIB.so off[,off…]", file=sys.stderr)
        return 2
    e = Elf32(sys.argv[1])
    offs = [int(x, 16) for x in sys.argv[2].replace(",", " ").split()]
    bl = e.llamadores()
    malo = False
    print(f"# {sys.argv[1]}: {len(offs)} desplazamiento(s); .text {e.sec['.text'][2]} B; "
          f"{sum(1 for k in bl)} destinos de bl")
    for o in offs:
        par = o % 2 == 0
        ejec = e.ejecutable(o)
        llaman = bl.get(o, [])
        lits = e.literales(o) + e.literales(o | 1)
        prev = struct.unpack_from("<H", e.leer(o - 2, 2) or b"\0\0")[0] if o >= 2 else 0
        prologo = es_prologo(e, o)
        frontera = prev in TERMINADORES or (prev & 0xFF00) == 0xBD00 or (prev & 0xF800) == 0xE000
        if not par or not ejec:
            veredicto, razon = "NO", f"{'impar (1 de Thumb)' if not par else ''}{' fuera de segmento ejecutable' if not ejec else ''}".strip()
        elif llaman:
            veredicto, razon = "ENTRADA", f"bl desde {', '.join(f'{a:#x}' for a in llaman[:3])}"
        elif lits and (prologo or frontera):
            veredicto, razon = "ENTRADA", f"puntero en {', '.join(f'{a:#x}' for a in lits[:3])} + {('prólogo' if prologo else 'frontera')}"
        elif prologo:
            veredicto, razon = "DUDOSA", f"prólogo pero sin bl ni puntero (previo {prev:#06x})"
        elif frontera:
            veredicto, razon = "DUDOSA", f"solo frontera (previo {prev:#06x} = {TERMINADORES.get(prev, 'pop/b')})"
        else:
            veredicto, razon = "NO", f"sin bl, sin puntero, previo {prev:#06x} no cierra función y no hay prólogo"
        malo |= veredicto != "ENTRADA"
        print(f"{o:#08x} {veredicto:8s} llamadores={len(llaman):3d} punteros={len(lits):3d} previo={prev:#06x} "
              f"prologo={'si' if prologo else 'no':2s} — {razon}")
    if malo:
        print("NO ARMAR en caliente: no todos son entrada de función demostrada (ver informe §3). "
              "Si aun así hace falta, FUERZA=1 en estable.sh asume el riesgo de IMEXIT 139.", file=sys.stderr)
    return 1 if malo else 0


if __name__ == "__main__":
    sys.exit(main())
