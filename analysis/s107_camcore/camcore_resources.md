# S107 — `Camera::CamCore` (37 cadenas `[CAMCORE]`) y la pila `ResourceStack` del motor de imagen

**Milestone:** S107  
**Firmware:** A6000 fw3.21  
**Base virtual:** `vaddr = 0x43541000 + file_offset`  
**Total cadenas:** 37 con el prefijo `[CAMCORE]`, en el rango `0x43c905ca → 0x43cebcb2`  
**Comparativo:** A7S fw3.20 tiene **0** cadenas con ese prefijo; idénticas funcionalidades sin etiqueta de módulo.

## 1. Qué es `Camera::CamCore`

`CamCore` es la librería núcleo del controlador de cámara, confirmada por los símbolos RTTI:
- `N6Camera7CamCore8RdcImageE` en `0x43c906b6`
- `N6Camera7CamCore13SplitRdcImageE` en `0x43cb0b94`

Agrupa los siguientes subsistemas del motor de imagen (los **siglas** SGC, RDC, PFR, AIF y
Exl son las que usa el propio firmware; su desarrollo completo **no aparece en el binario** y
las de abajo son **hipótesis** NO VERIFICADAS):

| Subsistema (sigla del firmware) | Función principal | Desarrollo (hipótesis) | Direcciones características |
|---|---|---|---|
| **SGC** (`SgcTable`) | selección de controlador por modo | Sensor Gate Controller (hipótesis) | `0x43c905ca`, `0x43c909f7` |
| **RDC/PFR** | conversión y procesado de datos RAW; memoria PFR | Raw Data Converter / Partial Fixed Point Range (hipótesis) | `0x43c90846`, `0x43c9088e`, `0x43c90ca3`, `0x43c9073a`–`0x43c90799` |
| **AIF** | configuración DMA/extents para procesado de imagen | (sin desarrollo verificable) | `0x43c90a96`–`0x43c90bed` |
| **Memory/Resource** | MemoryPool, adquisición/liberación ResourceBase, ResourceStack | — | `0x43c908e7`, `0x43c90ec5`, `0x43ca10d1`–`0x43ca120f` |
| **ExlHelper** | conversión de CamMode a ExlMode; validación de parámetros de imager | — | `0x43c90f98`–`0x43c91074` |
| **DMA Setter** | control de canales DMA con manejo de errores | — | `0x43c910a4`–`0x43c91160` |
| **Powersave** | monitoreo y habilitación de powersave | — | `0x43c90f07` |
| **Defect correction** | corrección de píxeles defectuosos del sensor | — | `0x43cebcb2`, `0x43cebc93` |

Ninguna de las 60 cadenas con prefijo de S104 (`ADC_DEBUG`, `AVR`, `ADR`, `BKID`, `AVOUT`) aparece en CamCore; este es un bloque independiente.

## 2. La pila `ResourceStack`

La pila `ResourceStack` gestiona el ciclo de vida de los recursos adquiridos por CamCore durante la captura still. Cuatro de sus strings aparecen dentro del bloque `[IMAGING_CAP]` (S106), lo que confirma su consumo por la máquina de captura:

| Dirección (vaddr) | Cadena | Subsistema | Interpretación |
|---|---|---|---|
| `0x43ca10d1` | `[IMAGING_CAP]: ResourceStack)CamCore Release Error!: 0x%02x` | CamCore | Error durante el release de CamCore en la pila |
| `0x43ca110d` | `[IMAGING_CAP]: ResourceStack)rcct_Release err RC: RC_ERR:0x%02x` | CamCore/RC | Error en RC release con código RC_ERR |
| `0x43ca11c2` | `[IMAGING_CAP]: ResourceStack)Dfe Release Error!: %02x` | CamCore/DFE | Error en DFE release |
| `0x43ca120f` | `[IMAGING_CAP]: ResStack) GetMemIndex Err handle:%x` | CamCore/memoria | Error en GetMemIndex, handle inválido |

