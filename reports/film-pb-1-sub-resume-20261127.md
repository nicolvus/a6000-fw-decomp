# FILM-PB-1 — Punto de reanudación: formato, destino, validación y 0x1A

27-11-2026. **Estático**: cámara no accesible, sin red/USB/flash. **Espacios: VA del ELF (base 0)**; en libmpr
REA = ELF+`0x10000`. fw 3.21 `.../nflasha15_unpacked_unpacked/lib/` (libmpr SHA-256 `9a74a3bb…4c30`). Capstone 5 local,
sin `mcp_rea`. Evidencia: [`evidence/film-pb-1-sub-resume-20261127/`](evidence/film-pb-1-sub-resume-20261127/)
(`obj-8cae60-8cb4b2.txt`, `mpr-437bc0-playmovie.txt`, `mpr-resume-chain.txt`, `mpr-resume-strings.txt`).

## 1. 0x8CAE60 y 0x8CB4B2 no son MPR: son los envoltorios del modelo

| VA (libObj) | Qué es | Evidencia |
|---|---|---|
| **0x8CAE60** (en 0x8CADF0..0x8CAEDC) | Envoltorio «get»: `blx` al PLT `0xE1814` = `MprIf::GetContentResumePoint(ulong, EntryCondition, EntryId, ulong)`; lo llama **sólo** 0x8B241C | obj:8 |
| **0x8CB4B2** (en 0x8CB448..0x8CB4E6) | Envoltorio «set»: `blx` PLT `0xDFAB4` = `MprIf::SetContentResumePoint(...)`; lo llama **sólo** 0x8B125C | obj:44 |

**Corrección** al [informe de catálogo](film-pb-1-sub-catalogo-20261127.md) §5: `0x7267FA` **no** llama a
`GetContentResumePoint`; cae en `0x726650` (`"WAF"` + `MprFileIf::WriteAndFlush`, un volcado). El único llamador real
es `0x8CAE60`.

## 2. Formato del valor y destino

- **Get (`0x8CAE60`)**: vuelca la respuesta en un struct de 0x78 B del llamador — `[+0]`=estado, `[+8]`=válido, y
  **terna h/m/s en `+0x60/+0x64/+0x68`** más **segunda terna en `+0x6C/+0x70/+0x74`** (3 palabras de 32 b cada una;
  `0x8CAECC-0x8CAF0A`). Retornos: 0 = OK, **8 = «no válido»** (`ldrb r3,[r0,#8]` en `0x8CAEC8`), `0x6001` = sin parámetro.
  Ese molde es el de `PbTimeInfo` (modelo+`0x534`): `+0x60/64/68` = `m_pbTimeInContent` (0x594/0x598/0x59C).
- **Destino inmediato (RAM)**: `0x8B241C` guarda la terna en **this+`0x1314`** (→ `this+0x1374/0x1378/0x137C`) y el
  código en `this+0x138C`. Es caché en RAM del controlador, no NVRAM.
- **Quién lo escribe**: `0x8B125C` (único llamador del set) desde `0x8DDEA8`, `0x8E123E` y `0x8E4C82`, siempre tras el
  flag «reanudación pendiente» `this+0x5EAC`; posición en `this+0x18` (16 B) y `this+0x30` (48 B), EntryId `this+0x28`.
- **Cadena**: `MprIf::GetContentResumePoint` **0x721684** / `SetContentResumePoint` **0x7216F8** → API
  **0x41000046** / **0x41000045** (pools `[0x7216F4]`, `[0x721764]`; tabla 0x66F284/0x66F27C =
  `CB_GET/SET_CONTENT_RESUMEPOINT`) → `AviMMgr::Get/SetContentResumePoint` **0x612280**/**0x612140**
  (sub-órdenes **0x23000043**/**0x23000042**, buffer 0x58 B).
