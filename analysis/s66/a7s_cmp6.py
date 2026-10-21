import sys
sys.path.insert(0,'analysis/s58')
from tdis import data
A7=data('A7S'); B=0x43541000
o=0x43ca1069-B
seg=A7[o-200:o+200]
i=0
print('--- A7S [BL][HS] region ---')
while i<len(seg):
    if seg[i]!=0:
        e=seg.find(b'\0',i)
        if e<0: break
        t=seg[i:e].decode('latin1')
        if t.strip(): print(f'  {0x43ca1069-200+i:#x}: {t!r}')
        i=e+1
    else: i+=1
# A7S update region 0x43c9f7ff onward
print('--- A7S FW-update region ---')
o=0x43c9f7ff-B
seg=A7[o-100:o+400]
i=0
while i<len(seg):
    if seg[i]!=0:
        e=seg.find(b'\0',i)
        if e<0: break
        t=seg[i:e].decode('latin1')
        if t.strip(): print(f'  {0x43c9f7ff-100+i:#x}: {t!r}')
        i=e+1
    else: i+=1
