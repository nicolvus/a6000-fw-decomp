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
`build_base_tar.py analysis/gui/g22/base-380.tar` (sha256 `ac842a74…c2ab6`) → `build_cfw_completo.py analysis/gui/g22/pkg-380w --version 3.80`
(`BASE_TAR` apunta ahora a `base-380.tar`). Menú y `/usr` iguales que el 3.79.

## 5. Paquete y auditoría

**Corrección:** el primer 3.80 (`.dat` `4e37a846…8dd3`, commit `c22be949`) **no llevaba el cambio**: su `base-380.tar` (`68af4054…`) tenía el copiador
anterior (`c4f81c24` en `0x43845f34`). Se reconstruyó y ahora `base-380.tar` lleva `93f83802 0243 c4f81c24`. El BIONZ del paquete es idéntico,
byte a byte, a `bionz_cfw(patch_tristate(3.38))` (0 diferencias). Ese primer `.dat` no debe usarse.

`analysis/gui/g22/pkg-380w/pkg-3.80/package-3.80/firmware_packed.dat`, sha256 `7a0e8aae0dc1e921c902b1c0ba19010ef44fb22916cde07b7c03c30b5f57c429`,
**NO instalado**. Auditoría `--darwin-v3 --sin-wbi --bionz-g22`: **29/29**.

Los dos controles BIONZ fallaban igual en el 3.76, 3.77, 3.78 y 3.79 (27/29 en los cuatro): exigían «3.38 + `patch_tristate` y nada más», y
desde el 3.73 el BIONZ lleva además el parche PP del núcleo y Silent calibrado. Comprobado en el 3.79: su BIONZ es exactamente
`build_base_pp.bionz_cfw(3.38 + patch_tristate anterior)` (0 diferencias). El control (`audit_package_nflasha15.bionz_g22_checks`) acepta ahora
solo dos imágenes exactas: 3.38 + tres estados, o esa más `bionz_cfw` (PP + Silent calibrado). Cualquier otro byte falla (`tests/test_g22_audit_bionz.py`).
`build_base_pp.bionz_cfw` se extrajo de `build_base_pp.main` sin cambiar su lógica (`test_g31_base_pp.py` pasa).
Con el control nuevo, el 3.77–3.79 seguirían fallando por el copiador anterior. Reversión: reinstalar el 3.79 con una versión mayor.

## 6. Lectores de `+0x210` y `cap+0x41c/0x41d` (sin REA)

Búsqueda de bytes en el BIONZ: cargas y almacenamientos T32 `imm12` (`ldr/ldrb/ldrh/ldrs*/str*`) con desplazamiento `0x210`, `0x41c`–`0x41f`.

* `+0x210` con el literal `0x43EDF684` a ±1 KiB: solo el envío `0x438d01ac`, que ya no lo usa (`mov r3,r2`).
* En la zona de captura (`0x4383f000–0x43846000`), los usuarios de `cap+0x41c` son los lectores de Sony `0x4384219e`/`0x43842270`
  (`ldrb`, `cmp #1`: ahora ven 1 con Silent, la rama «EFCS off», lo que se busca). `0x4384231e` hace `ldr.w r1,[r7,#0x41c]` y luego `strb` a una
  global: guarda el byte bajo (EFCS | Silent), coherente. El copiador escribe en `0x43845f34`/`0x43845f3e`. Los de `cap+0x41d` son el CTOR
  `0x43841472` y el copiador.
* Otros 140 accesos `#0x210` y 131 `#0x41c` en todo el BIONZ usan otras bases. Revisados: `0x43837e5a` (`ldrb [r3,#0x210]` de una tabla global
  de bytes con paso 9: `0x1fe`, `0x207`, `0x210`, `0x219`), `0x4383c834` (`ldr.w r1,[r8,#0x210]` sobre el objeto `r0` de esa función) y
  `0x43862338` (`ldrb [r0,#0x41d]` junto a `0x410`–`0x418` de un objeto `[r6]+r8`). No se pudo atribuirlos ni descartarlos sin flujo de datos:
  **NO_VERIFICADO**.
* No cubre: accesos con base calculada (`add rX,#0x400` y desplazamiento corto), `ldrd`/`ldm`, copias por `memcpy` (`0x43844e80` copia la
  estructura `cap` entera: cualquier lector de la copia ve el mismo valor), ni lectores en otros procesadores. Ningún acceso hallado contradice
  «Silent manda sobre EFCS».

## 7. Protocolo de prueba en cámara (3.80 instalado; solo lecturas y fotos normales)

Regla del `AGENTS.md` (reinicio experimental): no reutilizar direcciones de sesiones anteriores, ni escribir RAM, MMIO, firmware o NVRAM.

0. **Inicio de la sesión.** Identificar cámara e IP (`scripts/camera_telnet.py --host IP`), probar Telnet y RemoteShutter, versión (3.80) y hashes
   pertinentes, originales T050, punteros GOT y mapa de memoria (`/proc/<av-cam>/maps` o equivalente).
   Localizar de nuevo el bloque de ajustes: buscar el literal que usa el envío `0x438d01aa` en la imagen viva. No dar por bueno
   `0x43EDF684`/`0x83EDF894`/`0x83EDF8BC` sin comprobarlo. Línea base: objetivo/focal, f, ISO, Tv, modo M, luz, escena fija con trípode,
   WB fijo, batería, temperatura si la hay; lo no medible, «desconocido». Comprobar que la cámara está estable.
1. **Cuatro combinaciones**, en este orden y en la misma sesión (misma escena, luz, f e ISO; Tv 1/250 y, si da tiempo, 1/2000):
   A = EFCS Off + Silent Off, B = EFCS On + Silent Off, C = EFCS Off + Silent On, D = EFCS On + Silent On (la nueva).
   Para cada una:
   * por menú: elegir los dos ajustes y anotar si EFCS aparece en gris (C y D deben mostrarlo en gris);
   * por Telnet, solo lectura: los bytes `+0x210` y `+0x238` del bloque localizado en el paso 0. Se espera A (1,0), B (0,0), C (1,1), D (0,1);
   * una foto normal (RAW + JPEG) con el disparador o RemoteShutter (`/mode?v=menu`, no los otros `/mode`, que escriben RAM).
     Anotar si se oyen las cortinas.
2. **Criterio:**
   * A tiene sonido de cortinas y exposición de referencia.
   * B tiene EFCS (cortina final mecánica).
   * C y D: sin sonido de cortinas, EXIF con la Tv pedida y exposición dentro de ±1/3 EV de A (R87: 0,93–1,10).
   * Los RAW de C y D, con la misma escena, deben ser iguales en exposición y en el rolling shutter visible (probar con un objeto en movimiento si se quiere).
   * Si D sale como B (cortinas) o con exposición distinta a C, el cambio no actúa: volver al 3.79.
3. **Final.** Releer los mismos bytes y hashes, confirmar que no hay modificaciones y guardar los RAW originales con metadatos y el registro
   (`analysis/camera-dumps/<fecha>-g22a-380/`).

## 8. Límites (NO_VERIFICADO)

* Sin cámara: el (0,1) del 3.80 no se ha medido. Se espera lo mismo que el (1,1) de R87.
* Lectores del §6 no atribuidos y modos de acceso no cubiertos.
* Persistencia: ninguno de los dos se ha verificado (que `+0x238` se restaure al arrancar, ni la vuelta a Off tras reiniciar, G22-A (3)).
* Un único menú de 3 valores (como `CustomStillShutterType` de la A6300) no se hizo, porque la A6000 no tiene `SequenceSetShutterType`.
  Los dos menús con Silent dominante dan los tres estados igual que el A6300.