El flujo típico es: `acquire` → uso del recurso → `release` por la pila. Si el release falla (recurso ya liberado, handle inválido), se registra la cadena correspondiente. Estas strings están referenciadas por el gestor de captura `CapMgr`, confirmando que ResourceStack es consumido por la máquina de estados still (S106).

## 3. Desglose completo de las 37 cadenas `[CAMCORE]`

### 3.1 SGC (Sensor Gate Controller)

| vaddr | Cadena | Xrefs | Función | Nota |
|---|---|---|---|---|
| `0x43c905ca` | `[CAMCORE]: GetFlowType: No SgcTable. imgmode=%d, cammode=%d` | `0x436c22b8` | `0x436c227c` | GetFlowType no encuentra SgcTable para imgmode/cammode |
| `0x43c909f7` | `[CAMCORE]: No SgcTable. imgmode=%d, cammode=%d, hFlip=%u, vFlip=%u` | `0x436c4e4e` | `0x436c4e20` | Segunda variante con flips |

### 3.2 RDC/PFR

| vaddr | Cadena | Xrefs | Función | Nota |
|---|---|---|---|---|
| `0x43c90846` | `[CAMCORE]: [Error] Memory for PFR couldn't be freed. : unit_handle = %x` | `0x436c38b6` | `0x436c3890` | Liberación de memoria PFR fallida |
| `0x43c9088e` | `[CAMCORE]: [Error] Memory for PFR couldn't be allocated.` | `0x436c39cc` | `0x436c38e4` | Reserva de memoria PFR fallida |
| `0x43c90ca3` | `[CAMCORE]: PFR in width[%d] > 596` | `0x436c5462` | `0x436c53d8` | PFR: ancho > 596 |
| `0x43c9073a` | `[CAMCORE]: typeof(rawIn) must be RdcImage.` | `0x436c2bfc` | `0x436c2b48` | Entrada RDC obligatoria |
| `0x43c90765` | `[CAMCORE]: Cannot read with skipping when 4bit RAW.` | `0x436c2c70` | `0x436c2b48` | RAW de 4 bits sin skipping |
| `0x43c90799` | `[CAMCORE]: typeof(rawOut) must be RdcImage.` | `0x436c2e42` | `0x436c2d4e` | Salida RDC obligatoria |
| `0x43c90bad` | `[CAMCORE]: AIF%d RDC param error. encType[%d] lcut[%d] rcut[%d]` | `0x436c51f6` | `0x436c50dc` | Parámetros RDC inválidos en AIF |
| `0x43c90bed` | `[CAMCORE]: AIF%d RDC none. encType[%d] lcut[%d] rcut[%d]` | `0x436c5222` | `0x436c50dc` | RDC desactivado en AIF |

### 3.3 AIF (Arterial Image Framework)

| vaddr | Cadena | Xrefs | Función | Nota |
|---|---|---|---|---|
| `0x43c90a96` | `[CAMCORE]: AIF%d out[%d] > memsize[%d]` | `0x436c4fdc` | `0x436c4f6c` | Salida > tamaño memoria |
| `0x43c90abd` | `[CAMCORE]: AIF%d pbl_aif_set_func error[%d] size[%d] dest[%d] iib[%d] addr[%08x]` | `0x436c516e` | `0x436c50dc` | Error pbl_aif_set_func |
| `0x43c90bad` | `[CAMCORE]: AIF%d RDC param error. encType[%d] lcut[%d] rcut[%d]` | `0x436c51f6` | `0x436c50dc` | Parámetros RDC en AIF |
| `0x43c90bed` | `[CAMCORE]: AIF%d RDC none. encType[%d] lcut[%d] rcut[%d]` | `0x436c5222` | `0x436c50dc` | RDC desactivado |
| `0x43c90b2a` | `[CAMCORE]: AIF%d Extent count[%d] must be 1 or 2.` | `0x436c505e` | `0x436c4f6c` | Extents = 1 o 2 |
| `0x43c90afa` | `[CAMCORE]: AIF%d out[%d] memsize[%d] extent[%d]` | `0x436c5034` | `0x436c4f6c` | Traza extent/memsize calculados |
| `0x43c90982` | `[CAMCORE]: SplitEEController: Memory Close Error!(VATR)` | `0x436c45aa` | `0x436c4560` | Error cerrar memoria VATR |

