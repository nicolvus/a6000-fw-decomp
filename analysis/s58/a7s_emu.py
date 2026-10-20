"""S58-C: arnés Unicorn para C_Imager de la A7S (IMX235, firmware 3.20): ejecuta el código real de SetMode/SetExposure/SetRead/Execute.
Simplificaciones: llamadas fuera de AMBITO -> 0 (stub; se registran); memoria sin mapear = relleno 0 (o patrón); ITSTATE limpiado tras bloques IT (Unicorn 2.1.4);
sin hardware P2S real: las escrituras MMIO se capturan; objeto C_Imager sin constructor (campos a cero salvo vtable): ver limitaciones en el informe."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent / 's57')); sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
from wtrace import W
from imx235_matrix import rows
VT = 0x43fce050                 # vtable (GOT 0x4402ac80 -> 0x43fce048, +8)
SETMODE, SETEXP, SETREAD, EXEC = 0x436f3b44, 0x436f4168, 0x436f4a94, 0x436f5a14
AMBITO = [(0x436f2000, 0x43700000), (0x43ad9000, 0x43adb000), (0x43550000, 0x43570000)]
O, ARG = 0x45600000, 0x45700000
OVR = 0x43de4910
class A7S(W):
    def __init__(s, fill=0, ambito=None, stubfn=None, **k):
        super().__init__('A7S', ambito=ambito or AMBITO, fill=fill, ranges=[(0xf3000000, 0xfd000000, 'MMIO')], stubfn=stubfn, **k)
        s.w32(O, VT)
        s.u.mem_write(OVR, b'\xff' * 0x100)   # estructura de parámetros de depuración (0xFF = sin sustitución); BSS=0 en la imagen: ver informe
        s.recptr = [r['ptr'] for r in rows]
    def regs(s): return [s.rd(p, 1)[0] for p in s.recptr]          # vista histórica S57; usar shadow para el banco completo
    def setmode(s, mode, sub=0):
        s.u.mem_write(ARG, bytes(0x40)); s.w32(ARG, mode); s.u.mem_write(ARG + 4, bytes([sub]))
        return s.call(SETMODE, O, ARG)
    def setexposure(s, shd=0x100, svd=0, spl=0, shut=0, w12=0):
        s.u.mem_write(ARG, bytes(0x40)); s.w32(ARG, shd); s.w16(ARG + 4, svd); s.w16(ARG + 6, spl); s.u.mem_write(ARG + 9, bytes([shut])); s.w16(ARG + 0xc, w12)
        return s.call(SETEXP, O, ARG)
    def setread(s, agc=0x0100, b6=0):
        s.u.mem_write(ARG + 0x100, bytes(0x40)); s.w16(ARG + 0x102, agc); s.u.mem_write(ARG + 0x106, bytes([b6]))
        return s.call(SETREAD, O, ARG + 0x100, 0, 0)
    def execute(s):
        return s.call(EXEC, O)
    def shadow(s):
        return shadow(s)

R0 = 0x44021ebc          # 98 registros sombra {u16 dev, u16 dirección, u16 dato}, paso 6; matriz de modos: 69 filas
NREC = 98
def shadow(e):
    """Mapa (dev, dirección) -> (dev, dato) del banco sombra completo (98 registros; hay direcciones repetidas con otro dev)."""
    out = {}
    for k in range(NREC):
        dev, ad, dat = struct.unpack('<HHH', e.rd(R0 + 6 * k, 6)); out[(dev, ad)] = (dev, dat & 0xff)
    return out
