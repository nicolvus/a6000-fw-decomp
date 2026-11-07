# E26-R76 — Calibración propia de la pérdida EFCS (borrador, 07-11-2026, solo estático)

Pregunta: ¿cómo compensamos nosotros, con software propio, la pérdida del EFCS (≈1,25 ms con B−A ≤ 0, decreciente hasta ≈0 con B−A ≈ +4,6 ms)? Base: R74 §4/§6, R66, R68, R61, R64, R56 §7, R54 y `custom-fw-recovery-and-install.md`. No se tocó la cámara ni ningún archivo versionado.

Etiquetas: **VERIFICADO** (bytes/emulación) · **MODELO** (usa la curva de R74 §4) · **INFERENCIA** · **NO VERIFICADO** (solo en cámara).
Código y pruebas (sin cámara) en `scratchpad/calibracion/`:
`e26_r76_parche_darwin_tabla.py selftest` y `e26_r76_calibrar_efcs.py selftest` (ambos pasan; ver §6).

## 0. Lo que hay que compensar, en una línea

Darwin hace `S+0x48 = T − G42` (G42 = 3407 µs) y con él calcula `B − A` (corta: `T−3401`; larga: `T−3428`; intermedia −150…+50 µs de `S+0x48`, es decir T′ ∈ [3257, 3457] µs, va a `0x20544`). La exposición real es `T′ − δ(B−A)`, con δ ≈ 1,25 ms para B−A ≤ +0,6 ms y → 0 hacia +4,6 ms. **Como δ depende de B−A y B−A depende de lo que compensemos, la corrección correcta es un punto fijo, `c(T) = δ(B−A(T + c))`, no una constante.** Una constante sobrecompensa donde δ ya decae (modelo, EFCS activado, sin parche → con G42−1250):

| Velocidad | T µs | Sin compensar | G42 −1250 | B86 +1250 (satura) | Tabla c(T) |
|---|---|---|---|---|---|
| 1/4000 | 250 | −990 (negro) | −4 % | −4 % | c = 1261 |
| 1/1000 | 1000 | −240 (negro) | −6 % | −6 % | 1313 |
| 1/500 | 2000 | 680 | −2 % | −2 % | 1216 |
| 1/320 | 3125 | 1827 | +2 % | **−33 %** | 1206 |
| 1/250 | 4000 | 2710 | +7 % | **−32 %** | 1031 |
| 1/160 | 6250 | 5573 | **+15 %** | −11 % | 525 |
| 1/125 | 8000 | 7830 | **+14 %** | −2 % | 169 |

(MODELO; coincide con R68 §1.3 y R74 §6.2: B86 solo cubre T < 2,13 ms; G42 sobreexpone ≈ +0,25 EV a 1/125.) Todo depende de que δ siga a B−A (INFERENCIA de R74). Por eso el plan mide y cierra el lazo (§3).

## 1. Inventario de vías

Resumen (ordenadas por beneficio/riesgo en §5).

### (a) Propiedades NVRAM `0x1850000` (G) y `0x1850001` (B)

