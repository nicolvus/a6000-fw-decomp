# FILM-PB-1 (sub) — Qué configuración lleva a un modo con movie = 0, y si el usuario puede cambiarlo

Fecha: 26-11-2026. **Solo análisis estático** (sin cámara, sin flasheo, sin ejecutar firmware).
Objeto: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(Thumb-2, 10.321.204 B = 0x9D7D34).
Evidencia: [`reports/evidence/film-pb-1-sub-modo-camara-20261126/`](evidence/film-pb-1-sub-modo-camara-20261126/).
Herramientas: capstone del `.venv` (`dump.py`, `dis2.py`, `brscan.py`, copiados en la evidencia).
**No se usó `mcp_rea` para binarios.** Continúa [la tabla de buffers por modo](film-pb-1-sub-tabla-buffers-20261126.md).

---

## 0. Resumen (≤20 líneas)

1. **`Type2Mode` = 0x5F699C–0x5F6A3E** (87 instrucciones, `pop.w` en 0x5F6A3E): `int Type2Mode(type, subType,
   int* pRamMapAreaMode, int* pAreaTblMode)`; elige tabla por `m_systemType` (0 → 0x9DE7C8, **1 → 0x9DE898**, 2 → 0x9DEDC0).
2. **Solo depende de `type`, `subType` y `m_systemType`** (`[0x9DEFE0]`, constante 1 escrita una única vez en
   `MemInfo::Init`, **0x5F755C**): **no lee HDMI, flash, tarjeta, batería, EEPROM ni menús**; `subType == 8` es comodín (0x5F69F0).
3. `type` = trabajo pedido por el software (`0 Movie Pb`, `1 Still Pb`, `2 Movie Rec`, `3 Still Rec`, `4 Index Pb`, … `0x1E`;
   tabla **0x9DF094** con xref real en 0x5F99A0) y `subType` = formato (tabla 0x9DF054).
4. Cadena única: `GetMemoryInformation` (**0x4284AC**, 33 llamadas) → `StreamAreaAllocate` (**0x5F7BE8**, Type2Mode en
   0x5F7C40) o `ChangeAllocate` (**0x5F7F1C**, en 0x5F7F44) → `DistributeBufInfo`.
5. **Los cinco modos con movie = 0 son trabajos de FOTO**: 0x03 ← `Still Rec`(3,8), 0x06 ← `Still Pb`(1,8), 0x12 ←
   `Still Dubbing`(0x0B,8), 0x20 ← `Still Pb RAW`(0x1B,8); 0x13 no lo pide nadie con `m_systemType = 1`.
6. **Foto (0x03) y reproducción de foto (0x06) usan movie = 0 por diseño** (still 24 / 22 MiB): `ThumbnailRecorder` 0x330118 y 0x43966C.
7. **Reproducción de vídeo: no usa esos modos y sí cambia el modo** — `EnterMoviePbStillRec` (0x437A40–0x437AC4) pide
   `Movie Pb` (tabla **0x85AA54**), reparto nuevo (r2 = 1) y deja **0x0E con 20 MiB**; luego `SetUpPlayerInstance`.
8. **Ningún ajuste de cámara** (calidad, formato, HDMI, ahorro) fuerza movie = 0: los trabajos de foto llevan `subType = 8`
   forzado (0x4284BC/0x428528) y los de vídeo `subType` 0–6 caen todos en la misma fila (0x0E / 0x01).
9. Único caso que lo explicaría: reparto fallido — `areaTblMode` se escribe **antes** (0x5F7C7C) y quedaría **0x0E con el
   hueco 11 a 0**; se distingue leyendo `0x9DECAC` / `0xA4F478` / `0xA4F4A8` y las cinco líneas de log (§5).
10. **Instrucción: no hay nada que cambiar en la cámara** (§6). Corregidos además los nombres de modo del informe anterior (§7).

---

## 1. `Type2Mode` completa (VA + instrucciones)

