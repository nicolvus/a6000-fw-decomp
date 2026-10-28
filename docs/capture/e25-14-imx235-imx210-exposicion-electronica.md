# E25-14 — Temporización del obturador electrónico: IMX235 (A7S) frente a IMX210 (A6000)

Sesión **100 % offline** (28-10-2026). No se conectó la cámara, no se ejecutó firmware, no se escribió RAM/NVRAM/NAND.
Binarios verificados por SHA-256 antes de comparar:

| Binario | SHA-256 | Base |
|---|---|---|
| A7S fw 3.20 `av-cam.bin` | `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e` | `0x43541000` |
| A6000 fw 3.21 `av-cam.bin` | `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9` | `0x43541000` |

Etiquetas: **V** = bytes/instrucciones leídos; **I** = inferencia; **N** = no verificado. Las pruebas mecánicas están en
`tests/test_e25_14_exposicion.py` (se omiten si falta el firmware).

## 1. Resumen ejecutivo

1. **La cadena Silent del IMX235 está reconstruida hasta el driver**: BIONZ prepara dos bloques de 16 B por captura
   (`cap+0x648` para `SetExposure` y `cap+0x6b0` para el método de velocidad), llama a `SetExposure`
   (`vtable+0x28 = 0x436f4168`) y después al método de velocidad (`vtable+0x30 = 0x436f4a94`) **en ese orden**. (V)
2. `SetExposure` no recibe un tiempo: recibe `param+0` (posición/`SHR` en líneas), geometría en `param+4/+6` y
   `ShutMode` en `param+9`; el ShutMode 0 cambia bits de configuración y calcula un contador auxiliar desde una tabla
   de 12 B por modo. La integración real se expresa en **líneas enteras**. (V)
3. El método de velocidad `+0x30` sí recibe una representación temporal y la convierte en líneas con
   `0x436f5df0` (A7S) / `0x436d8a90` (A6000), dos funciones **semánticamente idénticas** (misma tabla lineal de 256
   entradas, mismo clamp, misma división). (V)
4. **La A6000 ya llama a ese método en la foto normal** (`0x438c831e`), con el bloque `cap+0x6bc`. La conclusión de
   E25-11 «la foto no recibe la velocidad» es incompleta: la recibe por el método `+0x30`; lo que no usa es
   `ShutMode 0` (el registro de modo lleva `param+9=3`). (V)
5. El único mecanismo del driver que puede ir **más allá de un cuadro** es una máquina de estado del A7S
   (`0x436f43c0/0x436f43f0`, estado `obj+0x3dc` 2/1, recurso hardware `0xe`), armada por el **tercer argumento** del
   método `+0x30`. La A7S la arma en una ruta concreta (`0x438b6f02`, `r3=1`) y la desarma en la captura normal
   (`0x438b77be`, `r3=0`). (V)
6. **El método `+0x30` de la A6000 no guarda ni usa el tercer argumento antes de la primera llamada** y no contiene
   esa máquina de estado; fija `obj+0x3a3=1` por sí mismo. No se encontró en él un equivalente al armado de
   exposición larga. (V para la diferencia de código; N para ausencia en todo el firmware)
7. El límite de ~65 ms no es solo de nuestro parche: la función de conversión satura en **un cuadro** (máximo de
   líneas del modo). Para superarlo haría falta un modo de sensor con cuadro más largo o acumulación multicuadro; no
   se encontró ninguno demostrado. (V/I) **Corrección posterior (E25-17):** el productor nativo `0x4383fa40` sí planifica más de un cuadro
   (`svd = cuadros − 1` en `record+0x68`, VTS ampliado en `record+0xd8`); el límite es de la ruta manual `r5`, no un clamp del firmware.
   Sigue sin demostrarse el efecto físico. [E25-17](e25-17-bulb-exposicion-electronica-larga.md)
8. La precisión de las velocidades rápidas es de **una línea (15,2 µs)**; no se encontró temporización fraccionaria
   ni corrección de latencia. El sesgo de T050 (±20–25 %) no se explica solo por cuantización salvo en 1/8000. (V/I)

