# S103 — Prefijos de traza exclusivos de la A6000

**Hito:** documentar los seis prefijos con token `[PREFIJO]` que existen en la A6000 (fw3.21)
pero **no** en la A7S (fw3.20) y que no tenían hito propio: `ADC_DEBUG`, `AVR`, `ADR`, `BKID`,
`AVOUT` y `CAMCORE`. **Método:** análisis estático de bytes de `analysis/rea-independent/input/av-cam.bin`
(regla `vaddr = 0x43541000 + file_offset`), conteo idéntico a S79 y localización de xrefs PIC
(`ldr rN,[pc,#imm]` + `add rN,pc`). **Sin firmware ejecutado, sin cámara, sin flasheo, sin sesiones
Ghidra/REA.** Datos completos: `a6000_prefixes.json`; prueba: `tests/test_s103_prefixes.py`.

## Resumen

| Prefijo | n | Rango de direcciones | Qué es | Evidencia |
|---|---:|---|---|---|
| `ADC_DEBUG` | 14 | `0x43ce50dd`–`0x43ce5273` | Depuración del ADC de 12 canales de LIRO | VERIFICADO (cadenas, xrefs, mensaje OSAL 0xfff1/0xfff0) |
| `AVR` | 2 | `0x43c25502`–`0x43c25528` | Clase de accesorio **LANC-AVR** (ACCY) | VERIFICADO (log de fábrica `LANC-AVR` + handlers GPIO) |
| `ADR` | 1 | `0x43cce3fa` | Campo **dirección** de una apertura de imagen (CAM_UTIL_SENS) | VERIFICADO (mensaje IM open en `0x43901d50`) |
| `BKID` | 4 | `0x43cce1ea`–`0x43cfb1a8` | **Backup ID**: callback de cambio y registro/anulación | VERIFICADO (`backupId`, `Backup_read(BKID_*)`) |
| `AVOUT` | 2 | `0x43c2549e`–`0x43c254c6` | Clase de accesorio **AvOut** (ACCY) | VERIFICADO (log de fábrica + dispatcher ACCY) |
| `CAMCORE` | 37 | `0x43c905ca`–`0x43cebcb2` | Librería **Camera::CamCore** (SGC/RDC/PFR/AIF/DMA) | VERIFICADO (cadenas, 43 xrefs, RTTI) |

**Total:** 60 cadenas. Ninguno de los seis tokens aparece en el mapa S79 de la A7S: son
exclusivos de la A6000. `ADR` y `BKID` **no son módulos**: son campos entre corchetes dentro de
logs de `[CAM_UTIL_SENS]`/`[LIF_DEBUG]`. `AVR`/`AVOUT` tampoco: son clases de accesorio de `ACCY`.

---

## 1. `ADC_DEBUG` (14) — ADC de 12 canales de LIRO

El bloque ADC se arranca como unidad LIRO (`boot_exit_adcliro`, `0x43ce5315`; tarea `TSK_ADC`,
`0x43ce5291`) y expone comandos con `unit_no` y 12 canales (`ADC_GET_DATA`, `ADC_GET_DATA_ALL`,
`ADC_SET_DATA_ALL`). La función `0x4398eb22` valida `unit_no`, reserva 0x20 bytes (OSAL
`0x435612d0`), escribe la cabecera `0xfff1` y envía el mensaje (`0x43561228`); después imprime
`DATA0..DATA11` leyendo 12 halfwords desde `[msg+6]`. La función `0x4398ec7e` repite el patrón con
cabecera `0xfff0`, mensaje de 8 bytes y dos canales (cadena genérica `ADC DATA`).