### 1.1 Cuerpo (0x5F699C–0x5F6A3E), desensamblado íntegro en la evidencia 01

```asm
005f699c: push.w {r4,r5,r6,r7,r8,sb,lr}      ; prólogo
005f69a0: sub    sp,#0x14
005f69a2: ldr    r6,[pc,#0xa0]      ; r6 = 0x009DEFE0 -> m_systemType   <-- ÚNICO global leído
005f69a4: add    r7,sp,#0x10
005f69a6: mov    r8,r1              ; r8 = subType
005f69a8: mov    r4,r2              ; r4 = pRamMapAreaMode (salida 1)
005f69aa: mov    r5,r3              ; r5 = pAreaTblMode    (salida 2)
005f69ac: mov    sb,r0              ; sb = type
005f69ae: bl     #0x5f9e0c          ; (helper de log/nivel)
005f69b2: movs   r1,#1
005f69b4: ldr    r3,[r6]            ; r3 = m_systemType
005f69b6: ldr    r2,[pc,#0x90]      ; 0x008D908C "[MemInfo]Type2Mode()   ** m_systemType = [%ld]!!"
005f69b8: bl     #0x5f9d8c
005f69bc: ldr    r3,[r6]
005f69be: cmp    r3,#1
005f69c0: beq    #0x5f69d2          ; ---- systemType 1 (el de este firmware)
005f69c2: cmp    r3,#2
005f69c4: beq    #0x5f69de          ; ---- systemType 2
005f69c6: cbnz   r3,#0x5f6a0c       ; otro valor -> "not found mode"
005f69c8: str    r3,[r4]            ; ---- systemType 0: *pRamMapAreaMode = 0
005f69ca: adds   r3,#0xe
005f69cc: str    r3,[r5]            ;      *pAreaTblMode = 0x0E
005f69ce: ldr    r3,[pc,#0x7c]      ;      tabla 0x009DE7C8
005f69d0: b      #0x5f6a06
005f69d2: movs   r3,#0              ; ---- systemType 1: *pRamMapAreaMode = 0
005f69d4: str    r3,[r4]
005f69d6: adds   r3,#0x11
005f69d8: str    r3,[r5]            ;      *pAreaTblMode = 0x11 (valor por defecto si no hay match)
005f69da: ldr    r3,[pc,#0x74]      ;      tabla 0x009DE898   <<< LA ACTIVA
005f69dc: b      #0x5f6a06
005f69de: movs   r3,#0              ; ---- systemType 2: 0 / 0x11 / tabla 0x009DEDC0
005f69e0: str    r3,[r4]
005f69e2: adds   r3,#0x11
005f69e4: str    r3,[r5]
005f69e6: ldr    r3,[pc,#0x6c]
005f69e8: b      #0x5f6a06
005f69ea: cmp    sb,r2              ; bucle: ¿type de la entrada == type pedido?
005f69ec: bne    #0x5f6a04
005f69ee: ldr    r2,[r3,#4]         ; subType de la tabla
005f69f0: cmp    r2,#8
005f69f2: beq    #0x5f69f8          ; subType==8 -> COMODÍN, casa siempre
005f69f4: cmp    r8,r2
005f69f6: bne    #0x5f6a04
005f69f8: ldr    r2,[r3,#0xc]       ; *pRamMapAreaMode = entrada+0xC
005f69fa: movs   r6,#1              ; encontrado = 1
005f69fc: str    r2,[r4]
005f69fe: ldr    r3,[r3,#8]         ; *pAreaTblMode = entrada+8 (modeId)
005f6a00: str    r3,[r5]
005f6a02: b      #0x5f6a0e
005f6a04: adds   r3,#0x10           ; siguiente entrada (0x10 B)
005f6a06: ldr    r2,[r3]            ; terminador: type == 0x20
005f6a08: cmp    r2,#0x20
005f6a0a: bne    #0x5f69ea
005f6a0c: movs   r6,#0              ; no encontrado
005f6a0e: bl     #0x5f9e0c
005f6a12: ldr    r3,[r4]
005f6a14: movs   r1,#1
005f6a16: ldr    r2,[pc,#0x40]      ; 0x008D90C0 "type=%d /subType=%d / ramMapAreaMode=%ld / areaTblMode=%ld"
005f6a18: str.w  r8,[sp]
005f6a1c: str    r3,[sp,#4]
005f6a1e: ldr    r3,[r5]
005f6a20: str    r3,[sp,#8]
005f6a22: mov    r3,sb
005f6a24: bl     #0x5f9d8c
005f6a28: cbnz   r6,#0x5f6a36
005f6a2a: bl     #0x5f9ddc
005f6a2e: movs   r1,#1
005f6a30: ldr    r2,[pc,#0x28]      ; 0x008D910F "[MemInfo]not found mode"
005f6a32: bl     #0x5f9d8c
005f6a36: mov    r0,r6              ; retorno 0/1
005f6a38: add.w  r7,r7,#4
005f6a3c: mov    sp,r7
005f6a3e: pop.w  {r4,r5,r6,r7,r8,sb,pc}
```

