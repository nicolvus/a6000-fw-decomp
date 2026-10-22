# S300 — Barrido de xrefs al estado del imager `0x43f72d02` (A6000 fw3.21)

> Hito **Agente B (S300+)** — Imager: estado, drive modes y gates.
> Análisis estático de `av-cam.bin` A6000 fw3.21 (SHA `b60c845c...56bb9`), base `0x43541000`.
> Complementa: S153–S176 (lectores/escritores estado IMX210), CURRENT.md.

---

## Resumen del barrido

**Xrefs a `0x43f72d02` (objeto estado imager) encontradas por REA:** 15 direcciones

| # | Dirección | Función / Contexto | Clasificación | Evidencia previa |
|---|---|---|---|---|
| 1 | `0x4383643e` | `FUN_438363cc` (S154) | **Lectura GOT + propagación puntero** | Carga slot `0x4401f990`, lee campos `+0x38..+0x3b` |
| 2 | `0x4383ace8` | `FUN_4383abec` (S160) | **Escritura `state+0`** | `strb r3,[r2]` en `0x4383ac90` → WRITE a `0x43f72d02+0` |
| 3 | `0x4384cb5e` | `FUN_4384b268` (S161) | **Spill puntero a stack** | `str r3,[sp,#0x20]` en `0x4384cb0a` |
| 4 | `0x4384cb62` | `FUN_4384b268` (S161) | **Lectura campos** | Lee `+0x26/+0x28/+0x29`, stores a otros objetos |
| 5 | `0x43857fe8` | `0x43857f90` (S155) | **Lectura `state+0` → predicado** | Carga byte `+0`, devuelve predicado |
| 6 | `0x43858008` | `0x43857fb0` (S155) | **Lectura `state+0` → predicado** | Carga byte `+0`, devuelve predicado |
| 7 | `0x4385818c` | `0x43858134` (S155) | **Lectura `state+4`, `state+0x1c`** | Carga puntero GOT, lee `+4` y `+0x1c`, stores a otros |
| 8 | `0x438599ac` | `FUN_43859944` (S157) | **Lector snapshot** | Lee `+5`, condicional `+0xf`, vuelca a buffer, escribe global distinto |
| 9 | `0x4385b2c0` | `FUN_4385b234` (S158) | **Spill puntero a stack** | `str r3,[sp,#0x20]` en `0x4385b268` |
| 10 | `0x43860074` | `FUN_4385fff0` (S159) | **Spill + lecturas** | `str r3,[sp,#0x1c]` en `0x4386001c`; lee `+0/+0x1c/+0xa2` |
| 11 | `0x4386016a` | `FUN_4385fff0` (S159) | **Lecturas / stores a otros** | Stores a otros destinos, no gates `+3/+6` |
| 12 | `0x4386055e` | `FUN_4385fff0` (S159) | **Lecturas / stores a otros** | Stores a otros destinos |
| 13 | `0x438d9396` | `FUN_438d939c` (S163) | **Lector `state+0x1c/+0x1e`** | Halfword `+0x1c`, byte `+0x1e`; defaults 3/4 si cero |
| 14 | `0x438d93d0` | `FUN_438d9318/438d936c` (S162) | **Lectores `state+0x1c`** | Halfword `+0x1c` → escribe a `0x43f7c702`/`0x43f7c704` |
| 15 | `0x43ff32a0` | Tabla `0x43ff3200` (S176) | **Referencia datos (tabla)** | Entrada en tabla de 0x43ff3200; no es código |

---

## Clasificación por tipo de acceso

| Tipo | Cantidad | Direcciones |
|---|---:|---|
| **Spill puntero a stack** | 4 | `0x4384cb5e`, `0x4385b2c0`, `0x43860074`, `0x4386016a`/`0x4386055e` |
| **Lectura campo `state+0` (byte open flag)** | 3 | `0x4383ace8` (write), `0x43857fe8`, `0x43858008` (read predicado) |
| **Lectura campos varios (`+4`, `+0x1c`, `+0x1e`, `+5`, `+0xa2`, `+0x26`, `+0x28`, `+0x29`, `+0x38..+0x3b`)** | 6 | `0x4383643e`, `0x4384cb62`, `0x4385818c`, `0x438599ac`, `0x43860074`, `0x438d9396`, `0x438d93d0` |
| **Escritura a `state+0`** | 1 | `0x4383ace8` (`0x4383ac90`) |
| **Referencia datos (tabla)** | 1 | `0x43ff32a0` |
| **Escritura a gates `state+3` / `state+6`** | **0** | — |

---

## Veredicto sobre writers de gates `+3` y `+6` (S153)

**NO SE ENCONTRARON writers a `state+3` (`0x43f72d05`) ni `state+6` (`0x43f72d08`) en el barrido completo de xrefs al objeto base.**

