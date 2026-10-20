# S29 — WriteStill: entrada, escritura, retorno y cierre

Fecha: 2026-10-17. A6000 FW 3.21. Direcciones de bibliotecas expresadas
como VA ELF; los exports Ghidra correspondientes usan `ELF+0x10000`.

## Resultado y alcance

Se identifica el recorrido lógico desde la orden **`0x10000003`** de
`ObjStillRecorderCore` hasta su respuesta **`0x10000004`**, incluyendo la
escritura delegada, el callback asíncrono y la devolución al Pool.
Se cierran dos huecos de S21: **RecStill→FEA** y **WriteStill→SetImageWrited**.

Esta operación escribe imágenes que ya existen en el Pool. No inicia una
exposición ni convierte las cuatro propiedades de un pin YC en una imagen.
`EncodeStill`, `Execute` y `RecordStill` son operaciones distintas, aunque
algunas confluyen en el mismo escritor MPR.

El cierre descrito es el de la operación de software. La elección del medio
activo depende de los objetos suministrados al escritor; no se afirma haber
observado una escritura en tarjeta, una barrera de durabilidad física ni
la aparición de la foto en la interfaz de reproducción.

## Recorrido principal

```text
ObjMsg: orden 0x10000003
  → dispatcher ObjStillRecorder 0x9162d0
  → ObjStillRecorderCore::WriteStill 0x909a84
      → MediaComInfo + Pool + metadatos + uno/dos UniqueId
      → preparación StillInfo y WriteStillParam
      → MprAcsr 0x8fe0a0
          → MprIf::WriteStill → FeaIf → cola FEA
          → FeaCore::WriteStill 0x440794
          → StillRecorderIf → comando 9
          → hilo Recorder → RecStill
          → StillWriterFilter: comando 5
          → dcf_If::WriteDcfFile
          → secuenciador DCF configurado
          → JPEG / RAW / MPO → escritor → FileAcc/dfs → backend de archivos
          → registros de contenido/DCF según implementación
          → filtro: resultado 4 B
          → RecStill: evento 0x66, resultado agregado 0x84 B
          → callback registrado {destino=0x1020, función=0x428bac, contexto=FEA}
          → cola FEA → dispatcher 0x42b9ac → handler 0x441644
          → callback 0x40000012, resultado 0x48 B
          → MprAcsr 0x900648 → evento local → despierta 0x8fe110
      → procesa resultados por imagen
      → cierre Pool y estados auxiliares
      → respuesta ObjMsg(0x3500, 0x10000004)
      → comprobaciones/liberaciones finales → retorna resultado
```

## 1. Entrada y preparación

**ACEPTO — VERIFICADO.** El dispatcher de `0x9162d0` obtiene el MessageId,
normaliza restando `0x10000003` y usa TBB en `0x916316`. Su entrada cero
va a `0x916328`, que llama `0x909a84` desde `0x916338`.
No se identifica esta entrada mediante una etiqueta por proximidad.

El contrato leído en `WriteStill` contiene:

| Entrada | Uso efectivo |
|---|---|
| `MediaComInfo`, obtenido al comienzo | Estado/contexto del medio y de la operación |
| `0x10000011`, `0x10000012` | Hasta dos **UniqueId**, según los diagnósticos de la propia función |
| Param compuesto `0x10000003`, mensaje interno ID `0x1000` | Grupo de información de captura |
| `0x1000` del grupo | **CaptureId** |
| `0x1001` | CapDate, 10 B |
| `0x1007` | GPS, `0x90` B |
| `0x1008`, según modo | RepresentativeImageInfo, 2 B |
| `0x100e` | StillRecCtrlInfo, 8 B |
| `0x100f` de la solicitud | Información que se conserva para responder al solicitante |

Los textos `UniqueId[%d]`, `CaptureId is not set`, `CapDate is not set`,
etc. se resuelven PC-relativamente dentro de esta función. Corrigen la
inversión CaptureId/UniqueId que aparecía en S12.

Se consultan estados del Pool/gestor, se efectúan preparaciones condicionadas
por modo y se inhibe temporalmente AutoPowerOff. Se crean uno o dos
`WriteStillParam` de **`0x40` B**. `0x90f698` recupera/prepara los
`StillInfo` de **`0x6b0` B** desde las imágenes existentes en el Pool.
No se entrega una `PIN_PROPERTY` al escritor.

`0x90a172` llama `0x8fe0a0` con esos bloques, el resultado y el número de
imágenes. La operación hermana `RecordStill` también llama ese wrapper,
desde `0x908d9c`; su respuesta externa es distinta.

## 2. Encolado y ejecución del escritor

