# ObjStillRecorder "modo 4", 0x1027 y el Pool (sesión 11)

Todo estático. Direcciones: ELF salvo indicación; Ghidra = ELF + 0x10000 en libObj (validado: `0x9163ac` Ghidra = getter en ELF `0x9063ac`). Exports: `analysis/ghidra/libobj-mode4-*.json`, `libobj-isp-*.json`, `libobj-recorder-1027*.json`. Script nuevo: `scripts/thumb_pc_strings.py` (resuelve cadenas PC-relativas Thumb).

## Veredicto
- VERIFICADO: `0x1027` **no entrega ninguna imagen** al grabador. Su manejador (ELF `0x919ca0`) fija `this+0x128=4`, inicializa los punteros del gestor de medios (`this+0xDC`) con `0x91efb0` y responde `0x3500` repitiendo los ítems del ticket. No lee el contenido de `0x131f/0x1320`.
- VERIFICADO: la imagen que graba `RecordStill::Execute` sale del **Pool** (base de contenidos por medio), no del "anillo". El Pool recibe cada imagen mediante `InfraStillPool::RegisterImage`, que a su vez llama a `MakeWriteStillImage`.
- VERIFICADO: `Execute → 0x918afc (RecordStill) → 0x90e0a0 (MprCtrl::WriteStill)` existe en el código, salvo que el modo del gestor de medios (`+0xDC+0x2c`) valga 4, caso en que solo libera (`0x91f8c8`, mensaje `0x6108/0x101b`).
- Clasificación del modo 4 de `+0x128`: **D (variante de la grabación convencional)**, con carácter de ARMADO. Descartado A (grabación de imagen externa): el código no contiene ningún canal para bytes externos en esa rama.

## Correcciones a documentos previos
| Afirmación previa | Estado |
|---|---|
| "+0xDC es un anillo de buffers de imagen" (sesión 10) | DESCARTADO: es `ObjStillRecorderMediaMgr` (cadena `ObjStillRecorderMediaMgr.cpp`), con dos *slots* de medio, `+0x2c` = modo de grabación por medios (0..6) |
| "modo 4 = imagen externa" | DESCARTADO. `+0x128` (copiado desde el parámetro `0x1005` en ELF `0x919a7c`) y `+0x128=4` (de `0x1027`) solo cambian dos banderas del bloque de 0xBC B |
| `param[0x1D]=1` solo en modo 0 (enunciado de la sesión) | CORREGIDO por offsets de pila: modo 0 → índice `0x16`; modos 2..6 → índice `0x1D`; `[0]=1` en 0 y 4. INFERENCIA (no contrastado con desensamblado) |
| "el bloque de 0xBC es WriteStillImageParam" | DESCARTADO: en `Execute` solo viaja dentro de la respuesta `0x3500` (clave `_DAT_0091bbbc`). No llega a MPR |
| "0xBC = WriteStillImageParam de MakeWriteStillImage" (sesión 10) | DESCARTADO: ese parámetro real mide ~0x30 B (dos fechas de 10 B, indicadores+punteros a descriptores `0x3009`/`0x1007`, área `+0x24..0x2e`) y lo arma `0x940c34` |

## Mapa de la ruta real (con evidencia)
1. Captura (LIRO/ISP) → `ImageMgr::PreRegisterImage` (ELF `0x931e14`, cadena `ImageMgr.cpp`) guarda la imagen con `captureId`. NO VERIFICADO quién la llama.
2. `ObjStillRecorder::Execute` (ELF `0x90b248`) arma el mensaje `ObjMsg(0x2008,0x1000)` con ítems `0x1000` (id), `0x1001`/`0x1002` (fechas 10 B), `0x1006` (0x88 B), `0x1007` (0x90 B), `0x100b` (0xB0 B), `0x100e`, `0x1012` y lo envía por `0x922b4c` a la cola del Pool del medio.
3. `InfraStillPool::RegisterImage` (ELF `0x9328b4`): `0x940c34` parsea el mensaje, `0x940508` construye la imagen del Pool (anida un `ObjMsg 0x3002` con tipo `0x100e`, tabla de handles DMM `u16` en `0x100b/0x100c/0x100d` y área `0x300a`), `0x93e9d0` (`MakeStillInfo`) rellena la `StillInfo` (0x6B0) y `0x94b8e0` llama a `MprIf::MakeWriteStillImage`. Responde `0x1003` = `uniqueId`.
4. `Execute` pide la `StillInfo` con `0x91f698 → 0x92bb58`, es decir `ObjMsg(0x6108,0x1009)` al Pool (reply: `0x3002` id, `0x3005` StillInfo 0x6B0, `0x300a` área, `0x4004` nombre `DSC0NNNN.JPG`). `ELF 0x9314ec` genera la respuesta; el número de archivo sale de `image+0xF2`.
5. `0x918afc`: `0x90dc04/0x90dc70/0x90dcdc` (parámetros de MprCtrl: `0x1007`, `0x1006`, nombre) y `0x90e0a0(MprCtrl, WriteStillParam 0x40, StillInfo, resultado 0x48, 1)`.
6. Posterior: `0x920f28`, `0x9205cc`, `0x90ef48` (confirmación `0x1045`), mensaje `0x3500/0x3002` con `0x1001` = código de resultado y `0x100f` = estado del gestor.
7. `InfraStillPool::SetImageWrited` (ELF `0x932a44`) existe; quién lo invoca y con qué condición NO VERIFICADO.

