# FILM-PB-1 · Parche de las dos guardas de `PlayMovie` (`FUN_00437BC0`)

26-11-2026 (sesión offline del 25-11-2026 22:11 UTC). **Espacio: VA de ELF de `libmpr.so` 3.21**, en
`.text` la VA **es** el offset de fichero (`.text` addr == off == `0x120228`).
Original de fábrica (intacto): `9a74a3bb…4c30`. Copia parcheada: **`build/cfw_bypass_guardas/libmpr.so`**,
sha256 `63dfaed5…2e1578`. Nada se ha escrito dentro de `firmware/`.

## 1. Qué se ha hecho y por qué

Hecho nuevo del usuario: **un clip grabado por la propia cámara también da «No se puede visualizar»** y
«Recuperar BD imag.» no lo arregla ⇒ la hipótesis de cadencia (`isSupportContent`) queda descartada y el
fallo es global. Por eso el parche ya no se limita a la comparación TvSystem: **anula las dos guardas**
que el manejador `PlayMovie` (`0x437BC0`, opcode `0x4000001D`) evalúa en serie antes de arrancar el motor.

| # | Guarda | VA de la llamada | Qué decide |
|---|---|---|---|
| A | `FeaCore` → `AviMMgr` capacidades | `0x437BFA` `bl 0x447A1E` | `GetPlayMovieStatus(6)` + `GetInhInfo` + estado del motor |
| B | `AviMMgr::isSupportContent` | `0x437C2C` `bl 0x447F26` | miniatura/indexado + `frameRate` vs `TvSystem()` |

## 2. El parche, byte a byte

| VA = offset | antes | después | instrucción resultante |
|---|---|---|---|
| `0x437BFA` | `0f f0 10 ff` | `01 20 00 bf` | `movs r0,#1` ; `nop` (antes `bl 0x447A1E`) |
| `0x437C2C` | `10 f0 7b f9` | `01 20 00 bf` | `movs r0,#1` ; `nop` (antes `bl 0x447F26`) |

Comprobaciones de forma:
- `0x437BFE` = **`38 b9`** (`cbnz r0, #0x437C10`) y `0x437C30` = **`f0 b9`** (`cbnz r0, #0x437C70`): los dos
  saltos quedan **intactos** y con `r0=1` toman el camino bueno (verificado byte a byte y desensamblado).
- **Alineación**: `0x437BFA` y `0x437C2C` son múltiplos de 2 (Thumb-2 sólo exige semipalabra) y las dos
  instrucciones nuevas suman exactamente los 4 B de la `bl` ⇒ no se desplaza ninguna instrucción vecina.
- **Tamaño**: 10 321 204 B antes y después.
- **Registros**: las dos llamadas se comían `r0..r3` de argumentos; éstos se recargan justo después
  (`0x437C10`–`0x437C28` para B y `0x437C70`–`0x437C74` para A), así que dejar `r0=1` no rompe nada.
- Flujo final: `0x437BFA movs r0,#1` → `0x437BFE cbnz` → `0x437C10` … `0x437C2C movs r0,#1` →
  `0x437C30 cbnz` → `0x437C70` → `bl 0x447DA8` → `AviMMgr+0xB4 = MovieReadStart 0x608698`.

## 3. Verificación del resultado

| Comprobación | Resultado | Evidencia |
|---|---|---|
| ELF válido y con las mismas secciones/segmentos (`readelf -hlS --wide`, original vs parcheado) | **diff vacío** (0 líneas, sin warnings): 25 secciones (`readelf -S`) y los 5 `PT_*` (`2 LOAD` + `DYNAMIC` + `GNU_STACK` + `ARM_EXIDX`) idénticos | `readelf-original.txt`, `readelf-parcheado.txt`, `readelf-diff.txt` |
| Cabecera, tabla de segmentos y tabla de secciones | **byte a byte iguales** (aserción del script, no sólo `readelf`) | `parche-guardas-ejecucion.txt` |
| Instrucciones parcheadas | `movs r0,#1 ; nop` en las dos, con los `cbnz` detrás | ídem (desensamblado) |
| Diff byte a byte (`cmp -l`) | **8 bytes** exactos: `0x437BFA..FD` (`0f f0 10 ff`→`01 20 00 bf`) y `0x437C2C..2F` (`10 f0 7b f9`→`01 20 00 bf`) | `diff-bytes.txt` |
| Relocaciones sobre los parches | **ninguna**: 132 021 entradas `.rel/.rela` revisadas, `r_offset` ≠ esos sitios; tampoco hay `R_ARM_RELATIVE`/literal que apunte a ellos | `reloc-sobre-parches.txt`, `parche-guardas-ejecucion.txt` |
| Ramas/punteros que entren en los 4 B parcheados | **ninguna** (`b/bl/cbz/cbnz` con destino en los dos rangos: 0; `u32` iguales a `0x437BFA/Fc/FE/2C/2D/2E/30`: 0) ⇒ no se parte ninguna instrucción destino | `ramas-y-literales.txt` |
| Original no tocado | sha256 `9a74a3bb…4c30` recalculado al final | `SHA256SUMS` |

El script reproducible es `reports/evidence/film-pb-1-sub-bypass-guardas-20261126/parche_guardas.py`
(aborta si cambia el sha del original, si un byte original no casa, si el diff no es exactamente el
previsto, si cambia cualquier cabecera/sección o si aparece una relocación en esos sitios).

## 4. Cómo se incluiría `libmpr.so` en el paquete CFW

