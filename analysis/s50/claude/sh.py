import re,sys
ins=[l.strip() for l in open('av.dis')]
a0,a1=int(sys.argv[1],16),int(sys.argv[2],16); out=[]
for l in ins:
    a=int(l.split(':')[0],16)
    if a0<=a<a1: out.append(f"{a:x} "+re.sub(r'^(?:[0-9a-f]{4} )+','',l.split(' ',1)[1]))
print(' | '.join(out))