## Respuestas
1. Modo 4: armado del grabador; sin carga de imagen. VERIFICADO (D).
2. Ticket `0x131f/0x1320`: claves del mensaje `0x1027` (u32 de ObjScalar `+0x5c` y búfer de área construido por `0x3fed34` desde `+0x58`). El grabador solo los devuelve en `0x3500` (claves `0x1000000b`/`0x10000006`). Semántica final NO VERIFICADO. (Los valores `0x131e..0x1320` en ObjCamera ELF `0xae0b00` son otro uso, ids de parámetro, sin relación demostrada.)
3. Quién introduce imágenes: el Pool, vía RegisterImage/PreRegister; no el gestor `+0xDC`. VERIFICADO.
4. Formato: componentes ya codificados referenciados por handles DMM `u16` (JPEG, miniatura, etc.) + StillInfo. INFERENCIA (por `MakeJpgInfoArea`, `AddHandle(short)`).
5. `MprCtrl::WriteStill`: alcanzado desde `Execute` en el código. VERIFICADO estáticamente; no para una imagen no producida por el pipeline.
6. DCFStillWriter: NO re-verificado en esta sesión.
7. Metadatos: dos fechas, descriptores `0x1006`/`0x1007`/`0x3009`, tipo (`0x100e`), tabla de handles. Miniatura/screennail/EXIF las ensambla `MakeWriteStillImage` en RegisterImage; quién las produce aguas arriba NO VERIFICADO.
8. JPEG de SFRA: HIPÓTESIS. Los handles DMM `u16` coinciden con los de SFRA, pero faltan miniatura/EXIF y el layout exacto de `0x100b`.
9. Señales de grabación: código de resultado de `RecordStill` en `0x3500/0x3002 item 0x1001`; `SetImageWrited`; `0x1045`. Completitud en SD NO VERIFICADO.
10. Arquitectura: ver apéndices. La más prometedora es "C′": registrar un ítem en el Pool (`RegisterImage`) y disparar el `Execute` nativo; A sigue siendo la referencia.

## NO VERIFICADO / bloqueos
- Layout de los 0xB0 B de `0x100b` y semántica de cada handle.
- Remitente de `PreRegisterImage` y de `0x2008/0x1000` hacia el Pool distinto de `Execute`.
- Qué comando invoca `Execute` fuera de `SeqStillCap` y qué parámetros exige (`0x1017/0x1031/0x1041`, `0x1012`).
- Qué establece `+0xDC+0x4c/+0x2c` (modo de grabación por medios) y su valor en una disparo normal.
- Efecto real de `+0x128` más allá de las dos banderas.

## Corrección sesión 12 (supera partes de las secciones anteriores)
- El «modo 4» de `MediaMgr+0x2C` es `mediaSelectMode = None` (ver `objstillrecorder-mediamgr.md`); no es un modo de imagen externa ni equivale a `this+0x128=4`.
- `0x100b` NO son «componentes existentes entregados por el productor»: son áreas de salida que `Execute` reserva y `MprIf::EncodeStill` rellena a partir de un YC (ver `analysis/objstillpool-100b-layout.json`).
- Línea de «`0x6108/0x1009` pide StillInfo» → es `SetImageWrited` (ver `pool-write-completion.md`).
- Direcciones del enunciado `0x940C34/0x940508/0x93E9D0/0x94B8E0` son VA Ghidra; en ELF son `0x930C34/0x930508/0x92E9D0/0x93B8E0`.
