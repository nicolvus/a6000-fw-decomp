# FILM-PB-1 — Auditoría del CFW instalado frente a la reproducción de vídeo

Fecha: 27-11-2026. Estado: **la causa no está en el código de reproducción**. Falta el
paso físico que decide entre las dos causas que quedan (estado de arranque o
contenido/catálogo). Cámara **no accesible** en esta sesión (ping a `192.168.1.30`
falla, sin dispositivo Sony en USB, `adb` sin dispositivos).

Continúa [el productor del `0x1A`](film-pb-1-productor-mpr-20261126.md) y el
[traspaso físico](film-pb-1-traspaso-20261125.md).

## 1. Qué se ha auditado y con qué

El paquete instalado es `build/cfw_func393/pp/files` (versión 3.93, base 3.38 para el
contenedor; ver `build/cfw_func393-pp.audit.json`). Se ha comparado **byte a byte**
contra el `/usr` de Sony 3.21
(`firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked`).

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Ficheros distintos del paquete | **32**: 5 `.so` + 22 `string_*.uxc` + `MANIFEST.json` + `SHA256SUMS` | [paquete-diferencias.txt](evidence/film-pb-1-20261127/paquete-diferencias.txt) |
| `libmpr.so` en el paquete | **no existe**: el productor del `0x1A` es código de fábrica | ídem |
| `libObj.so` | 41 rangos, **506 B** distintos; 26 rangos en `.text`, 15 fuera | [libobj-rangos.json](evidence/film-pb-1-20261127/libobj-rangos.json) |
| Mapa de errores `0xFD9248` (97 × 16 B) | **idéntico**, incluida la conversión `0x1A → 7` | [verificacion-ruta-reproduccion.txt](evidence/film-pb-1-20261127/verificacion-ruta-reproduccion.txt) |
| Direcciones conocidas de la ruta de reproducción | **ninguna** cae en un rango modificado (margen ±64 B) | ídem |

Direcciones de la ruta de reproducción comprobadas: `0x8C9BAE` (llamada a
`MprIf::PlayMovie`), `0x8CC958` (`EnterMoviePb`), `0x8CCDE0` (conversor de errores),
`0x8E95B0` (`ObjPlayerCore::PlayMovieCmp`), `0x42D5DC` (modelo, `ER_FAILED`),
`0x42F7EC`, `0x41C964`, `0x4310BC`, `0x7258F8` (envoltorio de
`GetMovieContentProperty`), `0x942156`/`0x94A8A4` (`ObjMedia`), `0xFD9248` (mapa).

## 2. Qué son los 506 bytes que sí cambian

Todos los rangos de `.text` caen en los puntos que aplican los parches del proyecto, no
en la reproducción:

| Rango (ELF) | Parche |
|---|---|
| `0x4A784C`, `0x4A7860`, `0x4B4184`, `0x4B42FA–0x4B433A`, `0x4B4390`, `0x4B471C–0x4B4775`, `0x4B477A–0x4B47C4`, `0x4B73DE` | `patch_libobj_ppeco.py` |
| `0x4C0AE2`, `0x4C0B0A`, `0x4C0BE2`, `0x4C0D6C`, `0x4C0E62`, `0x4C0EA2` | `patch_libobj_ppeco.py` (límites y ganchos de Reset de PP) |
| `0x4DB4B6`, `0x4DB4DE` | `patch_libobj_ppeco.py` |
| `0x9B325E–0x9B32C0`, `0x9B36DE–0x9B3744` | `patch_libobj_pp.py` |
| `0x686DE6`, `0x686DEC`, `0x686DFA–0x686E0E` | `patch_libobj_eco.py` / eco de Silent (G111 §13) |

Fuera de `.text`:

- **Cabecera ELF** `0x1C` y `0x2C`: `e_shoff` y `e_shnum`, por la cola añadida.
- **`.data.rel.ro`** (12 palabras en 6 entradas, VA `0xFDF19C…0xFDF564`): son entradas
  de tabla `{marca, puntero de datos}`; la marca pasa de `0x00080004` a `0x000C0004`
  (la tabla crece de 8 a 12 elementos) y el puntero se reapunta a la tabla nueva de la
  cola (`0x01188250` / `0x01188280`, que es **dato**, no código: comprobado con
  Capstone). Es la tabla de descriptores de Picture Profile, no de reproducción.
- **`.dynamic`** `0x1024B6C`: `DT_REL` pasa de `0x365D0` a `0x10E8000`.

Estructura añadida al fichero (de 17 436 172 a 18 127 472 B): dos `PT_LOAD` nuevos,
`0x01149000→0x00FCB000` (2 672 B) y `0x010A8000→0x010E8000` (656 512 B). El segundo
contiene **una copia byte a byte** de los primeros `0xA0248` B del `.rel.dyn` original
(comparada: idéntica) más 39 entradas `R_ARM_GLOB_DAT` nuevas. No se toca ni una
instrucción de `.rel.dyn` ni del mapa de errores.

