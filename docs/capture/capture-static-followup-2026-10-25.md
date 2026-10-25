# Seguimiento de los cinco pendientes de captura — 25-10-2026

Continúa la [auditoría del 24-10-2026](repo-audit-2026-10-24.md). Se avanzó en
los cinco puntos mediante análisis estático. **La cadena física completa y
S51 A/B/C siguen NO**. No se ejecutó firmware, no se conectó cámara ni se
flasheó. Los entregables nuevos no implican que todas las preguntas estén cerradas.

## Estado por punto

| Punto | Resultado comprobado | Qué permanece abierto |
|---|---|---|
| 1. `0x40193` | Servicio +`0x3c` = **`sta_tsk`**, tarea `0x46`, argumento descriptor `0x43ea048c`. Transporte userland→`ioctl`→OSAL kernel→recepción bloqueante LIRO identificado. | Activación efectiva de la tarea y estado de la cola en ejecución no observados; no es una validación física. |
| 2. RecordImage/RecordStill | Entrada estática concreta: estado 2, mensaje `0x10000005`, check `0x907ba0`, callback `0x90d7e8`. Mapeadas **43 llamadas** de RecordStill A6000↔A7S: 20 a la misma importación y 23 llamadas locales, agrupadas en ocho parejas candidatas. | Productor del mensaje desde el disparo, equivalencia completa de los cuerpos locales y enlace íntegro con `0x40193`, YC, archivo y cortina. |
| 3. IMX210/IMX235 | Escritor **`S[0]` localizado** en `0x43843a5e`; quinto argumento y slot GOT demostrados. Enlazado banco G→S para selector 3 y cuatro filas de 16 B. | Productores anteriores del selector, valores efectivos por modalidad, modo 1, pin `0x2a`, ciclo de buffers, correspondencia IMX235 y fin eléctrico de integración. |
| 4. S305 y CAIF | S305 original invalidado por sesgo +`0x58`; cuerpo correcto exportado. Consumidores GOT y productor por copia Backup localizados. **Constructor CAIF A7S y condición del bit `0x20` comprobados.** | Tamaño/contenido efectivos de Backup, origen UI del selector CAIF, condiciones/longitud del envío y propagación Darwin/imager. |
| 5. S176 | **Entregables reproducidos**, con dos lectores y pruebas. Default 6 en el primer lector; ocho anulaciones a cero en el segundo. | Significado físico y ejecución concreta de esas lecturas; no falta ya el entregable reproducible. |

## 1. Servicio y transporte `0x40193`

La cabecera LIRO contiene `metadata=0x435410b4` en `blob+0x14`.
El cargador de `liro.ko` copia su tabla `.init.data` de **209 entradas** a
**`*(blob+0x14)+0x24`**, no a `blob+0x24`. Esta precisión es esencial:
el servicio +`0x3c` corresponde a la relocación de tabla +`0x18`, cuyo símbolo
es **`sta_tsk`**. Su código conserva el argumento de arranque y cambia el
estado de la tarea. La función receptora es el bucle `0x4381d16c`, instalado
previamente en el descriptor. La tarea indicada es `0x46`, no una cola OSAL.

Para el envío de userland, `libosal_uipc.so:0x421c` prueba el bit `0x8000`
del destino. En `0x40193` ese bit está a cero: deriva a `u_osal_snd_msg`,
que serializa `{destino,puntero}` y usa **`ioctl 0x80000004`**. La entrada 4
del dispatcher de `osal_uipc.ko` es **`__k_4u_snd_msg`**, que llama
`osal_snd_msg` (relocación `.text+0x1b90`). Tanto envío como recepción del
kernel usan los 16 bits bajos para buscar la cola: **`0x193`**.

