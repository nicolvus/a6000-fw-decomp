# T052-B0 — VTS, predicado de cuadro extra y viabilidad de C3

**Fecha:** 28-10-2026 · **Cámara:** ILCE-6000, fw **3.23** (Darwin B1a) · **BIONZ analizado:** `av-cam.bin` 3.21,
SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`
**Alcance:** análisis estático dirigido, emulación *offline* y lectura del volcado de reposo del 20-10-2026.
**No se conectó la cámara, no se escribió RAM/NVRAM/NAND, no se ejecutó firmware en hardware y no se ejecutó C3.**

Etiquetas: **V** = verificado por bytes/instrucciones, emulación o un volcado real; **I** = inferencia con
evidencia; **N** = no verificado. Un **N** por falta de medida no es una prueba de imposibilidad física.

---

## 0. Respuesta corta y decisión

**La pregunta final —¿podemos obtener un `r5` correcto y reproducible desde la velocidad, usando código nativo
de Sony, sin depender de un VTS supuesto ni del predicado?— tiene respuesta SÍ, pero solo por la vía C3-B.**

- **C3-A (usar directamente el `r5` de `0x4383fa40`) no es autorizable.** El predicado de cuadro extra está
  configurado a **0** en el bloque de NVRAM que BIONZ copia a RAM; con 0 el predicado devuelve 1 y la función
  suma un cuadro completo. El `r5` nativo sale 8422 / 8175 / 7341 para 1/4000, 1/250 y 1/60: mayor que el VTS,
  inválido. Además, el VTS de fotografía (`record+0x20`) sigue sin leerse.
- **C3-B (usar `record+0xf0`, el número de líneas, y la referencia medida 4219) es preferible y ya está
  respaldado por T046/T047.** `record+0xf0` se calcula antes del cuadro extra y no depende ni del VTS ni del
  predicado. La emulación con VTS 4219/4266/1000 y predicado 0/1 da **las mismas líneas** para cada Tv.
  `r5 = 4219 − líneas` reproduce T047 exactamente (4203 / 3956 / 3122).
- **La cámara no estuvo accesible**, así que **T052-B0 no se ejecutó físicamente**. No se leyó ningún registro
  de una foto. El recolector `scripts/t052_b0_readonly.py` queda listo, con modo offline separado.

**Decisión:** **B. C3-B es preferible y se demuestra por qué.** C3-A queda bloqueado por el predicado y por el
VTS no leído. El dato físico exacto que falta para cerrar B0 es la lectura de `record+0x20` (y del byte
`[0x43deb360+0x10]`) inmediatamente después de una foto normal; no es necesario para autorizar el diseño C3-B,
pero sí para confirmar el estado real y descartar un escritor externo.

---

## 1. Resumen ejecutivo

1. **VTS.** La cadena ya conocida se confirmó byte a byte: `record+0x20 ← cap+0x5e0 ← [descriptor+6]`
   (`0x43846d9c` carga el descriptor, `0x43846e08` lee `+6`, `0x43846e12` escribe `cap+0x5e0`). El contexto
   `ctx = 0x43eaadd8` se identificó por emulación de la cadena `0x437b4eb4 → 0x437b4df0 → 0x437b5b14 →
   0x43844e80`; su `+0x3c` apunta al descriptor de modo `0x43ea13dc`. En reposo, `[descriptor+6] = 0` y
   `record+0x20 = 0`. **El valor de fotografía no se pudo determinar estáticamente**: el descriptor es un objeto
   de modo en DRAM, no una constante, y no se localizó el escritor/selector de su `+6`.
2. **Predicado.** El objeto `0x43deb360` es el bloque 5 (ID `0xbc0005`) de un conjunto de diez bloques de
   parámetros de sensor de 0x100 B. El bloque completo está en el **Backup/NVRAM** en el offset `0x74218`; es
   **idéntico en los 12 backups** disponibles (3.21 y 3.22 (pre-B1a)) y su byte `+0x10` es **0**. El bloque de RAM
   `0x83deb360` es **byte a byte igual** al de NVRAM en sus 0x100 B. No se encontró ningún escritor directo de
   `+0x10` en `av-cam`: las 41 referencias al único slot GOT (`0x440253cc`) son lectoras en el análisis
   dirigido. **El predicado devuelve 1 y el cuadro extra está activo** en el estado configurado; la lectura
   física tras un disparo queda pendiente para descartar un escritor externo.
3. **Contador `record+0x68`.** `0x4383fd6c` copia 16 B de `record+0x64` a `cap+0x64c`; `+0x68` cae en
   `param+4`, que `SetExposure` lee como ventana (`0x436d6faa`), no como contador de cuadros. No se encontró
   ningún consumidor que acumule varios cuadros ni una secuencia de lectura multicuadro. La existencia del
   contador no demuestra integración electrónica multicuadro.
4. **Emulación.** Escenarios A/B/C/D/E (VTS 4219/4266/1000 × predicado 0/1): `record+0xf0` es constante para
   cada Tv; el `r5` nativo es válido solo con predicado 0 y VTS 4219; con el predicado observado (0) es inválido.
   C3-B reproduce T047 en las tres velocidades.
5. **Física.** La cámara no estaba accesible (PC en `192.168.0.13/24`, sin ruta a `192.168.1.29`, sin `adb`/
   `pmca`, sin dispositivo Sony por USB). No se repitieron barridos. Se preparó el protocolo y el recolector.
6. **Estado.** C3 no se autoriza. C3-B es el candidato para T052-B1, condicionado a la lectura física de B0 y a
   la autorización expresa del usuario. No se modificó firmware ni memoria de la cámara.

---

## 2. Evidencia de acceso o falta de acceso

Comprobación única del 28-10-2026, sin barridos extensos:

| Comprobación | Resultado |
|---|---|
| Interfaces | `wlan0 192.168.0.13/24`; `tailscale0`; `lo` |
| Rutas | `default via 192.168.0.1`; `192.168.0.0/24`; **no hay ruta a `192.168.1.0/24`** |
| `ping 192.168.1.29` | 1 paquete, 100 % de pérdida |
| USB (`lsusb`) | hubs, Intel USB Bridge, Broadcom; **ningún dispositivo Sony** |
| `adb`, `pmca`, `pmca-console` | no instalados en el `PATH` |
| Extremo conectado | no se pudo confirmar que haya cámara; no se asumió la IP anterior |

No se modificó la red de terceros, no se instalaron servicios en la cámara y no se simuló ninguna lectura
física. **La cámara no estuvo accesible.**

---

## 3. Reconstrucción del descriptor VTS

### 3.1 Cadena verificada por bytes

```
settings+0x162 (Tv)  →  record+0xf6          (0x437b4662/0x437b4670; E25-16)
cap+0x5c8 (48 B)     →  record+8             (0x437b43b4; E25-16)
  record+0xc  = cap+0x5cc  (período Q8)
  record+0x1c = cap+0x5dc  (suelo)
  record+0x20 = cap+0x5e0  (VTS)
