"""S57: utilidades comunes (inicios de función por 'push {..lr}', caché en /tmp)."""
import sys, pickle
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 's56')); sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
import rec_users as R
from gpio_calls_diff import disasm
CACHE = Path('/tmp/claude-1000/fstarts.pkl')
def fstarts():
    if CACHE.exists(): return pickle.load(open(CACHE, 'rb'))
    st = sorted(i.address for i in disasm(R.d) if i.mnemonic in ('push', 'push.w') and 'lr' in i.op_str)
    CACHE.parent.mkdir(parents=True, exist_ok=True); pickle.dump(st, open(CACHE, 'wb')); return st
