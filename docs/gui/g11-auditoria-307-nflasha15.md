# G11 — Auditoría del −307 (3.40/3.42) y del `nflasha15` recompuesto (08-11-2026)

Continúa [G10](g10-menu-silent-informe-de-continuacion.md) §3–§4 y [G09 §8d](g09-silent-a6300-menu.md). Offline, sin cámara.
Etiquetas: **VERIFICADO** (bytes/instrucciones) · **MEDIDO** · **INFERENCIA** · **NO DETERMINADO**.
Fuentes: `analysis/camera-dumps/updater-20261020-175427/bootloader.bin` (Loader3 en `0xc01f0000` = archivo `0x22800`, R25),
paquetes no versionados de `analysis/gui/silent-menu-{pkg,fix}/`. Desensamblado con Capstone (Thumb).

## 1. Resultado

1. **Corrección de G09 §8d:** el −307 de Loader3 **no** es «no consigue cargar el kernel/initrd». `0xc01f127a` es el
   traductor de errores al que solo saltan `Init UDIF_P` (`0xc01f686c`) e `Init UDIF_D` (`0xc01f68a4`) desde `0xc01f0d36`.
   Devuelve −202 para −110/−16/−5 y −307 para cualquier otro error distinto de 0 (VERIFICADO).
2. **Las tres fuentes de −307 de Loader3** (`mvn r0,#0x132`; no hay ningún literal −307) están en la inicialización
   `0xc01f0cca` (VERIFICADO). Todas van antes de la selección de modo y de cualquier carga:

   | Dirección | Etapa | Condición |
   |---|---|---|
   | `0xc01f1290` | `Init UDIF_P` / `Init UDIF_D` | el driver devuelve un error distinto de −110/−16/−5 |
   | `0xc01f29e4` | `Reinit BOSS` (`0xc01f2a48` → `0xc01f2994`) | falla la reserva de la tabla MuMin (`[[0xc0001500+0x10]+0x4c]·8`) |
   | `0xc01f2a8a` | `Init BlkDev` (`0xc01f2a4c` → `muminblk_init` `0xc01fd72e`) | `init_mumin` / `init_ext_mumin` / `init_internal_data` / `init_blkdev_if` fallan (`BOS_E:Init MuMin(%d)[%d]`) |

3. **Loader3 solo toca la cabecera y el TOC de `nflasha15`** (VERIFICADO). `muminblk_init` recorre las 30 filas de la
   tabla BOS (`0xc01fe2c4`) y, por cada partición de tipo 3, lee 24 B de cabecera TPZL (`0xc01fe4ec`: magia, `blockSize ≤ 17`,
   `tocOffset`/`tocSize` no nulos y alineados a 4), reserva `tocSize` B y lee el TOC. **El retorno de ese bucle se ignora**
   (`0xc01fd7ce`; `muminblk_init` devuelve el de `init_blkdev_if`). No lee ningún bloque de datos. Cabecera, `tocSize`
   (2373 entradas), `blockSize` y desplazamiento de datos son **idénticos** en el `nflasha15` de Sony, en el del 3.39 y en el
   del 3.40/3.42 (VERIFICADO). Las reservas y la tabla `tulist` (`0xc01fe198`) dependen solo de esos campos.
4. **Conclusión:** por la vía estática, Loader3 no distingue mi `nflasha15` del de Sony. Un −307 emitido por Loader3 **no
   puede deberse al contenido de `nflasha15`** (INFERENCIA fuerte: cubre todo lo que lee Loader3 de esa partición; la parte
   INFO6 de `bootloader.bin` no está adquirida, R25). Contradice la conclusión de G10 §3 («la causa del −307 está en mi
   `nflasha15`») tal como estaba formulada. Las dos lecturas compatibles con lo MEDIDO están en §4.

## 2. Auditoría de los paquetes (VERIFICADO)

* Miembro a miembro del tar (105 miembros): 3.42 = 3.41 salvo `dev/nflasha15` y `part_image.sum`; 3.40 = 3.42 + Darwin v3.
  El `nflasha15` del 3.40 y el del 3.42 son el mismo (`ffe8bf83…`, 84 691 456 B). 3.43 = 3.41 + Darwin v3.