* **Qué cambia (VERIFICADO el código, INFERENCIA fuerte el flujo NVRAM→Darwin, R68 §2):** el BIONZ copia cada propiedad `0x185xxxx` al bloque de RAM de Darwin al arrancar; G (128 B) → `0x20000480`, B (384 B) → `0x20000300`. Valores actuales (R66 §2): G+0x40 = −435 (s16), **G+0x42 = 3407 (u16)**; B+0x84/86/88/8a = 6/6/−22/−21 (s16), B+0xc6..c8 = 29/37/35 (s8). Unidades: µs.
* **Opciones y a qué velocidades llegan (MODELO, tabla de §0):**
  * `B+0x86` +1250 (s16, 6→1256): adelanta A solo en la rama corta. Cubre T ≤ 2,13 ms (1/500 y más rápido, **incluye 1/1000**); satura (retardo de A = 1 µs) entre 2,13 y 3,26 ms: −33 % a 1/320. No toca 1/250 ni más lentas. Solo lo lee `0x18d6e` → efecto lateral mínimo. Es la propuesta de R74 §6.2.
  * `G+0x42` −1250 (3407→2157): desplaza todas las ramas EFCS; cubre todo, pero sobreexpone +0,1/+0,25 EV de 1/250 a 1/125 y mueve los umbrales de rama (T′ en la ventana intermedia cae en 1/450±): hay 5 lectores de G+0x42 (`0x182d8`, `0x18398`, `0x18a30`, `0x18daa`, `0x18fbc`), uno en `0x182d8` alarga 1,25 ms sus plazos (R70 §4).
  * **Nueva: tabla por T en G+0x44…0x7f** (60 B, hoy ceros en los 28 volcados), usada por el parche (c). Con NVRAM sola no hace nada.
* **Herramientas existentes:** `scripts/e26_r61/bk4_variante.py ENTRADA SALIDA ID OFFSET DELTA` (un s16 con checksum recalculado; sirve para G+0x42 y B+0x86: `… 0x1850000 0x42 -1250`; `… 0x1850001 0x86 1250`); `scripts/senser_backup_dump.py` (copia previa), `scripts/senser_backup_restore.py FILE SHA256` (escribe, verifica por relectura y sincroniza a flash, por modo servicio PMCA). Mi `e26_r76_calibrar_efcs.py nvram` genera el volcado con la tabla (escribe 60 B en G+0x44, aborta si no están a cero).
* **Riesgo:** bajo-medio. Es el mismo camino que ya recuperó la cámara el 20-10 (`nvram-referencia-20261020-214913`, probado en hardware). Límites: (1) **ninguna prueba ha comprobado todavía que editar `0x185000x` cambia Darwin** (R66 §1: «ningún experimento de NVRAM tocó Darwin»); la primera variante es esa prueba. (2) Restaurar el volcado completo reescribe toda la NVRAM; usar siempre el dump hecho justo antes. (3) Restaurar es modo servicio + reinicio: cada iteración cuesta minutos.
* **Reversibilidad:** total, restaurando el volcado previo (no requiere firmware).

### (b) Escritura en RAM de Darwin en vivo (estilo `camera_silent.py`)

* `camera_silent.py` escribe por telnet en `/dev/mem` **RAM del BIONZ** (`0x836D6FB6`, `0x836D7000`: ShutMode y `r5` del modo electrónico), con guardián de reversión a 25 s en la cámara. **No llega a Darwin**: Darwin es otro procesador y sus bloques se escriben solo por el enlace BIONZ→Darwin (tabla `0x2a124/0x2a160`, validador `0x1b53e`, comandos `AdjCmd/RAM Write`, R58 §13, R67).
* No existe en el repo ninguna herramienta que genere esa escritura, y no se ha localizado un disparador desde el espacio de usuario. Lo que sí se puede hacer en vivo es cambiar la **imagen BIONZ** de la propiedad (R66 §1: tabla `0x43fe8c38`, manejador `0x436bc514`), pero sin un disparador que la reenvíe a Darwin no sirve.
* **Veredicto:** NO VERIFICADO e inviable hoy. Habría que (i) hallar el emisor `RAM Write` del BIONZ (REA sobre `av-cam.bin`: xrefs a `0x436bc514`/`FUN_435614ec`), y (ii) invocarlo (requiere código propio en el BIONZ → vía (d)/(e)). Riesgo: medio (Darwin gobierna los imanes). Reversibilidad: reinicio. Valor: permitiría iterar sin reiniciar; no es necesario si la tabla (c) vive en NVRAM.
* Alternativa en vivo que sí funciona (no corrige EFCS): el modo electrónico (ShutMode 0 + `r5`, R56 §7), que ya calibra N = T/16,73 µs − 97 por RAM.