| vaddr | cadena | xref / función | interpretación |
|---|---|---|---|
| `0x43ce50dd` | `[ADC_DEBUG]: few arg` | `0x4398eb2a (+1)` / `0x4398eb22 (+1)` | Aviso de argumento inválido (unit_no fuera de rango). |
| `0x43ce50f3` | `[ADC_DEBUG]: ADC DATA0  = %04x` | `0x4398eb68` / `0x4398eb22` | Canal 0 del volcado: halfword en [msg+0x6]. |
| `0x43ce5113` | `[ADC_DEBUG]: ADC DATA1  = %04x` | `0x4398eb7a` / `0x4398eb22` | Canal 1 del volcado: halfword en [msg+0x8]. |
| `0x43ce5133` | `[ADC_DEBUG]: ADC DATA2  = %04x` | `0x4398eb8c` / `0x4398eb22` | Canal 2 del volcado: halfword en [msg+0xa]. |
| `0x43ce5153` | `[ADC_DEBUG]: ADC DATA3  = %04x` | `0x4398eb9e` / `0x4398eb22` | Canal 3 del volcado: halfword en [msg+0xc]. |
| `0x43ce5173` | `[ADC_DEBUG]: ADC DATA4  = %04x` | `0x4398ebb0` / `0x4398eb22` | Canal 4 del volcado: halfword en [msg+0xe]. |
| `0x43ce5193` | `[ADC_DEBUG]: ADC DATA5  = %04x` | `0x4398ebc2` / `0x4398eb22` | Canal 5 del volcado: halfword en [msg+0x10]. |
| `0x43ce51b3` | `[ADC_DEBUG]: ADC DATA6  = %04x` | `0x4398ebd4` / `0x4398eb22` | Canal 6 del volcado: halfword en [msg+0x12]. |
| `0x43ce51d3` | `[ADC_DEBUG]: ADC DATA7  = %04x` | `0x4398ebe6` / `0x4398eb22` | Canal 7 del volcado: halfword en [msg+0x14]. |
| `0x43ce51f3` | `[ADC_DEBUG]: ADC DATA8  = %04x` | `0x4398ebf8` / `0x4398eb22` | Canal 8 del volcado: halfword en [msg+0x16]. |
| `0x43ce5213` | `[ADC_DEBUG]: ADC DATA9  = %04x` | `0x4398ec0a` / `0x4398eb22` | Canal 9 del volcado: halfword en [msg+0x18]. |
| `0x43ce5233` | `[ADC_DEBUG]: ADC DATA10 = %04x` | `0x4398ec1c` / `0x4398eb22` | Canal 10 del volcado: halfword en [msg+0x1a]. |
| `0x43ce5253` | `[ADC_DEBUG]: ADC DATA11 = %04x` | `0x4398ec2e` / `0x4398eb22` | Canal 11 del volcado: halfword en [msg+0x1c]. |
| `0x43ce5273` | `[ADC_DEBUG]: ADC DATA = %04x` | `0x4398eccc` / `0x4398ec7e` | Volcado genérico de 2 canales (mensaje de 8 bytes, cabecera 0xfff0). |

Los cinco nombres `ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_*` (`0x43ce4fc7`–`0x43ce507a`) son comandos de
ajuste de fábrica del mismo bloque; **solo cuatro tienen xref PIC** (`GET_DATA_ALL`, `CHECK_DATA`,
`TEST_MODE`, `SET_DATA`) y `GET_DATA` (`0x43ce4fc7`) no está referenciada. Esto corrige el conteo de
cuatro nombres que daba S73.

## 2. `AVR` (2) — accesorio LANC-AVR

`AVR` no es un módulo: son las notificaciones de attach/detach de la clase de accesorio **LANC-AVR**
gestionada por `ACCY`. Lo decisivo es el log de fábrica
`[ACCY][DEBUG][FACTORY]:%d:LANC-AVR Attached` (`0x43c252b4`).

| vaddr | cadena | xref / función | interpretación |
|---|---|---|---|
| `0x43c25502` | `[ACCY][DEBUG][AVR] NotifyDetached(%d)` | `0x43565688` / `0x43565680` | Notificación de desacople del accesorio AVR. |
| `0x43c25528` | `[ACCY][DEBUG][AVR] NotifyAttached(%d)` | `0x435656dc` / `0x435656d4` | Notificación de acople del accesorio AVR. |

El handler de `0x43565680` (imprime `NotifyDetached`) escribe el GPIO mask `0x2000100` y configura
`0xa000012`; el de `0x435656d4` (imprime `NotifyAttached`) escribe `0x2000000`.

## 3. `ADR` (1) — dirección de apertura de imagen

Única aparición del token: `>>[FILE_NUM]%x [ADR]%x [SIZE]%x` dentro de `[CAM_UTIL_SENS]`. La función
`0x43901d50` construye el mensaje de IM open con tipo 1 en `[0]`, `file_num` en `[2]`, **dirección en
`[4]`**, tamaño en `[8]`, flags en `[0xc..0xf]` y ceros en `[0x10]/[0x14]`. `ADR` es, por tanto, la
dirección de carga del buffer/imagen, no un subsistema.

| vaddr | cadena | xref / función | interpretación |
|---|---|---|---|
| `0x43cce3fa` | `[CAM_UTIL_SENS]: >>[FILE_NUM]%x [ADR]%x [SIZE]%x` | `0x43901e42 (+3)` / `0x43901d50 (+2)` | Traza de apertura: FILE_NUM, ADR (dirección) y SIZE. |

