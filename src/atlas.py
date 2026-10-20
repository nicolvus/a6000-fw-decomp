"""Metadatos ELF y relaciones declaradas; no ejecuta programas del firmware."""

import argparse
import collections
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = 2
RULES = {
    'capture': r'CameraHardwareDiadem|CommandProcessorCameraTakePicture|CameraEx|captureStart|libcamera',
    'ui': r'CmnViewSetting|OBJDISPLAY|ViewBaseProduct|Widget|libgui',
    'service': r'SenserIf|senser_usb|SenserThread|senser_normal',
    'network': r'^socket$|^connect$|SSL_|BIO_|wifi_|wpa_|libssl|libcurl',
    'storage': r'sqlite3_|ext2fs_|nand_|mtd_|mmc_|jffs2|libsqlite',
    'android-ipc': r'Parcel|IPCThreadState|IServiceManager|JNI_|Java_|libbinder|libandroid_runtime',
    'audio': r'AudioTrack|AudioFlinger|^snd_|^pcm_|libaudio',
    'codecs': r'^jpeg_|avcodec_|avformat_|^png_|^inflate|^deflate|libjpeg|libpng|libavcodec',
    'crypto': r'EVP_|AES_|SHA1_|SHA256_|RSA_|MD5_|libcrypto',
}


