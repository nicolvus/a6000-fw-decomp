# E25-24b — Selector EFCS / Electronic: implementación offline

28-10-2026. Continuación de [E25-24](e25-24-selector-efcs-electronico.md). Sin cámara, sin
flasheo, sin escrituras RAM. Todo lo que sigue es análisis de bytes, parches preparados y
emulación; **no** es una validación física.

Base: `bed32ade` (HEAD al empezar). Firmware A6000 3.21:
`av-cam.bin` SHA-256 `b60c845c…e56bb9`; `darwin_core.bin` SHA-256 `5f2be06d…0bf4`.

**Método:** el MCP de REA no estuvo disponible en esta sesión. Las direcciones y los bytes
decisivos se verificaron contra los binarios originales con Capstone y con los exports de REA
ya presentes en `analysis/efcs-reia/` y `analysis/e25-*`; no se inventó ninguna consulta ni
resultado de REA. Donde una afirmación depende de un valor de ejecución se marca
NO_VERIFICADO.

---

## 1. Arquitectura seleccionada

**Binaria: EFCS ↔ ELECTRONIC**, reutilizando el ajuste EFCS existente.

| Opción de menú | Modelo | Campo `+0x210` | Modalidad | Segunda cortina |
|---|---|---|---|---|
| EFCS activado | `0x2b4` | 0 | `EFCS` | mecánica (ruta Sony original) |
| EFCS desactivado | `0x2b5` | 1 | `ELECTRONIC` | ninguna (Darwin suprime bobinas y motor) |

No se añade una entrada de menú ni se reinterpreta `+0x210`: el valor sigue significando
EFCS on/off (T012: 0 con EFCS activo, 1 con EFCS inactivo). La modalidad se deriva en una
variable explícita (`scripts/e25_24/selector.py`) y se transporta por captura en
`pkt[0x0e]`. La alternativa de tres estados (MECHANICAL ↔ EFCS ↔ ELECTRONIC) queda
documentada al final, pero no se implementa: exigiría un tercer valor de menú/persistencia
no demostrado.

La ruta ELECTRONIC conserva, por ahora, el planificador normal (`ShutMode 3`, `r5=1`) y
solo demuestra la **selección de ruta sin cortinas mecánicas**. La corrección de exposición
electrónica (C3-B, `ShutMode 0` + `r5`) es un parche separado, E25-26, que se engancha en
`0x438c82fe` y se condiciona al mismo byte `pkt[0x0e]`. No se mezcla con el selector.

---

## 2. Solución de B1a

### 2.1 Por qué B1a no podía condicionarse solo en Darwin

B1a (`0x1fe6a: 28 46 → 0a e0`) fuerza a 0 la compuerta del motor (`0x1fe66`, nibble alto del
tipo de mecanismo). El parche tipo 0 (`0x20c78: 09 e0 00 bf 00 bf 00 bf`) fuerza a 0 el tipo
de bobina (`0x20c74`, nibble bajo). Ambos leen la **misma** celda `[0x20000050+canal]` a través
de `0x1b080`:

```
0x1b080  ldr r2,=0x200002c0     ; presencia
         ldrb r2,[r2,r1]
         movs r0,#0
         cbz r2, ret
         ldr r0,=0x20000000
         add r0,r1
         ldrb.w r0,[r0,#0x50]   ; tipo (nibble alto = compuerta; bajo = bobina)
ret:     bx lr
```

Los dos parches son globales y Darwin no recibe EFCS en el mensaje `0x0c`: BIONZ envía el
mismo `0x0c` y el mismo `0x107` con EFCS on u off. Por tanto, sin una señal nueva por captura,
cualquier condición en Darwin sería o global o inventada. La señal nueva se añade en un byte
del propio `0x0c` que el análisis de E24-05a no asigna a ningún consumidor: `pkt[0x0e]`.

### 2.2 Señal por captura: `pkt[0x0e]`

El constructor `0x43841070` escribe el paquete de 22 B. En `0x43841476` escribía
`pkt[0x0e] = 0` de forma incondicional. El analizador de Darwin `0x17f8c` copia el paquete a
`S+0x30` (`S = 0x200036d8`) y, en `0x17ff8`/`0x17ffc`, copia `pkt[0x0e]` a `S+0x3e`
(`0x20003716`). Ese byte no tiene lector estático identificado en el mapa del paquete
(E24-05a lista `+0`, `+1`, `+2..3`, `+4..0x0b`, `+0xc`, `+0xd`, `+0x12`).

