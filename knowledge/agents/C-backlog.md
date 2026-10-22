# Backlog Agente C — Ruta de control: configuración → LIRO → imager (S401+)

Estado: DOING (S401 en progreso, S402-S403 pendientes)

## Ítems

### S401 — Trazar ruta SilentShutter en A7S: configuración → LIRO → estado imager
- [x] 1. Identificar en A7S fw3.20 el handler LIRO para SilentShutter (equivalente a 0x40e3 en A6000) → **NO EXISTE en tabla de despacho LIRO A7S**
- [x] 2. Comparar tabla de despacho LIRO A7S vs A6000 → **A7S no tiene cmd 0x40e3; A6000 lo tiene pero rechazado en libObj.so (S174)**
- [x] 3. Darwin MCU: A7S tiene predicado `no_silent` (`pkt[+0x12]&0x20`) y rama "sin mecanismo"; A6000 tiene tipo 0 similar pero sin `no_silent` (S53, S54)
- [x] 4. CAIF packet: A7S/A6300 ponen bit 0x20 en `pkt[+0x12]` para Silent; A6000 NO lo pone (silent-caif-transport.md)
- [x] 5. Documentar diferencias 1-8 con etiquetas VERIFICADO/INFERENCIA/NO_VERIFICADO → **Hecho en s401-a7s-silent-control-path.md**
- [x] 6. Localizar en A7S constructor CAIF evento 1 y condición bit 0x20 → **Pendiente (requiere P5/P10 físico)**; documentado como INFERENCIA
- [x] 7. Rastrear propagación CAIF → Darwin → LIRO/imager → **Parcial (Darwin verificado; enlace LIRO/imager NO_VERIFICADO)**

### S402 — Mapear diferencias a pruebas físicas (physical-test-plan.md P1–P8)
- [x] Para cada diferencia hallada en S401, indicar cuál prueba la confirmaría/refutaría → **Hecho en s402-physical-test-mapping.md**
- [x] Proponer pruebas nuevas si faltan (solo redactar) → **Hecho: P9–P12 en s402**

### S403 — Escribir tesis final: docs/capture/tesis-obturador-electronico.md
- [x] Hipótesis, evidencia, qué la refutaría → **Hecho en tesis-obturador-electronico.md**

---

## Hallazgos S401 (resumen para S402/S403)

Ver `docs/capture/s401-a7s-silent-control-path.md` y `docs/capture/s402-physical-test-mapping.md`. Diferencias clave:

| # | Diferencia | A7S | A6000 | Etiqueta |
|---|---|---|---|---|
| 1 | Handler LIRO 0x40e3 | Ausente | Presente (inútil) | VERIFICADO |
| 2 | libObj.so ForLiro | 221 rechazados | 216 rechazados | VERIFICADO |
| 3 | Darwin no_silent | Sí (bit 0x20) | No | VERIFICADO |
| 4 | Darwin sin mecanismo | Sí + reposición | Tipo 0 (sin reposición) | VERIFICADO |
| 5 | CAIF bit 0x20 | Inferido Sí | No (solo 0/1) | A6000=VERIFICADO, A7S=INFERENCIA |
| 6 | Sensor/imager | IMX235 + APIs extra | IMX210 base | VERIFICADO |
| 7 | API imager común | 4 + 3 extra | 4 | VERIFICADO |
| 8 | LiroSeq CheckSet* | Ausente | Ausente | VERIFICADO |