* `nflasha15` del 3.40 descomprimido frente al de Sony (`rdump` completo + `diff -r`): difieren **exactamente los 27
  ficheros** del manifiesto (`CautionConfig.so`, `viewUnified2.so`, 25 `string_*.uxc`). `e2fsck -fn`: solo contadores de
  libres desfasados (esperado, bloque 0 = Sony). Cabe en la partición (100 MiB).
* Registros TPZL de los bloques recompuestos (2607 LZ77 y 49 almacenados) frente a los 37 968 de Sony: no aparece ninguna
  propiedad ausente en Sony (terminador, posición del fin en el grupo, códigos de longitud, distancias ≥ 0xF00 sin llegar a
  0xFFF, solapes, coincidencias desde el inicio del registro, registros LZ ≤ 4095 B, relleno a 0). Mismo codificador en el 3.39 y en el 3.40 (`tpzl.py` sin cambios desde el 04-11).
* **Los offsets se mueven:** el 3.40/3.42 desplaza 1779 entradas del TOC a partir del bloque 594, y el 3.39 1377 a partir
  del 996. El `nflasha3` del CFW 3.38, que arranca, no mueve ninguna (3 bloques cambiados, mismos tamaños). Pero los 53
  módulos de `/usr/kmod` (bloques 1679–1722) y 164 de las bibliotecas también estaban desplazados en el 3.39, que cargó el
  kernel, los módulos y llegó a `stella`. **Un TOC desplazado no impide leer `/usr`** (descartado como causa).
  Entre el 594 y el 995 solo hay `share/app/*` (60), firmware Wi-Fi, `tool/*` y `lib/libmpr.so`.

## 3. Defecto encontrado: permisos de los ficheros sustituidos (CORREGIDO)