### (c) Parche de `darwin_core.bin` con tabla de compensación por velocidad (recomendado)

* **Qué cambia:** `0x18d7c`: `bl 0x18a2e` → `bl CAVE` (4 B). El cave llama a `0x18a2e`, y **solo con EFCS activado** (`S+0x31` bit 1, `S+0x60` bit 1 = 0) suma `c(T)` (s16 µs) al resultado, con `c` leído de la tabla en RAM de Darwin `G+0x44` (`0x200004c4`): pares `{u16 Tmax µs, s16 c}`, terminada en `Tmax = 0`, hasta 14 entradas. EFCS desactivado y el resto de llamadas a `0x18a2e` (`0x18c9a`, `0x18cc6`, fase previa) no se tocan. Detalle en §4.
* **Qué corrige:** todas las velocidades de 1/4000 a ≈1/100 (T hasta 9,8 ms) con un c distinto por tramo; evita la saturación de B+0x86 (R68 §1.3) y la sobreexposición de G42. Error modelado ≤ 1,7 % (la prueba exige < 3,5 %) en las 17 velocidades de 1/3 de paso de 244 µs a 9,8 ms; sin tabla (ceros) el parche es **neutro** (probado por emulación con la imagen original).
* **Efectos laterales:** (1) los T′ = T+c que caen en 3257…3457 µs (rama `0x20544`, esperas activas, **no modelada**) se evitan con un margen de 40 µs: el generador desplaza `c` para que ningún 1/3 de paso caiga allí (1/500 queda con −34 µs). (2) La tabla vive en G+0x44…0x7f: verificar que ningún lector de G use offsets ≥ 0x44 (hoy son ceros, así que un lector así vería 0). (3) Con la tabla vacía no cambia nada.
* **Riesgo:** medio-alto en el empaquetado, no en la lógica: no hay un hueco contiguo ≥ 56 B en el código (§4.4). Hay que instalar un firmware propio (3.39) y la recuperación depende de `nflasha1` (`custom-fw-recovery-and-install.md`: reflash con versión distinta; 3.37 oficial reinstalable; el 3.30–3.38 ya se instalaron sin NG).
* **Reversibilidad:** reinstalar 3.37 (versión distinta) con `pmca-console firmware`; mientras tanto la tabla puede quedar a ceros (neutro).
* **Herramientas:** `scripts/e25_24/patch_darwin.py`, `scripts/e25_27/build.py` (constructor con comprobación de cuevas y reversión), `scripts/e26_r56`, `analysis/e25-27/artifacts-338/` (3.38 = base actual); mi generador `e26_r76_parche_darwin_tabla.py` (`parchear`, `emular_18d6e`).

### (d) Parche o ajuste del planificador EFCS del BIONZ

* R74 §2: con `0x30097+0x15 = 0` el plan (`record+0x64 = record+0x1c`, `0x438417c6`) **no depende de T**; hoy no hay nada en el BIONZ que se pueda escalar con T. Dos variantes:
  * **NVRAM:** `0x30097+0x15 = 1` entra en `0x4383fa40` (`max([rec+0x1c]+sb, VTS)`), el camino de nuestros parches electrónicos. NO VERIFICADO que con EFCS dé una línea de reinicio dependiente de T; si lo diera, la corrección sería en filas (1,25 ms ≈ 75 líneas de 16,73 µs, R56 §7), con la ventaja de poder corregir el **gradiente vertical** (0,5 ms) que Darwin no ve. Reversible por NVRAM; pero 13 lectores de `+0x15` y la fase de `sb` (R58 §12) sin evaluar.
  * **Firmware BIONZ** (cueva como R54): reinicio `sl` adelantado `c(T)/16,73` líneas. Mayor superficie: `av-cam.bin` entero y TPZL de `nflasha3`; un error deja la cámara sin arrancar; recuperación por actualizador solo si `nflasha1` está intacto (NO VERIFICADO en hardware, §3 del doc de recuperación).
