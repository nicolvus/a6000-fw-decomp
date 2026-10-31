# E25-18 — Diseño offline del obturador electrónico de 1/8000 s a 30 s (y BULB)

**Fecha:** 28-10-2026 · **Binario:** A6000 fw 3.21 `av-cam.bin` (SHA-256 `b60c845c…56bb9`, base `0x43541000`) · **Commit base:** `d7a2d032`.
**Alcance:** bytes (Capstone), emulación de código real (Unicorn) y diseño. **No se conectó la cámara, no se escribió RAM/NVRAM/firmware, no se generó instalador.**
Etiquetas: **V** = bytes o emulación del código real · **I** = inferencia · **N** = no verificado. La emulación prueba aritmética y flujo del firmware, **no** el comportamiento del IMX210.

> Nomenclatura: PENDIENTES ya usaba «E25-18» para T052-B1 (C3-B en RAM). Esta sesión toma ese ID por petición del usuario; la fila antigua pasa a **E25-20**.

## 0. Resumen y decisión

1. **Una sola fórmula cubre todo el rango:** el productor nativo `0x4383fa40` (ejecutado, no reimplementado) normalizado frente al predicado de cuadro extra. El predicado suma exactamente un VTS (`shd += VTS`, `svd += 1`; verificado en las 16 velocidades), de modo que `shd' = shd − VTS`, `svd' = svd − 1` recupera el plan de predicado 0 **sin tocar el predicado**. **C3-B es el caso `svd' = 0` y VTS inicial = 4219 de esa fórmula** (idéntico en 1/8000–1/30, §9); lo que C3-B no representa (≥ 1/15 s) lo da el mismo plan con `svd' > 0` o VTS inicial ampliado.
2. **El enganche `0x438c82fe` es correcto y suficiente para la ruta rápida** (≤ 1/30 s): ejecuta solo en el paso 0, después de `cap+0x504` y de `0x43b1e520`, y su escritura de `svd` prevalece (§3). **No basta para la larga:** el planificador de VTS (`0x437b21b8`) y el contador del host leen `record+0x68/+0xd8/+0xda/+0xdc`, que ese enganche no corrige.
3. **Sumidero del VTS ampliado en el sensor: no encontrado.** El VTS por cuadro llega a `record+0x60`, al mensaje de tipo 3 y a `0x43e849c0+0x40` (variable del host); `SetExposure` no lo recibe. Ningún otro acceso literal a esa variable existe en `av-cam` (§6). Es una ausencia de evidencia, no una refutación.
4. **BULB:** el flag `0x8000` (parada externa) solo lo emiten **dos callbacks de temporizador** (`0x438d0e64`, `0x43b1f16c`) armados desde el autómata de captura en `0x438c8aa8` (§7). No hay enlace demostrado botón → fin electrónico.

**Decisión final: C — dos rutas con restricciones explícitas.** Un único modelo de cálculo (`scripts/e25_18/silent_plan.py`), dos despliegues:
- **Ruta rápida** (1/8000–1/30): un enganche, `shd'` y `svd' = 0`; reversible; la única parcialmente validada físicamente (T046/T047: 1/4000–1/60 con `r5` manual).
- **Ruta larga** (1/15–30 s): el cálculo está resuelto y reproducido, pero requiere tres capacidades **no demostradas** (VTS dinámico, `svd` multicuadro continuo, corrección coherente de `record`). El modelo las exige y, sin ellas, **rechaza** en vez de producir un `r5` inválido.

No se elige A (nativa completa) porque exige un segundo punto de intervención y el sumidero del VTS; no B porque no hay dos fórmulas, sino una. No se elige D: existe diseño y todo lo demás está resuelto offline; lo que falta es una pregunta física (§12), no una dependencia que impida diseñar.

## 1. Arquitectura seleccionada

