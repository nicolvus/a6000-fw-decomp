# E26-R84 — Parche Darwin v3 en cámara: la NVRAM llega a Darwin (08-11-2026)

Continúa [R82](e26-r82-parche-efcs-v3.md) y [R83](e26-r83-informe-final-efcs-negro.md). Etiquetas: **VERIFICADO** · **MEDIDO** · **INFERENCIA** · **NO DETERMINADO**.

## 1. Resultado
Con el 3.43 instalado y una tabla de prueba en la NVRAM, **EFCS activado deja de salir negro, incluso a 1/4000** (MEDIDO, el usuario). Cierra la premisa «nunca probada en cámara» de R66 §1/R82 §1: escribir `0x1850000+0x48` **sí cambia lo que hace Darwin**, y el parche de R82 (vía A, reescritura en sitio de `0x18d6e..0x18e0f`) funciona con el cargador de Darwin de la cámara.

## 2. Qué se instaló
Paquete **3.43** = 3.38 (CFW base) + `/usr` original de Sony + Darwin v3. Frente al 3.38 cambian solo `0640_darwin/darwin_core.bin` y `0641_darwin_sum/darwin.sum` (VERIFICADO: sumas 66/66, `darwin_core` = `efcs_tabla_diff` del 3.38, `nflasha15` = Sony). SHA-256 del `.dat`: `56e21d4abb2d6a75fbb080df6bced291ad15692c3623ddc2442706a3d885760d` (no versionado, `analysis/gui/silent-menu-fix/pkg-3.43-darwin/`).
Instalación: primer intento `0x1063` al 45 % (NG de Darwin, tras abrir la sonda SWD), segundo `Done` (3.42 → 3.43). La versión de Darwin instalada no se leyó, pero el comportamiento de §1 solo se explica con el core parcheado.

## 3. Cómo se escribió la tabla
`scripts/senser_efcs_table_write.py` (nuevo): service mode de PMCA, lee la NVRAM en memoria (sin volcado a fichero, por orden del usuario), exige región `CX77500_E38`, `G+0x42 = 3407` y una tabla conocida, cambia solo `G+0x48..0x7f` (56 B), recalcula el checksum, escribe, relee y sincroniza a flash. Sin `--execute` solo lee y muestra. Opciones: tabla del modelo R82 (defecto), `--zero` (neutra, reversión), `--test` (una entrada `{Tmax=30000, c=2000}`: 2000 µs a todas las velocidades).
Notas de uso (MEDIDO): al entrar en service mode la primera vez expira («Operation timed out») pero la cámara sigue cambiando; **repetir el comando** cuando aparece como `054c:0336`. Al terminar (`Done`) la cámara se apaga o reinicia sola: hay que encenderla con el interruptor antes del siguiente comando.

## 4. Secuencia de pruebas (MEDIDO)
| Tabla en NVRAM | Resultado |
|---|---|
| Modelo R82 (11 entradas, c = 24–1374 µs) | Persistió tras reiniciar (releída). El usuario: con EFCS activado **no salió** la foto buena (sin cuantificar; a 1/1000 negra como antes) |
| `--test`: c = 2000 µs a todo | **No sale negro; se ve hasta 1/4000.** A 1/4000 la exposición efectiva ≈ 244 − 1250 + 2000 ≈ 1000 µs, unas 4× la nominal |
| (estado final de la sesión) | **`--test` sigue escrita en la NVRAM** |

## 5. Interpretación
* **VERIFICADO en cámara:** la NVRAM llega a Darwin; el parche v3 aplica `c` por velocidad.
* **INFERENCIA:** con la tabla del modelo la foto a 1/1000 seguía mal porque la pérdida real es **mayor** que la modelada (R74/R80: 1,26 ms) o porque el degradado vertical (R83 §5) hace que la parte baja siga oscura; ambas se resuelven calibrando, no cambiando de vía.
* **NO DETERMINADO:** la causa física de la pérdida (R83: probable obturador/circuito, confianza media). El parche compensa, no repara. Útil de 1/1000 hacia abajo; 1/2000 y 1/4000 no corrigen el degradado arriba/abajo (R83 §5).
* El EFCS off + silent del CFW no se vio afectado.

## 6. Cómo continuar (calibrar la tabla)
1. (Opcional, con autorización) volver a la tabla del modelo (`senser_efcs_table_write.py --execute`) para partir de un `c` conocido, o calibrar partiendo de `--test` (`c = 2000`; el script de calibración usa el `c` aplicado, que hay que indicar).
2. Fotos **RAW (ARW) a ISO 100**, misma escena y luz, EFCS activado y desactivado, a 1/4000, 1/2000, 1/1000, 1/500, 1/250 y 1/125 (una foto por velocidad y modo; dos si se puede). Leerlas desde la tarjeta (la cámara aparece como almacenamiento masivo) con `scripts/camera_raw_exposure.py` (mide luminancia lineal por canal CFA y por bandas).
3. `scripts/e26_r76/e26_r76_calibrar_efcs.py ajustar ON.json OFF.json [--previo TABLA.json --previo-on ON1.json] --out TABLA.json`, y escribir la tabla resultante con el escritor (hay que añadir una opción `--tabla TABLA.json`; hoy solo trae modelo/zero/test).
4. Repetir una vez para refinar (el calibrador amortigua 0,8 por iteración).
5. Reversión: `--zero` (parche neutro) o reinstalar 3.41.

## 7. Pendientes
| ID | Pendiente |
|---|---|
| E26-R84-CALIB | Calibrar la tabla con fotos RAW (§6); el escritor necesita `--tabla` |
| E26-R84-ESTADO | Dejar una tabla razonable en la NVRAM: ahora `--test` (sobreexpone mucho) |
| E26-R84-DARWINVER | Leer la versión/estado de Darwin instalada (no se leyó) |
| E26-R74-FISICO | Sigue abierto: pruebas físicas del obturador (R83 §6.1) |