* **Veredicto:** solo si (c) deja gradiente residual. Riesgo alto, beneficio incierto; no se recomienda antes de medir.

### (e) App propia en la cámara

* La app RemoteShutter (v8c) ya gobierna `/ss`, `/shoot`, `/iso`, `/fmt`, y aplica el parche electrónico solo con EFCS desactivado. No puede escribir en Darwin ni en `/dev/mem` sin telnet (R51 §6, `Runtime.exec` colgó entre dos escrituras en T049).
* Útil como **disparador de la calibración** (ya lo es) y para guardar la tabla de medidas; **no** como vía de compensación del EFCS. Riesgo: bajo; reversible; sin valor de corrección.

## 2. Ordenación por beneficio/riesgo

| # | Vía | Beneficio | Riesgo | Coste de iteración | Estado |
|---|---|---|---|---|---|
| 1 | (a) `B+0x86` +1250 o tabla en G (con medidas) | alto en ≤ 1/500, **verifica la premisa NVRAM→Darwin** | bajo | restaurar NVRAM (minutos) | listo (script), sin autorización |
| 2 | (c) parche con tabla en G+0x44 | **completo** (1/4000…1/100) | medio (empaquetado) | solo NVRAM tras instalar | diseñado y emulado; falta hueco de código |
| 3 | (a) `G+0x42` −1250 | todas las ramas, sobreexpone +14 % a 1/125 | bajo | NVRAM | listo; peor que (c) |
| 4 | (d) NVRAM `0x30097+0x15` | incierto (gradiente) | medio | NVRAM | NO VERIFICADO |
| 5 | (b) RAM en vivo Darwin | iteración rápida | medio | — | inviable hoy |
| 6 | (d) firmware BIONZ | incierto | alto | reflash | no recomendada |
| 7 | (e) app | ninguno para EFCS | bajo | — | solo disparador |

## 3. Propuesta: flujo automático de calibración (dos pases + verificación)

Herramientas ya existentes: `scripts/camera_raw_exposure.py` (RAW por ADB: `/fmt?v=rawjpeg`, `/iso?v=`, `/ss?n=&d=`, `/shoot`; devuelve `report.json` con `mean_lin` y `octavos` por disparo; restaura jpeg/ISO automático al terminar) y `scripts/camera_suite.py` (JPG, métricas por franjas). Nuevo: `e26_r76_calibrar_efcs.py` (sin cámara; reproduce el flujo con una cámara sintética).

0. **Preparación (autorización del usuario + cámara):** luz continua estable y uniforme (LED sin PWM visible o lámpara incandescente), cámara fija, ISO fijo alto (p. ej. 3200–6400) para que 1/1000–1/4000 sin compensar den señal medible en la referencia. Copia previa: `senser_backup_dump.py OUT` y comprobar el SHA-256 contra el volcado de referencia.
1. **Pase 0 (medición base):** `camera_raw_exposure.py OUT_off --iso N --reps 3 1/4000 1/2500 … 1/100` con **EFCS desactivado** (3.37 oficial = obturador mecánico completo, R57 §5); luego, tras activar EFCS en el menú, `… OUT_on0`. (El conmutador de EFCS es de menú; el espejo `0x83EDF894` solo se ha forzado por RAM en pruebas, no hay un comando remoto.) Orden intercalado y 3 repeticiones por velocidad para absorber deriva de la luz; descartar `sat_pct > 0,5 %`.
2. **Ajuste (sin cámara):** `e26_r76_calibrar_efcs.py ajustar OUT_on0/report.json OUT_off/report.json --out tabla1.json`:
   * razón `r = L_on / L_off` (mediana de repeticiones, luminancia lineal sin negro; el RAW evita la curva gamma del JPEG);
   * pérdida `δ = T − r·T` en función de `x = B−A` (puntos con `r < 0,04` están censurados: negro = cota inferior; ahí se extrapola plano, hipótesis R74 «δ constante con B≤A»);
   * punto fijo `c(T)`, ventana intermedia evitada, agrupación en ≤ 14 tramos `{Tmax, c}` (tolerancia relativa 3 %).
   * Para la vía (a) simple: el mismo script da `c` único; `B+0x86 = 6 + c` solo si todos los T medidos < 2,1 ms.