`build_nflasha15.replace_files` escribía `set_inode_field … mode 0o100555` (formato `:#o`). `debugfs` no admite el prefijo
`0o`, rechaza el comando («Couldn't parse») y sale con 0, así que el modo quedaba en el del fichero del host:
**3.39 y 3.40/3.42: `.so` 0555 → 0644, `.uxc` 0755 → 0644** (VERIFICADO en las dos imágenes). uid y gid sí se conservaban.
Como el 3.39 tenía el mismo defecto y cargó `viewUnified2.so`, **no explica la diferencia con el 3.40** (INFERENCIA: el
`dlopen` de Linux no exige el bit x). Corregido: modo `0{…:o}` y comprobación posterior de modo, uid y gid (`debugfs -f` no
informa de errores). Regresión: `tests/test_gui_build_nflasha15.py`. Los paquetes 3.39–3.42 **no** se han reconstruido.

## 4. Qué pudo pasar (NO DETERMINADO; por orden de compatibilidad con lo MEDIDO)

| Hipótesis | A favor | En contra / falta |
|---|---|---|
| **H1: fallo en el espacio de usuario**, ahora en el código del menú. Con los ids corregidos, `im.elf` supera el assert del 3.39 y ejecuta más código parcheado (`viewUnified2`/`CautionConfig`, solo probados en `qemu-user`). El sistema se apaga y el LED no sería de Loader3, o lo sería en un reinicio posterior | El único cambio frente al 3.41 está en `/usr`, que Loader3 no lee (§1). Mismos síntomas USB que el 3.39 («Charger» `054c:0994`, sin Wi-Fi) | No hay log: en el 3.40 se sacó la batería antes de leer `0x83400000` por SWD. El patrón 3+7 nunca se filmó ni se cronometró (R13 §5) |
| **H2: −307 real de Loader3 por una causa ajena a `nflasha15`** (UDIF o MuMin de la NAND, p. ej. en un rearranque en caliente con `ddr = 1`, que pasa a `muminblk_init` el indicador de reanudación) | El CPU no era depurable y el SoC se apagaba solo | No explicaría que el 3.41 y el 3.43 arranquen y el 3.40 y el 3.42 no. Solo cuadra si coincide con H1 (el usuario cae y provoca el rearranque) |

G10-D («por qué Loader3 depende de `nflasha15`») queda resuelto: no depende, salvo la cabecera y el TOC, que no cambiaron.

## 5. Siguiente (decisivo y barato; cada instalación requiere autorización)

1. **Antes de tocar nada tras el próximo fallo:** sin sacar la batería, leer por SWD el log de AP0 (`0x83400000`, método de
   R51/G09 §8c) y filmar el LED con el contador de fotogramas. Basta para elegir entre H1 y H2.
2. Aislar con un solo cambio por paquete (G10-A reformulado), reconstruidos con el constructor corregido: (a) solo los 25
   `.uxc` (si falla, el problema está en los recursos o en la recompresión); (b) `.uxc` + `CautionConfig.so`;
   (c) todo. Versión ≥ 3.44.
3. (Offline) Repetir en `qemu-user` el camino de `im.elf` posterior a la búsqueda de recursos, con los ids nuevos.

## 6. Verificación estática de los ficheros cambiados (08-11-2026)

Sobre `analysis/gui/silent-menu-fix/files/` (el contenido del 3.40/3.42) frente al 3.21 de Sony.

### 6.1 Sin defecto (VERIFICADO)

| Pieza | Comprobación |
|---|---|
| `viewUnified2.so` (ELF) | Fuera del segmento nuevo solo cambian 27 bytes: `e_phoff`/`e_phnum`, los 5 literales, los 5 `movs r2,#N` y `DT_REL`/`DT_RELSZ`. El `PT_LOAD` nuevo (`0x4d0000`, RW) está alineado y es congruente con su offset; los `PT_LOAD` siguen en orden ascendente; la tabla de cabeceras cae dentro del segmento; no hay `PT_PHDR` ni `GNU_RELRO`; `DT_RELCOUNT` sigue siendo válido (se añade al final) |
| Páginas | Resolviendo las relocaciones con los símbolos de `CautionConfig.so`, cada página nueva = la original con `RootSilentShutter` insertado justo antes de `RootCustomFrontCurtainShutter`. Cada array tiene una sola referencia en `.text`, que es la parcheada, y ningún puntero en datos. El literal y la cuenta van al mismo `CmnViewSettingNode(nodo, hijos, cuenta, props)` |
| Relocación nueva | `R_ARM_ABS32` contra `cmnViewSettingNodeRootAelWShutter` + 0xEB0 = `cmnViewSettingNodeRootSilentShutter`. Una sola definición en `/usr`, ninguna relocación `R_ARM_COPY` en `bin/` ni en `lib/` |
| `CautionConfig.so` | 13 bytes distintos, todos dentro de las tres listas. El nodo usa la clase genérica `CmnViewSettingNode` (sin código propio). Las listas van ordenadas por id: `_getPropertyIndex` hace una búsqueda binaria. Valores coherentes con el EFCS (`Silent On` = 1 = `EFCS Off`) |
| Propiedades `0xb`/`0xc` | La raíz nueva no las tiene (todas las raíces que se muestran sí). Los 14 lectores de `viewUnified2.so` inicializan la salida a −1 antes de la llamada virtual (`vtable+0x58/0x60`), y −1 no activa ninguna rama: es inocuo |
| `.uxc` (25) | Solo se añaden 3 registros, sin perder ninguno. La cabecera no cambia y sigue siendo válida (5958 ranuras), los índices caben en 16 bits y los ids de ayuda viven en `string_*.uxc`, no en `*_guide.uxc`. El glifo U+E08C de la etiqueta ya lo usan 38 textos del A6000 |

### 6.2 Riesgos no descartados (INFERENCIA; candidatos para el fallo del 3.40)

1. **Reutilización de un nodo vivo (R1).** `cmnViewSettingNodeRootSilentShutter` es en la A6000 un nodo de tipo SteadyShot con
   ProcessId `0x26`. Aparece en el registro maestro `cmnViewSettingNodesRootDefault` (206 raíces, solo lo lee `viewUnified2.so`)
   y en la lista de funciones de `viewUnified7.so` (`0x5f7b8`, entre `FacePriorityTracking` y `StillSteadyShot`;
   INFERENCIA: lista de funciones asignables). El parche hace desaparecer el ProcessId `0x26` de todo `/usr` y convierte esa
   entrada en un segundo `0x46`. Si un ajuste guardado (tecla personalizada, menú Fn) o el código busca `0x26`, la búsqueda falla.
   Sin verificar.
2. **Páginas de 7 entradas (R3).** Las páginas 2 y 5 pasan a 7. Las 4 páginas de 7 que trae Sony mezclan entradas excluyentes
   (AF por contraste o por fase), así que nunca muestran 7 visibles. No se sabe si la vista admite 7; depende de si
   `TouchShutter` / `ExposureCompSaveReset` están ocultas en la A6000.
3. **ProcessId `0x46` duplicado (R2), débil:** el registro de Sony ya tiene 6 ProcessId repetidos.
4. **Idiomas no latinos (G10-C):** sin los ids nuevos; solo afecta si la cámara está en uno de ellos.

### 6.3 Paquetes de aislamiento propuestos (sustituyen al orden de §5.2)

* (a) `CautionConfig.so` + `.uxc`, **sin** tocar `viewUnified2.so`: prueba R1 sola (el nodo cambia, pero no se añade a ningún menú).
* (b) (a) + `viewUnified2.so` solo en las páginas 1, 3 y 4 (pasan a 6 entradas): prueba R3.
* Diseño alternativo si R1 se confirma: no reutilizar el nodo `0x26`; construir un nodo nuevo en el segmento añadido.

## 7. Paquete 3.44a construido (08-11-2026, offline; instalación NO autorizada)

Variante (a) de §6.3: **3.43 + `nflasha15` con `CautionConfig.so` y los 25 `.uxc`; `viewUnified2.so` de Sony** (la entrada no
se añade a ningún menú; prueba R1 sola). Frente al 3.43 instalado solo cambian `dev/nflasha15` y `part_image.sum` (VERIFICADO).

| Dato | Valor |
|---|---|
| Ficheros | `analysis/gui/silent-menu-fix/files-344a/` (26), `nflasha15.344a` (84 075 008 B, CRC `16376ae4`, 88 bloques recompuestos, bloque 0 = Sony) |
| `.dat` | `analysis/gui/silent-menu-fix/pkg-3.44a/package-3.44/firmware_packed.dat`, SHA-256 `040645f5a6654af5bb0734f931b6d760bc0801f0c1a2c14bca4b1845069a1ed2` (no versionado) |
| Auditoría | [`analysis/gui/audit-3.44a.json`](../../analysis/gui/audit-3.44a.json): **23/23 OK** (las de antes + `ext2.modo_uid_gid_como_sony`, nueva) |

La comprobación nueva del auditor falla en el 3.40 (25 ficheros con el modo cambiado), así que habría detectado el defecto de §3.

**Lectura del resultado en cámara:**
* No arranca → la causa está en `CautionConfig.so` (nodo `0x26` reutilizado, R1) o en los `.uxc`; el siguiente paso sería separarlos.
* Arranca, sin entrada nueva en el menú (esperado); comprobar que SteadyShot y el EFCS siguen igual → R1 queda descartado como causa de arranque; probar la variante (b).
* En cualquier fallo: G11-LOG antes de sacar la batería.

## 8. 3.44a en cámara: no arranca; fallo capturado en Loader2; recuperada con 3.45 (08-11-2026)

**Instalación (MEDIDO):** 3.43 → 3.44 por USB, `Done` en un intento (`install-3.44a.log`).

**Síntomas (MEDIDO, usuario y USB):** ciclo de ≈ 40 s con `054c:0994` («modo carga») y ≈ 30 s sin dispositivo; la pantalla
parpadea dos veces («como que lo intenta»); después, LED rojo **1 muy lento + 2 lentos + 1 rápido**.

**Decodificación (R13 §2):** grupos LDR2 (2 s) / LNG (0,5 s) / SHT (0,25 s) → 1/2/1 → n = 1201. Solo Loader2 añade el pulso LDR2
(`n = 1000 + |err|`) → **error −201 de Loader2** (INFERENCIA fuerte: el orden se dedujo del ciclo observado). En Loader2 el −201
solo sale de `0xc00305c0` (`Init BOSS`: MuMin, información, carga de BOSS o reinicio) y de `0xc003074c`
(`BOS_E:Load page(%d <-> %X)`: la página leída no es la pedida) (VERIFICADO). Loader2 tiene además el mismo traductor UDIF que Loader3
(`0xc00303f0`, −202/−307); el «3 lentos + 7 rápidos» del 3.40 podría ser un 1/3/7 de Loader2 con el pulso largo no visto (NO VERIFICADO).

**SWD (solo lectura, autorizado; [`analysis/camera-dumps/20261108-swd-344a/`](../../analysis/camera-dumps/20261108-swd-344a/)):**
* Con la cámara en el ciclo, el DP responde a ratos y el MEM-AP da `stalled AP operation`: el log del kernel (`0x83400000`) **no
  se pudo leer**.
* En un encendido, parada corta de la CPU: **PC `0xc00310e0` en Loader2** (espera activa del temporizador), llamada desde
  `0xc00332be`: espera de un evento de MuMin con tiempo límite (devuelve −10003 si se agota). Volcado de 1 MiB de eSRAM por la
  CPU (no versionado).
* **Búfer de log de Loader2 en la eSRAM** (`0xc0060000`, `loader2-log-0xc0060000.txt`): `Init UDIF_P/D`, `InfSec_S` y
  `BOSS` correctos, `Load InfSec_N` (`BK:2 PG:0`) y `Load LBkup` (`BK:2 PG:8`) correctos, y se queda en
  **`LDR:Load LDR3` → `BOS:Load[DI:0 PL:0 BK:2 PG:21 SZ:43 MEM:C01F0000]`**: **Loader2 no termina de leer Loader3 de la NAND**
  (bloque 2 de `nflasha0`, la zona de arranque, que el actualizador no escribe).

**Recuperación (MEDIDO):** R48 en el arranque siguiente; esta vez Loader2 sí cargó Loader3 (BP en `0xc01f0000` a 107 ms),
2 comprobaciones forzadas, BootMode 3 y entrada al actualizador. 3.45 (= 3.43, mismo tar): primer intento `0x1063` al 45 %;
tras apagar y encender con el interruptor, `Done`. **Arranca normal, firmware 3.45.**

**Interpretación:**
* La UI no explica el fallo: el 3.44a no toca `viewUnified2.so` y falla igual (R3 descartado como causa de arranque). Quedan
  `CautionConfig.so` (R1), los `.uxc` o el hecho de escribir un `nflasha15` recompuesto. Recuento: 3/3 paquetes con `/usr`
  recompuesto no arrancan (3.40, 3.42, 3.44a) y 3/3 con el `/usr` de Sony sí (3.41, 3.43, 3.45).
* El fallo capturado está **antes de Loader3**, en la lectura NAND del bloque 2, y es **intermitente**: la pantalla se encendió
  en intentos anteriores y el arranque de R48 cargó Loader3 sin problema. No hay mecanismo estático conocido por el que el
  contenido de `nflasha15` afecte a esa lectura (NO DETERMINADO). Hipótesis por comprobar: fallo en Linux/espacio de usuario
  con apagado anómalo que deja la NAND o el controlador en un estado que Loader2 tarda en superar, o efecto de Darwin cortando la
  alimentación a mitad de un arranque.
* Siguiente prueba decisiva y barata: separar `CautionConfig.so` de los `.uxc` (3.46 = solo `.uxc`; 3.47 = solo
  `CautionConfig.so`) y, en el fallo, la misma captura SWD del log de Loader2 y, si es posible, del de Linux.
