"""S57: genera analysis/s57-evidence-matrix.json (entradas + hipótesis). Fuente única de los estados citados en docs/capture/s57-*.md."""
import json
from pathlib import Path
A = 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9'
S = 'b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e'
T = 'tests/test_s57_imx210_exposure.py::'
FW = 'av-cam.bin (fw 3.21 A6000 / 3.20 A7S)'


def e(i, claim, model, addr, regs, bits, data, instr, interp, status, method, test, lim, refs=None):
    return dict(id=f'S57-{i:02d}', claim=claim, model=model, firmware=FW, sha256=A if model == 'A6000' else S if model == 'A7S' else f'{A} | {S}',
                function_address=addr, registers=regs, bits=bits, data=data, instructions=instr, address=addr,
                references=refs or ['analysis/s57/emu57.py', 'analysis/s56/p2s_emu.py'], interpretation=interp, status=status,
                validation_method=method, test=T + test, limitations=lim)


E_ = [
 # --- A: ID1 -----------------------------------------------------------------------------------------------------------------
 e(1, 'ID1 está en dos registros sombra: A=0x4401ca2c (índice 1 de la lista de 119) y B=0x4401c734 (índice 2); A se transmite antes que B', 'A6000',
   'lista 0x43fe995c; GOT +0x20b8 (A), +0x1984 (B)', ['ID1 (dir 0x0001)'], 'byte de dato +2 de cada registro', 'A: 0x4401ca2e; B: 0x4401c736', ['—'],
   'dos entradas consecutivas de la lista síncrona con la misma dirección', 'VERIFICADO', 'bytes + emulación del formateador', 'Id1Writers', 'qué hace el sensor con dos escrituras seguidas a la misma dirección: NO VERIFICADO'),
 e(2, 'Todas las escrituras de bits de ID1 están en SetExposure (0x436d70d2-0x436d7132), 0x436d7c08 (0x436d7c16-0x436d7c46) y 0x436d7cf0 (0x436d7d0e-0x436d7d3a); más la carga de columna de SetMode (0x436d6570) en A', 'A6000',
   '0x436d6f6c, 0x436d7c08, 0x436d7cf0, 0x436d6570', ['ID1'], '2,3,4,6,7 (+0,2 vía SetMode)', 'bfc/orr/bfi sobre [rec,#2]', ['analysis/s57/bitops.json'],
   'no hay otros escritores en la región imager; ID1 no se lee fuera de 0x436d7c08', 'VERIFICADO', 'seguimiento estático de GOT→registro→orr/bfc (Capstone) + REA pseudo-código de 0x436d7c08/0x436d7cf0', 'Id1Writers',
   'seguimiento lineal; escrituras por puntero calculado fuera de la región 0x436d5000-0x436daa00 no excluidas (la lista se recorre por 0x436d75f8 solo para lectura)'),
 e(3, 'SetMode (0x436d6570, vtable 0x43fcc130) carga A desde la matriz de 59 filas: 0x44 (0x0b,0x2f), 0x40 (0x01,0x12,0x03,0x0a), 0x41 (0x05,0x10,0x07,0x0f,0x18,0x1a,0x19)', 'A6000',
   '0x436d6570; matriz 0x43fe9b74', ['ID1'], '0 y 2', 'ldrb r5,[r5,#4]; strb r5,[r2]', ['scripts/imx210_modes.py', 'analysis/s57/id1_grid.py'],
   'bit0=1 en el grupo «vídeo» y 0x0f; bit2=1 en los modos fotográficos 0x0b/0x2f', 'VERIFICADO', 'matriz de bytes originales + emulación de la función', 'Id1Emulation',
   'nombres «fotográfico/vídeo» son HIPÓTESIS (S50); significado eléctrico de bits 0/2 desconocido'),
 e(4, 'SetExposure fija bits (2,7,4,6) de A según ShutMode: 0→(0,0,0,1); 1→(1,1,0,1); 2→(1,1,1,0); 3→(1,1,1,1); 4→(0,1,0,1); no toca bits 0,1,3,5', 'A6000',
   'tbb 0x436d70c6; 0x436d70d0-0x436d7132', ['ID1'], '2,7,4,6', 'ID1 = 0x40/0xC4/0x94/0xD4/0xC0 con base SetMode 0x40', ['—'],
   'ShutMode es un selector de 5 estados que reparte 4 bits de ID1', 'VERIFICADO', 'emulación (130 combinaciones, rellenos 0x00/0xA5)', 'Id1Emulation', 'nombre y efecto eléctrico de cada bit: NO VERIFICADO'),
 e(5, 'Pulso SSB: B←A; si [O+0x268]==1: A|=8, B&=~8 y la petición se borra; si no, ambos &=~8', 'A6000',
   '0x436d7c08 (REA: FUN_436d7c08)', ['ID1 A y B'], '3', 'ldrb.w r1,[r0,#0x268]; orr r1,r1,#8; bfc r2,#3,#1', ['analysis/s57/rea-out/pseudo_436d7c08.txt'],
   'strobe de un bit en dos registros consecutivos de la lista', 'VERIFICADO', 'Capstone + REA procedure_pseudo_code + emulación Execute completo', 'Id1Emulation', 'función eléctrica del bit 3: NO VERIFICADO'),
 e(6, 'En el flujo de bytes el pulso ocupa dos bloques: [dir0=0x0C, dir1=0xCC] y [cabecera 81 2F 81 00 01][dir1=0xC4, dir2=0x20,…]', 'A6000',
   '0x43ad8fa2 (formateador) tras 0x436d839c', ['ID1'], '3', '81 05 81 00 00 0c cc 81 2f 81 00 01 c4 20 …', ['analysis/s56/p2s_emu.py'],
   'separación mínima de 5 B de cabecera; temporización real fijada por hardware P2S', 'VERIFICADO', 'emulación del formateador y commit reales', 'Id1Emulation', 'duración real del pulso en el pin: NO VERIFICADO (sin analizador)'),
 e(7, 'Orden de Execute (0x436d839c): 0x436d79c4 → 0x436d7b34 → 0x436d8040 → 0x436d7c08 → 0x436d7c58 → 0x436d7c94 → 0x436d7db4 → 0x436d7cb0 → 0x436d7cf0 → 0x43ad92d0 → 0x436d8244 → 0x436d8064 → vtable+0x9c → lista 119 (modo 2) → espera 0x436d5bcc → 8 inmediatos (modo 0)', 'A6000',
   '0x436d839c (0x436d84d0-0x436d859e)', ['ID0','ID1','0x1c','0x1d','0x65','0x73','0xdc','0x126-0x128','0x12f'], '—', 'bl en secuencia', ['analysis/s57/thumbdis.py'],
   'las modificaciones de ID1 ocurren dentro de Execute justo antes del envío', 'VERIFICADO', 'desensamblado Capstone', 'P2SSync', 'duraciones de espera no medidas'),
 e(8, 'Banderas +0x277/+0x278/+0x279/+0x27c: las pone el manejador AdjustCmd 0x91 (0x43a12d9c) según la categoría (4→+0x278, 7→+0x27c, 8→+0x279, 1/7→+0x277) de una tabla de comandos; +0x279 con drive 0x0b borra bits 2,7,4 de ID1 y pone 3..8=0, 0x73=0x39, 0x12f=0x0E', 'A6000',
   '0x43a12d9c (case 0x91), 0x43ad9194/91a0/91ac/91b8, 0x436d7c94/7cb0/7cf0', ['ID1','3-8','0x65','0x73','0xdc','0x12f'], '2,4,7', 'bfc #2,#7,#4; strb #0x39; strb #0xe', ['—'],
   'ruta de ajuste/servicio (cadena «AdjustCmd Select error»), no fotografía normal', 'VERIFICADO', 'bytes + emulación con banderas forzadas', 'AdjustCmdFlags', 'uso real de las categorías 7/8: tabla de comandos no resuelta (NO VERIFICADO)'),
 e(9, 'Los resultados de ID1 no dependen del relleno de memoria (0x00 vs 0xA5) en 130 combinaciones', 'A6000', '—', ['ID1'], '—', '—', ['analysis/s57/id1_grid.py'],
   'descarta artefacto de memoria a cero', 'VERIFICADO', 'doble emulación', 'Id1Emulation', 'estado inicial de la RAM real no medido'),
 # --- B: SSB -----------------------------------------------------------------------------------------------------------------
 e(10, 'La petición SSB (0x43ad9116: [O+0x268]=1) tiene 5 llamadores: 0x438c7a0a, 0x438c8326, 0x438c883c, 0x438cc5ce, 0x43ae936c (REA da 0x43b1af3a en lugar de 0x438c86b0 por límites de función)', 'A6000',
   '0x438c7800, 0x438c828c, 0x438c86b0/0x43b1af3a, 0x438cc4b4, 0x43ae935a', ['ID1'], '3', 'bl #0x43ad9116', ['—'],
   'cinco puntos: arranque de captura, StartExposure, ExposureTimerStart(first), prelight y helper SSB+SetExposure', 'VERIFICADO', 'índice de llamadas + REA procedure_callers', 'SsbProducers', 'llamadas indirectas no cubiertas'),
 e(11, 'Orden en los productores: captura SetMode→Execute→SetExposure→SSB→SetRead→Execute; StartExposure/TimerStart SetExposure→SetRead→SSB→Execute(1) solo si [cap+0x4b9c]==0 (si no, Execute(0)); helper 0x43ae935a SSB→SetExposure', 'A6000',
   '0x438c7800, 0x438c828c, 0x438c86b0, 0x43ae935a', ['ID1','3-8'], '3', 'secuencia de bl', ['—'],
   'SSB siempre se solicita justo después de preparar una actualización de exposición; nunca con Execute(0)', 'VERIFICADO', 'secuencia de llamadas en rango (Capstone)', 'SsbProducers', 'Execute(0) (0x436d6a34) solo reinicia el P2S y no envía registros'),
 e(12, 'En el camino de «ExposureTimerEnd!» (0x438c893a) no hay SetExposure, SetRead, SSB ni Execute', 'A6000', '0x438c86b0 (0x438c890e-0x438c8960)', ['—'], '—', 'ausencia de bl a 0x436d6320/0x436d6398/0x43ad9116/0x43ad911c tras 0x438c8890', ['analysis/s57/thumbdis.py'],
   'el fin de exposición en esta función no reescribe registros del sensor (envía mensaje a Darwin)', 'VERIFICADO', 'desensamblado de la rama', 'SsbProducers', 'otras rutas de fin (Darwin, ISR) no descartadas'),
 e(13, 'El bit 3 de ID1 solo lo escribe 0x436d7c08 (A|=8, B&=~8); los demás pares poner/quitar bit de la región imager son ramas excluyentes (SetExposure por ShutMode, 0x436d7b34 por [O+0x267])', 'A6000', '0x436d5000-0x436daa00', ['52 registros con operaciones de bit'], '—', 'orr/bfc por función', ['analysis/s57/bitops.json'],
   'SSB es el único pulso (dos registros, mismo lote) del sensor en esta región', 'VERIFICADO', 'escaneo estático', 'Id1Writers', 'seguimiento lineal aproximado'),
 e(14, 'A7S: la petición de pulso [O+0x3d7] se genera dentro de SetExposure A7S (0x436f4a94): =1 si el parámetro u16 arg+2 > 0x1000, =0 si no; el consumidor activa el bit 0x10 del byte +4 de un registro', 'A7S',
   '0x436f4a94 (0x436f4b10-0x436f4b48); consumidor 0x436f459c', ['registro IMX235 con byte +4 bit 4'], '4 (byte +4)', 'cmp.w r8,#0x1000; strb.w r1,[r4,#0x3d7]', ['analysis/s57/a7sdis.py'],
   'en A7S el strobe es función de la magnitud del parámetro de exposición; en A6000 lo piden los flujos de captura: no equivalentes', 'VERIFICADO', 'bytes + desensamblado', 'Imx235Silent', 'significado de 0x1000 (¿12 bits?) NO VERIFICADO'),
 # --- C: timing -------------------------------------------------------------------------------------------------------------------
 e(15, 'Mapa exacto: arg+4 (svd u16)→ID3 y ID4[3:0]; arg+0 (shd u16)→ID5 y ID6[5:0]; arg+6 (spl u16)→ID7 y ID8[3:0]; arg+9 = ShutMode; los bits altos de ID4/6/8 se conservan', 'A6000',
   '0x436d6f6c (0x436d6faa-0x436d70a4); log 0x436d723a', ['ID3','ID4','ID5','ID6','ID7','ID8'], 'ID4[3:0], ID6[5:0], ID8[3:0]', 'ldrh r6,[r1,#4]; ldrh r5,[r1]; ldrh r7,[r1,#6]; bfi', ['analysis/s57/c_timing.py'],
   'svd 12 bit, shd 14 bit, spl 12 bit (los bits de entrada superiores se descartan)', 'VERIFICADO', '200 vectores aleatorios x 2 rellenos (400/400)', 'TimingMapping', 'unidades físicas: NO VERIFICADO'),
 e(16, 'ShutMode 2 carga ID0x100←arg+8 y ID0x101←arg+0x14; en los otros ShutMode 0x100/0x101 no cambian (0x00/0x38 del arranque)', 'A6000', '0x436d7134-0x436d71c0 (rama ShutMode 2)', ['0x100','0x101'], 'byte completo', 'lectura de arg+8/+0x14', ['analysis/s57/c_timing.py'],
   'en el log de la captura principal arg+8 se llama «sint»', 'VERIFICADO', 'emulación', 'TimingMapping', 'significado de 0x100/0x101: NO VERIFICADO'),
 e(17, 'El espejo 0x144-0x149 de svd/shd/spl solo se escribe si [G(0x4f24)+0x7f] != 0xff', 'A6000', '0x436d7036-0x436d70a4', ['0x144-0x149'], '—', 'ldrb r3,[r3,#0x7f]; cmp r3,#0xff', ['analysis/s57/c_timing.py'],
   'indicador de configuración externo a SetExposure', 'VERIFICADO', 'emulación con ambos valores', 'TimingMapping', 'origen de [G+0x7f]: NO VERIFICADO'),
 e(18, 'CAMERA_MAIN_SYNC 0x4381106c (StrtExps) comprueba svd contra n·svr_num−1 (VdNum≤1) o n/VdNum−1, con n=[obj+0x1f8] (o 1 si [obj+0x1fc]==9); error si bit15; sustituye solo con indicador de depuración', 'A6000',
   '0x4381106c (REA: FUN_4381106c)', ['ID3','ID4'], '—', 'muls; bl 0x4355faf0; subs r0,#1; tst.w r0,#0x8000', ['analysis/s57/rea-out/pseudo_4381106c.txt'],
   'svd es un contador entero relacionado con repeticiones de VD (svr_num/VdNum) y no una duración en ns', 'VERIFICADO', 'Capstone + REA pseudo-código', 'TimingMapping', 'qué son svr_num (u8 +0x14e) y VdNum (u16 +0xcc): NO VERIFICADO'),
 e(19, 'En ese camino ShutMode (arg+9, «gs» en el log) = ([obj+0x1fc]==9) ? 1 : 0', 'A6000', '0x4381118e-0x4381119c', ['ID1'], '2,7,6 (ShutMode 1)', 'cmp r3,#9; subs r3,#8; strb.w r3,[sp,#0x21]', ['analysis/s57/rea-out/pseudo_4381106c.txt'],
   'el ShutMode 1 (0xC4) se elige cuando el «tipo» de captura vale 9', 'VERIFICADO', 'Capstone + REA', 'TimingMapping', 'significado de «tipo 9»: NO VERIFICADO'),
 e(20, 'Constantes escritas en cap+0x655 (ShutMode): 0 en 0x438c79e2 y 0x438c82bc; 1 en 0x438c87f0 (ExposureTimerStart); copia en 0x4389cc28. No se encontró constante 2, 3 ni 4', 'A6000', '0x438c79e2, 0x438c82bc, 0x438c87f0, 0x4389cc28', ['ID1'], '—', 'strb.w r3/sb,[r4,#0x655]', ['—'],
   'en las rutas rastreadas solo se usan ShutMode 0 y 1', 'VERIFICADO', 'barrido de stores', 'SsbProducers', 'producer de la copia 0x4389cc28 y otros objetos: NO VERIFICADO'),
 e(21, 'Banco de parámetros: 0x43b0893c copia la fila de banco (S+4+16·S[0]) a S+0xC4..0xD0; 0x43849fb8 construye el bloque de exposición; 4 bancos de 16 B los prepara 0x43843a44; el pipeline AE 0x437b5b14 (etapas 0x20-0x36) lo alimenta; S=0x43eb35d0 (BSS)', 'A6000',
   '0x43b0893c, 0x43849fb8, 0x43843a44, 0x437b5b14', ['svd','shd','spl'], '—', 'ldr/str de 4 palabras', ['analysis/s57/rea-out/pseudo_0x43b0893c.txt', 'analysis/s57/rea-out/pseudo_0x43849fb8.txt'],
   'los números nacen en el pipeline AE (fuera de lo rastreado)', 'VERIFICADO', 'REA pseudo-código + bytes (S está a cero en la imagen)', 'TimingMapping', 'escritor concreto de +0xC4..+0xD8: NO LOCALIZADO'),
 e(22, '[cap+0x650] es svd (arg+4); 0x43b1e7f2/0x43b1e854 incrementan [cap+0x4b9c] por paso y StartExposure solo programa registros en el paso 0; si svd==0 envían el mensaje de fin (4,2) sin repetir', 'A6000',
   '0x43b1e7f2, 0x43b1e854, 0x438c828c', ['ID3','ID4'], '—', 'ldrh r4,[r0,#0x650]; adds r2,#1; str.w r2,[r3,#0x9c]', ['—'],
   'svd cuenta pasos del secuenciador del host (cada paso = un evento VD o equivalente: INFERENCIA)', 'VERIFICADO', 'desensamblado; correspondencia arg=cap+0x64c', 'TimingMapping', 'cadencia real de los pasos (VD) no medida'),
 # --- D: IMX235 --------------------------------------------------------------------------------------------------------------------
 e(23, 'Matriz efectiva IMX235 (A7S): 35 registros (34 dev 0x81 + 1 dev 0x83) x 34 modos; fila = {ptr, 34 valores, 2 relleno}; registro de 5 B {dev,0,dirLE16,dato} en ptr-4', 'A7S', 'tabla de modos 0x43fee370, matriz 0x43fee598', ['34 modos'], '—', '—', ['analysis/s57/imx235_matrix.py'],
   'reconstruye los valores de SetMode por modo sin ejecutar nada', 'VERIFICADO', 'lectura de bytes', 'Imx235Silent', 'SetExposure/SetRead no están en la matriz'),
 e(24, 'Selector A7S 0x43826d58: tipo==2 → sub 0 → drive_mode 0x4e; sub 1 → 0x4f; fuera de Silent: 0x0b / 0x35 / 0x17', 'A7S', '0x43826d58 (0x43826d7c, 0x43826da6)', ['drive_mode'], '—', 'movs r0,#0x4e / #0x4f', ['docs/capture/a7s-silent-reconstruction.md'],
   'Silent = selección de dos modos de sensor dedicados', 'VERIFICADO', 'bytes', 'Imx235Silent', 'origen del tipo 2 (UI) heredado de S52/S53'),
 e(25, 'Los modos Silent 0x4e/0x4f difieren del 0x0b en 33 y 35 de 35 registros; son «hermanos» de 0x4c/0x4d (0x4e vs 0x4c: solo dir 0x000C 0x10 vs 0x20; 0x4f vs 0x4d: solo dir 0x000A 1 vs 2; 0x4e vs 0x4f: 4 registros)', 'A7S', 'columnas 29,30 vs 27,28 de 0x43fee598', ['dir 0x000C','0x0000','0x0008','0x000A'], '—', 'comparación de columnas', ['analysis/s57/imx235_matrix.py'],
   'el Silent A7S no añade un conjunto de registros nuevo: es una variante mínima de modos de lectura 0x4c/0x4d con otra dirección 0x000C', 'VERIFICADO', 'comparación de bytes', 'Imx235Silent', 'qué son 0x4c/0x4d y el efecto de 0x000C: NO VERIFICADO'),
 e(26, 'En la matriz IMX235 no hay ningún registro que solo difiera en Silent y que sea candidato de «fin de integración»; la diferencia Silent es el modo de lectura (y la política de clase de S52)', 'A7S', '—', ['35 registros'], '—', '—', ['—'],
   'D.6: el firmware no revela un comando de terminación; la diferencia funcional recuperada es el modo de lectura + lógica Darwin/LIRO', 'INFERENCIA', 'ausencia en comparación de columnas', 'Imx235Silent', 'IMX235 podría usar temporización interna no codificada en la matriz (SetExposure, 0x436f4a94)'),
 # --- E: XPI -------------------------------------------------------------------------------------------------------------------------
 e(27, 'Esquema A6000: CIS0_SHT_RST (BIONZ) → conector CN0400 (51P) pin 6 → XPI del sensor (pin F6); vecinos del conector: XCLR(11)=CIS0_IMG_RST, SDO(10), SCK(9), SDI(8), XCE(7)=CIS0_XCS, XVS(2)=CIS0_VD, XHS(3)=CIS0_HD, pin 5 VREF_ON', 'A6000',
   'docs/references/sony-ilce-6000-level3-sm.txt l.488, 1631, 1694, 2531', ['XPI'], '—', '—', ['docs/references/sony-ilce-6000-level3-sm.txt'],
   'línea discreta directa a la flex del sensor, junto a reset y sincronías', 'INFERENCIA', 'texto del esquema extraído de PDF (ambiguo)', 'MatrixConsistency', 'polaridad, resistencias, función alternativa del pin y rango de tensión: NO VERIFICADO'),
 e(28, 'Ninguna cadena SHT_RST/SHTRST/sht_rst en todo el árbol de firmware extraído (rg -a)', 'both', 'firmware/ (todos los módulos)', ['—'], '—', '—', ['—'],
   'el controlador de XPI no se identifica por nombre; puede ser hardware o rutas sin cadenas', 'VERIFICADO', 'barrido de bytes', 'MatrixConsistency', 'ausencia de cadena ≠ ausencia de uso'),
 # --- F: sync ------------------------------------------------------------------------------------------------------------------------
 e(29, 'SyncMode (cfg[0]) se escribe tal cual en 0xfc088800; solo el modo 2 usa banderas OSAL (grupo 0x18: clr,set,wait,clr,set) y el disparo 1,0,1 en 0xfc088808', 'A6000', '0x436d5b74, 0x43ad8dca, 0x43ad8de4, 0x436d5cdc', ['P2S 0xfc088800/0xfc088808'], '—', 'mmio 0xfc088800=2; 0xfc088808=1,0,1', ['analysis/s57/sync_modes.py'],
   'SyncMode 2 = transferencia con espera de fin por interrupción/bandera', 'VERIFICADO', 'emulación de los cuatro modos', 'P2SSync', 'semántica de los valores del registro de bloque en hardware: NO VERIFICADO'),
 e(30, 'Execute envía la lista de 119 (modo 2), llama a la espera de banderas P2S (0x436d5bcc) y después envía los 8 inmediatos (modo 0)', 'A6000', '0x436d8568-0x436d859a', ['lista 0x43fe995c, 0x43fe9b50'], '—', 'bl 0x436d79b0; bl 0x436d75f8; bl 0x436d5bcc; bl 0x436d75f8', ['—'],
   'el lote de 119 (con la exposición) precede a los 8 inmediatos; que la espera garantice el fin eléctrico de la transmisión no está demostrado', 'VERIFICADO', 'desensamblado', 'P2SSync', 'semántica OSAL de la espera y evento que activa la bandera: NO VERIFICADO'),
 e(31, '«SIFSyncCode» del log de Execute es el código de sincronía del receptor SIF (0x435440a0 SetSyncCode: patrones tipo 0x3FF/0xFF00), no un parámetro del P2S', 'A6000', '0x435440a0; log 0x43c940d7', ['—'], '—', '—', ['—'],
   'no hay vínculo demostrado entre SyncMode del P2S y la sincronía del receptor', 'INFERENCIA', 'desensamblado parcial', 'P2SSync', 'conexión con VD: NO VERIFICADO'),
 e(32, 'El planificador CAMERA_MAIN_SYNC (0x43792a0c, «VD_Pre») aplica por VD y avisa «start delayed %dV» / «overflow %dV»', 'A6000', '0x43792a0c', ['—'], '—', 'cadenas 0x43ca39e6/0x43ca3a50', ['—'],
   'existe un planificador por VD que decide cuándo se programa la exposición', 'PARCIAL', 'cadenas + referencias literales', 'SsbProducers', 'mecanismo interno no analizado (7 KB)'),
 e(33, 'Fin electrónico de integración a resolución completa: sin registro, bit ni señal demostrados', 'A6000', '—', ['ID1','3-8','0x100','0x101','XPI'], '—', '—', ['—'],
   'ningún registro se escribe al terminar la exposición; los de duración se fijan al inicio; faltan semántica de unidades y de XPI', 'NO VERIFICADO', 'cierre de evidencias S57', 'MatrixConsistency', 'datasheet IMX210 o traza pasiva'),
]
H = {
 'H57-1': dict(status='PARCIAL', conf='alta (estructura) / baja (semántica eléctrica)', note='ID1 mezcla bits de modo de lectura (SetMode: bits 0,2), selector ShutMode (bits 2,4,6,7) y strobe (bit 3); clasificación: función combinada'),
 'H57-2': dict(status='INFERENCIA', conf='media', note='SSB es un strobe que acompaña a toda actualización de exposición (SetExposure→SSB→Execute) y no aparece en fin de exposición ni en Execute(0); latch/disparo de parámetros probable; fin de exposición no demostrado'),
 'H57-3': dict(status='INFERENCIA', conf='media-alta', note='svd/shd/spl son temporización de integración: svd se valida contra n·svr_num−1 y el host cuenta pasos hasta svd; shd/spl sin fórmula'),
 'H57-4': dict(status='NO VERIFICADO', conf='-', note='ningún registro 3-8 se reescribe al terminar; el fin podría estar implícito en la temporización fijada al inicio'),
 'H57-5': dict(status='PARCIAL', conf='media', note='Silent A7S = modos de lectura 0x4e/0x4f (hermanos de 0x4c/0x4d, 1-4 registros de diferencia); IMX210 tiene 13 modos, ninguno equivalente; no hay comando adicional recuperable'),
 'H57-6': dict(status='NO VERIFICADO', conf='-', note='XPI existe como línea discreta; ni controlador ni efecto localizados'),
 'H57-7': dict(status='PARCIAL', conf='media', note='SyncMode 2 = transferencia con handshake de banderas y disparo 1,0,1 (VERIFICADO); aplicación en el siguiente VD (INFERENCIA)'),
 'H57-8': dict(status='NO VERIFICADO', conf='-', note='existen piezas (svd/shd/spl, ShutMode, strobe) pero ninguna demostrada como fin de integración'),
 'H57-9': dict(status='HIPÓTESIS', conf='baja', note='compatible con la evidencia: la terminación podría depender de hardware del sensor no codificado en registros conocidos'),
 'H57-10': dict(status='NO VERIFICADO', conf='-', note='no se deduce ninguna ruta de terminación electrónica a partir de las señales y registros recuperados'),
}
out = dict(phase='S57', date='2026-10-20', sha256=dict(av_cam_a6000=A, av_cam_a7s=S), entries=E_, hypotheses=H)
Path(__file__).resolve().parents[1].joinpath('s57-evidence-matrix.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
print(len(E_))
