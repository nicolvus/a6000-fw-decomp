# G57 — Focus Shift Shooting / Focus Bracket: comando de paso de enfoque localizado, gancho de fin de captura pendiente (15-11-2026)

Sin cámara, sin CFW construido, sin tocar `scripts/gui/harness/`. Código: `scripts/g57/focus_bracket_patch.py`, ajustes en `scripts/cfw_ajustes.py` (`fb_n`, `fb_paso`), tests en `tests/test_cfw_ajustes.py`.

## 1. Hallazgo: existe «mover el enfoque un paso relativo» (VERIFICADO en bytes)
Cadena completa de la API de fábrica que Sony usa para el bracketing de AF (PMCA `CameraEx.shiftFocusPosition`, también existe `startOneShotFocusDrive`/`isFocusDriveSupported`):

| Capa | Pieza | Evidencia |
|---|---|---|
| Java | `CameraEx.shiftFocusPosition` → `native_shiftFocusPosition` | `sony.cameraex.odex`, `libcameraex_jni.so` |
| `libScalarDaemon.so` | `CommandProcessorCameraShiftFocusPosition::SyncProcessor::execute` (`0x1149f0`): lee el parámetro `0x3001` (el paso), espera el evento y llama a `SystemEventIssuerCamera::bracketAF(int jobId, int paso)` (`0xe2b2a`); éste arma un `SysParamList` `{0x101: jobId, 0x204: paso}` y emite el evento de sistema `(0x13, 4)` | `analysis/symbols/libScalarDaemon.so.demangled.txt`, desensamblado Capstone |
| `libObj.so` | `SequenceBracketAF` (ya citado en [s105](../capture/s105-panorama-bracket-interval.md)) | s105 |
| `av-cam` 3.21 | `lc_BracketAF.cpp` (`0x43ca79ba`): dos métodos de `Camera::LC`, **máquina de estados** `0x437c74b6` (campo `+0xa` = paso s16 con `sxth`, `+0xc` = activo, `[obj]` = estado 0/1/2) y `0x437c7554` | desensamblado |
| `av-cam` primitiva | `0x43adcc34` → `0x43adb5e6(r0 = paso u16, r1)` → `0x43adb17a` arma la trama de lente **`{1D, paso_lo, paso_hi, 00, byte4}`** con `byte4 = 2 \| 1<<2 \| 2<<4 \| r1<<6` y la encola con `0x43adb15c`; la máquina de estados espera el fin con `0x43adcc22` («¿cmd 0x1D en curso?», `movs r0,#0x1d; b.w 0x436f6358`) y un temporizador | desensamblado |

Es la ruta «orden de movimiento relativo al objetivo» que se buscaba: **comando de lente `0x1D`, argumento s16 con signo** (el paso), envío asíncrono por la cola de la montura ([s66](../capture/s66-lens-mount.md): trama `F0`, ID en `+5`). No se encontró el camino del anillo MF físico (no hace falta: la primitiva es la misma que usa el bracketing de AF). Cierra la duda de [g52](g52-post-focus.md) §2.

## 2. Diseño integrado (menú → Backup → av-cam)
- Menú (carpeta «CFW», circuito de [g56](g56-ajustes-propios-cfw.md)): «Focus Bracket» (Off/3/5/10/15/20/30 → valor N, id de Backup `0x1070212`, pid `0xEB`) y «Focus Br. paso» (Fino/Medio/Grueso → 4/16/64, id `0x1070213`, pid `0xEC`). La carpeta pasa a 4 ajustes.
- av-cam: cueva `fb_paso` (`0x43541500`, contador en `0x435417F0`): N = Off → nada; si no, cuenta tomas y emite `0x43adb5e6(paso, 0)` mientras `tomas < N`; en la N-ésima reinicia el contador sin mover. N tomas → N-1 movimientos.
- Punto de enganche: **fin de la captura**, una vez por toma (así sirve para disparo único, ráfaga, intervalo y autodisparador continuo, que no tienen que saber del enfoque). Cada toma debe esperar `0x43adcc22 = 0` antes de disparar la siguiente: pendiente.

## 3. Pruebas
- **Unicorn con bytes reales** (`python3 scripts/g57/focus_bracket_patch.py`; test `test_focus_bracket_unicorn_bytes_reales`): comprueba los bytes originales de la primitiva (`0x43adb5e6`, `0x43adb17a`, `0x43adcc22`) y que la cueva cae en hueco cero; ejecuta la cadena **real** `0x43adb5e6 → 0x43adb17a` y captura lo que llega a `0x43adb15c`: Off y byte fuera de tabla → 0 tramas; N = 5 con cada paso (4/16/64) → **4 tramas** `1D pp pp 00 26`; dos series de 5 tomas → 8 (contador reiniciado).
- Corrección de raíz en `cfw_ajustes.leer_asm`: un byte fuera de tabla dejaba en r0 el índice en vez de 0 (el docstring decía 0); ahora devuelve 0. Bulb Timer sigue en verde (`scripts/g55/bulb_timer_patch.py`).
- Arnés: ver §5.

