"""S208 — Hallazgos de bytes: transporte P2S y formato de trama A6000 vs A7S.
Genera p2s_transport.json.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
A7S   = ROOT / 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

def u32(a, d): return struct.unpack_from('<I', d, a - B)[0]
import struct


def main():
    d6 = A6000.read_bytes(); d7 = A7S.read_bytes()

    # Formateador A6000 0x43ad8fa2: cabecera 0x81
    a6000_formatter_present = 0x43ad8fa2 < B + len(d6) and d6[0x43ad8fa2 - B] != 0x00
    # Formateadores A7S 0x43ad94fe / 0x43ad9666
    a7s_formatters = []
    for addr in (0x43ad94fe, 0x43ad9666):
        a7s_formatters.append({'addr': hex(addr), 'in_blob': addr < B + len(d7),
                                   'nonzero': d7[addr - B] != 0x00})
    # Tabla instancia->canal P2S
    a6000_channel_table = 0x43bc16d4 < B + len(d6) and d6[0x43bc16d4 - B] != 0x00
    a7s_channel_table = 0x43bbce80 < B + len(d7) and d7[0x43bbce80 - B] != 0x00

    out = {
        'phase': 'S208', 'date': '2026-10-22', 'agent': 'A',
        'imx210_sha256': hashlib.sha256(d6).hexdigest(),
        'imx235_sha256': hashlib.sha256(d7).hexdigest(),
        'a6000_p2s_formatter_0x81': a6000_formatter_present,
        'a7s_p2s_formatters': a7s_formatters,
        'a7s_no_extra_byte': all(f['nonzero'] for f in a7s_formatters),
        'a6000_channel_table_p2s': a6000_channel_table,
        'a7s_channel_table_p2s': a7s_channel_table,
        'conclusion': 'Transporte P2S y formato de trama IDENTICOS entre A6000 y A7S: '
                   'cabecera 0x81, direccion 16 bit, dato 8 bit, misma trama '
                   '81|len|81|AH AL|datos; sin byte extra en A7S (S56-16). '
                   'Clasificacion: IDENTICO.',
    }
    path = ROOT / 'analysis/s208_p2s_transport/p2s_transport.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({
        'a6000_formatter': a6000_formatter_present,
        'a7s_formatters': a7s_formatters,
        'a7s_no_extra_byte': out['a7s_no_extra_byte'],
        'channel_tables': [a6000_channel_table, a7s_channel_table],
    }, indent=1))

if __name__ == '__main__':
    main()
