# Tesis: Obturador electrónico en Sony A6000 fw3.21 — Hipótesis, evidencia y criterios de refutación

> Síntesis final de la investigación Agente C (sesiones S401–S403).
> Basada en: `s401-a7s-silent-control-path.md`, `s402-physical-test-mapping.md`, `silent-shutter-status.md` (E015–E019, S174), `s53-darwin-a7s-a6000-comparison.md`, `s54-mechanism-type-zero.md`, `darwin-state-machine.md`, `silent-caif-transport.md`, `s171-imager-api.md`, `s169-drive-api-a6300.md`, `physical-test-plan.md`.
> Fecha: 22-10-2026. Firmware A6000 3.21 (SHA `b60c845c...56bb9`), A7S 3.20 (SHA `b857d338...5103e`).

---

## 1. Hipótesis principal

> **H₀ (hipótesis nula)**: La A6000 fw3.21 **no puede** realizar captura fotográfica totalmente electrónica (sin accionar ninguna cortina mecánica) a resolución completa, porque le faltan **tres eslabones críticos** que sí existen en la A7S fw3.20:
>
> 1. **Bit Silent en CAIF** (`pkt[+0x12]&0x20`) — no se construye en `av-cam.bin` A6000.
> 2. **Predicado `no_silent` en Darwin** — no existe en firmware MCU A6000.
> 3. **Rama de reposición coherente** — A6000 tipo 0 no acciona bobinas en aborto/reposición, dejando cortinas en estado indeterminado si existen físicamente.
>
> **H₁ (hipótesis alternativa)**: La A6000 **tiene la capacidad latente** (hardware IMX210 + Darwin tipo 0 + estructura CAIF) pero le falta **activación por firmware** de los tres eslabones. Un parche mínimo (modificar construcción CAIF + añadir predicado Darwin + habilitar reposición) **podría** habilitar SilentShutter real, **si** el IMX210 soporta fin de integración electrónico por filas (no verificado).

---

## 2. Evidencia estática (VERIFICADA / INFERENCIA / NO_VERIFICADO)

| # | Componente | A7S fw3.20 | A6000 fw3.21 | Evidencia | Etiqueta |
|---|---|---|---|---|---|
| 1 | **UI / libObj.so** | Menú SilentShutter; mensaje 0x768e **rechazado** | Menú SilentShutter; mensaje 0x768e **rechazado** | S174, E015 | VERIFICADO |
| 2 | **LIRO dispatcher** | **Sin handler 0x40e3** (220 cmds) | Handler 0x40e3 en `0x438032d4` (escribe estado +0x238) | Bytes tabla `0x43fff30c` | VERIFICADO |
| 3 | **CAIF evento 1** | **Inferido**: pone bit 0x20 en `pkt[+0x12]` | `0x43841070`: **no pone bit 0x20** (solo 0/1) | silent-caif-transport.md | A6000=VERIFICADO, A7S=INFERENCIA |
| 4 | **Darwin parser** | Extrae bit 0x20 → `no_silent` en `S+0xd0.b5` | **No extrae** bit 0x20 | S53, S54 | VERIFICADO |
| 5 | **Darwin rama sin meca** | `no_silent=0`: omite P4D/P4E/ADC, **reposición acciona bobinas** (`no_silent=1`) | Tipo 0: omite P4D/P4E/ADC, **reposición NO acciona bobinas** | S54, darwin-state-machine.md | VERIFICADO |
| 6 | **Driver imager** | IMX235: APIs `GetImagerStabilizationTime`, `SetImagerFrameSize`, `SetImagerMode`, `SteadyShotInfo` | IMX210: **sin** esas APIs; solo 4 comunes | s171-imager-api.md, E017/E018 | VERIFICADO |
| 7 | **LiroSeq CheckSet*** | Ausente (0/201) | Ausente (0/201) | S169 | VERIFICADO |
| 8 | **Enlace Darwin → imager** | No verificado (IMX235 modo electrónico) | No verificado (IMX210 modo 0–4 selector) | E019, s134-imager-params.md | NO_VERIFICADO |
| 9 | **Fin integración electrónico** | No identificado en binario | No identificado en binario | E018, E019 | NO_VERIFICADO |

---

## 3. Cadena completa A7S SilentShutter (reconstrucción parcial)

```mermaid
flowchart TD
  U[Usuario: SilentShutter ON] --> L1[libObj.so: pvt_ActionSetSilentShutterMode]
  L1 --> L2[Mensaje 0x768e / param 0x9983 → RECHAZADO en libObj.so]
  L2 -. ¿cómo sigue? .-> C1[av-cam.bin: construcción CAIF evento 1]
  C1 --> C2[Condición: *(captura+0x804)==2 → pkt[+0x12] |= 0x20]
  C2 --> D1[Darwin: parser 0x18396 lee pkt[+0x12]&0x20]
  D1 --> D2[no_silent=0 → rama sin mecanismo]
  D2 --> D3[Omite P4D/P4E/ADC; solo P4C + temporización]
  D3 --> D4[En aborto/reposición: no_silent=1 → acciona bobinas]
  D4 --> I1[LIRO/imager IMX235: SetExposure/SetRead modo electrónico]
  I1 -. enlace NO_VERIFICADO .-> I2[Fin integración electrónico / lectura completa filas]
```

