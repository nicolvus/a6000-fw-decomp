import sys, collections, struct, hashlib, math

SEC=1024
FILES={
 'D1':'analysis/camera-dumps/nand-20261020/dev_nflasha4.bin',
 'D2':'analysis/camera-dumps/nand-20261105/dev_nflasha4.bin',
 'D3':'analysis/camera-dumps/nand-20261105-total/dev_nflasha4.bin',
}
def runs(b, fill=0xFF):
    """devolver lista (start,len,value_is_not_fill)"""
    out=[]; i=0; n=len(b)
    while i<n:
        j=i
        while j<n and b[j]==fill: j+=1
        if j>i: out.append((i,j-i,'F'))
        if j>=n: break
        k=j
        while k<n and b[k]!=fill: k+=1
        out.append((j,k-j,'D'))
        i=k
    return out

def entropy(b):
    if not b: return 0.0
    c=collections.Counter(b); n=len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def census(path):
    d=open(path,'rb').read()
    n=len(d)//SEC
    info=[]
    for s in range(n):
        sec=d[s*SEC:(s+1)*SEC]
        magic = sec[4:8]==b'\x4a\x00\x4a\x00'
        blank = sec.count(0xFF)==SEC
        marker = sec.find(b"draCNV4'")
        info.append(dict(s=s, magic=magic, blank=blank, marker=marker,
                         nz=SEC-sec.count(b'\xff')))
    return d, info

def recs(sec, off=8, stride=8, end=SEC, term=None):
    term = term or b'\xff'*stride
    out=[]; p=off
    while p+stride<=end:
        e=sec[p:p+stride]
        if e==term: break
        out.append((p,e)); p+=stride
    return out

if __name__=='__main__':
    for tag,path in FILES.items():
        d,info=census(path)
        print("="*70); print(tag, path, len(d), "bytes =", len(d)//SEC, "sectores de", SEC)
        print("  sectores con magic 4a004a00: %d"%sum(1 for i in info if i['magic']))
        print("  sectores totalmente 0xFF   : %d"%sum(1 for i in info if i['blank']))
        print("  con marcador draCNV4'      : %d"%sum(1 for i in info if i['marker']>=0))
        mo=collections.Counter(i['marker'] for i in info if i['marker']>=0)
        print("  offset del marcador       :", mo.most_common(5))
        ms=[i['s'] for i in info if i['magic']]
        print("  rango de sectores con magic: %d..%d"%(min(ms),max(ms)))
        # gaps
        gaps=[]
        for a,b in zip(ms,ms[1:]):
            if b!=a+1: gaps.append((a,b,b-a-1))
        print("  huecos (sector_prev,next,n):", gaps[:10], "total", len(gaps))
