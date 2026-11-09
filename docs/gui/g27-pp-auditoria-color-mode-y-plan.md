# G27 — Picture Profile: auditoría de G23–G26, Color Mode en el núcleo y plan de cierre (09-11-2026)

Continúa [G26](g26-slog3-color-mode-a6300.md). **Offline**: nada instalado ni probado en cámara. Herramientas: REA (sesiones `a6k` y `a7sb`), capstone, Unicorn.
Corrige G26 §3, §6 y §6.2 (ruta del tipo de Color Mode) y G24 §6 (Saturation −32…+32, Copy).

## 1. Auditoría de lo hecho (G23–G26)

| Pieza | Comprobación | Resultado |
|---|---|---|
| Tests PP (`test_g23_*`, `test_g25_*`, `test_g26_*`) | ejecutados enteros | 24 pasan antes de los cambios; 26 después (2 nuevos) |
| `build_pp_menu.py` de punta a punta | paquete base y paquete con `--gamma-slog --color-gamut --copy-reset` | los dos se construyen (25 idiomas, 31 / 33 ajustes) |
| Gamma (10 opciones, S-Log2/3, ITU709(800%)) | `libObj` con Unicorn, curvas y selector emulados | correcto; sin cambios |
| **Copy / Reset en el menú por defecto** | el menú los llevaba siempre, pero la `libObj` sin `patch_actions` manda los eventos `0x41`/`0x42` al error `0x4d02b8` | **DEFECTO, corregido**: sin `--copy-reset` el menú ya no los incluye (`build_pp_menu.sin_acciones`, test nuevo) |
| **Color Mode B&W/S-Gamut «sin efecto o indefinido»** (G26 §3) | ruta real en el núcleo (§2) | **corregido**: no es indefinido, el núcleo los trata como Movie; B&W pasa a tener efecto (§3) |
| **Ruta del tipo en el núcleo** (G26 §6/§6.2: «bytes `0x133…0x144` → bloque `+0x740`») | esos desplazamientos son de otra estructura (el bloque de registros YC), no del `cfg` | **ERROR de G26, corregido** en §2 |
| **`--saturacion-a6300` (−32…+32)** | el núcleo toma toda saturación < −7 como blanco y negro (§2) | **no equivale a la A6300**: de −8 a −32 todo sale monocromo; se deja opt-in con el aviso en el código |
| G26 §3 (orden de B&W/S-Gamut) | el texto decía 9 = B&W, 8 = S-Gamut; código y tests usan 8 = B&W, 9 = S-Gamut (A7S) | texto corregido |
| `job_EC_CalcCaptureGamma` (A7S `0x437db3c0`) | ya estaba en G16 §1: solo metadatos | la «vía del conjunto de ajuste 9/10» de la sesión anterior queda descartada |

## 2. Cómo aplica el núcleo el Color Mode (VERIFICADO con bytes y decompilación)

| Paso | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| `cfg` global (lo escribe el desempaquetador del `0x4066`) | `0x43edf684`; tipo `+0x138`, nivel `+0x13c`, saturación `+0x14e`, fase `+0x14f`, Color Depth `+0x148…+0x14d`, gamma `+0x153` | tipo `+0x144`, nivel `+0x148` |
| Resumen de ajustes (`FUN_437aa65c` / A7S `0x4383f6e0`): byte `+0x22` = **id de modo de color** | `0x437aa808`: `cmp #6` y tabla de **7** bytes en `0x43ca66f2` → tipos 1–7 = `0x0f…0x15`; tipo 0 o > 7 → Creative Style o 0 | `cmp #8` y tabla de **9** en `0x43cb5405`: además **8 → `0x17` (B&W), 9 → `0x16` (S-Gamut)** |
| Mismo resumen | `+0x23` nivel, `+0x24` saturación (PP + Creative Style), `+0x25` fase, `+0x2a…+0x2f` Color Depth, `+0x30` selector de gamma, `+0x31` tipo | igual |
| `switch` por id (`FUN_437a4cd4` / A7S `0x43839f48`) → índices de conjunto (`+0x7a` matriz, `+0x7b`, `+0x7c`, `+0x81` mono/sepia) | `0x0f`/`0x15` → (8, 7, 4) · `0x10` → (8, 7, 5) · `0x11` → (6, 7, 7) · `0x12` → (7, 7, 6) · `0x13` → (6, 7, `0xff`) · `0x14` → (0, 7, 0) · id 0 → igual que `0x13` | igual, más **`0x17` = mismo caso que `0x13` (Movie)** y **`0x16` → (`0x10`, `0x19`, `0xff`)** |
| Indicador monocromo (`ctx[2]+0x88`) | `0x437a273c`: bit 1 de `caps[3]` **y saturación < −7** | `0x438c3b9c`: lo anterior (umbral de tabla) **o id == `0x17`** |
| EXIF (`0xb020`/`0xb029`, nombres «Vivid…BW…») | ids 1–14 | además `0x17` → «BW» |

Consecuencias:

- Los cinco Color Mode que ya tenía el menú (Movie, Still, Cinema, Pro, ITU709 Matrix) llegan a casos propios del `switch` y eligen conjuntos distintos: **el núcleo de la A6000 los aplica** (la imagen en cámara sigue sin probar). Esto resuelve G17 §2.2 para Color Mode; saturación, fase y Color Depth entran en el mismo resumen, pero su consumidor no se ha seguido.
- Un tipo 8–11 acaba como id 0 y se procesa **igual que Movie**. Nada indefinido.
- En la A7S, B&W es «matriz de Movie + indicador monocromo». La A6000 pone ese indicador con **saturación −8** (el «−8: blanco y negro» de los Picture Profile antiguos de Sony).
- S-Gamut usa en la A7S los conjuntos `0x10`/`0x19`. La A6000 solo llega a `0x0f`/`0x18`: faltan código y datos.