Las variantes en minúscula `[Adr]` (`0x43cce34f`, `0x43cce5ce`) y los logs de apertura síncrona
(`0x43cce491`+) pertenecen a la misma capa `CAM_UTIL_SENS`.

## 4. `BKID` (4) — backup ID

Las cuatro cadenas son logs de callback de cambio de **backup ID**: `CB for BKID change` y el
registro/anulación del callback en `LIF_DEBUG`. La identificación no depende del contexto: el propio
firmware usa `BKID_*` como identificador de backup (`backupId size (BKID_SDF_QTBL_C)`,
`Backup_read(BKID_UPM_BOOT_CIPA_FLAG)`, `BKID_VDF_CIPA_MEM`, ...).

| vaddr | cadena | xref / función | interpretación |
|---|---|---|---|
| `0x43cce1ea` | `[CAM_UTIL_SENS]: CB for BKID change [BKID]:%x [Size]:%x` | `0x43901306` / `0x439012d0` | Callback de cambio de BKID con tamaño de datos. |
| `0x43cfb04d` | `[LIF_DEBUG]:  :[BKID] %x, [DataSize] %x` | `0x43a1c9f8` / `0x43a1c9d8` | Notificación de cambio de BKID y tamaño. |
| `0x43cfb09c` | `[LIF_DEBUG]: Reg CB func result [BKID]:%x, [Erro]:%x` | `0x43a1ca68` / `0x43a1ca1e` | Resultado de registrar el callback por BKID. |
| `0x43cfb1a8` | `[LIF_DEBUG]: UnReg CB func result [BKID]:%x, [Erro]:%x` | `0x43a1cb62` / `0x43a1cb3c` | Resultado de anular el callback por BKID. |

## 5. `AVOUT` (2) — accesorio AvOut

Misma familia `ACCY` que `AVR`. El log de fábrica `[ACCY][DEBUG][FACTORY]:%d:AvOut Attached`
(`0x43c25260`) identifica la clase. El dispatcher `0x435646a4` separa los tipos: 0 = AVOUT
(`0x435655a4`, mask `0x7000100`), 1 = JIRO (`0x43566074`, `0x7000200`), 4 = HELLO (`0x4356468c`,
`0x7000000`) y 5 = AVR (`0x4356573c`, `0x7000300`); el caso por defecto devuelve NULL/UNSUPPORTED.

| vaddr | cadena | xref / función | interpretación |
|---|---|---|---|
| `0x43c2549e` | `[ACCY][DEBUG][AVOUT] NotifyDetached(%d)` | `0x43565510` / `0x43565508` | Notificación de desacople de AvOut. |
| `0x43c254c6` | `[ACCY][DEBUG][AVOUT] NotifyAttached(%d)` | `0x43565554` / `0x4356554c` | Notificación de acople de AvOut. |

## 6. `CAMCORE` (37) — librería Camera::CamCore

`CAMCORE` es el core de cámara (`Camera::CamCore`, confirmado por RTTI `N6Camera7CamCore8RdcImageE`
en `0x43c906b6` y `N6Camera7CamCore13SplitRdcImageE` en `0x43cb0b94`). Agrupa: selección de
controlador por modo y tablas SGC (`0x43c905ca`, `0x43c90606`, `0x43c909f7`), procesado RDC/PFR
(`0x43c9073a`–`0x43c90ca3`), configuración AIF (`0x43c90a96`–`0x43c90bed`), memoria y recursos
(`0x43c90846`–`0x43c90ec5`), interrupciones, powersave, ExlHelper y setter DMA
(`0x43c910a4`–`0x43c91160`). La cadena final conecta con la corrección de puntos defectuosos del
sensor (`Acl::CAMHEAD_Z1C::setDefectPt`, `0x43cebcb2`, función `0x439cd794`).