3. **Escritura (autorización + cámara):** vía (a): `senser_backup_dump.py`, `bk4_variante.py` o `e26_r76_calibrar_efcs.py nvram DUMP SALIDA tabla1.json`, `senser_backup_restore.py SALIDA SHA256`, reinicio. Vía (c): primero instalar el firmware con el parche (tabla a ceros = neutro) y comprobar que EFCS off y on se comportan como antes; luego escribir la tabla por NVRAM.
4. **Pase 1 (verificación y refinado):** repetir el barrido EFCS activado (`OUT_on1`) → `ajustar OUT_on1 OUT_off --previo tabla1.json --previo-on OUT_on0 --out tabla2.json`. Cada pase añade puntos `(x′, δ′)` al ajuste (en `x′ = x(T+c)` la pérdida observada es `T + c − r·T`), así la curva se afina donde de verdad se trabaja. En la simulación con una unidad un 8 % peor que el modelo: error máx. de exposición 5,3 % tras el pase 1 y 4,5 % tras el 2 (el límite lo pone la agrupación en tramos y el ruido del 0,4 %).
5. **Criterio de cierre:** 1/4000…1/250 con `r ∈ [0,95; 1,05]`, gradiente por octavos |V| < 5 % (en `octavos`; la cortina real puede dejar ≈ 0,5 ms de gradiente que ninguna vía Darwin corrige) y foto de prueba a 1/1000 con exposición correcta. Repetir con batería baja/caliente: R74 §6.2 advierte que si el transitorio cambia con temperatura o batería la tabla se desplaza (validar a ±5 °C).
6. **Reversión:** `senser_backup_restore.py` con el volcado del paso 0 (probado el 20-10) o, en (c), reinstalar 3.37.

Límites: el modelo supone δ función solo de B−A; si no lo es (por ejemplo depende de T en absoluto), el pase 1 lo mostrará como residuo y la tabla por velocidad lo absorbe igualmente (es empírica por tramos). No corrige el gradiente.

## 4. Parche (c) a nivel de instrucciones

### 4.1 Gancho y datos
* Original (`darwin_core.bin` 3.21, base `0x4200`): `0x18d7c: bl 0x18a2e` seguido de `str r0,[r7,#0x48]` (`0x18d80`). `0x18a2e` (VERIFICADO, Capstone): con `S+0x31` bit 1 (EFCS) y `S+0x60` bit 1 = 0 hace `r0 −= u16[G+0x42]`; sin EFCS suma `s16[G+0x40]`.
* Nuevo: `0x18d7c: bl CAVE`. `S = 0x200036d8`, `G = 0x20000480`, tabla `0x200004c4` (= G+0x44, 15 palabras: 14 entradas + terminador).

### 4.2 Cave (56 B, ensamblado con Keystone y verificado con Capstone/Unicorn)
```
CAVE: push {r4, lr}
      mov  r4, r0               ; T (µs)
      bl   0x18a2e              ; r0 = T − G42 (EFCS) / T + G40
      ldr  r1, S_               ; 0x200036d8
      ldrb r2, [r1, #0x31]
      lsls r2, r2, #30          ; bit 1 → N
      bpl  done                 ; EFCS desactivado: no tocar
      ldrb r2, [r1, #0x60]
      lsls r2, r2, #30
      bmi  done                 ; compuerta S+0x60: Sony ya anula la resta
      ldr  r1, T_               ; 0x200004c4
loop: ldrh r2, [r1], #4         ; Tmax
      cbz  r2, done             ; terminador: sin entrada → c = 0
      cmp  r4, r2
      bhi  loop                 ; T > Tmax: siguiente tramo
      ldrsh r2, [r1, #-2]       ; c del tramo
      add  r0, r0, r2           ; S+0x48 += c  (equivale a G42 efectivo = 3407 − c)
done: pop  {r4, pc}
S_: .word 0x200036d8
T_: .word 0x200004c4
```
Registros: solo r0–r2 y r4 (guardado); `bl 0x18a2e` puede ser llamado desde el cave porque `lr` está guardado. La suma ocurre antes del `str r0,[r7,#0x48]` y de la lógica del `S+0x94` (que sigue pudiendo anular `S+0x48`).

