# FILM-PB-1 (sub) — Riesgo de los tres flasheos candidatos (A: 3.21 oficial · B: CFW con WBI · C: `libmpr` parcheado)

Fecha: 26-11-2026. **Auditoría 100 % offline**: no se abrió la cámara, no hubo USB ni `pmca`, no se construyó
ningún DAT, no se escribió nada fuera de `reports/`. La salida la lee quien decide si flashea, así que cada
afirmación lleva su fuente y las que no se han probado van marcadas. Etiquetas: **MEDIDO/VERIFICADO** (fichero o
byte comprobado hoy), **LEÍDO** (documento o código del repo), **INFERENCIA**, **NO_VERIFICADO**.

Evidencia reproducible: [`evidence/film-pb-1-sub-riesgo-flash-20261126/`](evidence/film-pb-1-sub-riesgo-flash-20261126/)
(`verificar-riesgo-flash.py`, `reconstruir-tar-oficial.py`, `verificacion.json`, `tar-oficial-reconstruido.json`,
`extractos.txt`).

---

## 0. Veredicto en una tabla

| Vía | ¿La acepta el guard hoy? | Qué bytes nuestros entran en la cámara | Riesgo de **ladrillo** (irrecuperable sin desmontar) | Riesgo de **quedarse sin arranque** (hay que repetir R48 por SWD) | Qué información da |
|---|---|---|---|---|---|
| **A tal cual** — DAT oficial 3.21 (`camera_reflash_fw321.sh`) | **NO**, casi con seguridad: la versión instalada es ≥ 3.93 (NO_VERIFICADO el valor exacto) y el guard exige **estrictamente mayor** | ninguno: se rechaza en `checkGuard`, **antes** de escribir | **NULO** | **NULO** | **Ninguna** (solo el mensaje `Invalid version`) |
| **A operativa** — el mismo contenido oficial reempaquetado con versión > instalada (4.04 ya construido; 4.05 si la instalada es ≥ 4.04) | Sí | **ninguno propio** si se pasa el `nflasha15` de Sony: el tar sale **byte a byte** igual al oficial (§1.3) | **BAJO** — igual que las ~40 instalaciones anteriores | **BAJO** (abortos ya vistos se recuperan reintentando; 3.26) | ¿Es el CFW (sus ~40 parches acumulados) la causa del fallo de reproducción? |
| **A2** — A operativa **conservando el `nflasha5` de Sony** (mismo paquete, un miembro más) | Sí | ninguno propio (todo Sony, WBI incluido) | **BAJO** | **BAJO-MEDIO** (estado caliente; precedente que arranca: 3.48) | Lo mismo **y** discrimina H1 (arranque caliente) con contenido coherente |
| **B** — CFW con WBI (`build_package_nflasha15.py` sin `--sin-wbi`) | Sí, si `--version` > instalada (por defecto **3.39**, que **no** pasaría) | `/usr` del CFW + `nflasha3` del CFW + Darwin v3, con el **WBI de Sony** | **BAJO** | **MEDIO** (mezcla WBI de Sony ↔ `/usr` modificado; no reversible en caliente, `warm.ignore_drop=1`) | Si H1 fuera cierto, B **no** lo arregla (en caliente el `/usr` del CFW queda inerte) → sirve para descartar, no para curar |
| **C** — `pp` + `lib/libmpr.so` parcheado | Sí, con `--version` > instalada | 8 B en `/usr/lib/libmpr.so` + `nflasha3` del CFW + Darwin v3 (y por defecto **sin** `nflasha5`) | **BAJO** | **MEDIO** (un `.so` de arranque de la app no probado; si la app no arranca, no hay `pmca` y hay que ir por SWD) | Si las guardas A/B son la causa del `0x1A`: es el único de los tres que responde a eso |

**El riesgo de *ladrillo* es el mismo y bajo en las tres** (escriben el mismo conjunto de particiones por la misma
vía que ya se usó ~40 veces). Lo que cambia es el riesgo de dejar la cámara sin arranque normal y tener que
repetir el rescate de [R48](../docs/capture/e26-r48-plan-recuperacion-actualizador-swd.md)/[R49](../docs/capture/e26-r49-cierre-recuperacion-326.md),
y la información que se obtiene a cambio.

---

## 1. Hecho que cambia la decisión: **A, literal, no se ejecuta**

