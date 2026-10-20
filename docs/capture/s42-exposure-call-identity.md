# S42 — identidad de SetExposure, productores de control y límite de exposición IMX210

Fecha: 18-10-2026. Hito S40–S45. **Resultado global: PARCIAL.**
La ambigüedad de identidad queda resuelta; captura completamente electrónica
y fin físico de integración siguen **NO_VERIFICADO**.

## VERIFICADO — método e integridad

Único proyecto abierto: `analysis/ghidra/silent-liro.gpr`, programa `av-cam.bin`,
siempre `-readOnly -noanalysis`. Sin guardar ni crear funciones, instrucciones,
tipos o referencias. Las instrucciones faltantes se decodifican temporalmente
con `pseudoDisassembleBlock`, Thumb, sin incorporarlas al listado persistente.
Se reutilizaron `S41Export.java` y `S39Export.java`; sus comentarios conservan
el nombre de la sesión que creó el exportador, no el de la ejecución actual.

SHA-256 antes de exportar y después de investigar:
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
El exportador contrasta todos los bytes cargados con el archivo. Los manifiestos
S38 de `.gpr/.rep` se verifican otra vez en `s42-audit.py`.
Sin firmware ejecutado, cámara, flasheo, instalaciones, producción ni push.

Se leyó CURRENT primero, después CONTEXT/STATE y S41; no S31–S40 completos.
Aplicadas knowledge-navigation, contradiction-audit y knowledge-maintenance.
La revisión es cruzada entre instrucciones, pseudocódigo, literales del blob,
vtable y factoría; no se ejecutó otro agente/Claude para emitir conformidad.

Evidencia primaria: `analysis/ghidra/s42-identity.json/.c`, `s42-callers`,
`s42-init`, `s42-object`, `s42-producers`, `s42-control`, `s42-config-copy`,
`s42-sequence`, `s42-mode-producer`, `s42-setters` y `s42-vtable`.
Inventarios: `s42-scan.json`, `s42-writers.json`, `s42-data-refs.json`,
`s42-mode-refs.json`, `s42-pic.json`, `s42-table-pic.json`.
Los inventarios son candidatos, no relaciones CALLS demostradas.

## VERIFICADO — CORRECCIÓN de S41: wrapper y método virtual distintos

Corrige la nomenclatura ambigua de [S41](s41-message-origin-imx210.md),
secciones «propagación de valores» y «Línea C»: `0x436d6320` es el **wrapper
de despacho de exposición**; `0x436d6f6c` es el **método del backend instalado
por la factoría IMX210**. No son alias, thunk de salto fijo ni entradas
desplazadas del mismo cuerpo. Existe una llamada **virtual**, no un BL directo.
La atribución ya no depende de cadenas próximas a RTTI.

| Instrucciones / datos exactos | Resultado |
|---|---|
| `436d6320 push {r0,r1,r4,lr}`; `436d6322 cbnz r1,436d6344` | Argumento de exposición nulo toma diagnóstico y retorna 1; ruta no nula continúa |
| `436d6344 ldr r0,[r0]`; `436d6346 ldr r3,[r0]` | Desreferencia contenedor → objeto → vtable; conserva r1 con el bloque de parámetros |
| `436d6348 ldr r3,[r3,#28]`; `436d634a blx r3`; `436d634c pop {r2,r3,r4,pc}` | Invoca slot +0x28, retorna resultado; no hay salto a mitad del cuerpo 6f6c |
| `436d72f6..436d7306` en constructor `436d72e8` | Resuelve slot GOT `44026d1c` → `43fcc088`, suma 8 e instala `43fcc090` en objeto+0 |
| Palabra en `43fcc0b8 = 43fcc090+28`: `436d6f6d` | Dirección Thumb de entrada `436d6f6c` |
| `436d650e/10/12`: carga objeto desde GOT `4401ef58` → `43e7f4a8`; llama constructor | Identidad del objeto de esa factoría, entrada `436d6504` |
| `436d6528/2e` y `43ad9054 str r1,[r0]`, `43ad9056 bx lr` | Publica objeto en contenedor `43e7f858` (GOT `44026878`) |
| `436d6118..611e` | Devuelve ese contenedor; no devuelve directamente la vtable |
| `438c830c bl 436d6320`, precedido de `436d6118` y argumento captura+64c | La llamada citada por S41 es al wrapper; con ese objeto instalado llega al método 6f6c |

