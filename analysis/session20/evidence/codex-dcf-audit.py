"""Contrasta los hallazgos con bytes, todas las relocaciones y RTTI existente."""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from rtti_vtables import Elf, recover, self_check

EVIDENCE = ROOT / 'analysis/session20/evidence'
LIB = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib'
NAMES = ('PreRegisterDcfContentSync', 'GetEntryIdFromDirectoryFileNumberSync')


def relocations(elf, names):
    """Incluye GLOB_DAT y JUMP_SLOT, además de ABS32/RELATIVE del lector RTTI."""
    result = []
    for section_name, section in elf.secs.items():
        if section['type'] != 9:  # SHT_REL
            continue
        for offset in range(section['off'], section['off'] + section['size'], 8):
            where, info = struct.unpack_from('<II', elf.d, offset)
            index = info >> 8
            name = elf.syms[index][0] if index else ''
            if name in names:
                result.append({'section': section_name, 'va': hex(where),
                               'type': info & 255, 'symbol': name})
    return result


def main():
    elves = {name: Elf(str(LIB / name)) for name in ('libmpr.so', 'libObj.so')}
    elf = elves['libmpr.so']
    rtti = recover(elf)
    self_check(elf, rtti)
    targets = {name: value & ~1 for name, value in elf.syms
               if value is not None and any(n in name for n in NAMES)}
    assert set(targets.values()) == {0x71eafc, 0x71eb70}
    reloc = {name: relocations(e, targets) for name, e in elves.items()}
    assert not reloc['libmpr.so']
    assert len(reloc['libObj.so']) == 2
    assert all(row['type'] == 22 for row in reloc['libObj.so'])
    for address in targets.values():
        assert not rtti['methods_by_entry'].get(hex(address))
        assert not [v for v, _ in elf.rel.values()
                    if v is not None and v & ~1 == address]
    # Control positivo: el extractor sí recupera los dispatchers examinados.
    assert any(m['class'] == 'StillWriterFilter'
               for m in rtti['methods_by_entry']['0x5144e4'])
    assert any(m['class'] == 'FeaCore' and m['slot'] == 0x1c
               for m in rtti['methods_by_entry']['0x429000'])
    assert elf.u32(0x440c4c) == elf.u32(0x4419dc) == 0x40000012
    assert elf.u32(0x441ba0) == 0x40000012
    accepted = lambda value: ((value + 0xc0000000 - 1) & 0xffffffff) <= 0x90
    assert accepted(0x40000012) and not accepted(0xc0000012)
    obj = elves['libObj.so']
    assert obj.u32(0x900944) == 0x40000012
    assert obj.rel[0x10329cc][0] == 0x900649
    assert elf.rel[0x39b9e8][0] == 0x82df28
    initial = json.loads((EVIDENCE / 'codex-dcf-mpr-initial.json').read_text())
    assert initial['sha256'] == hashlib.sha256(elf.d).hexdigest()
    obj_initial = json.loads((EVIDENCE / 'codex-dcf-obj-boundary.json').read_text())
    assert obj_initial['sha256'] == hashlib.sha256(obj.d).hexdigest()
    # Las etiquetas LLVM por proximidad nunca se usan como atribución de clase.
    classes = {}
    for c in rtti['classes'].values():
        if c['name'] not in ('MMgr', 'MMgrIf', 'AviMMgr', 'AviMMgrIf', 'BgmMMgrIf',
                             'DiscMMgr', 'dcf_AVISequence', 'dcf_Sequence', 'dcf_Lib'):
            continue
        classes[c['name']] = [{
            'vtable': v['addr_point'],
            'slots': {hex(i * 4): m['entry'] for i, m in enumerate(v['methods'])
                      if i * 4 in (0x34, 0x38, 0x48, 0x4c, 0x290)}
        } for v in c['vtables']]
    importers = {}
    for path in sorted(LIB.glob('*.so')):
        output = subprocess.run(['llvm-nm', '-D', str(path)], capture_output=True,
                                text=True, check=True).stdout
        found = [line.strip() for line in output.splitlines()
                 if any(n in line for n in NAMES)]
        if found:
            importers[path.name] = found
    assert set(importers) == {'libmpr.so', 'libObj.so'}
    evidence_files = sorted(EVIDENCE.glob('codex-dcf-*.json'))
    for path in evidence_files:
        json.loads(path.read_text())
    before = {name: hashlib.sha256(e.d).hexdigest() for name, e in elves.items()}
    after = {name: hashlib.sha256((LIB / name).read_bytes()).hexdigest() for name in elves}
    assert before == after
    result = {
        'classification': 'VERIFICADO', 'result': 'PASS', 'hashes': after,
        'public_api_targets': {name: hex(va) for name, va in targets.items()},
        'all_named_relocations': reloc, 'import_export_scan': importers,
        'vtable_slots': classes, 'valid_evidence_json_count': len(evidence_files),
        'checks': ['RTTI self_check y controles positivos',
                   'Sin relocaciones ni entradas virtuales hacia las dos APIs en libmpr',
                   'Dos JUMP_SLOT en libObj; inventario de importadores *.so',
                   'ID 0x40000012 y callback GOT 0x10329cc -> 0x900649',
                   'Rango modular del notificador: 0x40000001..0x40000091',
                   'Constructor AVI instala vtable 0x82df28',
                   'SHA256 original antes/despues y contra primera captura'],
        'limits': ['Las llamadas indirectas calculadas no son enumerables por este test',
                   'Los limites de func_owner son candidatos y se contrastan manualmente',
                   'VA ELF; las decompilaciones Ghidra antiguas pueden incluir +0x10000',
                   'No hay prueba de ejecucion, fsync ni visibilidad real en reproduccion']}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
