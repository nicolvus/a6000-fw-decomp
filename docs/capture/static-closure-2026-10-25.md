# Cierre estático S402 — ocho pendientes de ingeniería inversa (25-10-2026)

Análisis estático con Capstone, bytes originales y REA (sesiones Ghidra únicas, cerradas al terminar). **Sin firmware
ejecutado, sin cámara, sin flasheo.** Direcciones de `libObj.so` = VA del ELF (sin sesgo REA `+0x10000`); `av-cam` base
`0x43541000`. Entregables en [`analysis/s402_static_closure/`](../../analysis/s402_static_closure/) y
[`tests/test_s402_static_closure.py`](../../tests/test_s402_static_closure.py). «Cerrado» significa: lo que el código
permite decidir está decidido y el resto queda como límite explícito, no como pendiente vago.

## Resumen

| # | Pendiente | Resultado |
|---|---|---|
| 1 | Productor de `0x10000005` | Hay **dos** constructores `ObjMsg(0x3500,0x10000005)`: `0x919f4a` (al recibir `PlayData 0x1003`) y `0x90868a` (al despachar `0x1000000f`, que nace de `ObjScalar::SequenceRecordStillImageCmd`, secuencia `0x3026`). Ninguno es un envío externo. Disparo de UI PbCap: acción 6 de `ModelPbCap` → `0x3001`. |
| 2 | Cuerpos locales de RecordStill | **Equivalentes** A6000↔A7S: 25 pares (RecordStill) y 174 (RecordImage), solo cambian números de línea de logs. |
| 3 | Cola `0x40193` | Ocho wrappers envían cuatro comandos (`0x4042–0x4045`) con 53 llamadores en 32 métodos de `CEventDispatcher`/`CExecSeq`; manejadores LIRO identificados. |
| 4 | Backup `0x3000b` | 256 B; defaults idénticos en las 11 imágenes; gates `+3`/`+6` = 0; `+0xac` = 0 (por tanto el reader S176 aplica el default 6). |
| 5 | A7S CAIF | Origen completo: UI `SequenceSetSilentShutterMode` → LIRO **`0x40e3`** → bloque de ajustes `+0x250` → `0x4379ec04` → `root+0x78c` → bit `0x20`. Entrega A6000≡A7S (22 B, evento `0x122`). **Corrige S401 (dif. 1).** |
| 6 | Enlaces IMX210/YC/archivo/cortina | Ver §6. |
| 7 | S206/S207/S301 | Correspondencia funcional por ranura de vtable (§7). |
| 8 | REA de `libObj.so` | Ver §8. |

## 1. Productor de `0x10000005`

- Fila de estado `0x101f11c`: `{2, 0x10000005, check 0x907ba1, call 0x90d7e9, next 0x907c95, 1}` (verificada).
- **Ruta A (S13/S14, verificada de nuevo):** el manejador `0x919ca0` recibe `0x1003` (`PlayData`) por el pin YC y crea
  `ObjMsg(0x3500, 0x10000005){0x10000006 = mensaje recibido}` en `0x919f46..0x919f50`.
- **Ruta B (nueva):** el mismo manejador, ante `0x1027` (`ObjScalar::SequenceRecordStillImageCmd::Begin`, `0x3d2ef8`),
  responde `0x1000000f`; el despachador `0x9162d0` (tabla `tbb` en `0x91631a`) lo envía a `0x908500`, que construye
  otro `ObjMsg(0x3500, 0x10000005)` en `0x90868a` con el `PlayData` anidado (`0x10000006`). La secuencia se registra en
  la factoría `0x3a9a80` con id **`0x3026`** (`movw r1,#0x3026` en `0x3a9b80`).
- Corrige la lectura «no hay remitente externo y solo PbCap» de S13: la ruta B existe en el mismo recorder. No se
  trazó quién emite el comando de secuencia `0x3026` (siete sitios con la constante: `0x19e076`, `0x424544`, `0x659cdc`,
  `0x7867c6`, `0x7a901a`, `0x8afd3a` y el registro `0x3a9b80`); queda como límite.
