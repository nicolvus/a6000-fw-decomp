# Registro MPR/DCF y StillInfo — tarea A

Investigación estática de Sony A6000, firmware 3.21, 2026-10-16. No se ejecutó firmware ni se conectó cámara. El JSON [stillinfo-layout.json](../../analysis/stillinfo-layout.json) contiene offsets en decimal, hashes de binarios, pseudocódigo, listing y fuente del extractor reproducible.

**VERIFICADO:** existen tres ABI diferentes: payload LIRO de 0x28c, StillInfo Linux de 0x6b0 y WriteStillParam de 0x40. **NO VERIFICADO:** todavía no hay una instancia mínima que garantice guardar y reconocer en reproducción un JPEG externo de 1024 px.

Convención: todas las direcciones de libObj.so y libmpr.so de este documento son VA ELF; sumar 0x10000 para Ghidra. LIRO usa VA directa. Los nombres descriptivos de funciones stripped son reconstrucciones; el listing prevalece sobre tipos inferidos por el descompilador.

### 1. Layout completo y transporte

**ACEPTO — VERIFICADO:** Stage_Notify LIRO 0x437efe78 copia 0x28c bytes mediante 0x43afe932 desde contexto C=0x43ae75dc, C+0x4bb0, a mensaje+0x14. Envía 0x2a8 bytes por 0x437feef8 con argumento 0x20002. El éxito de ese envío no acredita escritura.

| Mensaje | Tamaño | Contenido |
|---|---:|---|
| +0x00 | 1 | Tipo 4 |
| +0x01 | 1 | NO VERIFICADO: no asignado en esta función |
| +0x02 | 2 | Código 0x1006 |
| +0x04 | 4 | Secuencia de C+0x4b64 |
| +0x08 | 4 | Resultado 0xf000 |
| +0x0c | 4 | Identificador de captura C+0x4b54 |
| +0x10 | 4 | Valor de C+0x1dc; significado no demostrado |
| +0x14 | 0x28c | StillInfo LIRO |
| +0x2a0 | 8 | Dos words C+0x4b58/C+0x4b5c |

**VERIFICADO:** cobertura de StillInfo; los huecos están delimitados, sin atribuirles semántica de padding demostrada.

| StillInfo | Mensaje | Tamaño | Campo |
|---|---|---:|---|
| 0x000 | 0x014 | 4 | captureId |
| 0x004 | 0x018 | 0x0a | capDate |
| 0x00e | 0x022 | 2 | Desconocido |
| 0x010 | 0x024 | 0x90 | GPS |
| 0x0a0 | 0x0b4 | 0xb0 | JpgInfo |
| 0x150 | 0x164 | 0x120 | RawInfo |
| 0x270 | 0x284 | 8 | StillRecCtrl |
| 0x278 | 0x28c | 0x10 | MpoInfoAdr |
| 0x288 | 0x29c | 2 | faceScore y bracketScore |
| 0x28a | 0x29e | 2 | Desconocido |

**VERIFICADO:** JpgInfo tiene once descriptores de 0x10, según libObj 0x935b20 y conversión 0x930508. Cada uno contiene u32 memHandle, u32 offset, u32 size, u32 argumento de reutilización. DMM consume los 16 bits bajos del handle; el último word se pasa a DmmReuseAndOpen, no está probado que sea reservado.

| Campo | Dentro JpgInfo | StillInfo | Mensaje |
|---|---|---|---|
| exifSrcArea | 0x00 | 0x0a0 | 0x0b4 |
| model | 0x10 | 0x0b0 | 0x0c4 |
| software | 0x20 | 0x0c0 | 0x0d4 |
| lensModel | 0x30 | 0x0d0 | 0x0e4 |
| publicMakerNote | 0x40 | 0x0e0 | 0x0f4 |
| pimInfo | 0x50 | 0x0f0 | 0x104 |
| secretMakerNote | 0x60 | 0x100 | 0x114 |
| mpfSrcArea | 0x70 | 0x110 | 0x124 |
| mainJpg | 0x80 | 0x120 | 0x134 |
| thumJpg | 0x90 | 0x130 | 0x144 |
| screenNail | 0xa0 | 0x140 | 0x154 |

**VERIFICADO:** RawInfo conserva los ocho primeros descriptores EXIF y después thumJpg, developInfoSrcData, decryptionKey, developInfoArea, dumpOfRegister, rawMainSrcData, rawMainCFAPattern, screenNail, rawMain y rawAdditionalInfo (0x935df4). Los offsets y tamaños individuales están en el JSON.