def parse_readelf(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {'needed': [], 'soname': [], 'runpath': [],
                              'imports': [], 'exports': [], 'kernel_module': False}
    for key, label in [('elf_type', 'Type'), ('machine', 'Machine'), ('class', 'Class')]:
        match = re.search(r'^\s*' + label + r':\s*(.+)$', text, re.MULTILINE)
        result[key] = match.group(1).strip() if match else 'unknown'
    for tag, key in [('NEEDED', 'needed'), ('SONAME', 'soname'),
                     ('RUNPATH', 'runpath'), ('RPATH', 'runpath')]:
        result[key].extend(re.findall(r'\(' + tag + r'\)[^\n]*\[([^\]]+)\]', text))
    for line in text.splitlines():
        match = re.match(
            r'\s*\d+:\s+[0-9a-fA-F]+\s+\d+\s+\w+\s+(GLOBAL|WEAK)\s+\w+\s+(\w+)\s+(\S+)',
            line,
        )
        if match:
            key = 'imports' if match.group(2) == 'UND' else 'exports'
            result[key].append(match.group(3))
    for key in ['needed', 'soname', 'runpath', 'imports', 'exports']:
        result[key] = sorted(set(result[key]))
    result['kernel_module'] = bool(re.search(r'\s\.modinfo\s', text))
    interpreter = re.search(r'Requesting program interpreter:\s*([^\]]+)', text)
    result['interpreter'] = interpreter.group(1) if interpreter else None
    return result


def classify(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    """Etiquetas de asociación basadas en interfaces; no responsabilidades probadas."""
    tokens = metadata['imports'] + metadata['exports'] + metadata['needed']
    labels = []
    for subsystem, expression in RULES.items():
        evidence = [token for token in tokens if re.search(expression, token.split('@')[0])]
        if evidence:
            labels.append({'subsystem': subsystem, 'status': 'INFERENCIA',
                           'evidence': evidence[:12], 'matching_tokens': len(evidence)})
    if metadata.get('kernel_module'):
        labels.append({'subsystem': 'kernel-module', 'status': 'VERIFICADO',
                       'evidence': ['section .modinfo'], 'matching_tokens': 1})
    return labels


def region(path: str) -> str:
    match = re.search(r'nflasha\d+', path)
    return match.group() if match else 'updater-or-other'


def structural_role(metadata: dict[str, Any]) -> str:
    if metadata.get('kernel_module'):
        return 'kernel-module'
    if metadata['elf_type'].startswith('EXEC') or metadata.get('interpreter'):
        return 'executable'
    if metadata['elf_type'].startswith('DYN'):
        return 'shared-object-candidate'
    if metadata['elf_type'].startswith('REL'):
        return 'relocatable-object'
    return 'unknown'


def subsystem_map(rows: list[dict[str, Any]],
                  dependencies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels = {r['path']: {a['subsystem'] for a in r['associations']} or {'unclassified'}
              for r in rows}
    counts: dict[tuple[str, str], set[tuple[str, str]]] = collections.defaultdict(set)
    ambiguous: dict[tuple[str, str], set[tuple[str, str]]] = collections.defaultdict(set)
    for edge in dependencies:
        target_labels = set().union(*(labels[p] for p in edge['candidates']))
        if not target_labels:
            target_labels = {'missing'}
        for source in labels[edge['source']]:
            for target in target_labels:
                pair = (source, target)
                reference = (edge['source'], edge['needed'])
                counts[pair].add(reference)
                if edge['status'] == 'ambiguous':
                    ambiguous[pair].add(reference)
    return [{'source': a, 'target': b, 'declared_references': len(refs),
             'ambiguous_references': len(ambiguous[(a, b)]), 'runtime_verified': False}
            for (a, b), refs in sorted(counts.items())]


def resolve_needed(source: str, needed: str,
                   candidates: list[dict[str, Any]]) -> dict[str, Any]:
    same_dir = [r for r in candidates if Path(r['path']).parent == Path(source).parent]
    same_region = [r for r in candidates if region(r['path']) == region(source)]
    pool = same_dir or same_region or candidates
    basis = 'same_directory' if same_dir else 'same_region' if same_region else 'global_inventory'
    unique = {r['sha256'] for r in pool}
    return {'source': source, 'needed': needed,
            'status': 'missing' if not pool else 'candidate' if len(unique) == 1 else 'ambiguous',
            'basis': basis, 'candidates': [r['path'] for r in pool],
            'runtime_verified': False}


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def build(root: Path, manifest: Path, output: Path, cache: Path) -> dict[str, Any]:
    readelf = shutil.which('readelf')
    if not readelf:
        raise RuntimeError('readelf no disponible')
    version = subprocess.run([readelf, '--version'], capture_output=True, text=True,
                             check=True).stdout.splitlines()[0]
    identity = {'schema': SCHEMA, 'readelf_sha256': digest(Path(readelf)),
                'readelf_version': version}
    producer_key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    rows = [row for row in json.loads(manifest.read_text())
            if row.get('format') == 'ELF candidate']
    cache.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []
    hits = 0
    # El cache guarda solo metadatos por contenido y productor; las etiquetas se recalculan.
    for row in rows:
        path = root / row['path']
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('ruta fuera de la extracción: ' + row['path'])
        actual = digest(path)
        if actual != row['sha256']:
            raise ValueError('hash distinto al inventario: ' + row['path'])
        cached = cache / f'{producer_key}-{actual}.json'
        if cached.exists():
            metadata = json.loads(cached.read_text())
            hits += 1
        else:
            process = subprocess.run([readelf, '-h', '-l', '-d', '-S', '-W', '-s', str(path)],
                                     capture_output=True, text=True, timeout=30, check=False,
                                     env={**os.environ, 'LC_ALL': 'C'})
            if process.returncode:
                errors.append({'path': row['path'], 'error': process.stderr})
                continue
            metadata = parse_readelf(process.stdout)
            metadata['diagnostics'] = process.stderr
            cached.write_text(json.dumps(metadata, sort_keys=True) + '\n')
        results.append({**row, 'region': region(row['path']), 'metadata': metadata,
                        'associations': classify(metadata), 'producer': identity,
                        'structural_role': structural_role(metadata)})
    index: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in results:
        names = set(row['metadata']['soname'] + [Path(row['path']).name])
        for name in names:
            index[name].append(row)
    edges = [resolve_needed(row['path'], needed, index.get(needed, []))
             for row in results for needed in row['metadata']['needed']]
    associations = collections.Counter(label['subsystem'] for r in results
                                       for label in r['associations'])
    graph: dict[str, Any] = {
        'schema': SCHEMA, 'producer': identity,
        'limitations': ['DT_NEEDED is a declaration, not an observed runtime load',
                        'dlopen, IPC, ioctl and physical buses are not resolved',
                        'subsystem associations are heuristics with observed tokens'],
        'summary': {'input_paths': len(rows), 'analyzed_paths': len(results),
                    'unique_hashes': len({r['sha256'] for r in results}),
                    'cache_hits_this_run': hits, 'errors': len(errors),
                    'unknown_associations': sum(not r['associations'] for r in results),
                    'associations': dict(associations),
                    'structural_roles': dict(collections.Counter(
                        r['structural_role'] for r in results)),
                    'dependency_edges': len(edges),
                    'dependency_status': dict(collections.Counter(e['status'] for e in edges))},
        'files': results, 'dependencies': edges, 'errors': errors,
        'subsystem_dependencies': subsystem_map(results, edges),
    }
    output.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + '\n')
    return graph


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('firmware/extracted/fw321'))
    parser.add_argument('--manifest', type=Path, default=Path('reports/inventory.json'))
    parser.add_argument('--output', type=Path, default=Path('reports/elf-atlas.json'))
    parser.add_argument('--cache', type=Path, default=Path('analysis/elf-cache'))
    args = parser.parse_args()
    print(json.dumps(build(args.root, args.manifest, args.output, args.cache)['summary'],
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