## 3. Hecho — B&W con efecto en imagen

`patch_libobj_pp.patch_bw` (20 B en el hueco que deja `patch_color`, `0x9b328c`; lo aplica `--color-gamut`): al escribir la saturación en el `0x4066` (`0x9b35a2`), si el tipo es B&W (8) envía **tipo 5 (Movie) y saturación −8**. El núcleo queda como en la A7S: caso Movie del `switch` más indicador monocromo. El ajuste Saturation guardado no cambia; solo cambia el mensaje.
Test Unicorn `test_bw_envia_movie_y_saturacion_menos_8`: B&W → (5, `0xf8`); los demás tipos y saturaciones pasan intactos; sin `patch_color` el parche se niega.

**NO verificado**: el valor en ejecución de `caps[3]` bit 1 (`0x43e964a7`, se rellena al arrancar; en la A7S el camino B&W no lo exige), y la imagen en cámara. Si el bit fuera 0, B&W sería «saturación mínima» sin el indicador.

## 4. Lo que falta y plan

| # | Tarea | Qué hay que hacer | Verificación | Estado |
|---|---|---|---|---|
| 1 | **S-Gamut** (A7S) | **CERRADO como «igual que Movie» (§5)**: los datos de S-Gamut en la A7S son la matriz de Movie y un conjunto de deltas a cero | — | cerrado |
| 2 | **S-Gamut3 / S-Gamut3.Cine** (solo A6300) | lo mismo sobre el `av-cam` de la A6300, cuyo `cfg` tiene otro diseño (G26 §6.1) | ídem | pendiente, depende de 1 |
| 3 | **Color Mode Level** (byte 9 → `+0x23`) | el núcleo ya lo lleva en el resumen; falta un ajuste de menú (clave `0x1fc`) si se quiere exponer; la A6300 no lo expone | test de descriptor | opcional |
| 4 | **Reset**: id `0x42` inferido | confirmar que la capa de modelo entrega `0x41`/`0x42` al despachador | arnés de la UI (G22-B) o cámara | pendiente |
| 5 | **Gamma Disp. Assist** | conversión del visor (LUT), sin `PARAMID` en ninguna `libObj` | — | fuera de alcance solo-datos |
| 6 | **Metadatos de gamma de captura** (`job_EC_CalcCaptureGamma`) | código de ~0x9e B que la A6000 no tiene; solo etiqueta el vídeo | — | opcional |
| 7 | **Prueba en cámara** (requiere autorización expresa) | paquete `nflasha15` + `pp_ram.sh`; por orden: menú visible → un ajuste numérico → Gamma Cine → S-Log2/3 → Color Mode → B&W → Copy/Reset → persistencia | lista de comprobación por ajuste | bloqueada por autorización |
| 8 | Integración | combinar con Silent/3.56 (mismas páginas y `CautionConfig`), empaquetar `pp_ram.sh` en el CFW, ProcessIds `0x55–0x5b` | auditoría del paquete (G11) | pendiente |

Orden recomendado: 7 con lo que ya hay (es lo único que valida todo lo anterior), después 1 (c) con las dos sesiones REA, y 4 en el arnés.

## 5. S-Gamut en la A7S: qué lleva realmente (VERIFICADO con bytes)

- Las matrices y los conjuntos de deltas **no están en el `av-cam`**: viven en la propiedad de Backup `0x30001` (0x600 B, NVRAM; preset `CX77500_*.bin` / `CX78500_*.bin`). Las dos funciones de búsqueda son `0x437a4b40` (matriz: índices 0–7 en `+0x48`, 8–0xe en `+0x400`, 0xf en `+0x310`; A7S añade 0x10 en `+0x322`) y `0x437a44d0` (deltas de 24 B: 0–0xd en `+0x100`, 0xe–0x17 en `+0x480`, 0x18 en `+0x390`; A7S admite 0x19 en `+0x588`).
- En la A7S, S-Gamut (id `0x16`) usa la matriz índice `0x10` = **(1292, −180, −88, −44, 1340, −272, −24, −108, 1156), idéntica a la de Movie de la A6000** (índices 0, 6, 7 y 8), y el conjunto `0x19` = **24 ceros** (sin deltas).
- Por tanto, en esta ruta S-Gamut = Movie. La diferencia visible de S-Gamut procede de la gamma (S-Log2/3, ya portada) y no de este bloque. El tratamiento actual (tipo 8–11 → Movie) es **equivalente en datos**; no hace falta código del núcleo ni escribir NVRAM.
- La A6300 sí tiene matrices propias para S-Gamut3 (índices 0xf/0x10/0x13/0x14, `+0x590`, `+0x5c0`), pero ni el `av-cam` de la A6000 llega a esos índices ni su NVRAM los trae: portarlos exige código del núcleo y escribir la propiedad `0x30001` (fuera de alcance sin autorización). S-Gamut3/S-Gamut3.Cine quedan como «Movie» en la A6000.
- Backup de la cámara real (`20261105-volcado-total-nvram`) = preset de la A6000 en `0x30000/0x30001`; el bit de capacidades de monocromo (`caps[3]` bit 1) es **0** (G27 §3): B&W puede no activar el indicador. Pendiente de cámara.
