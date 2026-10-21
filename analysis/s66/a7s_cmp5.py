import sys, re
sys.path.insert(0,'analysis/s58')
from tdis import data
A7=data('A7S'); B=0x43541000
def has(sub):
    i=A7.find(sub.encode()); return hex(i+B) if i>=0 else None
# Confirm A7S [BL] strings relevant to FW update present/absent
for s in ['[BL]FirmUpReq Error','[BL]GetLensVersion Error','[BL]LensFirmUpdateResult','[BL]LENS FIRMERR',
          '[BL]UPDATE UNPLUG USB','[BL]PREPARE UPDATE OK','[BL]PREPARE UPDATE NG','[BL]UPDATE times',
          'MSGID_GET_FORCE_FIRMUP','MSGID_FIRM_UP_REQ','MSGID_UNPLUG_USB','meg_id illegal',
          '[BL][L->B]UART_HZ NG','[BL]UART_HS_COMPLETE','[BL][HS]','BonoboDSP_Send: Data latch failed!\n']:
    print(f'{s!r:45} -> {has(s)}')
# BonoboDSP context: dump surrounding strings
o=0x43ca167b-B
seg=A7[o-80:o+180]
i=0
print('--- A7S BonoboDSP region ---')
while i<len(seg):
    if seg[i]!=0:
        e=seg.find(b'\0',i)
        if e<0: break
        t=seg[i:e].decode('latin1')
        if t.strip(): print(f'  {0x43ca167b-80+i:#x}: {t!r}')
        i=e+1
    else: i+=1