## 2. Cadena Silent real del IMX235

### 2.1 Entrada y representación

La captura de la A7S (`0x438b7728`) hace, en orden:

| Paso | Instrucción | Qué hace | Estado |
|---|---|---|---|
| 1 | `0x438b7748 bl 0x439fb708` | lee el modo de disparo; si es 2 o 3 fuerza `param+9=0` y `param+0=2` | V |
| 2 | `0x438b77a0..0x438b77ac` | `SetExposure(cap+0x648, [cap+0x4bb0])` por `vtable+0x28` (`0x436f2938`) | V |
| 3 | `0x438b77b4..0x438b77be` | `SetShutterSpeed(cap+0x6b0, [cap+0x4bb0], r3=0)` por `vtable+0x30` (`0x436f2988`) | V |
| 4 | `0x438b782a..0x438b7834` | si `cap+0x748` (tipo Silent) y `cap+0x60c==0`, toma `r5 = u16(0x438284b4(cap))` | V |
| 5 | `0x438b7852..0x438b7868` | envía el mensaje `0x107` a Darwin con `[cap+0x570]` y `[cap+0x574]` | V |
| 6 | `0x438b78f8` | arranca la secuencia de captura `0x437b8bec` | V |

`0x438284b4` construye el bloque `cap+0x6b0` (16 B) a partir del registro de modo (`0x43862158` /
`0x438625a0`). Es el mismo patrón que la A6000 (`0x437f8a50` → `0x4383fd6c` / `0x43840150`). (V)

### 2.2 `SetExposure` del IMX235 (`0x436f4168`, `vtable+0x28`)

- `r1 = *(u32*)param`; `r8 = param+4`; `r9 = param+6`; `r6 = param+9` (`0x436f4198 ldrb.w r6,[r10,#9]`). (V)
- `r7` = bits 0–13 de `param+0` (`lsl #0x12; lsr #0x12`), con override por el byte de configuración
  `[cfg+0x2e]`. (V)
- Escribe `r8 → obj+0x10`, `r7 → obj+0x12`, `obj+0x19=1`, y llama a `0x43ada042(obj+0x13c, r8, r7, r9, ShutMode)`:
  guarda ventana y modo en el bloque de comandos del sensor (`+0x50/+0x52/+0x54/+0x57`). (V)
- Despacho: `0x436f423e cmp r6,#4; bhi error; tbb` → casos `0x424c` (0), `0x425c` (1), `0x42fc` (2 = error),
  `0x4290` (3), `0x42c4` (4). (V)

| Modo | Bits de configuración | Temporización auxiliar | Destino |
|---|---|---|---|
| 0 | `cfg1` b2=0, b6=0, b4=0; `cfg2` b3=1 | `0x436f2d10(obj+0x2d8, obj+0x1b8)`; `([fila]>>8)+1` | `obj+0x3d4` |
| 1 | b2=1, b6=0, b4=0; `cfg2` b3=1 | `([fila+4]>>8) * r7 / 1000 + 1` | `obj+0x3d4` |
| 3 | b2=1, b6=0, b4=1; `cfg2` b3=1 | `param+0xc / 1000 + 1` | `obj+0x3d4` |
| 4 | b2=0, b6=1, b4=0; `cfg2` b3=1 | igual que 0 | `obj+0x3d4` |

La tabla de 12 B por modo está en `0x43bd8154` (34 filas); `0x436f2d10` indexa con `obj+0x1b8` y devuelve
`fila = base + 12·índice`. Las seis primeras filas son `14539, 14756, 14974, 15192, 15411, 15630` (µs si la unidad
es 1 µs; la unidad exacta no está cerrada). (V estructura; I unidad)

### 2.3 Método de velocidad del IMX235 (`0x436f4a94`, `vtable+0x30`)