```
Tv ─► productor 0x4383fa40 sobre scratch (record+0xc=3891, +0x1c=1, +0x20=4219 medido, +0xf6=Tv, imager+0x4b8)
        │   pred = 0x43a12ca8() (solo lectura)         ; pred ∈ {0,1}, otro valor → rechazo
        ▼
   normalizar:  pred=1 ⇒ shd' = shd − 4219 ; svd' = svd − 1        (pred=0 ⇒ sin cambio)
        ▼
   validar:  1 ≤ shd' ≤ 0x3FFF · svd' ≤ 0xFFF · VTS inicial ≤ 0xFFFF · ShutMode = 0 · período 3891 · VTS 4219 · modo = foto
        ▼
   ruta rápida (svd'=0 ∧ VTS inicial = 4219): escribir cap+0x64c = shd' y svd' en 0x438c82fe        [1 enganche]
   ruta larga  (resto): exige vts_dinamico ∧ svd_multicuadro ∧ record_coherente; sin ellas → Rechazo
```
`exposición_modelo = (svd'·VTS + VTS_inicial − shd') · período` (identidad `d8 + svd·VTS = L + shd`, V en emulación).

## 2. Comparación de diseños

| Criterio | A — C3-B | B — plan nativo completo | C — híbrido (elegido: una fórmula, dos despliegues) |
|---|---|---|---|
| Precisión | ±2,7 % (cuantización de línea) hasta 1/30 | igual + 0,04–1,28 % por la conversión Tv→µs del firmware | igual a B |
| Continuidad entre velocidades | **no**: `r5<2` desde 1/15 (4219−4388<0) | sí | sí (misma fórmula; frontera 1/30→1/15 explícita) |
| Compatibilidad con el sensor | validada 1/4000–1/60 | VTS≠4219 y `svd>0`: N | rápida validada; larga N |
| Campos modificados | `cap+0x64c` (shd) | shd, svd, `record+0x68/+0xd8..+0xdc` | rápida: shd (+svd); larga: además record |
| Dependencia del predicado | ninguna (usa `record+0xf0`) | total (suma un cuadro) | normaliza algebraicamente; no lo toca |
| Dependencia del VTS | referencia medida 4219 | VTS de `record+0x20` (origen en foto N) | fuerza 4219 en scratch; rechaza si difiere |
| Efecto sobre el secuenciador | ninguno | cambia pasos y VTS por cuadro | rápida: ninguno (`cap+0x650` se restaura); larga: sí |
| AF / Live View / vídeo | no afecta (solo paso 0 de foto) | requiere aislar el modo | el modelo rechaza `modo != foto` |
| Riesgo de corrupción de estado | bajo | medio-alto | bajo (rápida) / medio (larga) |
| Reversibilidad | alta | media | alta (rápida); larga depende del 2.º punto |

## 3. El punto de enganche `0x438c82fe`

Tramo `0x438c829c → 0x438c8344` leído instrucción a instrucción (38 comprobaciones de bytes en `analysis/e25-18/evidencia.json`, 0 fallos):

| Dirección | Efecto |
|---|---|
| `0x438c829c` | `bl 0x437f8a50`; `0x438c82a8..82b6`: consulta `0x43a12c64` (valor 2 ó 3 ⇒ bloque forzado) |
| `0x438c82b8..82cc` | bloque forzado: `cap+0x655=0`, `cap+0x650=0`, `cap+0x64c=2`, `cap+0x652=0`, `cap+0x654=0` |
| `0x438c82d8` | `cbnz [cap+0x4b9c]` ⇒ salta a `0x438c833a`: **solo el paso 0 llega a SetExposure** |
| `0x438c82dc` | `bl 0x43b1e520`: fija `cap+0x73b` leyendo `cap+0x655` (y `cap+0x73a`, `0x43ad90c2`, `[cap+0x12f8]`) |
| `0x438c82e4`/`82f0` | `r7 = cap+0x650`; **si `cap+0x504 == 1`, `cap+0x650 = 0`** |
| `0x438c82fa` | `cap+0x6b8 = [cap+0x12f8]` |
| **`0x438c82fe`** | `bl 0x436d6118` (obtiene el imager): **punto de enganche** |
| `0x438c830c` | `SetExposure(cap+0x64c)` → `0x438c831e` `SetRead(cap+0x6bc)` → SSB (`0x43ad9116`) → `Execute(1)` (`0x43ad911c`) |
| `0x438c8334` | `cap+0x650 = r7`: **restaura el svd nativo** |
| `0x438c83c4` | si `cap+0x740 == 0`: `cap+0x650 = 0` (el contador del host se anula) |