**ACEPTO — VERIFICADO:** relación wrapper → método virtual en la configuración
de factoría recuperada. **RECHAZO:** identidad de cuerpos y llamada directa.
**PARCIAL:** que el contenedor conserve ese objeto en todo estado de ejecución;
no se presenta el análisis estático como una traza de cámara. La condición
captura+4b9c==0 de `438c828c` sigue siendo necesaria.

## VERIFICADO/PARCIAL — productores de argumento1+36/+37

`43842162 mov r5,r0` identifica el argumento1; las cargas de control son
`438422bc` y `438422d2`. Su llamador `438412d0`, dentro de `43841070`,
pasa el bloque **G=`43ea6ad4`**. La identidad se reconstruye desde
`438411d6` (GOT `44022420`), spill en `438411f0`, recarga/copia del spill
en `4384120a/0e` y argumento r0 en `438412ca`.

Se recupera un productor por **copia de bloque**, que un barrido de escrituras
literales a +36/+37 por sí solo no encontraba:

| Flujo con identidad | Evidencia | Clasificación |
|---|---|---|
| `C=*(contexto+50)`, bytes C+94/C+95 → B+36/B+37 | `4382e3a2/a4/a8` y `4382e3ac/ae/b2` dentro de `4382dd78`; cargas y stores **byte** | VERIFICADO en esa rama |
| B=`43eae270` | `437b5b14` resuelve `DAT_437b5d1c` y pasa el mismo uVar5 a `4382dd78` y como argumento6 de `4384b268` | VERIFICADO |
| B → G, tamaño `0xc14` | `4384cb58→437b0480`; `437b0486` tamaño, `437b0490` destino G, `437b0492→439c5320` | VERIFICADO; incluye ambos bytes |
| G → selector | `438412ca/d0→43842158`; comparación de +36/+37 en `438422bc..43842306` | VERIFICADO; si +36==1 y +37==2 permite clase2 según selector |
| Quién origina concretamente C+94=1/C+95=2 | No recuperado; no hay store inmediato2 demostrado con identidad C en estos exports | NO_VERIFICADO |
| Mecánica/EFCS/clase2 realizable desde una opción de usuario | Banco+41c y diagnóstico+7e siguen siendo controles distintos; no se asigna un nombre de menú a C+95 | PARCIAL |

El camino de `437b5b14` ejecuta antes `43844e80` y `4382dd78`, después
`4384b268`; la copia a G es condicional en esta última. `438565a8`, llamado
antes de la publicación, también se exportó: no acredita por sí mismo el
origen del valor2. No se omiten estas condiciones para afirmar realizabilidad.

**RECHAZO — VERIFICADO:** los stores `43845b68/70` como prueba del productor G.
Son copia de bytes +90/+91 de `436efa1c()` al bloque devuelto por `43859ac4()`
(`43f9d656`), otro objeto. También se descartan como prueba por offset los
contadores +36/+37 de `4386ec54` y la tabla constante de `43b71d36`.
El inventario `s42-writers.json` amplía a todo el listado las escrituras byte
a +36/+37, pero no cubre automáticamente memcpy, bases desplazadas o código
sin instrucciones persistentes. **No es una frontera estática agotada.**

## VERIFICADO — clase2: anchura, destinos y cálculo exacto

El discriminador es el **byte parámetro+9** en `436d6fb6`; clase2 entra
en `436d7114`. `r10` conserva el puntero de parámetros; `r4` es el objeto.
`436d7114..7132` conserva bits ajenos y fija máscara `0xd4` a `0x94`.

