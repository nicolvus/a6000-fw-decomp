# S34 — APL/DMA, fases VD y frontera de interrupción (18-10-2026)

Continúa la frontera física de [S33](s33-yc-rendezvous-producer.md) y el motor
de [S31](s31-camera-main-sync-strings.md), usando los callbacks resueltos en
[S32](s32-vd-callbacks-sync-ycout.md). Análisis exclusivamente estático de
`av-cam.bin`, base `0x43541000`, SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.

**Resultado: PARCIAL.** Orden software direcciones → registros → kick cerrado.
No se cierra kick → fin DMA → EC/LM ni se identifica el cuadro físico afectado.
El evento `0x80` que espera Drive no demuestra fin DMA; varias ramas lo señalan
antes de ejecutar Sequence.

## VERIFICADO — llamadores y fases

El barrido completo de BL/B.W Thumb alineados a media palabra encuentra
exactamente tres llamadas; coinciden con xrefs y listing Ghidra:

| Callsite | Contenedor completo | Slot selector | Fase recuperada |
|---|---|---|---|
| `0x4355164a` | `0x435503b0` | `0x44020064→0x435503b1` | VD_Sequence, categoría 0; selector permite también categoría 1 |
| `0x435536be` | `0x435525c0` | `0x44020e70→0x435525c1` | Igual; su bucle puede programar más de una unidad |
| `0x435557de` | `0x43554590` | `0x44021a2c→0x43554591` | Categoría 0 en las selecciones recuperadas |

No hay BL/B.W adicional, punteros absolutos par/Thumb al helper ni candidatos
del patrón comprobado LDR literal T1 + ADD PC. Esto no garantiza ausencia de
toda llamada calculada, puntero relativo o código no reconocido.

**ACEPTO:** ruta VD concreta `0x4379155c`, callsite `0x437916d4`
→ `0x43796954`, callsite `0x43796c7a` → `0x4381bf38(0x43e9de14)`
→ `0x43b047d0→0x43b0478c→0x43afb3ba` → productor → helper.
Está dentro de **VD_Sequence**, después de esperar `0x40` y antes de señalar
`0x100` en `0x437917a4`, cuando se alcanza esa rama.

**RECHAZO una exclusividad universal «solo VD_Sequence»:** el otro llamador
directo de `0x4381bf38` es `0x43796690`, tail branch de `0x437965ec`.
Viene de **HS_Sequence `0x43790b68`**, callsite `0x43790d38`, y ejecuta
**`0x43e9d810`**. El selector `0x4380e43c` puede elegir los slots de los
dos primeros productores y asigna categoría 1 cuando el ID final de trabajo
es `0x12`, `0x3f` u `8`; en otro caso categoría 0. La categoría está en
`0x43eea2fc`, offset `+0x18` del descriptor `0x43eea2e4`.
`0x4381bd4c` recibe callback desde descriptor+4 y categoría en `param_1[5]`;
`0x437965ac` resuelve 0/1 a las listas anteriores.

**PARCIAL:** esta selección no demuestra la factibilidad conjunta de cada
modo, categoría HS y rama APL ni su ejecución física. El tercer productor se
selecciona en ramas `0x26`/`0x2a`, de categoría 0. No se encontró llamada
directa desde **VD_Pre, VD_Post o VD_Drive** al helper ni a esos productores,
ni un camino resuelto de las listas Post/Drive al ejecutor Image. No se
generaliza a objetos virtuales arbitrarios.

## VERIFICADO — programación y kick síncronos

| Orden | Callsite / función | Efecto |
|---|---|---|
| 1 | `0x43815054→0x436be554` | Prepara direcciones desde handles/extents por unidad |
| 2 | `0x43815082→0x436bdbfc` | Programa configuración MMIO |
| 3 | `0x436bddf8→0x436c0354` | Banco `…0400 +0x20` |
| 4 | `0x436bde20→0x436c041c` | Banco `…0400 +0x34`, secundario |
| 5 | `0x436bde48→0x436c04e4` | Banco `…0400 +0x50` |
| 6 | `0x436bde60→0x436c06fc` | Banco `…0400 +0xa4` |
| 7 | `0x436be3a4→0x43acb2e8` | Dos llamadas a `0x436c019c`, valores 0 y 1 |

Los bancos son `0xf3850400`, `0xf3950400`, `0xf3a50400`.
Las escrituras 3–6 forman parte de una secuencia mayor, condicionada por
validaciones/estado. El helper continúa tras errores y registra resultados;
no toda invocación garantiza todas las escrituras.