### 1.2 De qué decide (tabla cerrada)

| entrada | cómo se obtiene | ¿la controla el usuario? |
|---|---|---|
| `type` (0–0x1E) | argumento; lo elige el módulo que pide memoria (33 sitios, evidencia 05) | **no** (lo fija el código de la operación) |
| `subType` (0–8) | argumento; `GetMemoryInformation` lo deriva de un `contentType` (formato del contenido) | **no** (es el formato del fichero/operación, no un menú) |
| `m_systemType` | `[0x9DEFE0]`, **escrito solo en 0x5F755C con el literal 1** | **no** (constante de compilación) |
| HDMI / flash / tarjeta / batería / ahorro / calidad | **no aparecen** en la función | — |

Prueba de lo último: el cuerpo solo tiene **una** carga de un global (`ldr r3,[r6]`, r6 = 0x9DEFE0, en
0x5F69B4 y 0x5F69BC) y **ningún** `bl` a servicios (0x5F9E0C / 0x5F9D8C / 0x5F9DDC son
helpers de log del propio `MemInfo`, todos los `bl` del cuerpo). No hay `Fsys_*` ni acceso a `/dev`.

### 1.3 La cadena hasta `Type2Mode` (quién pide qué)

```
módulo de la operación
  └─ bl 0x004284AC  GetMemoryInformation(type, contentType, bAllocate, extListPackHeader)
       ├─ 0x4284B0 (bhi) / 0x4284BC-0x4284CC: si type>0x0F o ((1<<type)&0x9FD5)==0 -> subType = 8 (DontCare)
       ├─ contentType -> subType   (0x10 se deja; 1(M2PS)->1; 6->4; 8->3; 0x20->0; 0x80->6; 0x100->7; 0x200->4)
       └─ si bAllocate!=0: 0x428588  b.w 0x005F7BE8  StreamAreaAllocate(type, subType, hdr)
          si bAllocate==0: 0x428594 b.w 0x005F7F1C  ChangeAllocate(type, subType)
                                   ├─ 0x5F7C40 / 0x5F7F44:  bl 0x005F699C  Type2Mode(...)
                                   └─ 0x5F7CF2 / 0x5F7FA4:  bl 0x005F703C  DistributeBufInfo(mode, 0xA4F368, rammap)
```
Llamadores de `Type2Mode` (escaneo completo de BL de 32 bits): **solo 0x5F7C40 y 0x5F7F44**.
Llamadores de `GetMemoryInformation`: 33 (evidencia 05).

### 1.4 Quién escribe `areaTblMode` (0x9DECAC) y con qué

