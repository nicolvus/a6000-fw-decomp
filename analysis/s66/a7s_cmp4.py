import sys, re
sys.path.insert(0,'analysis/s58')
from tdis import data
A7=data('A7S'); B=0x43541000
def strings_with(kw):
    out=[]; kb=kw.encode()
    for m in re.finditer(re.escape(kb), A7):
        i=m.start(); s=max(0,i-30); e=min(len(A7),i+50)
        seg=A7[s:e]
        for piece in seg.split(b'\0'):
            if kb in piece:
                try: out.append((hex(s+B+seg.find(piece)), piece.decode('latin1')))
                except: pass
    return out[:3]
for kw in ['PREPARE UPDATE','UUD CallBack','UPDATE_ON','UPDATE_DATA','CS_CREDIT','UART_HZ','CS_HIGH','CHG FREQ','EclipseDataCom','LIF CRED','SYSTEM_HZ','NEXTVD','LUPDT','FirmUp','LENS_PDR','BonoboDSP','paritycheck','latch failed','ATTACH_INFO','STARTUP_INFO']:
    r=strings_with(kw)
    print(f'== {kw} ==')
    for a,t in r: print(f'   {a}: {t!r}')