| vaddr | cadena | xref / función | interpretación |
|---|---|---|---|
| `0x43c905ca` | `[CAMCORE]: GetFlowType: No SgcTable. imgmode=%d, cammode=%d` | `0x436c22b8` / `0x436c227c` | GetFlowType no encuentra SgcTable para imgmode/cammode. |
| `0x43c90606` | `[CAMCORE]: Warning! The controller for mode(%d) does not implemented` | `0x436c24d2` / `0x436c243c` | No hay controlador implementado para el modo solicitado. |
| `0x43c9070a` | `[CAMCORE]: SetCasRMaxRatio parameter error [%d]` | `0x436c2880` / `0x436c2868` | Validación de SetCasRMaxRatio. |
| `0x43c9073a` | `[CAMCORE]: typeof(rawIn) must be RdcImage.` | `0x436c2bfc` / `0x436c2b48` | RdcImage: la entrada debe ser RdcImage. |
| `0x43c90765` | `[CAMCORE]: Cannot read with skipping when 4bit RAW.` | `0x436c2c70` / `0x436c2b48` | RdcImage: no se puede leer con skipping en RAW de 4 bits. |
| `0x43c90799` | `[CAMCORE]: typeof(rawOut) must be RdcImage.` | `0x436c2e42` / `0x436c2d4e` | RdcImage: la salida debe ser RdcImage. |
| `0x43c90846` | `[CAMCORE]: [Error] Memory for PFR couldn't be freed. : unit_handle = %x` | `0x436c38b6` / `0x436c3890` | Liberación de memoria PFR fallida (unit_handle). |
| `0x43c9088e` | `[CAMCORE]: [Error] Memory for PFR couldn't be allocated.` | `0x436c39cc` / `0x436c38e4` | Reserva de memoria PFR fallida. |
| `0x43c908e7` | `[CAMCORE]: MemoryPool has no space.` | `0x436c3e68 (+10)` / `0x436c3e14 (+10)` | MemoryPool sin espacio (11 sitios de llamada). |
| `0x43c90982` | `[CAMCORE]: SplitEEController: Memory Close Error!(VATR)` | `0x436c45aa` / `0x436c4560` | SplitEEController: error al cerrar memoria (VATR). |
| `0x43c909ba` | `[CAMCORE]: NOT SUPPORT!` | `0x436c463c` / `0x436c45d8` | Operación no soportada. |
| `0x43c909f7` | `[CAMCORE]: No SgcTable. imgmode=%d, cammode=%d, hFlip=%u, vFlip=%u` | `0x436c4e4e` / `0x436c4e20` | Segunda variante de SgcTable ausente (incluye flips). |
| `0x43c90a96` | `[CAMCORE]: AIF%d out[%d] > memsize[%d]` | `0x436c4fdc` / `0x436c4f6c` | AIF: salida mayor que el tamaño de memoria. |
| `0x43c90abd` | `[CAMCORE]: Extent size must be just divided into equal size.` | `0x436c5006` / `0x436c4f6c` | AIF: el extent debe dividirse en partes iguales. |
| `0x43c90afa` | `[CAMCORE]: AIF%d out[%d] memsize[%d] extent[%d]` | `0x436c5034` / `0x436c4f6c` | AIF: traza de memoria/extent calculados. |
| `0x43c90b2a` | `[CAMCORE]: AIF%d Extent count[%d] must be 1 or 2.` | `0x436c505e` / `0x436c4f6c` | AIF: el número de extents debe ser 1 o 2. |
| `0x43c90b5c` | `[CAMCORE]: AIF%d pbl_aif_set_func error[%d] size[%d] dest[%d] iib[%d] addr[%08x]` | `0x436c516e` / `0x436c50dc` | AIF: error de pbl_aif_set_func con tamaño/destino/iib/addr. |
| `0x43c90bad` | `[CAMCORE]: AIF%d RDC param error. encType[%d] lcut[%d] rcut[%d]` | `0x436c51f6` / `0x436c50dc` | AIF: parámetros RDC inválidos (encType/lcut/rcut). |
| `0x43c90bed` | `[CAMCORE]: AIF%d RDC none. encType[%d] lcut[%d] rcut[%d]` | `0x436c5222` / `0x436c50dc` | AIF: RDC desactivado (encType/lcut/rcut). |
| `0x43c90ca3` | `[CAMCORE]: PFR in width[%d] > 596` | `0x436c5462` / `0x436c53d8` | PFR: ancho de entrada superior a 596. |
| `0x43c90e8d` | `[CAMCORE]: Interruption::AddStartCallback(%d, %08x) NG.` | `0x436c63d6 (+1)` / `0x436c63a8 (+1)` | Interruption: AddStartCallback rechazado. |
| `0x43c90ec5` | `[CAMCORE]: ResourceBase::Release was called without acquire. %08x` | `0x436c6b44` / `0x436c6b3c` | ResourceBase: Release sin acquire previo. |
| `0x43c90f07` | `[CAMCORE]: MonPowersave[%d] is already Enabled !` | `0x436c7450` / `0x436c723c` | MonPowersave ya estaba habilitado. |
| `0x43c90f38` | `[CAMCORE]: SGC1: Invalid imager_if_type enum %d` | `0x436c79bc` / `0x436c7950` | SGC1: imager_if_type inválido. |
| `0x43c90f98` | `[CAMCORE]: ExlHelper: Cannot convert CamMode[%d] to ExlMode.` | `—` / `—` | ExlHelper: CamMode sin conversión a ExlMode (sin xref PIC localizada). |
| `0x43c90fd5` | `[CAMCORE]: ExlHelper: Invalid imager_mode_aspect[%d]` | `—` / `—` | ExlHelper: imager_mode_aspect inválido (sin xref PIC localizada). |
| `0x43c9100a` | `[CAMCORE]: ExlHelper: Invalid imager_if_type[%d]` | `0x436c7d30 (+1)` / `0x436c7d08` | ExlHelper: imager_if_type inválido. |
| `0x43c9103b` | `[CAMCORE]: ExlHelper: Invalid imager_physical_coding[%d]` | `0x436c7d6e` / `0x436c7d08` | ExlHelper: imager_physical_coding inválido. |
| `0x43c91074` | `[CAMCORE]: ExlHelper: Invalid imager_aspect[%d]` | `0x436c7dd2` / `0x436c7d08` | ExlHelper: imager_aspect inválido. |
| `0x43c910a4` | `[CAMCORE]: [Setter] DMA Err open [%d]` | `0x436c9020` / `0x436c900c` | DMA Setter: error al abrir el canal. |
| `0x43c910ca` | `[CAMCORE]: [Setter] DMAC_CH_NONE` | `0x436c9066` / `0x436c9050` | DMA Setter: DMAC_CH_NONE. |
| `0x43c910eb` | `[CAMCORE]: [Setter] listCount = %d` | `0x436c9082` / `0x436c9050` | DMA Setter: traza de listCount. |
| `0x43c9110e` | `[CAMCORE]: [Setter] DMA Err status [%d]` | `0x436c9146` / `0x436c9050` | DMA Setter: error de estado. |
| `0x43c91136` | `[CAMCORE]: [Setter] DMA Err set_func [%d]` | `0x436c917e` / `0x436c9050` | DMA Setter: error en set_func. |
| `0x43c91160` | `[CAMCORE]: [Setter] DMA Err start [%d]` | `0x436c91bc` / `0x436c9050` | DMA Setter: error al arrancar. |
| `0x43cebc93` | `!/6;>?[CAMCORE]: loadDefectPos` | `—` / `—` | loadDefectPos (cadena precedida de bytes binarios; sin xref PIC localizada). |
| `0x43cebcb2` | `[CAMCORE]: Acl::CAMHEAD_Z1C::setDefectPt return err.` | `0x439cd7f6` / `0x439cd794` | setDefectPt de CAMHEAD_Z1C devuelve error. |

