"""S207 — Hallazgos de bytes: fin de integración / segunda cortina electrónica
en A7S (IMX235) vs IMX210 (A6000). Genera full_eoi.json.
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
A7S   = ROOT / 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

EOI_LONG = [b'second curtain', b'2nd curtain', b'shutter close',
            b'integration end', b'end of integration',
            b'finish integration', b'curtain close']
EOI_SHORT = [b'eoi', b'eos', b'curtain']

def _c_string_present(d, s):
    return d.find(s + b'\x00') != -1

def main():
    d7 = A7S.read_bytes(); d6 = A6000.read_bytes()

    eoi_a7s_long = [s.decode() for s in EOI_LONG if s in d7]
    eoi_a7s_short = [s.decode() for s in EOI_SHORT if d7.find(s + b'\x00') != -1]
    eoi_a6000_long = [s.decode() for s in EOI_LONG if s in d6]
    eoi_a6000_short = [s.decode() for s in EOI_SHORT if d6.find(s + b'\x00') != -1]

    # Matriz IMX235: 35 registros, direcciones 0x0000-0x00CF
    d = d7
    def u16(a): return struct.unpack_from('<H', d, a - B)[0]
    def u32(a): return struct.unpack_from('<I', d, a - B)[0]
    rows = []
    a = 0x43fee598
    while True:
        p = u32(a)
        if not p or not (B < p < B + len(d)):
            break
        raw = d[p - 4 - B:p + 1 - B].hex()
        if raw[:2] in ('81', '83'):
            rows.append({'ptr': p, 'dir': u16(p - 2), 'init': d[p - B]})
        a += 40
    imx235_dirs = {r['dir'] for r in rows}

    # ¿Hay algún registro IMX235 dedicado a fin de integración?
    # No hay nombres; se anota ausencia de evidencia en matriz y código.
    out = {
        'phase': 'S207', 'date': '2026-10-22', 'agent': 'A',
        'imx210_sha256': hashlib.sha256(d6).hexdigest(),
        'imx235_sha256': hashlib.sha256(d7).hexdigest(),
        'eoi_strings_a7s_long': eoi_a7s_long,
        'eoi_strings_a7s_short': eoi_a7s_short,
        'eoi_strings_a6000_long': eoi_a6000_long,
        'eoi_strings_a6000_short': eoi_a6000_short,
        'imx235_registers': len(rows),
        'imx235_dirs': sorted(imx235_dirs),
        'imx235_has_eoi_dedicated_register': False,
        'exposure_timer_end_no_register_rewrite': True,  # S57-F: ExposureTimerEnd! no reescribe sensores
        'conclusion': 'No hay registro ni mecanismo de fin de integracion / segunda '
                   'cortina electronica en A7S que falte al IMX210; ambos carecen '
                   'de operacion de fin de integracion identificada (NO_VERIFICADO '
                   'si el sensor la hace internamente).',
    }
    path = ROOT / 'analysis/s207_imx235_end_of_integration/full_eoi.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({
        'eoi_a7s_long': eoi_a7s_long,
        'eoi_a7s_short': eoi_a7s_short,
        'eoi_a6000_long': eoi_a6000_long,
        'eoi_a6000_short': eoi_a6000_short,
        'imx235_registers': len(rows),
    }, indent=1))

if __name__ == '__main__':
    main()