**VERIFICADO:** capDate: +0x00 td i16, +0x02 año i16, +0x04 mes, +0x05 día, +0x06 hora, +0x07 minuto, +0x08 segundo; +0x09 desconocido (dumper 0x9365c0). GPS contiene flags y valores para versión, latitud, longitud, altitud, fecha, hora, estado, modo, DOP, velocidad, rumbo, dirección de imagen y mapDatum (0x936000); el JSON desglosa sus offsets. No se han demostrado todos sus enums ni bytes de alineación.

**VERIFICADO:** StillRecCtrl contiene colorModeFlag u32 y recMode u32. El dumper distingue sRGB/Adobe y JPG/RAW/JPG+RAW/otro; no implica que cualquier valor distinto sea válido universalmente.

### 2. Campos y condiciones obligatorios

**ACEPTO — VERIFICADO:** RecordStill 0x908afc prepara WriteStillParam; MprCtrl::WriteStill 0x8fe0a0 llega a FeaCore::WriteStill de libmpr 0x440794. Este último comprueba estado, disponibilidad del escritor, cantidad hasta dos, identificador no cero en WriteStillParam+0x18 y correspondencia con líneas de grabación activas. Hay acceso temprano a parámetros: estos checks no constituyen una API segura para punteros arbitrarios.

**RECHAZO — DESCARTADO:** interpretar WriteStillParam+0x18 como handle DMM. Se resuelve por 0x447810 → 0x66d0c8, como objeto de grabación. Es distinto de los handles de memoria de JpgInfo.

**VERIFICADO:** WriteStillParam mide 0x40; RecordStill inicializa fecha en +0x00, words +0x10/+0x14 a 1, identificador de objeto en +0x18, bytes +0x28=1/+0x29=0/+0x2a=1, dato del propietario en +0x2c, +0x30=0x65 y fecha original en +0x34. Otros espacios se inicializan a cero. Los valores observados no permiten inventar nombres de enums.

**VERIFICADO:** la ruta habitual de EXIF nuevo exige miniatura y reserva escribible previa al JPEG (libmpr 0x38b064). **NO VERIFICADO:** conjunto mínimo exacto de etiquetas EXIF, MakerNote, dimensiones y alineamientos que produce una fotografía aceptada extremo a extremo.

### 3. Campos omisibles y generación

**ACEPTO — VERIFICADO:** RecordStill tolera ausencia de capDate, orgDate y StillRecCtrl con valores por defecto y log. GPS/CamInfo ausentes invocan setters desactivados. Que el wrapper continúe no garantiza que todas las combinaciones lleguen a un fichero válido.

**ACEPTO — VERIFICADO:** libmpr 0x37a51c contempla model/software/lensModel nulos; 0x38b064 contempla screenNail de tamaño cero. Esto prueba ramas consumidoras, no que todos los descriptores DMM correspondientes admitan handle cero en los convertidores anteriores.

**RECHAZO — DESCARTADO:** suponer que MPR genera automáticamente la miniatura de un JPEG externo. En la ruta de EXIF nuevo, la rama normal con tamaño de miniatura cero da «Thumbnail not found» (0x38b064). Con EXIF original configurado mediante 0x37b170 puede recuperarla a través de 0x38ba98; no demuestra un reescalado automático.

**NO VERIFICADO:** omitir exifSrcArea completo. Que modelo y software tengan ramas nulas no prueba que la fuente EXIF, que tiene accesos internos, pueda ser nula.

### 4. Quién valida cada representación

**ACEPTO — VERIFICADO:** mapa reconstruido de llamadas y transformaciones:

```text
LIRO 0x437efe78 → msg 0x1006
 libObj SeqStillCap 0xa3b650
 → dispatcher 0x9bc9a8 → handler 0x9a9c68
 → parámetros MWF → MakeStillRecInfo 0x930508
 → 0x92d6d8 → EXIF 0x92c8d0 / miniatura 0x92abf4 / JPEG 0x92a140
 → MakeStillInfo 0x92e9d2 / áreas JPEG 0x92e604
 → RecordStill 0x908afc → MprCtrl 0x8fe0a0
 → libmpr FeaCore 0x440794 → cola y escritor DCF
```