## 3. Conclusión de la auditoría

1. **El `0x1A` lo produce código de fábrica.** `libmpr.so` no viaja en el paquete y el
   manejador `0x437BC0` de `libmpr` es el original de 3.21.
2. **El CFW no parchea la ruta de reproducción de `libObj`**: ni las llamadas
   `EnterMoviePb`/`PlayMovie`, ni `PlayMovieCmp`, ni el conversor de errores, ni el mapa
   `0x1A→7`, ni `ObjMedia`. Los 506 B son Picture Profile, Silent/EFCS y las tablas de
   descriptores.
3. Por tanto **la causa no es un parche de código**: es entorno (contenido/tarjeta) o
   **estado global de arranque**. Esto retira la línea de trabajo «hay un parche que
   rompe la reproducción» y deja dos hipótesis vivas:
   - **H1 — arranque en frío.** El paquete quita `0700_part_image/dev/nflasha5` (WBI de
     Sony; `tar_quitados_vs_base` del audit). Sin esa instantánea, `ud_wbi_drop`
     (`us_mkfs.sh`) invalida el WBI y Loader3 arranca en frío (`BootMode 1` en vez de
     `11`). Es el **único** cambio global del CFW (G111 §14) y encaja con una guarda de
     capacidades que falla (`Pb Disable!! ref) dsm get`, `0x437C0A`) o con una lectura de
     metadatos incompleta (el `0:02` frente a 9,5095 s reales).
   - **H2 — contenido/catálogo.** El firmware documenta que la base de datos de imágenes
     gobierna la reproducción de películas («Recovers the image database file for movies
     and enables recording and playback»); una entrada obsoleta explicaría a la vez el
     `0:02` y la guarda de contenido no soportado (`0x437C3C`).

## 4. Experimentos, en orden, con su decisión

Cada paso descarta algo concreto; el primero que resuelve, cierra FILM-PB-1.

| # | Acción | Si sale bien | Si sale mal |
|---|---|---|---|
| **E1** | Con la cámara encendida (WiFi o USB): reproducir un clip con el log de `im`/`libmpr` capturado y un breakpoint de un solo uso en `0x437C0A`, `0x437C3C` y `0x437CFC` | Se sabe cuál de los tres productores dispara (`0x437C0A` ⇒ H1; `0x437C3C` ⇒ H2) y se actúa en consecuencia | Sin log ni breakpoint no hay más información estática posible |
| **E2** | Menú → **«Recuperar BD imág.»** (`Recover Image DB`) y volver a reproducir | Cierra H2 sin flashear | H2 pierde peso |
| **E3** | Restaurar el **Sony 3.21 oficial** (con WBI) con `scripts/camera_reflash_fw321.sh` y reproducir | El CFW es la causa (solo cambia el WBI ⇒ confirma H1) | La cámara/tarjeta son la causa y el CFW queda exculpado |
| **E4** | Reconstruir el mismo paquete **conservando `nflasha5`** (`build_package_nflasha15.py` sin `--sin-wbi`) y reproducir | Arreglo definitivo: CFW completo con arranque en caliente | El WBI reinyecta el `/usr` de Sony y el CFW queda inerte (motivo documentado por el que se quita); se descarta esta vía |

E4 es la única vía que puede dar **arreglo** sin renunciar al CFW, pero su riesgo está
documentado: el WBI es una instantánea de RAM con el `/usr` de Sony. E3 es la que
**discrimina** con menos riesgo.

Material ya preparado y verificado para E3:

- DAT oficial: `firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat`,
  212 988 056 B, SHA-256 `29aef21ab9b5c2e98388974ac9749c2cbfb1815273b444e62f2e41398aa8892f`
  (coincide con el que exige el script).
- Script: `scripts/camera_reflash_fw321.sh` (pide confirmación y comprueba el hash antes
  de tocar la cámara).
- Build de control alternativa, por si se prefiere no perder el CFW:
  `build/sony_puro_sin_wbi_404` (Sony 3.21 intacto, sin `nflasha5`).

## 5. Límites

- **NO_VERIFICADO** cuál de los tres productores de `0x1A` dispara: exige cámara (E1).
- **NO_VERIFICADO** que el `0:02` venga del catálogo y no de otra propiedad: el modelo
  (`M_SinglePbBase_Utils`, `m_durationOfContent` en modelo+`0x108`) no se ha podido
  observar en ejecución.
- La auditoría cubre **código**; no cubre estados de NVRAM ni de la base de datos de la
  tarjeta, que solo se leen con la cámara encendida.
