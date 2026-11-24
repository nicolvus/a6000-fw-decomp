"""G104 §8.6 — Recursos de las filas ISO 64000…409600: textos «ISO n» e iconos de la lista.

Textos: 64000/80000/102400/204800 ya existen en los `string_*.uxc` del A6000; 128000/160000/256000/320000/409600 van en ranuras libres
(`build_pp_gamma_menu.free_ids`, mismas reglas que el resto del CFW).
Iconos: la A6000 no los tiene; se copian los de la A7S 3.20 (`image_cmn_43.uxc`, mismos tamaños 116×100 y 70×60 que los de 51200)
a ranuras libres de `image_cmn_169.uxc`.
Formato de `image_*.uxc` (VERIFICADO en los dos ficheros): cabecera 16 B (cuenta de ranuras = u32 +12 & 0x1fff, primer id 0xc000),
tabla de u16 (índice en palabras del registro desde `base` = 0x10 + 2·cuenta; 0xffff = vacía), registros de 20 B
(u16 id, u16 0x1a05, u32 formato 0xc0…/A7S 0xe0…, u16 ancho, u16 alto, u32 tamaño, u32 desplazamiento desde `base + 4`; los de formato 0xc8… miden 40 B
y no apuntan a datos) y después los datos, que empiezan justo tras el último registro.
El códec de los datos no es LZPT (salvo por azar); se copian tal cual. INFERENCIA: el bit 29 del formato (A7S) no cambia el códec — se comprueba en el arnés.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_pp_gamma_menu as G
import iso_ui_patch as P
import uxc_strings

TEXTOS_A6000 = {64000: 0xEF9B, 80000: 0xEF30, 102400: 0xEF8B, 204800: 0xEFF4}
# iconos de las filas de la A7S 3.20 (vu4 `0x1b8728…`): (lista, seleccionado)
ICONOS_A7S = {64000: (0xDD80, 0xDD69), 80000: (0xDD3A, 0xDD7A), 102400: (0xDD2F, 0xDD61), 128000: (0xDD44, 0xDD7F), 160000: (0xDD4F, 0xDCE2),
              204800: (0xDD4E, 0xDD19), 256000: (0xDCDF, 0xDD83), 320000: (0xDD2C, 0xDD49), 409600: (0xDD23, 0xDD04)}
PRIMER, VACIA, REG = 0xC000, 0xFFFF, 20
A7S_APP = Path(__file__).resolve().parents[2] / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/share/app"


def _indice(d: bytes):
    n = struct.unpack_from("<I", d, 12)[0] & 0x1FFF
    base = 0x10 + 2 * n
    return n, base, list(struct.unpack_from(f"<{n}H", d, 0x10))


def _registro(d: bytes, rid: int):
    _, base, tab = _indice(d)
    t = tab[rid - PRIMER]
    assert t != VACIA, f"sin imagen {rid:#x}"
    r = struct.unpack_from("<HHIHHII", d, base + 4 * t)
    assert r[0] == rid & 0xFFFF and r[1] == 0x1A05 and r[2] >> 24 in (0xC0, 0xE0), (hex(rid), r)
    return r, d[base + 4 + r[6]:base + 4 + r[6] + r[5]]


def refs_recurso(dirs, alto: int) -> set:
    """Ids (16 bits) que alguna biblioteca ya referencia como recurso `alto`<<16 (0x0204 textos, 0x0205 imágenes)."""
    refs = set()
    for dd in dirs:
        for so in Path(dd, "lib").glob("*.so*"):
            b = so.read_bytes()
            refs |= {w & 0xFFFF for (w,) in struct.iter_unpack("<I", b[: len(b) // 4 * 4]) if w >> 16 == alto}
    return refs


def imagenes(a6000: bytes, a7s: bytes, ids_a7s, ocupadas=frozenset(), formato=None) -> tuple[bytes, dict]:
    """Copia las imágenes `ids_a7s` de la A7S a ranuras libres (de mayor a menor, fuera de `ocupadas`). Devuelve (fichero, {id A7S: id nuevo}).
    `formato` = {id A7S: palabra de formato} sustituye la de la A7S (pruebas en el arnés)."""
    formato = formato or {}
    n, base, tab = _indice(a6000)
    libres = [PRIMER + i for i in range(n - 1, -1, -1) if tab[i] == VACIA and PRIMER + i not in ocupadas]
    nuevos = dict(zip(ids_a7s, libres))
    assert len(nuevos) == len(ids_a7s), "no hay ranuras libres"
    regs = [(t, struct.unpack_from("<HHIHHII", a6000, base + 4 * t)) for t in tab if t != VACIA]
    fin_regs = max(4 * t + (2 * REG if r[2] >> 24 == 0xC8 else REG) for t, r in regs)
    datos = min(r[6] for _, r in regs if r[2] >> 24 == 0xC0) + 4          # los datos empiezan justo tras el último registro
    assert datos == fin_regs and fin_regs + REG * len(nuevos) <= 4 * 0xFFFF, (hex(datos), hex(fin_regs))
    hueco = (REG * len(nuevos) + 15) // 16 * 16            # conserva la alineación (mód 16) de los datos
    out = bytearray(a6000[:base + fin_regs])
    for t, r in regs:                                       # los de formato 0xc8 (40 B, desplazamiento 0/1) no apuntan a datos
        if r[2] >> 24 == 0xC0:
            struct.pack_into("<I", out, base + 4 * t + 16, r[6] + hueco)
    cola = bytearray(a6000[base + fin_regs:])
    cola += b"\0" * (-len(cola) % 16)
    extra = b""
    base7 = _indice(a7s)[1]
    for k, (viejo, nuevo) in enumerate(nuevos.items()):
        r, _ = _registro(a7s, viejo)
        blob = a7s[base7 + r[6]:base7 + r[6] + 4 + r[5]]    # con los 4 B previos: vale tanto si el lector parte de `base` como de `base + 4`
        off = fin_regs + hueco + len(cola) + len(extra)
        out += struct.pack("<HHIHHII", nuevo, r[1], formato.get(viejo, r[2]), r[3], r[4], r[5], off)
        struct.pack_into("<H", out, 0x10 + 2 * (nuevo - PRIMER), (fin_regs + REG * k) // 4)
        extra += blob + b"\0" * (-len(blob) % 16)
    out += b"\0" * (hueco - REG * len(nuevos))
    return bytes(out + cola + extra), nuevos


def ids_textos(dirs, ocupar=()) -> dict:
    """Ids de texto de cada valor: los existentes y, para el resto, ranuras libres en todos los `dirs` (orden de `VALORES`)."""
    faltan = [v for v in P.VALORES if v not in TEXTOS_A6000]
    comunes = None
    for dd in dirs:
        lib = set(G.free_ids(Path(dd), 400, set(ocupar)))
        comunes = lib if comunes is None else comunes & lib
    libres = sorted(comunes, reverse=True)[:len(faltan)]
    assert len(libres) == len(faltan), "no hay ids de texto libres"
    return {**TEXTOS_A6000, **dict(zip(faltan, libres))}


def aplicar(files: Path, orig: Path) -> tuple[dict, dict, list[str]]:
    """En `files` (árbol `/usr` del CFW, con sus `string_*.uxc`): textos nuevos e iconos de la A7S. Devuelve (textos, iconos, ficheros escritos)."""
    textos = ids_textos([files, orig])
    escritos = [f"share/app/{f}" for f in escribir_textos(files / "share/app", files / "share/app", textos)]
    img = files / "share/app/image_cmn_169.uxc"
    base = img if img.exists() else orig / "share/app/image_cmn_169.uxc"
    nuevo, mapa = imagenes(base.read_bytes(), (A7S_APP / "image_cmn_43.uxc").read_bytes(), [i for p in ICONOS_A7S.values() for i in p],
                           refs_recurso([files, orig], 0x0205))
    img.write_bytes(nuevo)
    return textos, {v: (mapa[a], mapa[b]) for v, (a, b) in ICONOS_A7S.items()}, [*escritos, "share/app/image_cmn_169.uxc"]


def escribir_textos(src: Path, dst: Path, ids: dict) -> list[str]:
    """`ISO n` en cada `string_*.uxc` latino de `src` (los que `uxc_strings` reconstruye igual) → `dst`. Devuelve los ficheros escritos."""
    hechos = []
    for f in sorted(Path(src).glob("string_*.uxc")):
        if f.name.endswith("_guide.uxc"):
            continue
        try:
            head, _, recs = uxc_strings.parse(f.read_bytes())
            assert uxc_strings.build(head, recs) == f.read_bytes()
        except AssertionError:                  # idiomas no latinos: como el resto del CFW, sin textos nuevos
            continue
        for v, i in ids.items():
            if v not in TEXTOS_A6000:
                assert i not in recs, f"{i:#x} ocupado en {f.name}"
                recs[i] = f"ISO {v}"
        Path(dst, f.name).write_bytes(uxc_strings.build(head, recs))
        hechos.append(f.name)
    return hechos
