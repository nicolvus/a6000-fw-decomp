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