| Campo | Uso demostrado por instrucciones | Clasificación |
|---|---|---|
| parámetro+08 | `436d7136 ldrb.w r2,[r10,#8]`; `436d713a` resuelve descriptor; `436d713e strb r2,[r3,#2]` | VERIFICADO: **u8**, no u16 |
| parámetro+14 | `436d7142 ldrb.w r2,[r10,#14]`; `436d7146` resuelve descriptor; `436d714a strb r2,[r3,#2]` | VERIFICADO: **u8**, offset hexadecimal |
| Destinos | Base PIC `4401eee4`; literal `436d72d8=8ac` → slot `4401f790` → descriptor `4401c6d0`; literal `436d72dc=6c28` → slot `44025b0c` → descriptor `4401c7cc` | VERIFICADO: escribe en `4401c6d2` y `4401c7ce`, buffers de programación; no MMIO demostrado por esos stores |
| parámetro+14, segundo uso | `436d7164` recarga byte; `436d7168..7174` multiplica `(byte+1)*0x26aa` y toma `>>16` | VERIFICADO |
| Tiempo calculado | `436d7154→436d6f34(objeto+294,byte objeto+17c)`; lee entrada+4, desplaza8; `436d7160→4355faf0(...,1000)`; multiplica por u16 parámetro+0, suma1 y término anterior; `436d71e0` guarda u16 objeto+3a0 | VERIFICADO aritmético; unidades físicas NO_VERIFICADO |

Forma exacta, con truncamiento u16 final:
`objeto[3a0] = u16(u16(P[0]) * div_u32(entry[4] >> 8,1000) + 1 + (((u8(P[14])+1)*0x26aa)>>16))`.
Aquí `P[n]` denota offset **en bytes**; `entry[4]` es palabra a offset4.
`4355faf0` corresponde al helper de división unsigned; su decompilado conserva
advertencia de salto indirecto en la implementación general.

**CORRECCIÓN de lectura:** la expresión decompilada `param_2[4]/[10]` proviene
del tipo `ushort*` y de conversiones a char; las instrucciones efectivas son
LDRB a +08/+14. No se transporta el ancho u16 del tipo supuesto a la interfaz.
El listado persistente omite parte del switch; `s42-linear.json` suministra
el listado temporal. **Excluir `436d70ca..70cf`**, bytes de la tabla TBB
decodificados linealmente como si fueran instrucciones; no son evidencia de flujo.

La cola del método llama `43ad9a40` (guarda valores en objeto+fc+50..57),
`43ad99d4` (copias de bytes de configuración) y `436d9f70` (comprobaciones).
**NO_VERIFICADO:** transporte de esos buffers a registros físicos, primer/
segundo telón, consumidor temporal de objeto+3a0 y llamada/argumento que lo
enlace a `VD_Drive 4378f410` o `VD_Post 4379210c`. Ninguna proximidad ni
constante /1000 acredita sincronía. **RECHAZO** presentar clase2 como fin
electrónico de integración o exposición sin segunda cortina.

## PARCIAL — Línea A: datos de getters3023 y consumidor

Se volvieron a contrastar los datos del blob. Las filas tienen paso **16 bytes**:
clave, puntero Thumb al getter, segunda clave y discriminador. Las cuatro filas
3023 concretas empiezan en `43ffe02c`, `43ffe34c`, `43ffe6dc`, `43ffe74c`;
sus punteros están en +4. Los valores 2/3b/31/42 de +c son discriminadores
de tabla; su semántica no está tipada.

| Getter → datos | Primeros seis u16 little endian |
|---|---|
| `437fd5e4→43bf37c4` | `1,52,2,10,2,2` (hexadecimal) |
| `437fd3b0→43bf344e` | `1,54,1,7,4,66` |
| `437fd0b0→43bf3736` | `1,53,1,1,1,58` |
| `437fd11c→43bf341e` | `1,5d,3,43,2,1` |

**VERIFICADO:** son secuencias binarias compactas devueltas por getters;
no son los bytes de una solicitud3023 construida en estos getters, ni nombres
de comandos. **INFERENCIA:** descriptores/esquemas compactos, posiblemente
metadatos para construcción o transformación de mensajes. **NO_VERIFICADO:**
formato de cada opcode, tamaño de objeto descrito y consumidor parser real.
El segundo u16 no se declara tamaño sin consumidor que lo interprete.

Se buscaron referencias existentes a las cuatro regiones de tablas y candidatos
PIC; los resultados nuevos remiten sobre todo al estado `43ffee98..43ffeeac`,
no al recorrido de las filas3023. No se recuperó una llamada que tome el retorno
de esos getters y programe IMX210. **RECHAZO** clasificarlos como valores de
configuración de sensor por su ubicación. La ausencia de xrefs persistentes en
un proyecto noanalysis no demuestra ausencia de consumidor.

