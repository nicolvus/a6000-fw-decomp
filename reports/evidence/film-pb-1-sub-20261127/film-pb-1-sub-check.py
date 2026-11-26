#!/usr/bin/env python3
"""Verificación en solo lectura del DAT oficial 3.21 y del build 4.04 (Sony sin WBI).
No escribe nada fuera de reports/evidence/film-pb-1-sub-20261127/."""
import hashlib, json, sys, zlib, mmap
from pathlib import Path

ROOT = Path('/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter')
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'references/fwtool'))
sys.path.insert(0, str(ROOT / 'scripts/gui'))
from e25_06 import audit_packages as A
from e25_27 import build, sums, tpzl

OUT = ROOT / 'reports/evidence/film-pb-1-sub-20261127'
OUT.mkdir(parents=True, exist_ok=True)

SONY_DAT = ROOT / 'firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat'
SONY_FDAT = ROOT / 'firmware/extracted/fw321/firmware.fdat'
SONY_TAR = ROOT / 'firmware/extracted/fw321/firmware.tar'
B404 = ROOT / 'build/sony_puro_sin_wbi_404'
B404_DAT = B404 / 'package-4.04/firmware_packed.dat'
B404_FDAT = B404 / 'package-4.04/firmware_packed.fdat'
B404_TAR = B404 / 'firmware.tar'
STOCK15 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15'
LIMIT = 104_857_600


def sha(b):
    return hashlib.sha256(b).hexdigest()


def mm(path):
    f = open(path, 'rb')
    return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)


def raw(path):
    return Path(path).read_bytes()


def container(path, compare_fdat=None):
    """Contenedor + FDAT descifrado comparado con el .fdat de al lado (si se da)."""
    buf = mm(path)
    info = A.parse_dat(buf)
    keys = A.load_keys()
    cmp = mm(compare_fdat) if compare_fdat else None
    dec = A.decrypt_fdat(buf, info['fdat_offset'], info['fdat_size'], keys, compare=cmp)
    return buf, info, dec


def fdat_report(buf, info, fdat_path):
    """Cabecera del FDAT (texto plano del .fdat, ya verificado byte a byte) y sha de la partición U."""
    hdr = A.parse_fdat_header(raw(fdat_path)[:512])
    upd = next(fs for fs in hdr['filesystems'] if fs['mode'] == 'U')
    upd_sha = sha(raw(fdat_path)[upd['offset']:upd['offset'] + upd['size']])
    return hdr, upd, upd_sha


def check_no_wbi(tarmv, tar, sumname='0701_part_image_sum/part_image.sum'):
    m = next((x for x in tar['members'] if x['name'] == sumname), None)
    text = bytes(tarmv[m['data_offset']:m['data_offset'] + m['size']]).decode('ascii')
    return {
        'part_sum_sha256': sha(text.encode('ascii')),
        'lineas': len(text.splitlines()),
        'tiene_linea_nflasha5': ',dev/nflasha5,' in text,
        'lineas_nflasha': [ln for ln in text.splitlines() if 'nflasha' in ln],
    }


rep = {}

# ---------------------------------------------------------------- A: DAT oficial 3.21
buf, info, dec = container(SONY_DAT, compare_fdat=SONY_FDAT)
hdr, upd, upd_sha = fdat_report(buf, info, SONY_FDAT)
fdat_mv = mm(SONY_FDAT)
tarmv = memoryview(fdat_mv)[hdr['firmware_offset']:hdr['firmware_offset'] + hdr['firmware_size']]
tar = A.parse_tar(tarmv)
by = {m['name'].rstrip('/'): m for m in tar['members']}


def miembro(name):
    m = by[name]
    return m, bytes(tarmv[m['data_offset']:m['data_offset'] + m['size']])