### 4.3 Tabla actual del modelo R74 (c en µs, T=Tv de 1/3 de paso emulado con `0x19a12`)
`(Tmax, c)`: (347, 1264) (551, 1287) (1752, 1310) (2205, 1263) (3504, 1252) (4411, 1050) (5560, 825) (7008, 535) (9834, 169); T mayor: sin compensación. Se recalcula con las medidas reales (paso 2 de §3).

### 4.4 Espacio libre (el punto débil)
* No hay huecos de código a cero ≥ 56 B: solo `0x4316..0x4327` (18 B) en la tabla de vectores, que el 3.30–3.38 ya usa (cave de la compuerta, 14 B + literal en `0x4330`); las demás series de ceros (`0x25c5c…0x28100`) son datos (estructuras de 60 B con relleno, punteros que apuntan dentro) y no son seguras.
* Un barrido de «funciones sin llamadores» (Capstone, 45 candidatas, p. ej. `0x251a8` 210 B, `0x13f40` 394 B) **no basta**: una de las candidatas, `0x19fca`, resultó ser una rutina de inicialización con código contiguo distinto; hay que confirmar con REA/Ghidra (xrefs indirectas) antes de pisar nada.
* Opciones, de más a menos recomendable: (1) **anexar el cave tras `0x2a85c`** (`parchear(img, cave=0x2a860)`, 60 B; es lo que prueba el selftest) — requiere que el cargador y `build.py` admitan +60 B en `darwin_core.bin` (tamaño en `darwin.integrated.sum`, `nflasha3` TPZL): NO VERIFICADO, comprobable offline con `e25_27/build.py`; (2) sustituir una función muerta confirmada; (3) reducir el cave a ≤ 18 B moviendo la tabla/lógica a Darwin RAM (código en SRAM desde NVRAM), descartado por riesgo.

## 5. Recomendación

1. **Paso 1 (barato, informativo):** vía (a) con la prueba más simple, para validar la premisa «NVRAM `0x185000x` → Darwin». Variante mínima: `B+0x86` +1250 (R74 §6.2) o, mejor, `G+0x42` desde la tabla medida; volcar antes; fotos a 1/1000 y 1/2000 con EFCS activado: si dejan de ser negras, la premisa queda confirmada y se mide `δ(x)` real.
2. **Paso 2 (solución completa):** vía (c): construir 3.39 = 3.38 + gancho + cave anexado (o hueco confirmado) con tabla a ceros; instalar; comprobar neutralidad; escribir la tabla por NVRAM con el flujo de §3 en 2 pases.
3. No tocar BIONZ ni intentar escritura en vivo en Darwin salvo que (c) deje un gradiente inaceptable.
4. Advertencia de fondo (R74): si la causa es física (transitorio ligado al evento A), la compensación es un parche de síntoma que se mueve con temperatura/batería; seguir con E26-R74-FISICO (sonda USB, flex CN4900) en paralelo.

## 6. Pruebas ejecutadas (sin cámara)

* `e26_r76_parche_darwin_tabla.py selftest` (Capstone+Keystone+Unicorn sobre `darwin_core.bin` 3.21): el binario parcheado solo difiere en los 4 B del gancho + 60 B anexados; con tabla vacía las esperas emuladas de `0x18d6e` son **idénticas** a las originales en las 17 velocidades; EFCS desactivado no cambia; con tabla, B−A y exposición modelada por velocidad (emulación completa de `0x18d6e` con las llamadas externas sustituidas; rama larga: `r8`; corta: `r0` en `0x198ee`):