Resultados de emulación del código real (`analysis/e25-18/hook.json`, plan de 1 s):

| Condición | Resultado | Consecuencia |
|---|---|---|
| `cap+0x504=1`, sin enganche | `svd` entregado a SetExposure = **0** | confirma E25-17; con `cap+0x504=1` y plan nativo el sensor recibiría `svd=0` |
| `cap+0x504=1`, escritura en **`0x438c82fe`** | `svd` = **14** | el enganche posterior a `0x82f0` prevalece |
| `cap+0x504=1`, escritura en `0x438c82a0` (E25-16) | `svd` = 0 | un enganche anterior se anula: el nuevo punto es el correcto |
| `cap+0x740=0` | `cap+0x650` final = 0 | la secuencia del host es de un paso aunque `svd>0` |
| ShutMode nativo 3 (`cap+0x12f8 ≤ cfg`), forzar 0 en `0x438c82fe` | `cap+0x73b` = **1** (calculado ya con ShutMode 3), SetExposure recibe 0 | `0x438c82fe` no altera la condición de `0x43b1e520`; la deja como la calculó Sony |
| ídem, forzar 0 en `0x438c82a0` | `cap+0x73b` = 0 | un enganche anterior cambiaría `0x43b1e448/474` |
| bloque forzado (`0x43a12c64=2`) | `shd=2, svd=0, ShutMode 0` antes del enganche | el enganche corre después y sobrescribe: si debe respetarse, comprobar `0x43a12c64` y no actuar |

**Hallazgo nuevo (V):** el `svd` escrito en `cap+0x650` en el enganche **no persiste**: `0x438c8334` restaura el valor previo. Por eso el contador del host y el planificador siguen viendo el plan nativo (con predicado 1: `svd+1`). Es lo deseable en la ruta rápida (el host no cambia) y es la razón de que la larga necesite un segundo punto.

**¿Válido para toda la gama?** **Sí para las rápidas, no por sí solo para las largas.** Para la larga, `0x438c82fe` sigue siendo el sitio correcto para lo que llega a **ID3/ID4** (la emulación de `SetExposure` real así lo muestra), pero hay que corregir además lo que leen `0x437b21b8` y el contador (`record+0x68`, `+0xd8..+0xdc`): segundo punto aún sin elegir (p. ej. la lectura de esos campos en el planificador o una copia coherente en scratch). No se propone uno sin analizarlo (§11).

## 4. Transferencia de parámetros y auditoría de `svd`

`SetExposure` real (`0x436d6f70`, emulado con `scripts/e25_18/secuencia.py`) decodifica el bloque `cap+0x64c`:

| Campo | Destino | Verificado |
|---|---|---|
| `shd` (u16 útil 14 bit) | ID5 = `shd[7:0]`, ID6 = `shd[13:8]` | 5 vectores, 0 fallos (p. ej. 2025 → 233/7) |
| `svd` (12 bit) | ID3 = `svd[7:0]`, ID4 = `svd[11:8]`, `obj+0x3a8` | 14 → 14/0; 472 → 216/1 |
| `spl` (12 bit) | ID7/ID8 | 0 |
| ShutMode | tabla `0x436d70c6` (bits de ID1) | 0 |
| bits altos | descartados (`svd` y `spl` [15:12], `shd` [15:14]) | test |

Trayectoria de `svd` por velocidad (`diferencial.json`; 9 velocidades × `cap+0x504∈{0,1}` × `cap+0x740∈{0,1}`):