El parche de BIONZ escribe en `pkt[0x0e]` el campo EFCS (`cap+0x41c`, el mismo que lee la
clase en `0x43842158`), en **las dos ramas** del constructor:

* `[sp+0x44] == 1`: cave → `pkt[0x0e] = cap+0x41c`, retorno a `0x43841346`.
* `[sp+0x44] != 1`: cave → mismo store, salto a `0x43841576` (rama original).

Así no hay residuos de una captura anterior y no se depende de que el buffer esté a cero.

### 2.3 Compuerta condicionada en Darwin

Se parte del **Darwin original**, no del tipo 0/B1a. Se sustituyen solo las dos llamadas a
`0x1b080` dentro de las compuertas por una llamada a un cave:

```
0x20c78  bl 0x1b080  ->  bl 0x4318    ; 0x20c74, tipo de bobina
0x1fe6c  bl 0x1b080  ->  bl 0x4318    ; 0x1fe66, compuerta del motor

0x4318:  ldr r2,[pc,#0x14]   ; 0x4330 -> 0x20003716 (S+0x3e)
0x431a:  ldrb r2,[r2]
0x431c:  cbz r2, 0x4322      ; 0 -> EFCS: ruta original
0x431e:  movs r0,#0
0x4320:  bx lr               ; != 0 -> Electronic: 0
0x4322:  b.w 0x1b080         ; EFCS: 0x1b080 original
0x4330:  .word 0x20003716
```

`0x4318..0x4327` y `0x4330..0x4333` eran cero en la tabla de vectores (entradas 70 y 76). No
hay referencias `bl` ni literales a esas direcciones; el resto de la tabla no se toca. El cave
no modifica `0x20c74`, `0x1fe66`, `InitCom`, `Upd`, reset, watchdog ni GPIO.

Resultado:

| `pkt[0x0e]` | `0x20c74` (bobina) | `0x1fe66` (motor) | Efecto |
|---|---|---|---|
| 0 (EFCS) | 3 | 4 | ruta original: segunda cortina mecánica |
| 1 (Electronic) | 0 | 0 | sin bobinas P4D/P4E y sin motor de rearme |

P4B/P4C siguen su curso, igual que en la ruta original; no se afirma que P4B/P4C no se
accionen. La supresión demostrada es la de las compuertas que gobiernan P4D/P4E y el motor.

---

## 3. Cadena del selector

```
Menú EFCS (libObj / userland)
  acción 0x6896ac → mensaje 0x75fa → parámetro 0x9776
  conversor 0x68c24a: 1→0x2b4, 2→0x2b5
  secuencia 0x95a308 → selector 0x4099 → conversor 0x99e968
  buffer 9 B: +0=05, +2/+3=99 40, +8=0/1
        │  LIRO
        ▼
Tabla LIRO (entrada 0x4099, offset 0xabe954) → handler 0x43802e4c
  ldrb r2,[r0,#8]; str.w r2,[0x43edf684+0x210]   ; 0/1, palabra
        │
        ▼
0x43844e80  lee (*contexto)+0x210 y copia a param6+0x41c (cap/registro)
        │
        ▼
0x43841070  constructor de captura
  ├─ 0x43842158 lee [sb+0x41c] (EFCS) y calcula la clase 0–7
  ├─ parche E25-24: pkt[0x0e] = [sb+0x41c]  (las dos ramas)
  └─ 0x4383fa40 productor nativo de r5 (solo si la ruta Sony lo llama)
        │  0x0c (22 B) por CAIF
        ▼
Darwin 0x17f8c: copia pkt[0x0e] a S+0x3e (0x20003716)
        │
        ▼
Darwin 0x20c74 / 0x1fe66 → cave 0x4318 → 0x1b080 original o 0
        │
        ▼
P4D/P4E y motor: originales en EFCS; suprimidos en Electronic
```

La cadena BIONZ → `SetExposure` no cambia: `0x437f8a50` construye `cap+0x64c/0x6bc`,
`0x438c830c` llama a `SetExposure`, `0x438c831e` a `SetRead`, `0x438c8330` a `Execute(1)` y
`0x43901a8c` envía `0x107`. El selector solo decide si Darwin puede mover el mecanismo.