### 1.1 El guard rechaza 3.21 sobre lo instalado (LEÍDO + MEDIDO en su día)

- `sauu` compara contra `<nflasha2>\updater\dat4` y solo acepta **versión mayor**, o igual si falta `comp`
  ([R38 §2](../docs/capture/e26-r38-guard-y-entrada-updater.md): `UpdaterHandler::isVersionOK` `0xd3d0`).
- Medido en esta cámara con 3.21 instalado: **3.20 y 3.21 rechazadas**, 3.22 y 9.99 aceptadas
  ([custom-fw-recovery-and-install §«Cómo volver atrás» 2](../docs/capture/custom-fw-recovery-and-install.md)).
  El intento real de reflashear 3.21 sobre 3.21 dio `Invalid version` **sin escribir**
  ([liveview-silent-capture-via-cameraex:43](../docs/capture/liveview-silent-capture-via-cameraex.md)).
- La versión instalada hoy es **≥ 3.93** y el repo no la tiene confirmada (`3.93` en la auditoría del 27-11 frente
  a «4.02 instalada» de [G111 §14](../docs/gui/g111-film-receta-gui-iconos.md); **NO_VERIFICADO**, se resuelve en
  30 s en el menú de la cámara).
- `scripts/camera_reflash_fw321.sh` no puede saltarse el guard: solo comprueba `sha256sum` (línea 10), `lsusb`
  (11) y pide `SI` (13) → `pmca-console firmware -f DAT` (`extractos.txt` §5). El rechazo ocurre en
  `dev.checkGuard()` **antes** de `writeFirmware` (`references/pmca/pmca/commands/usb.py:390` vs `:421`), y la
  cámara devuelve `STAT_INVALID_VERSION`/`INVALID_MODEL`/`INVALID_REGION`/`LOW_BATTERY`… (`usb/sony.py:541-554`).

**Conclusión A:** tal cual, A es un **no-op**: cero daño, cero información. Para usar A hay que reempaquetar el
contenido oficial con una versión mayor (**A operativa**), que es exactamente lo que ya hizo el 3.26
([R49 §1 y §9](../docs/capture/e26-r49-cierre-recuperacion-326.md): 3.24 oficial con la versión subida a 3.26,
instalado con éxito tras un NG de Darwin).

### 1.2 A operativa ya existe construida y auditada

`build/sony_puro_sin_wbi_404/package-4.04/firmware_packed.dat`, SHA-256 `9c7b4f46…0872` (**MEDIDO**),
versión 4.04, `sin_wbi: true`, `darwin_v3: false`, tar base = **el oficial de Sony** (`container.json`). Su
contenido es el de fábrica salvo que **quita** `nflasha5`: 103 de 104 miembros idénticos byte a byte a Sony
([restauración 27-11 §2](film-pb-1-sub-restauracion-20261127.md)).

### 1.3 Si se le pasa el `nflasha15` de Sony, el tar es **idéntico al oficial** (MEDIDO hoy)

`reconstruir-tar-oficial.py`: base `firmware/extracted/fw321/firmware.tar` (`97024649…d5a8`), se sustituye
`0700_part_image/dev/nflasha15` por el **mismo** fichero de Sony y se recalcula su línea de `part_image.sum`
(`0,df198ecd,050264e1,…,dev/nflasha15,`) → el tar reconstruido da **el mismo SHA-256**, `identico_byte_a_byte:
true`. Es decir: la «A operativa» no mete ni un byte nuestro en el payload; lo único distinto del paquete oficial
es la **versión de la cabecera FDAT** (y su CRC + el CRC de DEND; mismo patrón que la 3.24 auditada en
[E25-06 §7](../docs/capture/e25-06-auditoria-independiente-paquetes.md), donde el `.dat` solo cambia en
`[140,156)`, `[172,188)` y el CRC final).

**A2** (misma operación **sin** quitar `nflasha5`) reconstruye el tar oficial **incluido el WBI de Sony**, que es
el estado de fábrica exacto. Es la única forma de probar H1 (arranque caliente) con contenido **coherente**.

---

## 2. Qué escribe cada candidato

Base común (LEÍDO en `part_image.sum`, `config.xml` y `us_mkfs.sh`; `extractos.txt` §1-§3):

