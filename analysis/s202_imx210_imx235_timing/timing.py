"""S202 — Comparación de tiempos de lectura/exposición IMX210 (A6000) vs IMX235 (A7S).

Genera analysis/s202_imx210_imx235_timing/timing.json con los hechos de bytes
registros de tiempo, fórmula svd, espejo, lectura y fin de integración.
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
A7S   = ROOT / 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

def u16(d, a): return struct.unpack_from('<H', d, a - B)[0]
def u32(d, a): return struct.unpack_from('<I', d, a - B)[0]

# {ID: (dirección_registro, dato_default)} del IMX210 (rec_map.json S56/S57)
IMX210_TIME = {
    3:  (0x4401c7e0, 'svd bajo'),
    4:  (0x4401c678, 'svd alto'),
    5:  (0x4401c744, 'shd bajo'),
    6:  (0x4401c684, 'shd alto'),
    7:  (0x4401c698, 'spl bajo'),
    8:  (0x4401c764, 'spl alto'),
}

def main():
    d6 = A6000.read_bytes()
    d7 = A7S.read_bytes()
    regs = {}
    for i, (addr, nombre) in IMX210_TIME.items():
        got = u16(d6, addr)
        regs[i] = {'id': i, 'addr': addr, 'nombre': nombre, 'id_leido': got, 'ok': (got == i)}
    # Matriz IMX235: columnas de modo (tiempos estáticos por modo), sin registro equivalente
    mt = [u32(d7, 0x43fee370 + 4 * i) for i in range(34)]
    silent_cols = [i for i, m in enumerate(mt) if m in (0x4e, 0x4f)]
    out = {
        'phase': 'S202', 'date': '2026-10-22', 'agent': 'A',
        'imx210_sha256': hashlib.sha256(d6).hexdigest(),
        'imx235_sha256': hashlib.sha256(d7).hexdigest(),
        'imx210_time_registers': regs,
        'imx210_svd_formula': 'svd = n·svr_num − 1 (o n/VdNum − 1), validado en 0x4381106c',
        'imx210_readout_lines': 4176,
        'imx210_readout_ms': '≈66,8 ms/cuadro (cálculo sobre matriz, no dato de sensor)',
        'imx235_time_registers': None,
        'imx235_modes': mt,
        'imx235_silent_columns': silent_cols,
        'end_of_integration': 'No reescritura de registros al terminar en ninguno (NO_VERIFICADO fin eléctrico)',
        'units': 'NO_VERIFICADO (sin datasheet): no se asignan µs/líneas/ciclos a svd/shd/spl',
    }
    path = ROOT / 'analysis/s202_imx210_imx235_timing/timing.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({
        'time_registers_ok': all(r['ok'] for r in regs.values()),
        'silent_columns': silent_cols,
    }, indent=1))

if __name__ == '__main__':
    main()