**Precisión de offset:** kick escribe `0xf3850500/0xf3950500/0xf3a50500`:
**+0x100 respecto de los bancos `…0400`**, o +0x500 respecto de `…0000`.
`…0400+0x500=…0900` es otra dirección.

No hay cola ni temporizador entre programar registros y escribir el kick.
El log `Apl_Kick` está después del retorno de `0x436bdbfc`.
**INFERENCIA:** 0/1 es compatible con lanzamiento/rearme APL, pero no demuestra
inicio inmediato, espera de VD, lectura del sensor o fin de exposición.

## VERIFICADO / PARCIAL — evento que espera Drive

Drive espera `0x43560de0(0x1a,0x80,…,5)` y comprueba el número de VD.
Post espera `0x100` en `0x43792474` y encola Drive en `0x43792510`.
En la ruta normal categoría 0 con esperas satisfechas, el kick precede el fin
de Sequence y Drive encolado. **No equivale a preceder su evento `0x80`:**

| Rama de `0x437918ac` | Origen de `0x80` | Orden respecto del kick |
|---|---|---|
| `0x43e9bb18!=0` | señal inmediata `0x43791986`, antes de cola `0x437919bc` | Anterior a Sequence/kick |
| `0x43e9bb18==0`, modo distinto de 1/2 | señal inmediata `0x437919a4`, misma cola | Anterior a Sequence/kick |
| modo 2 | señal `0x4379192c`; programa callback HS | No extrapolar la ruta VD |
| `0x43e9bb18==0`, modo 1 | borra `0x80`; timer 4 en `param_1+2*context[10]`, callback `0x43ae8d3e` | Callback señala `0x80`; relación con kick depende de planificación/duración |

Timer 4 programa objetivo/control `0xf3c30134/0xf3c30130` vía
`0x436ccd9c→0x43ad6006`, banco distinto de APL.
**RECHAZO** interpretar `0x80` como prueba de interrupción de fin DMA.

Post realiza trabajo antes de esperar Sequence. Los timeouts continúan:
Post registra error y señala `0x100`; Drive registra error y también continúa.
El orden normal no es una barrera universal ante timeout/overflow.

**NO_VERIFICADO — cuadro propio o siguiente:** las tareas transportan VD
software y lo comparan con el actual. Falta la regla hardware de latch/inicio
de APL frente al flanco VD y la tupla unidad/handle/secuencia/frame del sensor.
No se demuestra un cambio de cuadro causado por kick ni que el flanco físico
sea el evento software `0x80`. No se puede elegir «propio» o «siguiente».

## VERIFICADO — registrador y conversión de causas DFE

`0x436cfae0` registra máscara y callback en cuatro slots:
`0x43e7ec28` condición / `0x43e7ec2c` función, stride 8; limpia causas
acumuladas y habilita bits mediante `0x436cf844`. Handler0 acumula
`fact & 0x03380000`, exige todos los bits de la máscara, deshabilita la
condición, borra el slot y llama al callback.

| Condición lógica | Factor, conversor `0x43ad68e0` |
|---|---|
| `1` | `0x00080000` |
| `2` | `0x00100000` |
| `0x10` | `0x01000000` |
| `0x20` | `0x02000000` |

El bit **`0x00200000`** pertenece a la máscara del handler, pero no tiene
conversión en ese registrador. No se le atribuye nombre DMA/fin/sensor.
`0x436cfbcc` elimina callbacks; `0xfc0a0018` es enable leído/escrito y
`0xfc0a0014` recibe la limpieza de factores.

El llamador recuperado del registrador es el cuerpo compartido de
`0x43ad6d74`, BL en `0x436d47e0`: construye condiciones desde descriptor
DFE+`0x14`. `0x43ad8be4` consulta bits 4/5; `0x43ad87c4`, bits 0/1.
Activa objetos de slots `0x44023400/0x44024d10` mediante `0x43ad828c`, y
`0x44021914/0x4402603c` mediante `0x43ad79ae`; llaman métodos virtuales `+8`.
No se inventa identidad APL para esos objetos.

`0x43ae9300` reenvía el callback; llamadores recuperados `0x438c7800` y
`0x43b1c6d6` (diagnóstico `DFE Start Error`); el último pasa callback cero.
No se identificó EC/LM como destino efectivo de los cuatro slots.
**PARCIAL:** tabla de condiciones software resuelta; semántica hardware aún
no resuelta. El cuerpo compartido contiene `unaff_`; se usa su listing para
la máscara/llamada, no un prototipo C especulativo.

