import re,bisect,pickle,collections,sys
ins=[]
for l in open('av.dis'):
    m=re.match(r'([0-9a-f]+): (?:[0-9a-f]{4} )+(\S+)\s*(.*)',l.strip())
    if m: ins.append((int(m.group(1),16),m.group(2),m.group(3)))
starts=[a for a,op,ar in ins if ('push' in op or 'push' in ar) and 'lr' in ar]
fn=lambda a: starts[bisect.bisect_right(starts,a)-1]
callers=collections.defaultdict(list)
for a,op,ar in ins:
    if op in('bl','blx','b.w') and re.match(r'0x[0-9a-f]+$',ar): callers[int(ar,16)].append(a)
pickle.dump((dict(callers),starts),open('calls.pkl','wb'))