| Escritura | Dónde | Quién | A | B | C |
|---|---|---|---|---|---|
| `nflasha3` (sistema principal, TPZL) | `/dev/nflasha3` | bucle de miembros + CRC de `part_image.sum` | 11 489 040 B, CRC `0c047870`, residuo 0 (Sony) | 11 489 280 B, CRC `377ac2c4` (base `base-film.tar`, 3.93) o `1f6201c7` (base 3.38/3.80); residuo 0 en los cuatro tars (MEDIDO) | igual que B |
| `nflasha5` (WBI) | `/dev/nflasha5` | idem | 42 293 120 B (Sony) | **42 293 120 B (Sony)** | **se quita** del tar (frío) |
| `nflasha7` (rootfs) | `/dev/nflasha7` | idem | 3 324 495 B (Sony) | Sony | Sony |
| `nflasha15` (`/usr`) | `/dev/nflasha15` | idem | 84 042 977 B (Sony) | el del CFW (~84,6 MB) | el del CFW **+ `libmpr.so` parcheado** |
| `nflasha16` (Android system) | `/dev/nflasha16` | idem | 59 013 103 B (Sony) | Sony | Sony |
| Backup de Android / ficheros de lente | `nflasha17` / `nflasha18` | `0800_appli` (18 `VX910x_lensfile.bin`; `mount.conf`: `/lens`=`nflasha18`, `/android/data`=`nflasha17`) | Sony | Sony | Sony |
| `Backup.bin` en `/setting` | `/dev/nflasha2` | `ud_keep_backup -s` | sí | sí | sí |
| `\updater\mode`, `dat4`, `comp`, `mode1…6` | `/dev/nflasha2` | cuerpo del paquete (`StartUpdate`/`CompleteUpdate`) | sí | sí | sí |
| **Drop del WBI** (512 B a cero) | `/dev/nflasha5` | `ud_wbi_drop.elf` (siempre, `us_mkfs.sh:106`) | sí (y luego se reescribe) | sí (y luego se reescribe) | sí (y **no** se reescribe) |
| Formateo FAT | `/dev/nflasha*` (FAT) | `uc_mkfs.elf -m app` (USER; `-m full` solo en PRODUCT/VERSKIP) — formatea FAT según `mount.conf` ([R14 §139](../docs/capture/e26-r14-ramcfg-bos-analysis.md); alcance exacto de `app`: NO_VERIFICADO) | sí | sí | sí |
| Tabla de particiones (`edisx`) | `/dev/nflasha` | **NO en USER** (`us_mkfs.sh:39-46`, «do not edisx.elf») | no | no | no |
| Darwin `core` | MCU IC5700, por SIO | `us_darwin_firm.sh` → `ud_darwin_firmup.elf` | core de Sony `5f2be06d` | **Darwin v3** `9771c050` | Darwin v3 |
| `nflasha1`, Loader2/3, `nflasha0`, `dat2/dat3` en `nflasha1` | — | `loader_writer.sh` solo con `loader_sum`; `us_crc32sum_appli.sh:14` solo si el paquete trae `dat4` | **nada** | **nada** | **nada** |

Lo último está **MEDIDO**: ninguno de los cuatro tars base lleva `updater.sum` ni `loader.sum`
(`verificacion.json` → `updater_sum_o_loader_sum: false`) y el paquete 3.21 **no trae** `dat2/dat3/dat4`, así que
la rama que escribe en `nflasha1` no se ejecuta. Coincide con [R38 §3](../docs/capture/e26-r38-guard-y-entrada-updater.md)
(«`nflasha1` y los loaders nunca se reescribieron»).

**Delta real de cada vía respecto a lo instalado hoy** (paquete 3.93 `pp`, que se construyó con `sin_wbi: true`
codificado en duro, [`build_cfw_completo.py:97`](../scripts/gui/build_cfw_completo.py)):
**A**: `/usr`, `rootfs`, `nflasha3` y Darwin vuelven a Sony. **B**: solo cambia el `/usr` (y se **añade** el WBI
de Sony). **C**: solo cambia un fichero de `/usr` (8 B) y se reescribe el `/usr` entero como en cualquier CFW.

---

## 3. Lo que **no** se recupera sin desmontar (y por qué ninguna de las tres lo toca)