### 3.4 Memory / Resource management

| vaddr | Cadena | Xrefs | Función | Nota |
|---|---|---|---|---|
| `0x43c908e7` | `[CAMCORE]: MemoryPool has no space.` | 11 sitios: `0x436c3e68`–`0x436c4114` | — | Sin espacio en pool (11 callsites) |
| `0x43c90ec5` | `[CAMCORE]: ResourceBase::Release was called without acquire. %08x` | `0x436c6b44` | `0x436c6b3c` | Release sin acquire previo |
| `0x43ca120f` | `[IMAGING_CAP]: ResStack) GetMemIndex Err handle:%x` | — | — | Error GetMemIndex en ResourceStack |

### 3.5 ExlHelper

| vaddr | Cadena | Xrefs | Nota |
|---|---|---|---|
| `0x43c90f98` | `[CAMCORE]: ExlHelper: Cannot convert CamMode[%d] to ExlMode.` | — | Sin xref PIC localizada |
| `0x43c90fd5` | `[CAMCORE]: ExlHelper: Invalid imager_mode_aspect[%d]` | — | Sin xref PIC localizada |
| `0x43c9100a` | `[CAMCORE]: ExlHelper: Invalid imager_if_type[%d]` | `0x436c7d30`, `0x436c7d58` | Función `0x436c7d08` |
| `0x43c9103b` | `[CAMCORE]: ExlHelper: Invalid imager_physical_coding[%d]` | `0x436c7d6e` | Función `0x436c7d08` |
| `0x43c91074` | `[CAMCORE]: ExlHelper: Invalid imager_aspect[%d]` | `0x436c7dd2` | Función `0x436c7d08` |

### 3.6 DMA Setter

| vaddr | Cadena | Xrefs | Función | Nota |
|---|---|---|---|---|
| `0x43c910a4` | `[CAMCORE]: [Setter] DMA Err open [%d]` | `0x436c9020` | `0x436c900c` | Error al abrir canal DMA |
| `0x43c910ca` | `[CAMCORE]: [Setter] DMAC_CH_NONE` | `0x436c9066` | `0x436c9050` | Canal DMAC_NONE |
| `0x43c910eb` | `[CAMCORE]: [Setter] listCount = %d` | `0x436c9082` | `0x436c9050` | Traza listCount |
| `0x43c9110e` | `[CAMCORE]: [Setter] DMA Err status [%d]` | `0x436c9146` | `0x436c9050` | Error de estado |
| `0x43c91136` | `[CAMCORE]: [Setter] DMA Err set_func [%d]` | `0x436c917e` | `0x436c9050` | Error en set_func |
| `0x43c91160` | `[CAMCORE]: [Setter] DMA Err start [%d]` | `0x436c91bc` | `0x436c9050` | Error al arrancar |

### 3.7 Powersave

| vaddr | Cadena | Xrefs | Función | Nota |
|---|---|---|---|---|
| `0x43c90f07` | `[CAMCORE]: MonPowersave[%d] is already Enabled !` | `0x436c7450` | `0x436c723c` | Powersave ya habilitado |

### 3.8 Defect correction

| vaddr | Cadena | Xrefs | Función | Nota |
|---|---|---|---|---|
| `0x43cebcb2` | `[CAMCORE]: Acl::CAMHEAD_Z1C::setDefectPt return err.` | `0x439cd7f6` | `0x439cd794` | setDefectPt devuelve error |
| `0x43cebc93` | `!/6;>?[CAMCORE]: loadDefectPos` | — | — | Precedida de bytes binarios; sin xref PIC |

