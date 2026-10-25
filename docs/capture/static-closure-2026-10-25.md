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

## 9. Seguimiento de los límites 1–5 (25-10-2026)

Código y datos: `analysis/s402_static_closure/followup_blocks.py` → `followup_blocks.json` (prueba
`test_followup_settings_block_and_message_emitter`). Solo bytes originales y Capstone.

- **`S[0]` ≡ G en A7S, evidencia más fuerte (sigue sin ser la asignación):** el mismo bloque G (`0x43ea1d84`) recibe por
  los manejadores LIRO contiguos las escrituras `+0x250` (`0x437a9cb8`), `+0x56c` (`0x437aada2`) y `+0x570`
  (`0x437aadba`), y los tres desplazamientos se leen por doble indirección `ldr r3,[S]; ldr rN,[r3,#off]` (`+0x250`:
  `0x43813e90`; `+0x56c`: `0x4354eb30`; `+0x570`: `0x4354eb48`). Tres desplazamientos coincidentes escritor/lector hacen
  muy improbable una coincidencia, pero la escritura `S[0]=&G` no aparece: `S` es el objeto `0x43ea70a0` (getter
  `0x437b38ec`) y ninguna de las cuatro anclas PIC directas de `S` guarda en `[S+0]`.
- **Consumidor del byte A6000 `+0x238`: no encontrado.** Tres métodos sobre `av-cam.bin` A6000: (1) ancla PIC exacta de
  `0x43edf684` con `+0x238`: solo el escritor `0x438032dc`; (2) anclas hasta 0x700 B antes de `+0x238`: ninguna; (3)
  doble indirección `+0x238`: `0x43abb770` es una llamada virtual (`blx` de slot de vtable, no un dato) y `0x4370e994`
  lee `ldrb [p+0x238]` de otro bloque (puntero global `0x43e86414`, fijado vía `0x43716f18`/`0x4370ff8c` desde el global `0x43e85214`; lee
  bytes separados `+0x238/+0x239/+0x241`; no se demuestra relación con G). Con
  A7S el lector existe (`0x43813e90`); en A6000 el ajuste se guarda y nadie lo lee en `av-cam`.
- **Emisor del mensaje `ObjMsg(0x3a49, 0x3026)`:** una sola construcción en `libObj` A6000, `0x659cb0` (`0x659cdc`), con
  parámetro `0x2001` = valor de `r4`. La llama el manejador de mensajes `0x65b0bc` (llamadas `0x65b1fe`, `0x65b270`;
  entrada por salto desde `0x65bc40`) al recibir el evento `0x109` (directo) o `4` (tras condiciones). El mismo manejador
  consume `0x35001004`, `0x35003002` y `0x3a494026`. Los otros sitios con la constante son lecturas de parámetro
  (`0x6ce880`/`0x40b8e0` con id `0x3026`, en `0x7867c6`, `0x7a901a`, `0x424544`), `AddParam(0x3026)` en `0x8afd3a`, el
  registro de fábrica `0x3a9b80` y un `case` en `0x19e076`: ninguno emite. El id `0x3026` sí pertenece a `SequenceRecordStillImageCmd` (ver abajo); **no se probó** en ejecución que este mensaje
  la inicie. Es el único productor con ese id.
- **Modos `+8` de la cola `0x40193` (estructura, sin semántica):** el manejador `0x4379e47c` sustituye el modo por `0x15` si
  coincide con el byte global `+0xd2`, lo registra (`0x43901a8c`) y lo pasa como campo `+0x10` a `0x4379d838`. Allí el
  tipo 3/4 (`0x4379dbd0`) lo trata como **índice** (comparaciones con `0x10`, `0x2`, `0x13`) y `0x43aea210(obj, i, v)` guarda
  `obj[0x20+i]=v`: una tabla de bytes de estado por modo. Los códigos `4/5/6/0xa/0xb/0xc/0x14/0x15` son índices de esa
  tabla, no valores de registro; su nombre/efecto sigue sin observarse. Segunda pasada: los llamadores de los ocho envoltorios
  son métodos de `CExecSeq` y `CEventDispatcher`, y las únicas cadenas de esas funciones son `smile_seq.cpp` y `matrix_02_02`
  (secuencia de detección, no la ruta del obturador).