| Región | Qué es | Estado en el repo | ¿La escriben A/B/C? |
|---|---|---|---|
| `nflasha0` = NAND física `0x0–0x3ffff` | tabla de la clave del arranque por serie del BootROM | **sin nodo Linux y nunca volcado** ([R20 §KEYTABLE](../docs/capture/e26-r20-keytable.md), [R33 §1](../docs/capture/e26-r33-veracidad-clave-nflasha0.md)); contenido no determinable sin acceso físico | **No** (ningún script la abre) |
| Loader2 / Loader3 | NAND física **fuera de `/dev/nflasha`**; sin binario en el repo | solo lo escribiría `loader_writer.sh` con `loader_sum` ([E24-01 tabla](../docs/capture/e24-01-arranque-recuperacion.md)); ningún paquete lo trae (MEDIDO) | **No** |
| Arranque propio del MCU Darwin `0x0–0x41ff` («darwin_boo») | no va en ningún paquete; leer/escribir su flash exige acceso físico a `CN4906` pines 11/12 | [darwin-via-actualizacion](../docs/capture/darwin-via-actualizacion-2026-10-26.md), [R57 §107](../docs/capture/e26-r57-paquete-336-darwin-eq1.md) | **No** |
| Core de Darwin (el que sí se reescribe) | si queda a medias y el MCU no arranca, **no sube `DD_ON1/2/3`** → el BIONZ no tiene núcleo ni RAM → **ni el SWD sirve** | [E24-01 §Respuesta](../docs/capture/e24-01-arranque-recuperacion.md); el SWD de R49 funcionó porque el BIONZ estaba alimentado | **Sí, las tres** (ver §6) |
| Tabla de particiones (`/dev/nflasha[0:0x200]`) | la lee Loader3 al arrancar | volcada (`dev_nflasha.bin[0:0x200]` + `partinf.conf`) y **no se reescribe en USER** | **No** |
| `nflasha3/5/7/15/16`,`2`,`17`,`18` | datos y sistema | volcado completo del 20-10 (`analysis/camera-dumps/nand-20261020`) + reescritura por el actualizador | Sí, y es **recuperable** (precedente R48/R49) |

**Camino de vuelta probado cuando el sistema principal no arranca:** forzar `\updater\mode` por SWD en la parada
de Loader3 → el actualizador de `nflasha1` (intacto) acepta un paquete por USB → `Done`
([R48 §3](../docs/capture/e26-r48-plan-recuperacion-actualizador-swd.md),
[R49 §8-§10](../docs/capture/e26-r49-cierre-recuperacion-326.md)). Requisitos: la sonda soldada en R4911/R4912
(**[R46](../docs/capture/e26-r46-procedimiento-fisico-swd.md) opción 5a**) y **Darwin vivo** (es quien alimenta
el BIONZ). Si la sonda ya se retiró (R49 §12 lo deja pendiente), «recuperar» significa **volver a abrir y soldar**.

---

## 4. Qué verifica el actualizador antes de escribir, y qué pasa si el paquete no le gusta

Orden real (LEÍDO en `config.xml`, `usb.py`, `us_mkfs.sh`; `extractos.txt`):

| # | Comprobación | Dónde | ¿Antes de escribir? | Cubre A/B/C |
|---|---|---|---|---|
| 1 | Contenedor: `DATV/PROV/UDID/FDAT/DEND`, 207 996 bloques con suma de 16 bits y bandera de último, CRC de cabecera FDAT, CRC de DEND | PC (`fwtool`/`readDat`) | **sí** (nada sale del PC) | igual |
| 2 | **Guard**: modelo `0x41030035`, región 0, versión > `dat4`, batería, tarjeta | `checkGuard` (cámara, `CMD_CHK_GUARD`) | **sí**; rechazo = «Invalid version» y **no se escribe** (medido 3.21→3.21) | A: **no pasa**; A/A2/B/C: depende de la versión |
| 3 | CRC-32 + tamaño + permisos + tipo por fichero de cada `*.sum` (`uc_crc32sum.elf -c`: «size/crc/permission mismatch») | `config.xml` (`config`, `darwin`, `ca`, `prfile`, `backup`, `appli`, `partconf`, `part_image`) | **sí** para cada bloque, antes de su escritor | igual (los tres conservan la estructura) |
| 4 | Capacidad de NAND (`chknandcapa.elf` sobre `partinf.conf`) | `config.xml:21` | sí | igual |
| 5 | **Formateo lógico** `uc_mkfs -m app` + `Backup.bin` + **drop del WBI** | `us_mkfs.sh` (proc de `partconf_sum`) | — | igual (B y C lo hacen también) |
| 6 | Imágenes de partición | bucle de miembros (`KeyTag`), `ApiException(0x30002)` inmediata si algo falla ([R30 §3](../docs/capture/e26-r30-updater-done-boundary.md)) | se escriben **antes** de su suma | igual |
| 7 | **`part_image.sum` relee los nodos de dispositivo** y compara CRC-32 (error LED `0x81` si no cuadra) | `config.xml:17-18` → `us_crc32sum.sh … part_image image` con `TARGET_DIR=/` | **después** de escribir ([R30 §3.5](../docs/capture/e26-r30-updater-done-boundary.md)) | igual |
| 8 | Darwin: solo `darwin.sum` (CRC-32) y la cadena `VER`; **no firma**; el core se reescribe **siempre** (`darwin_boo` no va en el paquete) | `ud_darwin_firmup.elf` | — | igual (las tres reescriben Darwin) |
| 9 | `CompleteUpdate`: escribe `dat4`, crea `comp`, borra `mode*` | `libupdaterbody.so` | al final | igual |

