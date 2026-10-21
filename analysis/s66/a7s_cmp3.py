import sys
sys.path.insert(0,'analysis/s58')
from tdis import data
A7=data('A7S'); B=0x43541000
def fnd(sub):
    i=A7.find(sub.encode()); return hex(i+B) if i>=0 else None
for s in [
 '[BL]FirmUp Error : CAIF CASND LUPDT_INFO',
 '[BL]FirmUp Error : CAIF CASND LUPDT_DATA',
 '[BL]PREPARE UPDATE REQ RCV','[BL]PREPARE UPDATE TIME_OUT',
 '[BL]UUD CallBack : MSGID_GET_VERSION','[BL]UUD CallBack : MSGID_PREPARE UPDATE',
 '[BL]UUD CallBack : MSGID_PREPARE_UPDATE',
 '[L->B]UPDATE_ON','[B->L]UPDATE_DATA','[L->B]CS_CREDIT','[B->L]CS_CREDIT',
 '[BL]UART_HZ 750','[BL][HS]CS_HIGH','[BL]CHG FREQ','[BL]EclipseDataComState',
 'LIF CREDIT','LIF Command Change','[LENS_PDR]','BonoboDSP',
 '[BL]SYSTEM_HZ','[BL]WAIT NEXTVD','EclipseDataComState']:
    print(f'{s!r:55} -> {fnd(s)}')
print('A7S [BL] count', A7.count(b'[BL]'), '| BonoboDSP', A7.count(b'BonoboDSP'))
