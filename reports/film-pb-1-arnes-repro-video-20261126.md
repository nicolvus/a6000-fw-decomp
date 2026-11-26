# FILM-PB-1 — ¿reproduce el arnés QEMU el fallo de reproducción de vídeo? (26-11-2026)

Fecha: **26-11-2026** (reloj del anfitrión 00:22–00:45, −03). Cámara: **no usada** (ni red, USB, `adb` ni flasheo;
solo `qemu-system-arm`). Espacio de direcciones: **VA del ELF** de `libmpr.so` 3.21
(`firmware/extracted/fw321/…/nflasha15_unpacked_unpacked/lib/libmpr.so`; en REA suman `+0x10000`).
Estado: **medido y cerrado para esta pregunta** — el arnés **no** reproduce el fallo y **no puede** decidir qué guarda
lo produce.
Evidencia: [`evidence/claude-pbvid1/`](evidence/claude-pbvid1/) · comandos exactos
[`comando.sh`](evidence/claude-pbvid1/comando.sh) · registro crudo
[`run2-shim.log.gz`](evidence/claude-pbvid1/run2-shim.log.gz) y su extracto
[`run2-shim-extracto.txt`](evidence/claude-pbvid1/run2-shim-extracto.txt).

## 0. Respuesta corta

| Pregunta | Respuesta | Prueba |
|---|---|---|
| ¿Sale «No se puede visualizar.» en el arnés? | **NO** | [`21-run2-reproduccion.png`](evidence/claude-pbvid1/21-run2-reproduccion.png): la pantalla sigue en disparo, con «P» |
| ¿Hay rejilla de miniaturas (con o sin miniatura de vídeo)? | **NO hay rejilla**: la vista `view/INDEX_PLAYBACK` se instancia (id `0x3F`) pero **no produce capa** (`Vo FFFFFFFF`) | [`23-run2-index-playback.png`](evidence/claude-pbvid1/23-run2-index-playback.png) + `run2-shim-extracto.txt` |
| ¿Salen miniaturas de foto (que en la cámara SÍ salen)? | **Tampoco** | misma captura: la pantalla no cambia en absoluto |
| ¿Se ejecuta la cadena de reproducción de `libmpr`? | **NO, ni una vez**: 0 disparos en 5 entradas | `TRACE` total del registro = **1**, y es el control (§3) |
| ¿Se puede armar `TRACEFN2` en `0x437C0A` / `0x437C3C`? | **NO**: no son entradas de función, son instrucciones **dentro** del manejador `0x437BC0` | [`chequeo-trampas.txt`](evidence/claude-pbvid1/chequeo-trampas.txt) |
| ¿Dispara alguna guarda? | **Ninguna**: el manejador que las contiene nunca se ejecuta ⇒ el `0x1A` no llega a construirse | §3 |

**Conclusión en una línea:** en el arnés la tecla Reproducción no abre nada y el índice de medios está vacío, así que
**el `0x1A` no existe**; el arnés no sirve para discriminar guarda A / guarda B sin igualar antes el estado de la cámara
(§4–§5).

## 1. Qué se ejecutó (2 perfiles nuevos, modo `live`)

```sh
PUERTO=8799 scripts/gui/harness/estable.sh pbvid1 live > analysis/gui/g22/harness/live-pbvid1.out 2>&1 &
PUERTO=8801 scripts/gui/harness/estable.sh pbvid2 live > analysis/gui/g22/harness/live-pbvid2.out 2>&1 &
```

- Los dos arranques son **en frío** (primer fotograma a ≈190 s y ≈223 s) con la tarjeta del anfitrión:
  `tarjeta: 3 clip(s) y 3 foto(s) en /home/nicolas/A6000-SD` ([`live-pbvid2.out`](../../analysis/gui/g22/harness/live-pbvid2.out)).
