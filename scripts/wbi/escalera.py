"""Escalera SSBI de la A6000: comprueba y reetiqueta la cabecera de una imagen de nflasha5.

Según arch/arm/mach-cxd90014/{resume.S,pm.c} y kernel/power/suspend.c del OSS de Sony, la palabra
cxd90014_ssboot_stat (VA 0x400523a0) la fija la entrada de reanudación por la que salta Loader3:
  0x800523a4 _profile    -> stat 1 PROFILE      (perfilar; el siguiente warm sólo reescribe el vector)
  0x800523ac _optimize   -> stat 2 OPTSSBI      (optimizar con /log/ssbi_prof.bin, escribir WBI0, em_reboot)
  0x800523b4 _ssboot_pre -> stat 3 SSBOOT_PRE   (al reanudar, pm_finish reescribe WBI1 + _ssboot)
  0x800523bc _ssboot     -> stat 4 SSBOOT       (arranque caliente normal)
Este script lee las cuatro entradas de la propia imagen (no confía en la tabla de arriba), valida lo
que comprueba Loader3 (reports/evidence/g22-silent-wbi-20261127/D17.md §2.4) y, con --salida, escribe
una copia con otra firma/vector. Sólo cambia los 4 B de firma y los 4 B de vector.

Uso (raíz del repo):
  python3 scripts/wbi/escalera.py IMAGEN                       # informe
  python3 scripts/wbi/escalera.py IMAGEN --paso pre --salida X  # WBI0 + _ssboot_pre
  pasos: profile (prof+_profile), optimize (prof+_optimize), pre (WBI0+_ssboot_pre), ssboot (WBI1+_ssboot)
"""
import argparse
import hashlib
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capstone
from snapram import Ram

STAT_VA = 0x400523a0
ENTRADAS = {1: 'profile', 2: 'optimize', 3: 'pre', 4: 'ssboot'}
FIRMA = {'profile': b'prof', 'optimize': b'prof', 'pre': b'WBI0', 'ssboot': b'WBI1'}
NOMBRE_STAT = {0: 'CREATE_MINSSBI', 1: 'PROFILE', 2: 'CREATE_OPTSSBI', 3: 'SSBOOT_PRE', 4: 'SSBOOT'}


def valida_loader3(d):
    """Comprobaciones de Loader3 (D17 §2.4) salvo la firma, que se informa aparte."""
    fver, nsec, flag, rv, _dver, sec, rd, _ks, _kn, kc, od = struct.unpack('<4s10I', d[:44])
    errores = []
    if sec != 0x200:
        errores.append(f'sector_size {sec:#x}')
    if not flag & 4 and kc != 0x0F0F0F0F:
        errores.append(f'kern_cksum {kc:#x}')
    t, sr, so = 0x40000 + rd, 0, 0
    for i in range(nsec):
        e = struct.unpack_from('<8I', d, t + 32 * i)
        acc = 0x0F0F0F0F
        for x in e[:7]:
            acc ^= x
        if acc != e[7]:
            errores.append(f'meta_cksum sección {i}')
            break
        sr += e[1]
        so += e[4]
    if sr != rd or so != od:
        errores.append(f'tamaños Σr={sr:#x}/{rd:#x} Σo={so:#x}/{od:#x}')
    if not rv or rv % 4:
        errores.append(f'resume_vector {rv:#x}')
    return {'firma': fver, 'secciones': nsec, 'vector': rv, 'r_data': rd, 'o_data': od}, errores


def entradas(r):
    """Decodifica las cuatro entradas y el bloque común; devuelve {PA: stat}."""
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
    base = STAT_VA + 4
    ins = list(md.disasm(r.read(base, 0x30), base))
    mapa, comun = {}, None
    for a, b in zip(ins[0:8:2], ins[1:8:2]):
        assert a.mnemonic == 'mov' and a.op_str.startswith('r1, #'), (hex(a.address), a.mnemonic, a.op_str)
        assert b.mnemonic == 'b', (hex(b.address), b.mnemonic)
        destino = int(b.op_str.lstrip('#'), 16)
        assert comun in (None, destino)
        comun = destino
        mapa[a.address + 0x40000000] = int(a.op_str.split('#')[1], 0)
    c = list(md.disasm(r.read(comun, 8), comun))
    assert c[0].mnemonic == 'sub' or c[0].mnemonic == 'adr' or c[0].op_str.startswith('r0, pc'), c[0]
    # adr r0, cxd90014_ssboot_stat ; str r1, [r0]
    assert c[1].mnemonic == 'str' and c[1].op_str == 'r1, [r0]', c[1]
    destino_adr = comun + 8 - int(c[0].op_str.split('#')[1], 0) if c[0].mnemonic == 'sub' else None
    assert destino_adr in (None, STAT_VA), hex(destino_adr or 0)
    return mapa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('imagen', type=Path)
    ap.add_argument('--paso', choices=sorted(FIRMA))
    ap.add_argument('--salida', type=Path)
    a = ap.parse_args()
    d = a.imagen.read_bytes()
    info, errores = valida_loader3(d)
    r = Ram(a.imagen)
    mapa = entradas(r)
    stat = r.u(STAT_VA)
    print(f'{a.imagen}: firma {info["firma"]!r}, {info["secciones"]} secciones, vector {info["vector"]:#x}'
          f' (stat {mapa.get(info["vector"], "?")}), stat guardado {stat} ({NOMBRE_STAT.get(stat, "?")})')
    print('  entradas:', ', '.join(f'{pa:#x}->stat {s} {ENTRADAS[s]}' for pa, s in sorted(mapa.items())))
    print('  Loader3:', 'OK' if not errores else 'FALLA ' + '; '.join(errores),
          '| modo', {b'WBI1': '10 caliente', b'WBI0': '11 ssboot', b'prof': '12 perfil'}.get(info['firma'], 'frío'))
    if errores:
        sys.exit(1)
    if a.paso:
        if not a.salida:
            sys.exit('--paso exige --salida')
        pa = next(p for p, s in mapa.items() if ENTRADAS[s] == a.paso)
        nuevo = bytearray(d)
        nuevo[0:4] = FIRMA[a.paso]
        struct.pack_into('<I', nuevo, 12, pa)
        assert sum(x != y for x, y in zip(nuevo, d)) <= 8
        a.salida.write_bytes(nuevo)
        print(f'  escrito {a.salida}: firma {FIRMA[a.paso]!r}, vector {pa:#x}, '
              f'sha256 {hashlib.sha256(nuevo).hexdigest()}')


if __name__ == '__main__':
    main()
