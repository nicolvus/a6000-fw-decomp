# S44 — consumidor de registros y tabla de modos IMX210

Sesión 18-10-2026, hito S40–S45. Evidencia estática de `av-cam.bin`.
Continúa [S43](s43-exposure-mmio-and-lock-codes.md); no reabre su conclusión
sobre selección de modo/frame-rate ni la frontera OSAL bit31 de S41.

## VERIFICADO — método e integridad

Único proyecto abierto: `analysis/ghidra/silent-liro.gpr`, programa `av-cam.bin`,
con `-readOnly -noanalysis`, sin guardar, crear funciones ni ejecutar firmware.
Se reutilizaron exportadores que consultan funciones existentes y decodifican
Thumb temporalmente. Un primer arranque falló por JAVA_HOME ausente; se usó
el JDK portable ya existente, sin instalar paquetes.

SHA-256 antes y después:
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Los exports S41Export comparan además la memoria cargada con el blob completo.
`analysis/ghidra/s44-audit.py` contrasta los manifiestos históricos S38 de
`.gpr/.rep`, las tablas originales y el resumen `s44-findings.json`.
Sin cámara, flasheo, producción, push ni modificaciones del firmware/proyecto.

Se aplicaron knowledge-navigation, contradiction-audit, knowledge-maintenance y
session-checkpoint. `claim` de S43 se ejecutó antes de reutilizarlo. Solo se
consultó el informe S43 para detalle; no se releyeron S31–S43 completos.

Exports principales, todos bajo `analysis/ghidra/s44-`:
`wire.json/.c`, `register-read.json/.c`, `backend.json/.c`, `mmio.json/.c`,
`encode.json/.c`, `virtual.json`, `mode-listing.json`, `pointers.json`,
`controls.json/.c`, `c-alias.json/.c`, `origin.json/.c`, `context.json/.c`.
Los `.log` preservan aperturas de solo lectura. Los nombres S41/S42 en
exportadores/comentarios identifican herramientas reutilizadas, no esta sesión.

## VERIFICADO — consumidor real de ID u16 y valor byte

La tabla `0x43fe995c` contiene **119 punteros**, terminados por cero en
`0x43fe9b38`. Su slot PIC es `0x44023598`. Los primeros registros son
IDs `0,1,1,2,3,4,5,6,7,8,9…`; los IDs 3–8 de S43 ocupan las entradas 4–9.
La búsqueda de alias halló 270 palabras alineadas que apuntan al intervalo
`0x4401c600..0x4401ca3f`; no todas son lectores ni registros IMX210.
Las xrefs existentes omiten varias cargas PIC: ausencia de xref no prueba
ausencia de consumidor. `S44Pointers.java` conserva el inventario.

Cadena demostrada por decompilación y listado:

| Dirección | Operación |
|---|---|
| `0x436d839c`, llamada `0x436d857c` | Obtiene la lista mediante `0x436d79b0`; llama `0x436d75f8(objeto,2,lista)` y después `0x436d5bcc(objeto+0x298)`. |
| `0x436d79b0` | Devuelve `0x43fe995c` mediante el slot PIC `0x44023598`. |
| `0x436d75f8` | Recorre punteros hasta cero; lee `*(u16*)p` y `*(u8*)(p+2)`. Para tipo 2 llama `0x436d5e04(backend,ID,valor)`; para otros tipos usa `0x43ad9004`. Backend = objeto+`0x298`. |
| `0x436d5e04` | Añade el par al paquete. Si no cabe (retorno 2), finaliza/envía el paquete con `0x43ad8db2` y reintenta el mismo par. |
| `0x43ad8fe0→0x43ad8fa2` | Comprueba capacidad y agrupa IDs consecutivos; construye cabecera/datos, actualiza ID esperado. |
| `0x43ad8dca→0x43ad8d38→0x436d5cdc` | Finaliza longitud y terminador y transmite el último paquete. |

La condición de envío de `0x436d839c` es
`actual!=0x11 || (anterior!=0x11 && anterior!=0)` sobre objeto+`0x170/+0x174`.
Por tanto la tabla no se envía incondicionalmente en toda invocación.
Después del envío tipo2, la misma función espera y prepara otra lista con tipo0;
no se atribuye a esa segunda lista el contenido de la primera.

