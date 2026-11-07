# E26-R62 — Auditoría de datos estáticos y volcados del fallo EFCS (05-11-2026)

> **Corregido por [R66](e26-r66-bloques-darwin-en-nvram-1850000.md) y [R69](e26-r69-revision-informes-efcs.md):** §3, BK4 `0x30100` **no** es la copia del estado de Darwin (la relectura va a las propiedades `0x1850004/05`; solo 181 de 512 B coinciden): es una tabla del BIONZ que da `pkt[0xa..b]`. §4, `s8[B+0xc6..c8]` = 29/37/35 (no 0) y el término `G+0x42` solo se suma a `ip` con EFCS desactivado. Con EFCS activado se resta de `S+0x48` (R65). §2, el umbral 5–8 ms no viene de Darwin (R66 §3).

Solo lectura: EXIF de las fotos guardadas, 25 volcados BK4, Capstone sobre `darwin_core.bin` 3.21 (base `0x4200`) y `av-cam.bin` 3.21 (base `0x43541000`), REA (sesión `r62`, cerrada). Sin cámara ni escrituras.

Etiquetas: **VERIFICADO** (bytes/código/EXIF) · **MEDIDO** (fotos existentes) · **INFERENCIA** · **NO VERIFICADO**.

## 1. Correcciones a afirmaciones previas

| Afirmación | Resultado | Evidencia |
|---|---|---|
| R57 §8: `DSC03482` (1/60) es EFCS activado | **Falso**: EXIF `MakerNote ElectronicFrontCurtainShutter = Off`. La serie EFCS activado real es `DSC03496–03504` (1/90–1/1500); `03505–03514` es la desactivada | exifread (etiqueta de Sony; sale igual en las 66 ARW de la papelera) |
| «No hay fotos con EFCS entre el 20-10 y el 03-11» | **Hay 71 con EFCS = On** (26-10 T024 y 27-10 T044/T046/T047), pero con firmware o Darwin modificados (Darwin tipo 0 en 3.22; 3.23 B1a). No sirven como referencia del firmware original. Ninguna anterior a T024 (26-10 23:29) | `analysis/camera-dumps/20261026-T024-darwin-tipo0/fotos`, `…T044-raw-iso100`, `…T046…`, `…T047…` |
| El reloj se reinició el 26-10 | Entre `DSC03113` (26-10 23:36) y `DSC03114` (fecha 2014-01-01): pérdida del RTC tras T024 | EXIF |
| R58 §7: «el BIONZ envía a Darwin lo mismo a 1/500 y 1/125» | Cierto, pero **solo se capturó EFCS activado**. Nunca se ha leído el paquete con EFCS desactivado, así que «Darwin no recibe marca de EFCS» **no está demostrado** | `20261105-bionz-swd-disparos/bionz_shot1/2.txt` |
| R58 §8: «NVRAM idéntica al original → descartada» | El usuario confirma (05-11) que las fotos se hicieron **tras reiniciar**: el BK4 restaurado sí estaba activo en el BIONZ. Pero Darwin tiene SRAM siempre alimentada (E24-05 §5); un reinicio normal no la borra, y el volcado tras apagado limpio muestra `0x30100` reescrita con el estado de Darwin (§3). El estado interno de Darwin no se restauró salvo que se quitara la batería | §3 |
| R60: «`sl` no es la palanca» | Límite no resuelto: la escritura por SWD se verificó releyendo DRAM, no la caché de instrucciones (riesgo (c) del propio R60). Un resultado nulo puede ser código no ejecutado | R60 §3 |
| «Código de Darwin idéntico al original» | Verificado solo para el `darwin_core` del paquete (3.37 = `tar_oficial`). La flash de Darwin no se ha leído, y el arranque `0x0000–0x41ff` no está en ningún paquete ni volcado | `manifest-recuperacion-337.json` |

## 2. La pérdida depende del tiempo de exposición, no es un retardo fijo (MEDIDO)

Series `DSC03496–03514` (3.37 oficial, ISO 12800, misma escena), 10 franjas de arriba abajo, normalizadas con on/off a 1/90 y 1/125 (k = 1,058; R57 usó 1,067 con la foto mal etiquetada):