## 4. Límites (NO medido)
- **Unidades y sentido del paso**: el s16 va al objetivo tal cual; no se sabe cuántos µm/pasos del motor son 1, ni qué signo es «hacia infinito». Los valores 4/16/64 son **provisionales**. Medirlos exige cámara + objetivo (o el modelo de lente de `/lens/VX91xx_lensfile.bin`).
- **Gancho de fin de captura sin localizar** (`FOCUSSHIFT-HOOK`): sin dirección verificada no se parchea ningún byte original; `apply_bytes` solo instala la cueva. Candidatos: tras `CaptureUtilityPreReview`, fin de `SequenceSelfTimerReq` (g54), o cola de la rutina de captura de `libObj`; ninguno verificado.
- No se comprobó que el objetivo acepte `0x1D` en cualquier modo (¿AF/MF?, ¿objetivo con motor?); la máquina de estados de fábrica solo lo usa tras armar el bracketing.
- El flag `r1` (bits 6-7 del byte 4) se pasa a 0; en fábrica sale de `0x43af1988` (sin descifrar).

## 5. Arnés (perfil `g57a`, puerto 8760)
Overlay propio (`cfw_ajustes.construir`), qemu y perfil propios parados/borrados. Menú → carpeta «CFW» muestra cuatro filas (`img/g57-carpeta-cfw-cuatro-ajustes.png`); lista de «Focus Bracket» con Off/3/5/10/15/20 (`img/g57-focus-bracket-lista.png`); tras elegir 5 y Grueso (`img/g57-focus-bracket-5-grueso.png`) el `nvram.json` queda con `"1070212": "02"` (índice 2 = N 5) y `"1070213": "02"` (Grueso). Sin SIGSEGV. Tope G36 de 7 opciones respetado (Focus Bracket tiene 7). El consumo en av-cam no es emulable en el arnés (sin gancho): solo Unicorn (§3).

## 6. `SequenceBracketAF` de fábrica: NO dispara, solo mueve un paso (15-11-2026, VERIFICADO en bytes de `libObj` 3.21)
Se investigó arrancar el bracketing «nativo» desde el menú. Resultado: no existe un bracketing disparo→paso→disparo de fábrica; lo que hay es **un único paso de enfoque**, y el ciclo de tomas lo hace quien llama (la app PMCA, entre capturas).
- **Cadena completa**: `libScalarDaemon` `bracketAF(jobId, paso)` → evento → `ModelScalarCameraPatch` (vtable `0x10130c8`, slot 72, función `0x652940`): lee `0x101` (jobId) y `0x204` (paso, **guardado como s8**: `strb`, `ldrsb` en `0x65440a`) y lo reenvía con `0x6543e4` como mensaje `0x3100/0x765a` → dispatcher de `CamUser` (`0xad4ce4`, caso `0x765a` en `0xad57b8`) → `new` (0x34 B) + ctor `CamUser::SequenceBracketAF` (`0xaf45b4`, sin parámetros propios: reenvía r1–r3 a la base `0xa1641c`; vtable `0x1023290`, dtor `0xaf42e8`) → estado de arranque `0xaf4510`: empaqueta el parámetro con `0x9bbb5c` (`0x3027` → empaquetador `0x9b1c80`: byte2=`0x27`, byte3=`0x30`, u32 en +4, byte en +8) y lo envía a `av-cam` → `lc_BracketAF` (`0x437c74b6`); la respuesta (`0x3027xx`, manejador `0xaf43dc`) se devuelve como `0x9502` con `0xf000` (ok) / `0xf001` (error).
- **No hay disparo**: la máquina `0x437c74b6` solo hace `0x43adcc34(paso sxth, flag 0x43af1988)` (la misma primitiva `0x43adb5e6` de la cueva) y espera el fin con `0x43adcc22`/temporizador. Ni `SequenceBracketAF` ni `lc_BracketAF` llaman a ninguna captura.
- **Sin switch por modo de avance**: `0xad4ce4` despacha por id de comando (`0x7506` StillCaptureStart, `0x7518` SetDriveMode, `0x7522` SetBracketMode, `0x753e` SelfTimerReq, `0x765a` BracketAF…); son órdenes de la API externa, no el flujo de S2. No hay punto donde «sustituir la secuencia normal por `SequenceBracketAF`».
- **Consecuencia**: arrancarla desde el menú solo añadiría un rodeo (mensaje `0x765a` → libObj → av-cam) a lo que la cueva `fb_paso` ya hace llamando directamente a la primitiva; seguiría haciendo falta el gancho de fin de captura. Por eso no se parchea `libObj` y la cueva `fb_paso` se **mantiene**. Ventaja menor: la ruta nativa devuelve evento de fin (`0x9502`), pero `0x43adcc22` ya lo da.
- **Unidades (acota `FOCUSSHIFT-UNIDADES`)**: el paso de la API es **s8 (−128…127)** y av-cam lo extiende a s16; 4/16/64 caben. La escala física (µm/pasos de motor) sigue sin medir.