**Qué NO comprueba nadie (puntos ciegos):** no hay firma (FDAT cifrado, no firmado); no hay integridad por
fichero dentro de una partición (solo el CRC-32 global); **no** se simula el decodificador hardware LDEC —el 3.25
pasó las 80 sumas y aun así no arrancó ([R36](../docs/capture/e26-r36-causa-fallo-325.md),
[R15 §8](../docs/capture/e26-r15-tpzl-custom-fw325.md))—; no se comprueba el `ext2` interno; no se comprueba que
el **WBI** case con el `/usr` escrito; y no se sabe si el bootloader del MCU valida el core
(NO_VERIFICADO, [darwin-via-actualizacion](../docs/capture/darwin-via-actualizacion-2026-10-26.md)).

**Si el paquete no le gusta:** (a) rechazo en 1-2-4 → **no se escribe nada**, solo un mensaje de error; (b) fallo
a partir de 5-6 → particiones ya formateadas/WBI ya anulado y escritura a medias: **no** hay `Done`, la cámara
queda con `\updater\mode` creado y el siguiente encendido **vuelve solo al actualizador** (medido en el intento
del 3.26, [R49 §8](../docs/capture/e26-r49-cierre-recuperacion-326.md)) → se reintenta el mismo fichero (el
`dat4` no cambia hasta `CompleteUpdate`).

---

## 5. Historial: ¿se ha instalado algo equivalente antes?

| Versión | Qué era | Resultado | Fuente |
|---|---|---|---|
| 3.21 | oficial, de fábrica | referencia; **nunca** se ha reinstalado por nosotros (el guard lo impide desde 3.22) | custom-fw-recovery §2 |
| 3.22 | oficial + Darwin tipo 0 | `Done`, arranca y dispara | [darwin-via-actualizacion](../docs/capture/darwin-via-actualizacion-2026-10-26.md) (T024) |
| 3.23 | oficial + B1a | instalado, funciona | [E25-05/§STATE](../docs/STATE.md) |
| **3.25** | oficial con `nflasha3` **recomprimido** por nosotros | `Done` **y no arranca** (−302 en `\sabin\idt_cam.bin`): **el único ladrillo de la serie** | [R47 §15](../docs/capture/e26-r47-primer-contacto-swd-lectura-ram.md), [R49 §1](../docs/capture/e26-r49-cierre-recuperacion-326.md) |
| **3.26** | contenido **oficial** con la versión subida (= A operativa) | 1.er intento: `0x1063` (NG de Darwin) al **45 %**; 2.º intento: `Done`; cámara recuperada y `info`=3.26 | [R49 §8-§10](../docs/capture/e26-r49-cierre-recuperacion-326.md) |
| 3.30–3.38 | CFW integrados | «ya se instalaron sin NG» | [R76 §52](../docs/capture/e26-r76-calibracion-propia-efcs.md) |
| 3.40–3.93 | CFW (menús Silent/PP, Darwin v3, núcleo parcheado) | **27 ficheros de log** de instalación en `analysis/gui/g22/install-*.log` (3.59…3.94, varios son intentos fallidos que se repitieron); incidencias: 3.92 se quedó sin encender (INC-392) y 3.93 `iso`/`todo` en bucle → **recuperadas por SWD/R48** | [G105](../docs/gui/g105-builds-por-funcion.md), [G109](../docs/gui/g109-mezcla-pp-film-exfine-iso.md), logs |
| 3.94 / 3.96 / 3.99 | CFW de UI | cuelgues y 3.99 «no arranca» → recuperadas | [G111 §7-§12](../docs/gui/g111-film-receta-gui-iconos.md) |
| **3.48 con WBI** | CFW **conservando** `nflasha5` | **arrancó en caliente**: `BootMode: 11` medido (frente a `BootMode 1` en el 3.52 sin WBI) → **precedente de B**; si reproducía vídeo entonces no consta (NO_VERIFICADO) | [sub-wbi §1](film-pb-1-sub-wbi-20261127.md), `analysis/camera-dumps/20261108-swd-348` |
| 4.00–4.02 | CFW Film | instalados (4.02 según G111 §14) | [G111 §12-§14](../docs/gui/g111-film-receta-gui-iconos.md) |