El constructor `0x436d72e8→0x43ad8cb2` configura dirección de 16 bits y dato
de 8 bits. `0x43ad8eb0` escribe cabecera `0x81`, longitud, byte de control
`0x81` y dirección alta/baja para este formato; `0x43ad8f20` añade datos byte.
Al agrupar direcciones consecutivas evita repetir la cabecera. El buffer del
backend ocupa `+0x28..+0xa7`; los paquetes se dividen al agotarlo.
Esto demuestra un protocolo de comandos empaquetado; nombrarlo SPI/I²C o
asignar nombres eléctricos a sus señales sería **INFERENCIA**.

## VERIFICADO — transporte hasta MMIO real

`0x436d5cdc` llama configuración `0x436d5e58`, longitud/control
`0x436d5eb0` y carga de bytes `0x436d5ed0`. Esta última escribe cada byte
como palabra en `banco_A+0x40+4*i`. La tabla de bancos `0x43bc14e8`,
resuelta mediante PIC `0x4401eee4→slot0x440202b0`, es:

| Canal | Banco A | Banco B | Banco C |
|---|---|---|---|
| 0 | `0xf3c00300` | `0xf3c00800` | `0xf3c00900` |
| 1 | `0xfc088300` | `0xfc088800` | `0xfc088900` |
| 2 | `0xfc089300` | `0xfc089800` | `0xfc089900` |

La variante del constructor indexa `0x43bc16d4={1,2,0}` y guarda el canal
en backend+4. No asumir canal0 para todas las instancias.
`0x436d5e58` modifica A+`0,4,8,0xc` y B+`0,8`;
`0x436d5eb0` modifica el byte bajo de A+`0xc`;
`0x436d5f60` escribe **1→0→1 en B+8**.
La presencia de estos destinos MMIO no convierte las estructuras `0x4401c6xx`
en MMIO: su clasificación b3 de S43 se mantiene y ahora tiene consumidor.

En tipo2, `0x436d5cdc` primero carga los bytes, espera mediante
`0x43560de0(evento0x18,backend+8,...)`, limpia ese bit, activa/registra el
backend y pulsa B+8. `0x43ad8dca` marca backend+0xc; `0x436d5bcc` espera
la máscara combinada backend+8|backend+0xc. Es sincronización software
estática; **NO_VERIFICADO** que ese evento equivalga al final de integración
del sensor o a un cuadro YC válido. No se resolvió ni reabrió OSAL bit31.

## VERIFICADO — virtual+0xa8: comparación de clase de modo

`*(0x43fcc090+0xa8)=0x436d65b9`: destino Thumb `0x436d65b8`.
El llamador `0x436d92e0` busca ambos códigos en la tabla del backend+`0x294`
y entrega dos descriptores locales `{índice:u8,flag:u8}` a `0x436d938c`.
Normaliza flags de entrada mayores que1 a0. Si algún índice es `0xff`,
no llama virtual+a8 y retorna1; no hay acceso válido a tabla en esa rama.

El destino **ignora ambos flags**, toma solo descriptor+0 y busca la fila
de paso `0x14` cuyo puntero inicial coincide con `0x4401c6ac+2`.
La tabla está en `0x43fe9b74` (slot `0x44022f8c`), con 59 filas y terminador
en `0x43fea010`; la fila buscada es la primera. Compara
`tabla[fila+4+índiceA]&0xf0` frente a `tabla[fila+4+índiceB]&0xf0`.
Devuelve **1 si difieren y 0 si coinciden**. Si no encuentra fila, sus valores
inicializados a cero producen0. No escribe registros ni llama transporte.

| Índice | Código de modo en `0x43fea070` | Byte | Nibble alto |
|---|---|---|---|
| 0 | 11 | `0x0c` | `0x00` |
| 1 | 1 | `0x6c` | `0x60` |
| 2 | 5 | `0x2c` | `0x20` |
| 3 | 16 | `0x2c` | `0x20` |
| 4 | 7 | `0x2c` | `0x20` |
| 5 | 18 | `0x6c` | `0x60` |
| 6 | 3 | `0x5c` | `0x50` |
| 7 | 10 | `0x7c` | `0x70` |
| 8 | 15 | `0x0c` | `0x00` |
| 9 | 24 | `0x2c` | `0x20` |
| 10 | 26 | `0x2c` | `0x20` |
| 11 | 25 | `0x2c` | `0x20` |
| 12 | 47 | `0x0c` | `0x00` |

