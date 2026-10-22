# S601 — módulo `[CAM_SCALAR]` (34 trazas): exclusivo de A6000 fw3.21

**Estado: VERIFICADO** — 34 cadenas únicas (REA `search_strings`) / 34 ocurrencias totales (`strings -a`) con el prefijo `[CAM_SCALAR]` en la A6000 fw3.21; **0 en A7S fw3.20** y **0 en A6300 fw2.01** (búsqueda literal en los tres `av-cam.bin`).

---

## 1. Censo de trazas (34 únicas, direcciones virtuales base 0x43000000)

| # | VA | Texto (truncado) |
|---|---|---|
| 1 | 0x43cb04b2 | HAPI Manager:Recieve error |
| 2 | 0x43cb04db | HAPI Manager:Message size 0 |
| 3 | 0x43cb0505 | HAPI Manager:Empty Message |
| 4 | 0x43cb052e | req_sequence_create_stream: input image is null. |
| 5 | 0x43cb056d | req_tool_get_image_info: input image is null. |
| 6 | 0x43cb05a9 | req_filter_develop: input image is null. |
| 7 | 0x43cb05e0 | %s: input image and sdsYC is invalid. |
| 8 | 0x43cb0614 | %s: copyStdYc error. |
| 9 | 0x43cb0637 | %s: warning. NR Level OFF |
| 10 | 0x43cb065f | %s: input image is invalid. |
| 11 | 0x43cb0689 | %s: input stdYcHandle is invalid. |
| 12 | 0x43cb06b9 | HAPI Manager:Unknown MSG_ID |
| 13 | 0x43cb074c | %s: input image unsupported format. |
| 14 | 0x43cb077e | %s: YC(develop) DMM allocation error[%d]. |
| 15 | 0x43cb07c4 | %s: SdsYc error |
| 16 | 0x43cb0849 | %s: dmm_handle[DMM_HANDLE_YCC_FULL] error |
| 17 | 0x43cb0881 | %s: Alloc SDS YC error |
| 18 | 0x43cb08a6 | %s fatal |
| 19 | 0x43cb08bd | %s: No YCC_FULL handle |
| 20 | 0x43cb08e2 | %s: No RAW_FULL handle |
| 21 | 0x43cb0907 | %s: dmm_handle[%d] error |
| 22 | 0x43cb092e | %s: ShareCheck error |
| 23 | 0x43cb0951 | %s: p_newparam error |
| 24 | 0x43cb0974 | %s: outImage error |
| 25 | 0x43cb0995 | %s: dmm_handle[%d] Share error |
| 26 | 0x43cb09c2 | %s: Share error |
| 27 | 0x43cb0a5b | %s: ExposureCount parameter value is invalid. |
| 28 | 0x43cb0a97 | %s: RecordCount parameter value is invalid. |
| 29 | 0x43cb0ad1 | %s: CapMode is not CAP_SINGLE |
| 30 | 0x43cb0afd | Open Error |
| 31 | 0x43cb0b16 | %s: AllocNewWait error |
| 32 | 0x43cb0b3b | %s: %d Free error |
| 33 | 0x43cb0bb6 | %s: input image is null. |
| 34 | 0x43cc67f2 | RecordCount Unmatch! : remain %d |

---

## 2. Funciones emisoras (REA `xrefs`)

Las xrefs apuntan a direcciones en el rango **0x4380a710–0x4380c6fa**. Ghidra (ARM:LE:32:v7) **no reconoció estas direcciones como procedimientos** (probablemente código Thumb); no se pudo decompilar sus cuerpos. Las direcciones de instrucción que referencian las cadenas son:

```
0x4380a710, 0x4380a73e, 0x4380a762, 0x4380a7ea, 0x4380a834, 0x4380a87c,
0x4380a8ca, 0x4380aa38, 0x4380aba4, 0x4380a8f8, 0x4380aac8, 0x4380abd2,
0x4380aa6a, 0x4380aca2, 0x4380ace4, 0x4380ad2a, 0x4380ad72, 0x4380adda,
0x4380ae20, 0x4380ad94, 0x4380ae58, 0x4380b08a, 0x4380c220, 0x4380c6fa,
0x4380b0cc, 0x4380b268, 0x4380b5c0, 0x4380b77c, 0x4380b95a, 0x4380ba4e,
0x4380b994, 0x4380bb22, 0x4380bbb0, 0x4380bc5a, 0x4380be64, 0x4380bf8c,
0x4380be88, 0x4380beaa, 0x4380bee0, 0x4380bfbe, 0x4380bffe, 0x4380c026,
0x4380c3b8, 0x4380c3e0, 0x4380c42e, 0x4380c6a6, 0x4380c6fa
```