- Disparo PbCap: `UFsm::Action` de `ModelPbCap` (`0x61414c`, vtable `0x101242c`), índice 6 → `0x6137b0` →
  `ObjMsg(0x3500,0x3001){0x1005=0}` + `IssueCommandAsync`; el índice 2 crea la topología `0x2a`.

## 2. RecordStill y RecordImage A6000↔A7S

Motor: descenso recursivo desde la entrada (solo instrucciones alcanzables), normalización de llamadas por nombre,
cadenas PIC por texto, punteros GOT por símbolo/sección, y emparejado de destinos locales por posición.

- `RecordStill` `0x908afc`↔`0x847e1c`: 260/260 instrucciones, **25 pares**, 24 idénticos y 1 distinto solo en `movw rN,#línea`.
- `RecordImage/Execute` `0x90b248`↔`0x84a568`: 1112/1112, **174 pares**, 169 idénticos y 5 distintos solo en líneas.
- Las ocho parejas locales candidatas quedan **equivalentes** (incluida `0x915f04`↔`0x84e824`, el registrador de errores).
- Límites: llamadas indirectas (`blx reg`, vtables) y bloques de limpieza de excepciones no se comparan.

## 3. Cola `0x40193`

Los ocho wrappers (`0xaf9264, 0xaf92d8, 0xaf934c, 0xaf93bc, 0xaf9c88, 0xaf9ce8, 0xaf9d48, 0xaf9da8`) construyen un
mensaje de 16 B con comando en `+2/+3` y código de modo en `+8` (evaluador mínimo, no emulación):

| Wrapper | Comando | Modo `+8` (arg 0/1/2) | Manejador LIRO |
|---|---|---|---|
| `0xaf9264`, `0xaf9c88` | `0x4042` | `0xc/0xb/0x14`; `0xa` | `0x4379e47c` |
| `0xaf92d8`, `0xaf9d48` | `0x4043` | `0xc/0xb/0x14`; `0xa` | `0x4379e3fc` |
| `0xaf934c`, `0xaf9ce8` | `0x4044` | `0x6/0x5/0xa`; `0x4` | `0x43aeaa4a` |
| `0xaf93bc`, `0xaf9da8` | `0x4045` | `0x6/0x5/0xa`; `0x4` | `0x43aea9f0` |

53 sitios de llamada en 32 métodos; 31 pertenecen a vtables de `CExecSeq` (19) y `CEventDispatcher` (12). Los
manejadores LIRO clasifican la cola de respuesta (`0x4379d2ec`: `0x1502c7`/`0x40193`→1, `0x20002`→2,
`0x260185/6`→3, otras→4) y llevan contadores de serie por clase (`this+0xc80`/`+0xc84`, `0x4379d328`). La semántica de
cada código de modo y la recepción en ejecución siguen sin observarse.

## 4. Backup `0x3000b`

Formato (de `backup.ko`, verificado por palabras y relocaciones): cabecera `+0x10` = nº de grupos (403), tabla de
grupos en `+0x100` (6 B `{max u16, base u32}`), registros de 6 B; el byte alto del desplazamiento es el tamaño en línea
o `0xff` (u16 de tamaño antes de los datos). El núcleo de lectura llama `Data_SearchId`, `Data_GetSize`, `Data_GetDataPt`.

- Las 11 imágenes `CX775xx_*.bin` del paquete dan el **mismo** payload de **256 B**: `1` en `+0x30..+0x37`, `+0x41`
  y `+0x51`; el resto `0`. Destino `0x43f72d02` (stride `0x100`, las claves vecinas `0x43f72c02`/`0x43f72e02`).
- Gates `+3` (`0x43f72d05`) y `+6` (`0x43f72d08`): **0 por defecto**. `+0xac` = 0 ⇒ el primer lector S176 sustituye por 6.
- Límite: valores ajustados de fábrica o de uso de una cámara concreta no están en el paquete.

## 5. A7S CAIF: origen y entrega

1. UI: `CamUser::SequenceSetSilentShutterMode` (`libObj` A7S `0x93a078`) construye un comando LIRO de 9 B con id
   **`0x40e3`** (`movw r0,#0x40e3` en `0x93a0bc`) y lo envía (`0x881c34`, `osal_valloc_msg_wait`).