- **Ruta**: el overlay del CFW es `pp/files/lib/libmpr.so`; la raíz del ext2 de `nflasha15` **es `/usr`**
  (`scripts/gui/build_nflasha15.py:41`, `dest = "/" + rel  # la raíz del ext2 es /usr`) ⇒ en la cámara queda
  **`/usr/lib/libmpr.so`**. El CFW 3.93 ya construido sigue ese patrón (`build/cfw_func393/pp/files/lib/`).
- **Cadena de scripts** (los tres, en orden):
  1. `scripts/gui/build_cfw_film.py` (o `build_cfw_completo.py`) arma `files/` y escribe
     `MANIFEST.json` (`originales`/`parcheados`/`md5`) y `SHA256SUMS` — líneas 200 y 229–235.
  2. `scripts/gui/build_nflasha15.py` mete los ficheros en el ext2 con `debugfs` (`rm`+`write`, conserva
     modo/uid/gid), `e2fsck -fn`, recompone sólo los bloques TPZL de 64 KiB que cambian y calcula CRC-32
     y tamaño para `part_image.sum`. **La lista de ficheros es `MANIFEST.json["parcheados"]`
     (líneas 71–73)**: si `lib/libmpr.so` no figura ahí, el `.so` **no** se sustituye aunque esté en `files/`.
  3. `scripts/gui/build_package_nflasha15.py` sustituye `0700_part_image/dev/nflasha15` y su línea de
     `part_image.sum` en el tar base (38–39), ejecuta `fwtool pack` (56) y **verifica el resultado**:
     tar extraído == tar construido (62), cada miembro sustituido byte a byte + `sums.verify` (64), firma
     ext2 `0x53EF` en 1080:1082 (65), cabecera FDAT versión/modelo (57–58) y `package_checksums` (69).
- **¿Firma o verifica cada fichero?** **No hay firma por fichero.** `fwtool` no firma (sin `sign`/`rsa`/
  `cert`/`hmac` en `references/fwtool/fwtool/sony/{dat,fdat}.py`): sólo cifra/empaqueta y valida CRC y
  chunks DEND. Lo que se valida es **por partición y por contenedor**: CRC-32+tamaño en `part_image.sum`,
  roundtrip del tar, firma del superbloque ext2 y cabecera FDAT. El `MANIFEST.json`/`SHA256SUMS` del
  overlay son contabilidad del proyecto, no una firma de Sony.
- **Confirmación indirecta**: el CFW 3.93 instalado lleva «32 ficheros distintos del paquete: 5 `.so` + 22
  `string_*.uxc` + `MANIFEST.json` + `SHA256SUMS`» y la cámara arranca
  ([auditoría](film-pb-1-auditoria-cfw-20261127.md) §1) ⇒ `/usr` no comprueba integridad por fichero.
- **Pasos mínimos para publicarlo** (no ejecutados aquí): copiar
  `build/cfw_bypass_guardas/libmpr.so` → `files/lib/libmpr.so`; añadir `lib/libmpr.so` a
  `MANIFEST.json["parcheados"]` con su sha/md5 original y parcheado; `build_nflasha15.py`;
  `build_package_nflasha15.py` con una versión mayor que la instalada (el actualizador sólo acepta
  versiones mayores).

## 5. Riesgos y límites

- **No probado**: ni en cámara ni en emulación; la verificación es estática (bytes, ELF, relocaciones).
- **Puede no arreglar el síntoma**: si el bloqueo real está aguas abajo — `0x447DA8` →
  `MovieReadStart 0x608698` (devuelve `0x31000007` `ER_SEQUENCE` si el motor no está listo) o el propio
  decodificador/visor — el mensaje cambiará de código pero no habrá reproducción. En ese caso el parche
  es además **diagnóstico**: deja de poderse atribuir el `0x1A` a las guardas.
- **Alcance**: sólo se anulan las dos llamadas de `FUN_00437BC0`. `FeaHighlight::PlayHighlightMovie`
  (`0x43570C`), `0x435AB0` y el callback `0x43897E` siguen llamando a la guarda A (`0x447A1E`) y
  conservan su comportamiento.
- **Efectos laterales perdidos**: las trazas « Pb Disable!! ref) dsm get » (`0x85A51C`) y
  « Detect UnSupported Content » (`0x85A7D8`) ya no saldrán por esta ruta, y la guarda A no se ejecuta
  (sólo consultaba estado y logueaba — **NO_VERIFICADO** que no tuviera algún cacheo).
- **NO_VERIFICADO**: que el `0x1A` observado viniera de este manejador (es la hipótesis de partida), el
  estado `[r4+0x1F0]==5` y `r5!=0` en el momento del fallo, y el comportamiento del motor con las
  guardas anuladas.

## 6. Artefactos

- `build/cfw_bypass_guardas/libmpr.so` — copia parcheada, sha256 `63dfaed5a6ebf8e6d9a94a8bf29a5effdb98350cc680d41abf913617a92e1578`.
- `reports/evidence/film-pb-1-sub-bypass-guardas-20261126/`: `parche_guardas.py`,
  `parche-guardas-ejecucion.txt`, `readelf-original.txt`, `readelf-parcheado.txt`, `readelf-diff.txt`,
  `diff-bytes.txt`, `reloc-sobre-parches.txt`, `ramas-y-literales.txt`, `contexto-manejador.txt`,
  `empaquetado.txt`, `SHA256SUMS`.