La recepción LIRO ya conocida es `0x4381d176 → 0x43561260`, plazo -1,
resuelta por la tabla instalada a `osal_rcv_msg_tmo`. Este último instala
internamente un receptor de espera y usa el scheduler Linux. **No requiere
una llamada específica a `osal_reg_msg_queue_cb(0x40193,...)`** para esta ruta.
El adaptador genérico de `libObj.so:0xa1b310` sigue existiendo, pero no se
debe convertir la falta de asociación a ese adaptador en un bloqueo de la
recepción síncrona ya identificada.

Lo verificado es la ruta del firmware y módulos suministrados. Carga real,
interposición de símbolos, contenidos de la cola y activación física no se
observaron. Los informes S1–S48 se preservaron como fuentes históricas.

## 2. Contrato de captura Linux

La fila 22 de `StateMgr::_FuncEntry` es
`{2,0x10000005,0x907ba1,0x90d7e9,0x907c95,1}`. Sus punteros Thumb
corresponden a check `0x907ba0`, call `0x90d7e8` y next-state `0x907c94`.
El consumidor `StateMgr::CallFunc` ya estaba verificado; el callback alcanza
RecordImage `0x90b248` por el BL `0x90de2e`, que llama al helper RecordStill
`0x908afc`. Las condiciones del check y el productor original del mensaje
siguen requiriendo seguimiento; no se afirma activación real por presionar
el disparador.

El nuevo auditor compara los 43 sitios de llamada del cuerpo de RecordStill
de 260 instrucciones con A7S `0x847e1c`. Resuelve PLT por instrucciones/GOT
y nombres importados: 20 coincidencias exactas de importación. Las otras 23
se agrupan en ocho parejas locales; registra sus intervalos unwind, incluso
cuando el destino no coincide con el inicio de ese intervalo. Igualar
posiciones de llamada no demuestra equivalencia de todos los destinos.

## 3. Selector S y banco G

[S205 actualizado](s205-imager-s0-writer.md) prueba:
`0x44020c9c → S=0x43eb35d0`; el slot había quedado fuera del barrido parcial
`0x44010000..0x44020000`. El llamador `0x437b617c` pasa S como quinto
argumento a `0x43843a44`; `0x43843a5e` escribe
`S[0]=u8(*(ctx+0x20)+1)`. Con selector 3 copia cuatro filas desde
`G+0x224+0x2c+16*i` a `S+0x64+16*i`; el productor parcial del banco G ya
estaba documentado en S147. Luego se selecciona la fila activa.

No se identifica S[0] con un modo físico de obturación ni con los códigos
Silent `0x4e/0x4f` de IMX235.

## 4. Backup, S305 y constructor CAIF

[S305 actualizado](s305-fun43858390-literal-pool.md) retira la entrada
`0x43858390`: es un bloque interior de `0x43858338`. Las trece llamadas
atribuidas eran un error ya invalidado en S303 y persistían en el backlog.

El directorio GOT `0x4401f080 → 0x43ff3200` sí tiene consumidores que
indexan sus 148 filas. `0x4378bfa0` registra `{clave,callback,contexto}` por
`Backup_reg_cb`; fila 18 = **clave `0x3000b`, destino `0x43f72d02`** en ambas
tablas de claves. El callback `0x43ae8b7a` ejecuta
`memcpy(arg4,arg3,arg2)`. `0x4378c1e4` también pasa el destino a `Backup_read`.
El módulo Backup confirma que obtiene el tamaño de la base de datos y copia
a ese destino; la actualización por callback transmite tamaño y contexto.
Esta ruta localiza una procedencia indirecta del estado, sin inventar el
tamaño efectivo ni los valores de sus gates +3/+6.

[S401 actualizado](s401-a7s-silent-control-path.md) identifica A7S
**`0x43862e24`**, caller `0x4382822c`. Su quinto argumento es el payload
`*(root+0x4ae8)+0x40`, cuando el objeto existe. Para `C=root+0x20`, la ruta
normal escribe en `0x438632b4`:

`payload[0x12] = 32*(u32(C+0x76c) == 2) + (otro_flag == 1)`.