2. LIRO A7S **sí tiene** el manejador: fila `0x43ff79e4` `{0x40e3, 0, 0x437a9cb1}` → `0x437a9cb0` guarda el byte `+8`
   en `0x43ea1d84+0x250` (bloque de ajustes G, puesto a 0 por `0x437aae44`).
3. `0x43813d90` calcula `root+0x78c = F(*(*S+0x250), root)` con `F=0x4379ec04`: tabla `{0→0, 1→2}`; un byte de
   depuración `0x43ea3182` fuerza 2 (`"SET Silent Shutter Type: %d"`). Si es 2, `root+0x748=1`.
4. `0x43862e24`: `payload[0x12] = 0x20·(C+0x76c==2) + (flag==1)` y `payload[0x0d]` fuerza 2 con Silent.
5. Entrega: `0x4379b5f2` copia 22 B (`captura+0x40`) con `0x436d8354` → `0x43acade8` (evento `0x122`); es el mismo
   código que en A6000 (`0x437db8da` → `0x436b8a50` → `0x43acabac`).

**Corrección a S401, diferencia 1:** la tabla de despacho de A7S tiene `0x40e3`; S401 la buscó en la VA de A6000. Tampoco
es cierto que A7S no reciba el comando: `SequenceSetSilentShutterMode` existe en ambos `libObj` (A6000 `0x978e0c`,
mismo flujo salvo un `printf` de error y el offset `0xc70/0xcd0`) y el manejador A6000 `0x438032d4` guarda el mismo
byte en `+0x238` del bloque `0x43edf684`. La diferencia real está en el consumidor (A7S lo lee y construye el bit `0x20`).

Límite: no se demostró la escritura `S[0]=&G`; la identidad `G`≡`*S` es evidencia estructural (mismas posiciones `+0x250`,
`+0x580` en el mismo clúster), no una asignación observada.

## 6. Enlaces IMX210 / YC / archivo / cortina

Cadena estática verificada con evidencia de hoy y de informes previos (S12–S14, S53–S54, S171):

| Arista | Estado | Evidencia |
|---|---|---|
| UI `SequenceSetSilentShutterMode` → LIRO `0x40e3` | VERIFICADO en A6000 y A7S | `movw r0,#0x40e3`: A6000 `0x978e50`, A7S `0x93a0bc`; flujo idéntico salvo un `printf` y un offset |
| LIRO `0x40e3` → bloque de ajustes | VERIFICADO | A6000 `0x438032d4` → `0x43edf684+0x238`; A7S `0x437a9cb0` → `0x43ea1d84+0x250` |
| Ajuste → bit `0x20` del paquete CAIF | VERIFICADO solo A7S | `0x4379ec04` → `root+0x78c` → `payload[0x12]`; el constructor A6000 `0x43841070` no lo lee |
| Paquete CAIF → destino (22 B, evento `0x122`) | VERIFICADO, igual en ambos | A7S `0x4379b5f2`, A6000 `0x437db8da` |
| Paquete → bobinas de cortina (Darwin) | NO_VERIFICADO aquí | MCU fuera de `av-cam`; ver S53/S54 (`no_silent`) |
| Driver IMX210/IMX235 → registros de obturación | VERIFICADO el despacho | `SetExposure` conmuta `params[+9]` (modos 0–4) en ambos drivers (§7) |
| Productor YC → recorder | VERIFICADO | S14: ObjEffect salida 1 → `ObjStillRecorder` entrada YC (`0x2a`) |
| Recorder → archivo | VERIFICADO | `Execute` → `EncodeStill` → Pool → `RecordStill` → `WriteStill`; cierre A6000≡A7S (§2) |
| Quién fija `params[+9]` y su relación con Silent | NO_VERIFICADO | no se trazó el llamador de `SetExposure` |

Lo no verificable estáticamente: significado eléctrico de los bits de modo (sin hoja de datos en el repositorio) y la
acción real de Darwin sobre las bobinas.

## 7. S206 / S207 / S301: correspondencia funcional