`0x436cf818` registra handler0 en índice 9 y handler1 en 10.
`0x43ad6a0c→0x436cfd38` escribe `0xfc01f15c=9`, habilita
`0xfc01f010=0x00800000`; el otro usa `0xfc01f160=10` y `0x01000000`.
**Handler1 solo cuenta y registra llamadas**, sin dispatch de cuatro slots.

## NO_VERIFICADO — finalización física: dato exacto ausente

**ACEPTO** programación APL y dispatch DFE como hechos separados.
**RECHAZO** unirlos por nombres o proximidad: no se recuperó lectura de estado
APL `…0400`/kick `…0500` que produzca esos factores, ni callback que certifique
el handle YC y despierte EC/LM.

EC guarda VD procesado en `0x43e992dc`; LM compara y programa **timer 5**
con objetivo `context[2]+0x43e99370` (`0xf3c3013c/0xf3c30138`). EC se
encola desde `0x437926fc` con timer 0 o desde `0x43791454`.
No se demuestra que estas operaciones consuman fin de transferencia APL.

Faltan concretamente:

1. **Unidad/banco APL → estado/fin → factor IRQ**, incluida la semántica
   de `0x00200000` si resulta pertinente.
2. Callback efectivo y tupla **handle/ID/secuencia/VD**, enlazados a consumo
   EC/LM. La tabla software ya no es desconocida; falta asociarla a estos bancos.
3. Latch/inicio por VD físico para distinguir cuadro propio/siguiente.
   Aun cerrando fin DMA, no equivale automáticamente a fin de integración.

Otra rama seguida: `ExecCallBackApl`, `0x4365dde0`, es SDF OnePassCcnrEncode,
con sus propios estados. Sin identidad banco/handle no cierra esta relación.
La cadena `Apl End`, `0x43cb3b0c`, no tiene xref recuperada; consultas vecinas
son conversores de enum, no un handler de fin. No se afirma ausencia universal
de una ISR ni se da por cerrada la captura electrónica.

## Evidencia y validación

- [Hallazgos JSON](../../analysis/ghidra/s34-findings.json),
  [auditor](../../analysis/ghidra/s34-audit.py) y [resultado](../../analysis/ghidra/s34-audit.json).
- Exports `.json`/`.c` bajo `analysis/ghidra/`: `s34-timing`, `s34-interrupts`,
  `s34-causes`, `s34-links`, `s34-frontier`, `s34-apl-end`, `s34-completion`,
  `s34-final`; listing/xrefs incluidos. Logs `s34-*-headless.log`.
- Reutilizado `s32-scripts/S32Export.java` sin modificar: etiquetas S32 del
  exportador; SHA y bytes cargados contrastados antes de cada exportación.
  Siempre **`-readOnly -noanalysis`**, rollback de anotaciones transitorias.
  [Baseline S34](../../analysis/ghidra/s34-integrity.json) anterior a la primera
  apertura; hashes persistentes del proyecto idénticos al terminar, salvo locks
  transitorios excluidos. Binario intacto, sin firmware ejecutado ni cámara.
- Auditor falló primero por `s34-timing.json` ausente; después PASS de SHA,
  tres callsites, slots originales, aristas de programación/cola, causas y
  preservación. **116 consultas exportadas**, incluidas consultas de datos e
  interiores; no son 116 funciones distintas válidas.
- Interiores resueltos a contenedores completos identificados en JSON.
  `0x436cf7d0` y `0x43814e00`: pools sin función. `0x43659fce` es interpretación
  exploratoria interior de xref SDF, excluida de conclusiones.
- Ruff del auditor PASS; `ruff check src tests` conserva los nueve avisos
  preexistentes de cuatro tests ajenos. Mypy de `src` y auditor PASS.
  `pytest tests/knowledge -q`: **67 PASS**; Ruff del sistema de conocimiento PASS.

Sin instalaciones, flasheo ni push. No existe `.git`: cambios sin commit.

**Próximo paso exacto:** resolver objetos virtuales DFE de los cuatro slots
anteriores hasta registros/IRQ; contrastar con bancos APL, conservar unidad y
callback, después unir handle/VD. La importación DMM de S33 sigue pendiente;
no reabrir sus 26 llamadores ni usar la ventana temporal S32 como completion.

**VEREDICTO: CAMBIOS** respecto de la hipótesis de ciclo físico cerrado;
evidencia estática parcial aceptada, fin de exposición **NO_VERIFICADO**.