n5_m, n5 = miembro('0700_part_image/dev/nflasha5')
n15_m, n15 = miembro('0700_part_image/dev/nflasha15')
n3_m, n3 = miembro('0700_part_image/dev/nflasha3')
sums_sony = A.verify_all_sums(tarmv, tar)
rep['oficial_321'] = {
    'dat': str(SONY_DAT.relative_to(ROOT)),
    'dat_size': len(buf), 'dat_sha256': sha(mm(SONY_DAT)),
    'chunks': info['chunks'], 'trailing': info['trailing'],
    'dend_ok': info['dend_stored'] == info['dend_computed'],
    'datv': info.get('datv'), 'prov': info.get('prov'), 'udid': info.get('udid'),
    'fdat_offset': info['fdat_offset'], 'fdat_size': info['fdat_size'],
    'descifrado_bloques': dec.blocks, 'bad_sum': dec.bad_sum[:5], 'bad_flag': dec.bad_flag[:5],
    'bad_len': dec.bad_len[:5], 'plain_size': dec.plain_size,
    'descifrado_igual_a_fdat': dec.first_mismatch_vs_fdat is None,
    'fdat_sha256_fichero': sha(mm(SONY_FDAT)),
    'cabecera': hdr,
    'updater_fs': upd, 'updater_sha256': upd_sha,
    'updater_sha_esperado_e25_06': A.UPDATER_SHA,
    'updater_sha_esperado_build': build.UPDATER_SHA256,
    'tar_size': len(tarmv), 'tar_sha256': sha(tarmv),
    'tar_sha_esperado_fichero': sha(mm(SONY_TAR)),
    'tar_sha_constante_e25_06': A.OFFICIAL_TAR_SHA,
    'tar_miembros': len(tar['members']), 'tar_problemas': tar['problems'],
    'tar_cola': {'tail_blocks': tar['tail_blocks'], 'tail_zero': tar['tail_zero']},
    'nflasha5_presente': True, 'nflasha5_size': n5_m['size'], 'nflasha5_sha256': sha(n5),
    'nflasha15_size': n15_m['size'], 'nflasha15_sha256': sha(n15),
    'nflasha15_igual_stock': sha(n15) == sha(STOCK15.read_bytes()),
    'sums_ok': {k: v['errors'] for k, v in sums_sony.items()},
    'sums_todo_ok': all(not v['errors'] for v in sums_sony.values()),
    'sums_entradas': sum(v['entries'] for v in sums_sony.values()),
    'part_sum': check_no_wbi(tarmv, tar),
}
lay = tpzl.TpzlImage.parse(n3)
rep['oficial_321']['nflasha3_layout'] = {
    'bloques': len(lay.entries), 'tamano': len(n3),
    'violaciones_ldec': tpzl.hardware_violations(lay)[:5],
    'no_alineados_512': sum(o & 0x1FF != 0 for o, _ in lay.entries),
}

# ---------------------------------------------------------------- B: build 4.04
buf4, info4, dec4 = container(B404_DAT, compare_fdat=B404_FDAT)
hdr4, upd4, upd4_sha = fdat_report(buf4, info4, B404_FDAT)
fdat4_mv = mm(B404_FDAT)
tarmv4 = memoryview(fdat4_mv)[hdr4['firmware_offset']:hdr4['firmware_offset'] + hdr4['firmware_size']]
tar4 = A.parse_tar(tarmv4)
by4 = {m['name'].rstrip('/'): m for m in tar4['members']}
sums4 = A.verify_all_sums(tarmv4, tar4)
sony_names = {m['name'].rstrip('/') for m in tar['members']}
new_names = {m['name'].rstrip('/') for m in tar4['members']}
only_sony = sorted(sony_names - new_names)
only_new = sorted(new_names - sony_names)
changed = []
for name in sorted(sony_names & new_names):
    a, b = by[name], by4[name]
    da = bytes(tarmv[a['data_offset']:a['data_offset'] + a['size']])
    db = bytes(tarmv4[b['data_offset']:b['data_offset'] + b['size']])
    if da != db or (a['mode'], a['uid'], a['gid'], a['type']) != (b['mode'], b['uid'], b['gid'], b['type']):
        changed.append(name)
n15_4 = bytes(tarmv4[by4['0700_part_image/dev/nflasha15']['data_offset']:
                     by4['0700_part_image/dev/nflasha15']['data_offset'] + by4['0700_part_image/dev/nflasha15']['size']])
