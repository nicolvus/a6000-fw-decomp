# S47 — entrada del payload y orden de actualización de C

Sesión 19-10-2026; continuación puntual de
[S46](s46-vd-base-and-context-identity.md). Hito S46–S52 **abierto**.
Se resuelve el orden pedido; la cadena interna del payload llega a una frontera
de entrada verificable, pero su productor original no está identificado.

## VERIFICADO — método, integridad y límites

Proyecto `analysis/ghidra/silent-liro.gpr`, abierto siempre con
`-readOnly -noanalysis`, sin guardar. Firmware original:
`firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin`.
SHA-256 antes y después:
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Manifiestos `analysis/ghidra/s47-integrity-before.json` y
`analysis/ghidra/s47-integrity-after.json`: mismos 10 archivos protegidos,
incluidos `.gpr` y todos los archivos de `.rep`.

Consultas sobre funciones existentes con `S41Export`; zonas sin funciones,
mediante desensamblado Thumb temporal `s47-chain-listing.json`. No se crean ni
guardan funciones. `s47-order-flow.json` exporta las aristas existentes, incluidas
las cinco TBB de VD_Pre. Los exports S41/S39 contrastan los bytes cargados con
el firmware completo. No se ejecutó firmware, no hubo cámara, flasheo,
instalaciones ni operaciones git.

## VERIFICADO — dos entradas distintas al preparador

El barrido de BL/BLX/B.W en los bytes originales encuentra llamadas a
`0x437d9f9c` en **`0x437896ce`, `0x4378975a` y `0x437da09a`**.
Las dos primeras no aparecen en sus xrefs de Ghidra: pertenecen a código sin
funciones definidas. Evidencia: `s47-direct-callers.json`, `s47-input-listing.json`.
No se deduce ausencia de llamadores indirectos del resultado de este barrido.

**RECHAZO:** los inmediatos `0xce` en `0x437a1394/0x437a1576/0x438269da`
son tamaños de memcpy, y `0x43b1d9a0` alimenta el log `0x43ae769a`.
No identifican el constructor del payload; sus exports se conservan como negativos.

| Entrada | Evidencia y significado |
|---|---|
| Solicitud recibida | `0x43789708`: `r5=r0` conserva la entrada; `0x4378970e` fija tamaño `0x140`; `0x4378971a` carga destino desde GOT `0x4401f0c0=0x43e95420`; `0x4378971e` copia entrada→destino. `0x4378975a` llama a `0x437d9f9c` con ese destino. |
| Reutilización del recibido | `0x43789688`, si byte de su condición es cero: `0x437896cc` carga el mismo slot GOT, `0x437896ce` llama a `0x437d9f9c`. No construye los dos u16. |
| Solicitud sintética | `0x437da094/0x437da096` construyen `0x43ed44dc`; `0x437da098` escribe su clave `+0x1a` desde el byte de estado; `0x437da09a` llama al preparador. Este objeto no es `0x43e95420`. No se encontró aquí la construcción de los dos u16. |

**PARCIAL:** seguir únicamente `0x43ed44dc` no recupera el productor real del
payload de las solicitudes recibidas. El origen de estas últimas es una vía
distinta, demostrada por una copia nueva y por dos llamadas nuevas; no implica
alias P/C ni P/snapshot.

## VERIFICADO — cadena interna de la solicitud clave 0x00ce

1. `0x4378a3d0` registra en **`0x4378a3e6`** los argumentos
   `r0=0x301d7`, `r1=0x43e953f4`, `r2=0x43789cc1`, `r3=0`, mediante
   `0x435612b4`. Slot de callback `0x440204c4=0x43789cc1` (Thumb).
   Se demuestra el registro; no se inventa el nombre ni el contrato completo
   del servicio externo.
2. El callback **`0x43789cc0`** recibe en `r0` el paquete original y lo conserva
   en `r4`. Su clave es `u16[paquete+0x1a]`; los bytes que acabarán siendo los dos
   u16 están ya en **`paquete+0x1c/+0x1e`** al entrar. Las cargas byte de
   `0x43789cc6..0x43789cd8` los leen para diagnóstico, sin construirlos.
