# G10 — Menú «Silent Shooting» estilo A6300: informe de estado para continuar (08-11-2026)

Resume G09 (§5–§8d) para retomar la tarea. Etiquetas: **VERIFICADO** (bytes/pruebas) · **MEDIDO** (en cámara) · **INFERENCIA** · **NO DETERMINADO**.

## 1. Objetivo
Añadir al menú de la A6000 (fw 3.21 base) una entrada «Silent Shooting» como la de la A6300, **sin sustituir** el EFCS: escribe el mismo ajuste que el CFW ya hecho (ProcessId `0x46`, Off = 0 EFCS/mecánica, On = 1 electrónico; sin Shutter Type ni cambios en `av-cam`).

## 2. Qué existe (todo en el repositorio)
| Pieza | Fichero | Estado |
|---|---|---|
| Parche de inserción de la entrada en 5 páginas de `viewUnified2.so` (segmento `PT_LOAD` nuevo, relocaciones, literal y `movs r2,#N` de `_INIT_70`) | `scripts/gui/add_menu_entry.py` | VERIFICADO con `qemu-user` + gdb |
| Nodo `SilentShutter` de `CautionConfig.so` (listas 3/4/4 propiedades) y textos en 25 idiomas latinos | `scripts/gui/build_silent_menu_test.py` | VERIFICADO offline; **corregido 08-11** (§3) |
| Editor de `string_*.uxc` | `scripts/gui/uxc_strings.py` | `build` rechaza ids sin ranura (regresión incluida) |
| Reconstrucción de `nflasha15` (TPZL de ext2) y paquete `.dat` | `scripts/gui/build_nflasha15.py`, `build_package_nflasha15.py` | VERIFICADO; bloque 0 = Sony |
| Auditoría independiente del `.dat` | `scripts/gui/audit_package_nflasha15.py` | 3.39: 23/23; 3.40: 22/22; 3.42: 20/20 |
| Pruebas | `tests/test_gui_uxc_strings.py` | 8 pasan |

## 3. Historial en cámara (MEDIDO)
| Paquete | Contenido | Resultado |
|---|---|---|
| 3.39 | menú (ids de texto de la A6300) + Darwin v3 | Arrancó Linux, **pantalla negra**. SWD: kernel vivo; log de RAM: `E/stella(148): assert src/ResourceManager.cpp(954)`. Causa: los ids `0xf840/0xf847/0xf849` están fuera de las 5 958 ranuras del índice de texto del A6000 (VERIFICADO offline; que sea la causa única es INFERENCIA fuerte) |
| 3.40 | menú corregido (ids `0xf3e8/0xf515/0xf56a`) + Darwin v3 | **No arranca**: LED 3 lentos + 7 rápidos = −307 de Loader3 (no carga kernel/initrd, INFERENCIA por orden de parpadeos) |
| 3.41 | 3.38 con `/usr` de Sony (vuelta atrás) | Arranca, firmware 3.41 |
| 3.42 | menú corregido, **sin** Darwin v3 | **No arranca** |
| 3.43 | 3.38 + `/usr` de Sony + Darwin v3 | Arranca (ver [R84](../capture/e26-r84-darwin-v3-en-camara.md)) |

> **Corrección (08-11-2026, [G11](g11-auditoria-307-nflasha15.md)):** Loader3 solo lee la cabecera y el TOC de `nflasha15`, idénticos a los de Sony, y el −307 sale de su inicialización (UDIF/MuMin), no de la carga del kernel. El `nflasha15` sigue siendo la única diferencia del paquete, pero su efecto tiene que producirse en Linux (H1) o el −307 tiene otra causa (H2). G10-D queda resuelto. Además, los ficheros sustituidos quedaron con modo 0644 (defecto del constructor, ya corregido).

**Conclusión (INFERENCIA, no aislada):** como el 3.42 difiere del 3.41 solo en `nflasha15` y falla, y el 3.43 con Darwin v3 arranca, **la causa del −307 está en mi `nflasha15` recompuesto** (o en cómo el cargador/LDEC lo lee), no en Darwin. Por qué Loader3 depende de `nflasha15` no se ha explicado (se esperaba que solo lo leyera Linux al montar `/usr`).

## 4. Hipótesis a probar (por orden de coste)
1. **Bloques recompuestos:** el 3.39 tenía 134 bloques recompuestos y llegó a Linux; el 3.40/3.42 tienen 165 (más idiomas/ficheros cambian de tamaño). R55 ya vio que el LZP/LDEC de Linux es sensible al contenido del bloque 0. Probar variantes **con menos bloques cambiados**: solo `viewUnified2.so` + `CautionConfig.so` + `string_english.uxc`, y luego el resto de idiomas.
2. **Bloque 0:** el 3.39 y el 3.40 tienen el bloque 0 idéntico al de Sony; descartado como diferencia entre ellos.
3. **Relación con la instalación:** los primeros intentos del 3.40 y 3.41 cayeron al 45 % con `0x1063` (NG de Darwin) tras abrir la sonda; el reintento limpio dio `Done`. El 3.42 se instaló de una vez y tampoco arrancó, así que la instalación por sí sola no lo explica.
4. Averiguar con REA/`bootloader.bin` por qué Loader3 lee `nflasha15` (cadena `Load vmlinux/initrd … in %s`, función `0xc01f127a`).

## 5. Recuperación (probada, 4 veces)
1. Interruptor OFF; batería fuera 10 s y dentro con interruptor OFF (a veces el SoC sigue alimentado: la batería fuera lo corta).
2. OpenOCD con `analysis/e26-recovery/r48_updater_swd.cfg` (un solo proceso; si la sonda se reenumera, `kill -9` del viejo).
3. Encender una vez; el script termina con «actualizador en marcha». Conectar el USB (`054c:03e2`).
4. `pmca-console firmware -f …/firmware_packed.dat`. El primer intento tras abrir la sonda cae al 45 % con `0x1063`; apagar, encender **sin sonda** y reintentar da `Done`.
5. Base segura: `analysis/gui/silent-menu-fix/pkg-3.41-revert/package-3.41` (SHA-256 `9cccdfdd…`; el actualizador solo acepta versiones mayores: la siguiente de vuelta atrás necesita ≥ 3.44).

## 6. Estado de la cámara y artefactos
* Firmware instalado: **3.43** (con Darwin v3, `/usr` de Sony; sin menú Silent). EFCS off + silent del CFW sigue funcionando.
* Paquetes (no versionados, `analysis/gui/silent-menu-fix/`): `pkg-3.40`, `pkg-3.41-revert`, `pkg-3.42`, `pkg-3.43-darwin`, `nflasha15.silent`, `files/`, `audit-*.json`, logs `install-*.log`.
* Evidencias versionadas: `analysis/camera-dumps/20261107-swd-339-pantalla-negra/`, `analysis/gui/audit-3.39.json`, `audit-3.40.json`.

## 7. Pendientes
| ID | Pendiente |
|---|---|
| G10-A | Aislar el −307: paquete con solo 3 ficheros cambiados (hipótesis 1) |
| G10-B | Probar la UI con el menú (nunca se ha ejecutado con el arreglo de ids) |
| G10-C | Idiomas no latinos (8, tabla de 32 bits, sin parsear): sin los textos nuevos pueden repetir el assert |
| G10-D | Explicar por qué Loader3 depende de `nflasha15` |
Cada instalación requiere autorización expresa y deja la cámara en riesgo de usar el procedimiento de §5.
