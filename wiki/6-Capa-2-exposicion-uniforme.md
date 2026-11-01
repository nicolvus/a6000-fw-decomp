# 6. Capa 2: exposición uniforme (parche en RAM)

Con solo el 3.23 el obturador no se mueve, pero sin cortina trasera la fila `i` integra **T + ≈7 ms + 15,2 µs·i**: la parte inferior puede
recibir hasta 3,7× más luz que la superior. La capa 2 fija `ShutMode 0` y un registro `r5` calculado según la velocidad para que el sensor
controle la exposición de cada fila: (4219 − `r5`) × 15,2 µs.

- Vive **solo en RAM**: no toca flash, NVRAM ni `nflasha3`. Un reinicio la borra.
- Un **guardián** en la cámara revierte solo a los 25 s si el PC no responde.
- Probado en T050: 12 disparos y una ráfaga de 4 entre 1/4000 y 1/30, siempre revertido. Desde 1/15 se vuelve al disparo normal; 1/8000 solo se ha emulado.

## Requisitos en la cámara

1. **Cámara en 3.23** ([paso 5](https://github.com/nicolvus/a6000-fw-decomp/wiki/5-Instalar-el-3.23)) y Wi-Fi conectado a tu red local.
2. **OpenMemories Tweak** ([upstream](https://github.com/ma1co/OpenMemories-Tweak), fuente en `references/tweak/`): instálalo con
   `pmca-console install` según la sección «Installing Android apps» de [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE). En la app marca
   **Enable Telnet** (puerto 23, root, sin login) y **Enable ADB** (puerto 5555).
3. **RemoteShutter** (app del proyecto, servidor HTTP en el puerto 8080; endpoints `/shoot`, `/ss`, `/status`, `/info`, `/log`, `/jpg`):
   compílala con `tools/remote-shutter/build.sh` (requiere JDK 17 y build-tools en `~/.local/android-build`) e instálala por ADB:
   ```sh
   python scripts/camera_install_apk.py tools/remote-shutter/out/RemoteShutter.apk 192.168.1.29
   ```
   Ábrela en la cámara antes de disparar. Scripts de instalación y control: [Herramientas](https://github.com/nicolvus/a6000-fw-decomp/wiki/12-Herramientas).

## Uso desde el PC

El parche se aplica desde el PC por telnet, uno por disparo o ráfaga, con un guardián en la cámara que lo revierte solo a los 25 s.
Pasos, scripts y comandos: [Herramientas](https://github.com/nicolvus/a6000-fw-decomp/wiki/12-Herramientas). Por cada disparo o ráfaga se hace esto:

1. Comprobar que los bytes de RAM sean los originales (si no, **no se parchea**).
2. Arrancar el guardián en la cámara.
3. Escribir `ShutMode` (`0x836d6fb6`) y `r5` (`0x836d7000`) en **un solo comando** de telnet y verificar.
4. Disparar vigilando la app (sin respuesta en 12 s o 45 s ⇒ revertir y abortar).
5. Revertir en un solo comando, avisar al guardián y verificar.

Antes de calcular `r5` hay que esperar a que la velocidad se estabilice. Detalle del cálculo: `docs/capture/e25-11-r5-bionz-analisis.md` §10.

## Hacerlo todo desde la cámara (idea, no implementada)

Hoy hace falta un PC por telnet. Quitarlo es posible en principio, porque la app ya conoce la velocidad (`CameraEx.getShutterSpeed()`) y `/dev/mem`
es accesible al usuario de la app. **Nada de esto está probado en la cámara completa**; lo que sí se sabe:

- **Ya se intentó desde la app (T049):** funcionó en 6 disparos (1/4000, 1/1000, 1/250 ×2), con parche y reversión verificados, pero falló en dos puntos:
  `RandomAccessFile` no direcciona `/dev/mem` por encima de 2 GiB, y `Runtime.exec("dd")` desde un proceso de ≈100 MB con ≈8 MB libres colgó el `fork`
  **entre las dos escrituras**, dejando el parche a medias. Por eso la app no debe usar `Runtime.exec`.
- **Idea recomendada:** que la app hable con el `telnetd` local (`127.0.0.1:23`, sin `fork` propio) y envíe los mismos comandos del PC:
  (1) arrancar el guardián de 25 s *dentro de la cámara*, (2) aplicar ambos parches en **un solo comando**, (3) disparar, (4) revertir en un solo comando y avisar al guardián.
  El guardián es un `sh` independiente de la app: si la app se cuelga o se cierra, la RAM vuelve sola a los bytes originales.
- **Alternativa:** un proceso auxiliar preabierto (o un pequeño ayudante nativo) que haga las dos escrituras en una sola operación, sin crear procesos durante el disparo.
- **Interfaz:** un interruptor «uniforme» y la velocidad actual bastan: la app calcula `r5 = 4219 − µs/15,2` y, si `r5 < 10` (T > ≈ 64 ms), dispara normal.
- **Condiciones de seguridad:** `ShutMode 0` vale para todas las llamadas mientras esté parcheado (Live View ya lo usa); AF, vídeo y ráfagas largas no están probados;
  la función debe estar **desactivada por defecto** y revertir siempre en un bloque `finally`.
- **Persistir es experimental:** el 3.25 lo llevaba a firmware y bloqueó la cámara del autor por un error de formato de `nflasha3`; el
  [3.25c](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental) lo corrige pero nunca se ha instalado. La vía probada sigue siendo el parche en RAM.

## Límites

- Escala absoluta: el nivel cae ≈ 22 % por debajo del objetivo con una referencia y ±1 % con otra (incertidumbre ±25 %).
- Efecto rolling: la lectura dura ≈ 61 ms; los objetos en movimiento salen deformados.
- Sin medir: flash, vídeo y Live View con los parches activos.
- Exposición larga electrónica no implementada.
- No apliques el parche desde la app con `Runtime.exec`: en T049 se colgó entre las dos escrituras y dejó `ShutMode 0` forzado. Usa telnet (ver arriba).
