# FILM-PB-1 — ¿puede el arnés reproducir sin cámara el fallo de reproducción? (27-11-2026)

Estado: **veredicto + escenario mínimo montado y ejecutado**. Cámara no accesible (sin red, USB ni `adb`);
nada flasheado ni conectado. No se ha modificado `docs/`, `knowledge/`, `build/` ni código existente.
**Espacio de direcciones: VA del ELF** de `libmpr.so` 3.21 (base 0; *REA = ELF + 0x10000*). Andamio,
pruebas y transcripción: [mpr_pb.py](evidence/film-pb-1-sub-arnes-20261127/mpr_pb.py) ·
[test_manejador_playmovie.py](evidence/film-pb-1-sub-arnes-20261127/test_manejador_playmovie.py) ·
[transcripcion.txt](evidence/film-pb-1-sub-arnes-20261127/transcripcion.txt).

## 1. Qué cubre hoy el arnés en la ruta de reproducción (VERIFICADO)

| Vía | Hasta dónde llega |
|---|---|
| Arnés QEMU (`scripts/gui/harness/live.py`) | Arranca `im.elf` con el `/usr` de fábrica ⇒ libmpr y libObj reales, con `MprCtrl::Init` incluido (`live.py`:66-67). La tecla Reproducción manda `0x1f7` → evento `0x150100f0` y **no hace nada «sin medios»** (`docs/gui/g22-t7-mapa-teclas.md`:92); la tarjeta nunca se monta (G22-E-1g aparcado, `docs/gui/g22-avcam-puente.md` §5.7–5.8). **No llega a `MprIf::PlayMovie`.** |
| Tests Unicorn de `tests/` | Emulan funciones suelas con bytes reales (p. ej. `tests/test_g79_xavcs_tarjeta.py`:15-33 ejecuta `0x942156…0x942202` de libObj con objetos simulados). **Ninguno carga libmpr**: las cuatro menciones a `libmpr` en `tests/*.py` son comparaciones de bytes o cadenas (`tests/test_g81_tcub.py`:30). |
| `scripts/gui/avcam/*`, `tests/test_avcam_*` | Ejecutan `av-cam.bin` (lado cámara de la LIRO VM); no tocan la ruta MPR. |
| Búsqueda de la cadena en `tests/`, `scripts/gui/harness/`, `analysis/gui/` | **0** apariciones de `0x437BC0`, `0x42A354`, `FeaIf::PlayMovie` o `MprIf::PlayMovie` en el código de `tests/`/`scripts/gui/harness/` y en las trazas de `analysis/gui/` (solo las `.so` contienen las cadenas). |

Conclusión de §1: cobertura ejecutable **nula en el código del repo** antes de esta sesión en los cuatro
puntos de la cadena (`MprIf::PlayMovie` `0x7229E0` → `FeaIf::PlayMovie` `0x44EE9C` → despachador, caso en
`0x42A354` → manejador `0x437BC0`). El arnés QEMU los tiene *cargados*, pero no hay rastro de que se ejecuten:
la tecla de reproducción no produce efecto y ninguna traza de `analysis/` contiene la orden `0x4000001D`.

## 2. Hueco exacto para llegar al manejador con un MP4 real en la tarjeta emulada

| Pieza | Estado | Qué falta | Coste |
|---|---|---|---|
| P1 Tarjeta (`/dev/mmca`, FAT32) | `scripts/gui/harness/sd_image.py` + `sd_emu.py` construyen la imagen y el shim sirve lecturas | `ObjMedia`/`ModelMedia` no monta: callback de Front (`FRONTRM`), `KEY_MEDIA_MS` fuera de `InfraInput`, `InfraMediaConfig` sin soportes (`g22-avcam-puente.md` §5.7–5.8). `BKMULTIPTR=1` destapa una caída en `libObj+0x8456b4` | **alto y abierto** (G22-E-1g, sin fecha) |
| P2 Catálogo AV | `AVF_INFO\AVIN0001.INP` + `MP_ROOT\100ANV01\MAH0xxxx.MP4` identificados ([sub-tarjeta](film-pb-1-sub-tarjeta-20261127.md) §1–2) | escribir un `.INP` válido (registro **no invertido**) o dejar que libmpr lo reconstruya; el shim hoy sirve a libObj, no a `MprFileIf` (`FindFirst`, `0x13E496`) | medio (formato) + alto (fsys de libmpr) |
| P3 Modelo y API | `MprIf::PlayMovie` se llama desde libObj con `MPR::EntryId` | hace falta el modelo de reproducción con un contenido y la acción de la vista | medio |
| P4 Vista de reproducción | tecla mapeada, vista existente | listar el clip y disparar Play (nunca verificado; «sin medios») | medio |
| P5 Motor/decodificador | `MoviePlayerIf::PbStart` `0x307F54`, DMM `OpenUnit` con `ERR_DMM_RET_CODE 1026/402` (§5.7) | **no hace falta para el fallo**: las dos guardas van antes de `PbStart`. Sí para distinguir «reproduce» de «falla» | no bloquea |

P1 y P4 son incógnitas abiertas, no tareas medidas: **no es viable en una sesión** (ni acotable sin la cámara).

## 3. Veredicto