| Etapa | Aristas comprobadas | Qué significa su retorno |
|---|---|---|
| API Obj→MPR | `0x8fe0f0 → MprIf::WriteStill@PLT 0xe0f70` | Si la API rechaza inmediatamente, el wrapper retorna el error y no espera el evento |
| FeaIf | `libmpr:0x44f784`, intermediarios `0x71cfb4/0x71cfd6` | Encola trabajo; aceptar la solicitud no significa escribir el archivo |
| Consumidor FEA | `0x42a236/0x43fc86 → FeaCore::WriteStill 0x440794` | Valida estado, parámetros e imágenes; prepara descriptores nativos de grabación |
| Preparación Recorder | `0x440aee → 0x34b1be → 0x34adb4` | Configura la operación |
| Lanzamiento | `0x440b50 → 0x34b1cc → 0x34a92c → 0x2d7d20` | Envía **comando 9** al controlador |
| Dispatcher Recorder | `0x32d5b2`, `0x32ed34`, vtable RecStill `0x81c0b8` | Selecciona el controlador RecStill |
| Máquina RecStill | `0x34cc34`, bandera `+0x956` | Avanza por estados y completados; no hay una llamada directa e inmediata del comando 9 al archivo |
| Escritores | Filtros en `RecStill+0x968/+0x96c` | Dos filtros disponibles para las imágenes/operaciones configuradas |
| Orden de escritura | StillWriterFilter `0x5144e4`, rama comando **5** | Ejecuta `0x5144b0 → 0x5141ec → 0x514366` |
| Frontera DCF | `0x514366 → dcf_If::WriteDcfFile 0x3a2e74` | Serializa y llama al secuenciador de `dcf_If+4`, slot `+0x48` |

La unión comando 9→RecStill→comando 5 está documentada y contrastada en
[S21](s21-codex-exposure-to-library.md). Sus condiciones de estado siguen
siendo parte del contrato; el diagrama no las convierte en pasos incondicionales.

## 3. Formatos, archivos y registro DCF

El objeto DCF se suministra/configura mediante el gestor de medio. Por
ejemplo, `0x34b878` consulta métodos virtuales de ese gestor y configura el
filtro; `0x51334c` conserva el contexto DCF en `filter+0x74`.
`0x512cd4` guarda otro contexto en `filter+0x78`, usado por operaciones
auxiliares como FlushAVIndexFile. No se toma ese campo como prueba aislada
de qué secuenciador está instalado.

Hay dos implementaciones comprobadas del slot de escritura:

- `dcf_AVISequence`, vtable `0x82df28`, método `0x396dcc`;
  fábrica `0x3a8508 → 0x39b9c4`.
- `dcf_Sequence`, vtable `0x832050`, método `0x3a8e24`;
  fábrica `0x3a8554 → 0x3a9740/0x3a9758`.

Los constructores `dcf_If:0x3a83bc/0x3a842c` eligen fábrica según el
argumento recibido. Por eso no existe una única selección universal para
todas las solicitudes. La siguiente expansión corresponde a la implementación
AVI recuperada, conservando esa condición:

| StillInfo Linux `+0x6ac` | Archivos/contenidos |
|---|---|
| 0 | JPEG |
| 1 | RAW |
| 2 | JPEG + RAW |
| 3 | JPEG + MPO |

JPEG usa `0x38b064`, RAW `0x381a18`; convergen en el escritor común
`0x3816bc`. RAW construye ARW con sus datos y metadatos: no renombra un
buffer YC. La salida baja por `0x381594 → 0x3bd3bc → 0x3bcfbc`, donde
se seleccionan operaciones dfs/FileAcc. Hay rutas de escritura y de
escritura con flush; adaptadores `0x3b85a8/0x3b85da` alcanzan Fsys.

En AVI, tras las escrituras se registran los contenidos:

```text
JPEG: 0x397116 → 0x1d6c76 → RegisterJpegContent 0x22c190
RAW:  0x39746e → 0x1d6cb6 → RegisterRawContent  0x22d1cc
                  ↓
0x397494 → 0x1d6cc6 → RegisterDcfContent 0x22d648
```

El prólogo `0x396e24 → 0x38c220` precede localmente a
`0x396e42 → RecStartDcfContent`. No se reordena esa secuencia para hacerla
parecer una transacción atómica. El pre-registro que puede hacer `Execute`
es una ruta anterior y condicionada; no es un paso universal que se añada
automáticamente a esta orden alternativa `WriteStill`.

Las rutas de error del escritor incluyen cierre y eliminación de archivos.
Errores posteriores de registro también se propagan. La mera existencia de
`CancelRecStartDcfContent` y `FlushAVIndexFile` no demuestra compensación
completa de archivo+índice ni flush durable antes de cada callback.
El backend físico concreto y esa garantía no se deducen de un retorno cero.

