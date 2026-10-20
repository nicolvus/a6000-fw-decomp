# S43 — tabla PIC de exposición y revisión de códigos de modo IMX210

Fecha: 18-10-2026. Hito S40–S45. **Resultado global: PARCIAL.**
Captura electrónica completa y fin físico de integración: **NO_VERIFICADO**.

## VERIFICADO — método e integridad

Único proyecto utilizado: `analysis/ghidra/silent-liro.gpr`, programa
`av-cam.bin`, siempre `-readOnly -noanalysis`, sin guardar. Sin firmware
ejecutado, cámara, flasheo, paquetes instalados ni push. Se leyó CURRENT,
CONTEXT y STATE; no se releyeron S31–S42 completos. Se aplicaron las skills
knowledge-navigation, contradiction-audit y knowledge-maintenance; `claim`
no devolvió correcciones registradas de S42 antes de esta investigación.
La revisión solicitada por el usuario se contrastó con bytes y listado nuevo.

SHA-256 esperado, comprobado antes y después:
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Los exports S41Export contrastan además todos los bytes cargados con el blob.
`analysis/ghidra/s43-audit.py` verifica los manifiestos históricos S38 de
`.gpr/.rep`; el `.gpr` tiene tamaño cero y su hash aislado no basta.

Exports nuevos: `analysis/ghidra/s43-core.json/.c`, `s43-transport.json/.c`,
`s43-registers.json/.c`, `s43-followup.json/.c`, `s43-data-refs.json`,
`s43-fields.json` y `s43-linear.json`. Los `.log` preservan las opciones.
Los nombres/comentarios S41/S42 de exportadores reutilizados no son la sesión.

## VERIFICADO — tarea 2 prioritaria: resolución completa de la tabla PIC

En `436d6f76` se carga el literal `436d7298`; `436d6f80 add r8,pc`
usa PC=`436d6f84`. Resultado modular de 32 bits: **base=`4401eee4`**.
Los offsets de la tabla son relativos a esa base, no al literal individual.

| Literal | Offset | Slot base+offset | Puntero almacenado | Primeros 4 bytes |
|---|---|---|---|---|
| 436d72a0 | 6a34 | 44025918 | 4401c7e0 | 03 00 00 00 |
| 436d72a4 | 0584 | 4401f468 | 4401c678 | 04 00 00 00 |
| 436d72a8 | 77a4 | 44026688 | 4401c744 | 05 00 02 00 |
| 436d72ac | 3de8 | 44022ccc | 4401c684 | 06 00 00 00 |
| 436d72b0 | 48f8 | 440237dc | 4401c698 | 07 00 00 00 |
| 436d72b4 | 70d0 | 44025fb4 | 4401c764 | 08 00 00 00 |
| 436d72b8 | 4f24 | 44023e08 | 43e0a390 | 00 00 00 00 |
| 436d72bc | 2828 | 4402170c | 4401c6c8 | 44 01 00 00 |
| 436d72c0 | 5ba4 | 44024a88 | 4401c7e8 | 45 01 00 00 |
| 436d72c4 | 56e8 | 440245cc | 4401c6f8 | 46 01 01 00 |
| 436d72c8 | 568c | 44024570 | 4401c810 | 47 01 00 00 |
| 436d72cc | 2690 | 44021574 | 4401ca18 | 48 01 00 00 |
| 436d72d0 | 3d94 | 44022c78 | 4401c71c | 49 01 00 00 |
| 436d72d4 | 20b8 | 44020f9c | 4401ca2c | 01 00 40 00 |
| 436d72d8 | 08ac | 4401f790 | 4401c6d0 | 00 01 00 00 |
| 436d72dc | 6c28 | 44025b0c | 4401c7cc | 01 01 38 00 |

