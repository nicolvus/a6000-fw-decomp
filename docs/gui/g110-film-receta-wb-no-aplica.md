# G110 — Film 3.93: por qué la receta no cambia el balance ni A-B/G-M; RecipeLab, JPEGCAM y el PP activo (24-11-2026)

Petición: en el 3.93 los looks no mueven el balance de blancos ni el A-B/G-M, y deberían para parecerse más al look real.
Auditar la vía del CFW, comprobar cómo lo hace RecipeLab y proponer la mejora. Solo estático: nada construido ni instalado.

## 1. Qué hace el CFW (VERIFICADO en código)
- La receta está en todas las builds con Film (`film`, `sin_iso`, `todo`): `scripts/lut/userland/films.c` `receta()`/`pon_val()`.
- Escribe 16 ids con `Backup_write` (`libbackup.so`) desde el hilo userland. Codificación idéntica a RecipeLab (comparada con `Params.writes`/`abSlot`/`gmSlot`/`gmToStore` del APK):
  A-B en `0x1070017` + ranura `0x107067F` (AWB) o `0x1070683` (K); G-M negado en `0x1070016` + `0x107067E`/`0x1070682`; modo `0x1070019`; K/100 en `0x1070018`.
- **No avisa a nadie.** Tras escribir no hay `sync` ni orden al modelo de la cámara. Solo el blob de la LUT tiene un consumidor que lo vigila (el ACK que lee `av-cam`).

## 2. Por qué no se aplica (VERIFICADO en estático; efecto en la cámara: lo que observa el usuario)
- **El Backup solo guarda; no aplica.** En el firmware de fábrica el balance llega a la imagen por
  `WrapperWhiteBalance::setWhiteBalance(ViewBaseProduct*, modo, K, A-B, G-M)` → `WrapperSettingUtil::writeBackup` **y** `ViewBase::requestModelExecute`
  (S77 §3.2). Esa ejecución acaba en `libObj` → `ObjCamera::MSGID_SET_WB_SHIFT_CMD`, `PARAMID_WB_MODE`, `PARAMID_WB_COLOR_TEMP`, `PARAMID_WB_SHIFT_LB/CC`
  (cadenas de `libObj.so`). `av-cam` no tiene WB fotográfico propio (S77 §2).
- La app de cámara lee esos ids del Backup **al arrancar**; mientras corre trabaja con su copia en `libObj`. El hilo escribe en el mismo proceso, con la app viva:
  el valor queda en el Backup, pero ni el menú de balance ni el ISP lo ven.
- Lo mismo vale para estilo, saturación, contraste, nitidez, EV y DRO de la receta: misma vía (`WrapperCreativeStyle::setCreativeStyle` …).
  Lo que sí se ve de un look es la LUT y la curva, que `av-cam` lee directamente.
- G99 §3 ya lo dejó como NO_VERIFICADO («lo seguro es que se aplique al apagar y encender»). El síntoma del 3.93 lo confirma en la práctica.

## 3. Cómo lo hace RecipeLab 1.13.1 (VERIFICADO en el APK, androguard + `llvm-objdump`)
- `MainActivity.writeAll` → `NativeBackup.writeByte` por cada id → **`NativeBackup.sync()`** → `load()` relee lo escrito.
- `librecipelab.so` no enlaza `libbackup.so`: habla con el servicio Backup por `osal_snd_sync_msg`. `sync` es la orden `0xf` (`0x253c`: `movs r0,#0xf` → envío).
- **Clave:** RecipeLab es una app PMCA. Mientras está abierta, la app de cámara de Sony no corre. Al salir, la app de cámara arranca de nuevo y lee el Backup,
  así que el balance, el estilo y el resto entran por la vía normal del §2. RecipeLab nunca escribe con la app de cámara viva.
- Además su receta incluye la fila PP (`0x107031C`) y pide apagar el Picture Profile (`asksPictureProfileOff`), porque con un PP activo el estilo, el contraste y la saturación no cuentan.

## 3 bis. Cómo lo hace JPEGCAM 2.08 (VERIFICADO en el APK, `HardwareRecipeApplier.apply`)
- **Aplica en vivo, no por el Backup:** `Camera.getParameters()` → `set(...)` → `Camera.setParameters()`. Esto pasa por el servicio de cámara,
  que llama a `libObj` igual que el menú: el balance cambia al momento, con la app abierta. Es la vía que le falta al CFW.
