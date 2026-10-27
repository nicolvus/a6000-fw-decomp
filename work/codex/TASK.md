# Tarea Agente B (Codex) — DFE CXD90027GF y sensor, A7S 3.20 vs A6000 3.21

Trabajas SOLO en `work/codex/` (escritura). Todo lo demás del repo es de solo lectura.
Lee primero `AGENTS.md`, `knowledge/CURRENT.md` y `docs/STATE.md` § "Política de ingeniería inversa".
Restricciones: sin ejecutar firmware, sin cámara, sin flasheo (salvo autorización expresa del usuario
para un caso concreto), sin git push, no modificar `firmware/`,
`analysis/ghidra/`, `silent-liro.*`. No escribas en la base Ghidra histórica (solo readOnly).
Otro agente (Claude) tiene abierta una sesión REA sobre `work/claude/input/a7s-av-cam.bin`
(socket `work/claude/run/rea.sock`): NO la uses ni la cierres. RAM libre ~7 GB: si necesitas abrir
`av-cam.bin` completo, una sola sesión tuya con `analysis/rea-independent/bin/session_daemon.py`
y socket `work/codex/run/rea.sock`; ciérrala al terminar (`q.py SOCK --shutdown`).
Binarios pequeños (dfe.bin 64 KiB): MCP `rea` directo o `llvm-objdump`.

## Entradas
- A6000 DFE: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/dfe/dfe.bin`
  (sha256 fc4e314d…9fcd; ARM, vectores LDR PC, literales 0x0100xxxx).
- A7S 3.20 árbol: `firmware/extracted/a7s-fw320/` (av-cam en `.../nflasha3_unpacked_unpacked/av-cam.bin`, base 0x43541000,
  sha256 b857d338…103e). **Hecho comprobado por el coordinador:** la A7S 3.20 NO contiene un `dfe.bin` ni una imagen con el
  mismo patrón de vectores que el dfe.bin de A6000.
- A6000 av-cam: `.../fw321/.../nflasha3_unpacked_unpacked/av-cam.bin` (base 0x43541000).
- Manuales: `../sony_ilce-7s_level2_level3_sm/`, `sony_ilce-6000_..._level3.pdf`, comparación en `docs/references/a7s-vs-a6000-service-manuals.md`
  (IMX235 en A7S, IMX210 en A6000, CXD90027GF en ambos).

## Preguntas (en orden)
1. ¿Dónde está el código DFE en la A7S? (¿embebido en av-cam.bin, en ROM de la DFE, cargado desde otro blob, o no existe
   como firmware cargable?). ¿Quién carga `dfe.bin` en la A6000 (av-cam, kmod, userland)? Evidencia: offsets, cadenas, xrefs.
2. Arquitectura de dfe.bin A6000: base de carga, entry, vectores, init, manejadores de comandos, memoria compartida/DMA.
3. Comunicación BIONZ X ↔ DFE ↔ sensor: en av-cam (ambos modelos) objetos/clases DFE, `GCS2RxLink`, `MPHYRx4ch`,
   `C_ImagerCtrl_IMX235` (A7S) vs `C_ImagerCtrl_IMX210` (A6000): tablas de registros (ID u16 + dato), SetMode/SetExposure/SetRead.
   Distingue datos sub-LVDS del bus de configuración serie del sensor.
4. Diferencias de registros/secuencias de sensor A7S vs A6000 en modos foto/vídeo que sugieran exposición electrónica completa
   (reset global/rolling, integración por filas, lectura sin cortina). No inventes significados de registros.
5. Valida o refuta con evidencia: 12 canales, sub-LVDS, 54 MHz, 432 Mb/s, sensor (IMX235 vs IMX157).

## Entregables (en `work/codex/`)
`a7s_dfe_architecture.md`, `a7s_dfe_functions.csv`, `a7s_sensor_registers.csv`, `a7s_sensor_command_trace.md`,
`a7s_readout_modes.md`, `codex_evidence.json`. Cada hallazgo: archivo, sha256, dirección/offset, función, instrucciones,
xrefs, interpretación, clasificación (VERIFICADO / INFERENCIA / HIPÓTESIS / DESCARTADO / NO VERIFICADO) y cómo reproducir.
Una consulta REA vacía no prueba ausencia. Escribe un checkpoint `work/codex/CHECKPOINT.md` al avanzar.
Termina con un resumen de 15 líneas máximo.