| Etapa | Valor |
|---|---|
| A. productor (pred 1) | `svd+1` (1/4000 → 1; 1 s → 15; 30 s → 473) |
| B. bloque de captura `cap+0x650` | el mismo, hasta el enganche |
| C. SetExposure (candidata) | `svd'` (0, 14, 472) |
| D. ID3/ID4 (sombra) | `svd'` |
| E. sustituido por 0 | `cap+0x504==1` **solo si** el valor se escribe antes de `0x438c82f0` |
| F. tras `Execute(1)` | `cap+0x650` = nativo (restaurado) o 0 (`cap+0x740==0`) |
| G. `Execute(0)` posterior | solo con `cap+0x740 ≠ 0` (pasos del host); no emulado |
| H–J. conservación durante la exposición, cancelación, actualización incompatible | **N**: el sensor no se modela |

**Caso obligatorio, 1 s** (`secuencia_1s.json`, productor real, `svd=14`, VTS especial 6727, ShutMode 0, `cap+0x504=0`, `cap+0x740=1`): llamadas `0x43ae769a` → `0x437f8a50` → `0x43a12c64`×2 → `cfg 0x43ad90c2` → **SetExposure** (`shd=1, svd=14, spl=0, ShutMode 0`) → **SetRead** → **SSB** → **Execute(1)** → mensaje `0x107`. Registros sombra: ID3=14, ID4=0, ID5=1, ID6=0, ID7=0, ID8=0; `cap+0x650` final = 14 (con `cap+0x740=1`); VTS por cuadro `[6727, 4219×14]` (suma 65 793 = L + shd). Sin errores. El cuerpo de `SetRead` no se ejecutó (stub); sí su invocación y su bloque de entrada.

## 5. Semántica del predicado (`0x43a12ca8`)

- En el productor (`0x4383fa9a`): si devuelve ≠ 0, `R += VTS` (`0x4383faa0`). Efecto exacto: `shd += VTS`, `svd += 1`, `record+0xf0` y `d8` iguales; con `svd' = 0` los tres VTS pasan de `R` a `[d8, …, VTS]` (dos cuadros). Verificado con el productor real, 16 velocidades, predicados 0 y 1.
- Estado de la cámara: byte 0 en NVRAM ⇒ predicado 1 (T052-B0). **No se modifica el byte, la NVRAM ni el retorno.**
- La ruta propuesta lo **llama como lectura** y normaliza; así el cuadro previo nativo desaparece del plan Silent y el resto del secuenciador (que sigue viendo el plan nativo) no cambia.
- ¿El primer cuadro es un *dummy*? **N.** Hay un indicio indirecto: T047 midió exposición uniforme con `shd` manual `4219−L`; con predicado 1 y `svd` nativo 1 eso daría `4235` líneas (≈ 64 ms). Como se midió ~0,25 ms, el `svd` efectivo en T047 fue 0, lo que encaja con `cap+0x504 == 1` (que anula el `svd`). Es una **hipótesis I** que E25-19 comprueba leyendo `cap+0x504`.
- Si se mantuviera el plan nativo (predicado 1) en Silent, todas las velocidades llevarían un cuadro extra de ≥ 4219 líneas: no es la ruta elegida.

## 6. Flujo del VTS dinámico

Selección (bytes `0x437b2254..0x437b22be`, V; modelada en `matriz.vts_por_cuadro` y verificada por suma):

| Cuadro `record+4` | `record+0x60` | Dirección |
|---|---|---|
| 0 (`sb=1`) | `d8` (`record+0xd8`) | `0x437b22a4` |
| = `svd` (`r8=1`) | `dc` (`record+0xdc`) | `0x437b22b4` |
| intermedios | `da` (`record+0xda`) | `0x437b22be` |

Con `svd=0` el cuadro 0 es también el último y vale `d8 = R`. Después: `0x437b22dc` → `0x436ef628(período·record+0x60)` → `[0x43e849c0+0x40]`; `[r6+0x3b0] = record+0x60·período`, `[r6+0x3b6] = svd`; `b.w 0x43859944` envía el bloque (tipo 3) a otra tarea. `SetExposure` no contiene VTS.

