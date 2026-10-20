"""Inventario estático LIRO con base y tabla explícitas; no ejecuta firmware."""

import argparse
import hashlib
import json
import struct
from pathlib import Path


def parse_header(data: bytes, base: int) -> dict[str, int]:
    if len(data) < 0x30 or base < 0 or base % 4:
        raise ValueError('cabecera o base LIRO inválida')
    if struct.unpack_from('<I', data, 4)[0] != 0x4C49524F:
        raise ValueError('magic LIRO ausente')
    version = struct.unpack_from('<I', data, 8)[0]
    if version != 4:
        raise ValueError('solo se interpreta la cabecera LIRO versión 4')
    names = ('entry_pre', 'entry_main', 'descriptor', 'suspend', 'resume',
             'exit', 'func1', 'func2', 'func3')
    result = {'base': base, 'version': version}
    for i, name in enumerate(names):
        address = struct.unpack_from('<I', data, 12 + i * 4)[0]
        offset = (address & ~1) - base
        if not 0 <= offset <= len(data) - 4:
            raise ValueError(f'{name} fuera de la imagen declarada')
        result[name] = address
        result[name + '_file_offset'] = offset
    return result


def parse_dispatch(data: bytes, offset: int, count: int,
                   base: int) -> list[dict[str, int]]:
    if offset < 0 or offset % 4 or count < 1 or offset + count * 12 > len(data):
        raise ValueError('tabla de despacho fuera de límites')
    rows = []
    seen: set[int] = set()
    for i in range(count):
        command, handler, flag = struct.unpack_from('<3I', data, offset + i * 12)
        entry_offset = (handler & ~1) - base
        if command > 0xFFFF or command in seen:
            raise ValueError('identificador de comando inválido o repetido')
        if not 0 <= entry_offset <= len(data) - 2:
            raise ValueError('handler fuera de la imagen')
        seen.add(command)
        rows.append({'command_id': command, 'handler_address': handler,
                     'handler_file_offset': entry_offset, 'thumb': handler & 1,
                     'flag': flag})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--base', type=lambda s: int(s, 0), required=True)
    parser.add_argument('--table', type=lambda s: int(s, 0), required=True)
    parser.add_argument('--count', type=lambda s: int(s, 0), required=True)
    args = parser.parse_args()
    if args.binary.resolve() == args.output.resolve():
        parser.error('la salida no puede sobrescribir el firmware')
    data = args.binary.read_bytes()
    header = parse_header(data, args.base)
    rows = parse_dispatch(data, args.table, args.count, args.base)
    result = {
        'schema': 1, 'binary': str(args.binary),
        'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data),
        'header': header, 'table_file_offset': args.table,
        'table_count': args.count, 'dispatch': rows,
        'limitations': [
            'Base, table offset and count are analyst-supplied and require separate evidence',
            'Declared addresses are not measured runtime addresses',
            'Handler pointers and flags do not prove sensor capability or execution',
            'No function-boundary or control-flow proof from table parsing alone',
        ],
    }
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(f'LIRO v{header["version"]}; {len(rows)} comandos inventariados')


if __name__ == '__main__':
    main()
