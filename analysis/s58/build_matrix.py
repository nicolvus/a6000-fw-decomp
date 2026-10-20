"""S58: genera analysis/s58-evidence-matrix.json (entradas + hipótesis). Fuente única de los estados citados en docs/capture/s58-*.md."""
import json
from pathlib import Path
from typing import Any
A = 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9'
S = 'b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e'
T = 'tests/test_s58_timing_a7s.py::'
FW = 'av-cam.bin (fw 3.21 A6000 / 3.20 A7S)'
def e(i, claim, model, addr, func, data, interp, status, method, test, lim, refs=None):
    return dict(id=f'S58-{i:02d}', claim=claim, model=model, firmware=FW, sha256=A if model == 'A6000' else S if model == 'A7S' else f'{A} | {S}',
                address=addr, function=func, data=data, references=refs or ['analysis/s58/'], interpretation=interp, status=status, validation_method=method,
                test=T + test if test else '—', limitations=lim)
E_ = [
 e(1, 'Cadena de temporización por fotograma (variante 0x51–0x54): 0x437b5e70 → 0x4383d18c (instantánea P→X) → 0x4383d704 (X→AEOUT3: n_i, shd_i, reloj fino_i por banco) → 0x4383bc6c (AEOUT3,P→G) → 0x4383bf2c (G→filas de 16 B + A_i,B_i)', 'A6000',
   '0x437b5e70, 0x4383d18c, 0x4383d704, 0x4383bc6c, 0x4383bf2c', 'pipeline AE (temporización)', 'P=0x43eaee84, X=0x43ead7e0, AEOUT3=X+0x290=0x43eada70, G=0x43eb05d8, G224=G+0x224',
   'el pipeline AE contiene el cálculo numérico de svd/shd/spl (no solo copias de tablas)', 'VERIFICADO', 'REA procedure_pseudo_code + llamadores (Capstone) + trazado de escrituras Unicorn', 'AETimingA6000',
   'existe una variante 0x437b5d30 (0x42–0x45, 0x4383ecf8) no analizada; llamada de 0x437b617e es indirecta', ['analysis/s58/rea-out/', 'analysis/s58/a2_trace.py', 'analysis/s58/a4_trace.py']),
 e(2, 'El bloque de temporización del modo se copia sin transformar: 0x43844e80 copia [X8+0x138..0x167] a P+0x4c4..0x4f3 y u16 [X8+0xcc] (VdNum) a P+0x4f4; 0x43843e94 guarda N=[X8+0x3c] en P+0x22c; 0x4383bc6c los lleva a G (G+0x16=svr=X8+0x14e, G+0x30=N, G+0x38=VdNum)', 'A6000',
   '0x438451c2–0x438451ec, 0x43844998, 0x4383bc6c', 'copia de parámetros de modo', 'ldm/stm 12 palabras; strh [r4,#0x4f4]; str [r4,#0x22c]',
   'svr_num, VdNum y n son exactamente los de la validación de CAMERA_MAIN_SYNC 0x4381106c (S57)', 'VERIFICADO', 'desensamblado Capstone + REA', 'AETimingA6000',
   'el escritor original del bloque X8+0x138 (tablas de modo, 12 u16 de 0x43ae84c0()=0x437876dc()+0xdd0 y tablas param_2[…]) no se recuperó'),
 e(3, 'Tv→tiempo: 0x4382fa94(Tv)=256e6·2^(−(Tv−0x1000)/256) unidades; Tv≤0xc00 → 0xffffffff (satura 2^32 ud)', 'A6000', '0x4382fa94 (K=0xf424000 en 0x4382fac4; exp2 0x43902924)', 'Tv→T',
   '0x1000→256000000; 0x1100→128000000; 0x1800→1000000; 0xc01→4084937500', 'Tv en pasos de 1/256 EV con 0x1000 ≙ 256e6 ud', 'VERIFICADO', 'Unicorn sobre el código real (9 puntos)', 'AETimingA6000', 'unidad física de T (1/256 µs) es INFERENCIA (S58-12)'),
 e(4, '0x4383d4d0(T,M,clk,&n,&shd,&spl): n=T/(F·svr); líneas=(resto−sb)/Lt; shd=máx(M[0x14],M[0x10]−líneas); spl_fino=máx(0,M[0x2c]−(1000·(resto−sb−Lt·líneas)/tick))', 'A6000', '0x4383d4d0', 'descomposición de T', 'modelo Python timing_model.time_split == código real 600/600',
   'T = n·F·svr + (VMAX−shd)·Lt + (HMAX−spl_fino)·tick/1000 + sb (identidad algebraica; 0x4383d430 es su inversa)', 'VERIFICADO', 'Unicorn, 300 vectores × 2 rellenos (incl. caso ITSTATE)', 'AETimingA6000',
   'valores reales de M por modo y el significado del argumento clk (X+0x5c ← P+0x4c0, u32 formado por dos u16 de 0x438667e0) no recuperados'),
 e(5, 'Bucle de 4 bancos de 0x4383d704: T_i=0x4382fa94(Tv_i) con Tv_i=u16[AEOUT3+0xfc+2i]; salidas n_i→AEOUT3+0x348+4i, shd_i→+0x358+4i, fino_i→+0x368+4i; 0x4383bc6c las copia a G+0xd0/+0xb0/+0xc0', 'A6000',
   '0x4383d704 (0x4383e01a…), 0x4383d5b8, 0x4383bc6c', 'bucle por banco', 'escrituras en 0x4383d50a/0x4383d578/0x4383d5ac', 'cuatro bancos = cuatro candidatos de exposición por fotograma', 'VERIFICADO', 'trazado de escrituras Unicorn + pseudo-código REA', 'AETimingA6000',
   'origen de Tv_i (AE core) no recuperado; override por [param_1+0xb2] cuando flags 0x13f/0xa0'),
 e(6, 'Filas de 16 B por banco (0x4383c9dc): shd=word0 = mín(shd_i+G[0x18]·(N−1−n_i)·flag, G[0x10]) ≥ G[0x14]; svd = clamp((svr·(N−f)/VdNum)−1); spl = clamp(máx(0,(svr·N/VdNum−1)−n_i·svr), ≤svd); fino_i va a +10', 'A6000',
   '0x4383c9dc', 'constructor de filas', 'build_rows == código real 300/300', 'svd = n·svr/VdNum−1 coincide con la validación de S57; spl es una cuenta de pasos V restantes, no un reloj sub-línea', 'VERIFICADO', 'Unicorn sobre código real', 'AETimingA6000',
   'depende de FUN_436f059c (stub 0) y de bytes de depuración (a 0); semántica física de los campos: INFERENCIA'),
 e(7, 'Fila → SetExposure: 0x43b0893c copia la fila del banco S[0] (S+4+16·b) a S+0xc4; 0x43849fb8 la deja en arg[0..0xf] (shd=arg+0, svd=arg+4, spl=arg+6); S+0xd4/0xd8 → arg+0x10/0x14', 'A6000',
   '0x43b0893c, 0x43849fb8, 0x43843a44', 'fila→arg', 'Unicorn: banco 2 → arg idéntico', 'cadena AE→SetExposure cerrada', 'VERIFICADO', 'Unicorn', 'AETimingA6000', '0x43843a44 copia S+0x64.. (staging) a S+4.. según modo (no emulado)'),
 e(8, 'A_i y B_i por banco (0x4383b790 + 0x43b08684): B∈[0x801,0x1800] (constantes de 0x4383c7a8/0x4383c7c4), reparto con 0x1000; se guardan en G224+0x6e+6i y +0x86+2i', 'A6000', '0x4383b790, 0x43b08684, 0x4383c7a8, 0x4383c7c4', 'valores A/B',
   'pseudo-código REA', 'se envían a arg+0x10/arg+0x1e; significado desconocido', 'PARCIAL', 'REA + desensamblado', None, 'sin emulación dedicada; semántica NO_VERIFICADO'),
 e(9, 'Escenarios 1/4000…1 s con M SINTÉTICO (lt=4096, vmax=4176, hmax=864, F=vmax·lt, svr=1, reloj 54 MHz): Tv 0x1bf7,0x19f7,0x17f7,0x15e8,0x1200,0x1000 → (n,shd,spl) = (0,4161,316),(0,4114,397),(0,3926,723),(0,3134,754),(3,1079,864),(14,140,864)', 'A6000',
   '0x4382fa94 + 0x4383d4d0', 'escenarios', 'analysis/s58/out/a6000_timing_scenarios.json', 'solo ilustran la transformación; NO son valores reales del firmware', 'VERIFICADO', 'Unicorn', 'AETimingA6000', 'M sintético: ninguna velocidad real asociada'),
 e(10, 'Unidad de T: con clk=0, tick=0xde3 ≙ 72 MHz ⇒ 1 unidad = 1/256 µs, Tv 0x1000 ≙ 1 s, T máx = 16,78 s', 'A6000', '0x4383d4d0 (0x4383d4fa)', 'unidad', 'sl=256e6/(clk/1000); 0xde3=3555', 'coherente con 72 MHz por defecto', 'INFERENCIA', 'aritmética', None,
   'el valor de clk (u32 en P+0x4c0) no es una frecuencia demostrada; sin datasheet'),
 e(11, 'Tablas de modo 0x0b y 0x2f: ab12 = [864, 4176, 0] en 0x43bc1ae8 (HMAX, VMAX); 864·4176 = 3 608 064 → 66,8 ms solo si el reloj es 54 MHz (inferencia heredada de docs)', 'A6000', '0x43bc1ae8, 0x43bc1b84', 'tablas ctor C_Imager', 'analysis/imx210-drvparam-inputs.json',
   'HMAX/VMAX candidatos de M[0x2c]/M[0x10]; vínculo con M NO demostrado', 'NO_VERIFICADO', 'bytes', None, 'no se localizó la copia tabla→X8+0x138'),
 e(12, 'IDENTIDAD A7S: vtable 0x43fce050: SetMode +0x20=0x436f3b44, SetExposure +0x28=0x436f4168, SetRead +0x30=0x436f4a94, Execute +0x38=0x436f5a14. CORRECCIÓN S57: SetExposure A7S NO es 0x436f4a94 (es SetRead)', 'A7S',
   '0x43fce050+0x20/0x28/0x30/0x38', 'vtable C_Imager A7S', 'cadenas: SetExposure «SHR» y «[svd][shd][spl][shut]» en 0x436f4168; «Read. [AGCont]…» en 0x436f4a94', 'S57-B atribuía a SetExposure el pulso arg+2>0x1000', 'VERIFICADO', 'bytes + cadenas PIC', 'Integrity', 'ctor A7S no localizado'),
 e(13, 'CORRECCIÓN S57-D: la matriz IMX235 tiene filas de 0x14 B {ptr + 16 columnas}, 69 filas, 15 columnas usadas; columna = maptab[idx_modo] (34 B en 0x43c9c5b5): 0x0b→0, 0x35→1, 0x4c/0x4d→5, 0x4e/0x50→12, 0x4f/0x51→13', 'A7S',
   'matriz 0x43fee598; maptab 0x43c9c5b5; cargador 0x436f3928 (vtable+0xa0)', 'SetMode (carga de columna)', 'out/a7s_matrix_corrected.json', 'S57 usó paso 40 B × 34 modos (mezcla de filas)', 'VERIFICADO', 'bytes + SetMode emulado 69/69 en 6 modos', 'A7SMatrix', 'matriz B (NTPAL, 0x43e8de00) es BSS a cero'),
 e(14, 'Diferencias reales entre columnas: 0x4c↔0x4e: 14 registros; 0x4d↔0x4f: 11; 0x4e↔0x4f: 4 (0x01,0x09,0x0a,0x0b = mismo conjunto que 0x0b↔0x35); 0x4c≡0x4d: 0; 0x0b↔0x4e: 45 (S52 decía 45/69)', 'A7S', 'columnas 5, 12, 13, 0, 1', 'comparación de columnas',
   '0x4c↔0x4e: 0x01,0x08,0x09,0x0a,0x0b,0x0c,0x11,0x1f,0x28,0x3c,0x50,0x51,0x55,0x9a', 'Silent no es «variante de 1 registro» de 0x4c: ventana 0x08–0x0c igual a la del modo foto (0x0b), resto propio', 'VERIFICADO', 'bytes', 'A7SMatrix', 'significado de los registros sin datasheet'),
 e(15, 'SetExposure A7S (0x436f4168) escribe svd(12 b)→0x02/0x03, spl(12 b)→0x04/0x05, shd(14 b)→0x06/0x07 (bits altos preservados) y reg 0x00 bit 3 (tipo SSB)', 'A7S', '0x436f4168', 'SetExposure', '200/200 vectores aleatorios, 2 rellenos', 'misma tripleta svd/shd/spl que el IMX210 (regs 3–8) en otras direcciones', 'VERIFICADO', 'Unicorn sobre código real', 'A7SExposure', 'objeto C_Imager sin constructor; parámetros de depuración 0xFF asumidos'),
 e(16, 'ShutMode A7S: 0,1,3,4 válidos; 2 y ≥5 → error 1; reg 0x01 = 0x00/0x04/·/0x14/0x40 (modo 0x4e)', 'A7S', '0x436f4168 (tbb 0x436f4242)', 'ShutMode', 'Unicorn', 'ShutMode 2 no se admite en la A7S (como en S57)', 'VERIFICADO', 'Unicorn', 'A7SExposure', 'significado de bits desconocido'),
 e(17, 'El «pulso» arg+2>0x1000 de la A7S está en SetRead (código de ganancia AGC): fija [O+0x3d7]=1 y ajusta el código; no es SetExposure ni fin de exposición', 'A7S', '0x436f4b10', 'SetRead', 'AGC 0x1000→0; 0x1001→1', 'CORRECCIÓN de S57-B (atribución a SetExposure)', 'VERIFICADO', 'Unicorn', 'A7SExposure', 'efecto eléctrico (conmutación de ganancia) INFERENCIA'),
 e(18, 'Execute A7S (0x436f5a14) transmite el banco completo: 5 transacciones P2S (FIFO 0xf3c00340+4i; config 0xf3c00300; disparo 1,0,1 en 0xf3c00808), 99 escrituras [81|03|81|ADDR8|DATO]; mismo orden de direcciones en todos los modos', 'A7S', '0x436f5a14, 0x436f26c8, 0x43ad9666', 'Execute/P2S', 'out/a7s_scenarios.json', 'formato de trama distinto del IMX210 (dirección de 8 bit, registro único por trama)', 'VERIFICADO', 'Unicorn', 'A7SExecute', 'periférico físico no simulado'),
 e(19, 'Estado efectivo transmitido: ShutMode solo cambia reg 0x01; SetExposure/SetRead aplican los mismos cambios en 0x4c y 0x4e; las diferencias Silent están en la columna de SetMode', 'A7S', 'estado tras Execute', 'estado efectivo', '14 regs (0x4c↔0x4e), 4 (0x4e↔0x4f)', 'H58-6 descartada en el rango emulado', 'VERIFICADO', 'Unicorn', 'A7SExecute', 'rutas de SetExposure con parámetros reales de AE no emuladas'),
 e(20, 'Execute envía 2 mensajes inter-procesador (0x438f6864; ids 0x1000/0x1001, canal 1) incondicionalmente en modos 0x0b/0x35/0x37/0x38; en 0x4c/0x4d/0x4e/0x4f no (con estado de driver a cero); no existe en el C_Imager A6000', 'A7S', '0x436f5b84–0x436f5ba6; 0x43ada07a/0x43ada0b4', 'mensajes Execute', 'r2/r3 con valores por defecto', 'diferencia funcional A7S sin equivalente identificado en A6000', 'PARCIAL', 'Unicorn + desensamblado', 'A7SExecute', 'receptor del mensaje y condición de 0x436f5d90 no analizados'),
 e(21, 'Fin electrónico de integración: ningún registro se reescribe al terminar en A6000 ni en A7S emulada; la programación (svd/shd/spl) se hace antes de Execute', 'both', 'SetExposure/Execute', 'ausencia de comando de fin', 'S57 + S58', 'compatible con terminación autónoma del sensor, NO demostrada', 'INFERENCIA', 'ausencia (no es prueba)', None, 'ausencia de comando ≠ funcionamiento autónomo'),
 e(22, 'Harness: Unicorn 2.1.4 deja ITSTATE activo tras bloques IT con instrucciones saltadas (2/600 discrepancias); wtrace lo limpia. S56/S57 (60 tests) siguen en verde y c_timing 400/400 con la corrección', 'both', 'analysis/s58/wtrace.py', 'metodología', '598/600 → 600/600', 'riesgo de falsos negativos de emulación Thumb', 'VERIFICADO', 'Unicorn', 'Itstate', 'solo cubre bloques IT; VFP habilitado para SetRead'),
 e(23, 'Fin electrónico de integración a resolución completa: NO VERIFICADO; S51 se mantiene (A=NO, B=NO, C=NO)', 'A6000', '—', 'S51', 'sin medición', 'los registros programan el intervalo reset→lectura; falta evidencia de comportamiento', 'NO_VERIFICADO', 'cierre de evidencias', None, 'datasheet IMX210 o traza pasiva CIS0+XPI+VD'),
]
H: dict[str, dict[str, Any]] = {
 'H58-1': dict(status='VERIFICADO', conf='alta', note='el pipeline AE calcula svd/shd/spl (0x4383d4d0, 0x4383c9dc); no es solo selección de tablas; Tv_i y el bloque M de modo quedan como entradas no recuperadas'),
 'H58-2': dict(status='PARCIAL', conf='media-alta', note='svd+1 = svr·N/VdNum (aritmética verificada); es una cuenta de periodos de secuencia vertical; que cada paso sea un VD físico: INFERENCIA'),
 'H58-3': dict(status='PARCIAL', conf='media', note='shd = posición de línea (VMAX−líneas, mín M[0x14]) VERIFICADO aritmético; spl (arg+6) es una cuenta de pasos V restantes, no sub-línea; el reloj fino va a arg+0xa'),
 'H58-4': dict(status='INFERENCIA', conf='media', note='los valores descomponen el tiempo de exposición T en n·F·svr + líneas + relojes (identidad verificada): programan el intervalo reset→lectura; no demuestran un fin de integración a resolución completa'),
 'H58-5': dict(status='PARCIAL', conf='media', note='la A7S programa svd/spl/shd (regs 0x02–0x07) y ShutMode (reg 0x01) en SetExposure y no reescribe nada al terminar (emulación); misma situación que A6000'),
 'H58-6': dict(status='DESCARTADO', conf='alta (rango emulado)', note='SetExposure/SetRead producen los mismos cambios en 0x4c y 0x4e; la diferencia Silent está en la columna de SetMode (14 regs vs 0x4c; 45 vs 0x0b) y, condicionalmente, en los mensajes de Execute'),
 'H58-7': dict(status='DESCARTADO', conf='alta', note='reg 0x0C = 0x64 en 0x0b/0x35/0x4e/0x4f y 0x0A en 0x4c/0x4d: no es específico de Silent (la lectura S57 0x20→0x10 era un error de paso de matriz)'),
 'H58-8': dict(status='PARCIAL', conf='media', note='0x0A hace parte del conjunto de sub-modo {0x01,0x09,0x0a,0x0b} que distingue 0x4e/0x4f y también 0x0b/0x35; significado físico desconocido'),
 'H58-9': dict(status='NO_VERIFICADO', conf='-', note='hay paralelos estructurales (tripleta svd/shd/spl, ShutMode, bit 3 tipo SSB) pero ninguna equivalencia de valores demostrable; no se copia nada entre sensores'),
 'H58-10': dict(status='NO_VERIFICADO', conf='-', note='sin datasheet no se puede decir si faltan funciones del sensor; el IMX210 sí tiene el mismo mecanismo de programación de temporización'),
 'H58-11': dict(status='INFERENCIA', conf='baja', note='SyncMode 2 + planificador por VD (S57); sin evidencia nueva'),
 'H58-12': dict(status='INFERENCIA', conf='media', note='la ausencia de comando de fin es compatible con terminación autónoma (el intervalo ya está programado), pero la ausencia no la demuestra'),
}
# Rectificaciones tras reproducir y auditar el trabajo interrumpido.
E_[1]['interpretation'] = 'productor y validador leen la misma tripleta; sus fórmulas NO coinciden incondicionalmente para VdNum>1'
E_[3]['data'] = 'modelo Python == código real: 120 vectores en suite; campaña a6_verify: 600'
E_[3]['interpretation'] = 'descomposición en cociente, líneas y término fino; reconstrucción ideal sujeta a redondeo, clamps y overflow (no igualdad inversa universal)'
E_[5]['data'] = 'build_rows == código real: 80 vectores en suite; campaña a7_verify 150: 300'
E_[5]['interpretation'] = 'spl es un remanente aritmético de pasos; el host usa N/VdNum−1 para VdNum>1, frente a N·svr/VdNum−1 del productor antes de recortes'
E_[6]['interpretation'] = 'enlaces estáticos y dos tramos emulados; no se ejecutó AE completo hasta P2S en una única llamada'
E_[2]['limitations'] = 'unidad física 1/256 µs es INFERENCIA (S58-10); exp2 tabulada y truncada, no igualdad real exacta'
E_[2]['claim'] = 'Tv→tiempo: 0x4382fa94 aproxima 256e6·2^(−(Tv−0x1000)/256) con tabla y aritmética entera; Tv≤0xc00→0xffffffff'
E_[14]['data'] = '60 vectores (30 entradas × 2 rellenos) en la suite'
E_[17]['claim'] = 'Execute A7S: 5 transacciones P2S, 100 escrituras (99 al dispositivo 0x81 y 1 a 0x83:0x17=0x4a), formato 81|03|DEV|ADDR8|DATO y terminador 00'
E_[17]['interpretation'] = 'el decodificador inicial omitía 0x83; device_regs conserva dispositivos, duplicados y orden'
E_[20]['claim'] = 'Se ejecuta la configuración anticipada SetExposure→Execute; el escenario no ejecuta un evento posterior de fin de exposición'
E_[20]['limitations'] = 'la ausencia en ExposureTimerEnd de A6000 procede de S57; la secuencia temporal completa A7S no se emula'
E_[21]['claim'] = 'Harness: mitigación ITSTATE reproducida en el vector de regresión; límite de instrucciones debe alcanzar el retorno; 60 tests S56/S57 pasan sin modificaciones'
E_[21]['limitations'] = 'la mitigación no prueba un defecto general de Unicorn; barrido Thumb lineal puede incluir datos, sin equivalencia exhaustiva'
E_[22]['interpretation'] = 'hay parámetros de temporización; su relación eléctrica con reset, fin de integración y lectura sigue sin demostrarse'
E_.append(e(24, 'El consumidor 0x436f459c lleva O+0x3d7 al bit 4 del registro 0x81:0x5f y borra la petición; una segunda llamada borra ese bit, en foto y Silent',
             'A7S', '0x436f459c–0x436f45c2', 'consumidor de petición de ganancia', 'ldrb +0x3d7; orr #0x10 / bic #0x10; strb dato+4; clear +0x3d7',
             'la petición de SetRead no es exclusiva de Silent; efecto eléctrico desconocido', 'VERIFICADO', 'bytes Capstone + Unicorn, helper llamado explícitamente',
             'A7SExposure.test_gain_request_consumer_sets_then_clears_register_5f',
             'no se demuestra que el escenario Execute alcance ese helper; invocación aislada no demuestra orden físico'))
