# S59 Sol — temporización IMX210 de la A6000

20-10-2026. Análisis estático y emulación offline de instrucciones de `av-cam.bin`.
SHA-256: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Base de carga: `0x43541000`. No se ejecutó firmware en cámara ni se parcheó o flasheó.

## Resultado científico

**NO VERIFICADO:** que el IMX210 termine una exposición electrónicamente sin segunda
cortina. Se recupera una ruta de escritura del bloque solicitado, pero sus valores
proceden de un estado condicionado y no constituyen una configuración fotográfica
alcanzable. No se ha demostrado tampoco la imposibilidad física del sensor.

Se mantienen las conclusiones corregidas de [S58](s58-conclusions.md): el modelo
numérico reproduce operaciones de firmware; esto no acredita duración física,
alcanzabilidad ni finalización de integración. No se usa IMX235 como equivalente.

## Evidencia nueva y evaluación

| ID | Función/direcciones e instrucciones/datos | Método y resultado | Clasificación / confianza | Límites y test |
|---|---|---|---|---|
| SOL-01 | `0x437876dc`; GOT `0x4401eee4+0x6460 → 0x43e93f34`; `0x43ae84c6: add.w r0,r0,#0xdd0` | Bytes y ejecución del accesor: dirección efectiva `0x43e94d04`. | VERIFICADO / alta | Objeto marcado ya construido mediante su guard; no se atribuye esta precondición a una cámara. `test_accessor_actual_root`, `test_binary_identity`. |
| SOL-02 | `0x43b00da0`: suma `0xda0+0x14`, tamaño `0x50`, tailcall `0x43b7f878 → 0x439c5320` | Ejecutada copia real de 80 B a `obj+0xdb4`; abarca íntegro `obj+0xdd0..0xde7`. Para esos 24 B, fuente=`arg1+0x1c..0x33`. | VERIFICADO / alta | Ruta de escritura recuperada; no se reclama exclusividad de escritor. Copia ARM real, sin stub de memcpy, guardas intactas y dos rellenos. `test_writer_copies_exactly_80_bytes`. |
| SOL-03 | `0x43b00dd4`: lee byte `obj+0x57c`; `0x43b00de8/dea`: `arg1=obj+0xd64`, llama SOL-02 | Publicación `obj+0xdb4 ← obj+0xd64`, 80 B, solo si byte no cero. Bloque solicitado recibe `obj+0xd80..0xd97`. | VERIFICADO / alta | Se ejecutaron ambos lados de la guarda; `obj+0x568=0` deja fuera copias posteriores de otros bloques. `test_publish_gate`. |
| SOL-04 | `0x43b00b48`; memset de 80 B desde `obj+0xdb4` en `0x43b00c30..3a`; byte `obj+0x57c=0` | Constructor real sobre objeto previamente lleno de `0xa5`: bloque cero y publicación deshabilitada. | VERIFICADO / alta | Son valores de construcción del objeto de estado, no M efectivo por modo. `test_constructor_clears_override`. |
| SOL-05 | `0x437aad72..0x437aae0a` dentro de `0x437aa65c`: carga `input+0xb4`, `cbz`; doce LDRH/STRH | Selector cero produce 24 B cero en `X8+0x13c..0x153`; selector no cero copia los doce u16 de SOL-01. | VERIFICADO / alta | Ejecutado segmento original con registros/stack inicializados explícitamente, selectores 0/1/2; no equivale a ejecutar toda la función con objetos reales. `test_consumer_zero_or_override`. |
| SOL-06 | `0x4383d18c`: P+`0x4c0 → X+0x5c`; `0x4383d232..25a`: P+`0x4c4..0x4f3 → X+0x60..0x8f` | Snapshot original conserva palabra clk y 48 B de M, probado con marcadores distintos. | VERIFICADO / alta | Verifica alias y transferencia, no el origen físico de los valores. `test_snapshot_does_not_confuse_histogram_object`. |
| SOL-07 | `0x437b5b68..6e`: GOT+`0x7ad0 → stack+0x18`; `0x43844e80` reserva `0x88` B; `0x438479ce/d0`: carga stack+`0xa0` y llama `0x438667e0` | Primer argumento del escritor de histogramas=`0x43eb121c`, mientras entrada AE P de la misma llamada=`0x43eaee84` (GOT+`0xcb0`). Son objetos diferentes. | VERIFICADO / alta | CORRECCIÓN de la atribución de clk en [S58-A §5](s58-ae-timing-producers.md): un mismo offset `+0x4c0` no demuestra alias. Bloque del llamador ejecutado hasta antes del BL; aritmética del frame y sitio consumidor contrastados contra bytes. `test_histogram_writer_has_a_different_object`. |
| SOL-08 | `0x437aab3c`: LDRH de `param_2[0xd]+0x16`; `0x437aab48..52`: resta `0x3000`, BIC con ASR31, STRH a `X8+0xcc` | `VdNum=max(0,raw_u16−0x3000)`, rango local `0..0xcfff`. Para raw=`0xb000` produce `0x8000`, negativo si luego se usa LDRSH. | VERIFICADO / alta | No hay límite signed16 en este segmento; no prueba que el productor del raw permita todo el rango. Siete casos de borde ejecutados. `test_vdnum_constructor_range_is_not_a_signed_range`. |
| SOL-09 | Productor `0x4383c9dc`; segmento host `0x438110be..0x4381112a` | Comparación ejecutando ambos códigos: con modo productor=0, f=0, estado host=0 y N≥VdNum, coincidencias para VdNum=1 o svr=1 y discrepancias fuera de esos subdominios. | VERIFICADO / alta para esta campaña | No ejecuta el envío completo del host ni demuestra alcanzabilidad. `test_synthetic_compatibility_boundaries`; JSON conserva los 42 casos. |
| SOL-10 | `0x438069f0`, casos 4 y 10 con `obj+0x568=2`; `0x43b00d94` | REA y bytes: copia 80 B del payload+4 o payload+0x590 a obj+0xd64. En combinación con SOL-03, los 24 B solicitados proceden de payload+0x20 o payload+0x5ac. | PARCIAL / alta para el flujo estático | Se recupera procedencia del escritor; no el emisor ni payload real. No se emuló íntegro el despachador. Publicación llamada desde `0x43792f62`, bajo guarda, con raíz retenida de `0x43792a30`. |
| SOL-11 | Host `0x438110be..0x4381112a`: N=0, estado `param_1+0x1fc=9`, prueba de bit15 | N=0 deja resultado cero; estado 9 sustituye N por 1; resultado u16 con bit15 se diagnostica y normaliza a cero. | VERIFICADO / alta | Cinco casos de borde ejecutados; solo los dos diagnósticos se sustituyen por retorno cero. No confundir estado host=9 con modo de sensor. `test_host_normalizes_underflow_and_mode_nine`. |

