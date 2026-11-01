# 14. Estado actual y límites

| Aspecto | Estado (31-10-2026) |
|---|---|
| Cámara | **Bloqueada** tras instalar el 3.25 (actualizador al 100 % y Done; testimonio del usuario, sin captura UART ni lectura de NAND) |
| Causa | **Identificada offline** ([R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md)): el `nflasha3` recomprimido del 3.25 no respeta el formato que lee el descompresor por hardware (359/369 bloques empiezan a mitad de sector y Loader3 no transmite ese desplazamiento; 3 bloques son un solo registro de 64 KiB en vez de 16 de 4 KiB). La primera lectura de la partición falla y Loader3 da −302 (3 lentos + 2 rápidos). El 3.23 no tocaba `nflasha3`. Falta la confirmación física (vídeo del LED; la UART está silenciada, R37) |
| Recuperación | Solo hay que restaurar `nflasha3` y existe copia válida ([R30](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r30-updater-done-boundary.md)). La vía serie del BootROM se abre en cada arranque pero exige una clave guardada en `nflasha0`, nunca volcada ([R32](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r32-moderreg-valor-real.md), [R33](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r33-veracidad-clave-nflasha0.md)). Mínimo físico identificado ([R37](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r37-cierre-estatico-recuperacion.md)): un archivo vacío `\updater\mode` en `nflasha2` hace que Loader3 arranque el actualizador de fábrica de `nflasha1` (intacto) y acepte firmware por USB; el paquete **3.26** (contenido oficial) ya está preparado. En el último volcado de `nflasha2` basta **1 byte lógico** (recuperar una entrada `MODE` borrada, [R38](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r38-guard-y-entrada-updater.md)), y el guard del actualizador acepta el 3.26. Ese byte no se puede reprogramar en su sitio con un lector externo (MuMin + ECC, [R39](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r39-estatico-profundo.md)): hace falta escribir desde el propio BIONZ. No está autorizado |
| Obturador silencioso | Logrado con el 3.23 (T040, confirmado por el usuario); exposición por filas medida en el RAW ([E25-10](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-10-exposicion-por-fila.md)) |
| Selector EFCS / Electronic (3.25) | Implementado y verificado **solo offline** (emulación); nunca validado en la cámara ([E25-24b](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-24b-implementacion-selector.md), [E25-27](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-27-construccion-firmware-integrado.md)) |
| Verificación | 4 427 pruebas en local (las que leen firmware se omiten en CI); censo de etiquetas 133/372; 295 sesiones S + 74 informes de fase E; 12/24 planes físicos con prueba; registro T001–T056 |

**Último cierre:** E26 R40 (31-10-2026) — JTAG/SWD del BIONZ analizado como alternativa a escribir la NAND con lector externo: ningún
cargador bloquea el DAP CoreSight y el chip trae `defconfig` de fábrica para arrancar bajo depurador, pero sigue siendo físico
(falta población de R4911/R4912 y el eFuse de seguridad). Detalle por informe en [knowledge/CURRENT.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/knowledge/CURRENT.md).


## Límites y riesgos

- **Sin recuperación independiente** ([E24-04](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e24-04-dictamen-seguridad.md), [E25-04](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-04-recuperabilidad-y-decision.md)): Darwin también controla la energía. El caso real es el 3.25.
- **Lo offline no garantiza el arranque:** el 3.25 pasó todas las comprobaciones offline y bloqueó la cámara ([R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md)).
- **Escenarios sin medir con el 3.23:** operación 5 de Darwin (P40/P41=3) y P4B/P4C siguen activos; su efecto físico no se midió.
- **Respaldo:** la copia externa del respaldo (R1) sigue sin verificar.


Ver también la [verificación paso a paso](https://github.com/nicolvus/a6000-fw-decomp/wiki/Home) y [Requisitos y riesgos](https://github.com/nicolvus/a6000-fw-decomp/wiki/1-Requisitos-y-riesgos).

Tablero de progreso (cobertura documental, sesiones y pruebas): <https://nicolvus.github.io/a6000-fw-decomp/progress/>.
