# E26-R54 — 3.30: `pkt[0x0e]` también en el constructor del envío; primer obturador electrónico funcionando

Fecha: 04-11-2026. Continúa [R53](e26-r53-paquete-329-ajuste-efcs-en-vivo.md).

Etiquetas: **MEDIDO** · **INFERENCIA** · **NO VERIFICADO**.

## 1. Causa (MEDIDO, estático y emulación)

El paquete `0x0c` que sale hacia Darwin lo arma **`0x438d0064`** en cada envío (E24-05h §3), no `0x43841070`, donde estaba la cueva del selector. En `0x438d01fa` ejecuta `strb.w r3,[r2,#0x4e]`, que escribe `pkt[0x0e]` (`carga+0x40+0xe`) con un valor propio de Sony: 0 si el tipo es 0, y en otro caso `[obj+0x4b68] − [obj+0x1d8]` o `0xff`. El supuesto de E25-24b («`pkt[0x0e]` sin productor») era falso: el 1 del selector se pisaba en cada envío. Emulación del 3.29: `pkt[0x0e] = 0xff` con el ajuste a 0 y a 1.

## 2. Cambio (`patch_bionz.py`)

| Sitio | Antes | Después |
|---|---|---|
| `0x438d01fa` | `82f84e30` (`strb.w r3,[r2,#0x4e]`) | `bl 0x43541820` |
| `0x43541820` (16 B, ceros verificados; entre la cueva del selector `…1818` y C3-B `…1840`) | — | `ldr r3,=0x43edf894; ldr r3,[r3]; strb.w r3,[r2,#0x4e]; bx lr` + literal |

`r3` y `lr` quedan libres (el código siguiente recarga `r3`; la función guardó `lr`). Se pierde el valor de Sony en `pkt[0x0e]`; Darwin no tiene otro lector estático de `S+0x3e` que la compuerta `0x4318` (E24-05a, **NO VERIFICADO** en hardware). `build.py` comprueba que la nueva cueva no solapa con las otras dos.

## 3. Pruebas (offline)

* Regresión `test_emu_bionz_envio_lleva_ajuste_en_vivo` (emula `0x438d01fa`): con el 3.29 da `0xff`; con el 3.30, `pkt[0x0e]` = ajuste (0/1).
* `verify_325c.py` (32 comprobaciones): 3.30, 3.29 y 3.27 → 32/32. Cambio de criterio: «15 de 16 registros de Sony» pasa a «16 − páginas de 4 KiB cambiadas» (en el bloque 57 cambian ahora dos páginas: 14 registros); para 3.27/3.29 sigue dando 15.
* Tests del selector: 42/42. La suite completa se detuvo a petición del usuario (tardaba demasiado).

| Archivo (no versionado) | SHA-256 |
|---|---|
| `analysis/e25-27/artifacts-330/package-3.30/firmware_packed.dat` | `855a00ef18e5fa33…` |
| `av-cam.integrated.bin` | `8810027c0c2e1c8ad04735eb9bf8123af195d3f403dd369608354b8fee1d8623` |

## 4. En cámara (MEDIDO por el usuario)

Instalado 3.29 → 3.30 (`Done`; la cámara reporta 3.30). **El usuario confirma que con EFCS desactivado el obturador electrónico funciona: la foto se obtiene sin cortina.** No medido: RAW (exposición), rango de velocidades.

## 5. Parche de RAM de exposición (E25-11 §10) aplicado encima

A petición del usuario, `scripts/camera_silent.py` (ShutMode 0 en `0x836d6fb6`, `r5` en `0x836d7000`) con `r5 = 3956` (1/250). Cambio en el script: el archivo de aviso del guardián pasa a `/android/dev` (tmpfs), porque `/android/data` cuelga la E/S (R51 §6). Verificado por telnet tras los 25 s del guardián: `4ff00009` / `0f204ff0740e`. Solo RAM: se pierde al apagar, y fuerza ShutMode 0 en todos los disparos con `r5` calculado para 1/250 (otras velocidades darán otra exposición). **NO VERIFICADO:** cómo interactúa con C3-B (que también normaliza la exposición en Electronic).

**Resultado (usuario):** con el parche, la foto en Electronic a 1/250 **sale bien expuesta**; pero con EFCS activado (mecánico) sale **negra**, porque el parche fuerza ShutMode 0 en todos los disparos. Solución provisional: `scripts/camera_silent_follow.py` (PC, telnet) sondea el ajuste EFCS cada ~2 s y aplica el parche solo en Electronic y lo revierte en EFCS (al cambiar el ajuste hay que esperar ~3 s). Pendiente: integrarlo en el firmware condicionado al modo (la vía permanente).

### 5.1 Comparación RAW mecánico / electrónico con el parche (04-11-2026, MEDIDO)

Fotos del usuario en manual, f/3,5, ISO 2500, **1/90** (EXIF), escena fija: `DSC03398.ARW` (EFCS, sin parche) y `DSC03399.ARW` (Electronic, parche con `r5 = 3123`, calculado para **1/60** porque la app estaba cerrada). Media RAW sin negro: 307,9 → 568,8, razón **1,847 (+0,89 EV)**; canales con la misma razón (R 1,86, G 1,85, B 1,84); por franjas horizontales 1,78–1,96 (algo más en las inferiores). Con `r5` de 1/60 se esperaba 16,7/11,1 = 1,50; corregido por esa diferencia la electrónica queda **≈ 1,23× (+0,30 EV)** sobre la mecánica. Forma uniforme como en T050; la escala absoluta sigue con error de ~+25 % (T050 daba −22 %). Nota: escribir `+0x210` por `/dev/mem` no cambia el modo (Linux no ve la caché del núcleo de BIONZ: por `/dev/mem` se lee 0 cuando por SWD vale 1); el modo se cambia desde el menú.