- Perfiles en `analysis/gui/g22/harness/live/{pbvid1,pbvid2}/` (gitignored, no se borra ninguno).
- Conducción con `scripts/gui/harness/e2e_drv.py 8801 …` (`KEYWAIT=2` por lo lento del invitado: 0,5 fps).
- La instrumentación se armó **en caliente** (`E …` por `/linea`), así que no cambió la huella ni hizo falta otro
  arranque en frío.

## 2. Capturas y qué enseña cada una

| Fichero | Contenido |
|---|---|
| [`20-run2-inicio.png`](evidence/claude-pbvid1/20-run2-inicio.png) | pantalla de disparo tras el arranque («P», sin datos) |
| [`22-run2-menu.png`](evidence/claude-pbvid1/22-run2-menu.png) | **menú de la cámara** (pestañas y ajustes en español) — sí funciona |
| [`21-run2-reproduccion.png`](evidence/claude-pbvid1/21-run2-reproduccion.png) | tras pulsar **Reproducción** (`0x1f7`): pantalla idéntica a `20` (nada se abre) |
| [`23-run2-index-playback.png`](evidence/claude-pbvid1/23-run2-index-playback.png) | tras forzar `O view/INDEX_PLAYBACK 0`: idéntica; la vista no dibuja |
| [`24-run2-intro-en-rejilla.png`](evidence/claude-pbvid1/24-run2-intro-en-rejilla.png) | tras `abajo`×2 e `Intro` en esa vista: idéntica (no hay nada que seleccionar) |
| [`25-run2-index-arg3.png`](evidence/claude-pbvid1/25-run2-index-arg3.png) | ídem con `O view/INDEX_PLAYBACK 3` |
| [`04-menu.png`](evidence/claude-pbvid1/04-menu.png) | menú, primera sesión (perfil `pbvid1`) |
| [`run2-shim-extracto.txt`](evidence/claude-pbvid1/run2-shim-extracto.txt) | líneas del shim con las teclas, el armado, la apertura de la vista y el único `TRACE` |

**Huellas** ([`huellas-sha256.txt`](evidence/claude-pbvid1/huellas-sha256.txt)): las 17 capturas del intento —inicio, tras Reproducción, tras forzar la vista (args `0` y `3`), tras `abajo`×2 e `Intro`— son **el mismo PNG** `977cf37a…`, y las dos del menú son `8c5b639e…`. Es decir: la pantalla **no cambió ni un píxel** en ningún intento de reproducir.

Tramo decisivo del extracto (`wa` = pared, `g` = reloj del invitado; `LOGMARK` reenvía el registro de `libObj`):

```
320.99 249.27 TRACELIB libmpr.so base 0xadaab000: TRACEFN2 armadas en caliente (5)
329.90 258.18 tecla 0x1f7                       ← la tecla Reproducción LLEGA al invitado
387.24 315.51 B Vn 03F_viewUnified3.so           ← INDEX_PLAYBACK se instancia…
387.26 315.53 B Vo FFFFFFFF                      ← …y no produce capa ni layout
387.26 315.54 B Vo 0000003B                      ← se abre view/CAUTION (id 0x11) y se cierra
389.29 317.57 B Vd 011_viewUnified2.so
447.93        TRACE 125104 n=1 …                 ← ÚNICO disparo: el control de §3
```

## 3. Instrumentación: qué se armó, prueba de que dispara, y 0 disparos en la ruta

`0x437C0A` y `0x437C3C` **no son entradas de función**: son las instrucciones «tras la guarda A» y «tras la guarda B»
dentro del manejador `0x437BC0` ([productor-mpr §2 y §5](film-pb-1-productor-mpr-20261126.md)). Lo confirma la
herramienta del arnés:

```
0x437c0a NO  llamadores=0 punteros=0 previo=0xfe97 prologo=no
0x437c3c NO  llamadores=0 punteros=0 previo=0xfe7e prologo=no
0x437bc0 ENTRADA llamadores=1 — bl desde 0x42a37a
```