---

## 4. Implementación

| Archivo | Contenido |
|---|---|
| `scripts/e25_24/selector.py` | Modalidad, conversión modelo/campo, máquina de estados, ticket de captura, errores |
| `scripts/e25_24/patch_bionz.py` | Parche de `av-cam.bin`: NOP de la rama, BL al cave, NOP del store, cave de 20 B |
| `scripts/e25_24/patch_darwin.py` | Parche de `darwin_core.bin`: dos BL, cave de 14 B, literal `S+0x3e`, regiones protegidas |
| `scripts/e25_24/emu.py` | Unicorn: compuertas Darwin y cave BIONZ |
| `scripts/e25_24/build_evidence.py` | Genera `analysis/e25-24/evidence.json` (hashes, diff, matriz) |
| `tests/test_e25_24_selector.py` | 36 pruebas: estados, bytes, desensamblado, reversión, emulación, cadena |

### 4.1 Parche BIONZ (28 bytes distintos)

| Dirección | Antes | Después | Rol |
|---|---|---|---|
| `0x4384133e` | `40 f0 1a 81` | `00 bf 00 bf` | elimina el salto condicional; el cave decide |
| `0x43841342` | `00 23 23 70` | `bl 0x43541a80` | replica `pkt[0]=0` y escribe `pkt[0x0e]` |
| `0x43841476` | `a3 73` | `00 bf` | evita que el store posterior borre el byte |
| `0x43541a80` | 20 B a cero | cave | `pkt[0]=0; pkt[0x0e]=[sb+0x41c]; cmp r1; beq/b.w; bx lr` |

Cave (20 B):

```
00 23         movs r3,#0        ; se conserva r3=0 para pkt[1]
23 70         strb r3,[r4]      ; pkt[0]=0
d9 f8 1c 24   ldr.w r2,[sb,#0x41c]
a2 73         strb r2,[r4,#0xe] ; pkt[0x0e]=EFCS
01 29         cmp r1,#1
01 d0         beq +2
ff f2 70 bd   b.w 0x43841576
70 47         bx lr
```

El cave se coloca en el relleno de ceros `0x435418e4–0x43541aff`, entre la cabecera LIRO y
el código (`0x43541b00`). Es la única zona de 20 B contigua sin referencias `bl`/literal en
ese rango. **Riesgo residual:** no está demostrado que el cargador de BIONZ no consuma ese
relleno; la instalación física exigiría comprobarlo (fuera de esta autorización).

### 4.2 Parche Darwin (22 bytes distintos)

| Dirección | Antes | Después | Rol |
|---|---|---|---|
| `0x20c78` | `fa f7 02 fa` | `e3 f7 4e fb` | `bl 0x4318` (bobina) |
| `0x1fe6c` | `fb f7 08 f9` | `e4 f7 54 fa` | `bl 0x4318` (motor) |
| `0x4318` | 14 B a cero | cave | lee `S+0x3e`, decide |
| `0x4330` | 4 B a cero | `16 37 00 20` | literal `0x20003716` |

Cave (14 B): `05 4a 12 78 0a b1 00 20 70 47 16 f0 ad be`.

No se modifica `0x20c74`, `0x1fe66`, `0x1b080`, `InitCom`, `Upd`, reset, watchdog, tabla de
alimentación ni GPIO. Las regiones protegidas se comparan por SHA-256 en el manifiesto.

---

## 5. Emulación

Unicorn, memoria RAM sintética: `[0x20000050]=0x43`, `[0x200002c0]=1`, `[0x20003716]=flag`.
No se modela el sensor ni la captura completa.

| Imagen | flag | `0x20c74` | `0x1fe66` |
|---|---|---|---|
| original | 0 | 3 | 4 |
| original | 1 | 3 | 4 |
| parcheada | 0 (EFCS) | 3 | 4 |
| parcheada | 1 (Electronic) | 0 | 0 |

BIONZ, desde `0x4384133e`:

| `[sp+0x44]` | `cap+0x41c` | `pkt[0]` | `pkt[0x0e]` | Fin |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | `0x43841346` |
| 1 | 1 | 0 | 1 | `0x43841346` |
| 0 | 0 | 0 | 0 | `0x43841576` |
| 0 | 1 | 0 | 1 | `0x43841576` |