| Pregunta | Respuesta |
|---|---|
| ¿Cuándo se selecciona cada valor? | por VD/cuadro, en `0x437b21b8` (V) |
| ¿Se cambia VTS antes/durante la exposición? | el valor cambia **entre cuadros** del plan (primero `d8`, luego `da/dc`) (V código); si el sensor lo aplica: N |
| Límites | `record+0xd8..dc` son u16 (V); `SetExposure` ID3–ID8 conservan 12/14/12 bit (V). Valores del plan: 4219–8225 < 65 535; el ancho real del registro de longitud de cuadro del IMX210 y las tablas de modo: **N** (sin datasheet) |
| ¿Llega el VTS ampliado al IMX210? | **No demostrado.** Búsqueda exhaustiva de accesos literales a `0x43e849c0+0x40` (`consumidores_vts_host.json`, escaneo con resincronización de todo `av-cam` 0x43541000–0x43B40000): solo el escritor. Un consumidor por puntero (otra tarea/módulo/DFE) **no** queda descartado |
| 4219 / 4389 / 8225 / 6727 / 7737 | todos representables en u16 y en el campo del planificador; programabilidad física **N** |

## 7. BULB y finalización

- **Emisores de `0x8000`:** solo `0x438d0e64` y `0x43b1f16c` (escaneo de los 119 llamadores de `0x43560da8`): activan el flag `0x8000` del grupo `0x13` y publican `(4, 0xf016, 0x8000)`. No tienen `bl` directo: están en la GOT (`0x4402181c`, `0x44024b6c`) y se pasan como **callback** a `0x438c867c` en `0x438c8aa8` (rama `cap+0x4b84`), que arma un temporizador (`0x439018b0`). Es decir, la «parada externa» observable en el código **es un temporizador del autómata**, no el botón. (V)
- Los callbacks de tramo `0x2000/0x4000/0x100000` ya estaban en E25-17 (`0x43b1e4e4/508/4c0`).
- ¿Cambia la finalización el estado electrónico del IMX210? **N** (consistente con S57: sin escritura de registros al terminar). ¿Lectura antes/después de la parada? **N**. ¿RAW de integración continua sin cierre mecánico? **N.**
- **Bloqueo mínimo:** falta el enlace entre la liberación física del disparador y estos callbacks (o un flag equivalente), y qué hace el sensor al cesar el tramo. Hasta E25-19 no hay diseño de BULB; el modelo devuelve `Rechazo` explícito.

## 8. Modelo de referencia y emulaciones

- `scripts/e25_18/silent_plan.py`: `planificar(tv, periodo, vts, suelo, factor, pred, modo, caps, bulb)` → `Plan` o `Rechazo`. Usa el productor real emulado (no reimplementa la aritmética). Capacidades por defecto: todas falsas.
- `scripts/e25_18/secuencia.py`: `setexposure()` (cuerpo real de `0x436d6f70`) y `start_exposure()` (real `0x438c828c`..`0x438c83e8` con stubs registrados para las llamadas externas).
- `scripts/e25_18/matriz.py`: matriz de velocidades, **diferencial original/candidata**, orden del enganche, secuencia de 1 s, regla de VTS.
- Diferencial (9 velocidades × 4 combinaciones de `cap+0x504`/`cap+0x740` = 36 pares): misma secuencia de llamadas en los 36; **únicos bytes de `cap` que difieren: `0x64c–0x64d` (shd)**; `cap+0x650` final y `cap+0x73b` iguales; bloque `cap+0x6bc` de SetRead idéntico. **Limitaciones:** pila, registros CPU y memoria global fuera de `cap` no se comparan (los stubs las vacían); `SetRead`, `SSB` y `Execute` se registran pero no se ejecutan.
- Prueba especial (1 s con C3-B): `c3b_r5(65792)` lanza `ValueError` («no representa 65792 líneas… r5=−61573»); el modelo da `svd'=14` o `Rechazo`.
- Tv ↔ duración nominal: el firmware devuelve `L·3891/256 µs`; el error respecto al nominal es ≤ 2,72 % hasta 8 s y **+1,28 % en 15 y 30 s** (30 s ≈ 30,385 s). La conversión del firmware no es APEX exacta; el código `Tv` real de 15/30 s de la cámara debe leerse en E25-19.