| sitio | escritura | cuándo |
|---|---|---|
| 0x5F7C7C (`StreamAreaAllocate`) | `[0x9DECAC] = areaTblMode` | **antes** de redistribuir: si la distribución falla, el modo ya está cambiado |
| 0x5F7FD8 (`ChangeAllocate`) | `[0x9DECAC] = areaTblMode` | **después** de `DistributeBufInfo` OK; si falla no se toca |
| 0x5F80A4 (`StreamAreaFree`) | `[0x9DECAC] = -1` | al liberar el área |

Consecuencia práctica: **0x9DECAC no es prueba de que la tabla esté bien repartida.** Hay que leer
también 0xA4F478 (size del hueco 11) y 0xA4F4A8 (hueco 13).

---

## 2. Los cinco modos con movie = 0: combinación que los selecciona

`m_systemType = 1` ⇒ tabla **0x009DE898**. Nombres de `type` de **0x9DF094** (evidencia 03):

| modo | size movie (11) | size still (13) | `type` | nombre | `subType` | ¿alcanzable aquí? |
|---|---|---|---|---|---|---|
| **0x03** | **0 (ausente)** | 0x01800000 (24 MiB) | **3** | **Still Rec** | 8 (DontCare) | **sí** — lo pide `ThumbnailRecorder` (0x330118, medio «STILL») y cualquier grabación de foto |
| **0x06** | **0 (ausente)** | 0x01600000 (22 MiB) | **1** | **Still Pb** | 8 (DontCare) | **sí** — reproducción de foto (0x43966C → `SetUpPlayerInstance` 0x4396A6) |
| **0x12** | **0 (ausente)** | 0x01800000 (24 MiB) | **0x0B** | **Still Dubbing** | 8 (DontCare) | sí (dubbing de fotos; sin función en la A6000) |
| **0x13** | **0 (ausente)** | 0x01000000 (16 MiB) | — | — | — | **no** (ninguna entrada de 0x9DE898 produce 0x13) |
| **0x20** | **0 (ausente)** | 0x00300000 (3 MiB) | **0x1B** | **Still Pb RAW** | 8 (DontCare) | sí (reproducción de RAW) |

Los cuatro alcanzables son **trabajos de foto**, y en los cuatro el `subType` es **8 (comodín)**: no hay
ninguna combinación de `subType` que cambie la fila. Otros modos con movie = 0 que **no** son de esta
lista (para no confundir): 0x0F (`Thumb Rec`, sin tabla de buffers), 0x17 (`Content Edit`), 0x11
(`Create`/`Idle`) y 0x21/0x22/0x24 (movie presente con `size = 0` que se toma del `RamMapAreaInfo`).

### 2.1 Lo contrario (todos los trabajos de vídeo, movie > 0)

| `type` | nombre | `subType` | modo | movie (11) |
|---|---|---|---|---|
| 0 | Movie Pb | 0–6 | 0x0E | **0x01400000 (20 MiB)** |
| 0 | Movie Pb | 7 | 0x22 | 0 (del rammap) |
| 2 | Movie Rec | 1–6 | 0x01 | **0x01C00000 (28 MiB)** |
| 2 | Movie Rec | 7 | 0x21 | 0 (del rammap) |
| 4 | Index Pb | 0–7 | 0x05 | 0x01200000 (18 MiB) |
| 6 | Dual Rec | 1–6 | 0x0C | 0x01C00000 (28 MiB) |
| 8 | Pb Capture | 0–6 | 0x0E | 0x01400000 (20 MiB) |
| 0x0F | Highlight Pb | 2–3 | 0x07 | 0x01400000 (20 MiB) |
| 0x11 | Multi Rec HDHD | 8 | 0x01 | 0x01C00000 |
| 0x15 | Idle | 8 | 0x11 | 0 (ninguna de las dos) |
| 0x1A | OUCranc Rec | 8 | 0x1F | 0x03000000 (48 MiB) |
| 0x1D / 0x1E | Multi Rec AVCHDMP4 / XAVCMP4 | 8 | 0x23 / 0x24 | 28 MiB / 0 (rammap) |