## VERIFICADO/PARCIAL — Línea B: identidad R y bloque SetSequenceMode

`43793530/34`, `43793538/3c`, `43793540/42` y `43793546/4a` resuelven todos
**R=`43e9b548`**, antes del store común `4379357c` a R+5cc.
Por aritmética de direcciones **R+5cc=`43e9bb14`=ImgState(`43e9baec`)+28**.
Esto habilita buscar un alias +28, pero **no demuestra una lectura**.
Las referencias existentes al destino `43e9bb14` recuperadas en
`s42-mode-refs.json` son los cuatro stores de VD_Pre, no lectores.

**RECHAZO — VERIFICADO:** usar los lectores +5cc `438553dc` y `4385558a`
como consumidores de R. Ambos resuelven GOT `44025a2c` → **`43e18c60`**;
son otro objeto. Los demás candidatos del inventario conservan su identidad
sin resolver y no se incorporan a la cadena por coincidencia de offset.

La cadena de modo puede seguirse independientemente del campo:

| Tramo | Evidencia exacta | Clasificación |
|---|---|---|
| Generación y petición | `437937be→4380f440(contexto43e99208,43e994d0,ImgState43e9baec,0)`; `4380f4da→4380e43c`, condicional | VERIFICADO |
| Copia a petición | `4380f440` copia desde `43eea2e4` a argumento2 mediante `439c5320`, largo **0x44=68 bytes**, no 44 decimal | VERIFICADO |
| Petición a estado vigente | `4378ea8c→439c5320(43e99320,43e994d0,0x44)` | VERIFICADO |
| Selección del dispositivo | `4378eab8→437957ec`, `4378eac6→4378e334`; este último lee `*(param2+8)+44` y `4378e360→43795a60` | VERIFICADO como cadena software |
| Dependencia desde R+5cc | No hay lectura con identidad demostrada que conecte `43e9bb14` con el bloque fuente `43eea2e4` | NO_VERIFICADO; aquí se corta la cadena solicitada |

`43795a60` empaqueta parámetros; su invocación no sustituye la prueba del
campo fuente ni prueba por sí sola una escritura hardware. Se auditó la vigencia
de los antecedentes de SetSequenceMode y se contrastó el tramo con exports S42.

## Pendiente real y próximo paso exacto

1. Seguir **C=`*(contexto+50)`**, escritor C+94/C+95, hasta valor concreto2;
   conservar rama de `4382dd78`, publicación condicional de `4384b268` y
   llamada `438412d0`. No volver a buscar únicamente stores G+36/G+37.
2. Seguir lectores con identidad **objeto IMX210+3a0** y los buffers
   `4401c6d0/4401c7cc` hasta transporte real y argumentos de cortina/timer.
3. Recuperar consumidor indirecto de las filas3023 y su parser antes de tipar
   sus palabras; un getter no es constructor de solicitud.
4. Buscar alias **ImgState+28** con identidad R+5cc y su posible dependencia
   hacia `43eea2e4`; distinguirla de la cadena SetSequenceMode ya demostrada.

**No se declara agotamiento estático de estas ramas.** Por ello no se activa
Línea E como sustituto: se constató que existe `firmware/extracted/a6300-fw201`
y `firmware/original/Update_ILCE6300V201.exe`, pero no se analizó otro proyecto
ni se transportaron direcciones/offsets entre modelos. La frontera OSAL bit31
de S41 no se reabrió.

## Validación

Auditor primero FAIL por manifiesto S42 ausente; después comprueba identidades,
instrucciones, literales, SHA y manifiestos persistentes del proyecto.
Los logs conservan un intento inicial sin JAVA_HOME y otro rechazado por lock
al solapar aperturas readOnly; se repitió secuencialmente. El log de productores
contiene avisos del caché OSGi; el export terminó y verificó SHA/memoria.
Las verificaciones finales y estabilidad del grafo se registran en PROGRESS S42.
No existe `.git` en este workspace: cambios sin commit.

**VEREDICTO: CAMBIOS** para cierre físico y origen de valor2.
**ACEPTO** identidad virtual y usos byte; **RECHAZO** equivalencia de cuerpos,
lectores por offset o fin electrónico inferido.