Con `TRACEREP=1` la trampa es repetible **sólo en entradas de función** (UDF en la instrucción siguiente); armarla en
`0x437C0A`/`0x437C3C` mataría `im.elf` (`IMEXIT 139`, §3 del informe del arnés). Por eso se instrumentó **la entrada
del manejador que las contiene** y las demás entradas de la ruta:

```sh
E TRACELIB=libmpr.so ; E TRACEREP=1 ; E TRACEDEREF=d0:0:7
E TRACEFN2=437bc0,6e8430,7229e0,44ee9c,61a8f0
#  → «TRACELIB libmpr.so base 0xadaab000: TRACEFN2 armadas en caliente (5)»
```

| VA (ELF) | Qué es | Disparos |
|---|---|---:|
| `0x437BC0` | manejador de PlayMovie: **contiene las dos guardas** `0x437C0A` / `0x437C3C` | **0** |
| `0x6E8430` | `Mp4IfoIf::GetPlayThumbnailInfo` (miniatura / `0xB0100002`) | **0** |
| `0x7229E0` | `MprIf::PlayMovie` | **0** |
| `0x44EE9C` | `FeaIf::PlayMovie` | **0** |
| `0x61A8F0` | `isSupportContent` (guarda B) | **0** |

Intentos hechos **con las trampas armadas**: tecla Reproducción `0x1f7` (×2), `O view/INDEX_PLAYBACK 0` y `… 3`,
`abajo`×2, `Intro`. Recuento total en todo el registro: **1** `TRACE`, que es el control.

**Control (prueba de que el mecanismo dispara en este invitado)** — se arma una entrada conocida y se llama con `F`:
`E TRACELIB=libObj.so`, `E TRACEFN2=125104`, `F 125104` → `TRACE 125104 n=1 r0=0 r1=0 r2=0 r3=0 lr=b6ec6f04`.
Es decir: las trampas **funcionaban** y, aun así, la ruta de reproducción **nunca se ejecutó**.

## 4. Por qué no reproduce (diferencia con la cámara)

| En la cámara | En el arnés | Fuente |
|---|---|---|
| Reproducción abre la rejilla; las **fotos** muestran miniatura y los **vídeos** no | Reproducción **no abre nada**; forzada, la vista no dibuja (`Vo FFFFFFFF`); no hay miniaturas de nada | §2, §3 de este informe |
| El clip está en la lista y al pulsar Play sale «No se puede visualizar.» (`0x1A`) | no hay lista ni modelo con contenido ⇒ no hay orden `0x4000001D` ni manejador | `0x437BC0` = 0 disparos |
| `0x1A` lo produce la guarda A o la B dentro de `0x437BC0` | el manejador no se ejecuta: **el `0x1A` no existe** | §3 |
| El índice AV (`AVF_INFO\AVIN0001.INP` + `MP_ROOT\…MP4`) se lee del volumen | el índice está vacío: `GetAVIndexContentInfoList`/`GetIndexFilteringInfo` con **0 llamadas** y `0x6E8430` con **0 ejecuciones** | [sub-arnés-galeria §0](film-pb-1-sub-arnes-galeria-20261126.md), [sub-arnés §1 y §3](film-pb-1-sub-arnes-20261127.md) y hoy `0x6E8430` = 0 |
| La tarjeta se monta y el MPR la lee | el shim sirve la tarjeta a `libObj`, no a `MprFileIf` (`FindFirst` `0x13E496` falla, `0x2109`) | [sub-arnés §2 P1–P2](film-pb-1-sub-arnes-20261127.md) |

Detalle que importa: el síntoma **discriminante** del usuario (fotos con miniatura / vídeos sin ella) exige que la
rejilla se dibuje. En el arnés no se dibuja, así que **el arnés no puede reproducir ese par de síntomas ni por
casualidad ni forzando la vista**.