Volcado completo de las 54 entradas activas: evidencia **04**.

---

## 3. ¿Es el modo de FOTO o de REPRODUCCIÓN? ¿Cambia al entrar en vídeo?

### 3.1 Foto (grabación) — sí, movie = 0

`ThumbnailRecorder` (**0x33009C–0x330120**): compara el tipo de medio con `"MOVIE"` (0x80C66F) y
`"STILL"` (0x80C687); si es STILL pone `r4 = 3` y registra el literal de log
`" type = MemInfo::MEM_TBL_STILL_REC;"` (0x812B84), luego `r0 = r4; r1 = r5; bl 0x5F8020`
(= `ChangeAllocate`) en **0x330118** y lee **`[ret+0x138]` / `[ret+0x140]`** (hueco still). Con
`type = 3` ⇒ `Type2Mode` devuelve **0x03** (movie ausente, still 24 MiB). Es decir: **en foto el área de
movie vale 0 por diseño**, y por eso las miniaturas de foto funcionan (usan el hueco 13).

### 3.2 Reproducción de foto — sí, movie = 0

**0x43966C**: `r0 = 1` (`Still Pb`) → `GetMemoryInformation(1, …)` → modo **0x06**; justo después
**0x4396A6** `bl 0x43910C SetUpPlayerInstance(…, setupMode=2 …)` que lee **`[+0x138]`/`[+0x140]`**
(0x4392D2/0x4392D6), es decir el hueco *still* (22 MiB).

### 3.3 Reproducción de vídeo — no, y **sí cambia el modo**

Bloque **0x437A40–0x437AC4** (cadenas 0x85AA5C `"EnterMoviePbStillRec"`, 0x85AA71
`"core/feature/player/cam/feaCorePbCaptureApi.cpp"`, 0x85AAA1 `"ExitMoviePbStillRec()"`):

```asm
00437a6c: ldr.w r1,[r4,#0xdb8]   ; máscara de tipos de contenido del vídeo
00437a70: tst.w r1,#0x10  / #0x80 / #0x100 ...   ; -> r1 = 0x10 | 0x80 | 0x100 | 8   (contentType)
00437a92: ldr   r3,[r5,#0x10]    ; 0 o 1
00437a94: cmp   r3,#1
00437a96: itte  ls
00437a98: ldrls r2,[pc,#0x90]    ; r2 = 0x0085AA54  -> tabla { 0x00000000, 0x00000018 }
00437a9a: ldr.w r0,[r2,r3,lsl#2] ; type = Movie Pb (0x00)  |  Movie Pb 3D (0x18)
00437a9e: movs  r0,#0             ; (si [r5,#0x10] > 1 -> type 0)
00437aa0: ldr   r3,[r5,#0xc]
00437aa2: movs  r2,#1             ; bAllocate = 1  -> StreamAreaAllocate (reparto NUEVO)
00437aa4: bl    #0x4284ac         ; GetMemoryInformation
00437aa8: str.w r0,[r4,#0xdac]    ; guarda el puntero a la tabla de áreas
00437aac: cbz   r0,#0x437ace      ; si devolvió 0 -> sale por error, NO monta el reproductor
...
00437ac4: bl    #0x43910c         ; SetUpPlayerInstance(..., setupMode=1, ...)
```

Con `type = 0` (`Movie Pb`) y `m_systemType = 1` ⇒ **modo 0x0E, movie = 0x01400000 (20 MiB)**.
`SetUpPlayerInstance` (despacho `tbb` en 0x4391F0, `subs r3,r2,#1` / `cmp r3,#4` / `bhi 0x43944E`) lee
**`[+0x108]`/`[+0x110]`** (movie) en setupMode 1, 4 y 5 (0x439256/0x43925A) y **`[+0x138]`/`[+0x140]`**
(still) en setupMode 2 (0x4392D2/0x4392D6); en setupMode 3 elige por `0x40000031` (0x439312–0x43932E).
Si el puntero de tabla es **NULL**, salta a 0x439460 y **no llama a `SetArea`** (0x43924C, 0x439440, 0x43944E):
el área anterior se queda como estaba. `SetArea(0,0,1)` solo se ejecuta con `setupMode` fuera de 1..5 **y**
puntero no nulo (0x43944E–0x43945C).