- **Destino persistente: el índice AV, no NVRAM.** Registro por contenido `PubResume::ResumeInfo` (0x58 B:
  `header.resumeType`, `<tipo>.Data.entryId`, `rsmInfo.bIsValid`; para MP4 `vSyncSampleNo` y `vSyncSampleTimeOffset`,
  cadenas 0x918852/0x91A414/0x91A43E), escrito por el vaciado del índice `sources/avi_if/AviSeqFlush.cpp`:
  **`ResumeFlushAVIndexFile`**, `FlushAVIndexFileInParallel`, `WaitFlushAVIndexFile` (0x7BE72C-0x7BE790). En RAM lo
  cachea `ResumeMgr` (typeinfo 0x941CC4; `LastResumeInfo`, `ResumeMgr::BackupWrite`). Para MP4 el punto guardado es
  **sync sample + offset de tiempo**, no h:m:s.

## 3. El manejador de PlayMovie (orden 0x4000001D) **no lee** el punto de reanudación

- Función `0x437BC0..0x437D50` (REA `0x447BC0`). Orden interno: `[this+0x1F0]==5` (si no → `0x0A`, `0x437BE4`) →
  guarda A `0x447A1E` → guarda B `0x447F26` → pre-motor `0x447DA8` (vtable+`0xB4` = `MovieReadStart` `0x608698`) →
  `PbStart` `0x307F54` → `blx [vtable+0x1C]` con la finalización `0x4000001D`.
- **Cero** llamadas a `Get/Set/ClearContentResumePoint`, `GetContentResume` o `ChangeResumeInfo`: en todo libmpr esas
  APIs sólo las invocan los mandos de depuración `MprIfMcmd` (`0x731504`, `0x7316D4`).
- Con el punto sólo hace **paso**: `r8=[r7+0x78]` (4.º arg); si ≠0 copia **0x3C B** (`0x437C8C: movs r2,#0x3C` +
  `bl 0x12111C`) y entrega el puntero en `[sp+0xC]` (`0x437C9C`); si NULL, NULL. **No lo compara con la duración, no lo
  rechaza, no comprueba el clip.**
- `MoviePlayerIf::PbStart` `0x307F54` sólo lo imprime (`- pResumeInfo [0x`, 0x307FE4) y delega en `0x3079AA` (devuelve 0).
  El orden hermano **0x4000001E** (`MprIf::ResumePlayMovie` `0x7229AC`) es el destinado a reanudar.

## 4. Validaciones que sí existen — y sus códigos

`AviMMgrDBIf::GetContentResumePointCmd` **0x63523C** (`avimmgr/AviMMgrDBIf.cpp`) es quien valida, y sólo al **leer**:

| Comprobación | Sitio | Código devuelto | 0x7111B0 |
|---|---|---|---|
| máscara de tipos vacía/inválida | 0x6353AE | 0x31000001 | 0x05 |
| tipo del registro ≠ tipo pedido (`GetResumeInfo` 0x75E814/0x75EC9C) | 0x635536-0x63554E | 0x31000009 | 0x2A |
| `ResumeInfoToPlayPosition` (MP4 = `0x6EA1B4` → vtable+0xF0) | 0x6356BA | el del ifo | ≠0x1A salvo 0x31000002 |
| **`tst r8,[r5+4]` → `contentType missmatch`** | **0x6356EA-0x6356F0** | **0x31000002** | **0x1A** (sitio 0x71153C) |
| `GetLocationClusterIndexFromContent` (0x3F5F40) / `ConvEntryIdPostToPre` (0x678164) | 0x63579A / 0x6357F8 | el del ifo | — |
| **EntryId del registro ≠ EntryId pedido** | **0x63582A-0x63587C** | **ninguno**: avisa `EntryId Unmatch`, **no copia** el valor y **devuelve éxito** | — |

Traducción (tabla del traductor, `…motor…-tabla-0x1a.txt:10`): **`0x31000002 → 0x1A`**; 0x31000001→0x05,
0x31000007→0x0A, 0x31000009→0x2A.