## 4. Retorno asíncrono: hueco S21 cerrado

**ACEPTO — NUEVO, VERIFICADO.** El registro se ve en
`0x43f57e..0x43f58e`:

```text
this = FeaCore+0xd8c  (StillRecorderIf)
target = 0x1020
function = [0x43f5b0] = 0x428bad  (Thumb: 0x428bac)
context = FeaCore
llamada virtual slot 0 → 0x34b138
```

`0x34b138 → 0x2d7db0` conserva target/function/context en el controlador
con offsets `+0xc/+4/+8`. RecStill emite el evento `0x66`, payload
**`0x84` B**, mediante `0x34c848 → 0x2d7dd0`. Este último llama al callback
con contexto como quinto argumento.

El callback `0x428bac` encola la tupla en `FeaCore+0x34` y despierta el
trabajador. El hilo `0x428c0e` llama al slot `+0x24 → 0x4299d8`; este saca
la entrada y despacha los destinos con bit `0x1000` por slot
`+0x2c → 0x42b9ac`.

Para target `0x1020`, el dispatcher selecciona familia `0x20`. Resta
`0x64` al evento: `0x66` elige índice 2 de TBB `0x42bbf2`, cuyo byte es
`0x14`; destino `0x42bc1a`. Su branch de `0x42bc26` va a **`0x441644`**.
`0x441694` era una instrucción interior de este handler, no su entrada.

El handler transforma el resultado del controlador en el contrato FEA de
**`0x48` B**; llama al slot `+0x1c` de FeaCore con evento
**`0x40000012`**, en `0x441960/0x441b00` según la rama.
No se igualan los buffers `0x84` y `0x48`, ni el resultado de filtro de 4 B.

El tramo de regreso conocido queda enlazado:

```text
FeaCore slot+0x1c → 0x429000 → callback de MprAcsr
  → receptor Obj 0x900648
  → rama 0x90081c: ObjMsg(0x3500,0), Struct paramId=0, tamaño=0x48
  → EventSender local 0x90084c
  → EventReceiver / WaitEvent(UINT32_MAX) en 0x8fe110
  → copia de resultado en 0x8fe15e
  → retorno de MprAcsr a 0x90a176
```

**RECHAZO:** interpretar la llegada de `0x40000012` como éxito por sí sola.
También existe en rechazo previo; se comprueba el resultado transportado.
Si la API MPR falla inmediatamente, `0x8fe0f6` evita la espera del evento.

## 5. Resultado por imagen, Pool y devolución de recursos

Tras volver de MPR, `WriteStill` examina los resultados por imagen. La ruta
de éxito y la de error aplican estados diferentes mediante helpers como
`0x90f038`, `0x90f106`; no se marca toda la solicitud exitosa solo porque
uno de sus archivos se haya escrito.

**ACEPTO — NUEVO, VERIFICADO.** El cierre que faltaba en S21 es:

```text
WriteStill: 0x90a318 → 0x910f28
  → 0x91bb84 → 0x8fd738
      → mcmn_drv_buf_clear(0x2f, ...)
      → 0x8fc7b0: orden Pool 0x6108/0x100b
      → 0x8fc484: orden Pool 0x6108/0x1007
          → tabla registrada por InfraStillPool
          → 0x939dd8 → InfraStillPool::SetImageWrited 0x932a44
      → decrementos de contadores locales bajo lock
```

La tabla de operaciones de Pool es de registros de `0x1c` B. En VA
`0x101f838` figura **`0x1007`**, y en `+0xc` (`0x101f844`) el callback
**`0x939dd9`**. La tabla se copia/registra desde el constructor
`0x93957c`, con longitud `0x460` y 40 registros en `0x9395f0..0x939604`.
`0x932a44` encuentra la entrada por `0x1003`, actualiza su gestión de
referencias y recorre las entradas pendientes. Su nombre se confirma por
diagnósticos `SetImageWrited` / `InfraStillPool.cpp`.

**RECHAZO:** `0x6108/0x1009 = SetImageWrited`. La tabla asigna `0x1009`
a **`0x939da8`**, no a `0x939dd8`. Los clientes `0x8fc538/0x8fc62e`
estudiados en S21 pertenecen a esa otra operación. Tampoco se confunde
`0x100b`, enviado justo antes en la limpieza, con SetImageWrited.

