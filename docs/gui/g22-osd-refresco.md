# G22-OSD-REFRESCO — que la OSD se repinte sola cuando cambian el modo, la batería/carga y el jack USB

**Estado: PARCIAL (medido).** El **modo** ya se repinta **sin que el anfitrión reabra nada**: al llegar la tecla del dial de modo el propio
invitado vuelve a activar la vista de disparo con el modo que da el firmware (`REDIAL` del shim). La **batería** y el **jack USB** siguen sin
poder cambiar la OSD en el arnés por dos causas distintas y medidas: no hay quien pregunta por el nivel (`0x3001` no tiene consumidor sin
av-cam) y el jack se consulta **al activar la vista** (`execCheck`), no al llegar el mensaje.

Código: `scripts/gui/harness/shim/sonyshim.c` (`redial_on`, `redialhot`, gancho en la rama `K`) y **un hunk de backend** en
`scripts/gui/harness/live.py` (`Vm.gira`). Tests sin QEMU: `tests/test_g22_osd.py` (11 casos) y 3 casos actualizados de
`tests/test_g22_dial.py`/`tests/test_live_shimenv.py`.

## 1. Por qué no bastaba con el evento (estático, bytes del fw 3.21)

Binarios del arnés: `viewUnified2.so` md5 `1adc83954cfad8b17ff2e7199090f923`, `libObj.so` md5 `eb12512e6b74a940f1ae6de1c38477db`
(`analysis/gui/g22/harness/stage/cam/usr/lib`). Direcciones = VA = desplazamiento en el fichero; límites de función de `.ARM.exidx`.

### 1.1 `Event(0x15070050)` (dial de modo) **no tiene manejador**: es una clave de consulta

Los **12** sitios de `viewUnified2.so` que citan `0x15070050` son literales de código, y ninguno es un despachador de eventos:

| Offset | Instrucción | Qué es |
|---|---|---|
| `0x135a80` | `ldr r0,[pc,#8]` (`0x135a7c`, 40 B) | **devuelve** el id: es la consulta, no el manejo |
| `0x19f130`/`0x19f054` | `ldr r1,[pc,#0xd8]` dentro de `CmnViewBigModelUtil::getRecViewFromDial` (`0x19f004`) | clave de `InputService::getInputEventStatus` = **estado del dial** (§5.21 del puente) |
| `0x12b770` | `ldr r3,[pc,#0x1b8]` / `cmp r0,r3` / `beq 0x12c9b4` | switch **id → constante** (`0x12c9b4: ldr r0,[pc,#0x80]; pop {r7,pc}`), dentro de un conversor de 57 656 B (`0x120454`–`0x12e58c`) |
| `0xfdef8`, `0xfec78`, `0x12582a`, `0x17026a`, `0x17332c`, `0x17b8b8`, `0x17c404`, `0x18121e`, `0x181274`, `0x181ff8` | `cmp r0,r3` en cadenas / construcción de `Event` | consultas del estado del dial desde los checkers de `ViewRootPowerSw` y el mismo conversor |

- **`ACT_ExposureMode` es un `dynamic_cast`, no una acción de evento.** `ACT_ExposureMode::cast(Widget*)` — `viewUnified2+0x2b6e2c`, 44 B:
  `0x2b6e38 ldr r3,[r0]` / `0x2b6e3a ldr.w r3,[r3,#0x190]` / `0x2b6e3e blx r3` / `0x2b6e44 cmp r3,r0` / `ite eq; moveq r0,r5; movne r0,#0`
  (bytes `0368 d3f89031 9847`). Compara el discriminador de tipo de la vtable: **no lee ningún id de evento**. Es el mismo patrón que
  `ACT_IconBattery::cast` (`0x2c90c0`) y `ACT_IconBattery_Rec::cast` (`0x2badb4`).
