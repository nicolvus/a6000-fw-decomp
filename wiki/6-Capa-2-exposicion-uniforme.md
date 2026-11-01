# 6. Capa 2: exposición uniforme (parche en RAM)

Con solo el 3.23 el obturador no se mueve, pero sin cortina trasera la fila `i` integra **T + ≈7 ms + 15,2 µs·i**: la parte inferior puede
recibir hasta 3,7× más luz que la superior. La capa 2 fija `ShutMode 0` y un registro `r5` calculado según la velocidad para que el sensor
controle la exposición de cada fila: (4219 − `r5`) × 15,2 µs.

- Vive **solo en RAM**: no toca flash, NVRAM ni `nflasha3`. Un reinicio la borra.
- Un **guardián** en la cámara revierte solo a los 25 s si el PC no responde.
- Probado en T050: 12 disparos y una ráfaga de 4 entre 1/4000 y 1/30, siempre revertido. Desde 1/15 se vuelve al disparo normal; 1/8000 solo se ha emulado.

## Requisitos en la cámara

1. **Cámara en 3.23** ([paso 5](5-Instalar-el-3.23)) y Wi-Fi conectado a tu red local.
2. **OpenMemories Tweak** ([upstream](https://github.com/ma1co/OpenMemories-Tweak), fuente en `references/tweak/`): instálalo con
   `pmca-console install` según la sección «Installing Android apps» de [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE). En la app marca
   **Enable Telnet** (puerto 23, root, sin login) y **Enable ADB** (puerto 5555).
3. **RemoteShutter** (app del proyecto, servidor HTTP en el puerto 8080; endpoints `/shoot`, `/ss`, `/status`, `/info`, `/log`, `/jpg`):
   compílala con `tools/remote-shutter/build.sh` (requiere JDK 17 y build-tools en `~/.local/android-build`) e instálala por ADB:
   ```sh
   python scripts/camera_install_apk.py tools/remote-shutter/out/RemoteShutter.apk 192.168.1.29
   ```
   Ábrela en la cámara antes de disparar.

## Uso

Edita `HOST = "192.168.1.29"` en `scripts/camera_telnet.py` y `scripts/camera_silent.py` (o pasa `--host` donde exista) con la IP de tu cámara. Después:

```sh
python scripts/camera_telnet.py --host <IP> 'uname -a'      # comprueba el telnet
python scripts/camera_silent_test.py salida-t050/            # patrón de prueba de T050 (escena fija, sin tocar la cámara)
```

`camera_silent.py` hace, por cada disparo o ráfaga: (1) comprueba que los bytes de RAM sean los originales y, si no, **no parchea**; (2) arranca el
guardián; (3) escribe `ShutMode` (`0x836d6fb6`) y `r5` (`0x836d7000`) en un solo comando de telnet; (4) dispara; (5) revierte y verifica.
Antes de calcular `r5` hay que esperar a que la velocidad se estabilice. Detalle del cálculo: `docs/capture/e25-11-r5-bionz-analisis.md` §10.

## Límites

- Escala absoluta: el nivel cae ≈ 22 % por debajo del objetivo con una referencia y ±1 % con otra (incertidumbre ±25 %).
- Efecto rolling: la lectura dura ≈ 61 ms; los objetos en movimiento salen deformados.
- Sin medir: flash, vídeo y Live View con los parches activos.
- Exposición larga electrónica no implementada.
- No lances el parche desde la app con `Runtime.exec`: en T049 se colgó entre las dos escrituras y dejó `ShutMode 0` forzado. Usa telnet desde el PC.
