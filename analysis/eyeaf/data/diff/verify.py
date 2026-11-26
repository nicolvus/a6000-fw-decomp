#!/usr/bin/env python3
"""Verifica las afirmaciones byte-exactas de analysis/eyeaf/a6300_eyeaf_diff.md (solo estático).
Uso: python3 analysis/eyeaf/data/diff/verify.py  -> imprime OK/FALLA por comprobación."""
import os, struct, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))
BASE = 0x43541000
AV = {'A6000': 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin',
      'A6300': 'firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'}
OBJ = {'A6000': 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so',
       'A6300': 'firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so'}
SD = {'A6000': 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libScalarDaemon.so',
      'A6300': 'firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libScalarDaemon.so'}
D = {k: open(os.path.join(ROOT, v), 'rb').read() for k, v in AV.items()}
O = {k: open(os.path.join(ROOT, v), 'rb').read() for k, v in OBJ.items()}
S = {k: open(os.path.join(ROOT, v), 'rb').read() for k, v in SD.items()}
fails = []
def chk(name, cond, extra=''):
    print(('OK   ' if cond else 'FALLA') + ' ' + name + ((' ' + extra) if extra else ''))
    if not cond: fails.append(name)
def off(buf, s):
    i = buf.find(s.encode())
    return None if i < 0 else (i, i + BASE)
# cabecera LIRO y base
# magia: u32 0x4C49524F ("LIRO") en +0x04, que en memoria se lee 4F 52 49 4C
chk('magia LIRO (u32 0x4C49524F) en +0x04 (A6000)', struct.unpack_from('<I', D['A6000'], 4)[0] == 0x4C49524F)
chk('magia LIRO (u32 0x4C49524F) en +0x04 (A6300)', struct.unpack_from('<I', D['A6300'], 4)[0] == 0x4C49524F)
chk('puntero 0x43541044 en +0x0C (A6000)', struct.unpack_from('<I', D['A6000'], 0x0c)[0] == 0x43541044)
chk('puntero 0x43541044 en +0x0C (A6300)', struct.unpack_from('<I', D['A6300'], 0x0c)[0] == 0x43541044)
# av-cam: presencia/ausencia (RTTI de las clases de estado)
chk('RTTI CPafStateEyeStart A6000 en off 0x766b3a',
    D['A6000'].find(b'N6Camera2LC17CPafStateEyeStartE') == 0x766b3a)
chk('RTTI CPafStateEyeStart A6300 en off 0x88ebf9',
    D['A6300'].find(b'N6Camera2LC7PhaseAF5State17CPafStateEyeStartE') == 0x88ebf9)
chk('RTTI CPafStateEyeFocus A6300 en off 0x88ec27',
    D['A6300'].find(b'N6Camera2LC7PhaseAF5State17CPafStateEyeFocusE') == 0x88ec27)
chk('A6000 av-cam tiene CPafStateEyeStart', D['A6000'].count(b'CPafStateEyeStart') == 1)
chk('A6300 av-cam tiene CPafStateEyeStart', D['A6300'].count(b'CPafStateEyeStart') == 1)
chk('A6000 av-cam NO tiene CPafStateEyeFocus', D['A6000'].count(b'CPafStateEyeFocus') == 0)
chk('A6300 av-cam SI tiene CPafStateEyeFocus', D['A6300'].count(b'CPafStateEyeFocus') == 1)
for s, exp6, exp63 in [('CheckSetEyeStartAF', 0, 1), ('SET_EYE_START_AF[%d]', 0, 1),
                       ('LiroSeq ParamCheckErr@%s[eye_start_af]', 0, 1), ('CheckSet', 0, 201),
                       ('b8_pupil_information_data0', 0, 1), ('EyeDetection', 1, 1),
                       ('[CAMERA_MAIN_FC]: Eye data is invalid, but lc flag is true.', 1, 0)]:
    c6, c63 = D['A6000'].count(s.encode()), D['A6300'].count(s.encode())
    chk(f'av-cam "{s}" A6000={exp6} A6300={exp63}', c6 == exp6 and c63 == exp63, f'(real {c6}/{c63})')
# vtables
for tag, vt, ti, slots in [
    ('A6000', 0x43fcd0bc, 0x43ff6e4c, [0x43af45df, 0x43af45c5, 0x43af45c7, 0x43af45e5, 0x43af46cb, 0x43af4727, 0x43af45b1]),
    ('A6300', 0x4418dab4, 0x441d9470, [0x43bd04b3, 0x43bd0465, 0x43bd04a7, 0x43bd04e7, 0x43bd046d, 0x43bd04ed, 0x43bd0591])]:
    o = vt - BASE
    got_ti = struct.unpack_from('<I', D[tag], o)[0]
    got = [struct.unpack_from('<I', D[tag], o + 4 * (i + 1))[0] for i in range(7)]
    chk(f'{tag} vtable {vt:#x} type_info', got_ti == ti, f'{got_ti:#x}')
    chk(f'{tag} vtable slots', got == slots, str([hex(x) for x in got]))
# A6300 EyeFocus vtable
o = 0x4418daf4 - BASE
chk('A6300 vtable EyeFocus 0x4418daf4 type_info 0x441d9494', struct.unpack_from('<I', D['A6300'], o)[0] == 0x441d9494)
# libObj: nombres
for s in ('PARAMID_EYE_START_AF', 'PARAMID_EYE_START_AF_SET', 'PARAMID_EYE_START_AF_ACT',
          'MSGID_SET_EYE_START_AF_CMD', 'MSGID_SET_EYE_START_AF_CMP', 'MSGID_NOTIFY_EYE_START_AF_EVT',
          'VALUEID_AF_KEY_EYE_PRIORITY_AF', 'VALUEID_EYE_START_AF_ON', 'VALUEID_EYE_START_AF_OFF',
          'VALUEID_FOCUSING_STATE_EYE_START', 'SetEyeStartAFForLiro NON SUPPORTED MsgID[0x%04x]',
          'N7CamUser21SequenceSetEyeStartAFE'):
    chk(f'libObj "{s}" en AMBOS modelos', s.encode() in O['A6000'] and s.encode() in O['A6300'])
for s in ('PARAMID_FOCUS_RELEASE_PRIORITY_AF_C', 'VALUEID_FOCUS_PRIORITY_AF_C',
          'VALUEID_RELEASE_PRIORITY_AF_C', 'VALUEID_BALANCE_PRIORITY_AF_C', 'VALUEID_AF_KEY_IR'):
    chk(f'libObj A6300-only "{s}"', s.encode() not in O['A6000'] and s.encode() in O['A6300'])
# libScalarDaemon: nombre y tabla
for tag, ent, val in [('A6000', 0x1b2020, 0x5008), ('A6300', 0x1da9f0, 0x8008)]:
    chk(f'{tag} PARAMID_CAMSETTING_EYE_START_AF id', struct.unpack_from('<I', S[tag], ent)[0] == val,
        f'{struct.unpack_from("<I", S[tag], ent)[0]:#06x}')
print()
print('FALLOS:', len(fails))
sys.exit(1 if fails else 0)