- **De dónde sale el icono de modo.** `CmnViewModelWrpCameraExposureMode::getExposureModeActVal()` — `viewUnified2+0x1c0eb4`, 80 B:
  `ParamList::ParamList` (`blx 0xe6424`) → `CmnViewModelIfWrapper::getModelInfo("@M00B", 0xf, &pl, 0)` (`movs r1,#0xf` en `+0x1c0ec2`,
  `blx 0xe83b4` en `+0x1c0eca`) → `ParamList::get(0x12c)` (`mov.w r1,#0x12c` en `+0x1c0ed2`, bytes `4ff49671`) → `getInt` (`+0x1c0ede`).
  Cadena del nombre resuelta en `.rodata`: **`@M00B`**; clave **`0x12c` (300)**. Es la misma info `0xf`/`0x12c` que la auditoría de iconos
  (§5.18z¹³) veía a 0, y el consumidor que faltaba en G22-DIAL-FN.
- **El modo llega a la vista como parámetro de apertura** (§5.31, `setInitForRec` ← `viewUnified2+0x14068c`) y, en caliente, por
  `getRecViewFromDial`. Por eso el icono cambia al **activar** la vista y no al recibir el evento.

**Conclusión (a):** en `viewUnified2` no existe el «consumidor del evento que repinte el icono». El repintado es el de la vista activada; lo
que faltaba en el arnés era que **el invitado** la volviera a activar en vez de que lo hiciera el anfitrión desde Python.

### 1.2 `0x15040010` (jack USB): se consulta en `execCheck`, al activar la vista

- Clave del estado del jack en `InfraInput` (`KEYINIT=7000001:1:177`, §5.18w). Consumidores: `InputService::getInputEventStatus`
  (`libObj+0x114104` → `ParamList::get`, `+0x114114 bl 0xe5b20`) desde `ViewRootPowerSw` — literales en
  `viewUnified2+0x17083c`, `+0x1708cc`, `+0x171a7c` (bytes `10 00 04 15`) —, es decir `CheckerUSBAndClockReady` (§5.18: `execCheck` corre
  **al activar** la vista), y `CmnViewNoHdmi::enterConcurrentHdmiUsbMode` (`viewUnified2+0x1a9060`, vista `LG_master_other39…USB_CONNECTING`).
- **No hay handler de evento del jack**: el mensaje del driver solo actualiza el estado de la entrada (`libObj+0x806f88`) y quien quiera
  saberlo **pregunta**. Cambiar el jack con la vista ya activa no repinta nada (medido, §3).

### 1.3 Batería y carga: `ACT_IconBattery` lee `model/POWER` y `@M084`

- `ACT_IconBattery::WidgetUpdateSync()` — `viewUnified2+0x2758b8`, 12 B: `pop.w {r7,lr}` (`bde88040`) + `b.w 0x275530`.
- `0x275530` (la actualización real del icono) consulta, en este orden:
  - `getInfo(modelo, 1, &pl)` con **`movw r1,#0x101`** (`0x275568`, bytes `40f20111`) → int; valores 1..2 se tratan aparte;
  - `getInfo("model/POWER", 0, &pl)` (`movs r2,#0`) y lee **`0x100`** (`mov.w r1,#0x100`, `4ff40071`; == 2 → sigue), **`0x102`**
    (`4ff40271`) y **`0x104`** (`4ff40471`), estos dos como `ParamBase` (`0xedfcc`) + booleano (`0xedfc4`).
  - El nombre del primer modelo está en `.rodata` junto a `@M084` (`0x3954c8`); el segundo es literal `model/POWER` (`0x3986b2`).
- `CmnViewModelWrpPowerState::getPowerType()` — `viewUnified2+0x243c50`, 80 B: `getModelInfo(nombre, 0, &pl)` + `ParamList::get(0x100)`
  (`mov.w r1,#0x100` en `+0x243c6e`). **Clave `0x100` de info 0 = tipo de alimentación.**
- Clases hermanas del mismo icono: `ACT_IconBatteryLevel_C` (`cast 0x26a850`, `Check_ACT_IconBatteryLevel_C 0x26a938`),
  `ACT_IconBattery_Rec` (`0x2badb4`), `Check_ACT_IconBattery` (`0x2c91d4`), `ACT_IconBattery::SetInfoOffVal` (`0x275524` → `strb r3,[r0,#0x95c]`).
