# A7S 3.20 — traza estática de Silent Shooting (Agente A, Claude)

Fecha 19-10-2026. Análisis solo estático; sin cámara ni ejecución de firmware.

| Binario | SHA-256 | Base |
|---|---|---|
| A7S 3.20 `av-cam.bin` (`firmware/extracted/a7s-fw320/.../nflasha3_unpacked_unpacked/`) | `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e` | `0x43541000` (cabecera `ORIL`, punteros `0x435410xx`) |
| A6000 3.21 `av-cam.bin` (`firmware/extracted/fw321/...`) | `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9` | `0x43541000` |

Métodos: LLVM `llvm-objdump --triple=thumbv7-none-eabi` sobre `input/*-view.elf` (VA real) + escáneres propios de bytes
(`scripts/pcrel_scan.py`, `movwt_scan.py`, `ldst_imm_scan.py`, `imx235_modes.py`) + REA 6.5/Ghidra 12.1.4
(sesión `run/rea.sock`, análisis en frío 624,8 s; resultados `out/rea-batch1.jsonl`, `out/rea-batch2.jsonl`).
REA y LLVM coinciden en todas las funciones de abajo (REA no reconoce `0x436f3b44`/`0x436f3928` como función:
solo LLVM + bytes; REA comparte motor con Ghidra).

## Cadena (menú → sensor)

