# 14. Estado actual y límites

Estado a **25-11-2026**. Los informes enlazados están en español; la fuente operativa para agentes es
[knowledge/CURRENT.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/knowledge/CURRENT.md).

| Aspecto | Estado |
|---|---|
| Cámara | CFW de la serie **3.93/4.0x** sobre la base Silent; el paquete oficial 3.21 de vuelta atrás está verificado. Recuperada el 03-11-2026 por SWD ([R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md)); la sonda sigue soldada |
| Obturador electrónico | **Funciona desde el 3.30** (envío en línea de `pkt[0x0e]` + compuerta de Darwin, [R54](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r54-paquete-330-envio-pkt0e.md)); la exposición se calibró en el 3.35 ([R56](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r56-paquete-333-envio-inline.md) §7) y el Silent quedó nivelado **en el firmware** desde el 3.77 ([R87](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r87-disparo-remoto-y-recalibracion.md)). Primer hito: 3.23 (T040, solo obturador mecánico inactivo) |
| EFCS activado | **Negro desde 1/1000**: se pierden ≈1,27 ms, también con el firmware de Sony ([R57](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r57-paquete-336-darwin-eq1.md) §5). Descartados firmware, NVRAM y Darwin como causa: es física ([R74](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r74-conclusion-final-efcs-negro.md), [R83](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r83-informe-final-efcs-negro.md)). Sin resolver; falta medida física (E26-R74-FISICO) |
| Interfaz (GUI) | **Arnés QEMU**: arranca `im.elf` 3.21 con la botonera de la A6000, dibuja el menú y ejecuta teclas sin tocar la cámara; sobre él se construyen los CFW con función nueva ([carril GUI](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/README.md), [G22](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g22-arnes-ui-qemu.md)) |
| Serie 3.93 | **Una build por función** sobre la base Silent: `base`, `film`, `pp`, `exfine`, `iso`. Instaladas y probadas de una en una ([G105](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g105-builds-por-funcion.md)). `iso` deja la cámara en bucle de arranque; Film pega los botones (causa sin aislar); Extra Fine avisa de que no hay espacio en la tarjeta |
| Serie 4.0x | 4.01 y 4.02 instaladas para bisecar el vídeo; 4.03 (núcleo de la 4.02 + `/usr` de Sony) y 4.04 (Sony 3.21 intacto salvo `nflasha5`) construidas y auditadas, **sin instalar** |
| Vídeo (FILM-PB-1) | **Abierto**: los clips se graban y se reproducen en el PC, la cámara muestra «No se puede visualizar.» Se descartó que lo cause un parche ([auditoría](https://github.com/nicolvus/a6000-fw-decomp/blob/main/reports/film-pb-1-auditoria-cfw-20261127.md)); la causa probable es el **selector PAL/NTSC** frente a la cadencia de los clips ([informe](https://github.com/nicolvus/a6000-fw-decomp/blob/main/reports/film-pb-1-causa-sistema-tv-20261127.md)), ajuste que **no está expuesto en el menú** de este modelo |
| Incidente del 3.25 | Causa identificada offline (formato TPZL de `nflasha3`, [R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md)), corregida en el 3.25c, **instalada como 3.27** ([R51](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r51-respaldo-clave-nflasha0-nvram-326.md) §5) y sustituida por el 3.30 |
| Recuperación | **Resuelta por SWD** ([R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md)): se fuerza un registro de CPU y el actualizador de fábrica instala por USB, sin escribir NAND. Procedimiento y límites en [15](15-Recuperacion-SWD-experimental) |
| Carga USB encendida | En investigación: la orden llega a Darwin y con cargador de pared no se aplica ([informe](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/usb-carga-encendida.md)) |
| Open gate en vídeo | 6000×4000 grabando **descartado** (el sensor da 14,98 Hz); la única vía de firmware sería 1440×960 ([G112](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g112-opengate-video-3-2.md)) |

## Límites y riesgos

- **Sin recuperación independiente** ([E24-04](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e24-04-dictamen-seguridad.md), [E25-04](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-04-recuperabilidad-y-decision.md)): Darwin también controla la energía. La recuperación probada es la del BIONZ por SWD, no la del firmware de Darwin.
- **Lo verificado offline no garantiza el arranque:** el 3.25 pasó todas las comprobaciones y bloqueó la cámara ([R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md)).
- **Con EFCS activo, negro desde 1/1000**; el obturador electrónico está medido en una cámara y una unidad de sensor.
- **Los CFW de la serie 3.93/4.0x no reproducen vídeo** (FILM-PB-1) y `iso` no arranca.
- **Respaldo:** la copia externa del respaldo (R1) sigue sin verificar.
- Las cifras del tablero (módulos, sesiones, pruebas) miden documentación y verificadores, no funcionamiento en cámara.

Ver también [Resultados y límites](9-Resultados-y-limites), [Requisitos y riesgos](1-Requisitos-y-riesgos),
[Objetivos](16-Objetivos) y el [tablero de progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/).