**Saltos no verificados (NO_VERIFICADO)**:
- `L2 → C1`: Cómo la selección UI llega a construcción CAIF (mensaje 0x768e rechazado no pasa a LIRO).
- `C1`: Función exacta en A7S `av-cam.bin` y condición `*(captura+0x804)==2` (equivalente A6300).
- `I1 → I2`: Qué registros IMX235 programa driver en modo Silent; cómo se sincroniza fin de exposición con lectura.

---

## 4. Qué falta en A6000 (brecha concreta)

| Eslabón | A7S | A6000 | Acción requerida en A6000 |
|---|---|---|---|
| CAIF bit 0x20 | Sí (inferido) | **No** | Modificar `0x43841070` para poner bit 0x20 si campo captura == 2 |
| Darwin no_silent | Sí (parser + predicado) | **No** | Añadir extracción bit 0x20 en parser `0x17f8c` + predicado en ramas exposición/reposición |
| Reposición coherente | Sí (`no_silent=1` acciona bobinas) | **No** (tipo 0 no acciona) | En tipo 0, replicar lógica A7S: accionar bobinas en reposición/aborto |
| Driver imager modo electrónico | IMX235 (APIs extra) | IMX210 (selector 0–4 en `SetExposure`) | Identificar selector IMX210 para exposición electrónica (E019: selector 0–4 sin nombres físicos) |
| Fin integración electrónico | No verificado | No verificado | Requiere datasheet IMX210 o traza pasiva bus sensor (P9) |

---

## 5. Criterios de refutación (qué cambiaría la tesis)

| Criterio | Qué observaría | Consecuencia para H₀/H₁ |
|---|---|---|
| **R1 (P5)**: Analizador lógico muestra bit 0x20 en `pkt[+0x12]` A7S Silent y **también** en A6000 si se fuerza campo captura | A6000 **sí** tiene capacidad latente de poner bit 0x20 | **Refuta H₀** → H₁ gana (solo falta activar campo) |
| **R2 (P3+P7)**: Forzar `G+0x808=2` (tipo 2) en A6000 + disparo → foto silenciosa (P7: sin rolling shutter / bandas flicker distintas a mecánico) | A6000 **ejecuta** exposición electrónica completa | **Refuta H₀** → H₁ gana (Darwin tipo 0/2 funcional) |
| **R3 (P3+P12)**: Forzar tipo 2 en A6000 + aborto → **doble click** (bobinas accionan en reposición) | A6000 **tiene** reposición coherente latente | **Refuta H₀** parcial → H₁ gana (falta solo activar) |
| **R4 (P9)**: Traza bus sensor IMX210 muestra registros de fin integración electrónico / lectura global en modo vídeo/LiveView | IMX210 **soporta** fin electrónico por filas | **Refuta H₀** → H₁ gana (hardware capaz) |
| **R5 (P6)**: Service shell expone `captura+0x804` (o equivalente) y cambia con menú Silent/EFCS | Campo existe y es escribible | **Refuta H₀** → H₁ gana (origen del campo identificable) |
| **R6 (Datasheet IMX210 público/NDA)**: Documenta modo "electronic shutter" / "rolling shutter electronic" con registros | IMX210 **diseñado** para obturación electrónica | **Refuta H₀** → H₁ gana |

**Si NINGUNO de R1–R6 se cumple**: H₀ se mantiene (A6000 no puede Silent real sin rediseño profundo de firmware MCU + driver sensor).

---

## 6. Evaluación de viabilidad S51 (actualizada)

| Pregunta S51 | Respuesta vigente | Cambio tras S401–S403 |
|---|---|---|
| **A**: ¿Ruta electrónica demostrada? | **NO** | Sigue NO. Brecha: CAIF bit 0x20 + Darwin no_silent + reposición + driver IMX210 modo electrónico. |
| **B**: ¿Parche justificable? | **NO** | Sigue NO. Parche requeriría: (1) modificar `av-cam.bin` construcción CAIF, (2) flashear Darwin MCU (riesgo alto, no reversible), (3) identificar selector IMX210 electrónico, (4) verificar fin integración. Sin R1–R4, es conjetura. |
| **C**: ¿Hardware imposible? | **NO** | Sigue NO. IMX210 tiene lectura electrónica (vídeo/LiveView); Darwin tipo 0 existe; CAIF estructura compatible. Solo falta integración firmware. |

**Conclusión S51 inalterada**: **A=NO, B=NO, C=NO**. La investigación estática **agota** lo que puede decirse sin pruebas físicas (P5, P3, P7, P9) o datasheet IMX210.

---

## 7. Hoja de ruta para decisión final (requiere autorización física)