**Clasificación: b3.** VERIFICADO: son estructuras de datos presentes en el
blob, con identificador u16 pequeño en +0 y valor modificado en +2. Los seis
primeros identificadores son 3..8; el segundo grupo tiene 144..149 hex.
No son direcciones MMIO físicas literales ni objetos con vtable como Ofmt/Ifmt:
sus primeras palabras son 3, 4, 0x20005, 6, 7, 8, no punteros a código/vtable.
Su residencia y mutación en memoria software quedan demostradas estáticamente;
el mapa físico de RAM y la traducción de estas direcciones no se deducen del blob.
`43e0a390` es un bloque de estado distinto, consultado en +7f.

**INFERENCIA:** registros empaquetados de sensor, dirección u16 + dato byte +
otro byte auxiliar, preparados para un transporte posterior. No se ha demostrado
la semántica del cuarto byte ni se asignan nombres de registros de datasheet.
`43ad9262` confirma el mismo mecanismo: separa un valor en byte alto/bajo y
escribe cada byte en `registro+2`. `436d7e08` y `436d74b8` lo reutilizan.
Las escrituras de clase2 son a valores software de registros con ID 100/101 hex,
no escrituras físicas inmediatas a un periférico.

## VERIFICADO — tarea 3: las llamadas posteriores son almacenamiento software

El pseudocódigo reutiliza `iVar18`: antes de ambas llamadas asigna
**`iVar18=param_1+0xfc`**. Ya no es la base PIC `4401eee4`.

`43ad9a40(P,a,b,c,clase,0)` no llama otras funciones: guarda u16 en
P+50/+52/+54 y bytes en P+57/+56. En coordenadas del IMX210 son
objeto+14c/+14e/+150 y objeto+153/+152.

`43ad99d4(P,x,y)` tampoco llama ni toca MMIO: guarda ocho bytes en
P+10..+17, orden `x>>8,x,x>>24,x>>16,y>>8,y,y>>24,y>>16`.
Equivale a objeto+10c..+113. El decompilador del llamador muestra argumentos
adicionales; el cuerpo solo consume r0/r1/r2. No inferir una API de siete
parámetros a partir del prototipo recuperado del llamador.

`436d9f70` consulta máscara de habilitación de trazas y opcionalmente P+72;
los bloques posteriores imprimen datos mediante `436d6738`.
**RECHAZO** estas dos llamadas como aplicación física de timing/exposición.
**VERIFICADO:** cuerpos sin acceso a bancos `f3850400`/análogos ni transporte.
**NO_VERIFICADO:** cuándo y por qué mecanismo se envía el staging de registros
al sensor; las rutinas observadas aquí por sí solas no cierran esa ruta.

## VERIFICADO/PARCIAL — tarea 1: revisión de la hipótesis de bloqueo

**ACEPTO** que `4380e020` y `43902718` son log/trace. El primero reserva
0x9a bytes, formatea hasta 0x81 mediante `439c5004`, agrega salto de línea y
envía el paquete; el segundo formatea el mismo límite y entrega a `43902654`.
No son helpers de programación del sensor.

**RECHAZO** la conclusión de que los literales sean códigos de razón de bloqueo
AF/exposición: la evidencia positiva recuperada los relaciona con modos de imagen.
En `4378e334`, `DAT_4378e5a4+4378e568=43ca2585` apunta literalmente a:
`[CAMERA_MAIN_SYNC]: SetSequenceMode img:%d, fratechg:%d, clamp:%d, bb_out:%d cap_end:%d`.
La pareja sin prefijo está en `43ca2599`.

En `4380e43c`, resolución de literales PC-relative:

- `43cb0cd2`: `[CAMERA_MAIN_SYNC]: UnExp LC Req ImgMode`.
- `43cb0cfb`: `2KSuperSlowMotion error: IMAGE_FRAME_RATE=%d (enum)`.
- `43cb0d43`: `4KSuperSlowMotion[Buffering] error: IMAGE_FRAME_RATE=%d (enum)`.
- `43cb0d96`: `4KSuperSlowMotion[Buffering] error: SYNC_RAW_OUTPUT_SIZE=%d (enum)`.
- `43cb0e3e`: `4KSuperSlowMotion[Transfer] error: SYNC_RAW_OUTPUT_SIZE=%d (enum)`.

