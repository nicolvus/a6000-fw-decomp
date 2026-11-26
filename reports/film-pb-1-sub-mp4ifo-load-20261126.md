# FILM-PB-1 / sub-mp4ifo-load — las líneas 1749 y 1340 de `IF/mp4Ifo_General.cpp` y el código `0xB0800001`

26-11-2026 · Binario: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(fw 3.21, 10 321 204 B, SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`).

**VA = VA del ELF (base 0)**, y en este ELF coinciden con el offset de fichero en el primer LOAD.
Secciones (comprobadas, evidencia `10-verificacion-va.txt`): `.text` `0x00120228-0x007A3E84`,
`.rodata` `0x007A3E90-0x00956750`, `.data` `0x009C42E8-0x009DF808`, `.bss` `0x009DF808-0x00ADBB04`.
Fichero `0x9D7D34` B. **Todas** las VA que se citan aquí caen dentro de una de esas secciones.

Estático, sin cámara y sin ejecutar firmware. Desensamblador: `python3 /tmp/thumbdump.py` (capstone Thumb-2,
salta bytes inválidos para no desincronizarse). Evidencia cruda:
[reports/evidence/film-pb-1-sub-mp4ifo-load-20261126/](evidence/film-pb-1-sub-mp4ifo-load-20261126/).

---

## 0. Resumen (≤20 líneas)

1. Las dos líneas **no son dos fallos**: `1749` la emite `mp4Ifo_General::FlashLoadForMsv` (`0x698EC8`) y `1340`
   la emite `mp4Ifo_General::CheckSalvageStatus` (`0x698F18`) al **reimprimir el mismo código** que le devolvió
   la anterior.
2. `1749` = `0x698EE6` (`movw r3,#0x6D5`) con fichero `0x91443D`; `1340` = `0x698F4A` (`movw r1,#0x53C`) con el
   mismo fichero. Son las **únicas** instrucciones de `.text` que casan fichero+línea (barrido analítico de `movw`).
3. El texto lo **compone** el impresor `0x6F0A54(fichero, línea, código)`: `" ### mp4Ifo faild at "` (`0x91C945`) +
   fichero + `"("` (`0x8DD35E`) + `%d` + `") ErrCd: 0x"` (`0x8BBA44`) + `%08X`. No existe un `printf` único con el formato.
4. `1749` es la **única** salida de error de `FlashLoadForMsv`; su código no es fijo: es el que devuelve el traductor
   `mp4libErr::ConvStatusCode` `0x6F0D4C(status, 0xB0800001, fichero, 1749)`.
5. `0xB0800001` **no es un código de fichero**: es el **valor por defecto** del traductor para todo estado que no
   encaja en su tabla. Dos ramas lo producen: `0x6F0E40 → 0x6F0EBC` (estado `0xXX10XXXX`) y `0x6F0E96` (default).
6. En la cámara el estado vale `0x13100001` (medido: `TRACE 6f0d4c r0=13100001 r1=b0800001 r3=6d5`, shim G22);
   sus bits 16-23 son `0x10` → rama `0x6F0E40` → `0xB0800001`.
7. `0x13100001` se descompone: `0x350124(0x10100001, [iface+0x24])` = `0x00100001 | 0x13000000`. La base de módulo
   `[iface+0x24]` es lo que añade el prefijo `0x13` (eslabón que faltaba en los informes previos).
8. `0x10100001` lo devuelve la lectura del pack **RcsTbl** (`0x2B39B8`) cuando la entrada de la tabla `0xA3699C`
   **no tiene rutina de lectura**: `ldr r2,[entrada+4]; cbz r2 → 0x2B3A28 (r0=0x10100001)`.
9. Luego la comprobación concreta es `[0xA3699C + 0x14*idx + 4] != 0` (y `[+0] == clave`). Hoy vale 0 porque la tabla
   es `.bss` y **nadie la registra**; entonces `ReadFirstPackData` (`0x2B3948`) ni se ejecuta.
10. Para pasar: `status` de `0x3AFA94` debe ser **0**; para ello el campo `+4` de la entrada debe ser **!= 0**
    (puntero a rutina) y la lectura debe completar.
11. **No es contenido**: en todo el camino no se abre ni un byte del MP4. El fallo está en la capa MSV/RCS
    (tabla de respaldo del gestor de sectores), antes del IFO y antes del índice AV.
12. **Es estado/plomería**: `0xB0800001` = "el traductor no clasifica el estado"; no dice nada del fichero.
13. Discriminante en el anillo: `[MSV][MS1]Err RcsBackupTblData` (`0x823999`, impreso en `0x3AFB2C`) precede siempre
    a las dos líneas ⇒ rama de E/S (`(código & 0xFF000000) == 0x10`) de `0x3AFA94`.
14. Si el fallo fuera de contenido, `1749` mostraría un código **específico** (`0xB0400005`, `0xB0510001`,
    `0xB0810001`, `0xB0F30001`, `0xB0400001`, `0xB0400006`, `0xB0200001`…) y no habría `Err RcsBackupTblData`.
15. La misma firma aparece en **foto** (`[DCF][MS1]Err RcsBackupTblData`) y en **XAVC** ⇒ capa común, no el MP4.
16. `mb_load` (`this+0x23`) solo se pone a 1 si `Load` devuelve 0; al fallar queda a 0 y por eso
    `CheckSalvageStatus` reintenta y **repite** `1749` + `1340`.
17. Correlato: la línea `0x536` (`0xB0100006`) de la misma función es puro estado ("ya cargado") y **no** sale en el anillo.
18. Corrección: `FlashLoadForMsv` **no** devuelve siempre `0xB0800001`; devuelve el mapeo del estado (tabla §4).
19. Corrección/aviso: el mapeo `(userId,backupId) → índice` no se ha re-verificado aquí; la tabla `0x9D23FC`
    (`0x18` B, clave en `+0/+4`, índice en `+0xC`) merece relectura (§7.3).
20. **NO_VERIFICADO**: quién y cuándo registra las entradas de `0xA3699C`, y el medio físico del pack `RcsTbl`.

---

## 1. Las dos líneas: instrucción, función y formato

### 1.1 Localización exacta

| Línea | Instrucción | Función contenedora | Fichero (VA `.rodata`) | Impresor |
|---|---|---|---|---|
| **1749** (`0x6D5`) | `0x698EE6 movw r3,#0x6d5` | `mp4Ifo_General::FlashLoadForMsv` **`0x698EC8`** | `0x91443D` | `bl 0x6F0D4C` (`0x698EEA`) → `0x6F0A54` |
| **1340** (`0x53C`) | `0x698F4A movw r1,#0x53c` | `mp4Ifo_General::CheckSalvageStatus` **`0x698F18`** | `0x91443D` | `bl 0x6F0A54` (`0x698F54`) |

Barrido analítico de los `movw` de todo `.text` (`/tmp/movwscan.py`): los inmediatos `0x6D5` y `0x53C` aparecen en
18 sitios, pero **solo** `0x698EE6` y `0x698F4A` están en el rango de funciones de `IF/mp4Ifo_General.cpp`
(`0x697xxx-0x699xxx`), que es el único sitio del binario donde se carga el puntero al fichero `0x91443D`
(pools `0x697DB4 … 0x698FA0`). La identificación es única.

### 1.2 El formato se compone en `0x6F0A54` (no es un `printf` único)

`0x6F0A54(fichero = r0, línea = r1, código = r2)`; si `r2 == 0` sale sin imprimir (`0x6F0A62`). Piezas:

| VA | Instrucción | Pieza |
|---|---|---|
| `0x6F0A86` | `ldr r0,=0x91C945` | `" ### mp4Ifo faild at "` |
| `0x6F0A8C` | `mov r0,r6` | `%s` = fichero |
| `0x6F0A92` | `ldr r0,=0x8DD35E` | `"("` |
| `0x6F0A98` | `mov r1,r5 ; movs r0,#4 ; bl 0x695784` | `%d` = línea |
| `0x6F0AA0` | `ldr r0,=0x8BBA44` | `") ErrCd: 0x"` |
| `0x6F0AA6` | `movs r0,#8 ; mov r1,r4 ; b 0x695828` | `%08X` = código |

De ahí que el anillo muestre `### mp4Ifo faild at IF/mp4Ifo_General.cpp(1749) ErrCd: 0xB0800001`
y que la cadena buscada no exista como literal contiguo: está partida en cinco trozos.

### 1.3 Quién llega hasta ahí

```
mp4Ifo_Lib::Load            0x6EC1C4   (log "Load" en mp4Ifo_Lib.cpp:0x67)
  └ mp4Ifo_General::Load    0x698FB8   (device = 0 -> FLASH, 1 -> DISC)
      ├ device != 1 -> FlashLoadForMsv  0x698EC8   <-- emite 1749
      │    └ llamante MSV de RcsBackupTblData  0x3AFA94
      └ device == 1 -> DiscLoadForMsv   0x698E78   (emite 0x6B1 = 1713, no 1749)
```

Y por el otro lado, `mmgr` entra por `CheckSalvageStatus` (`0x698F18`, llamada única desde `0x6EE0D4`), que
**vuelve a llamar** a `FlashLoadForMsv` cuando `[this+0x23] == 0` (`0x698F2E-0x698F32`). De ahí el par
`1749` + `1340` seguido en el anillo.

---

## 2. `mp4Ifo_General::FlashLoadForMsv` — `0x698EC8` (la línea 1749)

Función completa (`0x698EC8-0x698F06`, 22 instrucciones; listado en `02-698ec8-flashloadformsv.txt`):

```
00698ec8  push {r4,r5,r7,lr}
00698ece  bl   0x6955a4                 ; (traza: nivel/filtro)
00698ed2  ldr  r0,=0x914EF2             ; " mp4Ifo_General::FlashLoadForMsv IN ()"
00698ed4  bl   0x6954ec                 ; log INFO
00698ed8  ldr  r0,[r4]                  ; this->[0]   = sub-objeto mp4Ifo_If
00698eda  bl   0x6964e2                 ; -> [sub+8]  = interfaz
00698ede  bl   0x3afa94                 ; *** status = carga (RcsTbl + contFileNo + ...) ***
00698ee2  ldr  r1,=0xb0800001           ; código POR DEFECTO
00698ee4  ldr  r2,=0x91443d             ; "IF/mp4Ifo_General.cpp"
00698ee6  movw r3,#0x6d5                ; 1749
00698eea  bl   0x6f0d4c                 ; err = ConvStatusCode(status, 0xB0800001, file, 1749)
00698eee  mov  r5,r0
00698ef0  cbz  r0,0x698ef8              ; 0 -> sin error
00698ef2  mov  r0,r4
00698ef4  bl   0x697d70                 ; Unload(this) -> deshace (linea 0x89)
00698ef8  ... log OUT
00698f02  mov  r0,r5 ; pop
```

**Condición de fallo: una sola** — `0x3AFA94` devuelve ≠ 0. El código impreso depende del mapeo del traductor
(§4); `0xB0800001` es solo el valor por defecto. No hay ninguna comprobación de fichero, tamaño, caja MP4 ni IFO aquí.

`0x3AFA94` tampoco mira el MP4: su primera acción es `RcsBackupTblData` (`0x35EA1C`), y sus únicos retornos de
error salen por `0x3502CA` (§5-6). Listado: `07-3afa94-ruta.txt`.

---

## 3. `mp4Ifo_General::CheckSalvageStatus` — `0x698F18` (la línea 1340)

```
00698f18  push {r3,r4,r5,r6,r7,lr}       ; r0=this, r1=pbIsNeedSalvage
00698f24  log " ... CheckSalvageStatus IN"
00698f2a  strb r3,[r6]                   ; *pb = 0
00698f2e  ldrb r3,[r5,#0x23]             ; mb_load
00698f32  cbz  r3,0x698f44               ; 0 -> intentar cargar
00698f34  ldr  r0,=0x91443d              ;  fichero
00698f36  movw r1,#0x536                 ;  linea 1334
00698f3a  ldr  r2,=0xb0100006            ; "ya cargado"
00698f3c  bl   0x6f0a54                  ; (A) log 0xB0100006  <- solo estado
00698f40  ldr  r4,=0xb0100006 ; b 0x698f76
00698f44  mov  r0,r5
00698f46  bl   0x698ec8                  ; *** FlashLoadForMsv -> dentro se imprime 1749 ***
00698f4a  movw r1,#0x53c                 ; 1340
00698f4e  mov  r4,r0
00698f50  ldr  r0,=0x91443d
00698f52  mov  r2,r4
00698f54  bl   0x6f0a54                  ; (B) log 1340 con el codigo heredado
00698f58  cbnz r4,0x698f76               ; si error -> salir
00698f5a  mov  r0,r5 ; bl 0x698b3e       ; salvage real -> 0x34EF4C(iface)
00698f60  strb r0,[r6]                   ; *pbIsNeedSalvage = ret
00698f62  mov  r0,r5 ; bl 0x697d70       ; Unload
00698f68  movw r1,#0x547 ; ... bl 0x6f0a54  ; (C) log del resultado de Unload
00698f76  ... log OUT ; return r4
```

Condiciones y códigos de esta función:

| Punto | Condición | Código |
|---|---|---|
| (A) `0x698F3C` | `[this+0x23] (mb_load) != 0` | `0xB0100006` (literal `0x698FA4`) — **no** aparece en el anillo |
| (B) `0x698F54` | siempre que se llama a `FlashLoadForMsv` | el **mismo** código que devolvió: `0xB0800001` en el caso real |
| (C) `0x698F72` | tras `Unload` si la carga fue OK | resultado de `Unload` (`0x697D70`, que usa default `0xB0800001` y linea `0x89` = 137) |

Por eso `1340` **no aporta información nueva**: es el eco de `1749`. En el anillo se ve la pareja y, más tarde,
un `1749` suelto (cuando se entra por `LoadSub → mp4Ifo_Lib::Load` sin pasar por `CheckSalvageStatus`).

---

## 4. `mp4Ifo_General::Load` — `0x698FB8` y el traductor `0x6F0D4C`

`Load(this, device)` (listado `04-698fb8-load.txt`) solo despacha:

```
00698fdc  cmp  r5,#1
00698fde  bne  0x698fe8
00698fe0  bl   0x698e78        ; device == 1 -> DiscLoadForMsv
00698fe8  bl   0x698ec8        ; resto      -> FlashLoadForMsv
00698ff0  cbnz r0,0x698ff8
00698ff2  movs r3,#1 ; strb.w r3,[r4,#0x23]   ; mb_load = 1 SOLO si ret == 0
```

Llamada desde `0x6EC1E6` (`mp4Ifo_Lib::Load`, device del llamante), `0x6EE006` y `0x6EE13A` (device=1, tras `Unload`).

`mp4libErr::ConvStatusCode` `0x6F0D4C(status, def, fichero, línea)` — tabla completa (listado `05-…txt`):

| Instrucción (VA) | Condición sobre `status` | Código final |
|---|---|---|
| `0x6F0D5A` | `== 0` | **0** (no imprime) |
| `0x6F0D62 → 0x6F0EB0` | `== 0x13810001` | `0xB0810001` |
| `0x6F0D6A/72/7A/82 → 0x6F0EB4` | `== 0x1340000E / 02 / 05 / 06 / 07` | `0xB0400005` |
| `0x6F0DAA → 0x6F0E72` | `(status & 0xFF0000) == 0x800000` | `0x1380000A` → `0xB0510001`; resto → **`0xB0800001`** |
| `0x6F0DF0 → 0x6F0E66` | `== 0x400000` | `0xB0400001` |
| `0x6F0E00 → 0x6F0E6A` | `== 0x500000` | `0x13500002` → `0xB0400006`; resto → **`0xB0800001`** |
| `0x6F0E30 → 0x6F0EB0` | `== 0x810000` | `0xB0810001` |
| **`0x6F0E40 → 0x6F0EBC`** | **`== 0x100000` o `== 0xF00000`** | **`0xB0800001`** |
| `0x6F0E18 → 0x6F0E82` | `== 0xF10000` (códigos `0x13F1xxxx`) | tabla `0x91CAD0`, 0x24 entradas (`0x13F10004..0x13F10027`) |
| `0x6F0E52 → 0x6F0EA8` | `== 0xF20000` | **0** (sin error) |
| `0x6F0E62 → 0x6F0E92` | `== 0xF30000` | `0xB0F30001` |
| `0x6F0DC8 → 0x6F0EB8` | `== 0x200000` | `0xB0200001` |
| `0x6F0E02 / 0x6F0E42 / 0x6F0E64 / 0x6F0EBC` | cualquier otro | **`0xB0800001`** |

`0x6F0E96` (`mov r4,ip`) es la rama "código del llamante": devuelve el `def` tal cual (aquí `0xB0800001`).
Todas las ramas acaban en `0x6F0E9A: r0=r6(fichero); r2=r4(código); bl 0x6F0A54`.

Con la tabla en la mano: **`0xB0800001` = "no clasificado"**. Y para `0x13100001`, `0x13100001 & 0xFF0000 = 0x100000`
→ `0x6F0E40` (Z=1) → `0x6F0EBC` → `0xB0800001`.

---

## 5. De `0xB0800001` hacia abajo: quién fabrica el `0x13100001`

### 5.1 `0x3AFA94` — envoltorio de carga (listado `07-…txt`)

```
003afaf6  bl   0x35ea1c            ; status = RcsBackupTblData(...)  ("RcsBackupTblData Start")
003afafa  mov  r6,r0
003afafc  cbz  r0,0x3afb44         ; 0 -> sigue con contFileNo / dirs / vtbl
003afafe  and  r3,r0,#0xff000000
003afb06  cmp.w r3,#0x10000000
003afb0a  beq  0x3afb28            ; top byte 0x10 -> "Err RcsBackupTblData" (0x823999) SIN salvage
003afb0c  ...                      ; otro top byte -> " Need Salvage" (0x8BCC33) y [obj+0x44]=1, r6=0
003afb38  bl   0x3536dc            ; log
...
003afbb8  mov  r0,r4 ; mov r1,r6
003afbbc  bl   0x3502ca            ; return -> 0x350124(codigo, [obj+0x24])
```

- `status == 0` → sigue la carga (dirs, `vtbl[0x78]`, `vtbl[0x60]`).
- `status` con top byte `0x10` → **fatal**, se propaga.
- `status` con otro top byte → salvage (marca y devuelve 0).

### 5.2 `0x3502CA → 0x3502B8 → 0x350124` — el prefijo `0x13` (listado `09-…txt`)

```
003502ca  pop {r7,lr} ; b 0x3502b8
003502b8  mov r3,r0            ; obj
003502ba  mov r0,r1            ; código
003502c0  ldr r1,[r3,#0x24]    ; base de módulo del objeto
003502c6  b   0x350124         ; -> r0 = mapea(código) | base
...
00350240  orrs r0,r1           ; <-- AQUÍ se añade el prefijo
```

`0x350124` mapea `0x10100001`: top byte `0x10` → `0x35023E` → `r0 = 0x00100001`; luego `orrs r0, r1` con
`[obj+0x24]`. Para que el resultado medido sea `0x13100001`, **`[obj+0x24] = 0x13000000`** (inferencia exacta,
no hay otra rama). Es el eslabón que faltaba: `0x10100001` (RCS) → `0x13100001` (mp4Ifo) → `0xB0800001` (log).

### 5.3 `0x10100001`: la tabla `0xA3699C` sin rutina (listado `08-…txt`)

```
002b39da  bl   0x2b2f48         ; idx = GetSectorManagerInfoTableIndexFromUserID(OM, userId, &byte)
002b39e2  muls r1,r2,#0x14      ; entrada = 0x14 * idx
002b39e8  ldr  r0,=0xa3699c
002b39ea  adds r2,r0,r1         ; r2 = &tabla[idx]
002b39ec  ldr  r2,[r2,#4]       ; *** [entrada+4] = rutina de lectura ***
002b39ee  cbz  r2,0x2b3a28      ; si 0 -> ERROR (salta el camino bueno)

  camino bueno (no tomado):                      camino de error (tomado):
002b3a1e  ldr  r3,[r7,#0x30]                    002b3a28  ldr  sb,=0x10100001
002b3a20  bl   0x2b3948  ; ReadFirstPackData    002b3a32  bl   0x2b38b4   ; log "[FBM]<RWB>..."
```

`0xA3699C` está en `.bss` (`0x9DF808-0xADBB04`): nace a ceros. Sin un registro previo,
`[entrada+4] == 0` **siempre**, y toda lectura de pack RcsTbl devuelve `0x10100001`.

Y `0x2B2F48 → 0x2B2DF4` busca el índice en una tabla de `0x18` B por entrada (`0x9D23FC`, clave en `+0/+4`,
índice en `+0xC`, terminador `-1` en `+4`). El índice no es constante: depende de `(OM, userId)`.

### 5.4 Cadena completa del caso real

```
mp4Ifo_General::Load(this,0)
  └ FlashLoadForMsv                                    0x698EC8
      └ 0x3AFA94  (RcsBackupTblData + dirs)            0x3AFA94
          └ RcsBackupTblData                          0x35EA1C
              └ 0x35E04C  ("BKUP RcsTbl Start")        0x35E04C
                  └ 0x2B39B8 (BkRead FirstPack)        0x2B39B8
                      └ [0xA3699C + 0x14*idx + 4] == 0  ->  0x10100001
          └ (top byte 0x10) "Err RcsBackupTblData"     0x3AFB2C
          └ 0x3502CA -> 0x350124: 0x00100001 | 0x13000000 = 0x13100001
      └ ConvStatusCode: 0x13100001 & 0xFF0000 = 0x100000 -> 0xB0800001
      └ log IF/mp4Ifo_General.cpp(1749) ErrCd: 0xB0800001
  └ CheckSalvageStatus 0x698F18: mb_load==0 -> reintenta -> log (1340) del mismo código
```

---

## 6. Qué comprobación produce `0xB0800001` y qué necesita para pasar

**Nivel inmediato (el que imprime).** `0x6F0D4C` no comprueba nada del MP4: **clasifica** un estado.

- Campo: `r0` de entrada (el retorno de `0x3AFA94`).
- Valor para pasar: **`0`**. Cualquier otro valor produce un código; y si cae en `0xXX10XXXX` o no está en la
  tabla, produce exactamente `0xB0800001` (`0x6F0E40 → 0x6F0EBC`, `0x6F0E96`/`0x6F0EBC`).

**Nivel real (lo que hay que arreglar).** `status == 0` exige que `RcsBackupTblData` (`0x35EA1C` → `0x35E04C`)
complete; y eso exige, para el `idx` que toque:

| Campo | Dirección | Valor necesario |
|---|---|---|
| clave de entrada | `[0xA3699C + 0x14*idx + 0x0]` | igual a la clave pedida (si no, `0x2B2F98` no casa) |
| **rutina de lectura** | **`[0xA3699C + 0x14*idx + 0x4]`** | **!= 0** (hoy 0 ⇒ `0x10100001`) |
| tolerancia | — | `0x10100003` ("sin datos") se tolera en `0x35E0FC` y no genera error |

Es decir: el valor que falta no es un dato del MP4, es **un puntero a función** que alguien debe registrar en la
tabla de respaldo del gestor de sectores. `0x10100001` es literalmente "esa entrada no tiene lector".

---

## 7. ¿Contenido o estado? Cómo se distingue

### 7.1 Es estado (y de la capa común), no contenido

1. **No se toca el MP4**: `0x3AFA94` empieza por `RcsBackupTblData`; el `ReadFirstPackData` (`0x2B3948`) que
   leería el pack **no se ejecuta** (salta a `0x2B3A28` antes). No hay `open`, ni caja, ni `moov`, ni IFO.
2. **`0xB0800001` es el default del traductor**: por construcción no identifica causa (`0x6F0E96`/`0x6F0EBC`).
3. **La misma firma sale en foto y en XAVC**: el anillo trae `[DCF][MS1]Err RcsBackupTblData` (ruta de foto,
   copia de `0x37C0xx`) y `[XAVCIFO] … 0xB0810001` con el mismo `MSV` detrás. Si fuera contenido, cada formato
   fallaría con su propio código, no con el mismo `Err RcsBackupTblData`.
4. **Es independiente del volumen**: la tarjeta formateada en cámara no cambia nada; el fallo ocurre antes de
   mirar el sistema de ficheros (§5.3).

### 7.2 Cómo se distingue en el log

| Señal | Fallo de ESTADO/plomería | Fallo de CONTENIDO |
|---|---|---|
| Línea previa `[MSV][MS1]Err RcsBackupTblData` (`0x823999`) | **sí** | no |
| Código en 1749 | `0xB0800001` (default) | específico: `0xB0400005`, `0xB0510001`, `0xB0810001`, `0xB0F30001`, `0xB0400001`, `0xB0400006`, `0xB0200001`, tabla `0x91CAD0`… |
| ¿Llega `ReadFirstPackData`? | no | sí |
| Otras rutas (foto/XAVC/DCF) | fallan igual | solo la afectada |
| `mb_load` (`this+0x23`) | queda 0 | queda 0 también, pero con código distinto |

La regla práctica: **si `1749` viene precedido de `Err RcsBackupTblData`, el MP4 no ha entrado en juego**.
El `0xB0800001` de `1340` es el eco; el de `1749` sin `1340` es la entrada por `LoadSub`.

### 7.3 Aviso sobre el mapeo `(userId,backupId) → idx`

El informe `film-pb-1-sub-rcsbackup-20261126.md` da valores concretos (`(0x22,8) → 0xA0`, `(0x23,2..7) → 0xB1..0xBD`)
para la tabla `0x9D23FC`. **No se ha re-verificado** aquí: al volcar `0x9D23FC` con paso `0x18` las primeras
entradas son `{puntero a cadena, id pequeño}` (p. ej. `0x8D7E89 "Dma Link List 2( Mux )" → 0x3E`) y el
terminador `-1` aparece pronto, así que esa tabla parece compartida con otro uso. Queda como **NO_VERIFICADO**:
qué `idx` exacto pide el RCS en el arranque y por tanto qué entrada concreta está vacía.

---

## 8. Correcciones a lo ya publicado

1. **`0xB0800001` no es "lo que devuelve `FlashLoadForMsv`"** (resumen 5 del informe `sub-rcsbackup`): es el
   *default* del traductor. `FlashLoadForMsv` devuelve el mapeo del estado; con `0x13100001` sale `0xB0800001`,
   pero con `0x1340000E` saldría `0xB0400005`, etc.
2. **Faltaba el eslabón `0x10100001 → 0x13100001`**: lo pone `0x350124` al hacer `| [obj+0x24]`
   (`0x350240 orrs r0,r1`). Sin él, el `0x13` del log no cuadra con el `0x10` de `RcsBackupTblData`.
3. **Las líneas `1749` y `1340` no son dos diagnósticos**: son la misma condición a dos niveles de anidamiento.
4. Las VA de este informe están todas verificadas contra la tabla de secciones (`10-verificacion-va.txt`), no
   contra las de otros informes.

---

## 9. Verificación y reproducción

```bash
B=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so
.venv/bin/python3 /tmp/thumbdump.py $B 0x698ec8 0x40    # FlashLoadForMsv (1749)
.venv/bin/python3 /tmp/thumbdump.py $B 0x698f18 0x84    # CheckSalvageStatus (1340)
.venv/bin/python3 /tmp/thumbdump.py $B 0x6f0d4c 0x170   # traductor
.venv/bin/python3 /tmp/thumbdump.py $B 0x3afa94 0x140   # carga MSV
.venv/bin/python3 /tmp/vacheck.py                       # cada VA vs .text/.rodata/.data/.bss
```

Evidencia en `reports/evidence/film-pb-1-sub-mp4ifo-load-20261126/`:

| Fichero | Contenido |
|---|---|
| `01-cadenas.txt` | las cinco piezas del formato con su VA |
| `02-698ec8-flashloadformsv.txt` | función 0x698EC8 + pool |
| `03-698f18-checksalvage.txt` | función 0x698F18 + pool (0x536/0x53C/0x547) |
| `04-698fb8-load.txt` | Load 0x698FB8 + llamantes |
| `05-6f0d4c-traductor.txt` | traductor completo + tabla de salto 0x91CAD0 decodificada |
| `06-6f0a54-impresor.txt` | impresor y sus literales |
| `07-3afa94-ruta.txt` | envoltorio 0x3AFA94 |
| `08-2b39b8-tabla.txt` | lectura del pack y tabla 0xA3699C |
| `09-350124-base.txt` | 0x3502CA/0x3502B8/0x350124 (el `orrs` de la base) |
| `10-verificacion-va.txt` | secciones del ELF y cada VA citada |

## 10. Límites

- **Estático**: no se ha ejecutado firmware ni tocado cámara ni tarjeta.
- El valor `0x13100001` está **medido** en el arnés G22 (`analysis/gui/g22/harness/live/c42t2/shim.log:210`),
  no en la cámara; en la cámara solo consta el `0xB0800001` del anillo del 20-10, que es coherente con él.
- `[obj+0x24] = 0x13000000` es **inferencia forzada** por el `orrs` de `0x350240` y el valor medido.
- **NO_VERIFICADO**: quién registra la tabla `0xA3699C` (el único registrador estático hallado, `0x2B208C`,
  se llama desde `0x2B5A3A`, un manejador de consola); y el `idx` exacto que pide el RCS al arrancar.
