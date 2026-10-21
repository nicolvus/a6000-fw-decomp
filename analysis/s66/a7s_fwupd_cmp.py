"""A7S: localizar el clúster FW-update equivalente vía pic_refs de cadenas y comparar
la función emisora LUPDT con A6000 (Capstone+bytes)."""
import sys, struct
sys.path.insert(0,'analysis/s58'); sys.path.insert(0,'analysis/s62')
from tdis import data
from pic_refs import pic_refs
A=data('A6000'); A7=data('A7S'); B=0x43541000
# Cadena clave del emisor LUPDT en A6000: '[BL]FirmUp Error : CAIF CASND LUPDT_INFO' 0x43c9a09f (A6000)
# En A7S: 0x43c957ff
refs=pic_refs('A7S',[0x43c957ff])
print('A7S pic_refs LUPDT_INFO:', refs)