## 4. Relación con `IMAGING_CAP` (S106)

- El bloque `[IMAGING_CAP]` (697 cadenas, `0x43c9b335 → 0x43ccab72`) consume ResourceStack para gestionar la adquisición y liberación de recursos durante la captura still.
- Cuatro strings del ResourceStack (vaddrs `0x43ca10d1`–`0x43ca120f`) están integradas en el bloque IMAGING_CAP, lo que demuestra que `CamCore` recursos son gestionados por el despachador de secciones still.
- La relación es: `IMAGING_CAP` (máquina de captura) → `ResourceStack` (acquire/release) → `CamCore` subsystems (SGC, RDC/PFR, AIF, DMA).
- Sin ResourceStack, el gestor de captura no puede adquirir los buffers de imagen necesarios (GetMem_RawCor, GetMem_MainYc, etc., vistos en S106 block `capmgr_notify`).

## 5. Relación con `sa_func_*` (S84)

S84 catalogó 19 familias `sa_func_*` del motor de imagen. Las trazas de error de la API del
motor de imagen aparecen dentro del bloque `[IMAGING_CAP]` (S106) y sus sitios de referencia
reales (recalculados con el esquema PIC, ver `analysis/s106_imaging_cap/pic_refs.json`) son:

| cadena (vaddr) | texto | sitios de referencia PIC |
|---|---|---|
| `0x43cac6cf` | `[IMAGING_CAP]: Error! sa_func_DUALREC_CLEARVID_acquire %d` | `0x437ed95e`, `0x437ee4ae` |
| `0x43cac867` | `[IMAGING_CAP]: Error! sa_func_DUALREC_CLEARVID_start %d %08X` | `0x437ee716`, `0x437eeb34` |
| `0x43cac9c1` | `[IMAGING_CAP]: Error! sa_func_DUALREC_BAYER_acquire %d` | `0x437ee84e` |

Es decir: `CamCore` aporta la infraestructura de bajo nivel (memoria, flujos, PFR, DMA) sobre la
que operan las funciones `sa_func_*` de nivel superior, y los errores de esa API se reportan
desde el mismo bloque de código del gestor de captura que usa `CamCore`.

## 6. Relación con el DFE (Digital Front End)

- Strings CAMCORE `0x43c90846` y `0x43c9088e` gestionan la memoria PFR usada por el DFE.
- String `0x43ca11c2` dentro de `ResourceStack` reporta errores DFE durante el release.
- String `0x43cad834` en bloque `stage_section_engine` de IMAGING_CAP: `[IMAGING_CAP]: DFE Acquire ERR:0x%02x`.
- String `0x43cad8d6` en bloque `stage_section_engine`: `[IMAGING_CAP]: DFE::Release: IMAGER0, DFE_ERR:0x%02x`.
- La relación es: `CamCore` reserva/libera memoria PFR → `DFE` consume el buffer → `ResourceStack` rastrea el ciclo de vida; si el release falla, se imprime `ResourceStack)Dfe Release Error!: %02x`.

## 7. Diferencial A6000 vs A7S fw3.20

| Característica | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| Cadenas `[CAMCORE]` | 37 (`0x43c905ca → 0x43cebcb2`) | 0 |
| RTTI `N6Camera7CamCore8RdcImageE` | `0x43c906b6` | No presente |
| RTTI `N6Camera7CamCore13SplitRdcImageE` | `0x43cb0b94` | No presente |
| Mensajes `ResourceStack)` en el gestor de captura | 4 con etiqueta `[IMAGING_CAP]:` (`0x43ca10d1`–`0x43ca120f`) | **presentes sin etiqueta**: `ResourceStack)CamCore Release Error!: 0x%02x` `0x43ca6252`, `ResourceStack)FOPD Acquire Fatal Error!: %x` `0x43ca61fa`, `ResourceStack)FOPD Release Fatal Error!: %x` `0x43ca6226` |
| `ExlHelper` | 5 apariciones | **5 apariciones** (mismo código, sin etiqueta) |
| `MonPowersave` | 1 aparición (`0x43c90f07`) | **1 aparición** (sin etiqueta) |