## 9. Matriz de velocidades (predicado 1, capacidades concedidas para el cálculo)

| Velocidad | Líneas | shd' | svd' | VTS inicial | Exposición modelo | Error | Ruta | Requiere | C3-B (`4219−L`) |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| 1/8000 | 8 | 4211 | 0 | 4219 | 0,122 ms | −2,72 % | rápida | — | 4211 |
| 1/4000 | 16 | 4203 | 0 | 4219 | 0,243 ms | −2,72 % | rápida | — | 4203 |
| 1/1000 | 65 | 4154 | 0 | 4219 | 0,988 ms | −1,21 % | rápida | — | 4154 |
| 1/250 | 263 | 3956 | 0 | 4219 | 3,997 ms | −0,07 % | rápida | — | 3956 |
| 1/60 | 1097 | 3122 | 0 | 4219 | 16,674 ms | +0,04 % | rápida | — | 3122 |
| 1/30 | 2194 | 2025 | 0 | 4219 | 33,347 ms | +0,04 % | rápida | — | 2025 |
| 1/15 | 4388 | 1 | 0 | 4389 | 66,694 ms | +0,04 % | larga | VTS dinámico | no representable |
| 1/8 | 8224 | 1 | 0 | 8225 | 124,998 ms | 0,00 % | larga | VTS dinámico | no representable |
| 1/4 | 16448 | 1 | 2 | 8011 | 249,997 ms | 0,00 % | larga | VTS din., svd, record | no representable |
| 1/2 | 32896 | 1 | 6 | 7583 | 499,993 ms | 0,00 % | larga | ídem | no representable |
| 1 s | 65792 | 1 | 14 | 6727 | 999,987 ms | 0,00 % | larga | ídem | no representable |
| 2 s | 131585 | 1 | 30 | 5016 | 2,000 s | 0,00 % | larga | ídem | no representable |
| 4 s | 263171 | 1 | 61 | 5813 | 4,000 s | 0,00 % | larga | ídem | no representable |
| 8 s | 526342 | 1 | 123 | 7406 | 8,000 s | 0,00 % | larga | ídem | no representable |
| 15 s | 999552 | 1 | 235 | 8088 | 15,192 s | +1,28 % | larga | ídem | no representable |
| 30 s | 1999104 | 1 | 472 | 7737 | 30,385 s | +1,28 % | larga | ídem | no representable |
| BULB | — | — | — | — | — | — | — | fin electrónico y emisor del botón | — |

Predicado 0 y 1 probados en las 16 filas (`matriz.json`: `nativo_p0`, `nativo_p1`, `normaliza_igual_p0`). 1/8000 y 1/30 son solo emulación; 1/4000, 1/1000, 1/250, 1/60: T046/T047 con `r5` manual. `svd ≤ 472 < 4096` en todo el rango; un BULB de más de ≈ 262 s por tramo exigiría re-armar `svd` (12 bit).

## 10. Seguridad y recuperabilidad de una intervención futura (no ejecutada)

