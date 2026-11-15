# G55 — Bulb Timer (Canon 7D II): parche de fase 1 en el temporizador por tramos (Unicorn)

Fecha 15-11-2026. Sin cámara, sin CFW, sin arnés (el parche solo toca bytes de `av-cam` del `.dat`). Código: `scripts/g55/bulb_timer_patch.py` (`python3 scripts/g55/bulb_timer_patch.py` = test).

## 1. Diseño confirmado, con una corrección
Confirmado: el fin de BULB ya es «S2 soltado O fin del temporizador». En `0x438c74b0` (V, bytes):
- con `cap+0x740 = 0` y `cap+0x734 = 0`, el objetivo es `T = ldrh [ajustes+0x66]` (`0x438c74f6`; ajustes = `*(0x4402546c)` = `0x43e95950`, BSS);
- `T = 0` ⇒ tramos de un cuadro sin último tramo (sin límite = BULB); `T ≠ 0` ⇒ último tramo `T − n·período` y fin por `0x4000/0x100000`;
- el fin externo (`0x8000`, emisor `0x438d0e64` envía `(4,0xf016,0x8000)`) sale por la misma decisión (E25-17 §2.2).
Corrección: no hace falta tocar la rama de fin ni leer S2. Basta **sustituir `T = 0` por un T propio**: el bucle ya cronometra, cuenta tramos (`cap+0x72c`) y termina por su ruta normal; S2 soltado sigue cortando antes. `cap+0x728` no interviene (solo guarda la duración del último tramo). Un solo gancho, 4 bytes.

## 2. Parche (fase 1)
- Gancho `0x438c74f6`: `b3f86600` (`ldrh.w r0,[r3,#0x66]`) → `bl 0x43541900`. Test de bytes originales incluido.
- Cueva `0x43541900` (hueco cero `0x435418e4…0x43541b00`; la de `0x43541800/20` es de otro parche): devuelve `T` si ≠ 0; si no, `celda·1000` ms (`mul`). Celda u16 en `0x43541920` (segundos; 0 = desactivado = fábrica). T es ms (I: `r7` = período de cuadro en ms y tramo = `valor·31250` ticks, E25-17).
- Rango: u16 de segundos ⇒ 1 s…18 h; 1–900 s y más caben (T sube a 32 bits sin desbordar: el último tramo ≤ período).

## 3. Unicorn (bytes reales de `av-cam.bin` 3.21; llamadas externas con stub; período de cuadro 33 ms)
| Caso | Resultado |
|---|---|
| celda = 0 | 3000 tramos sin fin (espera a S2, como fábrica) |
| imagen original, «celda» = 5 | sin fin (la celda no existe de fábrica) |
| celda = 5 s | fin en el tramo 151: 151 tramos de 33 ms + último de 17 ms (= 5000 ms) |
| celda = 900 s | 27 272 tramos + último; ticks `(900000−27272·33)·31250` |
| T de ajustes = 2000 (≠ 0) y celda = 5 | manda el T de fábrica (60 tramos) |

## 4. Límites y limitación de uso (NO VERIFICADO en cámara)
- **El disparador sigue haciendo falta para iniciar** (el arranque no se tocó). Si Sony mantiene el BULB solo mientras S2 está pulsado, el usuario debe mantener S2 hasta T y el parche solo corta antes; si la cámara admite BULB bloqueado (pulso único, mando/IR) el temporizador cierra solo. No se trazó quién emite `0x8000` (`0x438d0e64`, `0x43b1f16c`): ver pendiente.
- Que `T = 0` ⇔ BULB es inferencia (E25-17 §2.4): solo se cubre la rama `cap+0x740 = 0`; otras rutas (`0x43af6564`, `cap+0x736`) no se tocaron.
- La celda está en RAM de imagen (zona de cueva): que sea escribible en cámara y cómo persiste (NVRAM) no está resuelto; la fase 2 (menú Off/5 s…15 min) debe escribirla desde un manejador, con el patrón de `+0x238`/g39. No se hizo menú ni arnés.
- Precisión: sin medir en cámara (fin con granularidad de cuadro en el último tramo).