En case7 selecciona valores 3d/3e/10/18/1a/34 según estado y consulta
`436d6118→43ad909c` con esos mismos valores. Este wrapper despacha vtable+94;
`43fcc090+94=43ad95cf`. El destino Thumb `43ad95ce` consulta la tabla de modos
del objeto+294 mediante `43ad9438` y comprueba resultado distinto de ff.
Esto aporta una conexión positiva con disponibilidad de modos del backend.
`43795a60` conserva su primer argumento como primer campo de salida, usado
después por `4378e334` en comparaciones y preparación de secuencia.

**PARCIAL:** la rama selecciona/describre modos y prepara estructuras software;
no queda demostrada una escritura física desde `4380e43c` ni la dependencia
de `R+5cc`. No renombrar esta función como SetSequenceMode: la cadena citada
pertenece a `4378e334`. Tampoco atribuir AF/lock/reject a códigos sin cadena
asociada. La existencia de logs de error no clasifica todo el switch como diagnóstico.
Se detiene esta subrama tras refutar la hipótesis, conservando su vínculo de modo.

## PARCIAL — tarea 4 y límites

`s43-fields.json` inventaría 515 instrucciones con +3a0 o stores +94/+95.
Es búsqueda de candidatos en el listado persistente, no exhaustividad frente
a código sin analizar, alias, bases desplazadas y copias masivas. Por ejemplo,
la escritura real `436d71e0` no aparece en ese listado persistente; ya estaba
demostrada por decodificación temporal. No atribuir todos los matches al IMX210.
El slot virtual+4c apunta a `436d92e1`; se exporta su listado Thumb temporal
sin crear una función persistente. Busca ambos modos en la tabla del objeto+294,
rechaza índices ff y en `436d938c` llama virtual+a8 con los índices y flags.
El virtual+10 `436d8ff4` es un getter: copia 0x70 bytes desde objeto+180 a
la salida, después de actualizar +184/+188 según bytes de estado +a0/+a1.
No envía registros. Escritor original C+94/+95 no cerrado.

## Pendiente real

Transporte de registros software `4401c6xx–4401caxx` y lector con identidad
de IMX210+3a0; productor original C+94/+95 (especialmente valor2), dependencia
R+5cc→bloque de modos, parser3023 y sincronía física de clase2/cortinas/VD.
No se declara agotamiento de estas rutas. Línea E no activada: hay candidatos
locales nuevos. OSAL bit31 permanece en la frontera S41, sin evidencia nueva.

## Próximo paso exacto

Seguir consumidores de los registros empaquetados mediante los slots PIC que
los referencian, conservando dirección+valor; exigir un transporte demostrado
antes de llamarlo MMIO. Resolver virtual+a8 llamado por `436d92e0` con índices
de tabla y flags; virtual+10 (`436d8ff4`) queda clasificado como getter software.
Después, productor `4382dd78`: identificar C=*(contexto+50) y sus escritores
+94/+95, conservando B43eae270→G43ea6ad4→43842158. No transportar offsets A6300.

## Validación

Auditor reproducible `analysis/ghidra/s43-audit.py`; comprueba SHA, PIC, IDs,
cadena de modo, ausencia de llamadas en setters e integridad `.gpr/.rep`.
Primer ensayo falló al exigir decompilación de destinos sin función definida;
se corrigió para distinguir esos dos exports de listado sin inventar cuerpos.
La primera decodificación de rango atravesó un pool y falló; el reintento con
parada en retorno produjo `s43-linear.json` completo para ambos métodos.
Mantenimiento completo y pytest registrados en PROGRESS. Sin `.git`, sin commit.
**VEREDICTO: CAMBIOS** para cierre físico; tareas 1–3 contrastadas y documentadas.