| # | Paso | Dirección A7S | Evidencia | Estado |
|---|---|---|---|---|
| 1 | Menú/UI: `CmnViewProcessDataElementCustomSilentShutter`, `CautionConfig` nodos Silent On/Off | userland `lib/cmn_view_processDataMgr.so`, `CautionConfig.so` | RTTI/símbolos (no existen en `cmn_view_processDataMgr.so` A6000) | VERIFICADO (cadenas) |
| 2 | `libObj.so` `pvt_SetSilentShutterMode` → `SeqSetSilentShutterMode` → paquete 9 B `05 00 e3 40 rr rr rr rr mm` (comando `0x40e3`) | userland | Mismo protocolo documentado en A6300/A6000 (`docs/capture/a6300-silent-software.md`); en A7S solo cadenas | INFERENCIA (A7S no desensamblado) |
| 3 | Tabla de mensajes LIRO: fila `{0x40e3, 0x437a9cb1, 0}` en `0x43ff79e4` | `0x437a9cb0` | `ldrb r2,[r0,#8]; str.w r2,[0x43ea1d84+0x250]` | VERIFICADO (bytes+LLVM) |
| 4 | Conversor ajuste→tipo: `tipo = {0,2}[mm]` (tabla `0x43bc1658`), 0 si `cap+0x4b84≠0`, `cap+0x785≠0` o `cap+0x1e0==0x19`; flag diagnóstico `[*0x4402be04]+0x7a` fuerza 2 y registra `SET Silent Shutter Type: %d` | `0x4379ec04` | LLVM + REA pseudocódigo; llamadores REA `0x437b65a0`, `0x43813d90` | VERIFICADO |
| 4b | Lectura del ajuste: `ldr r3,[*0x43ea70a0]; ldr r0,[r3,#0x250]` | `0x437b6f6c`, `0x43813e90` | El puntero `0x43ea70a0` es RAM (0 en blob); su escritor no se recuperó | INFERENCIA (mismo offset +0x250 que el receptor) |
| 5 | Guardado en captura: `cap+0x78c = tipo`; si `tipo==2`, `cap+0x748 = 1` | `0x43813e94..ea2` | LLVM | VERIFICADO |
| 6 | Selector de drive_mode: `0x43826d58(cap+0x1e0, cap+0x6d0, cap+0x78c)`: 5→`0x0c`, `0x1b`→`0x1b`; **tipo 2: sub 1→`0x4f`, otro→`0x4e`**; normal: 0→`0x0b`, 1→`0x35`, 2→`0x17` | `0x43826d58`, llamado por `0x43826dc0` que escribe `cap+0x4d0` | LLVM + REA | VERIFICADO |
| 7 | Mapeo secundario: si `cap+0x78c≠2`, `0x0b→0x37`, `0x35→0x38`, `0x4e→0x50`, `0x4f→0x51` | `0x43826c90` | LLVM | VERIFICADO (instrucciones), condición de uso NO VERIFICADO |
| 8 | Política de clase de obturación: `banco+0x404 = (cap+0x20)+0x76c = cap+0x78c` y, con `banco+0x4c4 & 0xe0 == 0`, **`banco+0x404==2` → clase 0** antes de EFCS (`banco+0x424==1` → 1/3) | `0x43862e24` (escritura `0x43862f1c`) → `0x438649bc` | LLVM + REA (pseudocódigo compara `+0x76c==2` tres veces); llamador `0x4382822c` usa `cap+0x4d0/+0x4d4/+0x4d5` | VERIFICADO rama; identidad `cap` INFERENCIA fuerte |
| 9 | ModeRsvParam: `0x437b8948(cap+0x4d0, +0x4d4, +0x4d5)` en `0x4382822c` (equivalente A6000 `0x437f8a50`/`0x43795a60`) | `0x4382824e` | LLVM | VERIFICADO llamada; semántica por analogía |
| 10 | IMX235 `C_ImagerCtrl_IMX235` vtable `0x43fce050` (typeinfo `0x43feeb20`): SetMode `0x436f3b44` acepta modo `1..0x51`, busca en lista de 34 modos `0x43fee370` (vía GOT `0x44027230`), guarda índice en `+0x1b8`, aplica por virtual `+0xa0` = `0x436f3928` | `0x436f3b44` | LLVM + bytes | VERIFICADO |
| 11 | Aplicador: columna = `remap[índice]` (`0x43c9c5b5`), filas de 20 B `{u32 ptr campo, 16 B}` en `0x43fee598` (69 filas). `0x4e/0x50`→col 12, `0x4f/0x51`→col 13, `0x0b/0x37`→col 0, `0x35/0x38`→col 1 | `0x436f3928` | `scripts/imx235_modes.py` → `out/a7s-imx235-setmode-matrix.json` | VERIFICADO estructura; direcciones de registro (u16 en ptr-2) NO VERIFICADO |
| 12 | Diferencias col 0 vs col 12: **45 de 69 campos** (p. ej. grupos `0x2e–0x45`, `0x48/49`, `0x50–0x63`, `0x94–0x9a`); col 12 vs 13 solo 4 campos (`0x01,0x09,0x0a,0x0b`) | — | mismo JSON | VERIFICADO valores; significado eléctrico NO VERIFICADO |
| 13 | SetExposure IMX235 `0x436f4168` (slot `+0x28`): selector `param+9` (ShutMode) 0,1,3,4; **2 → «ShutMode:%d is not supported»**. Clase 0 (paso 8) → caso 0: campo `0x440220a8` bits 2,4,6 a 0 y `0x44021fee |= 8`; campo SHR en `+0x10/+0x12` | `0x436f4168` | LLVM + REA pseudocódigo | VERIFICADO instrucciones; paso «clase→param+9» INFERENCIA (por A6000 `0x4383fd6c`) |
| 14 | Transferencia, procesamiento y guardado de la imagen | — | No trazado en esta ronda | NO VERIFICADO |

## Lectura

En la A7S, Silent no es un bit aislado: el ajuste (mensaje `0x40e3`) produce tipo 2, y este (a) selecciona drive modes
de sensor propios (`0x4e/0x4f`, con 45/69 campos de registro distintos de la foto normal) y (b) fuerza la clase de
obturación 0 en la política que, con obturador mecánico/EFCS, da 1/3/5. No se ha demostrado aquí qué hace eléctricamente
la clase 0 ni las columnas 12/13 (lectura, bits, temporización), ni cómo se suprime la cortina mecánica físicamente.

## Reproducir

```bash
python3 -I work/claude/scripts/pcrel_scan.py work/claude/input/a7s-av-cam.bin 43541000 43ca4b6b   # ref 0x4379ec42
sh work/claude/scripts/dis.sh work/claude/input/a7s-av-cam-view.elf 0x43826d58 0x43826db0
python3 -I work/claude/scripts/imx235_modes.py work/claude/input/a7s-av-cam.bin
python3 -I work/claude/tests/test_a7s_silent_facts.py
```
