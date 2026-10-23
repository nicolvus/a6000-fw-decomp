# PENDIENTES FINALES — estado de cierre (22-10-2026, corregido)

## 1. B — canales MMIO CONFIRMADOS en av-cam.bin (corrige informe previo)

**VERIFICADO:** Los canales MMIO de B SÍ están en av-cam.bin del A6000 fw3.21:

| Dirección MMIO | Sitios | Tabla literal | Funciones |
|----------------|--------|---------------|-----------|
| 0xf3122300 | 36 | 0x436db000-0x436db0fc | Acceso a registro B (casos 0-5 del dispatcher TBB) |
| 0xf3122200 | 27 | 0x436db230-0x436db2fc | Acceso a registro B |
| 0xf3123200 | varios | 0x436db700-0x436db7fc | Acceso a registro B |
| 0xfc0a3100 | 41 | 0x436db7ac-0x436db7fc | Acceso a registro B |
| 0xf292b000 | 1 | 0x436dbe18 | Bloque base de escritura B |

**Dispatcher TBB en `0x436daf18`:** 6 casos (0-5) que saltan a:
- caso 0 → 0x436db214
- caso 1 → 0x436db3bc
- caso 2 → 0x436db5e8
- caso 3 → 0x436db790
- caso 4 → 0x436db9cc
- caso 5 → 0x436dbc08

Cada función usa `bfi` (bit field insert) sobre el valor leído del MMIO, confirmando que son accesos de registro a hardware.

**Efecto en S51:** Ninguno directo. Los canales MMIO existen pero no demuestran una ruta de exposición totalmente electrónica.

## 2. C2 receptor de cola `0x40193` — BLOQUEADO estáticamente (confirmado)

**Hecho:**
- No hay literal `0x40193` (word LE) en av-cam.bin (0 sitios)
- No hay `movw #0x0193` + `movt #0x0040` consecutivos (0 sitios)
- No hay BL a `osal_reg_msg_queue_cb` (0x43c9a215) desde fuera de OSAL
- No hay BL a `osal_rcv_msg` (0x43561260) desde fuera de OSAL
- `trace_call_path` y `trace_native_values` de REA no encontraron camino desde RelMgr `0x4379eba0` hasta `0x43809ed8`

**Conclusión:** El receptor de la cola `0x40193` usa un mecanismo completamente indirecto (registro dinámico de callback, ID de buzón compuesto, o tabla no accesible estáticamente). **Requiere trazado dinámico (prueba física P1 autorizada) o REA con `trace_native_values` desde el punto de envío en RelMgr.**

## 3. libObj.so — ANÁLISIS SUPERFICIAL

**Archivo:** `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so` (17MB, ELF32 ARM, stripped, PIE)

**Hallazgos:**
- Todos los símbolos son UND (importados desde MprIf, MWF). No hay definición local de `RecordStill::Execute`.
- `RecordStill::Execute` (0x90b248 en av-cam.bin) está en libObj.so, fuera del alcance de av-cam.bin.
- 0x40193: 9 sitios, todos falsos positivos (`lsls r3,r2,#6` = `0x0193` opcode)
- 0xf292b000: 16 sitios, todos falsos positivos (`movs r0,r0` = NOP)
- 0xf3122xxx, 0xfc0a3xxx: 0 sitios

**Conclusión:** libObj.so no contiene el receptor C2 ni los canales MMIO de B como literales directos. El análisis de libObj.so requiere Ghidra/REA con símbolos, no solo búsqueda de bytes.

## 4. Cobertura de módulos (33.6% → 247 pendientes)

**D:** continúa con cola de módulos (tareas D-02/D-03 pendientes: desensamblar casos 1, 4+ de fila 8 de tabla 0x43edccf8)
**E:** [SENSER], [STABILIZER], [AVOUT] — no tocados, el agente E los cubre
**S500-S515:** completados (64 tests PASS, 15 skipped)

## 5. Decisión S51 — SIN CAMBIOS

**A=NO, B=NO, C=NO.** Ningún hallazgo de esta sesión altera la decisión. Los canales MMIO de B existen pero no demuestran una ruta de exposición totalmente electrónica.

## 6. Pruebas físicas P1-P8 (requieren autorización de usuario)

| Prueba | Objetivo | Riesgo |
|--------|----------|--------|
| P1 | Observar `0x83e9bd50` (G+0x808) en cambios de menú | Bajo |
| P2 | Forzar `0x808`=1 sin disparar | Bajo-medio |
| P7 | Prueba objetiva (hélice/LED) | Medio |

## Archivos generados/actualizados esta sesión

- `docs/capture/PENDIENTES_FINALES.md` (este documento, corregido)
- `docs/capture/shutter-trigger-chain-0x3011.md` (C2 chain, actualizado)
- `docs/capture/capture-stage-reuse.md` (tabla de secuencias, actualizado)
- `docs/capture/sfra-electronic-frame-source.md` (productor YC SFRA)
- `docs/capture/sony-dcf-playback.md` (DCF/reproducción)
- `docs/capture/s134-svrnum-vdnum-status.md` (S134 writers)
- `analysis/rea-independent/out/C2_CHAIN_ANALYSIS.md` (C2 analysis)
- `analysis/rea-independent/out/c2_dispatcher_0x43807f4c.txt` (desensamblado dispatcher C2)
- `analysis/rea-independent/out/c2_handlers_0x43808100.txt` (handlers dispatcher)
- `analysis/rea-independent/out/c2_handlers2_0x43808400.txt` (handlers adicionales)

Sesión cerrada. Todo verificado contra bytes/instrucciones.