## 5. Veredicto sobre el 0x1A
| Vía | ¿Un punto inválido puede producirla? | Evidencia |
|---|---|---|
| **A** `0x437C0A` «Pb Disable!! ref) dsm get» | **No** | guarda A usa `[core+0xDB8/0x1EC/0xDC0]`; el punto no entra |
| **B** `0x437C3C` «Detect UnSupported Content» | **No como causa; sí como efecto** | `isSupportContent` 0x61A8F0 resuelve la condición con `0x3F9C7C`; el punto sólo se **escribe** después (`0x447EE2` → vtable+`0x54` = `AviMMgr::UpdateResumeInfo` 0x61AAA4) |
| **C** motor/asíncrono | **NO_VERIFICADO** | el puntero viaja a `PbStart` (`0x437C9C`) y al paso `ResumePbStart` (cadenas 0x806E60, 0x8080A3); esa ruta no se ha traído |
| **D (nueva, verificada en código)** | **Sí**: registro con **tipo de contenido distinto** del pedido ⇒ **0x31000002 → 0x1A** | 0x6356EA / 0x6357D4 + 0x71153C |

**Veredicto:** por las tres vías del manejador, el punto de reanudación **no** puede producir el `0x1A`: el manejador no
lo lee ni lo valida, y A y B no consultan reanudación. Un punto «mayor que la duración» tampoco se compara con la
duración en el camino síncrono (el único filtro posible está dentro de `ResumeInfoToPlayPosition`, vtable+`0xF0`, no
desensamblado). Lo que **sí** es un productor real de `0x1A` es la vía **D**, en la API de lectura (`0x41000046`): un
registro de otro clip/tipo (p. ej. heredado de XAVC) da `contentType missmatch` → `0x31000002` → `0x1A` **antes** de
reproducir. Que el objeto/GUI convierta ese error en «No se puede visualizar.» es **NO_VERIFICADO**.

## 6. Comprobación concreta (dato exacto a mirar)

1. **Tarjeta, 0 riesgo**: en `AVF_INFO/AVIN0001.INP` localizar el registro de `MAH04198.MP4` (`grep -aob`) y leer su
   bloque `PubResume::ResumeInfo` (0x58 B). **Corrupto =** `bIsValid=1` y (`entryId` ≠ el del clip **o**
   `header.resumeType` ≠ MP4/AVC **o** `vSyncSampleNo > 285` **o** `vSyncSampleTimeOffset > 9509 ms`) — 285 cuadros =
   9,5095 s · 29,97. Contraste con los otros 6 clips (5,005 / 24,5245 / 31,5315 / 34,5345 / 52,5525 / 72,5725 s).
2. **Cámara, una línea**: mando `MPR MMGRIF GetContentResumePoint 0 NONE <entryId>` → imprime `*** Movie Play Resume
   Information ***` y `C Idx Type S Resume Info`; tipo = MP4/AVC y posición ≤ 9,5 s. Si sale
   `GetContentResumePointCmd : contentType missmatch` (0x8EE8F5) se ha visto la vía D en vivo.
3. **Prueba funcional barata**: renombrar `AVF_INFO` (o Menú → Recuperar BD imág.) borra el punto; si el «0:02»
   desaparece y el clip se reproduce, el registro era el culpable.

## 7. Límites
- **NO_VERIFICADO** el copista `controlador+0x1314` → `modelo+0x594`, y el interior de `ResumeInfoToPlayPosition`
  (vtable+`0xF0` del ifo MP4) y de `0x3F5F40`: si alguno devolviera `0x31000002`, también daría `0x1A`.
- **NO_VERIFICADO** que libObj/GUI traduzca ese `0x1A` a «No se puede visualizar.», ni los offsets del bloque de 0x58 B
  en `AVIN0001.INP` (receta diferencial, §6.1). Sin tarjeta ni cámara: cero medidas.
