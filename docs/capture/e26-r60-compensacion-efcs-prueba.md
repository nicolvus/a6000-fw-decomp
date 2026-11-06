# E26-R60 — Compensación EFCS: prueba en RAM (EJECUTADA; sin efecto medible a 1/1000)

Fecha: 05-11-2026. Continúa R58 §10-§12 y R57 §8. Prueba en RAM ejecutada el 05-11-2026 con autorización del usuario (revertida); nada instalado.

Etiquetas: **VERIFICADO** (bytes/código) · **INFERENCIA** · **NO VERIFICADO**.

## 1. Idea

R57 §8: con EFCS activado se pierde ≈1,27 ms (gradiente ≈1,2 → 1,6 ms de arriba abajo). El temporizador de host no cierra la exposición (R58 §10). El plan del sensor sí: el productor `0x4383fa40` calcula `sb` (líneas de integración, 15,2 µs/línea) y `sl = r8 − sb` (línea del reinicio, `record+0x64`). Restar N líneas a `sl` adelanta el reinicio electrónico N × 15,2 µs; N = 84 ≈ 1,27 ms. **INFERENCIA**: que ese adelanto compense la pérdida (E25-11/R54 §5 calibraron `r5 = sl` así en el modo Electronic, no en EFCS).

## 2. Hechos de código (VERIFICADO)

* `0x4383fa40` tiene **dos llamadores**: el planificador EFCS (`0x438417c0`, rama `[[0x44020e90]+0x24]==1`) y el normal (`0x437b46d0`, EFCS desactivado). Un cambio dentro del productor afecta a **ambos**.
* No hay cuevas libres (R55 §5) y el bloque TPZL 0 no puede tocarse; en el sitio `0x438417c0` solo caben 10 B. Un parche permanente y selectivo exige reescribir en línea código vecino (como R56); no está hecho.
* Sitio de la prueba: `0x4383fac4` = `uxth.w sl, sl` (`1f fa 8a fa`, comprobado en `av-cam.bin`); se sustituye por `sub.w sl, sl, #N` (`aa f1 NN 0a`; N=84 → `aaf1540a`).

## 3. Prueba en RAM (`scripts/e26_r60/efcs_comp_live.py`)

* Sin flags: **solo lee** el sitio (física `0x8383fac4`, DRAM validada). `--apply` escribe una palabra de 32 bits solo si los bytes son los originales y verifica; `--revert` la restaura. Se pierde al apagar.
* **Riesgos:** (a) afecta también a EFCS desactivado mientras esté puesto; (b) sin `uxth`, `sl` desborda si `sl < N` (velocidades lentas): no disparar más lento de 1/125; (c) la coherencia de la caché de instrucciones tras escribir por SWD no está verificada (R56 §4 parcheó por `/dev/mem` y funcionó).
* **Medida:** con EFCS activado a 1/250, 1/500 y 1/1000, comparar brillo con EFCS desactivado (como R57 §8) con N = 0 y N = 84; ajustar N.

## 4. Pendiente

Dry-run con la cámara encendida (la última lectura falló por BIONZ apagado) y autorización expresa para `--apply`. Si la prueba compensa, un parche selectivo permanente en el planificador EFCS.

## 5. Resultado (05-11-2026, MEDIDO)

Escrito `sub.w/subw sl,sl,#N` en `0x8383fac4` (verificado por relectura, revertido al final). Impresión del usuario con N = 84, 168 y 252 a 1/250-1/1000: «más luz»; con N = 500: «sin diferencia».

**Medida cuantitativa a 1/1000, EFCS activado, normalizada por franja frente a EFCS desactivado** (`scripts/e26_r60/medir_raw.py`; ARW `DSC035 41-46`, 8 franjas, media RAW sin negro):

| N | Fotos | Cociente on/off por franja (arriba → abajo) | Global |
|---|---|---|---|
| 0 | 43 (ISO 10000), 44 (ISO 16000) | 0,29 0,16 0,10 0,05 0,03 0,01 0,00 0,00 | 0,064 / 0,063 |
| 84 | 46 (10000), 45 (16000) | 0,25 0,14 0,08 0,05 0,03 0,01 0,00 0,00 | 0,056 / 0,058 |

Referencia EFCS desactivado (41, 42): gradiente propio de ≈1,7× (la franja inferior recibe más que la superior).

* **Con N = 84 la luz no aumenta; baja un ≈10 %** (0,064 → 0,057), dentro de lo que cabe como ruido pero sin ninguna mejora.
* **Conclusión:** restar líneas a `sl` **no compensa la pérdida de EFCS a 1/1000**: la palanca útil (≈1 ms) no es `sl` o `record+0x64` en este planificador. La sensación de «más luz» a otras velocidades no está medida.
* El eje que limita la exposición con EFCS está probablemente en el cierre de la cortina trasera (Darwin) o en la apertura de la delantera, fuera del plan del sensor.
* Ya no se propone un parche estático basado en `sl`.

