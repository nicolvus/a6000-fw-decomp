# S46 — base VD e identidad de los escritores de contexto

Sesión 18-10-2026; continuación puntual de [S45](s45-context-identity-and-physical-closure.md).
Solo investigación estática de los dos objetivos pedidos. No se reabren OSAL
bit31, diagnóstico AF, consumidor de registros ni virtual+0xa8.

## VERIFICADO — método y evidencia

Firmware `av-cam.bin`, ORIL (firma en `0x43541004`), base lógica `0x43541000`.
No es ELF; no se aplicó un modelo de relocaciones ELF. La base VD se resuelve
por una asignación explícita de inicialización, sin necesitar hipotetizar un
loader que rellene ese slot. Esto no caracteriza todo el formato ORIL.
SHA-256 esperado: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Proyecto `analysis/ghidra/silent-liro.gpr`, siempre `-readOnly -noanalysis`;
sin guardar, crear funciones ni ejecutar firmware. S41Export compara todo el
programa cargado con los bytes del archivo antes de cada exportación.

Exports `analysis/ghidra/s46-*.json/.c/.log`; listados temporales para Thumb
sin función definida. `s46-derived-pseudocode.c` es una transcripción manual
identificada como tal: los exports `.c` vacíos de consultas sin función **no**
son pseudocódigo recuperado. El inventario `s46-offset-candidates.json` solo
enumera candidatos; no demuestra identidad ni exhaustividad de escritores.
El primer arranque falló por Java fuera de PATH; se usó el JDK ya existente,
sin instalar nada. Algunos rangos de listado incluyen pools: sus palabras no
se usan como instrucciones. El listado final del escritor termina antes del pool.

## VERIFICADO — escritor de 0x43e16d2c y destino real

| Dirección exacta | Evidencia y resultado |
|---|---|
| `0x436c224e/0x436c2250` → `0x436c6f3c` | Carga owner desde PIC `0x4401eee4`, slot `0x4402045c` = `0x43e15f18`, y llama inicialización. Ver `s46-vd-callsite.json`. |
| `0x436c6f68/0x436c6f6c/0x436c6f74` | r0=owner+`0xe10`=`0x43e16d28`; r1=literal de `0x436c71f8`=`0xf3120000`; BL a `0x436c7950`. |
| `0x436c7956/0x436c795c/0x436c7964` | r0=objeto+4=`0x43e16d2c`; r1 conserva la base; BL a `0x43acee66`. |
| `0x43acee66` | `str r1,[r0]`: escribe **`0xf3120000`** en `0x43e16d2c`. Su cero en archivo es estado previo a la inicialización. |
| `0x43ad2bd6` | La escritura condicional seguida en S45 tiene destino **`0xf3120220`**, base+`0x220`. |

El decompilador de `0x436c7950` omite r1 en la llamada al setter; el listado
`s46-vd-listing.json` preserva el argumento y elimina esa ambigüedad.
`0x436c6f8e` entrega la misma base al controlador asociado `0x436c5d2c`;
`0x436c71fc` contiene `0xf3121000` para su segunda instancia. No confundir
estos bancos con el transporte de registros IMX210 cerrado en S44.

**ACEPTO / VERIFICADO:** base MMIO concreta del controlador VD y destino
`0xf3120220`. La caché de `0x436c74c8` puede evitar el store: no es incondicional.
**INFERENCIA:** el valor empaquetado ajusta timing del controlador VD.
**NO_VERIFICADO:** unidades eléctricas, significado de sus mitades, flanco VD
efectivo, fin de integración y supresión de cortinas. Resolver una dirección
física no prueba esos efectos.

## VERIFICADO — construcción partida e identidad de C

`0x43792f84` carga el literal `0x43793644`; sumado al PC `0x43792f90`
da raíz `0x43e9b548`. `0x43792f8e/0x43792f94` construyen
raíz+`0x1e40`+`0x2c` = **C fuente `0x43e9d3b4`** en r8.
`0x43792f9a/0x43792f9c` lo pasan en r1 a `0x437da078`.
El contexto en r0 es `0x43e99208`, calculado con literal `0x43793648`.

La segunda construcción en `0x43793eae/0x43793eb4` usa literal
`0x437943c0` + PC `0x43793eb0` y produce el mismo C. Los helpers
`0x43780080` y `0x4380db04` reciben ese destino; los stores directos observados
en ellos no cubren `C+0x94/+0x95`. No se les atribuye el modo por proximidad.

## VERIFICADO — callback escritor y condiciones de +0x94/+0x95

La ruta desde `0x437da078` termina en el despachador `0x437da2d8`.
Su objeto de control es `0x43ed461c`; `+0x258/+0x25c/+0x260` son
cursor, tabla de callbacks y cantidad. En `0x437da300` r1=r2=C;
`0x437da308/0x437da30a` publican `C+8=0x43ed4620`, payload conservado.
`0x437da314` llama el callback con r0=contexto y r1=C.
Solo despacha con tabla no nula y `0 <= cursor < cantidad`.

`0x437da100`, cuando `*(u8*)0x43e959eb == 0` y su argumento3 no es cero,
selecciona tabla `0x43ff8308`, 184 filas de 12 bytes. La resolución PIC del
selector es slot `0x4402546c` → `0x43e95950`, campo `+0x9b`.
`0x43af6870` compara la clave u16 y publica la lista elegida.
La fila **`0x43ff8adc = {0x00ce, 0x43ff7414, 1}`** y el slot
**`*(0x43ff7414)=0x437dad79`** registran el callback Thumb **`0x437dad78`**.
No se denomina `0xce` opcode OSAL externo sin prueba del productor.