3. Con la selección de tabla correspondiente, `0x43789e2a..0x43789e62`
   busca la clave; GOT lleva al vector `0x43ff1b48`, cuyo índice 0 contiene
   `0x43ff23b0`. La fila **`0x43ff29b8={0x00ce,0x43789709}`** pertenece a esa
   tabla. `0x43789eee` carga el handler y **`0x43789f0e`** lo llama con el
   paquete original. Hay otras tablas/condiciones; no se afirma selección
   universal de esta fila para todos los estados.
4. **`0x43789708` → copia en `0x4378971e` → `0x43e95420`**.
   Los dos u16 quedan en **`0x43e9543c/+2`**. Los `0x140` bytes incluyen
   cabecera y payload; la respuesta sobre el paquete original se escribe después
   de `0x4378975a`, en offsets bajos, no en esos dos u16.
5. **`0x437d9f9c`** lee `+0x18/+0x1a` y pasa argumento4=`solicitud+0x1c`
   en `0x437d9fbc` o `0x437d9ffa` a **`0x437da100`**.
   Este prepara la tabla de callbacks, escribe la cabecera en
   `0x43ed461c/+2` y copia **`0x124` bytes** desde argumento4 a
   **`0x43ed4620`** (`0x437da268..0x437da274`).
   El salto final va a `0x4393ac84`: `BX PC` Thumb y rama ARM en
   `0x4393ac88` a **`0x439c5320`**. La función contenedora que Ghidra devuelve
   al consultar ese thunk compartido no representa su semántica; ver
   `s47-copy-thunk-derived.json` y la comprobación de su opcode ARM.
6. En VD_Pre, **`0x43792f9c` → `0x437da078` → `0x437da2d8`**.
   `0x437da308/0x437da30a` publica dispatcher+4 en C+8; `0x437da314`
   invoca el callback seleccionado. Con byte `0x43e959eb=0`, clave `0xce`
   y cursor válido, fila `0x43ff8adc` → slot `0x43ff7414=0x437dad79`.
7. **`0x437dad78`** copia esos cuatro bytes al scratch `0x43f7bbf4`
   (`0x437dad88`), lee u16 en `0x437dad8c/0x437dad96` y escribe C fuente:
   primero distinto de cero → `(C+94,C+95)=(1,low8(segundo))`;
   primero cero → `(0,0)`. Stores `0x437dad92/0x437dad9a/0x437dad9e`.

**NO_VERIFICADO — productor original:** no se ha localizado quién escribe
`paquete+0x1c/+0x1e` antes de entrar en `0x43789cc0`, ni una solicitud concreta
con segundo u16 igual a 2. La cadena anterior prueba transportes y condiciones;
no transforma esos datos de entrada en constantes demostradas.

**VERIFICADO — frontera adicional:** `0x435612b4` llama indirectamente al
servicio **tabla+`0x1ec`**. GOT `0x440205c0=0x43541000`, cabecera+14 apunta a
`0x435410b4`; slot **`0x435412a0=0`** en el blob. El proveedor de esa entrada y
el invocador original del callback no quedan resueltos. Esto es una referencia
nueva y distinta; no se reabren los slots/bit31 de S41 ni se atribuye al servicio
una semántica OSAL concreta solo por semejanza de otros wrappers.

## VERIFICADO — orden y rango exactos de la copia

**ACEPTO:** el callback, cuando se ejecuta en esta invocación de VD_Pre, escribe
**ANTES** de la copia. S47 supera el pendiente de orden de
[S46](s46-vd-base-and-context-identity.md); no refuta su propagación por orden.

