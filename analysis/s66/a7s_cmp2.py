"""Comparación A6000 vs A7S del dispatcher UUD y del emisor LUPDT a nivel de bytes.
Busca en A7S el patrón distinctive del dispatcher UUD (tbh sobre msg 0..4) cerca de
la cadena UUD CallBack."""
import sys, struct
sys.path.insert(0,'analysis/s58')
from tdis import data
A=data('A6000'); A7=data('A7S'); B=0x43541000
def fnd(d,sub):
    i=d.find(sub.encode()); return (i+B) if i>=0 else None
# A6000 verified: dispatcher UUD @ 0x436fe500, emitter LUPDT @ 0x436fe070, result @ 0x436fe994
# A7S string UUD CallBack MSGID_GET_VERSION
for model,d in [('A6000',A),('A7S',A7)]:
    a=fnd(d,'[MOUNT_INFO]: [BL]UUD CallBack : MSGID_GET_VERSION')
    b=fnd(d,'[MOUNT_ERROR]: [BL]FirmUp Error : CAIF CASND LUPDT_INFO')
    c=fnd(d,'[MOUNT_DEBUG]: [BL]PREPARE UPDATE REQ RCV')
    print(f'{model}: UUD_GETVER@{a and hex(a)} LUPDT_INFO@{b and hex(b)} PREPARE_REQ@{c and hex(c)}')
# Count [MOUNT_] strings
for model,d in [('A6000',A),('A7S',A7)]:
    print(f'{model}: [MOUNT_] count =', d.count(b'[MOUNT_'), '| [LENS_PDR] count =', d.count(b'[LENS_PDR]'), '| BonoboDSP count =', d.count(b'BonoboDSP'))