- Entrada: `r1` = bloque de 12 B (`cap+0x6b0`), `r2` = modo, `r3` = **armado de exposición larga**. (V)
- Guarda `r3` en `[sp+0x30]` (`0x436f4aa8 str r3,[sp,#0x30]`). (V)
- Convierte con `0x436f5df0` (clamp + tabla lineal de 256 entradas + división) y devuelve un valor de líneas. (V)
- Si el valor de entrada supera `0x1000`, ejecuta `0x436f4b10..0x436f4b22`:
  `cmp r8,#0x1000; add r3,r8,#0x1000; r6 = r3 − fila[0x1e]; obj+0x3d7=1`. (V)
- Si `r3` (armado) ≠ 0: `0x436f43c0` pone `obj+0x3dc=2` y llama a `0x43b73044(0xe)`; si es 0: `0x436f43f0`
  vuelve a `obj+0x3dc=1`. (V)
- Empaqueta el flag en el bloque de comandos: `0x436f5268..0x436f528e` construye
  `arg5 = ([obj+0x3dc]<<8) | obj+0x3d7` y llama a `0x43ada062` (`+0x60..+0x66`). (V)

**Interpretación (I):** `0x1000` (4096) es una frontera de representación de la posición de obturación, no un
temporizador de exposición: la rama reexpresa el valor cuando cruza esa frontera. No hay contador de cuadros ni
acumulador en la función. La alternativa «la rama es el inicio de una integración multicuadro» no está demostrada.

## 3. Mecanismo de exposición larga

### 3.1 Lo que existe

| Elemento | A7S / IMX235 | A6000 / IMX210 | Estado |
|---|---|---|---|
| Método de velocidad `+0x30` | `0x436f4a94` | `0x436d7e08` | V |
| Conversión a líneas | `0x436f5df0` | `0x436d8a90` | V (idénticas) |
| Rama `>0x1000` | `0x436f4b10` | `0x436d7e9a` | V |
| Flag de la rama | `obj+0x3d7` | `obj+0x3a3` | V |
| Estado de armado | `obj+0x3dc` (2/1) + `0x43b73044(0xe)` | **no encontrado en el método** | V/N |
| Tercer argumento de armado | sí (`r3`) | **no se guarda ni se usa antes de la 1.ª llamada** | V |
| Contador de cuadros / acumulador | no encontrado | no encontrado | N |

### 3.2 Lo que haría falta para > 1 cuadro

Para una exposición uniforme mayor que un cuadro hay tres familias posibles:

1. **Cuadro más largo** (VTS/línea más lenta). No se encontró una tabla o registro que alargue el cuadro por
   velocidad; la tabla de 12 B es común a ambos sensores y no depende de la velocidad. (N)
2. **Contador de varios cuadros**. No hay contador en `SetExposure` ni en `+0x30`; la máquina `0x3dc` es lo más
   parecido, pero su efecto eléctrico no está demostrado. (N)
3. **Acumulación electrónica** (mantener el reset y leer al final). La rama `>0x1000` y el flag podrían ser parte de
   ello, pero no hay evidencia de que el flag cambie la secuencia de reset/lectura; solo se empaqueta hacia el bloque
   de comandos. (N)

### 3.3 Lectura de los datos de T044/T046

La saturación medida a ~64,9 ms (T046) coincide con **un cuadro completo** (4219–4270 líneas × 15,2 µs). El método
`+0x30` no ofrece un valor mayor: su clamp superior es el máximo de líneas del modo. Por tanto, el límite actual es
también el del firmware, no solo el del parche `r5`. (V/I)

## 4. Control de las velocidades rápidas

- La unidad es la línea: `15,2 µs` (medida independiente en T044 y T046). (V)
- 1/8000 = 125 µs ≈ **8,2 líneas**; 1/4000 ≈ 16,4; 1/1000 ≈ 65,8; 1/500 ≈ 132. (V aritmética)
- No se encontró temporización sub-línea, corrección de latencia ni frecuencia de reloj distinta por modo en
  `SetExposure`/`+0x30`; todos los ajustes son de líneas enteras. (V ausencia en estas funciones; N en el resto)
