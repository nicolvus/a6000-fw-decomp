"""S57-D: matriz efectiva de registros IMX235 (A7S 3.20) por modo: filas de 40 B {ptr, 34 valores, 2 relleno}; registro 5 B {dev,0,dir16,dato} en ptr-2.
Reutiliza el análisis S52/S56; salida JSON con dev/dirección/valores por modo."""
import sys, struct
from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
from gpio_calls_diff import MODELS, B
d = MODELS['A7S']['path'].read_bytes()
u32 = lambda a: struct.unpack_from('<I', d, a - B)[0]
MT, RT, N = 0x43fee370, 0x43fee598, 34
modes = [u32(MT + 4 * i) for i in range(N)]
rows, a = [], RT
while (p := u32(a)) and B < p < B + len(d):
    rec = d[p - 2 - B:p + 1 - B]            # [dev?, 0?, ...] se valida abajo
    rows.append(dict(ptr=p, raw=d[p - 4 - B:p + 1 - B].hex(), init=d[p - B], vals=list(d[a + 4 - B:a + 4 + N - B])))
    a += 40
rows = [r for r in rows if r['raw'][:2] in ('81', '83')]   # la 36.ª fila leída es un puntero espurio a código (dev 0x00): fuera de la matriz
if __name__ == '__main__':
    print(len(rows), 'filas'); 
    for r in rows[:6]: print(hex(r['ptr']), r['raw'], r['init'], r['vals'][:6])