**Medida hermana, misma noche** ([sub-arnés-lista-contenidos §0 y §3](film-pb-1-sub-arnes-lista-contenidos-20261126.md),
perfil `lc1`, 00:14–00:35): abriendo la galería *por el camino normal* la vista sí generó capa y layout
(`Vo 00000017` + `Lc Layer`/`Lc Layout`, **sin** cautela), pero `PrmCntInfoList::add` = **0**, `0x3F684` = **0** y **0**
en los cuatro goznes del MPR y en `libInfraScalarMpr`/`libIMDB` (ambas mapeadas): la lista sigue vacía y la pantalla
uniforme. En mi `pbvid2` la apertura **forzada** dio `Vo FFFFFFFF` + cautela `011`; la diferencia entre `00000017` y
`FFFFFFFF` **no está explicada** (candidatos: apertura forzada vs. la del evento de modo, y el instante del arranque),
pero en las dos el resultado que importa es el mismo: **cero entradas y cero miniaturas**.
Mi medida es complementaria: ellos midieron el gozne de **listar** (`MprIf::GetAVIndexContentInfoList` `0x7203C0`,
0 disparos); yo, el manejador de **reproducir** (`0x437BC0`, 0 disparos).

## 5. Qué haría falta para igualar el estado de la cámara

1. **P1 tarjeta**: que `MprFileIf`/`FindFirst` vean el volumen (`/dev/mmca` FAT32) y no sólo `libObj`; hoy
   `FindFirst("ms:/AVF_INFO")` devuelve `0x2109` ([§5.51](../docs/gui/g22-avcam-puente.md)).
2. **P2 índice**: un `AVF_INFO\AVIN0001.INP` legible por `libmpr` (registro no invertido) o dejar que lo reconstruya
   (`scripts/mp4_set_framerate.py` no hace falta para esto; basta el `.INP`).
3. **P3 modelo con contenido**: que `modelIndexPb`/`ModelMedia` reciba la lista y la publique a la vista (hoy nadie
   pide la lista).
4. **P4 vista**: que `view/INDEX_PLAYBACK` produzca capa (`Vo` ≠ `FFFFFFFF`) y la acción de Play llame a
   `MprIf::PlayMovie` `0x7229E0` → `0x4000001D` → `0x437BC0`.

Con P1–P4 hechos, la medida que decide es la de este informe: `TRACEFN2=437bc0` con `TRACEDEREF` daría los valores de
entrada y, si el `0x1A` sale, el log del invitado diría cuál de las dos guardas ganó («Pb Disable…» o «Detect
UnSupported Content») — pero eso ya no sería el estado de la cámara, sería el del arnés.

## 6. Límites

- **No se ha tocado la cámara**, ni NVRAM, ni firmware, ni la tarjeta del usuario (sólo lectura de `$HOME/A6000-SD`
  por el arnés).
- El arnés **no** prueba qué guarda dispara en la cámara: prueba que **allí no dispara ninguna** porque la cadena no
  corre. Cualquier lectura del tipo «en el arnés no falla, luego el fallo es X» es inválida con estos datos.
- Fuera de alcance: por qué la vista no produce capa (ya documentado en
  [sub-arnés-ui-playback §0](film-pb-1-sub-arnes-ui-playback-20261126.md)) y el estado del mutex de `mp4Ifo`
  (ya cubierto en [fallo-global-pb §9](film-pb-1-fallo-global-pb-20261126.md)).
- Una trampa accidental en un desplazamiento **impar** (`viewManagerIf::openView`, `0x1251fd`) corrompió una
  instrucción en el primer perfil (`pbvid1`) y dejó al invitado sin procesar líneas nuevas; se repitió todo en
  `pbvid2` (las conclusiones de §3 son de `pbvid2`). Regla: `TRACEFN2` sólo con entradas de función **pares**,
  comprobadas con `scripts/gui/harness/chequea_trampas.py`.