- La rama `>0x1000` ajusta en bloques de 4096, no en fracciones de línea. (V)
- **Sesgo de T050:** a 1/1000 una línea es 1,5 %; a 1/4000, 6 %; a 1/8000, 12 %. Un sesgo de −22 % no se explica
  solo por cuantización salvo, quizá, en 1/8000. La explicación más probable sigue siendo la calibración de la
  escena por tanda (E25-10/E25-11), no la fórmula. (I)

## 5. Comparación IMX235 ↔ IMX210

| Función o mecanismo | A7S / IMX235 | A6000 / IMX210 | Equivalencia | Evidencia |
|---|---|---|---|---|
| Entrada de velocidad | bloque `cap+0x6b0` (16 B) | bloque `cap+0x6bc` (16 B) | estructural | `0x438b77b4`, `0x438c8314` (V) |
| Conversión temporal | `0x436f5df0` | `0x436d8a90` | **idéntica** (clamp + tabla 256 + división) | bytes y tabla `0x43bd80e4` / `0x43bdbebe` (V) |
| `SetExposure` | `0x436f4168` (`vtable+0x28`) | `0x436d6f6c` (`vtable+0x28`) | mismo contrato `param+0/4/6/9` | despacho y prólogo (V) |
| `SetMode` | `0x436f3b44` (`vtable+0x20`) | `0x436d6b50` (`vtable+0x20`) | mismo contrato; listas/matrices distintas | S52 + bytes (V) |
| ShutMode 0 | `cfg1` b2=0, b6=0, b4=0; `cfg2` b3=1 | b2=0, b7=0, b4=0, b6=1; `cfg2` b3=1 | misma rama; bits distintos (sin afirmar equivalencia eléctrica) | `0x436f424c`, `0x436d70d0` (V) |
| Tiempo de línea | 15,2 µs (medido) | 15,2 µs (medido) | igual | T044/T046 (V) |
| Longitud de cuadro | 4219–4270 líneas (medido) | 4219–4270 líneas (medido) | igual | T046 (V) |
| Tabla de tiempos por modo | `0x43bd8154` (34×12 B) | `0x43bdbf2e` (30 filas) + `0x43bdc0ca` (4) | **30 filas idénticas** | comparación byte a byte (V) |
| Tiempo de integración | `param+0` (SHR/líneas) | `param+0` (SHR/líneas) | mismo campo | T046/T047 (V) |
| Reinicio del sensor | ShutMode 0: por filas (uniforme) | ShutMode 0: por filas (uniforme) | mismo comportamiento medido | T046 (V) |
| Lectura del sensor | por filas, ~61 ms | por filas, ~61 ms | igual | T044/E25-10 (V) |
| Exposición > 1 cuadro | máquina `0x3dc` + `0xb73044(0xe)`, armado por `r3` | **no encontrada en `+0x30`** | no demostrada | `0x436f43c0`, `0x436d7e08` (V/N) |
| Límite de integración | 1 cuadro (~64,9 ms) | 1 cuadro (~64,9 ms) | igual | T046 + clamp (V/I) |
| Parámetros para velocidades rápidas | líneas enteras; rama `>0x1000` | líneas enteras; rama `>0x1000` | idéntica | `0x436f4b10`, `0x436d7e9a` (V) |
| Parámetros para velocidades lentas | clamp al máximo de líneas | clamp al máximo de líneas | idéntica | `0x436f5df0`, `0x436d8a90` (V) |

## 6. Fórmulas, direcciones y límites

- `SetExposure` IMX235: `0x436f4168`; `param+9` en `0x436f4198`; despacho `0x436f423e`; modo 0 `0x436f424c`;
  temporización `0x436f2d10`; destino `obj+0x3d4`.
- `SetExposure` IMX210: `0x436d6f6c`; `param+9` en `0x436d6fb6`; despacho `0x436d70be`; modo 0 `0x436d70d0`;
  temporización `0x436d6f50`; destino `obj+0x3a0`.
