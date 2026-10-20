# S52 — ShutMode IMX235/IMX210 y exposición electrónica (consolidado, 19-10-2026)

Fuente: Agente B (Codex) [`work/codex/s52_imx235_imx210_comparison.md`](../../work/codex/s52_imx235_imx210_comparison.md),
emulación Unicorn `work/codex/s52/emulate_setexposure.py` → `s52_shutmode_emulation.json` (30 casos); validado y corregido por Agente A
con arnés propio desde la entrada real (`work/claude/s52/xcheck_emu.py`, [`s52_crosscheck_claude.md`](../../work/claude/s52_crosscheck_claude.md)).

## Despacho

IMX235 `0x436f4168`: `param+9` en `0x436f4198`; `0x436f423e cmp r6,#4; bhi 0x436f42fc; tbb` → casos `424c/425c/42fc(error)/4290/42c4`.
IMX210 `0x436d6f6c`: `param+9` en `0x436d6fb6`; `0x436d70be cmp.w r9,#4; bhi.w; tbb` → casos `70d0/70e0/7114/717a/71ae`.

## Bits por ShutMode (campo de configuración; inicial 0 / inicial `0xff`)

| Modo | IMX235 campo `0x440220ac` | IMX210 campo `0x4401ca2e` | Temporización / 1.ª llamada |
|---|---|---|---|
| 0 | `00` / `ab` | `40` / `6b` | 235: `0x436f2d10` (`[r0]>>8+1`) · 210: `0x436d6f50` |
| 1 | `04` / `af` | `c4` / `ef` | 235: `0x436f2cf4`×r7 · 210: `0x436d6f34` |
| 2 | error («ShutMode:%d is not supported», `0x438f7114`) | `94` / `bf` + copias `param+8/+0x14` → `0x4401c6d2/0x4401c7ce` | 210: `0x436d6f34` |
| 3 | `14` / `bf` | `d4` / `ff` | 235: `param+0xc`/1000+1 → `img+0x3d4`, `0x4355de98` · 210: `0x4355faf0` |
| 4 | `40` / `eb` | `c0` / `eb` | 235: `0x436f2d10` · 210: `0x436d6f50` |

Correcciones de la fase C: (a) IMX235 escribe además `cfg2+4 |= 8` (`0x44021ff2`) en **todos** los modos 0/1/3/4 — corrige la tabla previa
`work/claude/a7s_shutter_modes_comparison.md`, que lo atribuía solo a la clase 0; (b) el rango de modo 3 del IMX210 es `0x436d717a..71a8`
(Codex citaba `0x436d7114..78`, que es el modo 2: REFUTADO); (c) «los tres SHR dan el mismo patrón» es artefacto del arnés de Codex
(arranca tras el prólogo): el prólogo IMX210 escribe SHR y similares en ~12 campos (`0x4401c67a…0x4401c812`), el IMX235 los pasa a
`0x43ad9ec6`. Valores iniciales de globals tomados del fichero: pueden diferir en ejecución.

**Lectura:** ShutMode 0 difiere de 1/3 en bits del campo y en la función de temporización. En ambos sensores 0 borra b2 (que 1 y 3 ponen);
pero los patrones no son iguales entre sensores (IMX210 fija b6, IMX235 lo borra). Significado eléctrico de los bits: **NO VERIFICADO**
(sin datasheet; el campo es RAM de configuración y no se ha recuperado su serialización al bus del sensor).

## Modos de lectura (B4)

IMX235: aplicador `0x436f3928` copia la columna elegida de la matriz de 69 filas `0x43fee598` a punteros de campo; col 0 (`0x0b`) vs col 12
(`0x4e`) / 13 (`0x4f`): **48 campos distintos** entre las tres columnas (45 entre col 0 y col 12), [`work/codex/s52_sensor_register_trace.csv`](../../work/codex/s52_sensor_register_trace.csv)
(48/48 CONFIRMADO por A desde bytes). **Ninguno** pudo clasificarse en geometría / velocidad / temporización / integración / obturación /
sincronización: no se resolvió consumidor posterior tipado → todos **NO VERIFICADO**. La columna `field` es el u16 adyacente al puntero, no un
registro del sensor demostrado.
IMX210: 13 modos, sin matriz equivalente; `0x0b` y `0x2f` son lectura completa 6000×4000 ([doc previo](imx210-video-readout.md)); ninguno es `0x4e/0x4f`.

## Respuesta P4 (ShutMode 0 en IMX210)

La rama existe y modifica el campo `0x4401ca2e` (b2=0, b7=0, b6=1, b4=0) y calcula temporización por `0x436d6f50`. Ninguna ruta normal de la
A6000 demostrada la alimenta (la política no produce 0; overrides sí podrían). Si termina la integración sin 2ª cortina: **NO VERIFICADO**.

## DFE / MMIO (B5)

| Capa | Evidencia | Estado |
|---|---|---|
| Estado LIRO (clase, tipo, `+0x748`) | instrucciones | VERIFICADO (software) |
| Campos IMX (`0x440220ac`, `0x4401ca2e`, matriz) | emulación + bytes | VERIFICADO (RAM de configuración) |
| Aplicadores/transporte (`0x436f2d10`, `0x4355de98`, `0x43ad9ec6`, …) | llamadas registradas | contrato NO VERIFICADO — frontera B5 |
| Registros del sensor / DFE CXD90027GF | — | NO VERIFICADO; `dfe.bin` A7S no reabierto (sin pista nueva) |
| Mecánico | CAIF→MCU Darwin; GPIO genérico | ver [traza de cortinas](s52-a7s-curtain-trace.md) |