**Nota:** Varias cadenas son referenciadas desde múltiples sitios (p. ej. la #7 desde 3 sitios, la #10 desde 6 sitios), indicando validaciones compartidas.

---

## 3. Temas funcionales inferidos

| Tema | Cadenas | Descripción |
|---|---|---|
| **HAPI Manager** | #1–3, #12 | Gestor de mensajes *Host API*: recepción, tamaño, mensaje vacío, MSG_ID desconocido |
| **Pipeline de imagen** | #4–6 | `req_sequence_create_stream`, `req_tool_get_image_info`, `req_filter_develop` — validan puntero de imagen de entrada |
| **Procesado YC** | #7, #8, #9, #11, #15 | `copyStdYc`, `sdsYC`, `stdYcHandle`, *Noise Reduction* Level OFF, `SdsYc error` |
| **DMM (Direct Memory Management)** | #14, #16, #17, #19, #20, #21, #25, #26 | Handles `DMM_HANDLE_YCC_FULL`, `RAW_FULL`; asignación, share check, errores de handle |
| **Parámetros de captura** | #27, #28, #29 | `ExposureCount`, `RecordCount`, `CapMode == CAP_SINGLE` |
| **Gestión memoria** | #30–33 | `Open Error`, `AllocNewWait`, `Free error`, `input image is null` (repetida) |
| **Contadores** | #34 | `RecordCount Unmatch! : remain %d` |

---

## 4. Diferencial A7S fw3.20 / A6300 fw2.01

| Firmware | Cadenas `[CAM_SCALAR]` | Conclusión |
|---|---|---|
| A6000 fw3.21 | 34 únicas / 34 totales | **Módulo presente** |
| A7S fw3.20 | 0 | **Ausente** |
| A6300 fw2.01 | 0 | **Ausente** |

**Verificación:** `strings -a` literal en los tres `av-cam.bin` (SHA256 distintos). REA `search_strings` en A6000 confirma 34 cadenas únicas con xrefs válidas.

---

## 5. Evidencia y reproducibilidad

- **JSON + test:** `analysis/s601_cam_scalar/`
  - `cam_scalar.json` — catálogo completo
  - `test_cam_scalar_exclusivity.py` — test automatizado (3 asserts)
- **Herramientas:** REA (MCP `search_strings`, `xrefs`) + `strings -a` / `grep` como control positivo.
- **Binario:** `av-cam.bin` A6000 fw3.21 (SHA256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`).

---

## 6. Límites / NO_VERIFICADO

- Ghidra (ARM:LE:32:v7) **no identificó funciones** en el rango 0x4380a000+; los bytes en 0x4380a710 (`7b44 fff7 89ff...`) muestran prólogos Thumb (`push {r2,r3,r6,r7,lr}` + `bl`), no soportados por el analizador ARM actual de REA.
- Nombres de función y archivos fuente no recuperados.
- Semántica de HAPI, DMM, SDS, YC inferida de formato de trazas; no confirmada en símbolos.
- No se probó alcance en runtime (sin firmware ejecutado).
- La ausencia en A7S/A6300 es **estática**; no prueba incapacidad de hardware.

---

## 7. Conclusión para la línea del obturador electrónico

**Sin efecto directo en S51 (A/B/C = NO).** El módulo gestiona **procesado de imagen YC (luminancia/crominancia), pipeline HAPI, memoria DMM y parámetros de captura** pero **no menciona** `shutter`, `silent`, `electronic`, `EFCS`, `curtain`, `mechanical`, `flicker`. Es un módulo de **procesado escalar de imagen** exclusivo de la A6000 fw3.21.

---

**Próximo:** S602 — decodificar `[REMOTE]` (32 trazas), exclusivo A6000.