**Lectura empírica:** ~40 flasheos por USB en esta cámara, **un solo evento de no-arranque por firmware**
(3.25) y **cero pérdidas irreversibles** — pero el 3.25 no arrancó *con `Done`*, o sea que el «Done» no prueba
nada: la única prueba de que el firmware sirve es que la cámara encienda.

---

## 6. Riesgo relativo, peor caso y camino de vuelta exacto

### A tal cual (DAT 3.21 con `camera_reflash_fw321.sh`) — riesgo **NULO**
- Se detiene en `checkGuard` (`Invalid version`) antes de transferir. Peor caso: ninguno; como mucho,
  `Low battery`/`Memory card inserted` (sacar la tarjeta y repetir).
- Camino de vuelta: **no hace falta**.

### A operativa (oficial reempaquetado, 4.04/4.05) — riesgo **BAJO**
- **Peor caso realista:** corte de cable/batería **después** de «Writing firmware» → conjunto de particiones a
  medias → no arranca → `\updater\mode` persiste → encender y repetir el mismo fichero (precedente 3.26). Si la
  cámara no volviera al actualizador, R48 (SWD) y otra pasada.
- **Peor caso absoluto:** pérdida de energía mientras se escribe el **core de Darwin** (ventana corta, en torno al
  45 % del flujo, donde aparecieron los dos `0x1063`; su duración no está medida) → MCU sin core válido → sin
  `DD_ON` → **ni SWD**; salida = desmontar y `CN4906`. No hay dato de que el MCU tenga banco A/B
  (NO_VERIFICADO). Es el **único** camino a ladrillo de las tres vías (mientras Darwin y `nflasha1` sigan sanos)
  y es idéntico en ellas.
- **Lo que se pierde:** el CFW (menús Silent/PP/Film, Darwin v3, núcleo parcheado) y la numeración sube a 4.04.
- **Camino de vuelta exacto:** reconstruir el CFW que se quiera con versión **> 4.04**
  (`build_package_nflasha15.py … --version 4.05 --darwin-v3`, base `base-film.tar`) y flashearlo. Por eso: **el
  paquete de vuelta se construye y se audita ANTES de flashear** y se deja con su `SHA256SUMS`.

### A2 (A operativa **con** el `nflasha5` de Sony) — riesgo **BAJO**
- Igual que A operativa; añade el arranque en caliente. **Coherente por construcción** (WBI y `/usr` salen del
  mismo paquete 3.21), a diferencia de B.
- **Peor caso:** reanudación desde una instantánea de RAM de fábrica sobre el estado actual (NVRAM y `/setting`
  de hoy) → cuelgue al arrancar → R48 + paquete con versión mayor. No hay medición de este caso
  (**NO_VERIFICADO**); el precedente más cercano (3.48, con WBI y `/usr` distinto) arrancó.

### B (CFW + WBI de Sony) — riesgo **MEDIO** (de quedarse sin arranque; de ladrillo, igual que A)
- **Peor caso:** caliente con el **TOC y la caché del `/usr` de Sony** (`0x8D3B8000`) y un `/usr` distinto en
  flash → metadatos viejos con datos nuevos → cuelgue de la reanudación. Y **no se puede invalidar desde el
  sistema**: `warm.ignore_drop=1` deja `wbi_drop()` inerte; solo otra actualización con `ud_wbi_drop` lo tira
  ([arranque/WBI §2.3 y §6](film-pb-1-sub-arranque-wbi-20261128.md)).
