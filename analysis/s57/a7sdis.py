import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
from gpio_calls_diff import MODELS,B
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
d=MODELS['A7S']['path'].read_bytes(); md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
a,b=int(sys.argv[1],0),int(sys.argv[2],0)
for i in md.disasm(d[a-B:b-B],a): print('%x %s %s'%(i.address,i.mnemonic,i.op_str))
