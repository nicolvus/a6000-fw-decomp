"""S201 — Tabla de comparación de registros por subsistema: IMX210 (A6000 fw3.21)
vs IMX235 (A7S fw3.20). Genera analysis/s201_imx210_imx235_registers/compare.json
con la tabla funcional por subsistema y la clasificación idéntico / distinto /
ausente-en-A6000.

Fuentes de bytes (no se ejecuta firmware):
  - IMX210: vector 0x43fe995c (119 registros) + rec_map (S56/S57), SetExposure
    0x436d6f6c, Execute 0x436d839c, ShutMode/SSB ID1.
  - IMX235: matriz 0x43fee370 (34 modos) + filas 0x43fee598 (35 registros),
    selector de modo 0x43826d58 (tipo==2 -> silent 0x4e/0x4f).
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
A7S   = ROOT / 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

def u16(d, a): return struct.unpack_from('<H', d, a - B)[0]
def u32(d, a): return struct.unpack_from('<I', d, a - B)[0]

def load_imx210():
    d = A6000.read_bytes()
    tab = [u32(d, 0x43fe995c + 4 * i) for i in range(119)]
    return {p: struct.unpack_from('<H', d, p - B)[0] for p in tab}

def load_imx235():
    d = A7S.read_bytes()
    mt = [u32(d, 0x43fee370 + 4 * i) for i in range(34)]
    rows = []
    a = 0x43fee598
    while True:
        p = u32(d, a)
        if not p or not (B < p < B + len(d)):
            break
        raw = d[p - 4 - B:p + 1 - B].hex()
        if raw[:2] in ('81', '83'):
            rows.append({'ptr': p, 'dev': raw[:2], 'dir': u16(d, p - 2),
                             'init': d[p - B],
                             'vals': list(d[a + 4 - B:a + 4 + 34 - B])})
        a += 40
    return mt, rows

IMX210 = load_imx210()
IMX235_MODES, IMX235_ROWS = load_imx235()

# ---------- Tabla por subsistema ----------
# Cada entrada: subsistema, campo, IMX210 (A6000), IMX235 (A7S),
# clasificacion (IDENTICO/DISTINTO/AUSENTE_EN_A6000), notas, evidencia (direcciones bytes)
SUBSYSTEMS = [
 {
  'subsistema': 'Selección de modo de lectura',
  'campo': 'Cantidad de modos de lectura',
  'imx210': '13 modos (SetMode devuelve error 2 para 0x4e/0x4f)',
  'imx235': '34 modos, incl. 0x4e/0x4f dedicados a Silent (índices 29,30)',
  'clasificacion': 'DISTINTO',
  'notas': 'La A7S añade dos modos de lectura exclusivos de Silent; el IMX210 no los define.',
  'evid': 'A6000 rec_map (119 IDs, sin modo silencioso); A7S 0x43fee370[29]=0x4e, [30]=0x4f'},
 {
  'subsistema': 'Selección de modo de lectura',
  'campo': 'Selector de modo (drive mode)',
  'imx210': 'SetMode carga columna de matriz por modo (0x436d6570, matriz 0x43fe9b74)',
  'imx235': 'Selector 0x43826d58(modo, sub, tipo): tipo==2 -> 0x4e/0x4f (silent); '
         'sin Silent: 0x0b/0x35/0x17; modo 5 -> 0x0c',
  'clasificacion': 'DISTINTO',
  'notas': 'La A7S selecciona Silent mediante el parámetro `tipo` (drive mode), no por un parámetro de obturador.',
  'evid': 'A7S bytes 0x43826d58-0x43826db0: cmp r2,#2 (02 2a); movs r0,#0x4e (4e 20); movs r0,#0x4f (4f 20)'},
 {
  'subsistema': 'Obturador silencioso / electrónico',
  'campo': 'Parámetro CheckSet* de LiroSeq (obturador)',
  'imx210': '0/0 CheckSet*, 0/0 SilentShutterMode, 0/0 sc_ShutDrive (S169 vigente)',
  'imx235': '0/0 CheckSet*, 0/0 SilentShutterMode, 0/0 sc_ShutDrive (S169 vigente)',
  'clasificacion': 'IDENTICO',
  'notas': 'Ambos carecen de la capa de validación de parámetros de obturador que sí tiene el A6300. '
        'La A7S implementa Silent por drive mode + tabla de timings, no por LiroSeq.',
  'evid': 'S169 (0/0 en A6000 y A7S); barrido de bytes sin CheckSetSilentShutterMode/Sc_ShutDrive'},
 {
  'subsistema': 'Obturador silencioso / electrónico',
  'campo': 'Mensaje a Liro (…ForLiro) para obturador',
  'imx210': 'SetShutterTypeForLiro ausente; …ForLiro en lista de rechazo (S174)',
  'imx235': 'SetShutterTypeForLiro ausente; …ForLiro en lista de rechazo (S174)',
  'clasificacion': 'IDENTICO',
  'notas': 'No hay mensaje a Liro que active el obturador electrónico en ninguno de los dos.',
  'evid': 'S174 (…ForLiro 0/0/6 solo A6300; rechazo en A6000/A7S); bytes sin SetShutterTypeForLiro'},
 {
  'subsistema': 'Temporización de exposición',
  'campo': 'Registros de tiempo (svd/shd/spl)',
  'imx210': 'ID3-ID8: svd (12b), shd (14b), spl (12b); espejo condicional 0x144-0x149',
  'imx235': 'Columnas de matriz por modo (valores estáticos por modo de lectura)',
  'clasificacion': 'DISTINTO',
  'notas': 'El IMX210 expone svd/shd/spl como registros de sombra programables; el IMX235 los fija por '
        'columna de modo. No se recuperó fórmula equivalente para IMX235.',
  'evid': 'A6000 rec_map ID3-8; S57-C fórmula svd=n·svr_num−1; A7S matriz 0x43fee598'},
 {
  'subsistema': 'Temporización de exposición',
  'campo': 'Fórmula / significado de svd',
  'imx210': 'svd = n·svr_num − 1 (o n/VdNum − 1); contador de pasos del host / periodos VD (INFERENCIA)',
  'imx235': 'No recuperada; valores de columna por modo sin semántica física asignada',
  'clasificacion': 'DISTINTO',
  'notas': 'Solo el IMX210 tiene fórmula documentada; el fin de integulación no se demuestra en ninguno.',
  'evid': 'S57-C (0x4381106c valida svd); S57-D (IMX235 sin función asignada a columnas)'},
 {
  'subsistema': 'Temporización de exposición',
  'campo': 'Fin de integración (reescritura al terminar)',
  'imx210': 'No hay reescritura de registros al terminar la exposición (ExposureTimerEnd! sin SetExposure)',
  'imx235': 'No hay comando adicional de "terminar integración" en matriz ni pulso (S57-D)',
  'clasificacion': 'IDENTICO',
  'notas': 'Ambos carecen de operación de fin de integración identificada; NO VERIFICADO si el sensor la hace internamente.',
  'evid': 'S57-F (ExposureTimerEnd! no reescribe sensores); S57-D D.6'},
 {
  'subsistema': 'Interfaz de transporte (P2S / CISIF)',
  'campo': 'Bloque y canal de transporte de registros',
  'imx210': 'P2S(DFE0), MMIO 0xfc088300/0xfc088800/0xfc088900, trama 81|len|81|AH AL|datos',
  'imx235': 'Mismo hardware P2S (mismas bases MMIO y programación de bloque, S56-15)',
  'clasificacion': 'IDENTICO',
  'notas': 'El transporte es idéntico; difieren los registros y valores que se envían (sensor distinto).',
  'evid': 'S56-15 (A7S mismo hardware P2S); S56-5/6 (formato trama A6000)'},
 {
  'subsistema': 'Strobe de configuración (SSB)',
  'campo': 'Pulso SSB',
  'imx210': 'Bit 3 del dato de ID1, enviado dos veces (1,0) en el mismo lote P2S',
  'imx235': 'Bit 0x10 del byte +4 de un registro ([O+0x3d7]) dentro de SetExposure/SetRead',
  'clasificacion': 'DISTINTO',
  'notas': 'Mismo concepto (strobe de registro que acompaña cambios de exposición), bit y registro distintos.',
  'evid': 'A6000 0x436d7c08 (bit 3 ID1); A7S 0x436f459c (bit 0x10 byte +4)'},
 {
  'subsistema': 'ShutMode (selector de obturación del firmware)',
  'campo': 'Valores y codificación',
  'imx210': 'ShutMode 0-4; ID1 bits 2/7/4/6; en captura real solo 0 y 1',
  'imx235': 'ShutMode 2 no soportado ("is not supported"); codificación de bits distinta',
  'clasificacion': 'DISTINTO',
  'notas': 'No hay mapeo 1:1 de ShutMode entre sensores; el significado eléctrico de cada bit es NO VERIFICADO.',
  'evid': 'S56-10/17 (ShutMode ID1 bits y tbb A7S vs A6000)'},
 {
  'subsistema': 'Registro ID1 / modo de lectura',
  'campo': 'ID1 (dirección 0x0001)',
  'imx210': 'ID1 duplicado (A=0x4401ca2c, B=0x4401c734); modo + ShutMode + strobe',
  'imx235': 'Registro 0x000c distingue 0x4e (0x10) de 0x4c (0x20); 0x000a distingue 0x4f (0x01) de 0x4d (0x02)',
  'clasificacion': 'DISTINTO',
  'notas': 'No hay correspondencia por dirección entre sensores (S57-D D.5); el registro equivalente de modo/silent es distinto.',
  'evid': 'A6000 rec_map ID1; A7S matriz filas 0x000c/0x000a'},
]

def main():
    out = {
        'phase': 'S201', 'date': '2026-10-22', 'agent': 'A',
        'imx210_sha256': None, 'imx235_sha256': None,
        'imx210_registers': len(IMX210),
        'imx235_registers': len(IMX235_ROWS),
        'imx235_modes': IMX235_MODES,
        'subsystems': SUBSYSTEMS,
    }
    import hashlib
    out['imx210_sha256'] = hashlib.sha256(A6000.read_bytes()).hexdigest()
    out['imx235_sha256'] = hashlib.sha256(A7S.read_bytes()).hexdigest()
    path = ROOT / 'analysis/s201_imx210_imx235_registers/compare.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({
        'n_subsystems': len(SUBSYSTEMS),
        'identicos': sum(1 for s in SUBSYSTEMS if s['clasificacion']=='IDENTICO'),
        'distintos': sum(1 for s in SUBSYSTEMS if s['clasificacion']=='DISTINTO'),
        'ausentes': sum(1 for s in SUBSYSTEMS if s['clasificacion']=='AUSENTE_EN_A6000'),
    }, indent=1))

if __name__ == '__main__':
    main()