El cave no toca `r0` (la instrucción `and r0,r0,#3` de `0x43841472` sigue ejecutándose en su
sitio) y usa `r2` para el campo EFCS, dejando `r3=0`: el bloque de clase hace `adds r3,#0x40`
y un `r3=1` habría producido `pkt[1]=0x41` en vez de `0x40`. La prueba
`test_emu_bionz_conserva_r3_y_pkt1` lo cubre comparando original y parcheado.

Casos cubiertos por los tests: EFCS→Electronic, Electronic→EFCS, transiciones repetidas,
valor inválido, cambio durante captura, error/recuperación, reinicio, reversión exacta,
regiones protegidas y comparación original/parcheado. No se simula el movimiento físico de
la cortina: observar una llamada o un registro no prueba que el obturador se mueva.

---

## 6. Compatibilidad

* **B1a / tipo 0:** este parche los sustituye. No se puede aplicar sobre un Darwin que ya
  lleva tipo 0 o B1a (`DarwinImage.load` lo rechaza); hay que partir del original.
* **T050 (RAM):** el parche de BIONZ es de imagen, no de RAM. T050 sigue siendo la vía
  experimental de exposición; no se mezcla con el selector.
* **C3-B (E25-18/E25-20):** el enganche recomendado sigue siendo `0x438c82fe`, limitado al
  paso 0 y a fotos rápidas. Debe añadir su propia condición `pkt[0x0e] == 1`; el selector no
  lo activa por sí solo. El plan nativo `0x4383fa40` no se toca.
* **Darwin:** recibe el mismo `0x0c` y `0x107`; la única diferencia es `pkt[0x0e]`. No se
  añaden mensajes ni se cambia `InitCom`.
* **Planificador EFCS:** la ruta EFCS conserva el constructor, la clase, el productor de `r5`
  y el orden `SetExposure`/`SetRead`/`Execute`. El parche no altera `record` ni `cap+0x64c`.

---

## 6bis. Contradicciones resueltas

| Afirmación A | Afirmación B | Evidencia | Resolución |
|---|---|---|---|
| «E = r5 × 15,2 µs» (informe EFCS) | «E = (VTS − r5) × período» (E25-10/E25-18) | `0x4383fa40` escribe `record+0x64 = frame − líneas`; T047: `r5=4203`, VTS 4219 → 243 µs ≈ 1/4000 | **B**. `r5` es la línea de inicio; la integración son las líneas restantes. Corregido en §2 y en el test `test_formula_r5_corregida`. |
| VTS 4219 y período 3891 Q8 son universales | E25-19 midió VTS 4176 y período 4096 | Lectura física T053; el productor lee `record+0x20`/`+0xc` | **B**. Son valores de un modo/contexto; el diseño lee el registro y no hardcodea. La emulación de E25-18 usa 4219 solo como referencia de T047. |
| Enganche C3 en `0x438c82a0` | E25-18 propone `0x438c82fe` | Bytes: `0x438c829c` es `bl 0x437f8a50`; `0x438c82a0` carga `r5`; `0x438c82fe` es `bl 0x436d6118`; `0x438c830c` es `SetExposure` | **B** para C3-B (tras `0x43b1e520`, antes de `SetExposure`). `0x438c82a0` no está «después de `0x438c82dc`». |
| EFCS original no mueve P4D/P4E (confusión con tipo 0) | EFCS usa segunda cortina mecánica | `0x20c74`/`0x1fe66` leen el tipo; tipo 0/B1a los fuerzan a 0; EFCS original no lleva esos parches | **B**. EFCS original sí usa la ruta mecánica; tipo 0/B1a son el baseline silencioso, no EFCS. El selector restaura la ruta original en EFCS. |
| La clase 1/3 es ShutMode | `record+0x6d` = clase/ShutMode; `cap+0x655` = ShutMode del bloque SetExposure | `0x43842158` escribe la clase en `destino+0x60`; `0x4383fd6c` copia `record+0x6d` a `cap+0x655`; el productor nativo escribe 0 | **B**. Clase y ShutMode están relacionados pero no son lo mismo; el selector no usa la clase como señal de modalidad (usa `cap+0x41c`). |
| Darwin distingue EFCS por el mensaje | BIONZ envía el mismo `0x0c`/`0x107` con EFCS on/off | E24-05a/E24-05f: el paquete no lleva EFCS; el tipo de mecanismo es celda de Darwin | **A es falsa**. Se añade `pkt[0x0e]` como señal explícita; no se reutiliza un campo con otro consumidor. |
| `SetExposure` demuestra inicio/fin físico | Solo demuestra despacho a P2S | E25-21/E25-22: bloque y despacho, sin traza eléctrica | **B**. La implementación no afirma inicio/fin físico; queda para E25-27. |

