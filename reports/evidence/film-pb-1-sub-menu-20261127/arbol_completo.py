import struct, sys
sys.path.insert(0,'/tmp')
sys.path.insert(0,'reports/evidence/film-pb-1-sub-menu-20261127')
from arbol_paginas import sites, reloc_map, w32
from elfhelper import Elf
BASE='firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/'
e=Elf(BASE+'lib/viewUnified2.so'); rel=reloc_map(e)
by_obj={}
for arr,cnt,obj,va in sites(e):
    kids=[]
    for k in range(cnt):
        cell=arr+4*k; r=rel.get(cell)
        if r and r[0]==2: kids.append(('sym',r[1]))
        elif r and r[0]==23: kids.append(('obj',w32(e,cell)))
        else: kids.append(('raw',w32(e,cell)))
    by_obj.setdefault(obj,[]).append((va,arr,cnt,kids))
kids_of=set(v for o in by_obj for va,arr,cnt,k in by_obj[o] for t,v in k if t=='obj')
roots=sorted((o for o in by_obj if o and o not in kids_of))
target='NtscPalSEL'
def walk(o,depth,seen):
    for va,arr,cnt,kids in by_obj.get(o,[]):
        names=[]
        for t,v in kids:
            if t=='sym': names.append(v.replace('cmnViewSettingNodeRoot',''))
            elif t=='obj': names.append('{%#x}'%v)
            else: names.append('raw')
        flag=' <<<' if any(target in (n or '') for n in names) else ''
        print('%s%#x cnt=%d @%#x: %s%s' % ('  '*depth,o,cnt,va,', '.join(names),flag))
        for t,v in kids:
            if t=='obj' and v not in seen:
                seen.add(v); walk(v,depth+1,seen)
seen=set()
for r in roots:
    if r not in by_obj: continue
    va,arr,cnt,kids=by_obj[r][0]
    if all(t!='obj' for t,v in kids): continue
    walk(r,0,seen)