**VERIFICADO:** el handler se resuelve también por GOT, no solamente por BL: base ELF 0x102cbd0, slot 0x102f880, puntero Thumb 0x9a9c69. Para mensaje interno 0x2008 extrae captureId→0x1000, fecha→0x1001, GPS→0x1007, JPG→0x100b, RAW→0x100d, control→0x100e, MPO→0x100f, representativa→0x1008 y footer→0x1012. El parámetro MWF 0x1006 (CamInfo) pertenece a otro espacio de identificadores que el mensaje de transporte 0x1006.

**VERIFICADO:** ObjConverter abre descriptores y construye áreas; FeaCore valida el objeto y estado; el escritor valida reserva y miniatura. **NO VERIFICADO:** comprobación exhaustiva de offset+size contra capacidad física para cada descriptor. Las rutas de éxito observadas no justifican pasar buffers fabricados sin contrato.

**VERIFICADO:** StillInfo Linux mide 0x6b0, con áreas de puntero u32+tamaño u32:

| Offset | Área |
|---|---|
| +0x04 | captureId |
| +0x08..+0x47 | Ocho áreas EXIF en el mismo orden que JpgInfo |
| +0x48 | mainReserve |
| +0x50 | mainData |
| +0x58 | thumJpg |
| +0x60 | screenNail |
| +0x68..+0x60f | MPO: contadores y almacenamiento de entradas |
| +0x610..+0x6a7 | RAW |
| +0x6a8 | colorModeFlag |
| +0x6ac | recMode |

**NO VERIFICADO:** semántica de word inicial +0x00 y capacidad de MPO como enum público. La copia de 0x6b0 de FeaCore no debe confundirse con la copia LIRO de 0x28c.

### 5. Traducción de memHandle a puntero

**ACEPTO — VERIFICADO:** 0x92980c llama DmmOpen o DmmReuseAndOpen(argumento +0xc, handle) según modo y seguimiento. 0x92a140 obtiene extents mediante DmmAccess y compone mapeo con ioctl/mmap (PLT ELF 0xe2ac4/0xe11b4); 0x938fc0 contiene el soporte de mapeo. El paginado usa 0x1000, con helper 0x948eb0.

**VERIFICADO:** reserva, JPEG y screenNail se representan como segmentos 1/2/3; miniatura como 0; EXIF como 4..0xb. Si main y screen comparten handle y main.offset+main.size==screen.offset, existe combinación contigua. 0x92e604 resuelve segmentos mediante 0x929630 y publica base+offset y tamaño.

**RECHAZO — DESCARTADO:** convertir memHandle a puntero con un cast, o usar el identificador de grabación como memHandle. Son tres dominios: DMM, objeto de grabación y dirección virtual Linux.

### 6. Retención y liberación

**ACEPTO — VERIFICADO:** 0x929788 registra handles no cero sin duplicados; esa lista por sí sola no incrementa referencias. 0x92980c distingue reutilización/apertura. Tras crear mappings se cierran aperturas temporales; el objeto convertido conserva mappings y metadatos.

**VERIFICADO:** limpieza 0x92d7a2 → 0x929698 desmonta mappings y libera estructuras; la limpieza de lista 0x928f78 incluye DmmCloseAndFree. SeqStillCap en descarte tipo 0xe libera handles de EXIF/main/thumbnail/screen mediante 0xa1a7f8. LIRO libera locales mediante 0x43903414(h,5) tras su notificación.

**NO VERIFICADO:** equivalencia exacta de referencias LIRO/Linux y momento seguro para soltar la última referencia de un JPEG externo. Las llamadas virtuales +0xac/+0xb0/+0x150, a través de 0x447d68/0x447d88/0x447f92, no tienen todavía semántica de retain/release demostrada. Mantener memoria hasta final de escritura es una condición de diseño, no un conteo de referencias probado.

### 7. Construcción DCF y registro

**ACEPTO — VERIFICADO:** libmpr 0x38b064 lee mainReserve, mainData, thumJpg y screenNail a +0x48/+0x50/+0x58/+0x60. Construye cabecera y metadatos, calcula espacio para miniatura, relleno y datos auxiliares, y rechaza reserva insuficiente. El cálculo incluye ajuste de bloques de 512; no se ha reducido a una constante mínima universal.

**VERIFICADO:** WriteDcfMemory 0x37af44 recibe flag, exifAddr/size, mainAddr/size, thumbnailAddr/size, reserveAddr/size. Comprueba reserva ≥ EXIF+miniatura, copia miniatura inmediatamente antes del JPEG y EXIF antes de ella; llama 0x3752c0. La comprobación simple de esta función no sustituye el cálculo más amplio del constructor.