Cada corrección tiene una prueba o una comprobación de bytes en
`tests/test_e25_24_selector.py`; las que dependen del sensor (inicio/fin, uniformidad) no se
pueden probar offline y se marcan como pendientes físicos.

---

## 7. Reversibilidad

Cada parche guarda los bytes originales y su SHA-256. `restore_bytes()` reconstruye la imagen
exacta y los tests comprueban que el SHA vuelve a `b60c845c…` / `5f2be06d…`. Para revertir:

```bash
python -m e25_24.patch_bionz  parcheado.bin  restaurado.bin --restore
python -m e25_24.patch_darwin parcheado.bin  restaurado.bin --restore
```

Los módulos `restore_bytes()` son la vía programática; no hay cambios fuera del diff. En
Darwin, restaurar los dos `bl` y el cave devuelve el comportamiento original (incluida la
segunda cortina para EFCS). En BIONZ, restaurar los tres sitios y el relleno devuelve el
constructor original.

---

## 8. Limitaciones físicas

No demostrado offline:

1. Que el cargador de BIONZ acepte el parche en el relleno y que la imagen arranque.
2. Que `pkt[0x0e]` no tenga un consumidor no detectado en Darwin (el mapa no lo lista; el
   barrido de lecturas con desplazamiento `0x3e` no encontró ninguno, pero no prueba ausencia).
3. Que las entradas 70/76 de la tabla de vectores de Darwin no se usen en ningún modo.
4. Que EFCS accione físicamente la segunda cortina con el Darwin parcheado.
5. Que Electronic no accione ninguna cortina (sonido, consumo, sensor).
6. La exposición RAW de Electronic: con `ShutMode 3` sigue el sesgo por filas de E25-10;
   la corrección C3-B es E25-26.
7. La sincronización de fin de exposición (`0x0e`) y la lectura RAW completa.
8. Cualquier recuperación tras un fallo de arranque: E24-04 sigue vigente (sin recuperación
   independiente demostrada).

El protocolo físico (separado, requiere autorización) está en
[e25-24c](e25-24c-protocolo-fisico-selector.md).

---

## 9. Publicación

* `scripts/e25_24/` (5 módulos + `__init__`).
* `tests/test_e25_24_selector.py` (36 pruebas).
* `analysis/e25-24/evidence.json` (hashes, diff, caves, emulación).
* Este informe y el protocolo físico.
* Actualización de E25-24, E25-25, E25-13, E25-12, PENDIENTES, STATE, CURRENT, PROGRESS e
  INDEX.

Los binarios parcheados **no** se versionan (política de firmware). El manifiesto contiene
los bytes exactos para reconstruirlos a partir de los originales.

---

## 10. Estado final

**IMPLEMENTADO Y VERIFICADO OFFLINE (selector y compuerta mecánica).**

* Cadena del selector reconstruida hasta `pkt[0x0e]` y las compuertas de Darwin.
* B1a/tipo 0 sustituidos por una compuerta por captura; EFCS conserva la ruta original y
  Electronic la suprime.
* Parches con bytes originales, manifiesto, reversión y 36 pruebas.
* Emulación: matriz EFCS/Electronic correcta; original vs parcheado idéntico con flag 0.
* **Pendiente:** C3-B para la exposición electrónica (E25-26) y toda la validación física
  (E25-27). No se declara funcionamiento en cámara.

---

## Apéndice — Tres estados (no implementado)

La variante MECHANICAL ↔ EFCS ↔ ELECTRONIC podría usar el campo Silent `+0x238` (handler
`0x438032d4`, bloque `0x43edf684`) para distinguir MECHANICAL de ELECTRONIC cuando EFCS está
desactivado. El cave de BIONZ necesitaría leer dos campos y calcular
`electronic = (+0x210 == 1 && +0x238 == 1)`; el resto del diseño no cambia. No se implementa
porque la A6000 no expone el ajuste Silent en el menú y no se ha demostrado un tercer valor
persistente seguro. La variante binaria es la que se entrega.