- **Reproducir el fallo con un MP4 real dentro del arnés: NO viable.** Falta P1–P4; además **no hay ningún
  MP4 en el repo** (`find` por `*.mp4`: 0; de MAH04198 solo hay metadatos en
  `reports/evidence/film-pb-1-20261125/`). Y aunque se cerrara, el veredicto de las guardas lo daría la
  cámara: el andamio no decide la causa.
- **Reproducir el mecanismo a nivel de manejador: SÍ, y está montado** (§4). Distingue los tres productores
  de `0x1A` y verifica por ejecución la tabla de puntos de un solo uso de [§5 del informe del 26-11](film-pb-1-productor-mpr-20261126.md).

## 4. Escenario montado

`evidence/…/mpr_pb.py`: cargador ELF32 propio (PT_LOAD + 934 `JUMP_SLOT`/`GLOB_DAT` + 2 580 `ABS32`;
`R_ARM_RELATIVE` no necesita nada con base 0), `FeaCore` y entidad «dsm» falsos, y ejecución del **código
real** de `0x437BC0` → `0x447A1E` → `0x447810` → `0x447F26` → `0x447DA8` → `0x7111B0` → `0x307F54`.
Se sustituyen parcheando su primera instrucción: `0x66D0C8` (entidad), `0x712938`/`0x712960` (logs),
`0x447DC8`, `0x447EE2`, `0x12111C` (copia del `RSMPoint`) y el retorno del motor; el traductor `0x7111B0`
se ejecuta entero. Parchear —y no saltar la llamada con un hook— es obligatorio: Unicorn 2.1.4 pierde el
estado del bloque `IT` de Thumb cuando un hook reescribe `PC`. La finalización se captura dejando sin mapear
`0x50000010` (4 bytes, orden `0x4000001D`).

Transcripción (`.venv/bin/python reports/evidence/film-pb-1-sub-arnes-20261127/mpr_pb.py`):

| Escenario | Punto de un solo uso ejecutado | Finalización |
|---|---|---|
| `[core+0x1F0] = 0` | ninguno | `0x4000001D`, tamaño 4, status **`0x0A`** |
| capacidad `vtable+0x60` = 0 | **`0x437C0A`** | status **`0x1A`** |
| contenido `vtable+0x58` = 0 | **`0x437C3C`** | status **`0x1A`** |
| `PbStart` = `0x1C00001A` (traductor real) | **`0x437CFC`** | status **`0x1A`** |
| todo en orden | ninguno | **sin finalización** (el manejador retorna) |

- Los tres puntos discriminan **exactamente** una rama cada uno: ninguno se ejecuta en otro escenario.
  Es la tabla §5 del [informe del productor](film-pb-1-productor-mpr-20261126.md) verificada por ejecución.
- `FUN_007211B0` se ejecuta de verdad: `0x1C00001A → 0x1A`, coherente con [sub-motor](film-pb-1-sub-motor-20261127.md).
- El mensaje lo arma también código real: `FeaIf::PlayMovie` (`0x44EE9C`) produce **140 B (`0x8C`)**:
  `+0x00` parámetro del API (`0x2A`), `+0x04` `EntryId` **público** (convertido por `MprCnv::ConvertMprToPubEntryId`,
  `0x711A4C`), `+0x1C` válido de `RSMPoint` = 1, `+0x20` `RSMPoint` (0x40), `+0x60` válido de `PlayMovieCtrl` = 1,
  `+0x64` el control (campos en `+0x64/+0x68`, flags en `+0x88/+0x89/+0x8A`). El manejador consume ese mensaje
  y finaliza igual. **Matiz sobre el traspaso**: `+0x00` es el parámetro del API (el `r1` de la llamada), no
  el `EntryId`; el que llega al manejador es el **convertido** (8 B) en `+0x04` (INFERENCIA que el `EntryId`
  nativo ocupe 16 B: ocupa `r2,r3` más dos palabras de pila, ver §4).

## 5. Qué NO queda verificado

- **Qué guarda salta en la cámara con MAH04198: NO_VERIFICADO.** Las tres respuestas de las guardas son
  inyectadas (entidad falsa); el andamio demuestra el mecanismo, no la causa.
- **NO_VERIFICADO** el contenido del `EntryId` convertido (se sustituye `0x711A4C`) y el `RSMPoint` copiado
  (se sustituye `0x12111C`): solo se comprueba su byte de validez.
- **NO_VERIFICADO** el enlace `MprIf::PlayMovie` → cola: se ejecuta el consumidor (`FeaIf::PlayMovie`) con una
  cola simulada; el despachador real (`0x42A354`) se replica con los mismos argumentos leídos de su
  desensamblado, no se ejecuta.
- **NO_VERIFICADO** nada contra el arnés QEMU: en esta sesión no se ha arrancado `im.elf`.
- Pruebas: `reports/evidence/film-pb-1-sub-arnes-20261127/test_manejador_playmovie.py`, **8 pasan** en menos de 1 s
  (`.venv/bin/python -m pytest reports/evidence/film-pb-1-sub-arnes-20261127 -q`); no se ha añadido nada a
  `tests/`, así que la suite del repo no cambia. Se omiten solas si falta `unicorn` o `libmpr.so`.
