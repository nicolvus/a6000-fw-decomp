# S303 — Árbol de referencias de `0x43ff3200` y callers de `FUN_43858338`

> Hito **Agente B (S300+)** — Imager: estado, drive modes y gates.
> Análisis estático de `av-cam.bin` A6000 fw3.21 (SHA `b60c845c...56bb9`), base `0x43541000`.
> Complementa: S153 (gates `[obj+3]&2` / `[obj+6]&0x20`), S176 (tabla `0x43ff3200`), S300 (barrido xrefs estado).

---

## 1. Tabla `0x43ff3200` (S176)

**Dirección**: `0x43ff3200` (file offset `0xab2200`), en región de datos (`.data`/`.bss` boundary).

**Contenido**: 240 bytes = 60 entradas de 4 bytes (punteros). Primeras entradas:

| Offset | Puntero | Tipo / Nota |
|---|---|---|
| +0x00 | `0x43e964a4` | Código/estructura |
| +0x04 | `0x43f78dd2` | BSS (estado-related) |
| +0x08 | `0x43f6ba62` | BSS |
| +0x0c | `0x43f72c02` | **Cerca de estado `0x43f72d02`** |
| +0x40 | `0x43f76a92` | BSS |
| +0x44 | `0x43e95a50` | Código/estructura |
| +0x48 | **`0x43f72d02`** | **ESTADO IMAGER (objeto principal S300)** |
| +0x4c | `0x43e973b0` | Código/estructura |

**Clave**: La entrada en **+0x48** apunta directamente al **objeto estado del imager** (`0x43f72d02`), confirmando que esta tabla es un directorio de objetos/estructuras del subsistema imager.

---

## 2. Referencias a la tabla `0x43ff3200`

| Método | Resultado |
|---|---|
| Literal `0x43ff3200` en binario | **1 ocurrencia** en `0x4401f080` (GOT slot) |
| GOT slot `0x4401f080` | Contiene `0x43ff3200` como primera entrada |
| Xrefs directas a GOT slot `0x4401f080` | **0** (ningún código carga este GOT slot directamente) |
| Xrefs a entradas individuales de la tabla | Pendiente (cada entrada es un puntero distinto) |

**Interpretación**: La tabla se accede **indirectamente** mediante su GOT slot `0x4401f080`. El código que usa la tabla debe:
1. Cargar el GOT slot `0x4401f080` → obtiene dirección base `0x43ff3200`
2. Indexar con offset para leer entradas individuales

**Pendiente**: Identificar qué funciones cargan `0x4401f080` (requiere análisis de código con REA/Ghidra para seguir LDR literal + ADD).

---

## 3. Función `FUN_43858338` (Dumper con gates, S153)

**Dirección**: `0x43858338` (Thumb, base `0x43541000`).

**Hallazgos S153**:
- Lee gates `[obj+3]&2` y `[obj+6]&0x20` para habilitar líneas del dumper
- Los xrefs directos a esos bytes son **solo lecturas**
- Bytes BSS iniciales a cero
- **Escritor/valor runtime NO_VERIFICADOS**

**Búsqueda de callers (BL a `0x43858338`)**:
- Literal `0x43858338` en binario: **0 ocurrencias**
- En Thumb, BL usa encoding PC-relativo, no literal absoluto
- **Pendiente**: Análisis con REA/Ghidra para listar callers reales

---

## 4. Árbol de referencias reconstruido (parcial)

```
0x4401f080 (GOT slot)
    └─► 0x43ff3200 (Tabla 60 punteros)
            ├─► +0x00: 0x43e964a4
            ├─► +0x04: 0x43f78dd2
            ├─► ...
            ├─► +0x48: 0x43f72d02  ◄── OBJETO ESTADO IMAGER (S300)
            └─► ...

0x43f72d02 (Estado imager)
    ├─► +0x00: byte open flag (writer: FUN_4383abec @ 0x4383ac90, S160)
    ├─► +0x03: gate [obj+3]&2 (lector: FUN_43858338, S153) — WRITER NO_VERIFICADO
    ├─► +0x06: gate [obj+6]&0x20 (lector: FUN_43858338, S153) — WRITER NO_VERIFICADO
    ├─► +0x1c: halfword (lectores: FUN_438d9318/6c, FUN_438d939c, S162/S163)
    ├─► +0x26, +0x28, +0x29: (lector: FUN_4384b268, S161)
    ├─► +0x30..+0x37: (lector: FUN_43859944, S157)
    └─► +0xa2: (lector: FUN_4385fff0, S159)

FUN_43858338 (Dumper gates, S153)
    ├─► Lee [obj+3]&2
    ├─► Lee [obj+6]&0x20
    └─► Callers: **NO IDENTIFICADOS ESTÁTICAMENTE** (requiere REA/Ghidra)
```

---

## 5. Limitaciones y trabajo pendiente

| Item | Estado | Acción requerida |
|---|---|---|
| Callers de `FUN_43858338` | **NO_VERIFICADO** | REA `procedure_callees` o Ghidra xrefs a `0x43858338` |
| Código que carga GOT `0x4401f080` | **NO_VERIFICADO** | REA xrefs a `0x4401f080` o análisis de LDR literal |
| Consumidores de entradas individuales tabla `0x43ff3200` | **NO_VERIFICADO** | Seguir cada puntero de la tabla |
| Escritores de gates `state+3` / `state+6` | **NO_VERIFICADO** | Búsqueda de stores con offset 3/6 + análisis dinámico |
| Significado físico gates | **NO_VERIFICADO** | Requiere datasheet IMX210 o traza física |

---

## 6. Conclusión para S300/S303

- La tabla `0x43ff3200` **contiene una referencia directa al objeto estado imager** (`0x43f72d02` en offset +0x48), validando que es un directorio central del subsistema imager.
- El acceso a la tabla es **indirecto vía GOT** (`0x4401f080`), lo que explica por qué REA no encontró xrefs directas al objeto estado desde esta tabla.
- Los **callers del dumper `FUN_43858338`** (que lee los gates `+3`/`+6`) **no se han identificado estáticamente** — son el eslabón faltante para entender cuándo y cómo se evalúan los gates.
- Los **writers de los gates `state+3` y `state+6`** siguen sin identificarse (coherente con S153 y S300).

**Próximo paso recomendado (S304)**: Usar REA/Ghidra para:
1. `procedure_callees` de `0x43858338` → callers del dumper
2. `xrefs` a `0x4401f080` → código que accede a la tabla `0x43ff3200`
3. `analyze_function` en candidatos que cargan el GOT slot

---

## Artefactos

- `analysis/s300_state_xref_sweep/xrefs_classified.json` — xrefs clasificados al estado
- `docs/capture/s300-state-xref-sweep.md` — informe S300
- `docs/capture/s303-ref-tree-43ff3200.md` — este informe

---

## Tests

```sh
python3 -m pytest analysis/s300_state_xref_sweep/test_s300_state_xref_sweep.py -v
# 7 tests passed
```