`0x436d6570` usa esas filas para copiar el byte seleccionado a su destino
software; por ello se compara la clase del byte preparado del registro ID0.
**INFERENCIA:** el cambio de nibble representa una transición que exige otro
tratamiento del modo. Nombre físico de esos bits y efecto sobre cortinas:
**NO_VERIFICADO**. No se revive la hipótesis AF cerrada en S43.

## PARCIAL — productor de byte+0x95=2 y alias de C

`0x4385ca3c` inicializa P+`0x94` desde un valor normalizado y P+`0x95=8`.
`0x437b3b08` le pasa P=raíz+`0x2bc`; `0x437b43b4` usa esa misma expresión
al llamar `0x4385cf2c` en `0x437b47c8` (o `0x4385d278` en la otra rama).

**VERIFICADO localmente:** `0x4385cf2c` produce P+`0x95=2` cuando el guard
global leído al inicio vale1, P+3=0, argumento5+`0x562`=0,
`*(u16*)(argumento3+0x68)` no es0 ni1 y `*(u16*)(P+0x92)>0x1000`.
Esto ocurre en la rama P+`0x8c`<2 y en la rama P+`0x8c`=2 con P+2=1.
En esta última hay store explícito `0x4385cf7a`; la primera converge al store
`0x4385cfe2`. La sobreescritura posterior a8 ocurre si
`*(u32*)(argumento5+8)=0x19` o `*(u16*)argumento2=0x313`.
El guard inicial puede saltarse toda esta actualización.

**PARCIAL:** falta demostrar que P es exactamente C=*(contexto+`0x50`)
leído por `0x4382dd78`, incluyendo las copias intermedias. No se eleva un
store con el mismo offset a escritor original de C por coincidencia.
`0x43859944` copia condicionalmente raíz+`0x2bc`, tamaño`0x6b0`, a
`0x43ef2474` (slot`0x4402196c`): candidato de snapshot, no alias probado.
La referencia adicional en `0x44004894` pertenece a una tabla de pares
ID/puntero; restarle0x50 NO demuestra una estructura de contexto.
Se preserva como antecedente la cadena B`0x43eae270`→G`0x43ea6ad4`→
`0x43842158`, sin atribuirle este productor hasta cerrar la identidad.

## Pendiente real

Identidad P/C y escritor original de C+`0x94/+0x95`; lectores IMX210+`0x3a0`;
semántica física del registro ID0 y de los IDs3–8/144–149; enlace entre este
transporte, integración, VD y cortinas. R+`0x5cc`/parser3023 siguen abiertos.
Las ramas prioritarias avanzaron hasta MMIO y comparación exacta: no hay
agotamiento estático real que justifique activar Línea E en S44.

## Próximo paso exacto

En S45, resolver el origen del argumento contexto de `0x437b5b14` y su
campo+`0x50`; contrastarlo con raíz+`0x2bc` y snapshot`0x43ef2474` antes de
transportar la condición de `0x4385cf2c` a C. Seguir después lectores
IMX210+`0x3a0` y el significado del registro ID0 aplicado por este backend,
buscando vínculo concreto con VD/integración/cortinas. No repetir la búsqueda
del consumidor ni virtual+a8; no reabrir OSAL bit31/AF sin evidencia distinta.

## Validación

Auditor S44: primer ensayo FAIL por manifiesto de resultados aún ausente;
después PASS al contrastar 119 registros,13 modos,nibbles,MMIO y `.gpr/.rep`.
`pytest tests/knowledge -q`:67 PASS. Ruff del auditor y mypy de src/auditor:
PASS; ruff src/tests conserva los nueve avisos previos en tests ajenos,
sin avisos nuevos en lo tocado. Mantenimiento completo ejecutado; ambos
builds finales conservaron1455 entidades/2777 relaciones/58 relaciones
CORRECTS/SUPERSEDES. Se eliminó del texto un falso enlace automático S44→S43
causado por la frase de auditoría, sin modificar el extractor ni el informe S43.
No hay repositorio .git utilizable: cambios sin commit.
**ACEPTO** consumidor/transporte MMIO y semántica de virtual+a8.
**RECHAZO** identificar P con C solo por offsets o declarar fin electrónico.
**VEREDICTO: CAMBIOS** para cierre físico y escritor original C.