H['H58-4']['note'] = 'descomposición numérica de T verificada; vínculo eléctrico reset→lectura y fin de integración NO demostrado'
H['H58-5']['note'] = 'configuración anticipada ejecutada; no se ejecuta un evento de fin posterior en A7S: no demuestra ausencia global de comandos'
H['H58-7'].update(status='PARCIAL', conf='media', note='0x0c participa en diferencias de columna, también comparte valor con foto normal; descarta exclusividad Silent, no su posible participación')
mapping = {1:[1,3,4,6], 2:[2,6], 3:[4,6], 4:[4,21,23], 5:[15,18,21,24], 6:[14,19,20,24], 7:[13,14], 8:[13,14], 9:[15,23], 10:[23], 11:[2,21], 12:[21,23]}
for number, indices in mapping.items():
    h = H[f'H58-{number}']
    entries = [E_[i - 1] for i in indices]
    h.update(support=[e['id'] for e in entries], against='No hay evidencia eléctrica; ver limitaciones de cada evidencia. ' + ('El escenario no contiene un evento final posterior.' if number in (4,5,12) else 'Los estados sintéticos no prueban estados alcanzables de captura.'),
             address=[e['address'] for e in entries], function=[e['function'] for e in entries],
             binary=[dict(model=e['model'], firmware=e['firmware'], sha256=e['sha256']) for e in entries],
             instructions=[e['data'] for e in entries], dependencies=[e['references'] for e in entries],
             test=[e['test'] for e in entries], limitations=[e['limitations'] for e in entries],
             next_experiment='Capturar M/Tv de un estado real o recuperar su inicialización; para semántica física, datasheet o traza pasiva autorizada CIS0/XPI/VD.')
out = dict(phase='S58', date='2026-10-20', sha256=dict(av_cam_a6000=A, av_cam_a7s=S), entries=E_, hypotheses=H)
Path(__file__).resolve().parents[1].joinpath('s58-evidence-matrix.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
print(len(E_), len(H))
