# EFCS + Darwin + Silent Shutter — Integración técnica integral

Sony A6000 fw 3.21, sensor IMX210, BIONZ X `av-cam.bin`.
Análisis principal mediante REA (Ghidra 12.1.4, sesión efímera sobre `av-cam.bin`,
SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`,
base `0x43541000`). Complementado con la investigación previa del repositorio
(E25-10 a E25-22, E24-05, rea-tema3, etc.).

Etiquetas usadas: **VERIFICADO** (bytes/instrucciones leídas con REA), **INFERENCIA**
(conclusión razonada sobre evidencia), **NO_VERIFICADO** (ausente del binario o sin
demostración física).

---

## 0. Resumen ejecutivo

La A6000 ya tiene un **Silent Shutter funcional** (fw 3.23, parche B1a en Darwin:
`0x1fe6a: 28 46 → 0a e0`, 2 bytes) que desactiva el accionamiento mecánico del
obturador durante la captura. Lo que falta es **control de exposición uniforme y
sincronizado** a velocidades rápidas: hoy la foto sale con exposición no uniforme y
casi independiente de la velocidad seleccionada de 1/4000 a 1/500 (E25-10).

Esta investigación reconstruye por primera vez la implementación EFCS completa de
Sony mediante REA y demuestra que:

1. **EFCS ya contiene el productor nativo de `r5`** (`0x4383fa40`), llamado tanto
   por el constructor normal como por el constructor EFCS. Calcula `r5` a partir del
   Tv real, el período de línea y el VTS, y fija `ShutMode = 0` (reinicio por filas,
   exposición uniforme).
2. **EFCS no controla directamente a Darwin.** BIONZ toma las decisiones de captura
   y envía mensajes a Darwin; Darwin ejecuta el mecanismo (o no, con tipo 0/B1a) y
   responde con `ExposureReady` (ID `0x0e`) para terminar la espera de BIONZ.
3. **La ruta más prometedora es la Alternativa B**: modificar exclusivamente BIONZ
   para que la foto use `ShutMode = 0` con `r5` calculado por el productor nativo
   `0x4383fa40`, manteniendo Darwin 3.23 (B1a) intacto. Punto mínimo de modificación:
   enganche tras `0x437f8a50` y antes de `SetExposure` (`0x436d6320`), en
   `0x438c82a0`/`0x438c82fe`.
4. **No es necesaria modificación adicional de Darwin** para velocidades ≤ 1/30 s.
   B1a ya suprime las bobinas P4D/P4E; EFCS + B1a da obturación electrónica
   uniforme sin mover el mecanismo.

---

## 1. Investigación A — Reconstrucción completa de EFCS

### 1.1 Mapa de ejecución EFCS (REA-verificado)

Todas las direcciones, funciones, llamadores y campos se verificaron contra los
bytes originales de `av-cam.bin` con REA. La evidencia completa se guarda en
`analysis/efcs-reia/evidence/`.

```
Configuración de usuario (menú EFCS, común +0x210)
        │
        ▼
0x43844e80  lee contexto+0x210 (campo EFCS ON/OFF)
        │
        ▼
0x437b5b14  banco de exposición (GOT 0x44023eb4 → 0x43eb2680, campo en 0x43eb2a9c)
        │
        ▼
0x4384b268  instantánea de 0x92c bytes (GOT 0x44021ba8 → 0x43ea976c)
        │
        ▼
0x4383fc48  selección de banco (0x43ea976c o 0x43eee9d4)
        │
        ▼
0x43842158  selección de clase de exposición (clase 0–7)
        │
        ▼
0x43841070  constructor de captura EFCS (6 parámetros)
        │  ├─ llama 0x4383fc48 (banco)
        │  ├─ llama 0x43842158 (clase)
        │  ├─ llama 0x4383fa40 (productor nativo r5, si flag)
        │  └─ escribe record+0x64 (r5), +0x68 (svd), +0x6d (ShutMode=0)
        │
        ▼
0x437f8a50  construcción de parámetros de captura (cap+0x64c, cap+0x6bc)
        │  ├─ si condición: 0x4383fd6c (copia registro→exposición)
        │  ├─ si condición: 0x43840150 (bloque +0x30 SetRead)
        │  └─ si no: 0x437b21b8 (planificador VTS)
        │
        ▼
0x438c828c  programación de exposición (StartExposure)
        │  ├─ 0x437f8a50 (construye params)
        │  ├─ modo 2/3: forza cap+0x64c=2, cap+0x650=0 (ShutMode 0, r5=2)
        │  ├─ paso 0 (cap+0x4b9c==0):
        │  │   ├─ 0x436d6320 → vtable+0x28 → SetExposure IMX210 (0x436d6f6c)
        │  │   ├─ 0x436d6398 → vtable+0x30 → SetRead IMX210 (0x436d7e08)
        │  │   ├─ SSB (0x43ad9116), Execute(1) (0x43ad911c)
        │  │   └─ 0x43901a8c(2, 0x107, ...) → mensaje a Darwin con timing
        │  └─ paso >0: Execute(0) solo
        │
        ▼
IMX210: SetExposure (blk+0x50..0x57) + SetRead (blk+0x66..0x6c)
        │
        ▼
P2S/DFE → inicio de integración → lectura por filas → RAW/JPEG → finalización
```

### 1.2 Funciones del mapa EFCS (desensamblado REA)

Cada función incluye dirección, tamaño, llamadores, callees, campos y pseudocódigo resumido.
Evidencia: `analysis/efcs-reia/evidence/<addr>_pseudo.txt` y `_analyze.json`.

| Función | Dirección | Tamaño | Rol en EFCS | Llamadores | Callees clave |
|---------|-----------|--------|-------------|------------|---------------|
| Config EFCS | `0x43844e80` | — | Lee `contexto+0x210` (EFCS ON/OFF) | — | — |
| Banco de exposición | `0x437b5b14` | — | Pasa banco como param6 | `0x43844e80` | — |
| Instantánea | `0x4384b268` | — | Copia 0x92c bytes del banco | `0x437b5b14` | `0x437b03c8` |
| Selección de banco | `0x4383fc48` | — | Retorna banco A o B | `0x43841070` | — |
| **Clase de exposición** | `0x43842158` | 486 B | Determina clase 0–7 | `0x43841070` | `0x43841aac` |
| **Constructor EFCS** | `0x43841070` | 2456 B | Construye captura EFCS | `0x437f87ac` (47 xrefs) | 0x43842158, 0x4383fa40, 0x4383fc48, 0x4383fbc4, 0x4383fb6c |
| **Productor nativo r5** | `0x4383fa40` | 186 B | Calcula r5, svd, ShutMode=0 | `0x437b43b4` (normal), `0x43841070` (EFCS) | 0x4355faf0, 0x4355fd4c, 0x4382fa94, 0x4382fac8, 0x43a12ca8 |
| **Registro→exposición** | `0x4383fd6c` | 156 B | Copia record+0x64..0x73 (16 B) | `0x437f8a50`, `0x43b1c096` | 0x4383fb6c, 0x43857f40, 0x43859944, 0x439c5320 |
| **Params de captura** | `0x437f8a50` | 218 B | Construye cap+0x64c y cap+0x6bc | `0x438c828c` | 0x4383fd6c, 0x43840150, 0x437b21b8, 0x43ae9462 |
| **Programación exposición** | `0x438c828c` | 462 B | StartExposure, envía 0x107 a Darwin | `0x43b1b22e`, `0x43b1e7f2` | 0x437f8a50, 0x436d6320, 0x436d6398, 0x43ad9116, 0x43ad911c, 0x43901a8c |
| SetExposure wrapper | `0x436d6320` | 46 B | Dispatch vtable+0x28 | `0x438c828c` | vtable+0x28 → `0x436d6f6c` |
| SetRead wrapper | `0x436d6398` | — | Dispatch vtable+0x30 | `0x438c828c` | vtable+0x30 → `0x436d7e08` |
| Mensaje a Darwin | `0x43901a8c` | 162 B | Envía mensaje clase 2 con 0x107 | `0x438c828c` | 0x43901a68, 0x435612d0, 0x4356120c |
| Selector secuencias | `0x437ea8cc` | — | (no auto-detectado por Ghidra) | — | — |
| Planificador VTS | `0x437b21b8` | 826 B | VTS por cuadro | `0x437f8a50` (else rama) | — |
| Bloque +0x30 | `0x43840150` | 442 B | SetRead params | `0x437f8a50` | 0x4383fb6c, 0x4383fbc4 |

**Direcciones mencionadas en la misión no reconocidas como entrada de función por Ghidra:**
- `0x436d6f6c` (SetExposure IMX210): alcanzado solo vía dispatch indirecto `**(code **)(*(int *)*imager + 0x28)` en `0x436d6320`. Bytes en `0x436d6f6c`: `d0 f8 70 31 2d e9 f0 4f …` (código Thumb real, entrada verificada en bytes, frontera de función por confirmar).
- `0x437ea8cc` (selector de secuencias): código Thumb real en bytes (`2d e9 f3 47 04 46 …`), no auto-detectado como función.
- `0x43844e80` (config EFCS): código Thumb real (`2d e9 f0 4f 99 b0 …`), no auto-detectado.

Estas tres direcciones son código Thumb válido (verificado por lectura de bytes) que Ghidra no sometió a análisis como entrada de función; se alcanzan por llamadas indirectas o no fueron semilladas. No invalidan el mapa.

### 1.3 Pseudocódigo de las funciones clave

#### `0x4383fa40` — Productor nativo de r5 (VERIFICADO)

```
void FUN_4383fa40(int record, int settings)
{
  uVar8 = record+0xc;              // período de línea (Q8), si 0 → 1
  uVar6 = settings+0x4b8;          // factor, si 0 → 1
  uVar2 = 0x825700 / uVar8;        // división truncante
  uVar3 = uVar2 / uVar6;
  uVar7 = record+0x20;             // VTS
  if (record+0x20 <= uVar3) uVar7 = uVar3;   // frame = max(VTS, 0x825700/period/factor)
  if (record+0xf6 < 0xc55) {       // Tv <= ~16 s
    uVar2 = 0x4382fac8();          // µs entero
    uVar8 >>= 8;
  } else {
    uVar2 = 0x4382fa94();          // µs Q8
  }
  iVar4 = uVar2 / uVar8;           // líneas de integración
  uVar8 = record+0x1c + iVar4;     // suelo + líneas
  if (uVar8 < uVar7) uVar8 = uVar7; // frame = max(suelo+líneas, frame)
  if (0x43a12ca8() != 0) uVar8 += uVar7;   // +1 frame si predicado de cuadro extra
  sVar1 = uVar8 / uVar7;           // cuenta de frames
  if (sVar1 != 0) sVar1 -= 1;      // svd = frames - 1
  record+0x68 = sVar1;             // svd
  record+0x64 = uVar8 - iVar4;     // r5 = frame - líneas
  record+0x6d = 0;                 // ShutMode = 0
  record+0xf0 = iVar4;             // líneas
  record+0xd8 = uVar6 * (extra + uVar7);   // VTS cuadro 1
  record+0xda = sVar1 * uVar6;     // VTS intermedios
  record+0xdc = sVar1 * uVar6;     // VTS último
}
```

**Significado:** `r5 = frame − líneas`, `ShutMode = 0`, `svd = frames − 1`. La exposición efectiva es `r5 × 15,2 µs` (reinicio por filas, uniforme).

#### `0x4383fd6c` — Transferencia registro → parámetro de exposición (VERIFICADO)

Copia 16 bytes desde `record+0x64` al destino apuntado por `param_3`:
- `destino+0` = `record+0x64` = **r5** (integración en líneas)
- `destino+4` = `record+0x68` = **svd** (frames)
- `destino+6` = `record+0x6a` = spl
- `destino+9` = `record+0x6d` = **ShutMode**

Llega a `cap+0x64c` vía `0x437f8a50`. Es el bloque que recibe `SetExposure`.

#### `0x438c828c` — Programación de exposición / StartExposure (VERIFICADO)

Secuencia real (paso 0, `cap+0x4b9c == 0`):
1. `0x43ae769a(cap, 0xe)` — inicialización
2. `uVar2 = 0x437f8a50(cap)` — construye `cap+0x64c` y `cap+0x6bc`
3. `iVar3 = 0x43a12c64()` — lee modo de captura (retorna 0, 1, 2 o 3)
4. **Si modo es 2 o 3:** fuerza `cap+0x655=0`, `cap+0x650=0`, `cap+0x64c=2`, `cap+0x652=0`, `cap+0x654=0` (bloque forzado: ShutMode 0, r5=2, svd=0)
5. **Si `cap+0x4b9c == 0`:**
   - `0x43b1e520(cap)` — fija `cap+0x73b` leyendo `cap+0x655`
   - `uVar1 = cap+0x650` (guarda svd)
   - **Si `cap+0x504 == 1`:** `cap+0x650 = 0` (anula svd para SetExposure)
   - `cap+0x6b8 = cap+0x12f8`
   - `uVar4 = 0x436d6118()` — obtiene objeto imager
   - `0x436d6320(uVar4, cap+0x64c, cap+0x4b9c)` — **SetExposure** (vtable+0x28)
   - `uVar4 = 0x436d6118()`
   - `0x436d6398(uVar4, cap+0x6bc, cap+0x4b9c)` — **SetRead** (vtable+0x30)
   - `0x436d6118()`
   - `0x43ad9116()` — SSB
   - `uVar4 = 0x436d6118()`
   - `0x43ad911c(uVar4, 1)` — **Execute(1)**
   - `cap+0x650 = uVar1` — restaura svd nativo
6. **Paso > 0:** solo `Execute(0)` (`0x43ad911c(uVar4, 0)`)
7. Cálculo de temporización (`cap+0x570`, `cap+0x740`, `cap+0x56c`)
8. `0x43901a8c(2, 0x107, timing, timing)` — **envía mensaje a Darwin** con clase 2, código 0x107, y datos de tiempo (`cap+0x4b64`, `cap+0x1d8`, `cap+0x56c`, `cap+0x570`)
9. Procesamiento final con `cap+0x74f`, `cap+0x548`
10. Retorna 1

#### `0x43842158` — Selección de clase de exposición (VERIFICADO)

```
uVar2 = banco+0x4bc;           // flags del banco
if ((uVar2 & 0x60) == 0 && (uVar2 & 0x80) == 0) {
  if (banco+0x41c == 1) {      // campo EFCS == 1
    uVar3 = 1;                 // clase base 1 (EFCS)
    if (param_4+2 == 0) { ... clase según umbral ... }
    else if (param_4+2 == 1) { ... modo +0x38c ... }
  } else { clase = 3; }        // EFCS desactivado → clase 3
} else { ... clase 1 o 5 según máscara 0x20 ... }
// Sobrescritura por bloque de diagnóstico:
// banco+0x7e == 0 → clase 0, 1 → 1, 2 → 1, 3 → 2, 4 → 3, 5 → 4, 6 → 5, 7 → 6
*(destino+0x60) = uVar3;       // escribe la clase
```

**Clases:** 0–7. La clase 1 se asocia con EFCS activado; la 3 es el modo normal. La clase 2 produce máscara 0x94 en SetExposure (difiere de la 3, que usa 0xd4, en bit 0x40).

#### `0x43841070` — Constructor de captura EFCS (VERIFICADO)

6 parámetros: `cap`, `settings/objeto`, `puntero_salida`, `byte*`, `byte*`, `int`.
- Llama `0x4383fc48` (selección de banco), `0x43842158` (clase de exposición)
- **Llama `0x4383fa40` (productor nativo r5)** cuando `pcVar22[0x15] == '\x01'`
- Escribe `record+0x64` (r5), `record+0x68` (svd), `record+0x6d` (ShutMode=0)
- 47 referencias cruzadas (muchos llamadores en el flujo de captura)

### 1.4 Campos clave de la captura (`cap`)

| Campo | Rol | Origen / escritor |
|-------|-----|-------------------|
| `cap+0x64c` | Bloque SetExposure: `+0=r5, +4=ancho, +6=alto, +9=ShutMode` | `0x4383fd6c` desde `record+0x64` |
| `cap+0x650` | svd (frames−1) | `0x4383fd6c` desde `record+0x68` |
| `cap+0x655` | ShutMode | `0x4383fd6c` desde `record+0x6d` |
| `cap+0x6bc` | Bloque SetRead (+0x30) | `0x43840150` o `0x437b21b8` |
| `cap+0x4b9c` | Contador de pasos (0 = paso 0) | Planificador de captura |
| `cap+0x504` | Flag que anula svd (1 → svd=0 a SetExposure) | Origen no localizado estáticamente |
| `cap+0x740` | Habilita contador de pasos / exposición larga | Productor no localizado |
| `cap+0x74f` | Rama de host (temporizador µs vs Darwin) | Escritores: `0x438acc9c`, `0x437df5e8`, `0x438c2562` |
| `cap+0x12f8` | Modo de captura | Ajustes |
| `cap+0x56c/0x570` | Tiempo enviado a Darwin | Cálculo en `0x438c828c` |
| `cap+0x11b0` | Compuerta del productor nativo en constructor normal | Origen no resuelto |
| `cap+0x1198` | Espejo de ajustes | `0x437f8a50` usa como `param_1` |
| `cap+0x1b8/0x1c0` | Selectores de banco/ajustes | `0x4383fb6c`, `0x4383fbc4` |

### 1.5 Campos clave del registro de cuadro (`record`)

| Campo | Rol |
|-------|-----|
| `record+0x64` | r5 (líneas de integración) |
| `record+0x68` | svd (cuadros − 1) |
| `record+0x6d` | ShutMode |
| `record+0xf0` | líneas computadas |
| `record+0xf6` | Tv (código de exposición) |
| `record+0x20` | VTS |
| `record+0x1c` | suelo de r5 |
| `record+0xc` | período de línea (Q8) |
| `record+0xd8/0xda/0xdc` | VTS por cuadro (primero/intermedio/último) |

### 1.6 Respuesta a las preguntas de Investigación A

| Pregunta | Respuesta | Etiqueta |
|----------|-----------|----------|
| ¿Qué hace EFCS durante una foto? | Construye parámetros de exposición (r5, svd, ShutMode), programa SetExposure/SetRead en el IMX210, envía timing a Darwin, gestiona pasos de captura | VERIFICADO |
| ¿Cómo se inicia la integración electrónica? | ShutMode 0 (reinicio por filas) + r5 (distancia reinicio→lectura), vía SetExposure blk+0x52 | VERIFICADO |
| ¿Diferencia EFCS on/off? | EFCS on: clase 1, productor nativo r5 llamado, ShutMode 0 posible. EFCS off: clase 3, r5=1 constante, ShutMode 3 | VERIFICADO (código) / INFERENCIA (efecto) |
| ¿Cómo se seleccionan las secuencias? | `0x4383fc48` selecciona banco; `0x43a12c64` lee modo (1/2/3); `0x438c828c` decide paso 0 vs paso >0 | VERIFICADO |
| ¿Qué habilita/bloquea EFCS? | Campo `banco+0x41c==1` habilita clase 1; modo 2/3 fuerza bloque ShutMode 0/r5=2 | VERIFICADO |
| ¿Qué determina ShutMode? | Byte `record+0x6d` (escrito por `0x4383fa40` a 0, o por ajustes a 3), modo 2/3 lo fuerza a 0 | VERIFICADO |
| ¿Cuándo ejecuta `0x4383fa40`? | Cuando es llamado por `0x437b43b4` (normal, compuerta `cap+0x11b0`) o `0x43841070` (EFCS, flag `pcVar22[0x15]==1`) | VERIFICADO |
| ¿Qué cambia EFCS en IMX210? | ShutMode 0 (reinicio por filas, uniforme) + r5 (tiempo de integración) vs ShutMode 3 (reinicio global + lectura, sesgo vertical) | VERIFICADO (código) + T046 (medido) |
| ¿Qué funciones quedan activas sin Darwin moviendo el obturador? | SetExposure, SetRead, SSB, Execute, productor r5, programación de sensor — todo el flujo BIONZ | VERIFICADO |
| ¿Qué elementos del flujo EFCS dependen de cortina mecánica? | Ninguno del flujo BIONZ/IMX210; solo Darwin mueve P4D/P4E (suprimido con tipo 0/B1a) | VERIFICADO (E25) |
| ¿Cómo y cuándo se lee el fotograma? | `0x438c814c` (ReadExecute) tras la exposición; lectura por filas del IMX210 (~61 ms) | VERIFICADO (E25-10/E25-17) |
| ¿Qué funciones gobiernan transiciones/temporizadores/sincronización? | `0x438c828c` (StartExposure), `0x43b1e7f2` (paso con contador), `0x438c74b0` (temporizador tramos), `cap+0x728` (cronómetro 32 µs) | VERIFICADO |

---

## 2. Investigación B — EFCS y Darwin

### 2.1 Arquitectura de comunicación

**BIONZ → Darwin:** mensaje enviado por `0x43901a8c(2, 0x107, ...)` al final de `StartExposure` (`0x438c828c`). Contiene:
- Clase 2, código 0x107
- Datos de tiempo: `cap+0x4b64`, `cap+0x1d8`, `cap+0x56c`, `cap+0x570`

También, antes de `StartExposure`, BIONZ envía el ID `0x0c` (CaptureStart, 22 bytes) a Darwin con `pkt[2..3]` = Tv (`settings+0x162`).

**Darwin → BIONZ:** ocho mensajes mss (IDs `0x0b, 0x0d, 0x0e, 0x10, 0x11, 0x14, 0x15, 0x17`) por la tabla CAIF `0x43fe87f0` → buzón `[0x43e77284]` → `caif_recv` (`0x437db9f0`). El más relevante para la exposición:
- **ID `0x0e` (clase 3, subclase 3):** «ExposureReady» — Darwin termina la espera de sub 9 en BIONZ. Lo envía el MCU Darwin tras cronometrar la exposición con la cortina.

### 2.2 Qué hace Darwin con EFCS activo

| Situación | Órdenes a Darwin | Movimiento mecánico | Sincronización |
|-----------|-----------------|---------------------|----------------|
| **A. Original, obturador mecánico** | ID `0x0c` (CaptureStart) con Tv; Darwin cronometra, mueve P4D/P4E (cortinas), P4C=1 en cada toma | P4D/P4E activan bobinas; cortinas se mueven | Darwin termina con `0x0e` (ExposureReady) |
| **B. Original, EFCS activado** | ID `0x0c` con Tv; mismo mensaje | P4D/P4E **no se mueven** (tipo 0 filtra); P4C sigue | Darwin sigue cronometrando; fin con `0x0e` |
| **C. Silent 3.23 (B1a, tipo 0 + compuerta 0)** | ID `0x0c` con Tv; mismo mensaje | P4D/P4E **no se mueven** (B1a); P4B/P4C siguen | Darwin termina con `0x0e`; BIONZ cronometra (`cap+0x728`) |
| **D. EFCS + Darwin B1a (propuesto)** | ID `0x0c` con Tv + mensaje 0x107 | P4D/P4E **no se mueven** (tipo 0); P4B/P4C siguen | EFCS programa ShutMode 0 + r5; fin sigue siendo `0x0e` de Darwin (o rama de host `74f=0`) |

**Conclusión clave:** EFCS no requiere cambiar la comunicación con Darwin. BIONZ ya envía los mismos mensajes (ID `0x0c` y `0x107`) con o sin EFCS. Darwin con tipo 0/B1a ya suprime el movimiento de P4D/P4E. La diferencia entre EFCS y Silent 3.23 está exclusivamente en el lado BIONZ/IMX210 (ShutMode y r5), no en Darwin.

### 2.3 ¿Es necesario modificar Darwin?

**NO** para velocidades ≤ 1/30 s. Evidencia:
- B1a (`0x1fe6a: 28 46 → 0a e0`) ya suprime P4D/P4E en todas las rutas (E25, E25-02)
- Los ocho mensajes Darwin→BIONZ son idénticos con tipo 0 y con tipo ≠ 0 (E24-05f)
- BIONZ no depende de una respuesta específica de Darwin para el modo de exposición (el modo viene de `record+0x6d`/ShutMode, no de Darwin)
- La espera de fin de sub 9 se satisface con `0x0e` de Darwin; con `cap+0x74f=0` existe una rama de host (temporizador µs) que no necesita a Darwin

Darwin solo necesitaría modificarse si se demostrara que la espera de `0x0e` bloquea indebidamente o que P4B/P4C causan movimiento residual. Ambos son **NO_VERIFICADO**.

---

## 3. Investigación C — EFCS, IMX210 y tiempos de exposición

### 3.1 Cómo EFCS programa el IMX210

EFCS usa `ShutMode = 0` + `r5`:
- `SetExposure` (`vtable+0x28 → 0x436d6f6c`) escribe `blk+0x52` = r5 (integración en líneas) y `blk+0x57` = ShutMode = 0
- ShutMode 0 configura: `cfg1` b2=0, b7=0, b4=0, b6=1; `cfg2` b3=1 (reinicio por filas)
- `SetRead` (`vtable+0x30 → 0x436d7e08`) escribe `blk+0x66..0x6c` = código de posición (no afecta la integración)

### 3.2 Comparación temporal (E25-10, E25-16, E25-17, E25-18)

| Ruta | Mecanismo | Exposición | Uniforme | Velocidad | Estado |
|------|-----------|------------|----------|-----------|--------|
| 1. Normal, mecánico | ShutMode 3, r5=1 | ~64,9 ms (cuadro completo) | Sí (cortina trasera corta) | Todas | VERIFICADO |
| 2. EFCS original | ShutMode 0, r5 del productor | r5 × 15,2 µs | Sí (reinicio por filas) | 1/8000–1/30 | VERIFICADO (código) + T046 (1/4000–1/60) |
| 3. Silent 3.23 sin parche temporal | ShutMode 3, r5=1 | ~64,9 ms | **NO** (sesgo vertical, lectura por filas sin cortina trasera) | 1/4000–1/500 casi fija | VERIFICADO (E25-10/T044) |
| 4. Silent + ShutMode 0 + r5 corregido | ShutMode 0, r5 = 4219 − T/15,2 µs | r5 × 15,2 µs | Sí | 1/8000–1/30 | VERIFICADO (T046/T047 RAM) |
| 5. Híbrido EFCS + Darwin B1a | ShutMode 0, r5 del productor nativo | r5 × 15,2 µs | Sí | 1/8000–1/30 | PROPUESTA (Alternativa B) |

### 3.3 Exposición corta y larga

| Rango | Viable con EFCS + r5 | Mecanismo | Limitación |
|-------|---------------------|-----------|------------|
| 1/8000–1/60 | **SÍ** | ShutMode 0, r5 = 4219 − líneas | Cuantización de línea (−2,7% a 1/8000) |
| 1/30 | **SÍ** | ShutMode 0, r5 = 2025 | Dentro de un cuadro (64,9 ms) |
| 1/15–1/8 | **Parcial** | Productor nativo da svd=0, VTS ampliado (4389/8225 líneas) | Sumidero de VTS en sensor no localizado; sin medida física |
| 1/2–30 s | **Parcial** | Productor nativo da svd ≤ 472 | svd físico no demostrado; sin armado de fin |
| BULB | **NO** | Tramos de un cuadro del host (`0x438c74b0`) | Fin de integración no identificado; emisor de `0x8000` no localizado |

### 3.4 Respuesta a preguntas de Investigación C

| Pregunta | Respuesta | Etiqueta |
|----------|-----------|----------|
| ¿EFCS ofrece temporización aprovechable? | **SÍ:** productor `0x4383fa40` calcula r5 desde Tv real | VERIFICADO |
| ¿Sincronización aprovechar? | Parcial: mensaje `0x107` a Darwin, fin con `0x0e`; rama de host `74f=0` como alternativa | INFERENCIA |
| ¿Finalización de exposición? | No identificada electrónicamente; Darwin `0x0e` es el fin demostrado | NO_VERIFICADO |
| ¿Exposiciones largas > 65 ms? | Productor planifica svd/VTS ampliado pero sin sumidero físico demostrado | NO_VERIFICADO |
| ¿BULB? | Sin mecanismo de fin electrónico identificado | NO_VERIFICADO |

---

## 4. Investigación D — Comparación con A7S y A6300

| Funcionalidad | A6000 (IMX210) | A7S (IMX235) | A6300 | Equivalencia |
|---------------|----------------|--------------|-------|--------------|
| SetExposure | `0x436d6f6c` (vtable+0x28) | `0x436f4168` | — | Mismo contrato param+0/4/6/9 | VERIFICADO |
| SetRead / +0x30 | `0x436d7e08` | `0x436f4a94` | — | Conversión idéntica (`0x436d8a90` ≡ `0x436f5df0`) | VERIFICADO |
| ShutMode 0 | Sí (reinicio por filas) | Sí | — | Mismo comportamiento | VERIFICADO (T046) |
| Productor nativo r5 | `0x4383fa40` | — | — | Solo A6000 tiene este productor identificado | VERIFICADO |
| Armado exposición larga (>1 cuadro) | **No encontrado** | `0x436f43c0` + `obj+0x3dc=2` + `0x43b73044(0xe)` | — | Ausente en A6000 | VERIFICADO (ausencia) |
| Tabla tiempos por modo | 30 filas idénticas | 34×12 B | — | 30 filas idénticas | VERIFICADO |
| Silent Shutter completo | **No** (solo parcial ≤ 1/30) | Sí (selector + bloque de tiempos) | Sí | A6000 carece del selector y armado | VERIFICADO |
| Darwin comunicación | ID `0x0c`, `0x107`; respuesta `0x0e` | Similar | — | Funcionalmente similar | INFERENCIA |

**Conclusión:** La A6000 ya contiene mecanismos suficientes para Silent mejorado ≤ 1/30 s (productor nativo r5, ShutMode 0, tabla de tiempos). No necesita portar subsistemas del A7S. Lo que falta (exposición > 65 ms, BULB) requiere el armado de exposición larga que el A7S tiene y el A6000 no.

---

## 5. Investigación E — Diseño de modificaciones

### 5.1 Evaluación de alternativas

| Alternativa | Descripción | Funciones afectadas | Dificultad | Probabilidad de éxito* |
|-------------|-------------|---------------------|------------|------------------------|
| **A** — Reutilizar EFCS original | Activar selección EFCS con Darwin B1a | `0x43841070`, `0x43842158`, `cap+0x210` | Media | Media |
| **B** — Modificar exclusivamente BIONZ | Inyectar r5 del productor nativo en ruta de foto | `0x438c82a0`/`0x438c82fe` (enganche C3) | Baja | **Alta** |
| **C** — Modificar Darwin | Cambiar comportamiento de Darwin | Darwin `0x1fe66`, `0x20c74` | Alta | Baja (riesgo de recuperación) |
| **D** — Combinada | EFCS + BIONZ + Darwin | Todas las anteriores | Muy alta | Media |
| **E** — Aprovechar flujo Silent actual | Seguir con ShutMode 0 + r5 manual (T050) | BIONZ RAM patch | Baja (pero requiere PC) | Alta (ya demostrado) |

*\*Probabilidad estimada, no garantía.*

### 5.2 Alternativa B (recomendada) — Especificación de implementación

**Dónde modificar:** `av-cam.bin`, en `FUN_438c828c` (`StartExposure`), tras `bl 0x437f8a50` (`0x438c829c`) y antes de `bl 0x436d6320` (`0x438c830c`). Punto de enganche recomendado: `0x438c82a0` (tras `0x43b1e520`, antes de `0x436d6320`), como se determinó en E25-17/E25-18.

**Qué cambiar:**
1. Tras `0x437f8a50`, obtener el registro y los ajustes como hace `0x4383fd6c`:
   - `rec = 0x4383fb6c([cap+0x1c0], [cap+0x1b8])`
   - `set = 0x4383fbc4([cap+0x1c0], [cap+0x1b8])`
2. Copiar el registro a un scratch de 0x158 B (no modificar el global).
3. Ejecutar `0x4383fa40(scratch, set)` — usa la aritmética de Sony, sin reimplementar.
4. Leer `r5 = [scratch+0x64]`, `sm = [scratch+0x6d]`.
5. Si `r5 >= 2` y el modo es foto y `cap+0x4b9c == 0` y `0x43a12c64()` no es 2/3 (no bloque forzado):
   - Escribir `[cap+0x64c] = r5` (param+0 = r5)
   - Escribir `[cap+0x655] = 0` (param+9 = ShutMode 0)
6. Si no, no escribir nada (comportamiento normal).
7. Restaurar registros y volver a `0x438c82a4`.

**Por qué produce el efecto esperado:**
- `r5 = 4219 − líneas` da exposición `E = r5 × 15,2 µs` uniforme por filas (T046/T047 verificados)
- `ShutMode = 0` selecciona reinicio por filas (no el reinicio global + lectura de ShutMode 3)
- El productor nativo ya está cableado y probado; no hay que reimplementar aritmética
- Darwin B1a queda intacto (sin riesgo de recuperación)

**Validación offline:**
- Emulación del productor `0x4383fa40` contra T047 (ya hecha, ±1 línea)
- Comparación de bytes `cap+0x64c` antes/después del enganche (diferencial E25-18: solo `0x64c–0x64d` difieren)
- Pruebas de regresión: `tests/test_e25_14_exposicion.py`, `test_e25_15_shutmode.py`, `test_e25_16_r5_autonomo.py` (59 pruebas verdes)

**Prueba en RAM (controlada, solo con autorización):**
- Enganche en RAM en `0x438c82a0` con guardián que revierte si falla
- Una foto de 4 s, medir `cap+0x64c` y `cap+0x655`
- Reversión verificada (apagado borra la cueva de RAM)

**Reversión:** Restaurar los 4 bytes originales del enganche; `cap+0x64c` se recompone en la siguiente foto (`0x4383fd6c` lo reescribe desde `record`).

**Evidencia que falta antes de firmware permanente:**
- Lectura física de `record+0x20` (VTS real: 4219 vs 4266) — E25-19 fase A
- Prueba física de exposición uniforme ±5% a 1/4000, 1/250, 1/60 — T052 fase B
- Comprobación de que Live View/AF/vídeo no se ven afectados (el enganche solo actúa en paso 0 de foto)

### 5.3 Alternativa A (reutilizar EFCS original)

Descartada como primera opción porque:
- EFCS es un ajuste de menú separado de Silent; reutilizarlo altera su semántica
- La compuerta `cap+0x11b0` del constructor normal impide que el productor r5 se use en la foto normal
- No se ha localizado el escritor de `cap+0x11b0` ni la semántica exacta de la compuerta

### 5.4 Alternativa C (modificar Darwin)

Descartada porque:
- E24-04: no hay recuperación independiente de Darwin demostrada
- B1a ya suprime P4D/P4E; no hay evidencia de que Darwin bloquee el flujo EFCS
- Cualquier parche de Darwin arriesga la vía de reinstalación (actualizador USB)

---

## 6. Investigación F — Validación y prototipos

### 6.1 Validación offline realizada (REA)

| Prueba | Resultado | Evidencia |
|--------|-----------|-----------|
| Desensamblado de 9 funciones EFCS | VERIFICADO | `analysis/efcs-reia/evidence/` |
| Pseudocódigo del productor r5 | VERIFICADO | `0x4383fa40_pseudo.txt` |
| Emulación del productor vs T047 | ±1 línea | `analysis/e25-16/emulacion.json` |
| Diferencial `cap` (solo 0x64c difiere) | VERIFICADO | `analysis/e25-18/diferencial.json` |
| Pruebas de regresión (59) | Todas verdes | `tests/test_e25_14/15/16_*.py` |
| SHA-256 de `av-cam.bin` | Coincide | `b60c845c…e56bb9` |

### 6.2 Plan de pruebas offline pendientes

1. Emular `0x438c828c` completo con el enganche C3, verificar que `cap+0x64c` recibe r5 correcto
2. Verificar que el enganche no afecta a `cap+0x650` (svd se restaura en `0x438c8334`)
3. Verificar que Live View/AF no entran en el enganche (`cap+0x4b9c != 0` en esos modos)
4. Comparar secuencia de llamadas con y sin enganche (debe ser idéntica salvo `cap+0x64c/0x655`)

### 6.3 Prueba física propuesta (protocolo separado, requiere autorización)

**T052 fase A (solo lectura):** Leer `record+0x20`, `+0xc`, `+0x1c`, `settings+0x4b8`, `cap+0x11b0` en fotos a 1/4000, 1/250, 1/60. Criterio: si `record+0x20 == 4219`, el nativo da la tabla de E25-16 §5.2.

**T052 fase B (RAM, C3):** Escribir `cap+0x64c` (r5) y `cap+0x655` (0) entre `0x437f8a50` y `0x436d6320`. Criterios de éxito:
- r5 calculado = r5 nativo (±1 línea)
- Exposición media dentro de ±5% del objetivo en 1/4000, 1/250, 1/60
- Uniformidad por filas dentro de ±5%
- Live/Video/AF sin cambios; reversión verificada

**No se prueba:** 1/15, bulb, 30 s (fuera del alcance de un cuadro).

---

## 7. Respuesta a las 12 preguntas de la misión

| # | Pregunta | Respuesta | Etiqueta |
|---|----------|-----------|----------|
| 1 | ¿Cómo funciona EFCS completo en la A6000? | Productor nativo r5 (`0x4383fa40`) + constructor EFCS (`0x43841070`) + selección de clase (`0x43842158`) + programación IMX210 (`0x438c828c` → SetExposure/SetRead) | VERIFICADO |
| 2 | ¿Qué hace Darwin específicamente cuando EFCS está activo? | Recibe ID `0x0c` y mensaje `0x107` de BIONZ; cronometra; responde `0x0e` (ExposureReady). Con tipo 0/B1a no mueve P4D/P4E. No hay diferencia con o sin EFCS en el lado Darwin. | VERIFICADO (E24-05) + INFERENCIA |
| 3 | ¿Qué diferencias reales existen entre EFCS y Silent 3.23? | EFCS: ShutMode 0 + r5 calculado (uniforme, sigue velocidad). Silent 3.23: ShutMode 3 + r5=1 (sesgo vertical, ~64 ms fijo). Mismo Darwin, mismo mecanismo desactivado. | VERIFICADO (E25-10/T046) |
| 4 | ¿Qué partes de EFCS pueden reutilizarse sin mover el obturador? | Productor nativo r5 (`0x4383fa40`), SetExposure con ShutMode 0, mensaje `0x107` a Darwin. Todo el flujo BIONZ/IMX210. | VERIFICADO |
| 5 | ¿Qué partes requieren control electrónico del IMX210? | ShutMode 0 (reinicio por filas) y r5 (tiempo de integración) vía SetExposure blk+0x52 | VERIFICADO |
| 6 | ¿Cómo se coordinan el inicio y el fin de exposición? | Inicio: SetExposure/SetRead/Execute(1) en BIONZ. Fin: Darwin `0x0e` (ExposureReady) o rama de host `74f=0` (temporizador µs). | VERIFICADO (inicio) / INFERENCIA (fin) |
| 7 | ¿Puede EFCS contribuir a corregir los problemas de temporización actuales? | SÍ: el productor nativo `0x4383fa40` ya calcula r5 desde Tv real; solo falta ejecutarlo en la ruta de foto | VERIFICADO |
| 8 | ¿Es necesaria alguna modificación adicional de Darwin? | NO para ≤ 1/30 s. B1a ya suprime P4D/P4E. | INFERENCIA (basada en E24-05/E25) |
| 9 | ¿Dónde está el punto mínimo de modificación de BIONZ? | `0x438c82a0`/`0x438c82fe` en `FUN_438c828c`, tras `0x437f8a50` y antes de `0x436d6320` (enganche C3) | VERIFICADO |
| 10 | ¿Qué ocurre con exposiciones largas y BULB? | > 65 ms: productor planifica svd/VTS ampliado pero sin sumidero físico demostrado. BULB: sin fin de integración identificado. | NO_VERIFICADO |
| 11 | ¿Qué se puede demostrar offline y qué requiere físico? | Offline: mapa EFCS, productor r5, emulación, diferencial de cap. Físico: VTS real, exposición uniforme medida, fin de integración. | VERIFICADO / NO_VERIFICADO |
| 12 | ¿Cuál es la implementación más prometedora? | Alternativa B: enganche C3 en `0x438c82a0`, r5 del productor nativo, ShutMode 0, Darwin B1a intacto. Probabilidad estimada: ALTA. | ESTIMACIÓN |

---

## 8. Conclusión y recomendación

**La EFCS original de Sony sí aporta una ventaja concreta para el Silent Shutter:** contiene el productor nativo de `r5` (`0x4383fa40`) que calcula la integración electrónica a partir del Tv real, ya usado por el constructor EFCS y disponible (pero con compuerta cerrada) en el constructor normal.

**Recomendación:** Implementar la **Alternativa B** — modificación mínima de BIONZ exclusivamente, con enganche en `0x438c82a0`/`0x438c82fe` que ejecute `0x4383fa40` sobre un scratch y escriba `cap+0x64c` (r5) y `cap+0x655` (ShutMode=0) solo en el paso 0 de foto. Mantener Darwin 3.23 (B1a) intacto.

Esto da:
- Capturas silenciosas (mecanismo desactivado por B1a)
- Resolución completa del sensor
- Exposición uniforme que respeta la velocidad seleccionada (1/8000–1/30)
- Sincronización con el flujo original (mismo mensaje `0x107` a Darwin, mismo fin `0x0e`)
- No dependencia de modificaciones adicionales de Darwin
- Ruta reversible y verificable offline

**No se recomienda** modificar Darwin (riesgo de recuperación sin beneficio demostrado) ni perseguir exposiciones > 65 ms o BULB sin el armado de exposición larga que el A6000 no tiene.

---

## 9. Índice de evidencia

| Archivo | Contenido |
|---------|-----------|
| `analysis/efcs-reia/evidence/0x43841070_pseudo.txt` | Pseudocódigo constructor EFCS (18,377 chars) |
| `analysis/efcs-reia/evidence/0x43842158_pseudo.txt` | Pseudocódigo selección de clase (4,436 chars) |
| `analysis/efcs-reia/evidence/0x4383fa40_pseudo.txt` | Pseudocódigo productor nativo r5 (1,521 chars) |
| `analysis/efcs-reia/evidence/0x4383fd6c_pseudo.txt` | Pseudocódigo registro→exposición |
| `analysis/efcs-reia/evidence/0x437f8a50_pseudo.txt` | Pseudocódigo construcción de parámetros |
| `analysis/efcs-reia/evidence/0x438c828c_pseudo.txt` | Pseudocódigo programación de exposición |
| `analysis/efcs-reia/evidence/0x43901a8c_pseudo.txt` | Pseudocódigo mensaje a Darwin |
| `analysis/efcs-reia/evidence/0x436d6118_pseudo.txt` | Getter de objeto imager |
| `analysis/efcs-reia/evidence/0x43a12c64_pseudo.txt` | Selector de modo de captura |
| `analysis/efcs-reia/evidence/0x43a12ca8_pseudo.txt` | Predicado de cuadro extra |
| `analysis/efcs-reia/evidence/0x437b21b8_pseudo.txt` | Planificador VTS |
| `analysis/efcs-reia/evidence/0x43840150_pseudo.txt` | Constructor bloque +0x30 |
| `analysis/efcs-reia/evidence/*_xrefs.json` | Referencias cruzadas de cada función |
| `analysis/efcs-reia/evidence/*_analyze.json` | Análisis completo de cada función |
| `tests/test_e25_14_exposicion.py` | 13 pruebas IMX235/IMX210 |
| `tests/test_e25_15_shutmode.py` | 17 pruebas ShutMode 0 |
| `tests/test_e25_16_r5_autonomo.py` | 29 pruebas productor nativo |

---

## 10. Actualización de pendientes

Este informe cierra parcialmente E25-12 (arreglo de exposición del silencioso) al identificar el productor nativo y el punto de enganche. Abre la necesidad de:
- E25-19 fase A: leer `record+0x20` (VTS real) — pendiente físico
- T052 fase B: prueba RAM de C3 — pendiente físico con autorización

No se modifica firmware, no se flashea, no se interviene físicamente la cámara en esta investigación. Toda la evidencia es estática (REA sobre binarios originales) o emulación offline.