| Aspecto | Evaluación |
|---|---|
| Solo fotografía | el sitio es el paso 0 de StartExposure; aun así debe comprobarse `cap+0x4b9c==0` y que el modo sea foto, y no actuar si `0x43a12c64 ∈ {2,3}` |
| Parche | 4 bytes (`bl 0x436d6118`, `0df60bff`). Un `bl` no alcanza memoria de scratch (±16 MB): requiere un trampolín en relleno del propio `av-cam` **(no localizado en esta sesión; N)** que salte al cuerpo en scratch, o una instrucción de 4 bytes equivalente |
| Registros y pila | la cueva debe salvar `r0–r3, r12, lr`, conservar alineación de 8 B y ejecutar luego el `bl 0x436d6118` original; el productor preserva `r4–r11, lr` y usa un `record` scratch de 0x158 B (E25-17) |
| Registro global | rápida: intacto (la cueva escribe solo `cap+0x64c..0x64f`; `cap+0x650` se restaura solo). Larga: **no**, hace falta tocar o desviar la lectura de `record` |
| Reversión | restaurar los 4 bytes originales y, si se escribió, `cap+0x64c` se recompone en la siguiente foto (`0x4383fd6c` lo reescribe desde `record`); guardián T050 (reversión probada para parches más simples) **no se asume suficiente** |
| Cachés | escribir con barrera de datos y limpiar la línea de instrucciones (patrón de T046/T047/T050); no verificado para el trampolín |
| Caída del proceso / bloqueo de cámara | el parche vive en RAM: apagar la cámara lo elimina. Plan: guardián independiente con temporizador que reescribe los 4 bytes originales y cancela si cualquier comprobación falla |
| Condiciones de cancelación | período ≠ 3891; `record+0x20` ≠ 4219; predicado ∉ {0,1}; `shd'` fuera de [1, 0x3FFF]; ShutMode nativo ≠ 0; `cap+0x4b9c ≠ 0`; modo ≠ foto |

## 11. Riesgos y restricciones

1. La hipótesis de que `svd'=0` sea lo que T047 ejercitó (§5) es **I**; si el `svd` efectivo era distinto, la ruta rápida puede divergir.
2. La ruta larga depende de tres capacidades no probadas; segundo punto de intervención no elegido.
3. Darwin B1a: no se asume cortina mecánica ni su ausencia; el ShutMode nativo debe leerse.
4. `cap+0x740` es 0 por defecto: el contador del host no sostiene la exposición; cualquier duración depende de `svd`/VTS en el sensor.
5. 1/8000: −2,72 % por truncamiento a 8 líneas; dentro de ±5 %, pero no medido.
6. La emulación no incluye SetRead/SSB/Execute reales ni temporización del sensor.

## 12. Preparación de E25-19 (solo lectura, no ejecutada)

**Pregunta experimental decisiva:** en una foto **normal** de 1 s, ¿el bloque `cap+0x64c` contiene `svd=14` (o `15` con predicado 1) y `cap+0x504` vale 1? Responde a la vez si el plan nativo se usa y si T047 ejercitó `svd=0`.

0. **Prerrequisito:** localizar `cap` mediante un puntero demostrado estáticamente (cadena de GOT que alcance la `r0` de `0x438c828c`/`0x43b1e854`), no por heurística de valores; si no se prueba, E25-19 no se ejecuta.
1. Sin parches ni escrituras; lectura de memoria (telnet/`/dev/mem` ya usados en T052-B0) tras cada foto, antes de la siguiente (campos transitorios pueden borrarse).
2. Campos: `cap+0x64c` (shd), `+0x650` (svd), `+0x652`, `+0x654`, `+0x655`, `+0x6bc..`, `cap+0x740`, `cap+0x504`, `cap+0x4b9c`, `cap+0x72c`, `cap+0x4b84`, `cap+0x73b`; `record+0x60/0x64/0x68/0xd8/0xda/0xdc/0xf0`, `record+0xc/0x20`, estado del predicado (llamada de lectura o byte de NVRAM ya copiado), flujo elegido (`0x43b1ae2a…`), modo de captura. Etiquetar cada valor como **observado** o **inferido**; los borrados no se rellenan.
3. Velocidades: 1/30, 1/8, 1 s, 4 s; BULB ~10 s solo si funciona con normalidad y sin ninguna modificación.
4. Sin instrumentación nueva, sin intentar revertir B1a ni activar cortina.
5. Criterios: (a) `svd` observado frente a 0/14/61; (b) `cap+0x504`; (c) `record+0x20`; (d) `cap+0x72c` sube en BULB; (e) Tv real de 15/30 s.

## 13. Veredictos

Base: **B** bytes · **E** emulación · **M** medición · **A** ausencia de evidencia.

