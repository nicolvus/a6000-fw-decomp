# Inicializador LIRO 0x437EBED8 — sesión 18 (hilo principal, en curso)

Clasificación: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO. No se afirma que SilentShutter funcione.

## 0. Corrección de base de carga

La base de carga LIRO usada por los scripts del proyecto (`scripts/ghidra_dec.sh`, `QuerySilentLiro.java`) es **`0x43541000`**, no `0x43540000` como quedó anotado en el resumen de sesión 17 (desfase de una página, `0x1000`). Verificado por búsqueda de patrón de bytes exacto (`push {r4,r5,r6,lr}; mov r4,r0; mov r0,r1; ldr r6,[pc,#0x94]; bl ...`) en `av-cam.bin` contra el desensamblado de `analysis/av-cam-analysis-view.elf`, que coincidieron exactamente en `0x43541000`. **No es un error del proyecto — los scripts ya usaban la base correcta; el error era solo de transcripción en el resumen de la sesión anterior.**

## 1. 0x437EBED8 es un inicializador maestro de tablas de fila de 20 bytes (VERIFICADO)

Decompilado con `scripts/ghidra_dec.sh`. La función, tras `push {r4,r5,r6,lr}`, itera sobre **al menos 9 tablas base distintas** (`DAT_44022970`, `DAT_4402559c`, `DAT_44020100`, `DAT_4401f96c`, `DAT_44022c18`, y otras no listadas por brevedad, incluyendo **`DAT_44022934`** — el mismo GOT slot que apunta a la tabla del selector de captura `0x43edccf8` identificada en sesión 17). Para cada tabla, llama repetidamente a `FUN_43afb46a(filaPtr, descriptorGOT)` con `filaPtr` en incrementos de `0x14` (20 bytes): `0x0, 0x14, 0x28, 0x3c, 0x50, 0x64, 0x78, 0x8c, 0xa0, 0xb4, 0xc8, 0xdc, 0xf0, 0x104, 0x118, ...` (algunas tablas tienen 5 filas, otras hasta 15+).

## 2. FUN_43afb46a → FUN_437de944: patrón constructor (VERIFICADO)

```c
void FUN_437de944(undefined4 *param_1, undefined4 param_2) {
    FUN_43acabf4();
    param_1[2] = param_2;          // offset +8: puntero/descriptor
    *param_1 = DAT_44020894;       // offset +0: vptr constante compartido
    param_1[1] = 0;                // offset +4: estado inicial = 0
}
```

Cada fila de 20 bytes se inicializa como un objeto con vptr común (`DAT_44020894`), estado cero, y un puntero en `+8` tomado de un slot GOT específico de esa fila. **Esto coincide exactamente con el patrón de objeto `LifeCycle` (0x14 bytes) descrito por Claude A en sesión 17** (vptr + estado + payload), aunque aquí vive en el binario LIRO monolítico, no en `libObj.so`.

## 3. La tabla del selector de captura SÍ es inicializada aquí (VERIFICADO — cierra parcialmente el blocker de sesión 17)

`DAT_44022934` (GOT del selector `0x437eabfc`) aparece literalmente en `0x437ebed8`. Las 15 filas de esa tabla (offsets `0x0` a `0x118`) se pueblan con descriptores GOT que, resueltos, son **punteros Thumb a funciones reales y contiguas** (`0x43b1bc0d` .. `0x43b1c097`, paso ~0x52 bytes):

| Offset fila | GOT descriptor | Función real |
|---|---|---|
| `0x00` | `0x440236b8` | `0x43b1bc0d` |
| `0x14` | `0x440223a4` | `0x43b1bc25` |
| `0x28` | `0x44026110` | `0x43b1bc71` |
| `0x3c` | `0x44021940` | `0x43b1bcc7` |
| `0x50` | `0x440241a0` | `0x43b1bd13` |
| `0x64` | `0x440268e0` | `0x43b1bd5f` |
| `0x78` | `0x44020b28` | `0x43b1bdb5` |
| `0x8c` | `0x44025d08` | `0x43b1be01` |
| **`0xa0`** | `0x44023a6c` | `0x43b1be37` |
| **`0xb4`** | `0x440265b8` | `0x43b1be99` |
| **`0xc8`** | `0x4401f664` | `0x43b1bf05` |
| **`0xdc`** | `0x44023054` | `0x43b1bf67` |
| `0xf0` | `0x44026070` | `0x43b1bfc9` |
| **`0x104`** | `0x44022dd4` | `0x43b1c035` |
| `0x118` | `0x44023c3c` | `0x43b1c097` |

