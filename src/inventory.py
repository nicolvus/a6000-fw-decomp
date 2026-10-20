"""Inventario estático: las firmas son candidatos, no funciones demostradas."""

import argparse
import hashlib
import json
from pathlib import Path


def inspect_file(path: Path, root: Path) -> dict[str, object]:
    with path.open('rb') as stream:
        head = stream.read(64)
        stream.seek(0)
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    kind, architecture = 'unknown', 'unknown'
    if (len(head) >= 52 and head[:4] == b'\x7fELF'
            and head[4] in (1, 2) and head[5] in (1, 2)
            and (head[4] == 1 or len(head) >= 64)):
        kind = 'ELF candidate'
        machine = int.from_bytes(head[18:20], 'little' if head[5] == 1 else 'big')
        architecture = {40: 'ARM', 183: 'AArch64', 3: 'x86', 62: 'x86_64'}.get(
            machine, f'e_machine={machine}')
    else:
        for magic, label in [(b'TPZL', 'LZPT'), (b'PK\x03\x04', 'ZIP candidate'),
                             (b'\x1f\x8b', 'gzip candidate'),
                             (b'hsqs', 'SquashFS candidate'),
                             (b'dex\n', 'DEX candidate')]:
            if head.startswith(magic):
                kind = label
                break
    return {'path': path.relative_to(root).as_posix(), 'size': path.stat().st_size,
            'sha256': digest, 'format': kind, 'architecture': architecture,
            'region': 'consultar ruta y cadena de extracción',
            'responsibility': 'desconocida', 'status': 'inventariado',
            'confidence': 'firma/cabecera; semántica no verificada'}


def inventory(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            rows.append(inspect_file(path, root))
        except OSError as error:
            rows.append({'path': path.relative_to(root).as_posix(),
                         'status': 'error', 'error': str(error), 'sha256': None})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if not root.is_dir() or output.is_relative_to(root):
        parser.error('la entrada debe ser un directorio y la salida debe estar fuera')
    rows = inventory(root)
    output.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n')
    print(f'{len(rows)} archivos inventariados: {output}')


if __name__ == '__main__':
    main()