- Búsqueda de literales `0x43f72d05` / `0x43f72d08`: **0 ocurrencias** (verificación por bytes).
- Búsqueda de instrucciones Thumb `strb/strh/str` con offset inmediato 3 o 6: **centenas de ocurrencias genéricas**, ninguna en las 14 funciones que acceden al objeto estado (verificadas manualmente en S153–S176).
- S153 ya estableció: "los xrefs directos a esos bytes son lecturas y los bytes BSS iniciales están a cero. **Escritor/valor runtime NO_VERIFICADOS**".

**Conclusión**: Los gates `[obj+3]&2` y `[obj+6]&0x20` que habilitan líneas del dumper en `FUN_43858338` (S153) **no tienen escritor identificado en el firmware estático**. Su valor en runtime es desconocido (puede venir de inicialización dinámica, otro hilo, o hardware).

---

## Limitaciones del barrido

1. **Cobertura REA incompleta**: "consulta vacía no prueba ausencia". Funciones Thumb no sembradas a mano pueden no aparecer en xrefs.
2. **Accesos indirectos/por alias**: Escrituras vía puntero copiado, índice calculado, o DMA no serían capturadas por xrefs al objeto base.
3. **Inicialización BSS**: El objeto está en `.bss` (cero en blob); writers que corren antes de `main` o en rutinas de init no analizadas pueden setear gates.
4. **Tabla `0x43ff3200`**: La entrada `0x43ff32a0` apunta a esta tabla (pendiente S176); sus referencias al vector/GOT base no fueron observadas como xrefs exactas.

---

## Artefactos

- `analysis/s300_state_xref_sweep/xrefs_classified.json` — tabla estructurada (JSON adjunto)
- `docs/capture/s300-state-xref-sweep.md` — este informe

```json
{
  "binary": "av-cam.bin A6000 fw3.21",
  "sha256": "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9",
  "base": "0x43541000",
  "state_object": "0x43f72d02",
  "got_slot": "0x4401f990",
  "xrefs_total": 15,
  "classified": [
    {"addr": "0x4383643e", "func": "FUN_438363cc", "type": "GOT_load + field_read", "fields": ["+0x38..+0x3b"], "evidence": "S154"},
    {"addr": "0x4383ace8", "func": "FUN_4383abec", "type": "write_state+0", "fields": ["+0"], "evidence": "S160"},
    {"addr": "0x4384cb5e", "func": "FUN_4384b268", "type": "stack_spill", "fields": [], "evidence": "S161"},
    {"addr": "0x4384cb62", "func": "FUN_4384b268", "type": "field_read", "fields": ["+0x26", "+0x28", "+0x29"], "evidence": "S161"},
    {"addr": "0x43857fe8", "func": "0x43857f90", "type": "read_state+0_predicate", "fields": ["+0"], "evidence": "S155"},
    {"addr": "0x43858008", "func": "0x43857fb0", "type": "read_state+0_predicate", "fields": ["+0"], "evidence": "S155"},
    {"addr": "0x4385818c", "func": "0x43858134", "type": "field_read", "fields": ["+4", "+0x1c"], "evidence": "S155"},
    {"addr": "0x438599ac", "func": "FUN_43859944", "type": "snapshot_reader", "fields": ["+5", "+0xf"], "evidence": "S157"},
    {"addr": "0x4385b2c0", "func": "FUN_4385b234", "type": "stack_spill", "fields": [], "evidence": "S158"},
    {"addr": "0x43860074", "func": "FUN_4385fff0", "type": "stack_spill + field_read", "fields": ["+0", "+0x1c", "+0xa2"], "evidence": "S159"},
    {"addr": "0x4386016a", "func": "FUN_4385fff0", "type": "field_read + other_stores", "fields": ["various"], "evidence": "S159"},
    {"addr": "0x4386055e", "func": "FUN_4385fff0", "type": "field_read + other_stores", "fields": ["various"], "evidence": "S159"},
    {"addr": "0x438d9396", "func": "FUN_438d939c", "type": "field_read", "fields": ["+0x1c", "+0x1e"], "evidence": "S163"},
    {"addr": "0x438d93d0", "func": "FUN_438d9318/6c", "type": "field_read", "fields": ["+0x1c"], "evidence": "S162"},
    {"addr": "0x43ff32a0", "func": "data_table_0x43ff3200", "type": "data_reference", "fields": [], "evidence": "S176"}
  ],
  "gates_writers": {
    "state_plus_3": "NO_ENCONTRADO",
    "state_plus_6": "NO_ENCONTRADO",
    "verdict": "NO_VERIFICADO (runtime desconocido)"
  }
}
```

---

## Siguiente (S301)

Barrido equivalente en **A7S fw3.20** (objeto estado IMX235 equivalente) y tabla de diferencias A7S vs A6000.