**Corrección sobre el recuerdo de sesión 17**: recalculando `iVar7*0x14` con `iVar7 ∈ {8,0xa,0xb,0xd}` (lógica real del selector `0x437eabfc`), los offsets dinámicamente seleccionables son **`0xa0, 0xc8, 0xdc, 0x104`** (marcados en negrita), no los que se citaron de memoria en el resumen de compactación. La fila **`0xb4`** se alcanza por una rama directa separada (primera condición de la función), no por el cálculo `iVar7*0x14`.

## 4. Decompilación de la fila 0xb4 (0x43b1be99) — INFERENCIA fuerte, sin marca Silent

El trampolín de la fila `0xb4` opera sobre **los mismos campos del struct de petición de captura** que usa el propio selector (`+0x4b70`, `+0x754`, `+0x4d8`, `+0x4a7c`) — confirma que es un manejador de captura real, no un stub muerto. Su cuerpo escribe bytes en offsets `+0x23..+0x27` de un registro tras una llamada a `FUN_43ae9226(..., 0x9400, ...)`, patrón compatible con metadatos tipo EXIF/lente. **No contiene ninguna marca de modo Silent/EFCS** — consistente con la conclusión de sesión 17 de que el selector y sus filas no tienen un modo electrónico explícito. Las filas `0xa0`, `0xc8`, `0xdc`, `0x104` (seleccionables dinámicamente) no se han decompilado aún en esta sesión — **NO VERIFICADO su contenido**, pendiente para continuación de este hilo.

## 5. Relevancia para el bloqueo de sesión 17

Esto **no demuestra** un modo Silent, pero **cierra metodológicamente** el blocker "la tabla es BSS, su contenido no es recuperable estáticamente": el contenido SÍ es recuperable — no leyendo la tabla (que en efecto es BSS en reposo), sino **leyendo su inicializador y resolviendo los punteros GOT que usa**, los cuales sí viven en secciones estáticas de solo lectura. Esta técnica es aplicable a cualquier otra tabla de fila de 20 bytes del binario LIRO, incluidas las que Claude D investigue en topologías dinámicas.

## 6. Estructura real de las entradas de fila: trampolines de 4 bytes (VERIFICADO)

Desensamblado crudo (`llvm-objdump`, sin tocar el proyecto Ghidra compartido — evita el conflicto de recursos con los 4 agentes Claude que lo usan en paralelo) de las direcciones de función de las filas `0xa0` (`0x43b1be37`) y `0xb4` (`0x43b1be99`): ambas son trampolines idénticos de 4 bytes — `push {r2}; b <destino lejano>` — que saltan a una región densa de implementaciones reales alrededor de `0x43b1c2c9`–`0x43b1c32b`. Esto confirma que la decompilación de Ghidra de la fila `0xb4` (§4) mostraba ya la lógica real (Ghidra sigue el salto de forma transparente), no un stub vacío. **No son filas muertas**: cada una salta a un manejador distinto y real.

**Incidente de recursos (declarado)**: al intentar decompilar las filas dinámicas `0xa0/0xc8/0xdc/0x104` con `scripts/ghidra_dec.sh` mientras Claude A y Claude C corrían en paralelo contra el mismo proyecto `analysis/ghidra/silent-liro`, Ghidra devolvió `ContextChangeException: Context register change conflicts with one or more instructions` — consistente con la regla de coordinación "no Ghidra simultáneo sobre el mismo binario". Dejé de usar Ghidra directamente desde este hilo y pasé a `llvm-objdump` puro (sin bloqueo de proyecto) para el resto de esta verificación.

## 6bis. Búsqueda de cadenas "Silent"/EncodeStill en LIRO (DESCARTADO — falso positivo de dominio)

`strings -a` sobre `av-cam.bin` completo: las únicas coincidencias de "SILENT" pertenecen al dominio de **sincronización de audio** (`[ENCAUDSYNC]... SILENT = %x`, `seamlessSilentAauNum`) — relacionado con codificación de audio continuo/sin costuras (AAU = Audio Access Unit), **no con el obturador electrónico**. Coincidencia de palabra, no de concepto. **Ninguna cadena `ObjCamera`, `ObjEffect`, `EncodeStill` ni `CBID_ENCODE_STILL` existe en el binario LIRO** — confirma que esos símbolos/diagnósticos viven exclusivamente en `libObj.so`/`libmpr.so`, no en LIRO. DESCARTADO como pista en este binario.

## 7. Próximo paso de este hilo (pendiente, delegado por recursos a Claude A/C vía esta misma técnica)

Decompilar con Ghidra (una vez liberen el proyecto) las implementaciones reales en `~0x43b1c2c9` y `~0x43b1c32b` (destinos de los trampolines 0xa0/0xb4) y las de `0xc8`/`0x104`, y buscar en cualquiera de las ~9 tablas registradas por `0x437ebed8` alguna fila cuyo callback contenga referencias a `ObjCamera`, `EncodeStill`, `CBID_ENCODE_STILL` o cadenas de diagnóstico relacionadas.