**Respuesta a la pregunta 3:** los modos con movie = 0 son los de foto y reproducción de foto; **al entrar
en reproducción de vídeo el modo se cambia a 0x0E y se pide un reparto nuevo** (r2 = 1). No hay ningún
camino de este binario que reproduzca vídeo con un modo de foto, **salvo** el caso del §1.4: que el
reparto nuevo falle y `areaTblMode` se quede escrito a 0x0E con el hueco 11 sin escribir (0).

---

## 4. ¿Hay algún ajuste de cámara que fuerce un modo con movie = 0?

**No.** Por cuatro razones independientes:

1. `Type2Mode` no lee ningún ajuste (§1.2).
2. Para los trabajos **de foto** (`type` 1, 3, 5, 0x0B, 0x0D, 0x1B) y para **todo `type > 0x0F`**,
   `GetMemoryInformation` fuerza `subType = 8`: bien porque `(1<<type) & 0x9FD5 == 0` (0x4284BC–0x4284CC),
   bien por el `bhi 0x428528` de 0x4284BA. Da igual la calidad, el formato o el tamaño de imagen.
3. Para los trabajos **de vídeo** todos los `subType` 0–6 caen en la misma fila (0x0E / 0x01). Solo
   `subType = 7` llevaría a 0x21/0x22, y su tamaño no está en la tabla sino en el `RamMapAreaInfo`
   (`mt_order`), es decir, en el mapa de RAM del sistema, no en un menú.
4. `m_systemType` es **constante de compilación**: `MemInfo::Init` (0x5F74D4) hace en **0x5F7550–0x5F755C**
   `ldr r3,[pc,#0x15c]` (= 0x009DEFE0), `movs r2,#1`, `str r2,[r3]`. No hay ninguna otra escritura en todo
   el binario. Ningún valor de NVRAM/EEPROM puede cambiarlo.

Caso especial mirado y descartado: **HDMI**. El bloque de entrada a reproducción usa la máscara
`[+0xdb8]` (tipos de contenido del *fichero*), no una bandera de salida HDMI; y `LibInfraHdmi` no
participa en esta cadena. **Ahorro de energía / tarjeta / batería**: no aparecen en `Type2Mode` ni en
`GetMemoryInformation`. **Formato de grabación** (`contentType`): solo elige `subType` dentro de filas
que ya tienen movie > 0.

---

## 5. Qué cambia entonces en el síntoma «no reproduce ningún vídeo» (lo que hay que leer en cámara)

Como el modo de vídeo **sí** tiene 20 MiB, la hipótesis «la tabla deja movie = 0» **queda descartada para
la reproducción de vídeo** salvo la variante «modo 0x0E con hueco 11 sin escribir». Las dos lecturas que
lo separan, sin tocar la cámara:

| lectura | esperado si todo bien | si sale esto, ése es el problema |
|---|---|---|
| `0x9DECAC` al pulsar play en un vídeo | 0x0000000E | 0x06/0x03 (no hubo cambio), 0xFFFFFFFF (área liberada, 0x5F80A4), 0x11 (Idle) |
| `0xA4F478` (movie, 4 B) | 0x01400000 | 0x00000000 con 0x9DECAC = 0x0E ⇒ falló el reparto |
| `0xA4F4A8` (still, 4 B) | 0x00000000 en modo 0x0E | 0x01600000/0x01800000 ⇒ sigue en modo de foto |

Líneas de log que ordenan la causa (`libmpr`, nivel verboso; VA de la cadena):

