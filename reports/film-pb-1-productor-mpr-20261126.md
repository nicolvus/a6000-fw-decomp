# FILM-PB-1 — productor de `MPR::ER_FAILED` (0x1A) localizado por completo (26-11-2026)

Estado: **mecanismo CERRADO estáticamente**; queda un solo dato de ejecución para saber cuál de los dos guardas saltó.
Libmpr analizada: `fw321/.../lib/libmpr.so`, SHA-256 `9a74a3bb…4c30`. Todas las direcciones de este informe son
**VA del ELF (base 0)**. REA importa esta biblioteca con **+0x10000** (la vista usada en el traspaso del 25-11), de modo que
*REA = ELF + 0x10000*: `FUN_00437BC0` (ELF `0x437BC0`) es `FUN_00447BC0` en REA.

## 1. Cadena completa (VERIFICADO contra bytes y pseudocódigo)

| Paso | Dirección | Qué hace |
|---|---:|---|
| `MprIf::PlayMovie` | `0x7229E0` | tres logs (`AsyncApiCall`, `AsyncApiCallWithEntryId`, `PlayMovie`) y llama a `FeaIf::PlayMovie`; devuelve 0 |
| `FeaIf::PlayMovie` | `0x44EE9C` | comprueba la cola (`[this+4]`, vtable+0x18) y encola la orden **0x4000001D** con un mensaje de **0x8C** bytes (vtable+0x20); si la cola rechaza devuelve 9 |
| Despachador del hilo FeaCore | `0x429C38` | `switch (msgId)`: `case 0x4000001D` → `FUN_00437BC0` (ver §2) |
| **Manejador real de PlayMovie** | `0x437BC0` | guardas, arranque del motor y finalización (§2–§4) |
| `MoviePlayerIf::PbStart` | `0x307F54` | arranque del motor de reproducción (solo si pasan las guardas) |

Mensaje `0x4000001D` (0x8C bytes), tal como lo copia `FeaIf::PlayMovie` y lo lee el despachador:

| Offset | Campo |
|---:|---|
| `0x00` | `MPR::EntryId` (dos palabras) |
| `0x1C` | válido de `RSMPoint` |
| `0x20` | `MPR::RSMPoint` (0x40 bytes) |
| `0x60` | válido de `MprIf::PlayMovieCtrl` |
| `0x64` | `MprIf::PlayMovieCtrl` (incluye flags en +0x24/+0x25/+0x26) |

Despachador, `case 0x4000001D` (pseudocódigo REA, `FUN_00439C38`):

```c
puVar2 = FUN_004397a2(param_1);                       // payload
puVar3 = (*(char *)(puVar2 + 7)  != 0) ? puVar2 + 8  : 0;   // +0x1C → +0x20 RSMPoint*
puVar7 = (*(char *)(puVar2 + 0x18) != 0) ? puVar2 + 0x19 : 0; // +0x60 → +0x64 PlayMovieCtrl*
FUN_00447bc0(core, payload[0], payload[1], ..., puVar3, puVar7);
```

## 2. `FUN_00437BC0`: los dos guardas que producen 0x1A (VERIFICADO)

Pseudocódigo REA (`FUN_00447BC0`, extracto literal):

```c
if (core[0x7c] == 5) {                       // [core+0x1F0] == 5  (estado)
  if (ctrl != NULL) {
    if (FUN_00457a1e(core[0x7b], core[0x370], core[0x36e]) == 0) {   // guarda A
      FUN_00722938(core[2], " Pb Disable!! ref) dsm get", 1);
      status = 0x1a;                                                  //  ← 0x1A
    } else if (FUN_00457f26(core[0x7b], core[0x370], ...) == 0) {     // guarda B
      FUN_00722938(core[2], " Detect UnSupported Content ", 1);
      status = 0x1a;                                                  //  ← 0x1A
      if (ctrl[0x24]) { FUN_00457ee2(...); FUN_00722938(..., " ResumeInfo is updated "); }
    } else {
      if (FUN_00457da8(core[0x7b], core[0x370]) == 0) {               // previo al motor
        r = FUN_00317f54(core[0x365], ..., ctrl);                     // MoviePlayerIf::PbStart
        if (r == 0) return;                                           // éxito: NO finaliza aquí
        status = FUN_007211b0();                                      // último error interno
        FUN_00457dc8(...);
      } else status = FUN_007211b0();
    }
  }
} else status = 0x0a;                                                 // estado ≠ 5

FUN_00722960(core[2], "PlayMovie()", status);
(**(code **)(*core + 0x1c))(core, 0x4000001d, &status, 4);            // finalización → libObj
```

- **Guarda A — `FUN_00447A1E`** (`0x447A1E`): consulta de capacidades. Con la máscara
  `[core+0xDB8]` (`core[0x36e]`), exige `vtable+0x60()` si el bit 0 está puesto y `vtable+0x5C(código)`
  para los bits 2, 4, 8, 0x10, 0x20, 0x80, 0x100 y 0x200. Devuelve 0 si **alguna capacidad exigida está
  deshabilitada**; la entidad se obtiene con `FUN_00447810` → `FUN_0067D0C8(id)` (id `[core+0x1EC]`,
  media `[core+0xDC0]`). El log lo llama «dsm».
