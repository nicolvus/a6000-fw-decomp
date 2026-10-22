# S201 — Comparación de registros por subsistema: IMX210 (A6000 fw3.21) vs IMX235 (A7S fw3.20)

22-10-2026. Agente A (sensor y driver), sesión S201 (rango S200–S299). **Solo investigación estática; sin ejecutar firmware, sin cámara, sin flasheo.** Evidencia contra bytes de `av-cam.bin` de ambos modelos.

## Veredicto resumen

| Clasificación | Cantidad | Subsistemas |
|---|---:|---|
| **IDÉNTICO** | 4 | transporte P2S, CheckSet*/LiroSeq (ausente en ambos), …ForLiro (rechazado en ambos), fin de integración (ausente en ambos) |
| **DISTINTO** | 7 | cantidad de modos, selector de modo/drive mode, registros de tiempo svd/shd/spl, fórmula svd, SSB/pulso, ShutMode, registro ID1/modo |
| **AUSENTE EN A6000** | 0 | — |

**Conclusión clave (S203 incorporada):** la A7S implementa el obturador silencioso **por drive mode + tabla de timings** (selector `0x43826d58`, `tipo==2` → modos `0x4e`/`0x4f` de su matriz), **no** por un parámetro `CheckSet*` de LiroSeq (0/0 en A6000 y A7S, S169 vigente) ni por un mensaje `…ForLiro` a Liro (rechazado en ambos, S174). El A6000/IMX210 **no tiene modos de lectura silenciosa equivalentes** (13 modos, `SetMode` devuelve error 2 para `0x4e`/`0x4f`).

**S51 se mantiene (A=NO, B=NO, C=NO):** ninguna diferencia demostrada equivale a una capacidad de obturador electrónico a resolución completa en la A6000; la ausencia de modo silencioso en el firmware no demuestra incapacidad del hardware.

## Metodología y límites

- **REA/bytes primero:** cada dirección, cadena y valor citado se leyó directamente de `av-cam.bin` (A6000 SHA `b60c845c…`, A7S SHA `b857d338…`). No se ejecutó firmware.
- **Una consulta vacía no prueba ausencia:** la ausencia de `CheckSet*` / `…ForLiro` / modo silencioso se confirmó con barrido de bytes, no solo con falta de xrefs.
- **Límite de plataforma:** el A6300 (fw2.01, otra generación LIRO/CXD) se usa solo como contraste secundario (S135/S169/S172); no se abren líneas nuevas con él.
- **Límite físico:** sin datasheet del IMX210/IMX235 ni traza eléctrica, no se asigna significado óptico ni eléctrico a ningún registro; "fin de integración" no está demostrado en ningún modelo.
- **Evidencia reutilizada (vigente tras contradiction-audit):** S57, S58, S169 no tienen correcciones registradas que las invaliden (grafo `claim` vacío para los tres; S169 solo aparece como entrada del catálogo en `linea-general-re.md`, no como corrección).

## Tabla por subsistema

