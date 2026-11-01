# 7. Volver atrás y recuperación

## Volver al Darwin oficial (3.24)

```sh
pmca-console firmware -f a6000-custom-fw-3.24-recovery-stock-darwin.dat
```

- Solo acepta la instalación si la cámara está en **3.23** y conserva el acceso al actualizador.
- Restaura el Darwin oficial de Sony 3.21 con número de versión 3.24.
- **Verificado solo offline (69/69, byte a byte); nunca instalado en una cámara real.**
- No es una recuperación independiente del microcontrolador: si la cámara no arranca, el 3.24 no se puede instalar.

## NVRAM corrupta o ajustes extraños

Service mode + `scripts/senser_backup_restore.py FILE SHA256` con tu backup ([paso 3](https://github.com/nicolvus/a6000-fw-decomp/wiki/3-Backup-de-NVRAM)). Probado en hardware el 20-10-2026.

## El incidente del 3.25 y el 3.25c

El 3.25 integraba un selector EFCS/Electronic en el firmware modificando `av-cam.bin` dentro de `nflasha3`. Tras instalarlo, la cámara del autor no arranca
(LED 3 lentos + 2 rápidos, código −302 de Loader3). Causa identificada offline ([R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md)):
el `nflasha3` recomprimido no respetaba el formato que lee el descompresor por hardware (bloques que empiezan a mitad de sector y un solo registro de 64 KiB
en vez de 16 de 4 KiB). Falta la confirmación física. El 3.25 original no se publica.

El **3.25c** ([release](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental), [R45](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r45-firmware-325c-experimental.md))
tiene las mismas funciones con `nflasha3` en el formato de Sony: 0 violaciones del descompresor, 366/369 bloques idénticos a los de Sony y 0 fallos en la emulación
del cargador real (el 3.25 falla en 361). **Debería arrancar, pero nunca se ha instalado** y su código nuevo de BIONZ/Darwin solo se ha ejecutado en emulación.
Requisitos: firmware 3.21 oficial (o 3.23/3.24), batería cargada y backup de NVRAM; **no** sirve para una cámara que ya instaló el 3.25 original.
Para volver al firmware de Sony después del 3.25c usa el **3.26** del mismo release (el 3.24 ya no se acepta tras un 3.25).
Si prefieres lo probado: **3.23 + capa 2 en RAM, sin tocar `nflasha3`.**

Rutas de recuperación estudiadas para esa cámara (todas físicas, sin probar ni autorizadas): restaurar `nflasha3` desde una copia válida, crear el archivo
vacío `\updater\mode` en `nflasha2` para arrancar el actualizador de fábrica y cargar el paquete 3.26, o JTAG/SWD. Resumen en `docs/capture/e26-recovery.md`.

## Si tu cámara no arranca

Detente. No intentes flashear nada más. Abre una *issue* en el repositorio con el LED y el último paso, y guarda tu backup de NVRAM. Si nada funciona, el último recurso es cambiar la placa.