- **Y no arregla lo que se quiere probar:** en caliente el `/usr` del CFW **no se carga nunca** → si H1 fuera
  cierto, B deja la cámara en caliente pero con el `/usr` de Sony otra vez. Sirve para **descartar**, no para curar.
- **Requisito mecánico:** `build_package_nflasha15.py` **por defecto usa `--version 3.39`** → no pasaría el
  guard. Hay que poner una versión > instalada.
- **Camino de vuelta:** otro paquete con versión mayor y `--sin-wbi` (estado actual), o A2.

### C (`libmpr.so` parcheado) — riesgo **MEDIO-BAJO**
- **Peor caso:** el `.so` parcheado en `/usr/lib` rompe el arranque de la app (como 3.92/3.93/3.99) → sin sistema
  normal no hay `pmca` → R48 por SWD. Segundo peor caso: las guardas anuladas meten al reproductor en un estado
  que no espera (p. ej. `MovieReadStart` sin `mp4Ifo_If`) y la app se cuelga al abrir el vídeo → apagar y seguir.
- **Dato a favor (MEDIDO):** `build/cfw_bypass_guardas/libmpr.so` = `63dfaed5…1578`, 10 321 204 B, **8 bytes**
  distintos del de fábrica `9a74a3bb…4c30` (`0x437BFA` y `0x437C2C` → `movs r0,#1 ; nop`), sin relocaciones ni
  ramas que entren en los parches ([bypass-guardas](film-pb-1-sub-bypass-guardas-20261126.md)).
- **Dato a favor (LEÍDO):** `/usr` no valida integridad por fichero; el 3.93 instalado ya lleva 32 ficheros
  distintos de Sony y arranca.
- **Aviso de construcción:** si se añade a mano a `MANIFEST.json["parcheados"]` del árbol `pp`, hay que
  **reconstruir `nflasha15` con `build_nflasha15.py`** (la lista de ficheros que se meten en el ext2 es
  exactamente `MANIFEST["parcheados"]`) y **empaquetar después**; y decidir explícitamente `--sin-wbi`: la cadena
  del CFW lo hace con `sin_wbi=True` codificado en duro; si se construye **sin** `--sin-wbi`, C se convierte en
  B+C (el peor de los dos).
- **Camino de vuelta:** reinstalar el CFW actual reconstruido con versión mayor, o A2.

---

## 7. Recomendación: primer paso de mínimo riesgo que da información útil

**Paso 0 — 0 riesgo, 5-20 min, sin flashear (hacerlo sí o sí):**
1. **Leer la versión instalada** (menú → Configuración → Versión, y `pmca-console.py info` en MTP). Sin esto no se
   sabe qué paquete pasa el guard: es el dato que decide todo lo demás (**NO_VERIFICADO** en el repo).
2. **Prueba de campo gratis:** encender y pulsar reproducción **antes** de que la galería genere miniaturas
   ([STATE](../docs/STATE.md)). Si reproduce solo al principio, el fallo es el mutex de `mp4Ifo_If` y **ninguno**
   de los tres flasheos hace falta.
3. Comprobar que la sonda SWD sigue soldada (si no, «camino de vuelta» = abrir la cámara) y batería ≥ 50 %.

**Paso 1 — el primer flasheo, si el Paso 0 no decide: la vía A, no la B ni la C.**
- **A literal no**: la rechaza el guard. Se usa **A2**: contenido oficial íntegro (incluido el `nflasha5` de
  Sony) con versión > instalada. Motivos, en orden:
  1. **Cero bytes propios en el payload** (el tar sale byte a byte igual al de Sony, §1.3).
  2. **Un solo flasheo responde la pregunta grande**: ¿es el CFW? Si en A2 se reproduce vídeo, el culpable es el
     CFW/el arranque en frío y se acota sin más escrituras; si sigue fallando, se descarta el firmware y el
     siguiente sospechoso es la cámara/tarjeta (H2) — y no se ha gastado ninguna vía arriesgada.
  3. Es la **única** forma de probar H1 con contenido coherente (WBI y `/usr` del mismo paquete). Si se prefiere
     el delta mínimo frente a lo instalado, la variante sin WBI (4.04 ya construida) es igual de segura.
  4. El camino de vuelta está probado y es barato: otro `.dat` con versión mayor.