**VERIFICADO:** 0x38b958 interviene en nombres, directorio, apertura y contenido DCF. Su evento por 0x35e638(0x20, ..., 0xf, ..., 0x1e) aparece durante preparación de ruta; no está probado como notificación final a reproducción.

**RECHAZO — DESCARTADO:** equiparar escribir bytes con fopen o recibir envío OK a registrar una foto nativa reconocible.

### 8. Evento que actualiza reproducción

**NO VERIFICADO:** no se identificó el evento exacto ni su receptor en el catálogo de reproducción. RecordStill::Execute 0x90b248 responde mediante ObjMsg 0x3500/0x3002, parámetro 0x1001 de error y 0x100f de información de contenido de 0x28 bytes.

**RECHAZO — DESCARTADO:** llamar a esa respuesta «evento de actualización de reproducción» sin seguir sus consumidores. Tampoco el evento de preparación de ruta de 0x38b958 demuestra invalidación del catálogo.

### 9. MPR sin Stage_SACC

**INFERENCIA:** los argumentos de la API Linux son memoria convertida, metadatos y objetos de grabación, sin argumento explícito Stage_SACC. La conversión separada muestra un punto potencial de entrada para JPEG externo.

**NO VERIFICADO:** independencia completa de Stage_SACC y de su configuración lateral. No se deduce desconexión por ausencia de BL, especialmente con GOT y llamadas virtuales. No se ha ejecutado una escritura sustituyendo la procedencia del JPEG.

### 10. Mínimo teórico para JPEG de 1024 px

**HIPÓTESIS:** candidato condicionado, sin handles ni EXIF inventados:

| Elemento | Condición propuesta | Evidencia/límite |
|---|---|---|
| Sesión | MPR iniciado, writer y objeto de grabación activo | Checks 0x440794 |
| JPEG | 1024×H, size real, buffer mapeable y vivo | 1024 no validado extremo a extremo |
| Reserva | Memoria escribible antes de mainData | 0x38b064 / 0x37af44; tamaño depende de cabeceras |
| Miniatura | JPEG válido y no vacío para creación EXIF nueva | Error explícito si falta |
| EXIF | Fuente coherente con dimensiones/fecha/miniatura | Bytes mínimos y MakerNote pendientes |
| Metadata opcional | GPS desactivado; screenNail ausente por rama soportada | No equivale a autorizar cualquier handle cero |
| Modo | JPG, sin RAW/MPO; usar valores nativos del wrapper | recMode=0 observado |
| Vida útil | Mappings/objeto conservados hasta resultado de escritura | Conteo interprocesador pendiente |
| Reconocimiento | Seguir final DCF y consumidor de información de contenido | Evento de catálogo pendiente |

**NO VERIFICADO:** no existe una estructura mínima binaria validada ni prueba de aceptación de JPEG SFRA READY. H=576 sería una decisión de diseño, no un requisito probado del firmware. Una plantilla rellena de ceros no satisface el contrato demostrado.

## Validación, límites y continuación

**VERIFICADO:** los ensayos estructurales comprueban cobertura exacta sin solapes de 0x28c, tamaño de mensaje, once descriptores, offsets de mainJpg, separación de dominios, diez respuestas y presencia de evidencia con espacio de direcciones. Primero fallaron por ausencia de entregables; el resultado final se registra debajo. No son tests de ejecución del firmware.

**NO VERIFICADO:** bloqueos concretos: contenido EXIF mínimo; capacidad/reserva exacta del JPEG externo; balance de referencias entre procesadores; evento y receptor final del catálogo. Siguiente tarea: seguir consumidores de ObjMsg 0x3500/0x3002 y content-info 0x100f, y reconstruir las entradas EXIF del constructor 0x38b064 para una prueba local controlada.

**VERIFICADO:** pruebas estructurales: 3/3 OK con python3 -I. Mypy: sin incidencias en cinco archivos de src. Ruff: nueve avisos en tests preexistentes no modificados (RUF100, SIM115, I001); no se corrigen por estar fuera del alcance. No se añadió código permanente ni avisos en código tocado. Los SHA-256 finales de libObj.so y libmpr.so coinciden con los registrados en el JSON.

Se conservaron solo las dos salidas autorizadas y se eliminó la copia privada de Ghidra. No se editan README/CONTEXT por la restricción expresa de _common.md. No hay commit: este directorio no es un repositorio Git utilizable. No se instalaron herramientas.

**VEREDICTO: CAMBIOS** — evidencia estática entregada; aceptación extremo a extremo pendiente de los bloqueos señalados.

