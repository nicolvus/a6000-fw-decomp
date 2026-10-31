# Sony A6000 — Silent Shutter

[![módulos](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sesiones](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![pruebas](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![CI](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml/badge.svg)](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml)

Ingeniería inversa del firmware 3.21 de la Sony A6000 (ILCE-6000: BIONZ + microcontrolador Darwin) para disparar con
obturador electrónico. **Hito:** con el firmware modificado **3.23** (parche de 2 bytes sobre Darwin) la cámara real disparó en
silencio y sin error. **Después**, el firmware integrado **3.25** dejó la cámara sin arrancar; hoy el proyecto investiga su
recuperación, solo con análisis offline.

> **⚠️ No instales el 3.25.** Tras instalarlo, la cámara del autor no arranca (LED 3 lentos + 2 rápidos). Instalar cualquier firmware
> modificado puede dejar la cámara inservible y **no hay recuperación independiente demostrada**. Lee [Límites y riesgos](#límites-y-riesgos).

## Estado técnico actual

| Aspecto | Estado (31-10-2026) |
|---|---|
| Cámara | **Bloqueada** tras instalar el 3.25 (actualizador al 100 % y Done; testimonio del usuario, sin captura UART ni lectura de NAND) |
| Causa | Indeterminada. Única anomalía del 3.25 frente al corpus Sony: alineación TPZL de `nflasha3` (residuo 256 en 359/369 entradas); Loader3 la acepta y su efecto en el descompresor por hardware no se puede decidir sin la cámara ([R15](docs/capture/e26-r15-tpzl-custom-fw325.md)–[R17](docs/capture/e26-r17-arm7-ldec-segment-analysis.md)) |
| Recuperación | Solo hay que restaurar `nflasha3` y existe copia válida ([R30](docs/capture/e26-r30-updater-done-boundary.md)). La vía serie del BootROM se abre en cada arranque pero exige una clave guardada en `nflasha0`, nunca volcada ([R32](docs/capture/e26-r32-moderreg-valor-real.md), [R33](docs/capture/e26-r33-veracidad-clave-nflasha0.md)). Lo que falta es físico y no está autorizado |
| Obturador silencioso | Logrado con el 3.23 (T040, confirmado por el usuario); exposición por filas medida en el RAW ([E25-10](docs/capture/e25-10-exposicion-por-fila.md)) |
| Selector EFCS / Electronic (3.25) | Implementado y verificado **solo offline** (emulación); nunca validado en la cámara ([E25-24b](docs/capture/e25-24b-implementacion-selector.md), [E25-27](docs/capture/e25-27-construccion-firmware-integrado.md)) |
| Verificación | 4 427 pruebas en local (las que leen firmware se omiten en CI); censo de etiquetas 133/372; 291 sesiones S + 74 informes de fase E; 12/24 planes físicos con prueba; registro T001–T056 |

**Último cierre:** E26 R35 (31-10-2026) — el receptor serie del BootROM acepta varios paquetes por llamada; con R20–R34 el BootROM,
Loader2 y Loader3 quedan descritos por completo en estático. Detalle por informe en [knowledge/CURRENT.md](knowledge/CURRENT.md).

## Cómo funciona el parche del 3.23

El obturador lo gobierna **Darwin**, un microcontrolador aparte (`darwin_core`), que mueve las cortinillas mecánicas y las rearma tras
cada foto. El 3.23 actúa sobre Darwin en dos pasos apilados:

| Paso | Cambio en `darwin_core.bin` (3.21) | Efecto |
|---|---|---|
| **Tipo 0** | `0x20c78..0x20c7f` → `b 0x20c8e; nop; nop; nop` | La función de tipo de mecanismo `0x20c74` devuelve siempre 0 (rama que ya existe, «sin bobinas»): no se activan P4D/P4E |
| **B1a** | `0x1fe6a: 28 46 → 0a e0` (2 bytes) | La compuerta `0x1fe66` devuelve siempre 0; los arrancadores eligen la lista `[0,7,8,9,10]`, que **no usa el motor del obturador** en captura ni en rearme |

La captura y el rearme no llegan a las primitivas que accionan P40/P41, y la exposición la determina el sensor (reinicio y lectura por
filas). Detalle en [E25](docs/capture/e25-desactivacion-mecanica.md) y la [auditoría independiente E25-06](docs/capture/e25-06-auditoria-independiente-paquetes.md).

## Versiones

Sony solo publicó hasta la **3.21**; las demás las generó el autor a partir del firmware oficial. El actualizador solo acepta versiones
**estrictamente mayores** que la instalada.

| Versión | Qué hace | Resultado en la cámara |
|---|---|---|
| **3.21** | Oficial de Sony | Obturador mecánico normal |
| **3.22** | Darwin «tipo 0» (bobinas apagadas) | Instalada en T024 (26-10-2026); arranca. Efecto «sin bobinas» deducido del código, no medido |
| **3.23** | 3.22 + B1a: Darwin no acciona el mecanismo en captura ni rearme | Instalada en T040 (27-10-2026); **dispara en silencio y sin error** (usuario) |
| **3.24** | Darwin oficial con número 3.24, para volver atrás desde el 3.23 | Preparada, no instalada; solo sirve si el actualizador sigue accesible |
| **3.25** | Integrado: selector EFCS/Electronic en BIONZ + C3-B + Darwin condicionado; `nflasha3` recompuesta | Instalada (informado el 29-10-2026); **la cámara no arranca** ([E26](docs/capture/e26-recovery.md)) |

## Qué se midió con el 3.23

- **Imágenes completas** (JPEG 6000×4000 y ARW 6024×4024) sin obturador mecánico; las medidas se hacen sobre el ARW (T044).
- **Disparo y rearme:** 36/36 disparos en ráfagas de 6 y 10/10 sueltos; rearme de 0,7–1,0 s; latencia de 2,6–2,9 s a velocidades rápidas.
- **Exposición** ([E25-10](docs/capture/e25-10-exposicion-por-fila.md)): sin cortina trasera la fila `i` integra **T + ≈7 ms + 15,2 µs·i**
  (lectura ≈ 61 ms), así que de 1/4000 a 1/500 la velocidad apenas escala y la fila inferior recibe hasta 3,7× la superior. Con ShutMode 0
  y `r5` calculado (parches en RAM, T046/T047) la exposición es uniforme: (4219 − `r5`) × 15,2 µs. Llevarlo a firmware fue el 3.25.
- Capturas de ejemplo: [T042](analysis/camera-dumps/20261027-221329-T042-b1a-323/), [T043](analysis/camera-dumps/20261027-223012-T043-suite/)
  y [T044](analysis/camera-dumps/20261027-224101-T044-raw-iso100/) (JPEG reducidos y montajes; los RAW no se versionan).

## Cómo replicar el obturador electrónico completo

«Completo» significa dos cosas a la vez: que no se mueva nada mecánico y que la exposición sea **uniforme** en toda la imagen. La única
forma probada en la cámara de conseguir las dos es combinar dos capas: el firmware 3.23 y un parche temporal en RAM. Lo hicimos así
en T046, T047 y T050.

| Capa | Qué hace | Cómo | Probado |
|---|---|---|---|
| 1. Darwin (3.23) | Las cortinillas no se mueven ni en captura ni en rearme | Instalar el FDAT 3.23 (ver [Instalación](#instalación-del-323-histórica-desaconsejada)) | Sí: T040–T044 |
| 2. BIONZ en RAM | `ShutMode 0` (`0x836d6fb6`) y `r5` calculado según la velocidad (`0x836d7000`) hacen que el sensor controle la exposición de cada fila | `scripts/camera_silent.py` por telnet: comprueba que los bytes sean los originales, deja un guardián que revierte solo a los 25 s, aplica el parche, dispara y revierte ([E25-11 §10](docs/capture/e25-11-r5-bionz-analisis.md)) | Sí: T050, 12 disparos y una ráfaga de 4, siempre revertido |

**Puntos a favor**
- Silencio total y sin desgaste mecánico: 36/36 disparos en ráfaga y 10/10 sueltos con el 3.23.
- Con la capa 2, la exposición es uniforme por filas y proporcional a la velocidad: (4219 − `r5`) × 15,2 µs.
- La capa 2 no deja nada guardado: vive solo en RAM, el guardián la deshace aunque se corte la conexión y un reinicio la borra.
- No hay que tocar `nflasha3` ni flashear nada más allá del 3.23.

**Puntos débiles**
- **Solo con la capa 1, la exposición no es uniforme.** Sin cortina trasera, cada fila recibe T + ≈7 ms + 15,2 µs·i: la parte inferior llega a recibir 3,7 veces más luz y las velocidades rápidas casi no escalan.
- **Escala absoluta:** con la capa 2 la forma de la exposición es correcta, pero el nivel cae ≈ 22 % por debajo del objetivo con una referencia y ±1 % con otra. La incertidumbre es de ±25 % hasta tener una referencia fiable.
- **Rango:** se midió de 1/4000 a 1/30 (T050); 1/8000 solo se ha emulado. Desde 1/15 se vuelve al disparo normal (con el 3.23, 30 s funciona bien); la exposición larga electrónica no está implementada.
- **Efecto rolling:** la lectura dura ≈ 61 ms, así que los objetos en movimiento salen deformados.
- **Dependencias:** necesita acceso telnet a la cámara y la app RemoteShutter. El parche hay que aplicarlo en cada disparo o ráfaga, y antes de calcular `r5` hay que esperar a que la velocidad se estabilice.
- **Sin medir:** flash, vídeo y Live View con los parches activos.
- **Riesgo de base:** instalar el 3.23 ya implica flashear firmware modificado, y no hay recuperación independiente demostrada.

## Qué falló en el 3.25 y cómo se podría solucionar (sin probar)

El 3.25 intentó llevar la capa 2 al firmware, con un selector EFCS/Electronic, para no depender del telnet. Para eso hubo que
modificar `av-cam.bin`, que vive dentro de la partición comprimida `nflasha3` ([E25-27](docs/capture/e25-27-construccion-firmware-integrado.md)):

| Cambio del 3.25 | Diferencia frente a Sony |
|---|---|
| Selector y C3-B en `av-cam.bin` (89 bytes) | Código nuevo, nunca ejecutado en la cámara |
| Darwin condicionado al selector | Cueva nueva, distinta del B1a probado en el 3.23 |
| Recompresión de 3 bloques TPZL (0, 48 y 57; +83 440 B) | El constructor (`scripts/e25_27/tpzl.py`) alinea a **256 B** (`ALIGN = 256`): 359 de 369 entradas quedan con residuo 256, mientras que todas las imágenes de Sony están alineadas a 512 |

**Qué falló:** no se ha demostrado. La desalineación TPZL es la única anomalía frente a todo el corpus de Sony y es la hipótesis
principal. Loader3 la acepta, con solo un aviso, y el ARM7 no lee el residuo. Lo que haga el descompresor por hardware (LDEC) con ese
residuo no se puede saber sin la cámara ([R15](docs/capture/e26-r15-tpzl-custom-fw325.md)–[R17](docs/capture/e26-r17-arm7-ldec-segment-analysis.md)).
Hay alternativas que no se han descartado: el código nuevo de BIONZ o de Darwin, el actualizador, la NAND y la alimentación.

**Cómo solucionarlo. Nada de esto se ha probado:**
1. **Dejar de recomponer `nflasha3`.** Usar el 3.23 con la capa 2 en RAM consigue el mismo resultado sin tocar la partición que falló. Es la vía recomendada.
2. **Si se vuelve a integrar en firmware:** alinear a 512 (`ALIGN = 512`). `scripts/e26_recovery/compare_tpzl.py` ya reconstruye esa imagen solo en memoria y comprueba que sus 369 bloques descomprimen igual que en el 3.25. Para separar las causas, convendría además probar en versiones distintas el cambio de Darwin y el de BIONZ. Ninguna de las dos variantes se ha instalado nunca.
3. **Recuperar esta cámara:** basta con restaurar `nflasha3`, y hay una copia válida (`dev_nflasha3.bin`, [R30](docs/capture/e26-r30-updater-done-boundary.md)). La vía serie del BootROM necesita una clave de 8 B guardada en `nflasha0` (bloque 0, `0xc00`), que solo se puede leer con un lector NAND o JTAG ([R33](docs/capture/e26-r33-veracidad-clave-nflasha0.md)). Antes de eso, una captura UART pasiva diría en qué punto se detiene el arranque. Todo esto es físico y no está autorizado ni probado. Si nada funciona, el último recurso es cambiar la placa.

## Límites y riesgos

- **Sin recuperación independiente** ([E24-04](docs/capture/e24-04-dictamen-seguridad.md), [E25-04](docs/capture/e25-04-recuperabilidad-y-decision.md)):
  Darwin también controla la energía, y un BIONZ o Darwin que no arranca no tiene vuelta atrás demostrada por USB. El caso real es el 3.25.
- **Lo offline no garantiza el arranque:** el 3.25 pasó todas las comprobaciones offline (FDAT, cifrado, extracción inversa, emulación) y aun así bloqueó la cámara.
- **Escenarios sin medir con el 3.23:** operación 5 de Darwin (P40/P41=3) y P4B/P4C siguen activos; su efecto físico no se midió.
- **Respaldo:** la copia externa del respaldo (R1) sigue sin verificar.

## Instalación del 3.23 (histórica; desaconsejada)

Se documenta lo que se hizo, no se recomienda repetirlo. Requisitos: A6000 con **3.21 o 3.22**, batería cargada, USB y
[`pmca-console`](https://github.com/ma1co/Sony-PMCA-RE). Probado solo desde la 3.22 (T040). El repositorio **no incluye** firmware de
Sony ni paquetes: se generan desde tu propio firmware ([E25-05](docs/capture/e25-05-preparacion-paquetes-323-324.md)).

1. Backup de NVRAM en modo servicio (`scripts/senser_backup_dump.py`, guarda fuera del repositorio).
2. Verificar el SHA-256 del 3.23 (`4c21353d…`) y del 3.24 (`e1345aff…`) con `scripts/recovery/r1_manifest.py verify`.
3. Medir el guard sin flashear (`fdat_guard_probe.py`): debe rechazar la versión instalada y aceptar 3.23 y 3.24.
4. Flashear con `pmca-console firmware`; `pmca info` debe dar **3.23**. Registrar la prueba en el [registro](docs/capture/registro-pruebas-camara.md).

## Navegación

| Necesito… | Voy a… |
|---|---|
| Contexto mínimo para retomar | [knowledge/CURRENT.md](knowledge/CURRENT.md) |
| Conclusiones y límites vigentes | [docs/STATE.md](docs/STATE.md) |
| Qué falta (única lista) | [docs/PENDIENTES.md](docs/PENDIENTES.md) |
| Incidente 3.25 y recuperación | [docs/capture/e26-recovery.md](docs/capture/e26-recovery.md) |
| Informes por subsistema | [docs/INDEX.md](docs/INDEX.md) |
| Registro de pruebas en cámara | [docs/capture/registro-pruebas-camara.md](docs/capture/registro-pruebas-camara.md) |
| Historial cronológico | [knowledge/PROGRESS.md](knowledge/PROGRESS.md) |
| Tablero de progreso | <https://nicolvus.github.io/a6000-fw-decomp/progress/> |
| README anteriores | [docs/history/](docs/history/) |
| Uso por agentes | [docs/agent/README.md](docs/agent/README.md), [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md) |

## Estructura

| Ruta | Contenido |
|---|---|
| `docs/` | Estado, pendientes, índice, correcciones e informes (`docs/capture/`) |
| `knowledge/` | Resumen operativo (`CURRENT.md`), historial (`PROGRESS.md`) y auditoría (`audit/`) |
| `analysis/` | Evidencia por sesión; de los volcados de cámara solo se versionan README, `SHA256SUMS`, registros, JSON y JPEG reducidos |
| `scripts/` | Volcados, estado de cámara, recuperación (`recovery/`), empaquetado, auditoría, REA y conocimiento |
| `tests/` | Verificadores por informe; los que necesitan firmware o el manual de servicio se omiten en CI |
| `projects/electronic-shutter/` | Subproyecto del obturador electrónico |
| `site/` | Tablero de GitHub Pages (generado por `scripts/build_pages_status.py`) |

## Reproducir y verificar

```bash
source .venv/bin/activate
CI=1 python -m pytest tests -q                       # suite sin firmware (como en GitHub Actions)
python3 scripts/audit/repo_audit.py                   # enlaces, rutas citadas, cifras y SHA-256 de volcados
python3 scripts/knowledge/search.py text "concepto"  # buscar sin releer el repositorio
```

## Seguridad y contribución

- No se suben firmware de Sony, `*.bin`/`*.elf`, RAW, paquetes generados ni datos personales (el número de serie, el correo personal y
  `libmprctrl.so` se borraron del historial el 31-10-2026; ver R7 en PENDIENTES). Commits convencionales.
- Toda prueba en cámara lleva backup NVRAM previo y se anota en el registro; toda tarea actualiza [PENDIENTES](docs/PENDIENTES.md) en el mismo commit.
