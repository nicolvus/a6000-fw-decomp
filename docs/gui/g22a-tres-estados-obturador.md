# G22-A — Tres estados de obturador (Mecánico / EFCS / Electrónico): verificación del 3.79 y CFW 3.80

12-11-2026. Offline: sin cámara, sin VM, sin REA (ocupado por otro agente). Evidencia por bytes (Python sobre los ficheros del paquete,
`llvm-mc --disassemble`) y emulación unicorn existente (`tests/test_g22_tres_estados.py`).

## 1. La premisa «Silent escribe lo mismo que EFCS» ya no vale desde el 3.57

Vale para el 3.54/3.56 (`build_silent_menu_test.py`, `pid_silent` por defecto `0x46`). El 3.79 (`analysis/gui/g22/pkg-379w/`) lo construye
`build_cfw_completo.py` con `pid_silent=0x12`. Comprobado por bytes en sus ficheros:

| Eslabón | 3.79 (por bytes) | EFCS (control) |
|---|---|---|
| Nodo `SilentShutterRoot` (`CautionConfig.so`, `0x1d0000`, 5 ternas) | `(0xe, 1, 0x12)` → ProcessId `0x12` | `0x46` |
| Tabla D de `viewUnified2.so` (copiada por `pid_space` a `0x6f5e44`) | `D[0x12]` = `0x63b510`: modelo `@M00F`, escritura `0x5b`, lectura `0x6c`, claves `0x291`/`0x292` | `D[0x46]` = `0x4b7044`: `0x54`/`0x4f`, `0x246`/`0x247` |
| Sony original | `D[0x12]` apunta a basura (pid inerte) | igual |

Tramo ya verificado en G22-A (09-11-2026, sin cambios): `0x5b`/`0x291` → `libObj` `0x689ea4` → mensaje `0x768e` → LIRO `0x40e3`
→ manejador `av-cam` `0x438032d4` → byte `+0x238` del bloque `0x43EDF684` (EFCS: `0x75fa` → LIRO `0x4099` → `+0x210`).
**Silent y EFCS son ajustes distintos (`+0x238` y `+0x210`).** Lo que oye el usuario como «lo mismo» puede venir del CFW 3.56
o de la interacción del §2. Medido en cámara con el 3.77 (R87, `/mode`): Mecánico = (`+0x210`,`+0x238`) = (1,0), EFCS = (0,0), Silent = (1,1).

## 2. BIONZ del 3.79 (extraído de `nflasha3` del `firmware.tar`)

Los seis sitios de `g22.patch_tristate` están aplicados y el enganche de `patch_silent_r5` también. Desensamblado:

* envío a Darwin `0x438d01aa`: `ldr.w r3,[r2,#0x210]; ldr.w r2,[r2,#0x238]; mov r3,r2` → **`pkt[0x0e]` = Silent solo** (el docstring decía
  `+0x210 & +0x238`; corregido);
* cueva r5 `0x43FB7E00`: `ldrb r3,[0x43EDF8BC]` (= `+0x238`), `cmp #1` → ShutMode 0 + `r5` solo con Silent;
* copiador `0x43845f2e`: `cap+0x41c` = `[+0x210]` (EFCS de Sony) y `cap+0x41d` = `[+0x238]`.

Hueco: con **EFCS On + Silent On** (0,1) Darwin no mueve cortinas y la cueva aplica la exposición electrónica, pero los lectores de Sony
de `cap+0x41c` (`0x4384219e`, `0x43842270`, `cmp #1`) siguen en la rama EFCS (`0x41c` = 0), y la tabla EFCS de NVRAM sigue en juego. Es una
cuarta combinación sin medir. El G30 solo pone EFCS en gris con Silent On (`pid_space`, `isGrayedOut`). No cambia su valor.

## 3. Cómo lo hace la A6300 (G09, S169, S401)

Dos menús separados, EFCS `0x4e` y Silent `0x2b`/Shutter Type `0x13f`. Silent manda: EFCS queda en gris y el núcleo decide por un campo propio
(`cap+0x804 == 2` → `pkt[+0x12] |= 0x20`), sin mirar EFCS. El equivalente en la A6000 es `cap+0x41d`/`pkt[0x0e]`. Lo que faltaba era
que Silent anulara también el EFCS de Sony en `cap+0x41c`.

## 4. Cambio (CFW 3.80, construido, NO instalado)

Copiador `0x43845f2e`, mismo tamaño (18 B reordenados, desaparece el `nop`):

```
antes: ldr.w r2,[r3,#0x210]; str.w r2,[r4,#0x41c]; ldr.w r0,[r3,#0x238]; nop; strb.w r0,[r4,#0x41d]
ahora: ldr.w r2,[r3,#0x210]; ldrb.w r0,[r3,#0x238]; orrs r2,r0; str.w r2,[r4,#0x41c]; strb.w r0,[r4,#0x41d]
```

`cap+0x41c` = EFCS | Silent. Con Silent On, Sony ve EFCS desactivado, así que (0,1) se comporta como el (1,1) medido. `ldrb` evita llevar a
`0x41e/0x41f` los bytes altos de la palabra `+0x238`. Los flags de `orrs` los sobrescribe `rsbs.w` antes del `adc.w`, que es el único que
los lee en el copiador. Tabla resultante:

| EFCS | Silent | `cap+0x41c` | `cap+0x41d` / `pkt[0x0e]` / cueva r5 | Estado |
|---|---|---|---|---|
| Off (1) | Off | 1 | 0 | Mecánico |
| On (0) | Off | 0 | 0 | EFCS |
| cualquiera | On | 1 | 1 | Electrónico (EFCS en gris en la UI) |

Pruebas: la regresión `test_copiador_igual_que_sony_salvo_el_byte_nuevo[0-1]` falla con el 3.79 y pasa con el cambio. Pasan 24/24 de
`test_g22_tres_estados.py`, `test_e26_r86_silent_r5.py` y `test_g29_pp_ram_vigilancia.py`. Construcción:
`build_base_tar.py analysis/gui/g22/base-380.tar` (sha256 `68af4054…ce8ca`) → `build_cfw_completo.py analysis/gui/g22/pkg-380w --version 3.80`
(`BASE_TAR` apunta ahora a `base-380.tar`). Menú y `/usr` iguales que el 3.79. Resultado en el §5.

## 5. Paquete

`analysis/gui/g22/pkg-380w/pkg-3.80/package-3.80/firmware_packed.dat`, sha256 `4e37a8466b60d5f8888d867391340d25f72eb3a591f7a5341081db5c69718dd3`,
**NO instalado**. `audit_package_nflasha15.py --darwin-v3 --sin-wbi --bionz-g22` da 27/29. Fallan los dos controles «BIONZ = 3.38 + `patch_tristate`
y nada más», y fallan igual en el 3.76–3.79: el `base_pp` añade los parches PP y r5 al BIONZ. Reversión: reinstalar el 3.79 (o el 3.78)
con una versión mayor.

## 6. Límites (NO_VERIFICADO)

* Sin cámara: el (0,1) del 3.80 no se ha medido. Se espera lo mismo que el (1,1) de R87.
* No se buscaron otros lectores directos de `+0x210` vivo (REA ocupado; una búsqueda de literales no prueba ausencia).
* Persistencia: ninguno de los dos se ha verificado (que `+0x238` se restaure al arrancar, ni la vuelta a Off tras reiniciar, G22-A (3)).
* Un único menú de 3 valores (como `CustomStillShutterType` de la A6300) no se hizo, porque la A6000 no tiene `SequenceSetShutterType`.
  Los dos menús con Silent dominante dan los tres estados igual que el A6300.