- **Orden de la receta:**
  1. `picture-profile` = `off` (si existe), `drive-mode` = `single`;
  2. `creative-style` o `pro-color-mode`; `color-mode` = `standard`;
  3. `picture-effect` = `off` (o el efecto que pida la receta);
  4. balance: `setWhiteBalance` (AWB, daylight, shade, cloudy, incandescent, fluorescent o kelvin por `color-temperture-white-balance`);
     `white-balance-shift-mode` = `true`, `white-balance-shift-lb` / `-cc`;
  5. `contrast`, `saturation`, `sharpness` (+ `sharpness-gain`), `dro-mode`/`dro-level`;
  6. `color-depth-{red,green,blue,cyan,magenta,yellow}`, `rgb-matrix-mode` + `rgb-matrix` (3×3), `lens-correction-shading-color-*`;
  7. curva por `setExtendedGammaTable` (G98 §3).
- **Al salir** (`ExitBehaviorManager`) restaura o conserva los ajustes de balance según la opción del usuario.
- **Conclusión:** JPEGCAM y RecipeLab **apagan los dos el Picture Profile** antes de aplicar un look, y los dos parten de un estilo neutro.

## 4. Otros límites del diseño actual (VERIFICADO en `film_userland.RECIPELAB`)
- 14 de los 38 looks no mueven el balance aunque la vía funcionara: su receta es AWB con A-B = G-M = 0
  (Ektar 100, Provia 100F, Velvia 100, Eterna 250/250D/400/500, Reala 500D y los Fuji Sim Eterna, Eterna BB, Pro Neg, Provia, Reala Ace, Velvia).
  9 usan kelvin fijo (Vision3, 50D, Classic Cinema…).
- La receta no toca el PP. Con la build `pp`/`sin_iso` y un PP activo, estilo, contraste y saturación de la receta no se aplicarían aunque llegaran.

## 4 bis. En qué influye un PP activo sobre un look (VERIFICADO en estático salvo lo marcado)
Las tablas de cada look (LUT 5×9×9 + curva 1D) se ajustaron sobre el **JPEG Estándar**: matriz y gamma de fábrica, sin Color Depth (G98 §6).
Cada ajuste del PP del CFW (`scripts/gui/pp_menu_spec.py`) cambia una etapa de esa cadena:

| Ajuste del PP | Etapa | Efecto con un look activo |
|---|---|---|
| Gamma (Movie, Still, Cine1–4, ITU709, S-Log2/3) | gamma por número (G92 §2) | La curva del look sale `T[gamma_PP[x]]`: cambia todo el tono; con S-Log el look queda irreconocible. |
| Black Gamma Range/Level | `bd1` de la cadena de tono | **Anula la curva del look**: `bd1`/`bd3` excluyen a `bd5` (G92 §3, test Unicorn). |
| Black Level, Knee (los 5) | tono | Se suman a la curva del look y la desplazan. |
| Color Mode (+ Level) | matriz 3×3 (G27) y elección de la tabla de referencia de la LUT (`cfg+0x7e`, G71 §1c) | La LUT corrige una base que ya no es la del ajuste; con B/N o S-Gamut, colores fuera de rango. |
| Color Depth R/G/B/C/M/Y | mismo búfer que la LUT 3D (G71 §1) | **Se pierde**: con un look la LUT sustituye el búfer entero. |
| Saturation, Color Phase | paquete de colorimetría (G69), aplicado en otro procesador | Se suman al look sin modelo (G99 §1). Saturation −8 = B/N. |
| WB Filter Type, WB LB/CC/R/B | desplazamiento de balance por perfil | Se suman al A-B/G-M de la receta. |
| Detail (los 7), Hi-Light Detail | nitidez | No cambian el color; se suman a la nitidez de la receta. |

Además, con un PP activo el estilo creativo, el contraste y la saturación de la receta no cuentan (por eso las dos apps apagan el PP).
Que el estilo quede anulado con PP en la A6000 + CFW: INFERIDO del comportamiento de Sony y de RecipeLab, sin medir.