1. `[MemInfo]Type2Mode: type=%d /subType=%d / ramMapAreaMode=%ld / areaTblMode=%ld` (0x8D90C0)
2. `[MemInfo]StreamAreaAllocate(next) : type=%ld /subType=%ld /m_ramMapAreaMode=%ld /m_bufTblMode=%ld` (0x8DA590)
3. `[MemInfo]StreamAreaAllocate(next) : Type2Mode falied...` (0x8DA5F2) ← aquí **no** se toca 0x9DECAC
4. `[MemInfo]**DistributeBufInfo --bufTbl item count = %d / defined count = %d` (0x8D9E64) y
   `...--bufTbl distribute Failed!` (0x8D9EAF) ← aquí **sí** se cambió 0x9DECAC y no el reparto
5. `[MemInfo]StreamAreaAllocate(next): complete ret=%ld` (0x8DA720) ← `ret=0` ⇒ no hay base

Si sale (1) con `type=0, subType=6, areaTblMode=0x0E` y (5) con `ret=1` y `0xA4F478 = 0x01400000`,
**esta línea de investigación está cerrada** y el fallo es el ya documentado (IFO no cargado / mutex de
`mp4Ifo_If` en `GetPlayThumbnailInfo`).

---

## 6. Conclusión e instrucción concreta y segura

**No hay ningún ajuste de la cámara que lleve a un modo con movie = 0 en reproducción de vídeo, y por
tanto no hay nada que el usuario pueda cambiar para arreglarlo.** Los cinco modos con movie = 0 son los
trabajos de foto (grabar foto, reproducir foto, reproducir RAW, dubbing de fotos) y valen 0 porque la
foto no necesita el búfer de vídeo; al entrar en reproducción de vídeo el firmware cambia a 0x0E (20 MiB).

Instrucción segura (no modifica nada, solo observa):

1. Encender la cámara con la tarjeta habitual, entrar en reproducción y seleccionar **un vídeo grabado
   por la propia cámara**. Pulsar play.
2. Con el monitor de sólo lectura del proyecto, leer en ese momento **0x9DECAC**, **0xA4F478** y
   **0xA4F4A8**, y capturar las cinco líneas de log del §5.
3. Interpretación: **0x0E / 0x01400000 / 0** ⇒ la tabla y el reparto están bien y la causa no es el modo;
   **0x0E / 0 / ≠0** ⇒ fallo de reparto (mirar `DistributeBufInfo`/`StreamAreaAllocate`, no los menús);
   **0x06 o 0x03** ⇒ no se ejecutó la entrada de vídeo (mirar `Type2Mode falied...`).
4. Qué debería pasar si el modo se recalculara bien: al pulsar play, `areaTblMode` pasa de 0x06 (foto) a
   **0x0E**, el hueco 11 pasa de 0 a **20 MiB** y el hueco 13 de 22 MiB a 0. Si eso ocurre y aun así no
   hay imagen, el problema está después de `SetUpPlayerInstance`, no en el reparto de memoria.

**No probar** (no aportan y no son la causa): cambiar calidad/tamaño de imagen, formato de vídeo,
«Recuperar BD imág.», formatear otra tarjeta, quitar HDMI, cambiar ajustes de ahorro. Ninguno toca
`Type2Mode`.

---

## 7. Corrección al informe anterior (nombres de modo)

`film-pb-1-sub-tabla-buffers-20261126.md` §4 lista los nombres de modo leyendo la tabla como
`{ptr, id}` a partir de **0x9DF090**. El código lo hace al revés: el literal es **0x009DF094** y el
formato es **`{id, ptr}`** (0x5F99A0 / 0x5F991E / 0x5F9210: `[base+i*8]` = id, `[base+i*8+4]` = puntero).
Por tanto:

* el nombre de `id 0` es **`Movie Pb`**, no el que se listaba como `id 1`; **toda la columna de nombres
  está desplazada una posición** (0x01 = `Still Pb`, 0x03 = `Still Rec`, 0x06 = `Dual Rec`,
  0x0E = `Content Edit`, 0x11 = `Multi Rec HDHD`, 0x12 = `Still Dubbing`, 0x14 = `Mass Strage`,
  0x1B = `Still Pb RAW`, …);