La rama diagnóstica escribe 1. `root+0x78c` es el mismo selector que se pasa
a `0x43826d58` para elegir `0x4e/0x4f`, con bypasses y overrides adicionales.
Esto supera el pendiente «productor A7S inferido»; no certifica entrega al
MCU ni el mecanismo electrónico de fin de integración de A6000.

## 5. Reproducción S176

[Informe nuevo S176](s176-imager-state-readers.md),
[datos](../../analysis/s176_imager_state_readers/readers.json) y
[test](../../tests/test_s176_imager_state_readers.py). No se recuperaron los
archivos históricos ausentes: se reconstruyó la evidencia desde los originales.
REA recupera el primer lector con un cuerpo no contiguo: su bloque terminal
sí sustituye el byte +`0xac` nulo por 6. El segundo lector realiza ocho
escrituras a cero, sin ese default. Son hechos diferentes.

## Evidencia y reproducción

- [Auditor de API, transporte, callees y Backup](../../analysis/s380_libobj_map/followup_audit.py),
  [resultado](../../analysis/s380_libobj_map/followup_audit.json) y
  [tests](../../analysis/s380_libobj_map/tests/test_followup_audit.py).
- [Staging](../../analysis/s205_imager_s0_writer/verify_staging.py) y
  [contrato CAIF](../../analysis/s401_a7s_caif/verify_caif.py): verifican
  instrucciones y rechazan mutaciones de argumentos, pools, ramas o bits.
- [Consultas REA A6000/módulos](../../analysis/s380_libobj_map/followup_evidence/)
  y [REA A7S](../../analysis/s401_a7s_caif/rea_evidence.json). Se conservan
  también errores de cobertura/selección para no convertirlos en negativos.
- REA primero; Ghidra histórico `readOnly/noanalysis` solo para entradas no
  reconocidas. Comparten motor. Lo decisivo se contrasta con bytes y un
  decodificador independiente. Sin instalación de dependencias.
- [Contraste LLVM](../../analysis/s380_libobj_map/followup_llvm.json): 26
  instrucciones decisivas en siete bloques; las secciones de las vistas ELF
  usadas son idénticas, byte por byte, a los originales.
- 23 tests nuevos aprobados, incluidos cambios sintéticos de pools, argumentos,
  ramas y bits que deben ser rechazados. Ruff/Mypy sin avisos en los ocho
  archivos Python añadidos. Esta selección no certifica la suite integral.
- Regresión ampliada: **217 PASS**, incluidos esos 23 tests nuevos; protocolo
  MCP **6 PASS** fuera del aislamiento que bloquea su comunicación local.
  Total de esta selección: **223 pruebas**. No se ejecutó la suite integral.
- Manifiestos: cinco archivos de firmware, nueve del proyecto `silent-liro`
  y 1328 de `analysis/ghidra` comprobados sin cambios.
- Los dos casos manuales de triaje afectados por estos documentos se revisaron
  y actualizaron con evidencia exacta; las cuatro relaciones candidatas nuevas
  quedan pendientes de revisión manual. No equivalen a cuatro preguntas físicas.

## Veredicto y cola restante

**ACEPTO** los contratos estáticos, el productor CAIF, el escritor S[0],
la ruta Backup y la reproducción S176 descritos.
**RECHAZO** las trece llamadas S305, la ausencia global de slot GOT de S,
la necesidad de un callback Linux específico para la recepción bloqueante
y el cierre físico de la captura a partir de estos resultados.

Continuar con el productor del mensaje `0x10000005`, los ocho destinos locales
de RecordStill, la clave Backup `0x3000b`, el origen UI/entrega CAIF y las
aristas IMX210/YC/archivo/cortina. Los inventarios documentales de 226 etiquetas
y 66 afirmaciones son otra cobertura; no se suman a estos cinco puntos.
P1–P21 permanecen diferidas. **VEREDICTO: CAMBIOS**.