- **Guarda B — `FUN_00447F26`** (`0x447F26`): llama al método `vtable+0x58` de la misma entidad con los
  parámetros del `PlayMovieCtrl`; devuelve 0 si el **contenido no está soportado**. Efecto lateral: si
  `ctrl[0x24] != 0`, refresca el punto de reanudación («ResumeInfo is updated»).

## 3. Tercer camino posible hacia 0x1A: la tabla de errores (VERIFICADO, acota la conclusión)

`status` no siempre es literal: en la rama de fallo de `PbStart`, `status = FUN_007211B0()`
(`0x7211B0`, «último error»), que **traduce códigos internos a códigos MPR**. Esa función tiene **seis
sitios que devuelven 0x1A** (p. ej. `0x1C00001A → 0x1A` en `0x711232`), así que el valor observado en
`PlayMovieCmp` **no distingue** entre:

1. guarda A (capacidades/«dsm»),
2. guarda B (contenido no soportado),
3. fallo del motor `MoviePlayerIf::PbStart` cuyo código interno se traduce a 0x1A.

Los tres desembocan en el mismo `vtable+0x1C(0x4000001D, 0x1A)` y en el mismo `PlayMovieCmp` de libObj.
No hay ningún otro emisor de la finalización de esta API en libmpr.

## 4. Qué NO es 0x1A

- No es un timeout, ni falta de RAM, ni error de demux/decoder: `PbStart` ni siquiera se llama si falla
  una guarda.
- Estado del core en la traza: obligatoriamente `5` (si no, el código habría sido `0x0A`, no `0x1A`).
- `0x1A` es genérico (`MPR::ER_FAILED`): libObj lo convierte a `DefObjPlayer::ER_FAILED = 7`.

## 5. Discriminador para la próxima sesión (barato y decisivo)

Tres puntos de un solo uso sobre el manejador (VA ELF; sumar +0x10000 no: son direcciones de ejecución
`base + offset`, y el offset es el del ELF):

| Punto | Offset ELF | Qué prueba |
|---|---:|---|
| `0x437C0A` | tras guarda A | si se ejecuta, ganó la guarda A (además el log «Pb Disable…») |
| `0x437C3C` | tras guarda B | si se ejecuta, ganó la guarda B (log «Detect UnSupported Content») |
| `0x437CFC` | fallo de `PbStart` | si se ejecuta, el 0x1A vino del motor |

Antes de eso, lo más barato: **capturar el log de depuración de MPR** (`testmode_debugPrint`), que ya
contiene las tres cadenas y no necesita parar la CPU.

## 6. Contador `0:02` (parcial: campos localizados, origen sin cerrar)

En libObj, el modelo de reproducción lleva `M_SinglePbBase_Utils` en **modelo+0x90** (el constructor de
`M_SinglePbBase`, `0x432290`, llama a su `dump` con `r0 = modelo+0x90`). Campos, en horas/minutos/segundos
(tres words cada uno, VERIFICADO en el `dump` `0x40E85C`):

| Campo | Offset en utils | VA en el modelo |
|---|---:|---:|
| `m_pbTimeInContent` | `0x60` | `0xF0` |
| `m_pbTimeInTotal` | `0x6C` | `0xFC` |
| **`m_durationOfContent`** | `0x78` | **`0x108`** |
| `m_durationOfTotal` | `0x84` | `0x114` |
| `m_currentFrameInContent` | `0x90` | `0x120` |
| `m_framesOfContent` | `0x98` | `0x128` |

Existe el camino de catálogo: `MprIf::GetMovieContentProperty` (`0x71FC04`, API **`0x41000067`**) devuelve
`MPR::ContentProperty`, cuyo campo `contentsDuration` (ms, con `bContentsDurationValid`) está descrito en
`.rodata` `0xD61D00–0xD62058`; en libObj lo consume el envoltorio `0x7258F8` (llamada PLT `0xDFE30` en
`0x7259C0`), y `GetTotalPbTimeInFolder` se usa en `0x728838`. El vídeo no contiene ningún campo de ~2 s
(medido con ffprobe y parser propio, informe del 25-11).

**Sin cerrar:** qué escribe exactamente `m_durationOfContent` (o si el texto que ve el usuario sale de
`m_pbTimeInContent`, sembrado desde el punto de reanudación). El enlace setter↔catálogo quedó a medias
porque la importación de libObj en REA (17 MB) no terminó en el tiempo de la sesión. No se ha demostrado
que el `0:02` provenga del catálogo; sigue siendo la hipótesis con más apoyo.

## 7. Reproducibilidad

- Nombres y direcciones: tabla `.dynsym` de `libmpr.so` (1576 funciones exportadas) + desensamblado Thumb-2
  con Capstone y PLT resuelta por `.rel.plt`.
- Pseudocódigo: REA/Ghidra sobre la misma SHA-256; extractos en
  [evidence/film-pb-1-20261126](evidence/film-pb-1-20261126/).
- No se ejecutó firmware, no se abrió la cámara y no se tocó ningún binario.
