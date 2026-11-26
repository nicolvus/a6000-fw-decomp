#!/usr/bin/env python3
"""Reconstruye las constantes de geometria del FBS usadas por FlashLib/DFB en libmpr.so.
Escribe el extracto en reports/evidence/film-pb-1-sub-nflasha4-20261126/libmpr-geometria.txt"""
import importlib.util, struct, re
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
import os
HERE=os.path.dirname(os.path.abspath(__file__))
an=load(os.path.join(HERE,'ann.py'),'an'); rd=an.rd
D=rd._data
out=[]
def P(*a): out.append(' '.join(str(x) for x in a))
P("### libmpr.so -> analysis/camera-extract/usr/lib/libmpr.so (ARM, base VA 0, offset == VA en el 1er PT_LOAD)")
P("### Desensamblado con capstone en modo Thumb-2; simbolos reales de .dynsym (no hay tabla de simbolos local).")
P()
P("## 1. Simbolos FlashLib relevantes (de .dynsym)")
for name,va,sz in [("FlashLib::Init(MPR::SystemType)",0x2B696C,560),("FlashLib::m_blockNum",0xA36C7C,4),
                   ("FlashLib::m_sectorNum",0xA36C74,4),("FlashLib::m_sectorSize",0xA36C80,4),
                   ("FlashLib::CheckExistSector(u64)",0x2B8B48,52),("FlashLib::m_packWriteInfo",0xA36C89,833),
                   ("FlashLib::m_fileTypeSizeInfo",0x9D2794,624)]:
    P("  %#010x %5d  %s"%(va,sz,name))
P()
P("## 2. FlashLib::Init: la geometria son PARAMETROS DE SALIDA de DFB::Init (no una tabla por modelo)")

import contextlib, io
f=io.StringIO()
with contextlib.redirect_stdout(f): an.dump(0x2b696c,400)
txt=f.getvalue().splitlines()
for l in txt:
    if any(k in l for k in ('0xa36c7c','0xa36c74','0xa36c80','#0x2b0ffc','#0x23fd7a','#0x1202e2','0x2b6a80','0x2b6a88')): P("   "+l)
P()
P("   => r1=&m_blockNum(0xA36C7C) r2=&m_sectorNum(0xA36C74) r3=&m_sectorSize(0xA36C80) hacia 0x2B0FFC")
P("   => despues: malloc(m_sectorSize) en 0x2B6A80-0x2B6A8C (buffer de alineamiento de sector)")
P()
P("## 3. 0x2B0FFC es un thunk a 0x2A9AD8 = DvdFlashBackupLib::Init")
for l in ('002b0ffc','002b0ffe','002b1000','002b1004'):
    pass
P("   002b0ffc  push {r7,lr} ; 002b1000 pop.w {r7,lr} ; 002b1004 b.w 0x2A9AD8")
P()
P("## 4. DFB::Init: de donde salen los tres valores (globlos proxy en .bss)")
f=io.StringIO()
with contextlib.redirect_stdout(f): an.dump(0x2B0FFC,2000)
txt=f.getvalue().splitlines()
for l in txt:
    if any(k in l for k in ('0x9e3c04','0x9e3bf4','0x9e3cb0','0x9e4128','0x9e4d64','0x9e4874','0x9e4840','0x9e5580','0x9e5588','0x9e4128','0x9e3ce8')):
        P("   "+l)
P()
P("## 5. CtrlInfoBlockNum: heuristica por numero total de bloques (0x2A9C4A-0x2A9C7E)")
for l in ['002a9c4a  cmp r1, #0x30','002a9c70  movs r3, #2','002a9c74  cmp r1, #0x50','002a9c78  movs r3, #6','002a9c7c  movs r3, #8','002a9c7e  str r3,[r5]     ; CtrlInfoBlockNum','002a9c80  log "[DFB]AllBlockNum:%d / CtrlInfoBlockNum:%d"']:
    P("   "+l)
P("   allBlockNum = 10 MiB / 128 KiB = 80  ->  0x30 < 80 <= 0x50  ->  CtrlInfoBlockNum = 6")
P("   (los tres volcados usan exactamente 6 bloques FBS: 0..5)")
P()
P("## 6. Direccionamiento de sector = indice << 10  (sectorSize = 1024, constante de compilacion)")
f=io.StringIO()
with contextlib.redirect_stdout(f): an.dump(0x2B0FFC,2000)
txt=f.getvalue().splitlines()
for l in txt:
    if '#0xa' in l and ('lsl' in l or 'lsr' in l): P("   "+l)
P()
P("## 7. Test de sector en blanco: 0x2B061E (unico test a nivel de sector en libmpr)")
f=io.StringIO()
with contextlib.redirect_stdout(f): an.dump(0x2B061E,40)
for l in f.getvalue().splitlines(): P("   "+l)
P("   => lee los 4 primeros bytes como u32 LE y devuelve 0 solo si valen 0xFFFFFFFF")
P()
P("## 8. Cadenas relevantes de libmpr.so")
for va in (0x7DD572,0x7E3CCE,0x7E003B,0x7E0052,0x7E0069,0x7E0080,0x7E0097,0x7E0139):
    e=D.find(b'\x00',va); P("   %#010x  %s"%(va, D[va:e].decode('latin1')))
P()
P("## 9. Lo que NO esta en libmpr.so")
for pat in (b'\x4a\x00\x4a\x00', b'draCNV'):
    offs=[m.start() for m in re.finditer(re.escape(pat),D)]
    P("   patron %-14r: %d apariciones %s"%(pat,len(offs),[hex(o) for o in offs[:5]]))
P("   (las tres de 4a004a00 caen dentro de la tabla de saltos 'tbh' de 0x4245DA; no es una constante)")
open(os.path.join(HERE,'libmpr-geometria.txt'),'w').write('\n'.join(out)+'\n')
print('\n'.join(out))
