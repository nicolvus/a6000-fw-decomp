# E26-R67 — Qué son los eventos A y B de Darwin con EFCS: `P4C` (`CA_1ST_CURTAIN_START`) y `P4E` (`2ND_CURTAIN_MG`) (07-11-2026, estático)

Continúa [R66](e26-r66-bloques-darwin-en-nvram-1850000.md) §3 (E26-R66-RESET). Capstone sobre `darwin_core.bin` 3.21. Mapa de puertos: [fm3-gpio-shutter-mapping](fm3-gpio-shutter-mapping.md) y [S54 sync](s54-bionz-darwin-sync.md).
Prueba: `tests/test_e26_r67_eventos_darwin.py`.

## 1. Los dos eventos (VERIFICADO)

`0x51c0(desplazamiento, valor)` escribe el alias bit-band `0x42668000 + desplazamiento`: `0x230` = **P4C** (`CA_1ST_CURTAIN_START`), `0x234` = P4D (`1ST_CURTAIN_MG`), `0x238` = **P4E** (`2ND_CURTAIN_MG`).

| Evento | Rutina | Acciones |
|---|---|---|
| **A** `0x202f2(0)` | `0x202c2` (lista según `t`), `0x20cb2` (P4D ← 0 solo si `0x20c74()` ∈ {1, 2}), **`0x16e68`: P4C ← 0 (`0x1ecec(0)`) y `S+0x10 = 0x93e6()`**, `0x2020a(0x20, 1)` → `0x16adc(6, 0x21)` (evento `0x21` al anillo de eventos) | flanco de P4C hacia el BIONZ |
| **B** `0x2041e(0)` | `0xd116(1<<22)`, `0x201b0(0)`, `0x16fe2` y **`0x20d00`: P4E ← 1 solo si `0x20c74() ≠ 0`** (además `0x210c0`, marca), `0x20408`, `0x20c4a`; estado 6 | segunda cortina mecánica |

* El otro escritor de P4C es `0x16e7a` (P4C ← 1 y marca en `S+0x10`), llamado desde `0x175ee` y `0x17cf0`, más el arranque `0x1708e`. **P4C es un pulso**: sube en `0x16e7a` (INFERENCIA: al preparar la captura; no se ha trazado cuándo se llama `0x175ee/0x17cf0`) y baja en A. P4C ← 0 se alcanza también desde `0x198d2`, `0x19906`, `0x19994` (ramas «casi simultáneas»), `0x206fa` y `0x20a92`.
* Según el esquema (S54), P4C llega al BIONZ por **dos pines**: `SENS_B` (AA13, función dedicada del bloque mecánico) y `GPIO_9` (AD21). No se ha encontrado consumidor por firmware (S54/S55). Lo coherente es que el flanco de A **dispare por hardware el reinicio electrónico** (INFERENCIA fuerte: es la única señal Darwin→BIONZ que se mueve en el instante de A y su nombre es «inicio de primera cortina»).

## 2. Qué implica para la pérdida de EFCS (INFERENCIA)

Con EFCS activado, Darwin genera el flanco de `CA_1ST_CURTAIN_START` y suelta `2ND_CURTAIN_MG` separados `T − 3401…3428 µs` (R66 §3). La exposición real es

`T − 3407 + (latencia real de la segunda cortina) − (retardo entre el flanco de P4C y el arranque del reinicio en el sensor)`.

Como los parámetros de Darwin no han cambiado (R66 §2), la pérdida de ≈1,27 ms (y su gradiente de 1,1 a 1,6 ms de arriba abajo) solo puede salir de dos sitios:

1. **El lado BIONZ/sensor tarda más desde el flanco** en arrancar el reinicio, o el BIONZ no ve el flanco y arranca por otra vía más lenta (por ejemplo, el aviso por el enlace serie). A 8 ms o más la pérdida desaparece (R62 §2), lo que encaja con que en ese régimen el BIONZ temporice el reinicio por su cuenta, sin depender del flanco. La cámara se abrió el 03-11 para el SWD (R46–R49); antes de la recuperación EFCS funcionaba.
2. **La segunda cortina llega antes de lo que supone Darwin.** Haría falta una cortina ≈1,3 ms más rápida en arrancar y ≈0,5 ms más rápida en el recorrido. Es menos probable.

Ninguna de las dos se decide estáticamente.

## 3. Prueba pasiva que lo decide (sin escribir nada; requiere autorización)

* **Lectura por SWD del BIONZ** (`analysis/e26-r59/bz_mon.py`, solo lectura, sin halt), durante disparos con EFCS activado a 1/1000 y 1/125: muestrear los registros de lectura (RDATA) de los bancos GPIO del BIONZ (`0xf2910000 + 0x100·n + 0x10`; el banco 4 es `0xf2910410`, R8) y buscar el bit que hace el pulso de `GPIO_9`. Si el pulso aparece con la duración esperada, la línea llega bien y el retardo está en el BIONZ/sensor. Si no aparece nunca, hay un fallo físico en P4C → AA13/AD21 (conector o pista tocados al abrir la cámara).
* Alternativa física: continuidad P4C (CN4900) ↔ AD21/AA13 con la cámara apagada, o analizador lógico en P4C y `CIS0_VD` (S56).
* Límite: la asignación banco/bit de `GPIO_9` no es estática (R44 §6); el barrido de bancos la resuelve en la propia medida.

## 4. Otros pendientes revisados

* **E24-05e:** el criterio de medida (≥ 3 disparos con EFCS activado y desactivado) **se cumplió en R63 §1** (`pkt[1]` = `0x02` / `0x40`; el primer disparo tras cambiar el ajuste es mixto, `0x42`). Queda solo la fuente estática de `cap+0x4bc` / `+0x10f`.
* **`S+0x60`** (compuerta que anularía la resta de `G+0x42`): `S` es la imagen del paquete con desplazamiento 0x30; el paquete visto por SWD no llega a `pkt[0x30]`. Sin escritor por código (barrido de R65); solo es escribible por la escritura de RAM del enlace (validador `0x1b53e`). INFERENCIA: vale 0.
* **E25-EFCS-4 (VERIFICADO por bytes en `av-cam.bin`):** `0x436d6f6c` (SetExposure IMX210) solo aparece como puntero de datos en `0x43fcc0b8`, y `0x437ea8cc` (selector de secuencias) como puntero en `0x43ff8fc8`: se llaman de forma indirecta. `0x43844e80` (configuración EFCS) **sí tiene una llamada directa**, `bl` desde `0x437b5ba4`. Ninguna de las tres tiene otra referencia. Sembrarlas en Ghidra no cambia el cierre: el proyecto histórico es de solo lectura y REA las trata con Capstone.