- **`params[+9]` de `SetExposure`:** `0x436d6f6c` (entrada de vtable `0x43fcc0b8`, slot `+0x2c`). El slot `+0x2c` lo
  comparten más de cien llamadas virtuales de otras clases y en los siete llamadores con estructura en pila
  (`0x43564608`, `0x4358ff04`, `0x435906c2`, `0x4361017e`, `0x436963d4`, `0x438228cc`, `0x439b1a6a`) no hay `strb` directo a
  `[sp,#N+9]`; el origen de ese byte exige resolver el tipo del objeto receptor. Un segundo barrido (escritores `strb [x,#9]` junto a
  `strh [x,#4]`/`[x,#6]` con una llamada al slot `+0x2c` a menos de 120 instrucciones) dio 10 candidatos, todos falsos
  (empaquetado para otros drivers `0x43b7a…`/`0x43b6…`). `SetExposure` lee `[r1]`, `[r1+4]`, `[r1+6]` (u16) y `[r1+9]` (u8, 5
  casos 0–4). Origen sigue sin cerrar.
  - Segunda pasada: dos de los siete llamadores (`0x4358ff04`, `0x435906c2`) rellenan un búfer de `0x50` bytes puesto a cero
    con el slot `+0x1c` del propio objeto (`r1=0`, `r2=búfer`) y lo pasan al slot `+0x2c`; el slot `+0x1c` del IMX210
    (`0x436d6ca0`) es una rutina de pines, no un getter, así que esos dos llamadores son de otra clase. `0x4361017e` usa otra
    convención (`r1=sp+0xa4`, `r2=sp+0xa0`). Sin el tipo del receptor (dato de ejecución) el origen de `params[+9]` no es
    determinable estáticamente.
- **Acción 6 de `ModelPbCap` y acción 13 de `ModelScalarPb` (cadena completa, 25-10-2026):**
  - El id `0x3026` de la factoría `0x3a9a80` (`movw r1,#0x3026` en `0x3a9b80`) se registra con el creador `0x3a7978`
    (`new 0x6c`; constructor `0x3d3130`, base `SequenceBase`), cuyo typeinfo es
    **`OBJSCALAR::SequenceRecordStillImageCmd`**. El id `0x3026` está, por tanto, ligado a esa secuencia por bytes.
  - `0x65bc7c` es el `UFsm::Action(idx)` (slot 17, `+0x44`) de `ModelScalarPb` (typeinfo `13ModelScalarPb`, vtable
    `0x1013140`): `tbh` de 20 casos; el índice **13** salta a `0x65bc38` → `0x65b0bc` → emisor `0x659cb0`.
  - La transición (slot 16, `0x65b9cc`) fija la acción 13 solo en el **estado 4**, con los eventos locales `4` y
    `0x109` o los mensajes `0x35001004`, `0x35003002` y `0x3a494026` (los tres están en el filtro de eventos de
    `ModelScalarPb`, `0x65b898`). Nadie llama al slot `+0x14` de `ModelScalarPb` con `r1=13`: la acción solo sale de esta
    tabla.
  - En `ModelPbCap`, la acción 6 es la acción de **entrada del estado 5** (tabla `tbb` de `0x613170`), y ese estado se
    alcanza desde el **estado 2** con el evento local `2` si la guardia `0x61320c` es verdadera (`0x61343a`). La guardia
    consulta `ObjMsg(0x3500,0x2001)` por `IssueCommandSync` y lee el parámetro `0x1000`.
  - Los eventos locales (`2`, `4`, `0x109`) son enteros pequeños que `0x131fd2` obtiene del id de evento tras el filtro.