| | Pregunta | Resp. | Base y distinción |
|---|---|---|---|
| A | ¿Se confirmó `0x438c82fe`? | **SÍ** | B+E (orden frente a `0x82f0`, `0x8334`, `0x43b1e520`) |
| B | ¿Válido para rápidas? | **SÍ** | B+E; sin prueba física del enganche |
| C | ¿Válido también para largas? | **NO** (por sí solo) | E: el planificador y el host no se corrigen; capacidad aún no demostrada, no refutada |
| D | ¿Se conserva el plan completo shd/svd/VTS? | **SÍ** en software; **NO** demostrado en el sensor | E / A |
| E | ¿La función nativa da todos los parámetros? | **SÍ** | E (shd, svd, spl, sint, ShutMode, d8/da/dc, líneas) |
| F | ¿`svd` llega a los registros en la ruta candidata? | **SÍ** hasta ID3/ID4 sombra | E con `SetExposure` real; la aplicación por el chip: **A** |
| G | ¿El planificador usa el VTS ampliado? | **SÍ** (host) | B (`record+0x60`, `0x436ef628`) |
| H | ¿Selección inicial/intermedio/final verificada? | **SÍ** | B + modelo contrastado por suma (no se emuló `0x437b21b8` completo) |
| I | ¿Sumidero del VTS en el sensor identificado? | **NO** | A: único acceso literal es el escritor; no refuta un consumidor indirecto |
| J | ¿Se conserva el predicado sin romper Silent? | **SÍ** | E (normalización exacta); el efecto físico: **A** |
| K | ¿C3-B sigue adecuado para rápidas? | **SÍ** | E (igual al plan en 6 velocidades) + M (T047, 4 velocidades) |
| L | ¿Plan nativo preferible para largas? | **SÍ** | C3-B no las representa (E); único origen existente |
| M | ¿Un único diseño cubre todo el rango? | **SÍ** como cálculo; **NO** como intervención | E / diseño C |
| N | ¿Registro global intacto? | **SÍ** rápida; **NO** larga | B+E |
| O | ¿SetRead y geometría preservados? | **SÍ** en el bloque entregado | E (bytes de `cap` idénticos salvo `0x64c–0x64d`); cuerpo de SetRead no ejecutado |
| P | ¿La emulación reproduce 1/15–30 s? | **SÍ** | E (16 velocidades × 2 predicados) |
| Q | ¿IMX210 integra 30 s de forma continua? | **NO demostrado** | **A**; la emulación no es evidencia física. Capacidad aún no demostrada, no hipótesis refutada |
| R | ¿Se identificó el fin electrónico de BULB? | **NO** | A (emisores de `0x8000` = callbacks de temporizador; sin botón ni efecto en sensor) |
| S | ¿Intervención en RAM acotada y reversible para una prueba? | **SÍ** para la rápida; **NO** para la larga | diseño (§10); trampolín no localizado |
| T | ¿Se ejecutó alguna modificación física? | **NO** | — |
| U | ¿Se modificó firmware persistente? | **NO** | — |

## 14. Límites y entregables

Límites: ancho real del registro de longitud de cuadro del IMX210 (N); consumidores indirectos de `0x43e849c0+0x40` (N); productor de `cap+0x504` y `cap+0x740` (N); relleno para el trampolín (N); `0x437b21b8` solo por bytes; stubs de las llamadas externas; sin SetRead/SSB/Execute reales.

- Informe: este documento · Evidencia: `analysis/e25-18/{evidencia,matriz,diferencial,hook,secuencia_1s,consumidores_vts_host}.json`
- Scripts: `scripts/e25_18/{silent_plan,secuencia,matriz,evidencia,consumidores}.py`
- Pruebas: `tests/test_e25_18_silent_full_range.py`
- Regenerar: `python3 scripts/e25_18/matriz.py && python3 scripts/e25_18/evidencia.py && python3 scripts/e25_18/consumidores.py 0x43e849c0 0x40 > analysis/e25-18/consumidores_vts_host.json` (el último tarda ≈ 40 s).