Evidencia reproducible: [scripts y salidas](../../analysis/s59/sol/), particularmente
`override-writer.asm`, `override-reader.asm`, `clock-caller.asm`,
`histogram-call.asm`, `vdnum.asm`, `probe-results.json`.

REA: una sesión útil A6000 con `GHIDRA_MAXMEM=6G`, daemon existente reutilizado
mediante `rea_session.py` para mantener su log dentro del alcance autorizado.
Arranque frío: **589,9 s**; solicitudes y respuestas originales en
`rea-initial.jsonl`, `rea-follow.jsonl`, `rea-resolve.jsonl` y `rea-session.jsonl`.
El primer intento desde el sandbox local falló al publicar el socket Unix; la
sesión útil se abrió a través de Context Mode. Se envió `--shutdown`, respondió
`{"bye":true}` y se comprobó la desaparición de sus tres procesos.

REA no reconoció las entradas `0x43b00da0`/`0x43b00dd4`; devolvió error de entrada,
no ausencia de función. Sus instrucciones se contrastaron directamente con el
blob y se ejecutaron en Unicorn. No se abrió ni modificó el Ghidra histórico.
`trace_native_values` sobre `0x43b00dd4` falló; sobre `0x438069f0` recuperó un grafo
acotado a 100 nodos/72 aristas, página de 80 nodos, una decompilación y profundidad
0. Está truncado, con alias/bindings desconocidos: no se presenta como prueba
completa de la cadena de copias. El JSONL inicial incluye consultas repetidas de
la misma sesión; no se cuentan como verificaciones independientes.

## M, Tv y clk: qué queda recuperado

`0x43843e94` copia `param_1[2]+0x138..0x167` a `P+0x4c4..0x4f3`
(exportación S58, líneas 690–713). El consumidor SOL-05 solo explica 24 B
interiores de ese origen; el bloque completo también contiene campos inicializados
por otras rutas. **PARCIAL:** se conoce una cadena de transferencias y una fuente
condicionada. **NO VERIFICADO:** valores M efectivos y alcanzables en una toma 0x0b/0x2f.
Los ceros del constructor y los patrones inyectados no sustituyen esa recuperación.

Tv: `0x4383d704` convierte los cuatro u16 `AEOUT3+0xfc+2i` con `0x4382fa94`;
antes usa `0x4383d3c0` para seleccionar/copiar bancos. **PARCIAL:** entrada inmediata
identificada. **NO VERIFICADO:** cadena completa desde controles/medición AE hasta
una selección fotográfica alcanzable. No se repiten las campañas numéricas S58
como si resolvieran esa procedencia.

clk: SOL-06 confirma su transferencia; SOL-07 descarta la atribución directa al
objeto de histogramas como prueba de procedencia. **NO VERIFICADO:** escritor final
de `P+0x4c0`, dominio alcanzable y unidad. El fallback `0xde3` del descomponedor
es una constante de software; identificarlo con 72 MHz es **INFERENCIA** y no mide
el reloj del IMX210. Tampoco se promueven 54 MHz ni el float 143 de otra tabla a
argumento efectivo de esta función.

## Restricciones, compatibilidad y modos fotográficos

- N: `0x437aa65c` copia `(*param_2)+0xa8 → X8+0x3c`; `0x43843e94`
  transfiere `X8+0x3c → P+0x22c`; luego va a G+0x30. **PARCIAL:**
  procedencia inmediata y tipo u32, sin dominio conjunto recuperado.
