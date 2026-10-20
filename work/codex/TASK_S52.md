# S52 — Agente B (Codex): propagación de clase 0, SetExposure IMX235/IMX210, registros, DFE/MMIO

Directorio exclusivo: `work/codex/` (scripts nuevos en `work/codex/s52/`). No escribas fuera salvo lectura.
NO empieces de cero: lee `knowledge/CURRENT.md`, `docs/capture/a7s-silent-reconstruction.md`, `work/claude/a7s_silent_execution_trace.md`,
`work/claude/a7s_shutter_modes_comparison.md`, `work/codex/crosscheck.md`, `docs/capture/s51-decision.md`,
`docs/capture/s50-parallel-conclusions.md`, `docs/capture/imx210-video-readout.md`, `docs/STATE.md` § Política de ingeniería inversa.
Usa el sistema de conocimiento (`scripts/knowledge/`) antes de buscar a mano.

## Entradas (solo lectura; hashes en `analysis/s52-hashes.initial.sha256`)
- A7S 3.20 `work/claude/input/a7s-av-cam.bin` / `a7s-av-cam-view.elf` (base `0x43541000`, Thumb) — leer, no escribir.
- A6000 3.21 `work/claude/input/a6000-av-cam.bin` / `a6000-av-cam-view.elf`; A6000 `dfe.bin` (ver `work/codex/a7s_dfe_architecture.md`).
- `work/claude/out/a7s-imx235-setmode-matrix.json` (matriz 69 filas × columnas, ya extraída), `work/claude/out/*setexposure.s`.
- Herramientas: `llvm-objdump --triple=thumbv7-none-eabi`, Python con capstone/unicorn/keystone/lief en `~/.venvs/re/bin/python`
  (Unicorn sirve para emular offline las ramas ShutMode de SetExposure y volcar escrituras de memoria), REA vía daemon.

## REA (sesión propia, separada de Claude)
```bash
nohup python3 analysis/rea-independent/bin/session_daemon.py work/codex/run/rea.sock '{"path":"<ruta abs al av-cam.bin A7S original en firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin>","format":"raw-binary","architecture":"arm","entry_point":"0x43541000"}' > work/codex/run/daemon.log 2>&1 &
# espera work/codex/run/rea.sock.ready (~8-10 min); consultas por lotes con q.py; --shutdown al terminar.
```
Claude corre otra sesión REA A7S en paralelo: antes de abrir una segunda (p. ej. A6000) comprueba `free -g` ≥ 4 GiB disponibles;
si no, cierra la tuya primero o usa LLVM/bytes. Un timeout o resultado vacío NO prueba ausencia. Lo decisivo: verificar en LLVM+bytes.

## Objetivos (resumen operativo del encargo del usuario)
- **B1** Cadena demostrada por instrucciones desde la política A7S `0x438649bc` (destino de la clase) hasta `param+9` del SetExposure
  IMX235 `0x436f4168` (slot vtable `+0x28` de `C_ImagerCtrl_IMX235`, vtable `0x43fce050`): intermediarios, copias de estructura, wrappers,
  despachos virtuales, constructores de parámetros, transformaciones. Contrasta con A6000: política `0x43842158`, `0x4383fd6c`,
  wrapper `0x436d6320`, SetExposure efectivo `0x436d6f6c`. No aceptes la correspondencia por analogía.
- **B2** Ramas ShutMode 0/1/3/4 de IMX235 `0x436f4168` vs 0/1/2/3/4 de IMX210 `0x436d6f6c` a nivel de ensamblador: escrituras de bits,
  buffers de registros, máscaras, integración (SHR), lectura, temporización, funciones de aplicación y transporte al sensor. Tabla de
  diferencias por instrucción. ¿Qué cambia en IMX235 con ShutMode 0 frente a 1/3? Si no es demostrable físicamente, la frontera exacta.
- **B3** ShutMode 0 en IMX210: ¿se usa hoy en A6000 (quién puede invocarlo, vídeo/LV/foto)? Campos y registros que modifica, efecto en
  integración/lectura/sincronización, condiciones de resolución completa, si permite terminar integración sin 2ª cortina. Sin inventar
  nombres de registro.
- **B4** Modos de lectura completa: IMX235 `0x0b` vs `0x4e/0x4f`; IMX210 `0x0b`, `0x2f` y otros. Dimensiones, binning/skipping, bits,
  temporización, líneas, duración de lectura, reset electrónico, integración. Clasifica los **45 campos** distintos (col 0 vs col 12)
  en geometría / velocidad de lectura / temporización / integración / control de obturación / sincronización / NO VERIFICADO.
  No traduzcas valores IMX235 a registros IMX210.
- **B5** Qué llega efectivamente al DFE CXD90027GF o al hardware: distingue registros del sensor, del DFE, MMIO del SoC, memoria compartida,
  estado de software, DMA, controladores mecánicos. No reabras la búsqueda de `dfe.bin` A7S salvo pista técnica nueva. Prioriza B1.

## Entregables (en `work/codex/`)
`s52_shutmode_propagation.md`, `s52_imx235_imx210_comparison.md`, `s52_sensor_register_trace.csv`, `s52_electronic_exposure_analysis.md`,
`s52_dfe_mmio_trace.md`, `s52_evidence.json`. Además un test independiente `work/codex/s52/test_s52_shutmode_facts.py`
(Python, `-I`) que compruebe automáticamente bytes, destinos de salto, offsets, condiciones de rama y la propagación que afirmes VERIFICADA.
Para H52-3, H52-4, H52-5, H52-7: evidencia a favor/en contra, confianza, incógnitas, próxima comprobación, estado
(VERIFICADO/INFERENCIA/HIPÓTESIS/DESCARTADO/NO VERIFICADO). Checkpoint vivo en `work/codex/s52/CHECKPOINT.md`.

## Prohibido
Flashear, ejecutar firmware real, modificar binarios, `silent-liro.*`, `analysis/ghidra`, informes consolidados, `git push`, escribir en
`work/claude/`. Error histórico tuyo: `0x43826dc0` llama al SELECTOR de drive_mode, no al conversor; los llamadores del conversor
`0x4379ec04` son `0x437b65a0` y `0x43813d90`. Verifica llamadores reales por instrucciones.