- Método `+0x30`: A7S `0x436f4a94`, conversión `0x436f5df0`, rama `0x436f4b10`, flag `obj+0x3d7`;
  A6000 `0x436d7e08`, conversión `0x436d8a90`, rama `0x436d7e9a`, flag `obj+0x3a3`.
- Armado A7S: `0x436f43c0` (estado 2) / `0x436f43f0` (estado 1); recurso `0x43b73044(0xe)`; lectura del estado en
  `0x436f521c` y empaquetado en `0x436f5268`.
- Límite: `E ≤ VTS × 15,2 µs ≈ 64,9 ms`; `r5` útil `≈ 0..4219` (T046). Para `E > 65 ms` no hay valor de `r5`
  representable en la ruta actual.
- Rápidas: `E = (VTS − r5) × 15,2 µs`; 1/8000 ≈ 8,2 líneas; resolución 15,2 µs.

## 7. Resultados de emulación

No se ejecutó Unicorn en esta sesión para las funciones nuevas: la verificación se hizo contra **bytes e
instrucciones** (LLVM/objdump), que es la prioridad 1 de §9. La emulación de `0x4382fac8` de E25-11 sigue siendo la
base del código Tv (`1e6·2^((4096−x)/256) µs`), pero **no** se usa para afirmar el comportamiento del sensor.
No se presenta ningún resultado de emulación como comportamiento real del sensor.

## 8. Capacidades reutilizables

- El contrato `param+0/4/6/9` de `SetExposure` es común: se puede seguir usando `ShutMode 0` + `param+0` para una
  exposición uniforme de hasta un cuadro.
- El método `+0x30` ya está conectado en la foto de la A6000 (`0x438c831e`): la velocidad real llega al imager. Es
  el punto natural para una prueba de datos (sin sobrescribir instrucciones) si se puede variar su bloque
  `cap+0x6bc`.
- La tabla de tiempos por modo es común (30 filas idénticas): una calibración de línea/tiempo vale para ambos.

## 9. Capacidades ausentes o no demostradas

- No hay contador de cuadros ni acumulador en `SetExposure` ni en `+0x30`.
- No hay una ruta de exposición uniforme > 1 cuadro demostrada en el IMX210.
- El armado de exposición larga del A7S (`r3` + `0x3dc`) **no tiene equivalente en el método `+0x30` del A6000**.
- No se demostró que el flag `0x3d7/0x3a3` cambie la secuencia física de reset/lectura.
- No se demostró que la rama `>0x1000` sea un temporizador multicuadro; su semántica exacta queda abierta.

## 10. Veredictos

