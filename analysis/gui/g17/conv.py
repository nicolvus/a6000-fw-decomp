"""Caso 0x4066 del conversor CamMsgConv de libObj (sub #0x4000 ; cmp ; tbh) → función y escrituras al buffer."""
import struct,sys
from capstone import *
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
def case_target(d, conv, msg):
    for i in md.disasm(d[conv:conv+0x400],conv):
        if i.mnemonic=='sub.w' and '#0x4000' in i.op_str: sub=i
        if i.mnemonic=='tbh' and i.address>conv+0x100:
            base=i.address+4; idx=msg-0x4000
            return base+2*struct.unpack_from('<H',d,base+2*idx)[0]
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read(); conv=int(sys.argv[2],16)
    t=case_target(d,conv,0x4066); print('caso 0x4066 ->',hex(t))
    for i in md.disasm(d[t:t+0x30],t): print(f'  {i.address:#x} {i.mnemonic} {i.op_str}')