## 4 ter. Qué debe mandar y qué ponerse en gris
**Regla: Film y PP se excluyen. Con un look activo manda Film.** Es lo que hacen JPEGCAM y RecipeLab, y es lo único que deja el look como se ajustó.
- **Al elegir un look:** la receta pone `Picture Profile = Off` (fila `0x107031C`, como RecipeLab), y al volver a Off lo devuelve con el resto de la copia del usuario.
- **En gris mientras Film ≠ Off** (el look lo fija o lo anula):
  - Picture Profile: selector y todas sus filas, y sus entradas del menú Fn y de la rueda;
  - Estilo creativo: estilo, contraste, saturación y nitidez;
  - DRO / Auto HDR;
  - Efecto de imagen;
  - Color Chrome (G69), si la build lo lleva: escribe en el mismo búfer que la LUT y no tendría efecto;
  - Desplazamiento de balance A-B/G-M (forma parte del look); en los looks con kelvin fijo (Vision3, 50D, Classic Cinema…), también el modo de balance.
- **Libres:** modo de balance en los looks AWB (para la luz de la escena), exposición, EV, ISO, enfoque, calidad. El RAW no lleva el look.
- **Al revés:** con un PP ≠ Off, Film en gris; para usar un look hay que poner el PP en Off.
- **Cómo:** con el mecanismo nativo de inhibición, `isInhOn`, que el CFW ya usa (gancho de `isInhOn` del pid ISO en G108; EFCS en gris con Silent).
  Los wrappers de estilo, balance y ajustes lo exportan: `WrapperCreativeStyle::isInhOn`, `WrapperWhiteBalance::isInhOn`, `WrapperSettingUtil::isInhOn`.
  Basta con devolver «inhibido» cuando el look (`0x1070219`/ACK) ≠ 0. Falta localizar los pids de PP, DRO y Efecto, y probarlo en el arnés.

## 5. Cómo mejorarlo (por orden de preferencia)
1. **Aplicar por la vía de la GUI (recomendada).** El nodo «Film» del menú Fn vive en `viewUnified4.so`, y la rueda en `viewUnified7.so`; las dos ya importan
   `WrapperWhiteBalance::setWhiteBalance` (y `viewUnified4` también `WrapperCreativeStyle::setCreativeStyle`). En el manejador que guarda el look
   (hilo de la GUI, con `ViewBaseProduct*`), llamar a esos setters con los valores de la receta: es lo mismo que hace el usuario al cambiar el balance a mano
   (escribe el Backup, ejecuta el modelo, el menú lo muestra y el ISP lo aplica al momento). El hilo userland se queda solo con la LUT, la curva y la copia de Off.
   Falta: localizar el manejador del nodo Film y la firma exacta de `WRAPPER_WHITE_BALANCE`; probarlo en el arnés (S77 §4: enumerado sin mapear).
2. **Mandar la orden a `libObj` desde el hilo** (`MSGID_SET_WB_SHIFT_CMD` …). Evita la GUI, pero no actualiza el menú y hay que reconstruir el formato
   del mensaje; además corre fuera del hilo de la GUI.
3. **Estilo RecipeLab: escribir + `sync` + reinicio de la app de cámara.** Lo más barato: añadir la llamada de sync de `libbackup` y pedir apagar y encender
   tras elegir el look. Peor uso, y hay que comprobar que la app no vuelve a escribir su copia en RAM al apagarse.
- En las tres: si la LUT ya lleva el color de la película, el desplazamiento de RecipeLab se suma encima (G98 §5). Ajustar la LUT como residuo
  sobre «JPEG Estándar + WB de la receta» (el WB sí se puede modelar, a diferencia de la saturación nativa) y revisar los 14 looks con A-B/G-M = 0.

## 6. Límites
- Estático: no se ha ejecutado nada en la cámara ni en el arnés. Que la app relea el Backup solo al arrancar es INFERIDO del diseño de los wrappers y de RecipeLab.
- Si un apagado y encendido aplica la receta en el 3.93: NO_VERIFICADO (prueba de 1 min para el usuario: elegir Portra 400, apagar, encender y mirar A-B/G-M en Balance).