| # | Subsistema | Campo | IMX210 (A6000 fw3.21) | IMX235 (A7S fw3.20) | Clasificación | Veredicto / límite |
|---|---|---|---|---|---|---|
| 1 | Selección de modo de lectura | Cantidad de modos | 13 modos; `SetMode` devuelve error 2 para `0x4e`/`0x4f` | 34 modos, incl. `0x4e`/`0x4f` dedicados a Silent (índices 29, 30) | **DISTINTO** | VERIFICADO (rec_map ID sin modo silencioso; `0x43fee370[29]=0x4e`, `[30]=0x4f`) |
| 2 | Selección de modo de lectura | Selector / drive mode | `SetMode` carga columna de matriz por modo (`0x436d6570`, matriz `0x43fe9b74`) | Selector `0x43826d58(modo,sub,tipo)`: `tipo==2` → `0x4e`/`0x4f` (silent); sin Silent `0x0b`/`0x35`/`0x17`; modo 5 → `0x0c` | **DISTINTO** | VERIFICADO (bytes `0x43826d58`: `cmp r2,#2`=`02 2a`; `movs r0,#0x4e`=`4e 20`; `movs r0,#0x4f`=`4f 20`) |
| 3 | Obturador silencioso / electrónico | Parámetro CheckSet* de LiroSeq | 0/0 `CheckSet*`, 0/0 `SilentShutterMode`, 0/0 `sc_ShutDrive` (S169) | 0/0 `CheckSet*`, 0/0 `SilentShutterMode`, 0/0 `sc_ShutDrive` (S169) | **IDÉNTICO** | VERIFICADO (S169: falta el parámetro, no solo la traza; barrido de bytes) |
| 4 | Obturador silencioso / electrónico | Mensaje a Liro (…ForLiro) | `SetShutterTypeForLiro` ausente; …ForLiro en lista de rechazo (S174) | `SetShutterTypeForLiro` ausente; …ForLiro en lista de rechazo (S174) | **IDÉNTICO** | VERIFICADO (S174: 0/0/6 solo A6300; bytes sin `SetShutterTypeForLiro`) |
| 5 | Temporización de exposición | Registros de tiempo | ID3–ID8: svd (12b), shd (14b), spl (12b); espejo condicional 0x144–0x149 | Columnas de matriz por modo (valores estáticos por modo de lectura) | **DISTINTO** | VERIFICADO (rec_map ID3–8; S57-C; matriz `0x43fee598`) |
| 6 | Temporización de exposición | Fórmula / significado de svd | `svd = n·svr_num − 1` (o `n/VdNum − 1`); contador de pasos del host / periodos VD (INFERENCIA) | No recuperada; valores de columna sin semántica física asignada | **DISTINTO** | INFERENCIA (S57-C `0x4381106c` valida svd; S57-D IMX235 sin función asignada) |
| 7 | Temporización de exposición | Fin de integración (reescritura al terminar) | No hay reescritura de registros al terminar (`ExposureTimerEnd!` sin SetExposure) | No hay comando extra de "terminar integración" en matriz ni pulso (S57-D) | **IDÉNTICO** | NO_VERIFICADO (ningún modelo demuestra fin eléctrico; posible temporización interna del sensor sin evidencia) |
| 8 | Interfaz de transporte (P2S / CISIF) | Bloque y canal | P2S(DFE0), MMIO `0xfc088300`/`0xfc088800`/`0xfc088900`, trama `81\|len\|81\|AH AL\|datos` | Mismo hardware P2S (mismas bases MMIO y programación de bloque, S56-15) | **IDÉNTICO** | VERIFICADO (S56-15 mismo hardware P2S; S56-5/6 formato trama A6000) |
| 9 | Strobe de configuración (SSB) | Pulso SSB | Bit 3 del dato de ID1, enviado dos veces (1,0) en el mismo lote P2S | Bit `0x10` del byte +4 de un registro (`[O+0x3d7]`) dentro de SetExposure/SetRead | **DISTINTO** | VERIFICADO (A6000 `0x436d7c08` bit 3 ID1; A7S `0x436f459c` bit `0x10` byte +4) |
| 10 | ShutMode (selector de obturación del firmware) | Valores y codificación | ShutMode 0–4; ID1 bits 2/7/4/6; en captura real solo 0 y 1 | ShutMode 2 no soportado ("is not supported"); codificación de bits distinta | **DISTINTO** | VERIFICADO (S56-10/17: tbb y bits ID1; sin mapeo 1:1) |
| 11 | Registro ID1 / modo de lectura | Registro de modo | ID1 duplicado (A=`0x4401ca2c`, B=`0x4401c734`); modo + ShutMode + strobe | Registro `0x000c` distingue `0x4e` (0x10) de `0x4c` (0x20); `0x000a` distingue `0x4f` (0x01) de `0x4d` (0x02) | **DISTINTO** | VERIFICADO (rec_map ID1; filas matriz `0x000c`/`0x000a`; sin correspondencia por dirección, S57-D D.5) |

## Determinación de la vía de Silent en la A7S (S203)

La A7S **no** usa `CheckSet*` de LiroSeq (0/0, S169) ni un mensaje `…ForLiro` (rechazado, S174). Por bytes, el selector de modo `0x43826d58` implementa:

- `tipo == 2` (drive mode Silent) → `sub==0` devuelve `0x4e`, `sub==1` devuelve `0x4f`
- Sin Silent → `sub==0`→`0x0b`, `sub==1`→`0x35`, `sub==2`→`0x17`
- `modo == 5` → `0x0c`

Los modos `0x4e`/`0x4f` son columnas 29 y 30 de la tabla de 34 modos (`0x43fee370`), y sus filas de registro difieren mínimamente de `0x4c`/`0x4d` (1 registro cada una: `0x000c` y `0x000a` respectivamente, S57-D). Es decir: **Silent = elección de modo de lectura (drive mode) + columna de timings dedicada**, aplicada vía P2S al sensor. No hay paso intermedio por Liro.

## Qué falta o difiere en la A6000 (resumen para el backlog)

1. **Modos de lectura silenciosa:** el IMX210 no define `0x4e`/`0x4f` ni equivalente; `SetMode` rechaza esos valores. → **ausente en A6000** (funcionalmente).
2. **Selector drive-mode tipo==2:** el A6000 no tiene el selector `0x43826d58` ni el concepto `tipo` de la A7S. → **distinto / ausente**.
3. **Parámetro CheckSet* de LiroSeq para obturador:** ausente en ambos (no es una diferencia A7S-vs-A6000, es una carencia compartida frente al A6300). → **idéntico (ausente en ambos)**.
4. **Mensaje a Liro para obturador:** ausente/rechazado en ambos. → **idéntico (ausente en ambos)**.
5. **Fin de integración electrónico:** no demostrado en ninguno. → **idéntico (NO_VERIFICADO en ambos)**.

## Artefactos

- `analysis/s201_imx210_imx235_registers/compare.json` — tabla estructurada (11 subsistemas, clasificación, evidencias, SHAs).
- `tests/test_s201_imx210_imx235_registers.py` — 7 pruebas de bytes (ver `analysis/s200_imx210_imx235_register_compare/`).

## Siguiente (S202)

Profundizar en tiempos de lectura/exposición: svd/shd/spl del IMX210 vs columnas de modo del IMX235, unidades, contador VD, y análisis del fin de integración.
