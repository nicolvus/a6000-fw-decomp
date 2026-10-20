"""S58: índice de llamadas bl/b.w/blx (A6000/A7S) cacheado; uso: calls.py MODEL 0xTARGET... -> llamadores"""
import sys, pickle, os, bisect
from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
from tdis import data, cache
from strrefs import sweep
def index(m):
    c = cache(f'calls_{m}.pkl')
    if os.path.exists(c): return pickle.load(open(c, 'rb'))
    ins = sweep(data(m)); calls = {}; starts = []
    for i in ins:
        if i.mnemonic in ('push', 'push.w') and 'lr' in i.op_str: starts.append(i.address)
        if i.mnemonic in ('bl', 'blx', 'b.w') and i.op_str.startswith('#'):
            calls.setdefault(int(i.op_str[1:], 16), []).append((i.address, i.mnemonic))
    pickle.dump((calls, starts), open(c, 'wb')); return calls, starts
def callers(m, t):
    calls, starts = index(m)
    return [(hex(a), mn, hex(starts[bisect.bisect_right(starts, a) - 1])) for a, mn in calls.get(t, [])]
if __name__ == '__main__':
    for t in sys.argv[2:]: print(t, callers(sys.argv[1], int(t, 0)))
