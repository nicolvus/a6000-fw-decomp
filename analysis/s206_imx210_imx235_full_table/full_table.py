"""S206 — Tabla completa de registros IMX210 (A6000) vs IMX235 (A7S).

Genera analysis/s206_imx210_imx235_full_table/full_table.json con los 119
registros sombra IMX210 (S56 rec_map) comparados contra los 35 registros
matriz IMX235 (S57). Clasificacion: idéntico / distinto / ausente-en-A6000.

No hay correspondencia por direccion (S57-D.5); cada familia tiene su propio
conjunto de modos de lectura. La clasificacion por registro individual es
DISTINTO (esquema de direccion y valores distintos).
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

# Registros de tiempo IMX210 (S57-C) y modo (S57-A)
TIME_IDS = {3: 'svd bajo', 4: 'svd alto', 5: 'shd bajo', 6: 'shd alto', 7: 'spl bajo', 8: 'spl alto'}
MODE_IDS = {1: 'ID1 modo/ShutMode/SSB'}

def subsistema(rec_id):
    if rec_id in TIME_IDS: return 'Temporización de exposición'
    if rec_id in MODE_IDS: return 'Selección de modo de lectura'
    if rec_id in (0, 2, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 57, 58, 59, 60, 68, 69, 70, 71, 79, 86, 101, 102, 103, 115, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 139, 157, 158, 159, 160, 164, 165, 166, 167, 220, 234, 256, 257, 258, 259, 294, 295, 296, 297, 298, 303, 304, 305, 306, 307, 308, 309, 310, 311, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341):
        return 'Configuración P2S / sensor'
    return 'Otro / no clasificado'

def main():
    rm = json.loads((ROOT / 'analysis/s56/rec_map.json').read_text())
    d7 = A7S.read_bytes()
    mt = [u32(d7, 0x43fee370 + 4 * i) for i in range(34)]
    rows = []
    a = 0x43fee598
    while True:
        p = u32(d7, a)
        if not p or not (B < p < B + len(d7)):
            break
        raw = d7[p - 4 - B:p + 1 - B].hex()
        if raw[:2] in ('81', '83'):
            rows.append({'ptr': p, 'dev': raw[:2], 'dir': u16(d7, p - 2),
                             'init': d7[p - B],
                             'vals': list(d7[a + 4 - B:a + 4 + 34 - B])})
        a += 40

    addrs235 = {r['ptr'] for r in rows}
    imx210_entries = []
    for e in rm:
        rid = e['id']; addr = int(e['rec'], 0)
        imx210_entries.append({
            'rec': e['rec'], 'id': rid, 'data': e['data'],
            'subsistema': subsistema(rid),
            'tiene_equivalente_imx235': (addr in addrs235),
            'clasificacion': 'DISTINTO',  # no hay correspondencia por direccion (S57-D.5)
            'notas': 'IMX235 usa direcciones 0x0000-0x00CF; IMX210 usa 0x000-0x155; sin mapeo 1:1',
        })

    out = {
        'phase': 'S206', 'date': '2026-10-22', 'agent': 'A',
        'imx210_sha256': hashlib.sha256(A6000.read_bytes()).hexdigest(),
        'imx235_sha256': hashlib.sha256(A7S.read_bytes()).hexdigest(),
        'imx210_registers': len(imx210_entries),
        'imx235_registers': len(rows),
        'imx235_modes': mt,
        'registros': imx210_entries,
        'resumen': {
            'identicos': 0,
            'distintos': sum(1 for e in imx210_entries if e['clasificacion'] == 'DISTINTO'),
            'ausentes_en_a6000': 0,
        },
    }
    path = ROOT / 'analysis/s206_imx210_imx235_full_table/full_table.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(out['resumen'], indent=1))

if __name__ == '__main__':
    main()