| T (ms) | δ global | δ por franja (ms, arriba → abajo) |
|---|---|---|
| 1,33 | 1,24 | 1,12 … 1,54 |
| 2,00 | 1,32 | 1,15 … 1,64 |
| 2,86 | 1,30 | 1,04 … 1,60 |
| 4,00 | 1,29 | 1,04 … 1,55 |
| 5,00 | 1,04 | 0,73 … 1,33 |
| 8,00 | 0,17 | ≈ 0 (salvo franja 9, escena) |
| 11,1 | 0,16 | ≈ 0 |

* De 1,33 a 4 ms, δ es **constante en T** y crece casi linealmente de ≈1,1 ms (arriba) a ≈1,6 ms (abajo).
* A 8 ms la pérdida **desaparece**, también por franjas. Un desfase fijo entre el reinicio electrónico y la cortina trasera, o una velocidad de barrido distinta, seguiría quitando ≈1,3 ms a 1/125 (−16 %, medible). No es así: hay un **cambio de régimen entre 5 y 8 ms**.
* Mecánico puro (EFCS desactivado) a 1/1500–1/1000: la franja superior recibe un 22–35 % menos que las centrales (≈0,2 ms). Puede ser parpadeo de la luz (ISO 12800, luz artificial) o la cortina. No está separado.

**Candidato estático para el umbral (VERIFICADO el código, INFERENCIA la relación):** el productor `0x4383fa40` hace `r8 = max([rec+0x1c] + sb, VTS)` y `sl = r8 − sb`. Por debajo de `sb* = VTS − [rec+0x1c]` la línea de reinicio se mueve con T; por encima, queda fija y se alarga el cuadro. Si `[rec+0x1c] ≈ VTS − (330…530)` líneas, el cruce cae entre 1/200 y 1/125, donde cambia el síntoma. `[rec+0x1c]` del modo EFCS sigue sin leerse. Hay un segundo umbral en el mismo productor (`[rec+0xf6] ≤ 0xc54` elige el conversor µs→líneas, `0x4382fac8` o `0x4382fa94`).

## 3. Datos de Darwin guardados en BK4 que cambian (VERIFICADO + MEDIDO)

* Tabla de bloques de Darwin `0x2a124/0x2a160` `{código, tamaño, RAM}`: `0x302000/0x80/0x20003cd8`, `0x302400/0x16c/0x200036d8` (S), `0x302700/0x190/0x200038d8`, `0x302990/0x18b/0x20003a68`, `0x20280/0x180/0x20000300` (B), `0x30100/0x100/0x20000600`, `0x10100/0x80/0x20000480`.
* Tabla BIONZ `0x4400ea60` `{ID BK4, RAM, tamaño}`: `0x30081→0x43f78692/0x60`, `0x30086→0x43f786f2/0x300`, `0x30102→0x43e97970/0x180`, `0x30100→0x43f76342/0x200`.
* `0x436bad9a–0x436bae2c` pide a Darwin el bloque `0x20000500` (0x100 B) y luego el `0x30100` (0x100 B) (512 B en total, el tamaño de BK4 `0x30100`). La respuesta se copia en `0x436ba8ce`. **BK4 `0x30100` es una copia del estado de Darwin** que se lee del MCU (INFERENCIA: al apagar, por los eventos `0x161/0x162`; la ruta de escritura hacia Darwin no se ha localizado). En Darwin, `0x20000600` incluye un anillo de 24 entradas (`+0x31` índice, entradas en `+0x80`) y contadores (`+0x04`, `+0x24`).
* Contenido: bytes `0x11–0x39` (41 valores decrecientes), `0x3b`, `0xf2–0xf7` (tres `u16` ≈ 2447/4359/4833), `0x166–0x16f`. Los demás son constantes en los 25 volcados.

| Volcado | Suma de `0x11–0x39` | `0x11` | `0x3b` |
|---|---|---|---|
| 20-10 (todos, antes de pruebas) | 1418 | 49 | 36 |
| 26-10 pre-T024 | 1422 | 51 | 36 |
| 27-10 pre-B1a | 1533 | 55 | 37 |
| 03-11 tras recuperación (3.26) | **0** (tabla a ceros) | 0 | 0 |
| 04-11 previo 3.37 (fallo ya presente) | 1408 | 50 | 36 |
| 05-11 pre-restauración | 1730 | 66 | 21 |
| 05-11 restaurado sin reiniciar | 1418 | 49 | 36 |
| 05-11 tras apagado limpio y siguientes | 1615 | 62 | 21 |