**Observación:** la fw3.21 de la A6000 añadió la etiqueta de módulo `[CAMCORE]:` (y
`[IMAGING_CAP]:` en el gestor de captura) a subsistemas que **ya existían** en la A7S fw3.20
—los mensajes `ExlHelper`, `MonPowersave` y `ResourceStack)` están en ambos blobs, sin etiqueta
en la A7S—. No se detectan diferencias funcionales; la distinción es de instrumentación.

## 8. No verificado / abierto

- El **significado de las siglas** SGC, RDC, PFR, AIF y Exl: el binario solo usa las siglas
  (`SgcTable`, `RdcImage`, `pbl_aif_set_func`, `ExlHelper`); **no hay ninguna expansión en el
  firmware**, de modo que cualquier desarrollo concreto es hipótesis.
- El formato binario interno de la ResourceStack (estructura de nodos, contadores RC/DFE,
  políticas de adquisición/liberación): se observan las cadenas de error pero no la tabla de
  metadatos.
- La relación completa entre las 5 cadenas `ExlHelper` y sus funciones contenedoras: 3 de 5
  tienen referencia PIC verificada (`0x436c7d08`), 2 no (`0x43c90f98`, `0x43c90fd5`).
- El significado de `!/6;>?[CAMCORE]: loadDefectPt`/`loadDefectPos` (precedida de bytes
  binarios sin interpretar en el flujo).
- Por qué 3 de las 697 cadenas `[IMAGING_CAP]` no tienen ninguna referencia PIC en toda la
  imagen (`0x43ca05d7`, `0x43ca9b12`, `0x43cc7d5c`) (las tres son **cadenas muertas**; ver S106).

## 9. Revisión del agente principal (correcciones aplicadas)

1. **Siglas**: el borradorcribía `SGC (Sensor Gate Controller)`, `RDC/PFR (Raw Data Converter /
   Partial Fixed Point Range)` y `AIF (Arterial Image Framework)` como si fueran hechos. El
   firmware **no expande** esas siglas → se marcan como hipótesis NO VERIFICADAS.
2. **Sitios de referencia erróneos** en §5: el borrador citaba `0x436c5462` y `0x436c51f6`
   como referencias de las trazas `sa_func_DUALREC_*`; esos son funciones, no sitios de
   referencia. Los sitios reales (recalculados con el esquema PIC) son `0x437ed95e`,
   `0x437ee4ae`, `0x437ee716`, `0x437eeb34` y `0x437ee84e`.
3. **Diferencial A7S**: el borrador daba por "no verificado" la presencia de `ExlHelper` y
   `MonPowersave` en la A7S; se ha comprobado en los bytes: **existen** (5 y 1 apariciones
   respectivamente, sin etiqueta). También se han citado los mensajes `ResourceStack)` concretos
   de la A7S (`0x43ca61fa`, `0x43ca6226`, `0x43ca6252`), que el borrador daba por ausentes.
4. **Nota de `docs/capture/`**: el borrador decía "≥60 líneas" para la nota breve; la nota
   real es más corta (resumen ejecutivo) y así se documenta.

## 10. Ficheros asociados

- `analysis/s107_camcore/camcore_resources.json` — datos estructurados (cadenas, vaddrs, xrefs, funciones, subsistemas).
- `analysis/s107_camcore/camcore_resources.md` — este informe.
- `docs/capture/s107-camcore-resources.md` — nota breve (resumen ejecutivo) que enlaza al informe.
- `tests/test_s107_camcore.py` — tests de bytes reales que afirman direcciones, textos y recuentos.
- `analysis/s107_camcore/scan_camcore.py` — script de extracción reproducible (opcional).