- svr: doce u16 de SOL-05 incluyen `X8+0x14e`; el productor consume un
  byte en M+0x16 / G+0x16. **PARCIAL:** ancho/truncamiento y origen
  condicionado; no se demuestra una lista de multiplicadores alcanzables por modo.
- VdNum: SOL-08 delimita el constructor local. El tipo signed16 del productor y
  las ramas del host requieren preservar las conversiones; no se impone
  artificialmente VdNum>0 ni ≤0x7fff a todos los estados del firmware.
- **ACEPTO** la corrección S58: productor y host no son universalmente iguales.
  **RECHAZO** interpretar una discrepancia sintética como fallo en cámara.
  Los recortes, flags y modo≠0 pueden cambiar la salida; los subdominios de SOL-09
  se limitan expresamente a modo=0/f=0 y las entradas de su campaña.
- SOL-11 precisa la expresión abreviada del host de S58: no es una fórmula
  incondicional sin guardas. Además, una discrepancia de `local_8c` genera
  diagnóstico y solo se sustituye si el bit2 del byte de control `+0x1d` está
  activo; su bit0 fuerza previamente el valor calculado. **DESCARTADO** llamarlo
  rechazo obligatorio de toda fila divergente. No se ejecutó esta política
  completa de envío/diagnóstico; se verificó estáticamente en REA y bytes.
- `0x4383b790` produce otros componentes A/B; sus límites aritméticos no prueban
  que todos los estados creados por `0x4383c9dc` superen el host ni seleccionen
  una exposición realizable. Esa composición integral sigue **NO VERIFICADO**.
- Modos `0x0b` y `0x2f`: **NO VERIFICADO** el conjunto alcanzable
  `(M,Tv,clk,N,svr,VdNum,flags)` para cada uno. La existencia de filas/tablas y
  valores `[864,4176,0]` heredados no resuelve el alias a M ni autoriza a llamar
  «alcanzables» a los escenarios sintéticos de S58/S59. **DESCARTADO** usarlos
  como prueba de cierre electrónico del sensor.

## Separación de etapas y límite físico

| Etapa | Qué acredita esta sesión | Clasificación |
|---|---|---|
| Configuración | Escritura/copia de parámetros de software condicionados | VERIFICADO en los bloques ejecutados |
| Inicio de integración | Ninguna medición ni instrucción nueva asociada a inicio eléctrico | NO VERIFICADO |
| Duración | Cálculo entero y transporte de parámetros; unidad física pendiente | PARCIAL / INFERENCIA para unidades |
| Fin de integración | Ningún evento del IMX210 identificado como cierre electrónico | NO VERIFICADO |
| Lectura | No se ejecutó ni midió lectura del sensor | NO VERIFICADO en S59 |
| Mecánica | No se demostró supresión de la segunda cortina | NO VERIFICADO |
| Sincronía BIONZ–Darwin–DFE | La publicación de estado no demuestra sincronía física ni relación fila/VD/IRQ | NO VERIFICADO |

La autonomía del IMX210 sigue **HIPÓTESIS**. La ausencia de un comando de fin no
es prueba de autonomía. Resolver alias y límites de software no establece que
lectura, fin de integración y segunda cortina sean el mismo evento.

## Reproducción y validación

Desde la raíz, Python del sistema con Capstone/Unicorn ya disponibles:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_s59_sol.py -v
PYTHONDONTWRITEBYTECODE=1 python3 analysis/s59/sol/timing_probe.py
PYTHONDONTWRITEBYTECODE=1 python3 analysis/s59/sol/inspect_timing.py
```

Resultado ejecutado: **11 tests, OK**; campañas y datos en `probe-results.json`.
Los logs `tests-before*.log` conservan fallos previos a añadir implementación;
`tests-run*.log` conservan ejecuciones posteriores reales. No se atribuye TDD a
la exploración de firmware anterior a esos tests.

Los bloques de copia usan el memcpy ARM original a través del veneer Thumb;
no se reemplazó por una implementación Python. Los segmentos internos tienen
registros inicializados a mano y punto de parada explícito; no son una captura
integral. Los dos patrones de relleno de SOL-02 afectan a páginas no mapeadas;
las guardas/patrones relevantes se escriben explícitamente en memoria mapeada.

Ruff completo y mypy (`--ignore-missing-imports --follow-imports=skip`) limitados
a los scripts y test nuevos. Los comandos de GPREMIUM sobre `src/` no corresponden
a este repositorio. El mantenimiento del conocimiento usa una copia temporal de
SQLite, los cinco pasos de indexación/grafo/exportación y salidas derivadas `.txt`
en `analysis/s59/sol/`: respeta el alcance exclusivo y no sobrescribe documentación
ni caché compartida de otras fases. El índice compartido permanece sin actualizar;
la comprobación aislada de estabilidad se conserva en `knowledge-maintenance.log`.

No hubo cámara, servicios de producción, instalación de paquetes, edición de
archivos de otras fases, `git add`, commit ni push. Quedan sin resolver valores
alcanzables y semántica eléctrica; no se propone un parche a partir de estos datos.