* Se **reconstruye** tras borrarse (03-11 → 04-11) hasta casi el mismo valor del 20-10. Con el fallo ya presente el 04-11, el valor era el del 20-10 (−0,7 %). **Por tanto esta tabla no explica cuándo empezó el fallo** (INFERENCIA fuerte), aunque el 05-11 se desplazó un +22 % y la restauración no se mantiene: se reescribe desde Darwin al apagar.
* Uso en BIONZ: el módulo `0x43841ba0–0x43842945` (REA: lectores de `0x43f76342` en `0x438421ec`, `0x43842748`, `0x438427b4`, `0x4384292c`) integra una curva de 41 puntos (`0x43842794`, escalas `u16[0]`/`u16[1]` = 128/185, constantes) y produce **`pkt[0xa..b]` del paquete `0x0c` a Darwin** (`0x43841d46` → `0x43eefb78` → `0x43842410` → `0x4383f796` → `0x43f7ca56` → `0x43841456`). En vivo vale `0x0e53` = 3667 (R58 §7, R59 §8). En Darwin es `S+0x3a`, la base del retardo `ip` que `0x18d6e` pasa a `0x1a738` (accionamiento de bobina/motor, según `[S+0x256]`). **No está demostrado** que la parte variable (`0x11–0x39`) entre en ese cálculo: en `0x4384282c` un byte `+0x11` de una estructura se usa como índice limitado a 0x12, pero no está cerrado que esa estructura sea `0x43f76342`.

## 4. Lógica de Darwin `0x18d6e` (VERIFICADO, completa R61 §1)

* `S+0x48 = 0x19a12(Tv)` y luego **se sobrescribe** con `0x18a2e()`. Si `[S+0x94]` ≠ 0, ese valor manda (ajuste de depuración). R61 da `S+0x48` como el resultado de `0x19a12`; no lo es.
* `r5 = 1` si `[S+0x31] & 3 == 0`. El paquete trae `pkt[1] = 2`, pero `S+0x31` se reescribe según el tipo de mecanismo (1/2 → `&~3`, S53). Por eso se usa `B+0x88` y por eso el experimento de R61 tuvo efecto. Queda coherente.
* Hay **dos** tiempos. (a) Cierre: `r8 = T + s16[B+0x88]` → `0x19948/0x198bc`. (b) Previo: `ip = S+0x3a (3667) + u16[0x20000480+0x42]` (con `[B+0xcd]&3 = 0` en esta unidad) `+ s8[B+0xc6|c7|c8]` según el rango de T (todos 0 en BK4) → `0x1a738(0, ip)`. Con `+0x88` se movieron los dos modos. **`ip` (vía `pkt[0xa..b]` o `0x20000480+0x42`) es la otra palanca de Darwin que no se ha probado.** `0x20000480` es el bloque `0x10100`, cuyo origen en BK4 no se ha identificado.
* La relación EFCS off +500 µs de R61 (2,47 arriba → 1,07 abajo) no es la de un retardo uniforme de la segunda cortina, que daría el mismo aumento en todas las franjas. O `+0x88` no es un retardo puro, o la referencia base no es uniforme. **NO VERIFICADO**.

## 5. Qué queda (por coste)

1. **Barato, sin riesgo:** fotos con EFCS activado a 1/160 y 1/180 (y repetir 1/200 y 1/125) bajo luz continua sin parpadeo, en RAW. Sirven para localizar el umbral del §2. Si cae donde predice `max([rec+0x1c]+sb, VTS)`, el planificador queda señalado.
2. Leer `[rec+0x1c]`, VTS y `sl` del modo EFCS en un disparo a 1/125 y otro a 1/250 (SWD del BIONZ con un objeto `cap` localizable, o emulando `0x43841070` con el descriptor de `desc.txt`).
3. Capturar el paquete `0x0c` con EFCS **desactivado** (mismo método que R58 §7) para cerrar si Darwin recibe alguna diferencia.
4. Repetir la prueba de NVRAM **con batería fuera** (reinicia la SRAM de Darwin) y volcar `0x30100` antes y después.
5. Repetir R60 asegurando la ejecución del parche (por `/dev/mem` como en R56, o invalidando la I-cache).

Límites: δ sale de una foto por velocidad y a ISO 12800 con posible parpadeo de la luz. La relación de `0x30100` con la curtain/EFCS es de flujo de datos, no de efecto medido. Las direcciones de RAM de BIONZ son estáticas del 3.21.
