# Backlog del Agente B — Imager: estado, drive modes y gates (S300+)

Sesiones asignadas: S300–S399. Un tema = una sesión. Estado: TODO | DOING | DONE <hash> | BLOCKED <causa>.

Referencia base: S153-S176 (lectores/escritores estado IMX210), S124 (parámetros exposición por drive_mode), S134 (fórmula svd), S140 (vector registros IMX210), S176 (lectores state+0xac, state+0x30-0x37), CURRENT.md § S153-S176.

## Ítems

### S300 — Barrido xrefs a `0x43f72d02` (GOT `0x4401f990`) en A6000
- [x] 1. Encontrar todas las xrefs (REA + bytes) al GOT slot `0x4401f990` y al objeto `0x43f72d02` → 15 xrefs
- [x] 2. Clasificar cada xref: spill stack / lectura campo / escritura campo / propagación puntero / otra
- [x] 3. Enfocarse en writers a `+3` y `+6` (gates de S153) → **NO ENCONTRADOS**
- [x] 4. Tabla en `analysis/s300_state_xref_sweep/xrefs_classified.json`
- [x] 5. Informe `docs/capture/s300-state-xref-sweep.md` con veredicto sobre writers de gates
- [x] 6. Tests reproducibles en `analysis/s300_state_xref_sweep/test_s300_state_xref_sweep.py` (7 verdes)

### S301 — Barrido xrefs a estado imager en A7S fw3.20
- [ ] Mismo barrido en A7S (objeto equivalente al `0x43f72d02`)
- [ ] Tabla de diferencias A7S vs A6000

### S301 — Barrido xrefs a estado imager en A7S fw3.20
- [ ] Mismo barrido en A7S (objeto equivalente al `0x43f72d02`)
- [ ] Tabla de diferencias A7S vs A6000

### S302 — Tablas de drive mode/exposición A7S vs A6000
- [ ] Campos S124 (`shut`, `svd`, `shd`, `spl`, `sint`, `gs`, `epdsel`) por drive_mode
- [ ] Fórmula svd S134 (`0x4381106c`) en ambos
- [ ] Vector registros IMX210 `0x43fe995c` vs A7S `0x43fee370`/`0x43fee598`
- [ ] Tabla comparativa campo a campo

### S303 — Árbol referencias `0x43ff3200` y callers `FUN_43858338`
- [ ] Seguir referencias de tabla `0x43ff3200` (pendiente S176)
- [ ] Analizar callers de `FUN_43858338` (dumper gates S153) y alcanzabilidad

---

## Ítems derivados (se añaden al agotar)
(none yet)