Tres cadenas (`0x43c90f98`, `0x43c90fd5`, `0x43cebc93`) no tienen xref PIC localizada con el patrón
`ldr`/`add`; no se les asigna función contenedora. La expansión de «SGC» no está documentada en el
binario (`NO_VERIFICADO`).

---

## 7. Frontera y correcciones

- **Qué mide cada canal ADC** (`unit_no`/`ch_no` frente a temperatura, alimentación, etc.):
  `NO_VERIFICADO`; requiere esquema o traza en cámara.
- **Semántica eléctrica de AvOut/LANC-AVR**: el binario solo muestra las máscaras GPIO y el
  dispatcher; `NO_VERIFICADO` más allá de eso.
- **Corrección a S73:** hay cinco cadenas `ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_*`, no cuatro; la
  quinta (`GET_DATA`, `0x43ce4fc7`) existe pero no está referenciada.
- **A7S:** los seis prefijos están ausentes del mapa S79 de A7S (fw3.20).

## 8. Trazabilidad

- Blob: `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21), base `0x43541000`.
- Datos: `analysis/s103_prefixes/a6000_prefixes.json` (cadenas, xrefs, funciones, notas).
- Prueba: `tests/test_s103_prefixes.py` (conteos, bytes exactos, xrefs PIC y ausencia en A7S).
- Conteo reproducible: mismo regex que `tests/test_s79_modules.py` (`[A-Z][A-Z0-9_]{2,}` en
  cadenas imprimibles de ≥6 bytes).