cap+0x5e0 ← [descriptor+6]                   (0x43846e00..12)
descriptor ← [ctx+0x3c]                      (0x43846d9c)
ctx = 0x43eaadd8                             (emulación de 0x437b4eb4)
descriptor = 0x43ea13dc
```

Bytes comprobados:

| Dirección | Bytes | Instrucción | Estado |
|---|---|---|---|
| `0x43846d9c` | `ea6b` | `ldr r2,[r5,#0x3c]` | **V** |
| `0x43846e00` | `b3f808e0` | `ldrh.w lr,[r3,#8]` | **V** |
| `0x43846e08` | `db88` | `ldrh r3,[r3,#6]` | **V** |
| `0x43846e12` | `a4f8e035` | `strh.w r3,[r4,#0x5e0]` | **V** |
| `0x4383fa66` | `268c` | el productor lee `record+0x20` | **V** |
| `0x4383fa46` | `c768` | el productor lee `record+0xc` | **V** |

### 3.2 Quién construye el contexto y el descriptor

La cadena de llamadas se siguió con emulación Unicorn y con bytes:

- `0x437b4eb4` es un *dispatcher* que alterna dos buffers de modo de `0xa70` B
  (`0x43eaaea0` y `0x43eab910`, byte de toggle en `0x43f9a549`).
- Llama a `0x437b4df0(ctx, buffer)` con `ctx = 0x43eaadd8` (capturado en emulación).
- `0x437b4df0` llama a `0x437b5b14(ctx, buffer)`.
- `0x437b5b14` llama a `0x43844e80(ctx, ..., descriptor, ...)`; el constructor lee `[ctx+0x3c]` y copia
  `descriptor+4/+6/+8/+0xa` a `cap+0x5da/+0x5e0/+0x5dc`.

El llamador de `0x437b4eb4` no se localizó como `BL` directo (probablemente es un puntero de estado o una
entrada de tabla); la cadena interna sí está verificada. Esto no cambia la conclusión: el descriptor es un
objeto de modo y su `+6` no es una constante.

El descriptor `0x43ea13dc` es un objeto de modo en DRAM, con cabecera
`01 04 00 00 … e7 2e 14 5f` y el campo `+6 = 0` en reposo. **No es una constante del binario**: no aparece
como literal ni se construye con un `movw`; el constructor lo consume, no lo rellena.

**Lo que no se pudo cerrar:** el escritor/selector de `[descriptor+6]` para fotografía. El objeto se referencia
desde varias tablas de componentes en DRAM (`0x43e8d920`, `0x43e993e0`, `0x43eaae14`, …), pero ninguna
referencia estática conduce a un `strh … [#6]` sobre ese objeto. La tabla de componentes `0x43e9939c+8` es
inicializada por código que no se localizó con el análisis dirigido; no se intentó una auditoría general del
sensor (fuera del alcance de T052-B0).

### 3.3 4219 frente a 4266

| Valor | Origen | Estado |
|---|---|---|
| **4219** | referencia efectiva medida en T046/T047: `E = (4219 − r5) · 15,2 µs`; cuadro completo ≈ 64,1 ms | **V físico** (T046/T047) |
| **4266** | `0x4385de94(600, 1, 0)`: `0x271000 / 600 = 4266`; es la función de la vista en directo | **V** de la función; **no** es el VTS de la foto |
| **0** | `[descriptor+6]` en reposo | **V** del volcado; **no** es el VTS de una foto |

La diferencia de 47 líneas (4266 − 4219 = 47; 47 × 15,2 µs = 0,714 ms) es coherente con un margen de
blanking/integración, pero **no está demostrada**. No se elige 4219 por proximidad: se elige porque es la ley
medida en T046/T047 y la que C3-B reutiliza.

### 3.4 Respuesta a la pregunta principal de B0-1

**¿Se puede determinar estáticamente el VTS de la ruta fotográfica concreta, sin depender de una lectura de
RAM?** **NO.** El campo `record+0x20` procede de un descriptor de modo en DRAM cuyo `+6` es 0 en reposo y cuyo
escritor/selector de foto no se localizó. La condición exacta que falta es: **valor de `[descriptor+6]` (o de
`record+0x20`) durante una foto normal**. La prueba C3-B no necesita ese valor; la prueba C3-A sí.

---

## 4. Escritores y consumidores del predicado de cuadro extra

### 4.1 El objeto es un bloque de parámetros de sensor, no un flag suelto

`0x43deb360` es el bloque 5 de un conjunto de diez bloques de 0x100 B enviados al servicio de imager con IDs
`0xbc0001 … 0xbc0010` (tabla de punteros `0x43fea1e4`, tabla de IDs `0x43fea210`, emisor `0x436d9df8`).
El bloque 5 tiene ID `0xbc0005`.

**Evidencia de que es una copia de NVRAM/Backup:**

| Comprobación | Resultado | Estado |
|---|---|---|
| Bloque de 0x100 B en `backup_mem.bin` | offset `0x74218`; SHA-256 `2a42df46c7f38bf4…e57ae370` | **V** |
| Byte `+0x10` en NVRAM | `0` en los 12 backups (3.21 y 3.22, pre-B1a) | **V** |
| Bloque de RAM `0x83deb360` | idéntico a NVRAM en los 0x100 B | **V** |
| Byte `+0x10` en RAM de reposo | `0` | **V** |
| Escritores de `+0x10` en `av-cam` | no se encontró ninguno directo; 41 referencias al slot GOT `0x440253cc`, todas lectoras | **V** estático |

No hay un backup NVRAM **posterior** a B1a: el último es `20261027-T040-pre-B1a` (3.22). B1a es un parche de
Darwin (tipo 0 + B1a) y no reescribe el bloque de BIONZ; el bloque de RAM del 20-10 (3.21) es idéntico al de
NVRAM, lo que apoya que la copia se mantiene. La confirmación definitiva sigue siendo la lectura física de B0.

Los dos únicos `str … [#0x10]` que aparecen en ventanas de 0x80 B alrededor de las referencias
(`0x43a12ac4`, `0x43a12d12`) pertenecen a otras funciones (`0x43a12a84`, `0x43a12d9c`) y usan otras bases
(`r4`, `r2`), no el puntero cargado desde `GOT+0x64e8`. **No son escritores del predicado.**

### 4.2 Semántica: selector de modo de captura

La decompilación de Ghidra simplifica la función a `byte == 1`; **los bytes y la emulación demuestran que
devuelve 1 para 0 o 1 y 0 para ≥2** (`sub.w` / `rsbs` / `adc.w`). Se usa el comportamiento de bytes, no la
simplificación del decompilador.

`0x43a12ca8` tiene tres llamadores:

| Llamador | Efecto | Estado |
|---|---|---|
| `0x4383fa9a` (`0x4383fa40`) | si devuelve 1, `r8 += frame`; `r5 = 2·frame − líneas` | **V** emulación |
| `0x438c7416` (`0x438c73f8`) | elige `0x19` (predicado 1) frente a `0x11` (predicado 0) en los flags de la petición de captura | **V** bytes/decompilación |
| `0x43a1415a` (`0x43a14154`) | elige la tabla `0x4401ae4e` (predicado 1) frente a `0x4401ad6c` (predicado 0); la tabla se usa para seleccionar el modo de lectura por código | **V** bytes |

No es un flag de usuario ni un estado transitorio de “cuadro extra”: es un **selector de modo de captura** que
cambia a la vez el cálculo de `r5`, los flags de la petición y la tabla de modos. Con `+0x10 = 0`, el modo
seleccionado es el de **cuadro extra**.

### 4.3 ¿Cambia durante la fotografía?

- **Estático:** el bloque se copia de NVRAM y no se le encontró escritor directo en `av-cam`. El valor configurado es 0.
- **Físico:** no se leyó tras un disparo. La lectura de B0 debe confirmar que sigue siendo 0 y que no hay un
  escritor externo (otro proceso/servicio) que lo cambie a ≥2.
- **Conclusión:** **el cuadro extra está activo en el estado configurado**; no se puede demostrar
  estáticamente una transición a ≥2 antes de `0x4383fa40`. La única forma de demostrarlo es la lectura física.

### 4.4 Contador `record+0x68`

> **Corregido por [E25-17](e25-17-bulb-exposicion-electronica-larga.md):** `record+0x68` es el `svd` (cuadros enteros − 1): `SetExposure` lo escribe en los registros ID3/ID4 y es la misma celda (`cap+0x650`) que compara el contador de pasos del host. «Ventana» (`blk+0x50`) es la misma cifra; para exposiciones de un cuadro vale 0, por eso C3-B no lo necesita.

`0x4383fd6c` copia 16 B desde `record+0x64`:

```
0x4383fdaa  add.w r3,r0,#0x64
0x4383fdb0  ldm.w r3,{r0,r1,r2,r3}
0x4383fdb2  stm.w lr,{r0,r1,r2,r3}   ; -> cap+0x64c
```

`record+0x68` cae en `cap+0x650` (param+4). `SetExposure` lee `param+4` en `0x436d6faa` y lo escribe en
`blk+0x50` como ventana/anchura; **no lo usa como contador de cuadros**. No se encontró ningún consumidor que
acumule varios cuadros ni una secuencia de lectura multicuadro. El contador es un subproducto del cálculo del
modo de cuadro extra, no una prueba de integración electrónica multicuadro.

---

## 5. Lecturas físicas

**No se realizaron.** No hay cámara accesible. El volcado del 20-10-2026
(`analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin`, 1 GiB, cámara en marcha, reposo, fw 3.21)
se usó solo para el mapa y los valores de reposo; **no contiene una foto**. Los dos registros A/B están a cero.

Cuando la cámara vuelva a estar accesible, el procedimiento es:

1. Verificar los sitios de T050 (`0x836d6fb6 = 91f80990`, `0x836d7000 = 28125ffa85fe`) y los seis punteros GOT.
2. Modo M, ISO fijo, RAW+JPEG, escena fija, sin parche RAM.
3. Para 1/4000, 1/250 y 1/60: fijar la velocidad, disparar una foto normal y ejecutar
   `python3 scripts/t052_b0_readonly.py --confirm-readonly --host 192.168.1.29 --label <velocidad>`.
4. El recolector lee dos veces, en orden, los dos registros y los objetos, guarda los bytes y los valores
   decodificados en el PC y registra errores. No escribe en `/dev/mem` ni deja temporales en la cámara. Usa
   `dd if=/dev/mem bs=2 skip=físico/2 count=tamaño/2 | base64` para evitar el fallo de `bs=1` con direcciones
   >2³¹ observado en T026; todas las regiones son pares.
5. Criterios de parada: sitios/GOT distintos; VTS fuera de {4219, 4266}; período ≠ 3891; Tv incoherente;
   predicado ≥ 2 con r5 nativo fuera de rango; lectura inestable o incoherente entre bancos.

El protocolo completo se imprime con `python3 scripts/t052_b0_readonly.py --protocol`.

---

## 6. Verificación temporal de los registros

No se puede afirmar que un registro leído después de un disparo corresponda al instante de `SetExposure`. El
propio firmware limpia el registro (`memset(record,0,0x158)` en `0x437b43b4`) y lo reutiliza. Por eso:

- El protocolo exige **dos lecturas inmediatas** y comparar los hashes; si cambian, se documenta la transición.
- La lectura se hace **después** del disparo, sobre el registro que persiste hasta el siguiente `memset`; no se
  introduce ningún hook ni se modifica memoria para conservarlo.
- Si el registro ya fue limpiado (todo cero), el resultado se registra como **no válido** y se detiene la fase
  física; no se interpreta como una foto.
- La emulación no sustituye esta verificación temporal: solo demuestra la aritmética de la función.

---

## 7. Emulación de los escenarios

Se ejecutó la función **del firmware** `0x4383fa40` en Unicorn con un registro sintético
(`record+0xc = 3891`, `record+0x1c = 1`, `record+0xf6 = Tv`, `imager+0x4b8 = 1`) y el predicado
`0x43a12ca8` sustituido por 0/1. Evidencia: `analysis/t052-b0/emulacion.json`; script:
`scripts/t052_b0_emulate.py`.

### 7.1 Escenarios A/B/C/D/E

| Vel. | Líneas | A: VTS 4219, pred 0 | B: VTS 4266, pred 0 | C: VTS 4219, pred 1 | D: VTS 4266, pred 1 | C3-B: 4219 − líneas | T047 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1/4000 | 16 | 4203 | 4250 | **8422** | **8469** | **4203** | 4203 |
| 1/250 | 263 | 3956 | 4003 | **8175** | **8222** | **3956** | 3956 |
| 1/60 | 1097 | 3122 | 3169 | **7341** | **7388** | **3122** | 3122 |

- **A** reproduce T047; **B** se desvía 47 líneas (0,71 ms); **C/D** (predicado activo) dan `r5 > VTS` y son
  inválidos. **E** (VTS 1000, 0/1) confirma que `record+0xf0` no cambia: las líneas son 16 / 263 / 1097 en
  todos los casos.
- **C3-B** usa `record+0xf0` y `4219 − líneas`; coincide con T047 en las tres velocidades. No usa el VTS del
  descriptor ni el predicado.

### 7.2 Otros puntos

| Vel. | Líneas | C3-B r5 | Comentario |
|---|---:|---:|---|
| 1/8000 | 8 | 4211 | −2,7 % por truncamiento de línea; no se declara ±5 % sin calibración |
| 1/30 | 2194 | 2025 | dentro de un cuadro (64,1 ms) |
| 1/15 | 4388 | **−169 → 0** | fuera de un cuadro; C3-B debe **rechazar** `r5 < 2` |
| 1 s / 30 s | — | negativo | fuera del mecanismo; no probar |

---

## 8. Comparación C3-A / C3-B

### 8.1 C3-A — reutilizar directamente el `r5` del productor

| Aspecto | Evaluación |
|---|---|
| Precisión | Buena **solo** con VTS 4219 y predicado 0 (A); con el predicado configurado (0) el `r5` es 2·frame − líneas, inválido |
| Compatibilidad | Requiere que `record+0x20` sea 4219 y que el predicado sea ≥2; ninguna de las dos cosas está demostrada |
| Efectos secundarios | La función escribe `+0x64/+0x68/+0x6a/+0x6c/+0x6d/+0xd8/+0xda/+0xdc`; exige copia a scratch |
| Reversión | RAM sí; no hay parche persistente |
| Veredicto | **No autorizable** con la evidencia actual |

### 8.2 C3-B — usar `record+0xf0` y reconstruir `r5`

| Aspecto | Evaluación |
|---|---|
| Precisión | Idéntica a T047: 4203 / 3956 / 3122; la cuantización de línea es la misma que la del productor. 4219 no es un VTS leído del descriptor: es la referencia efectiva medida en T046/T047 |
| Compatibilidad | No depende del VTS del descriptor ni del predicado; solo del Tv, del período y de la referencia 4219 |
| Efectos secundarios | Se ejecuta la función en scratch; se lee `+0xf0`; **no se copia `+0x68`** (no es un contador útil) |
| Reversión | RAM sí; apagado/encendido revierte; no hay escritura persistente |
| Veredicto | **Preferible**; es el candidato para T052-B1 |

### 8.3 Por qué C3-B ya está respaldado físicamente

T046/T047 aplicaron **ShutMode 0 + `r5` manual** con el predicado configurado (0; no se leyó en T047, se infiere del valor NVRAM) y obtuvieron
0,24 / 0,99 / 4,03 / 16,75 ms, uniformes por filas. Es decir, el cuadro extra del **cálculo** no impide una
exposición de un solo cuadro cuando el `r5` se construye con la ley de 4219. C3-B automatiza exactamente esa
`r5` a partir de las líneas que calcula Sony; no inventa una segunda integración.

### 8.4 Diseño lógico de C3-B (no implementado)

1. En `0x438c82a0` (después de `0x437f8a50`, antes de `0x436d6320`), guardar `r0-r3`, `r12`, `lr` y la pila.
2. Copiar **0x158 B** del registro global a un scratch verificado (nunca ejecutar sobre el global).
3. Ejecutar `0x4383fa40(scratch, imager)`.
4. Leer `líneas = [scratch+0xf0]`; calcular `r5 = 4219 − líneas`.
5. Comprobar `2 ≤ r5 < 4219`, `[scratch+0xc] != 0`, `[scratch+0x20]` coherente y `[scratch+0xf6]` igual a
   `settings+0x162`.
6. Si pasa, escribir **solo** `cap+0x64c = r5` y `cap+0x655 = 0` (ShutMode 0); **no** copiar `+0x68`, `+0x6a`,
   `+0x6c` ni `+0x6d` a `cap+0x64c+4..`. El bloque `cap+0x6bc` (SetRead) no se toca.
7. Si no pasa, no escribir nada y continuar con la foto normal.

**No se implementa en esta sesión.** La cueva C3, el scratch y el guardián son parte de T052-B1 y requieren
autorización adicional.

---

## 9. Riesgos

| Riesgo | Gravedad | Mitigación |
|---|---|---|
| Predicado ≥2 durante la foto (escritor externo) | media para C3-B: no afecta a `record+0xf0`; alta para C3-A | leer el byte en B0; C3-B lo ignora |
| VTS de foto distinto de 4219 | alta para C3-A; baja para C3-B | C3-B no usa el VTS del descriptor; la referencia 4219 es la medida T046/T047 |
| Período de línea distinto de 3891 | alta | leer `record+0xc` en B0; abortar si no es 3891 |
| Tv no estabilizado (carrera de T050) | media | esperar a que `settings+0x162` se estabilice antes de disparar/leer |
| `record+0xf0` ya limpio | alta | dos lecturas inmediatas; si el registro está a cero, no interpretar |
| Banco A/B equivocado | alta | leer los dos; decidir por Tv/r5/VTS no nulos y coherencia con settings |
| Scratch no verificado | media | reservar una región BSS verificada; volcar antes/después |
| Calibración absoluta ±25 % | media | luz controlada y referencias por tanda; no se cierra con C3 |
| >1 cuadro / bulb / 30 s | alta | no probar; límite de un cuadro |
| Escritura persistente | crítica | prohibida; solo RAM y reversión por apagado |

---

## 10. Veredictos A–T

| # | Pregunta | Veredicto | Tipo |
|---|---|---|---|
| A | ¿Se identificó el productor del descriptor VTS? | **PARCIAL**: se identificó el consumidor y la cadena `[ctx+0x3c]`; el escritor/selector de `+6` no | estático + emulación |
| B | ¿Se identificó cómo se selecciona el descriptor para fotografía? | **PARCIAL**: dispatcher `0x437b4eb4` → `0x437b4df0` → `0x437b5b14` → `0x43844e80`; el selector de modo no | estático + emulación |
| C | ¿Se pudo determinar el VTS fotográfico? | **NO** | falta lectura de foto |
| D | ¿Se identificó la causa de la diferencia 4219/4266? | **NO demostrada**; 4266 = `0x271000/600` de la vista en directo, 4219 = ley medida; 47 líneas ≈ 0,71 ms | V/I |
| E | ¿Se encontraron todos los escritores relevantes del predicado? | **SÍ en `av-cam`**: ninguno escribe `+0x10`; el bloque se copia de NVRAM | V estático |
| F | ¿Se demostró cuándo cambia su estado? | **NO físicamente**; el valor configurado es 0 y no hay transición estática | V/I/N |
| G | ¿Se identificó si el cuadro extra está activo durante fotografía? | **SÍ en el estado configurado** (byte 0 → predicado 1); falta confirmación física | V estático + N físico |
| H | ¿Se demostró el destino del contador `record+0x68`? | **SÍ**: `cap+0x64c+4` (param+4), leído por `SetExposure` como ventana; no hay acumulador | V |
| I | ¿La cámara estuvo accesible? | **NO** | comprobación única |
| J | ¿Se ejecutó físicamente B0? | **NO** | — |
| K | ¿Se leyeron registros de una fotografía real? | **NO** | — |
| L | ¿Se demostró que esos registros corresponden a la captura y no al reposo? | **NO** | — |
| M | ¿La emulación reproduce los datos observados? | **SÍ para la aritmética** (T047); **NO hay datos de foto** para comparar | V emulación |
| N | ¿Se puede usar directamente el `r5` de `0x4383fa40`? | **NO** con el predicado configurado (0); `r5 > VTS` | V emulación + NVRAM |
| O | ¿Es técnicamente viable reutilizar `record+0xf0`? | **SÍ**: `líneas` es independiente de VTS/predicado y C3-B reproduce T047 | V emulación + T047 |
| P | ¿Existe un candidato C3 con entradas y salidas verificadas? | **SÍ, C3-B**; C3-A no | V/I |
| Q | ¿Están cerradas las dependencias necesarias para preparar B1? | **CASI**: C3-B no necesita VTS/predicado; faltan la lectura física de B0 y el scratch/cueva | V/I |
| R | ¿Se recomienda ejecutar T052-B1? | **SÍ, después de B0 y con autorización expresa**, con C3-B; no C3-A | V/I |
| S | ¿Se realizaron escrituras RAM en la cámara? | **NO** | — |
| T | ¿Se modificó firmware persistente? | **NO** | — |

Los **NO** de C, F (parte física), I–L y M (datos de foto) son falta de medición, no imposibilidad física. El
**NO** de N sí es una contradicción demostrada con el estado configurado: el `r5` nativo incluye un cuadro
completo.

---

## 11. Decisión sobre T052-B1

**No se ejecutó T052-B1.** La decisión es:

### C3-B es el diseño preferido; C3-A no se autoriza

**Condiciones para B1:**

1. Ejecutar B0 físicamente: leer `record+0x20`, `+0xc`, `+0x1c`, `+0xf0`, `+0x64`, `+0x68`, `+0x6d`,
   `[0x43deb360+0x10]`, `settings+0x162`, `imager+0x4b8/+0x504` tras 1/4000, 1/250 y 1/60, dos veces.
2. Confirmar que `record+0xf0` es distinto de cero y que el período es 3891.
3. Implementar C3-B en RAM: scratch 0x158 B, `0x4383fa40`, `r5 = 4219 − [scratch+0xf0]`, escribir solo
   `cap+0x64c` y `cap+0x655`, guardián y reversión.
4. Capturar RAW+JPEG y medir exposición por filas y absoluta; criterios: r5 calculado = nativo ±1 línea,
   exposición ±5 % del objetivo, uniformidad ±5 %, Live/Video/AF sin cambios, reversión verificada.
5. Abortar si `r5 < 2`, `r5 ≥ 4219`, período ≠ 3891, predicado incoherente o lectura inestable.
6. No probar 1/15, bulb ni 30 s.

**Si B0 da un VTS distinto de 4219/4266:** C3-B sigue siendo válido porque no usa el VTS del descriptor; la
referencia 4219 debe re-medirse si el modo físico cambia. **Si B0 da predicado ≥2:** C3-A podría reevaluarse,
pero C3-B sigue siendo preferible por no depender del estado.

**No se construye firmware persistente. No se instala C3. No se ejecuta T052-B1 sin autorización adicional.**

---

## 12. Entregables, pruebas y límites

- **Informe:** este documento.
- **Evidencia:** `analysis/t052-b0/vts.json`, `predicado.json`, `emulacion.json`, `offline-sample.json`, `rea-xrefs.json`.
- **Scripts:** `scripts/t052_b0_readonly.py` (recolector; offline y físico), `scripts/t052_b0_emulate.py`
  (emulación), `scripts/t052_b0_evidence.py` (evidencia estática).
- **Pruebas:** `tests/test_t052_b0.py` — **19 pruebas**.
- **Regresión recomendada:** `tests/test_t052_a_parametros.py`, `tests/test_e25_16_r5_autonomo.py`,
  `tests/test_e25_15_shutmode.py`, `tests/test_e25_14_exposicion.py`.
- **Límites:** no hay lectura de foto; el VTS de foto sigue **N**; el predicado de foto no se leyó (solo su
  fuente NVRAM y el valor de reposo); `cap` no se localizó; la emulación no prueba el sensor; la calibración
  absoluta ±25 % sigue abierta; C3-B no se implementó.

**Comandos:**

```bash
python3 scripts/t052_b0_emulate.py          # regenera analysis/t052-b0/emulacion.json
python3 scripts/t052_b0_evidence.py         # regenera vts.json y predicado.json
python3 scripts/t052_b0_readonly.py --protocol
python3 scripts/t052_b0_readonly.py --offline analysis/t052-b0/offline-sample.json \
  --label offline-1_250 --out /tmp/t052b0-offline.json
python3 -m pytest tests/test_t052_b0.py tests/test_t052_a_parametros.py \
  tests/test_e25_16_r5_autonomo.py tests/test_e25_15_shutmode.py \
  tests/test_e25_14_exposicion.py -q
```