| # | Pregunta | Respuesta | Referencia y alcance |
|---|---|---|---|
| A | ¿Se reconstruyó la cadena de cálculo de exposición Silent del IMX235? | **SÍ** | `0x438b7728` → `0x436f2938`/`0x436f2988` → `0x436f4168`/`0x436f4a94`; alcanza el bloque de comandos, no los registros físicos (V) |
| B | ¿Está demostrado un tratamiento especial de exposiciones Silent > 1 cuadro? | **NO** | hay una máquina de armado (`0x436f43c0`) pero su efecto no está demostrado; no hay contador (V/N) |
| C | ¿Se identificó cómo se representa una exposición > 65 ms? | **NO** | el clamp de `0x436f5df0`/`0x436d8a90` satura en un cuadro; no hay campo mayor (V/I) |
| D | ¿Se identificó el mecanismo que controla el final de integración sin cortina? | **NO** (parcial) | el final es la lectura de la fila; el bloque `+0x60..+0x66` transporta el tiempo, pero no se siguió hasta el registro físico (V/N) |
| E | ¿El IMX235 dispone de temporización más fina que una línea? | **NO** | todas las rutas usan líneas enteras de 15,2 µs; no hay corrección fraccionaria (V en las funciones analizadas) |
| F | ¿Existe una primitiva equivalente verificable en el IMX210? | **PARCIAL** | `SetExposure`, tablas y `+0x30` idénticos; falta el armado `r3`/`0x3dc` (V) |
| G | ¿Se encontró una configuración compatible del IMX210 para exposición uniforme > 65 ms? | **NO** | no hay valor de `r5` ni rama que lo produzca (V/N) |
| H | ¿Está demostrado que el IMX210 pueda ejecutar dicha configuración? | **NO** | ausencia de evidencia, no imposibilidad física (N) |
| I | ¿Se encontró una ruta para tiempos variables sin sobrescribir instrucciones ejecutables? | **NO** | el método `+0x30` recibe el tiempo, pero no hay API/selector demostrado para variarlo sin parche (N) |
| J | ¿Existe una explicación reproducible del sesgo de T050? | **NO** (parcial) | la cuantización no basta salvo en 1/8000; la calibración por tanda sigue siendo la hipótesis (I) |
| K | ¿Hay base estática para diseñar una nueva prueba reversible? | **SÍ** | forzar solo `param+9=0` y dejar que `+0x30` calcule el tiempo; medir 1/8000–1/8 (V/I) |
| L | ¿Hay base para proponer una modificación permanente? | **NO** | E24-04/E25-04: recuperación independiente no demostrada (V) |
| M | ¿Se puede afirmar 1/8000–30 s totalmente electrónicos? | **NO** | el límite de un cuadro y la falta de armado en IMX210 lo impiden (V/N) |

Un **NO** por ausencia de evidencia no equivale a imposibilidad física.

## 11. Recomendación técnica para E25-12

1. **No perseguir `r5 > 4219`**: la ruta actual satura en un cuadro. El límite de 65 ms es del firmware, no solo
   del parche.
2. **Probar primero el camino que ya existe**: forzar únicamente `param+9=0` (2 bytes) y dejar que el método `+0x30`
   programe el tiempo desde la velocidad real. Medir 1/8000, 1/4000, 1/1000, 1/60, 1/8. Esto separa «ShutMode 0
   funciona» de «nuestro `r5` calculado a mano es correcto».
3. **Para > 65 ms**, no copiar registros del IMX235. El único candidato es el armado de exposición larga; hay que
   demostrar antes que el camino de bulb de la A6000 (`0x4381106c` / `0x43ae9380`) llega al sensor con `ShutMode 0`.
   Si no llega, la alternativa honesta es el obturador mecánico o la suma de varias tomas silenciosas en post.
4. **Calibración**: luz controlada y varias referencias por tanda; evitar la carrera de T050 (leer la velocidad
   estabilizada). El sesgo de ±20–25 % no se corrige con la fórmula de líneas.
5. **Recuperabilidad**: cualquier prueba debe seguir siendo de RAM, con guardián y reversión verificada; no se
   propone modificación persistente de BIONZ (E24-04, E25-04).

## 12. Experimento futuro mínimo (no ejecutado)

**Objetivo:** decidir si el IMX210 puede mantener una integración uniforme > 65 ms con código existente.

1. **Solo lectura, offline/depurador**: tras un disparo a 1/8 s en M, leer `cap+0x6bc` (bloque `+0x30`), `obj+0x3a3`
   (flag) y `obj+0x3a0` (contador de `SetExposure`). Si `+0x3a3=0` y el bloque está en el clamp, la ruta satura.
2. **Prueba reversible en RAM (si el usuario la autoriza)**: forzar solo `param+9=0` en `SetExposure` (sin tocar
   `r5`) y disparar 1/8000, 1/1000, 1/60, 1/8, 1/2. Criterios: uniformidad por filas ±5 %, exposición absoluta
   frente a referencia de la misma tanda, y reversión verificada.
3. **Si 1/8 sale uniforme**, el mecanismo existe y solo faltaba el ShutMode; si sale saturado, el límite es el
   cuadro y hay que buscar el armado de bulb o usar el obturador mecánico.

No se ejecutó nada de esto en E25-14.