* además esa tabla **no nombra los `modeId`**: nombra el argumento `type` de `StreamAreaAllocate`
  (como dicen los literales del volcado: `" main type "` 0x8DB498 cargado en 0x5F9904 y `" sub type "`
  0x8DB4A4 cargado en 0x5F9942).
  Los `modeId` (0x00–0x24) **no tienen tabla de nombres en `libmpr`**.

Ninguna conclusión de tamaños cambia: los 0 de movie siguen siendo los mismos cinco modos. Lo que cambia
es **quién los pide**: no «Movie Rec» ni «I-Pic Rec», sino **Still Rec / Still Pb / Still Dubbing /
Still Pb RAW**, que es lo que hace coherente que movie = 0.

---

## 8. Límites (NO_VERIFICADO)

* **NO_VERIFICADO en cámara** qué `areaTblMode` hay en el fallo real, ni qué líneas de log salen: todo
  este informe es estático (la cámara no se ha tocado).
* **NO_VERIFICADO** el significado exacto de `contentType` (los códigos 1/6/8/0x10/0x20/0x80/0x100/0x200
  no están documentados en el binario; 1→M2PS y 0x20→DVD cuadran, el resto es inferencia).
* **NO_VERIFICADO** que las 10 llamadas con `type = 0x0E` (`Content Edit`, modo 0x17 con las dos áreas a 0)
  sean código muerto en la A6000: están en el bloque de *dubbing* (`DubbingUnload` 0x42CF0A,
  `EnterDubbing` 0x42D2F4), que esta cámara no ofrece.
* **NO_VERIFICADO** que `type = 0x0D` (`Thumb Rec`) → modo 0x0F (sin tabla de buffers) sea tolerado: en
  `ChangeAllocate`, si `Type2Mode` falla no se cambia nada (0x5F7F6C–0x5F7FB2), que es lo que el
  `ThumbnailRecorder` necesita (reutilizar el área de foto).
* Los nombres de `type`/`subType` son de tablas de depuración del propio binario, pero **con xref real**
  (§7), a diferencia de la lectura anterior.

---

## 9. Evidencia

`reports/evidence/film-pb-1-sub-modo-camara-20261126/`

| fichero | contenido |
|---|---|
| `01-type2mode-0x5F699C-completo.txt` | desensamblado íntegro de `Type2Mode` (0x5F699C–0x5F6A3E) + pool de literales |
| `02-llamadores-y-cadena.txt` | escaneo de BL/B.W: llamadores de `Type2Mode`, `StreamAreaAllocate`, `ChangeAllocate`, `GetMemoryInformation`, `SetUpPlayerInstance` y los *thunks* de cola |
| `03-tablas-nombres-type-subtype.txt` | tabla de nombres `type` (0x9DF094, ids 0–0x1E) y `subType` (0x9DF054) con su xref |
| `04-mapeo-tipo-a-modo-sistema1.txt` | las 54 entradas de la tabla activa con nombre, `modeId`, movie (11) y still (13); y los cinco modos con movie = 0 con quién los pide |
| `05-getmemoryinformation-0x4284AC.txt` | `GetMemoryInformation` completa + los 33 sitios de llamada con su `type` |
| `06-reproduccion-video-y-setup-player.txt` | bloque `EnterMoviePbStillRec` (0x437A40–0x437AC4), tabla 0x85AA54, `SetUpPlayerInstance` (despacho `tbb`) y las ramas de `SetArea` |
| `07-m_systemType-init-constante.txt` | escritura única `[0x9DEFE0] = 1` en 0x5F755C y lectores |
| `dump.py`, `dis2.py`, `brscan.py` | scripts usados (lectura por VA, desensamblado, escaneo de ramas de 32 bits) |