| T µs | B−A original | E modelada (orig) | B−A nuevo | c | E modelada (nueva) |
|---|---|---|---|---|---|
| 9834 | 6406 | 9670 | 6575 | 169 | 9839 |
| 6204 | 2776 | 5514 | 3311 | 535 | 6204 |
| 3906 | 478 | 2615 | 1528 | 1050 | 3906 |
| 2458 | −943 | 1149 | 282 | 1252 | 2417 |
| 1953 | −1448 | 639 | −185 | 1263 | 1919 |
| 976 | −2425 | −264 | −1115 | 1310 | 973 |
| 244 | −3157 | −996 | −1893 | 1264 | 247 |

  Ninguna velocidad cae en la rama intermedia; error relativo máximo 1,7 %.
* `e26_r76_calibrar_efcs.py selftest`: cámara sintética (unidad 8 % peor que el modelo, ruido 0,4 %): 1/1000 negro antes, ninguna negra tras el pase 1, error 5,3 % → 4,5 %; genera además un volcado NVRAM de prueba sobre el último `backup_flash.bin` local (tabla en G+0x44, resto idéntico; **no se escribe en la cámara**).
* Dependencia: `keystone-engine` instalado solo en `scratchpad/kslib` (no se tocó `.venv`). Para llevarlo al repo bastaría precomputar los 56 B (o `pip install keystone-engine`).

## 7. Qué requiere autorización y cámara

| Paso | Necesita |
|---|---|
| Volcado NVRAM previo (`senser_backup_dump.py`, solo lectura, modo servicio) | cámara conectada; autorización por la regla de pruebas con cámara |
| Barridos RAW (`camera_raw_exposure.py`: `/ss`, `/shoot`, ADB pull) | cámara, luz, ISO fijo; no escribe RAM ni NVRAM |
| Escribir NVRAM (`senser_backup_restore.py`) y reiniciar | **autorización expresa del usuario** + copia previa verificada |
| Instalar el firmware 3.39 con parche Darwin | **autorización expresa** (flasheo) + `SHA256SUMS` + batería > 50 % |
| Confirmar espacio para el cave (REA/Ghidra, build offline) | solo estático, sin autorización |

## 8. Qué queda por verificar en cámara

1. Que editar `0x1850000/01` cambia el comportamiento de Darwin (premisa de (a) y (c)); hoy INFERENCIA fuerte.
2. Que δ siga a B−A al desplazar B−A con c (el punto fijo); si δ depende de T absoluto, la tabla empírica lo absorbe pero la curva R74 no sirve de semilla.
3. Que `0x20544` (rama intermedia) no se alcance en uso real (T no estándar, bracketing de 1/2 paso, variación de Tv).
4. Que el cargador de Darwin y el empaquetado admitan +60 B (o confirmar un hueco).
5. Estabilidad térmica/batería de la tabla (±5 °C, batería baja) y el gradiente vertical residual.
6. Que ningún lector de G use `G+0x44…0x7f`.


> **Verificación ([R76b](e26-r76b-verificacion-parche.md)):** usar `scripts/e26_r76/e26_r76_parche_darwin_tabla.py` — tabla en `G+0x48` (G+0x44..0x47 sí se leen), cave en la función muerta `0x13d5a`, tramos guarda que evitan la rama `0x20544`, compuerta `(S+0x31&3)≠0`.

> **Corrección ([R81](e26-r81-auditoria-opus-parche-efcs.md)):** el hueco `0x13d5a` pertenece a la función viva `0x13d58` (llamada desde `0x1516c`), y las alternativas de R80 §4 también están vivas. El parche está BLOQUEADO hasta encontrar otra ubicación.