| Operación | Direcciones y rango |
|---|---|
| Despacho síncrono | `0x43792f9c`; dentro, stores de `0x437dad78`; retorno antes de `0x43792fa0`. |
| Argumentos raíz | `0x43794086` construye destino `0x43e99514`; `0x43794092`, origen `0x43e9b548`. `r0=destino`, `r1=origen` en `0x43794096`. |
| Subcopia C en `0x43ae8faa` | `0x43ae9094/0x43ae909a` parten de raíz+`0x1e40`; `0x43ae90c8/0x43ae90cc` suman `0x2c`; `0x43ae90be` fija `0x1a4`; llamada memcpy en `0x43ae90ce`. |
| Origen C | `[0x43e9d3b4,0x43e9d558)`; campos `0x43e9d448/0x43e9d449` están dentro, offsets `0x94/0x95 < 0x1a4`. |
| Destino C | `[0x43e9b380,0x43e9b524)`; los campos llegan a `0x43e9b414/0x43e9b415`. |
| Copia posterior | `0x4379409e` llama a `0x43ae8eae` después de retornar `0x43ae8faa`. No es el sitio de la subcopia `0x1a4`. |

La prueba no se basa solo en comparar direcciones: en el CFG exportado,
`0x43794096` es alcanzable desde `0x43792a0c`, deja de serlo al retirar
`0x43792f9c`, y desde `0x4379409a` no se alcanza de nuevo `0x43792f9c`.
Las aristas TBB están incluidas. Esto prueba dominancia/orden local, sin prometer
ejecución real, ausencia de interrupciones ni exclusión de otros escritores.

**PARCIAL:** propagación del valor concreto `(1,2)` a B/G. El orden y la cobertura
de la copia dejan de ser pendientes; todavía faltan el productor original, el
payload concreto y las condiciones/sobrescrituras hasta los consumidores.
**RECHAZO:** «el callback ocurre después de esa copia» para esta ruta local.

## NO_VERIFICADO — cierre físico y próximo paso S48

No se aborda el punto opcional 3: el punto 1 sigue incompleto. No se concluye
que la escritura `0xf3120220` y C+94/95 sean independientes ni que compartan
control. No se asignan nombres eléctricos a las clases 1–3. Sin nueva evaluación
VD/cortinas ni diferenciación física completa, **el criterio de cierre no se cumple**.
No se reabren AF, consumidor/virtual+0xa8 ni alias P/C/P/snapshot.

**Próximo exacto S48:** resolver quién entrega `r0` a `0x43789cc0` para el registro
`0x301d7`; identificar el contrato/proveedor de la nueva entrada `+0x1ec`
(`0x435412a0`) y seguir la construcción de `u16[paquete+0x1c/+0x1e]` con clave
`0xce`. Ya no buscar su productor exclusivamente en `0x43ed44dc`, ni repetir
la prueba de orden/cobertura. Después, si se resuelve el productor, evaluar
la unión demostrable con `0xf3120220`.

## Validación

`analysis/ghidra/s47-audit.py`: FAIL inicial por resumen de hallazgos aún ausente;
PASS al registrarlo. Contrasta 2787 registros de listado con bytes originales,
literales PIC, tablas, thunk mixto Thumb/ARM, rangos y dominancia del CFG.
Ruff: sin avisos nuevos en los cuatro scripts S47; quedan nueve avisos previos
en cuatro tests ajenos, sin modificarlos. Mypy src+scripts S47: PASS (9 archivos).
Integridad final: PASS (10 archivos). Pytest conocimiento: **67 PASS**.
Mantenimiento completo: **1455 entidades / 2778 relaciones en ambos builds**,
idénticos; 59 relaciones de corrección, 57 filas de correcciones y 56 preguntas.
Índice: 376 archivos. Ver sección S47 de `knowledge/PROGRESS.md` y logs
`analysis/ghidra/s47-maintenance.log`, `s47-pytest.log`, `s47-ruff.log`, `s47-mypy.log`.

**ACEPTO:** entrada/copia del payload y orden antes de copia C.
**RECHAZO:** productor original identificado, valor2 demostrado y cierre físico.
**VEREDICTO: CAMBIOS** para el hito S46–S52.