lay4 = tpzl.TpzlImage.parse(n15_4)
rep['build_404'] = {
    'dat': str(B404_DAT.relative_to(ROOT)), 'dat_size': len(buf4), 'dat_sha256': sha(mm(B404_DAT)),
    'sha256sums_dat': (B404 / 'package-4.04/SHA256SUMS').read_text().split()[0],
    'chunks': info4['chunks'], 'trailing': info4['trailing'],
    'dend_ok': info4['dend_stored'] == info4['dend_computed'],
    'datv': info4.get('datv'), 'prov': info4.get('prov'),
    'udid_igual_sony': info4.get('udid_raw') == info.get('udid_raw'),
    'fdat_offset': info4['fdat_offset'], 'fdat_size': info4['fdat_size'],
    'descifrado_bloques': dec4.blocks, 'bad_sum': dec4.bad_sum[:5], 'bad_flag': dec4.bad_flag[:5],
    'bad_len': dec4.bad_len[:5], 'descifrado_igual_a_fdat': dec4.first_mismatch_vs_fdat is None,
    'fdat_sha256_fichero': sha(mm(B404_FDAT)),
    'sha256sums_fdat': (B404 / 'package-4.04/SHA256SUMS').read_text().split()[2],
    'cabecera': {k: hdr4[k] for k in ('magic', 'checksum_stored', 'checksum_computed', 'format', 'mode', 'luw',
                                      'version', 'model', 'region', 'firmware_offset', 'firmware_size', 'num_filesystems')},
    'version_mayor_que_base_321': tuple(map(int, hdr4['version'].split('.'))) > (3, 21),
    'updater_fs': upd4, 'updater_sha256': upd4_sha, 'updater_igual_sony': upd4_sha == upd_sha,
    'tar_size': len(tarmv4), 'tar_sha256': sha(tarmv4),
    'tar_sha_container_json': json.loads((B404 / 'container.json').read_text())['tar_sha256'],
    'tar_sha_igual_a_firmware_tar_de_build': sha(tarmv4) == sha(mm(B404_TAR)),
    'tar_miembros': len(tar4['members']), 'tar_problemas': tar4['problems'],
    'tar_cola': {'tail_blocks': tar4['tail_blocks'], 'tail_zero': tar4['tail_zero']},
    'solo_en_sony': only_sony, 'solo_en_404': only_new, 'miembros_distintos': changed,
    'sums_ok': {k: v['errors'] for k, v in sums4.items()},
    'sums_todo_ok': all(not v['errors'] for v in sums4.values()),
    'sums_entradas': sum(v['entries'] for v in sums4.values()),
    'part_sum': check_no_wbi(tarmv4, tar4),
    'nflasha15_size': len(n15_4), 'nflasha15_sha256': sha(n15_4),
    'nflasha15_igual_stock': sha(n15_4) == sha(STOCK15.read_bytes()),
    'nflasha15_layout': {'bloques': len(lay4.entries), 'tamano': len(n15_4),
                         'cabe_en_particion_100MiB': len(n15_4) <= LIMIT,
                         'violaciones_ldec': tpzl.hardware_violations(lay4)[:5],
                         'no_alineados_512': sum(o & 0x1FF != 0 for o, _ in lay4.entries)},
    'sha256sums_coincide': (B404 / 'package-4.04/SHA256SUMS').read_text().split()[0] == sha(mm(B404_DAT)),
}

# diff textual de part_image.sum (línea que desaparece)
pa = next(m for m in tar['members'] if m['name'].endswith('part_image.sum'))
pb = next(m for m in tar4['members'] if m['name'].endswith('part_image.sum'))
ta = bytes(tarmv[pa['data_offset']:pa['data_offset'] + pa['size']]).decode('ascii').splitlines()
tb = bytes(tarmv4[pb['data_offset']:pb['data_offset'] + pb['size']]).decode('ascii').splitlines()
rep['build_404']['part_sum_diff'] = {'quitadas': [x for x in ta if x not in tb], 'anadidas': [x for x in tb if x not in ta]}

(OUT / 'verificacion-dat-321-y-404.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False))
print(json.dumps({k: (v if k != 'cabecera' else '...') for k, v in rep['oficial_321'].items()}, indent=1, ensure_ascii=False))
print('---')
print(json.dumps(rep['build_404'], indent=1, ensure_ascii=False))
