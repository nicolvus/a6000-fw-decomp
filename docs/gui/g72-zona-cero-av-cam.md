# G72 — Auditoría de la «zona a cero de 2,3 MB» de `av-cam.bin` (15-11-2026)

**Veredicto: (B) INSEGURA para HLG (`0x43F9C000`) y LUT (`0x43FA4000`); Color Chrome (`0x43FB7C00`) es SEGURA.** HLG y LUT quedan bloqueados (`ZONA_VERIFICADA = False`) hasta reubicarlos.

## 1. Mapa de carga (VERIFICADO)
- `av-cam.bin` (11 427 236 B) se carga entero en `0x43541000` (físico `0x83541000`, `Param:adrs=83541000` del `klog`). Sin tabla de secciones (el ELF `av-cam-analysis-view.elf` es una vista sintética de un solo `.text`).
- La cabecera LIRO que lee el driver del kernel (`klog` real, p. ej. `20261110-swd-369/klog.txt`): `ram 43fa8f00 + 0x75fe4`, **`bss 43cfe37f + 0x244d5a` (= `0x43cfe37f…0x43f430d9`)**, `tail 4409ce00`, `limit 44140ffc` (campos `+0xb8…+0xd0` del fichero). La suspensión hace `cp_backup (43f430d9-4409ce00)`: lo que sigue al `bss` hasta la cola se respalda y restaura (memoria viva, no relleno).
- La «zona a cero» (`0x43d620d9…0x43fa8f00`, 2 387 495 B de ceros en el fichero) está **dentro** de la imagen cargada y solapa el `bss` declarado y los datos respaldados: es `.bss`/datos de módulo con relleno a cero, no hueco de alineación.

## 2. Evidencia dinámica (VERIFICADO, la decisiva)
Volcado de RAM de la cámara real en marcha (`analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin`, fw 3.21; el código `0x43541000…0x43d62100` es idéntico al fichero, 2081/2081 páginas):
- En la zona (a cero en el fichero) hay **508 877 B no nulos** y ningún bloque de 64 KiB queda vacío (3,5 KB…65 KB por bloque).
- `HLG` `0x43F9C000…0x43F9F060`: **145 B no nulos** (53 rangos, p. ej. `0x43f9c53d`). `LUT` `0x43FA4000…0x43FA54FC`: **402 B no nulos** (260 rangos). Un parche allí se corrompe por escritura del firmware (y a la inversa).
- Color Chrome `0x43FB7C00…+0xD0`: ceros en el fichero y en vivo (el hueco de G18 `0x43faf28c…0x43fb8ee0` es idéntico fichero/vivo, 40 020 B).

## 3. Evidencia estática (VERIFICADO)
- `movw/movt` (712 pares) dentro de la zona: variables globales en `0x43e318b8`, `0x43e337e0`, `0x43f35a88…0x43f38fe4`, `0x43f5d168…0x43f5e27c` (≈ 70 direcciones), `0x43fa8da4…0x43fa8eb8`; y **`0x43fa4b1e`** (`0x439cc660`: byte `completed` de `__do_global_dtors_aux`), que cae dentro de la tabla LUT2 (`0x43FA4854…0x43FA4EA8`). Los tests antiguos (s144, `0x43FA29F0` `MountSTAT`, `0x43FA2D23` `Flg`) también las usan como variables.
- Hueco de G18 (`0x43faf000…0x43fb9000`): 0 referencias `movw/movt` (se suma a los 7 métodos de G18).

## 4. Qué se hizo
- `pp_curves_patch.patches(hlg=…)` y `lut_patch.apply_bytes` lanzan `RuntimeError` salvo `ZONA_VERIFICADA = True` (solo los tests y la autocomprobación de bytes lo fuerzan). Tests: `tests/test_g67_hlg.py`, `tests/test_g71_lut.py` (+ test de bloqueo).
- No se movieron los parches: **no se halló sitio libre verificado**. Huecos reales medidos: el de G18 está lleno; `0x43be3b28` (2 056 B) y `0x43c1ff21` (3 435 B) son ceros idénticos fichero/vivo pero suman 5 491 B (< 5 564 B de la LUT y < 12 384 B de HLG). Un barrido de «funciones sin referencias» dio falsos positivos (cabeceras PIC mal recortadas), así que no se afirma código muerto.

## 5. Siguiente
Reubicar con espacio verificado (código muerto como G61, o 1 sola curva HLG de 4 122 B + LUT reducida) y quitar el bloqueo; hasta entonces HLG-2 y LUT-C siguen ABIERTOS (ver PENDIENTES).