Después se ejecuta `0x90f364`, que alcanza `0x91baf4 → 0x8fd7b8`
(consulta de estado local) y auxiliares del contexto. `0x90fec8/0x90ff8c`
alcanzan `DatabaseAcsr::RunChangeHndlStatus` (`0x9189b4`) y
`EndChangeHndlStatus` (`0x918bc0`) en sus ramas condicionadas.
`0x90f274` actualiza el contador local; se desactivan los ajustes temporales
del wrapper MPR. Cuando corresponde se reactiva AutoPowerOff y se ejecutan
restauraciones de estado por modo.

Esta es una cadena de llamadas real de limpieza y gestión de referencias;
no demuestra el instante del último acceso DMA ni que todo consumidor
externo haya soltado cualquier alias de los buffers.

## 6. Respuesta externa y último retorno

**ACEPTO — CORRECCIÓN NUEVA.** Esta operación construye en
`0x90a3b8..0x90a440`:

```text
ObjMsg(category=0x3500, messageId=0x10000004)
  0x1001 = resultado
  0x1002 = CaptureId
  0x100f = parámetro de información conservado de la solicitud
  → slot +0xc del emisor en this+0x18
```

El ID se comprueba en el literal **`0x90a608 = 0x10000004`**.
No es la respuesta `0x3500/0x3002` de la operación `Execute`.
El `0x100f` reenviado no se presenta como un nuevo certificado de alta DCF
producido por el callback MPR.

Después del envío todavía hay comprobaciones/restauraciones locales. Una
rama condicionada puede emitir otro mensaje **`0x10000007`**, con resultado
7 y el mismo `0x100f`; su literal está en `0x90a60c`. Finalmente se destruyen
los temporales y se retorna el resultado desde `0x90a558` al dispatcher.
Por tanto, «se envió la respuesta» y «ya retornó la función» son hitos distintos.

## Errores y garantías del cierre

| Situación | Qué permite concluir el código |
|---|---|
| Falta imagen, metadatos o estado admisible | Puede rechazarse antes de escribir; revisar resultado y rama, no solo la presencia de un callback |
| API MPR devuelve error inmediato | El wrapper no queda esperando su evento de finalización |
| Fallo del escritor o de registro | Se propaga mediante resultado; existen rutas close/remove, pero no se ha probado una transacción atómica universal |
| Dos imágenes, resultados diferentes | El cierre procesa estados individuales; no equivale automáticamente a un conjunto completo exitoso |
| Respuesta final `0x10000004` con resultado 0 | Finalización satisfactoria según el contrato software recorrido |
| Foto durable tras pérdida de energía o visible en reproducción | Requiere garantía del backend/flush/catálogo; el mensaje final no la acredita por sí solo |

## Evidencia y reproducción

Reutilizados S20/S21 para las APIs, escritores y variantes DCF, contrastados
con los SHA originales. Nuevas ventanas LLVM: `s29-write-completion-verified`,
`s29-obj-close`, `s29-pool-close`, `s29-pool-writed-path` y
`s29-write-entry-pool-registration`, todos `.json` en
`analysis/session22/evidence/`.

Los exports decompilados `s29-mpr-completion.json`,
`s29-obj-pool-functions.json` y `s29-obj-terminal-helpers.json` son auxiliares.
Las consultas interiores, funciones fusionadas y advertencias PIC no fijan
por sí solas límites ni ABI; los cierres nuevos se apoyan en instrucciones,
TBB, relocaciones y tablas ELF verificadas. El lector de datos usa PT_LOAD:
en `libObj.so`, VA de tablas **no equivale** a offset de archivo.

`QueryLibraryExisting.java` permite consultar funciones ya existentes sin
intentar cambiar su contexto de instrucciones: el exportador anterior falló
con `ContextChangeException`. Se usa en proyectos de análisis con `-readOnly`.

Auditor: `python3 -I analysis/session22/evidence/s29_writestill_audit.py`.
Comprueba SHA de ambas bibliotecas, evidencia, registro del callback,
dispatcher `0x66`, entrada/salida WriteStill y operación real SetImageWrited.
El primer pase falla únicamente porque faltaba este documento; cinco
comprobaciones de binario ya pasaban.

Validación final: **6/6 PASS**. `mypy --ignore-missing-imports src` más el
auditor: PASS (6 archivos). `ruff check src tests` más el auditor conserva
los nueve avisos previos en cuatro tests ajenos; ningún aviso en lo añadido.
README, CONTEXT, índice de captura, notas S12/S21 y README Ghidra actualizados.

**VEREDICTO: APROBADO para la cadena lógica WriteStill→retorno→cierre.**
No se extiende a durabilidad física, presentación en reproducción ni
adquisición de una nueva foto sin mecánica. No se ejecutó firmware ni se
instalaron paquetes. Sin repositorio `.git`: cambios sin commit y sin push.