- **CamMgr `0x3001`**: el shim solo contesta con `CAMGREMU=1` (opt-in) y sigue siendo la única fuente del nivel en el arnés sin av-cam.
  En el perfil medido **nadie pregunta** → `B` cambia la respuesta que se daría, no lo que se pinta.

**Conclusión (b):** el icono está y se actualiza por `model/POWER` (info 0: `0x100` tipo de alimentación, `0x102`/`0x104`) y `@M084`
(info 1: `0x101`); sin modelo de alimentación alimentado (av-cam/UPM) no hay valor que pintar. Cierre: alimentar esas claves.

## 2. Cambio de código (mínimo)

1. `scripts/gui/harness/shim/sonyshim.c` — **REDIAL** (nuevo, por defecto activo):
   - `redial_on()`: `REDIAL=0` lo apaga (se puede cambiar **en caliente** con `E REDIAL=0|1`, porque el shim sustituye `getenv`);
   - `redialhot()`: espera **300 ms** (el estado del dial lo escribe el hilo del driver, `libObj+0x806f88`) y llama a `openhot("view/STLREC")`,
     que **sin argumento** pide el modo al firmware (`modo_caliente` → `CmnViewBigModelUtil::getRecViewFromDial`, `OPENVIEWDIAL`).
     `REDIALROOT=1` añade el `O view/ROOT` previo (comportamiento antiguo) para diagnóstico;
   - gancho en la rama `K` del puerto LIVE: `if (m[0] == 0x7025 && redial_on())` → hilo `redialhot`.
2. `scripts/gui/harness/live.py` — **un solo hunk de backend** en `Vm.gira`: manda la tecla del dial y **nada más** (ya no lanza
   `reabre_vista()`, que queda como utilidad de diagnóstico manual). `PAGINA`, el HTML y el JS no se han tocado.
3. `shim/build.sh` reconstruido con el sysroot del arnés: **mismo conjunto de símbolos indefinidos** que antes (130, ni uno nuevo);
   `sonyshim.so` md5 `6054b3db2513de92f640f37349184e25`.

## 3. Lo medido

Perfil `osd1`, puerto 8660, 640×480, umbral 12 sobre la suma RGB (`POST /refrescar` + `GET /eventos` por captura). `E REDIAL=0|1` cambia el
modo **en caliente** dentro de la misma sesión (el shim sustituye `getenv`).

**VERIFICADO en el invitado (log del shim, `live/osd1/shim.log`).** El mecanismo corre entero dentro del invitado y pide el modo al firmware:

```
227.98 214.48 env REDIAL=0
239.04 225.54 env REDIAL=1
240.39 226.89 OPENVIEWDIAL getRecViewFromDial() = 6      <- K 7025 6 27 (M)
240.39 226.89 OPENHOT view/STLREC 0x6 -> -2025483104
243.44 229.93 OPENVIEWDIAL getRecViewFromDial() = 4      <- K 7025 4 27 (A)
243.44 229.94 OPENHOT view/STLREC 0x4 -> -2025483104
```

Es decir: la tecla del dial entra por la rama `K`, el shim espera y consulta `getRecViewFromDial` (6 = M, 4 = A, los mismos números que el
parámetro de apertura de §5.31) y vuelve a activar `view/STLREC` con ese modo, **sin que el anfitrión mande ninguna línea `O view/…`**.

**NO se pudo medir el cambio en píxeles en esta sesión.** El arranque en frío dio el primer fotograma a los 151–197 s (había 2–3
`qemu-system-arm` de otros agentes), pero la OSD de disparo aún no estaba pintada: las capturas salen casi negras (484–900 px no negros de
307 200) y **todas** las comparaciones dan **416 px** contra la primera captura y **0 px** entre el resto —incluido el ruido—, o sea que lo
único que cambió fue un elemento que apareció una vez. El estado autoguardado (`estado.zst`, 02:51) se restauró en **27 s**, pero la pantalla
restaurada seguía sin OSD (25 fotogramas, «0 listas» de GPU). **Por eso no hay tabla de píxeles válida aquí** y no se afirma ningún cambio
visible: la tanda de píxeles está pendiente (ver §5, primer punto).

## 5. PARA PENDIENTES.md

