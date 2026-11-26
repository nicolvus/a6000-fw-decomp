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

El **3.25c** ([R45](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r45-firmware-325c-experimental.md))
tiene las mismas funciones con `nflasha3` en el formato de Sony: 0 violaciones del descompresor, 366/369 bloques idénticos a los de Sony y 0 fallos en la emulación
del cargador real (el 3.25 falla en 361). **Se instaló como 3.27** (03-11-2026, [R51](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r51-respaldo-clave-nflasha0-nvram-326.md) §5):
la cámara arranca y el selector funciona dentro del BIONZ, pero el valor no llegó a verse en el paquete enviado a Darwin.
Requisitos: firmware 3.21 oficial (o 3.23/3.24), batería cargada y backup de NVRAM; **no** sirve para una cámara que ya instaló el 3.25 original.
Después del 3.27 la línea continuó: **3.30** (obturador electrónico real), 3.35, 3.77 y la serie 3.93. `.dat` publicados no hay:
se construyen con los scripts ([página 4](https://github.com/nicolvus/a6000-fw-decomp/wiki/4-Construir-los-paquetes)).

**Esa cámara se recuperó (03-11-2026, [R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md)).** Por SWD se forzó, solo en un registro de CPU y sin escribir la NAND, que Loader3 arrancara el actualizador de fábrica; este instaló el **3.26** oficial por USB. Método y límites en [15. Recuperación por SWD](15-Recuperacion-SWD-experimental). Requiere abrir la cámara y soldar; el caso es único y no es una garantía para otras. Otras rutas estudiadas y no usadas: restaurar `nflasha3` desde una copia, o escribir `\updater\mode` en `nflasha2` (Loader3 ignora las escrituras de bloque, R48 §2.1).

## Si tu cámara no arranca

Detente. No intentes flashear nada más. Abre una *issue* en el repositorio con el LED y el último paso, y guarda tu backup de NVRAM. Si nada funciona, el último recurso es cambiar la placa.