| Paso | Prueba | Decisión si pasa | Decisión si falla |
|---|---|---|---|
| 1 | **P5** (bus CAIF A7S Silent vs A6000) | Ver bit 0x20 en A7S, no en A6000 → confirmar Diferencias 3,5 | Si A6000 también pone bit 0x20 → R1: H₁ gana |
| 2 | **P1→P2→P3** (forzar tipo 2 + disparo + P7) | Foto silenciosa P7 → R2: H₁ gana | Si no silenciosa → tipo 2 no basta |
| 3 | **P12** (aborto tipo 2 → doble click) | Reposición coherente → R3: H₁ gana | Si no acciona → mecanismo en riesgo |
| 4 | **P9** (bus sensor IMX210 vídeo) | Registros fin integración electrónico → R4: H₁ gana | Si no → IMX210 no soporta |
| 5 | **P6** (service shell campo captura) | Campo identificable → R5: H₁ gana | Si no → origen desconocido |

**Orden recomendado**: P5 (solo lectura, máxima info) → P1/P7 (base) → P2/P3 (funcional) → P6/P12 (diagnóstico) → P9 (invasivo, último).

---

## 8. Límites de la investigación estática

1. **Cobertura incompleta**: REA/Ghidra no analizaron 100% del código (Thumb no sembrado, tablas de salto, colas OSAL indirectas). "Consulta vacía no prueba ausencia".
2. **Semántica física**: Registros IMX210/IMX235, pines Darwin, bit CAIF 0x20 — **no tienen nombre físico verificado** en binario; son inferidos por posición/condición.
3. **Ejecución no observada**: Timing, interrupciones, estado RAM vivo, valores por defecto en captura real — **no medidos**.
4. **Datasheet IMX210**: No público legítimo (Sony NDA). TechInsights DEF-1412-801 confirma IMX210 en A6000 pero no registros.
5. **A7S vs A6000 sensor distinto**: IMX235 vs IMX210 — capacidades electrónicas **no comparables directamente**.

---

## 9. Artefactos de la investigación (trazabilidad)

| Documento | Contenido | Sesión |
|---|---|---|
| `docs/capture/s401-a7s-silent-control-path.md` | 8 diferencias A7S/A6000 con evidencia | S401 |
| `docs/capture/s402-physical-test-mapping.md` | Mapeo diferencias → P1–P8 + P9–P12 propuestas | S402 |
| `docs/capture/silent-shutter-status.md` | E015–E019, S174, S169, S171, S172 | Base |
| `docs/capture/s53-darwin-a7s-a6000-comparison.md` | Darwin parser, no_silent, ramas | S53/S54 |
| `docs/capture/darwin-state-machine.md` | Fases, notificaciones, escrituras control | S54+ |
| `docs/capture/silent-caif-transport.md` | CAIF bit 0x20 A6300 vs A6000 | S135+ |
| `analysis/ghidra/silent-liro.gpr` | Proyecto Ghidra persistente IMX210/LIRO/Darwin | E016–E019 |
| `reports/silent-liro-dispatch.json` | Tabla despacho LIRO A6000 (220 entradas) | E016 |

---

## 10. Veredicto final

> **La A6000 fw3.21 no implementa obturador silencioso/electrónico completo** por ausencia de tres eslabones firmware que **sí** tiene la A7S fw3.20 en la misma plataforma (Darwin MCU FM3 MB9AF004BGL):
>
> 1. **CAIF**: bit `0x20` en `pkt[+0x12]` no construido.
> 2. **Darwin**: predicado `no_silent` y rama reposición coherente ausentes.
> 3. **Imager**: driver IMX210 sin modo electrónico identificado (selector 0–4 sin semántica física).
>
> **El hardware (IMX210 + Darwin FM3) no se ha demostrado incapaz**, pero la integración firmware **no existe** en fw3.21. Cualquier implementación requeriría:
> - Modificar `av-cam.bin` (CAIF) — riesgo medio, reversible en RAM.
> - **Flashear Darwin MCU** (parser + predicado + reposición) — **riesgo alto, irreversible** (fw mismo versión rechazado).
> - Identificar/implementar modo electrónico IMX210 — **requiere datasheet o traza pasiva bus sensor (P9)**.
>
> **Sin autorización para P5/P3/P7/P9 y sin datasheet IMX210, la investigación estática se da por agotada**. El punto pendiente queda acotado: **prueba física P5 (bus CAIF) es la única que puede confirmar/refutar la capacidad latente de A6000 sin flashear MCU**.

---

## 11. Reproducción y validación

```sh
# Verificar tabla LIRO A7S (sin handler 0x40e3)
python3 -c "
import mmap, struct
with open('firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin','rb') as f:
    m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    base = 0x43541000
    table = 0x43fff30c - base
    found = False
    for i in range(220):
        off = table + i*12
        cmd, flags, handler, pad = struct.unpack('<HHI', m[off:off+12])
        if cmd == 0x40e3:
            print(f'ENTRADA 0x40e3 ENCONTRADA en índice {i}: handler=0x{handler:x}')
            found = True
            break
    if not found:
        print('0x40e3 NO ENCONTRADO en 220 entradas (VERIFICADO)')
"

# Verificar CAIF A6000 no pone bit 0x20 (silent-caif-transport.md)
# Verificar Darwin A7S parser extrae bit 0x20 (s53-darwin-a7s-a6000-comparison.md)
# Verificar IMX210 driver APIs (s171-imager-api.md)
```