- **Quién publica los eventos locales (REA + Capstone, 25-10-2026, segunda pasada):** REA (Ghidra 12.1.4, base `+0x10000`,
  sha256 `8e8a937a…`) se reabrió sobre `libObj.so` A6000 y respondió en segundos. `0x131fd2` solo convierte: si
  `id & ~0xfff == 0x12000000 + (modelo<<12)` devuelve `id - base` (modelo = `this+0x18`, `0x11cf18`), así que un local es
  `0x12000000 + modelo<<12 + local`, construido por `0x120168` (`r0`=base, `r1`=modelo, `r2`=local). Los envoltorios
  (`0x420630`/`0x420656`, `0x132230`, `0x131eb0`, `0x131f28`/`0x131f76`) publican siempre al modelo de su propio `this`.
  - **`0x109` lo publica el propio `ModelScalarPb`:** el método `0x65a8a4` (llamado en `0x65b1f2` desde el manejador
    `0x65b0bc` al procesar el evento `4`, rama con `0x65a892` verdadera) publica `0x10a` y después `0x109` con carga
    `{r6, 0xb4, 0}` (`0x65a95e`). Con `0x109` el manejador llega a `0x659cb0` (emisor de `ObjMsg(0x3a49,0x3026)`, `0x65b270`);
    con `4` y `0x65a892` falsa llega a `0x659cb0` directamente (`0x65b1fe`). Los demás locales de Pb son `1` (init), `0x101`–`0x104`,
    `0x106` (`0x65bf58`) y `0x10a`; `4` y `2` no los publica ningún método de `ModelScalarPb`.
  - **`ModelPbCap`:** sus métodos solo publican `1`, `7` y `9` (`0x613e3c`, `0x613718`, `0x6135dc`); el local `2` no sale de la
    clase. El único método con local `2` cercano (`0x611ec4`, acción 1 de la clase con vtable `0x10123b4`) publica a su propio
    modelo, no a PbCap.
  - **Mensajes:** las únicas construcciones `ObjMsg(cat,id)` de `0x35001004`, `0x35003002` y `0x3a494026` son consultas dentro del
    propio manejador (`0x65a56c`, `0x65a204`, `0x659de4`) y de `0x65df04`/`0x611748`; los tres valores de 32 bits solo figuran
    en receptores de `libObj` y no aparecen en ningún otro de los 320 ELF del firmware ni en `av-cam.bin`.
  - **Cerrado como no determinable estáticamente:** quién publica el local `4` a `ModelScalarPb` y el `2` a `ModelPbCap`, y quién
    envía esos tres mensajes. Quedan solo emisores cruzados con el modelo destino en registro (`0x4ae6ac`, `0x50fb42`,
    `0x5e2f20`, `0x699ba4` para `2`; `0x5a760c`, `0x5a7c54`, `0x621440`, `0x6b2690` para `4`); el número de modelo de cada clase lo
    asigna el gestor que las carga por nombre (`Model*ToInstance` solo figura en `.dynsym`), es dato de ejecución.
- **REA/`libObj.so`:** reabierto en la segunda pasada (ver arriba). **Triaje:** las seis candidatas nuevas de S402 siguen
  `VIGENTE` sin cierre; la revisión manual exige el protocolo con hashes de `manual_review.json` (no se improvisó).

## Límites que permanecen (no son pendientes estáticos nuevos)

- Quién publica el local `4` a `ModelScalarPb` y el `2` a `ModelPbCap` (el `0x109` es auto-envío probado) y quién envía los
  tres mensajes: el modelo destino de los emisores cruzados es dato de ejecución; si `(0x3a49, 0x3026)` crea la secuencia, el
  id → clase está probado por bytes y el envío efectivo no.
- Nombre y efecto de cada índice de modo `+8` de la cola `0x40193` (solo se probó que es un índice de tabla de estado).
- Escritura `S[0]=&G` en A7S (evidencia estructural reforzada, no asignación) y lector del byte A6000 `+0x238` (no existe en `av-cam`).
- Origen de `params[+9]` en `SetExposure` y significado eléctrico de los bits de modo (sin hojas de datos).
- Revisión manual de las filas `VIGENTE` nuevas del triaje: el protocolo fija `revision_destinos`; los documentos de S402 no
  existen en esa revisión, así que cerrarlas exige una nueva campaña de auditoría, no un cambio local.
- REA sobre `libObj.so`: reabierto el 25-10-2026 (consultas en segundos); las conclusiones se verificaron con Capstone sobre los
  bytes originales. Código: `local_posts_in` y `message_constructors` en `followup_blocks.py`.
- Acción real de Darwin sobre las bobinas; todo lo físico. P1–P21 y S51 A/B/C=NO sin cambios.