- **Antes de flashear A2**: construir y auditar el paquete de vuelta (CFW con versión > la de A2), `sha256sum -c`,
  batería llena, cable directo, `systemd-inhibit`, tarjeta fuera si el guard se queja. **Criterio de aborto:** si
  aparece algo distinto de `Initializing… → Updating from A to B → Switching to updater mode → Writing firmware`,
  Ctrl-C **antes** de «Writing firmware» (no se ha escrito nada).

**Paso 2 — solo si A2** ***no*** **cura: C** (8 B en `libmpr.so`) es el siguiente, porque es el único de los tres
que discrimina la hipótesis de las guardas A/B, con un delta mínimo y un `/usr` coherente (cold boot).

**Paso 3 — B al final**, y solo si lo que se quiere medir es el arranque caliente con el CFW: está documentado que
deja el `/usr` del CFW inerte, no se puede deshacer en caliente y añade un estado (WBI de Sony + `/usr` del CFW)
que solo se ha visto arrancar una vez (3.48), sin registro de si reproducía vídeo.

**Regla de oro que se deduce de todo lo anterior:** cada flasheo **sube** `dat4` y **no hay descenso posible sin
escribir `nflasha2`**; por eso el paquete de vuelta se prepara y se audita **antes** de cada intento, y no se gasta
un número de versión sin tener el siguiente ya construido.

---

## 8. NO_VERIFICADO

- **Versión instalada ahora mismo** (3.93 vs 4.02 vs 4.04): decide si 4.04 pasa el guard o hay que reconstruir.
- **Que el guard acepte un descenso**: sin precedente local; la regla medida es «solo mayor» (con `comp` presente).
- **Que la sonda SWD siga soldada** y que el `\updater\mode` se pueda forzar sin volver a abrir la cámara.
- **Que el MCU Darwin tenga banco A/B** o valide el core antes de arrancarlo: es lo que convierte el corte de
  energía en «recuperable» o en «ladrillo».
- **Dónde cae exactamente la escritura de Darwin en el porcentaje de progreso** (los dos `0x1063` fueron al 45 %,
  pero el mapeo progreso↔partición no está trazado).
- **Que un arranque en caliente con WBI de Sony + `/usr` del CFW se cuelgue**: no medido; el 3.48 arrancó en
  caliente con una mezcla equivalente.
- **Que el parche de `libmpr` restaure la reproducción** (o al menos cambie el código de error): no probado ni en
  cámara ni en emulación.
- **Quién copia `0800_appli` a `nflasha17`/`18`** (lente y backup Android): deducido de los nombres de directorio y
  de `mount.conf`, no trazado en `libupdaterbody.so`.
- **Alcance exacto de `uc_mkfs -m app`** (qué particiones FAT formatea en USER): el único dato medido es que
  `-m full` solo formatea `nflasha1`/`nflasha2`; `app` no se ha desensamblado.

## 9. Evidencia reproducible

```bash
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python3 reports/evidence/film-pb-1-sub-riesgo-flash-20261126/verificar-riesgo-flash.py
.venv/bin/python3 reports/evidence/film-pb-1-sub-riesgo-flash-20261126/reconstruir-tar-oficial.py
cat reports/evidence/film-pb-1-sub-riesgo-flash-20261126/extractos.txt   # config.xml, us_mkfs.sh, part_image.sum, script A, guard
```

| Fichero | Qué contiene |
|---|---|
| `verificacion.json` | hashes y tamaños de los tres artefactos (DAT 3.21, DAT 4.04, `libmpr` parcheado vs Sony, 8 B), inventario de los 4 tars base, `hardware_violations` de cada `nflasha3` (**[] en los cuatro**), presencia/ausencia de `updater.sum`/`loader.sum`, `part_image.sum` línea a línea, `nflasha5` idéntico a Sony en los cuatro |
| `tar-oficial-reconstruido.json` | el tar de Sony reconstruido con su propio `nflasha15` da el **mismo** SHA-256 (`identico_byte_a_byte: true`) |
| `extractos.txt` | líneas exactas citadas: `config.xml`, rama USER de `us_mkfs.sh`, `part_image.sum` 3.21, sumas de los 4 tars, `camera_reflash_fw321.sh` numerado, códigos de estado del guard y orden `checkGuard` → `writeFirmware` |