| ID | Estado | Qué es | Criterio de cierre | Origen |
|---|---|---|---|---|
| G22-OSD-REFRESCO | EN CURSO (27-11-2026) | **Repintado de la OSD al cambiar modo/batería/USB.** Estático: `Event(0x15070050)` **no tiene manejador** en `viewUnified2` (los 12 sitios son consultas de `ParamList`/estado del dial; `ACT_ExposureMode::cast` `+0x2b6e2c` es un downcast por vtable `+0x190`); el icono de modo se pinta al **activar** la vista y su dato es `CmnViewModelWrpCameraExposureMode::getExposureModeActVal` (`+0x1c0eb4` → `getModelInfo("@M00B", 0xf, …)` clave `0x12c`). Implementado: **REDIAL** en el shim (al ver `K 7025 …` vuelve a activar `view/STLREC` sin modo → `getRecViewFromDial`, `REDIAL=0` lo apaga, `REDIALROOT=1` recupera el `O view/ROOT` previo) y `Vm.gira()` sin reabrir (un hunk de backend en `live.py`). **Medido**: el invitado consulta el modo y reabre solo (`OPENVIEWDIAL getRecViewFromDial() = 6/4`, `OPENHOT view/STLREC 0x6/0x4`). Batería: el icono es `ACT_IconBattery` (`WidgetUpdateSync 0x2758b8` → `0x275530`) y lee `model/POWER` info 0 claves `0x100` (tipo de alimentación, también en `CmnViewModelWrpPowerState::getPowerType 0x243c50`), `0x102`, `0x104` y `@M084` info 1 clave `0x101`; `0x3001` sigue sin consumidor (0 peticiones) y `B` no llega al modelo. USB: `0x15040010` se consulta en `execCheck` (`CheckerUSBAndClockReady`, literales en `viewUnified2+0x17083c/0x1708cc/0x171a7c`) al activar la vista, no al llegar el mensaje. Tests sin QEMU: `tests/test_g22_osd.py` (11). | Cerrar cuando (1) se mida el cambio en píxeles con la OSD ya poblada (capturar solo con >5 000 px no negros y ≤2 VM en el sistema): dial M/A/S/P/auto **sin** que el anfitrión reabra, `B 5` vs `B 100` y `U 0` vs `U 1`; (2) el nivel de batería llegue a `model/POWER` (interponer `CmnViewModelIfWrapper::getModelInfo` y rellenar `0x100/0x102/0x104` desde el modelo del anfitrión, o arrancar con av-cam real); (3) el jack USB produzca la transición de `ModelUsb*`/`CmnViewNoHdmi` (`…USB_CONNECTING`) o se documente que la A6000 solo lo mira al activar la vista | [informe](gui/g22-osd-refresco.md) · `shim/sonyshim.c` · `live.py` · `tests/test_g22_osd.py` |

## 4. Límites y NO_VERIFICADO

- **Lo que el arnés hace ahora no es el mecanismo íntimo de la cámara, sino su efecto**: el invitado vuelve a activar la vista en vez de que lo
  haga Python. El eslabón «info cambiada → vista se repinta» sigue sin localizar (§5.21/§5.27 del puente, abierto), y **no hay traza de una
  cámara real** que demuestre si repinta con `0x15070050` o reabriendo la vista: NO_VERIFICADO.
- **Batería**: sin av-cam nadie pide `0x3001`; `B` no llega a `model/POWER`. Siguiente paso concreto: interponer
  `CmnViewModelIfWrapper::getModelInfo` (el shim ya lo engancha para `GMIDUMP`) y rellenar info 0 claves `0x100/0x102/0x104` desde el modelo
  del anfitrión (`B`/`U`), o arrancar con av-cam real para que lo haga ObjCamera.
- **Jack USB**: emular la transición de `ModelUsb*`/`CmnViewNoHdmi` (vista `…USB_CONNECTING`) no está hecho; lo único verificado es que el
  mensaje llega y que la vista lo consulta al activarse.
- Las capturas miden el **fotograma del invitado**; la ventana del anfitrión y su HTML/JS no se han tocado ni comprobado aquí.