| Dirección exacta | Operación verificada |
|---|---|
| `0x437dad7c/0x437dad84` | Obtiene payload desde `*(contexto+0x50)+8`, es decir C+8 en esta ruta. |
| `0x437dad7e` | Conserva r1=C en r5: identidad del destino, no coincidencia de offset. |
| `0x437dad88` | Copia **4 bytes** a scratch `0x43f7bbf4`, resuelto por literal `0x437dada8` + PC `0x437dad86`. |
| `0x437dad8c/0x437dad8e` | Lee primer u16 little endian del scratch y bifurca si es cero. |
| `0x437dad92/0x437dad96` | Si primer u16 !=0: escribe `C+94=1` y lee segundo u16. |
| `0x437dad9a` | Si primer u16=0: escribe `C+94=0`; r3 sigue siendo cero. |
| `0x437dad9e` | Escribe `C+95`: byte bajo del segundo u16 en rama activa; cero en rama inactiva. |

Por tanto los destinos concretos son **`0x43e9d448` y `0x43e9d449`**.
Para producir el par `(1,2)` basta, en esta ruta, primer u16 !=0 y
`low8(segundo u16)==2`; no se requiere que el segundo u16 completo sea 2.
El callback devuelve 2 en `0x437dada2`, código que el despachador trata como
finalización de la lista; **ese retorno no es el byte de modo**.

## PARCIAL — contraste P, snapshot y propagación a B/G

| Objeto | Identidad y límite |
|---|---|
| C fuente | `0x43e9d3b4`; escritor directo anterior demostrado. |
| C consumido | `0x43e9b380`, copia `0x1a4` por `0x43ae8faa`; `VD_Pre` copia raíz en `0x43794096/0x4379409e` después del despacho `0x43792f9c`. |
| P | `padre+0x1454` en `0x437f88ec/0x43affe80`; productor `0x4385cf2c` opera sobre ese P en la ruta de S45. Padre dinámico sin identidad global demostrada. |
| Snapshot | `0x43ef2474`, copia condicional de `0x6b0` bytes desde P en `0x43859976`. Es distinto del scratch `0x43f7bbf4` usado por el nuevo escritor. |

**RECHAZO / NO_VERIFICADO:** alias P=C, P=snapshot o copia P→C por compartir
`+94/+95`. No se demuestra ninguna de esas identidades nuevas. Las condiciones
de `0x4385cf2c` no se transplantan a C. El nuevo escritor es una vía distinta,
basada en payload, y no necesita esa suposición.

**VERIFICADO, antecedente contrastado con exports S45:** `0x4382dd78` copia
C+94/+95 a B+36/+37; B=`0x43eae270`, copia posterior a G=`0x43ea6ad4`
y consumo en `0x43842158`. **PARCIAL:** el nuevo origen permite seguir
condicionalmente `(1,2)` por esas copias cuando se toman sus ramas y no hay
sobrescritura intermedia. No demuestra que una solicitud concreta llegue con
esos u16 ni que se ejecute en hardware. Falta el productor del payload y
cerrar su orden frente a las preparaciones/copias de VD_Pre.

## Pendiente real y próximo paso exacto S47

**NO_VERIFICADO:** productor original de los 4 bytes de clave `0x00ce`
conservados en `0x43ed4620`; relación con P/snapshot; semántica eléctrica
del registro `0xf3120220` y cierre de integración/cortinas.

S47: seguir el argumento4 de `0x437da100` y la solicitud copiada a
`0x43ed4620` (dispatcher `0x43ed461c+4`), encontrar quién construye los dos
u16 de la clave `0x00ce`, y demostrar el orden hasta `0x43792f9c` y
`0x4379409e`. Después contrastar el valor empaquetado de `0xf3120220`
con el controlador VD. No reabrir las ramas cerradas sin evidencia nueva.
No se declara agotamiento estático ni se activa Línea E.

## Validación

Auditor `analysis/ghidra/s46-audit.py`: ensayo inicial FAIL por resumen aún
ausente; después PASS contra literal VD, bytes del setter, construcciones PIC,
fila de registro, slot Thumb, scratch y stores/ramas exactos del callback.
Integridad antes/después: manifiestos `s46-integrity-before.json` y
`s46-integrity-after.json`, firmware y todos los archivos `.gpr/.rep`.
Pytest conocimiento: **67 PASS**. Ruff de scripts S46 PASS; src/tests mantiene
nueve avisos previos en cuatro tests sin tocar. Mypy src+scripts S46 PASS
(7 archivos). Mantenimiento completo: ambos builds dan **1455 entidades y
2777 relaciones**, idénticos; 58 relaciones de corrección, 56 correcciones y
55 preguntas exportadas. Índice: 375 archivos, 2866 secciones antes de esta
anotación final. Detalle de validación en `knowledge/PROGRESS.md`, sección S46.

**ACEPTO:** inicializador VD y escritor de C con registro, identidad y condiciones.
**RECHAZO:** alias P/C y cierre físico sin prueba.
**VEREDICTO: CAMBIOS** para cerrar el hito físico; S46 aporta las dos rutas
de escritura concretas y conserva explícitos los límites restantes.
