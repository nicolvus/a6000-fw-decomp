# E26-R60 — Compensación EFCS: diseño y prueba en RAM (PREPARADA, sin ejecutar)

Fecha: 05-11-2026. Continúa R58 §10-§12 y R57 §8. **Nada escrito en la cámara; nada instalado.**

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