[`imager_vtable_correspondence.json`](../../analysis/s402_static_closure/imager_vtable_correspondence.json) empareja las 34
ranuras de la vtable de `C_ImagerCtrl_IMX210` (`0x43fcc08c`) y `C_ImagerCtrl_IMX235` (`0x43fce04c`) y nombra el rol de cada
una por sus cadenas de depuración: `PowerOn`/`PowerOff` (6/7), `SetMode` (8), `GetParam` (9), `SetExposure` (10),
`SetExposureZ` (11, solo implementada en A6000), `SetRead` (12), `SetReadZ` (13), `Execute` (14–15), `Execute_sleep` (17),
`AsyncInitial` (23), `SyncInitial` (24). Solo 8 ranuras son idénticas (1, 20, 26–28, 31–33: stubs/bases); el resto difiere
(A7S 718 instrucciones en `SetRead` frente a 182; `SetExposure` 200 frente a 467).

- **S206:** correspondencia **por rol** establecida (tabla anterior); por dirección sigue siendo «distinto» y no hay
  equivalencia eléctrica demostrable sin hojas de datos.
- **S207 (fin de integración):** ambos drivers conmutan el modo de obturación `params[+9]` (`imager_shutter_modes.json`):
  A6000 tiene cuerpo para los cinco valores (0–4; el 2 fija los bits `0x04|0x80|0x10` y borra `0x40` en el registro
  sombra `+2`), A7S solo para 0, 1, 3 y 4 (el 2 lleva a `"ShutMode:%d is not supported."`). A7S además registra
  `SetExposure:SHR` y `SetRead … MCov/imgVolt/ReadExec`. Esto **no** demuestra un mecanismo de fin de integración
  electrónico en A6000 ni su ausencia: solo que el driver IMX210 ya distingue modos de obturación.
- **S301:** el volcador de estado de A7S `0x437e0974` y el de A6000 `0x43858338` son estructuralmente idénticos
  (1599/1599 instrucciones; solo difieren offsets GOT), de modo que las diferencias de S301 están en los lectores, no
  en el volcador.

## 8. REA sobre `libObj.so`

Se abrieron tres sesiones únicas con `session_daemon.py`: `av-cam` A7S (listo a los 852 s), `av-cam` A6000 (823 s) y
`libObj.so` A6000 (900 s, `provider_id=ghidra`, ELF autodetectado). Resultado:

- `av-cam` A7S/A6000: consultas `xrefs` y `procedure_pseudo_code` operativas; confirmaron los llamadores de `0x4379ec04`
  (`0x437b6f74`, `0x43813e94`), el constructor CAIF A7S (offsets `0x76c`/`0x12`/`0x0d`) y que el constructor A6000
  `0x43841070` no lee ningún selector Silent.
- `libObj.so`: la apertura **no falla** (la sesión llegó a «lista»), pero la primera consulta
  (`resolve_containing_procedure`) superó los **1700 s** del cliente sin responder. Es la limitación ya registrada
  (consultas de 300 s en S178/S380) y confirma que no hace falta intervención humana: el trabajo sobre `libObj.so` se
  hizo con Capstone/LLVM sobre los bytes originales, con el índice de inicios por `.ARM.exidx`, PLT por relocaciones y
  resolución de RTTI/vtables (`analysis/s402_static_closure/fw.py`). Esa ruta reproducible sustituye a REA aquí; una
  consulta vacía o sin respuesta de REA no prueba ausencia.
- Sesiones cerradas al terminar; el log compartido de REA no se versiona.

## Límites que permanecen (no son pendientes estáticos nuevos)

- Quién emite la secuencia `0x3026` y el evento de UI de PbCap que dispara la acción 6.
- Significado de los códigos de modo `+8` de la cola `0x40193` y recepción en ejecución.
- Escritura `S[0]=&G` en A7S (identidad de los bloques de ajustes) y consumidor del byte A6000 `+0x238`.
- Llamador que fija `params[+9]` en `SetExposure` y significado eléctrico de los bits de modo (sin hojas de datos).
- Acción real de Darwin sobre las bobinas; todo lo físico. P1–P21 y S51 A/B/C=NO sin cambios.
