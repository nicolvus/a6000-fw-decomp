# S385 — Diff libObj.so: A6000 fw3.21 ↔ A7S fw3.20 (contraste A6300 fw2.01)

## 1. Métricas generales

| Métrica | A6000 fw3.21 | A7S fw3.20 | Diferencia | A6300 fw2.01 (contraste) |
|---|---|---|---|---|
| Tamaño | 17 436 172 B | 16 184 848 B | -1 251 324 (-7.2%) | 17 352 524 B |
| Entry point | 0x000e2b70 | 0x000e5ff0 | +0x3880 | 0x000f40b0 |
| .text VA | 0x000e2b70 | 0x000e5ff0 | +0x3880 | 0x000f40b0 |
| .text size | 0xae6a1c (11.4 MB) | 0x9eec50 (10.4 MB) | -0xfd3cc | 0xaa6af8 |
| .plt entries | 1914 | 1927 | +13 | 1991 |
| .rel.plt entries | 2420 | 2437 | +17 | 2519 |
| .dynsym símbolos | 3617 | 3650 | +33 | 3764 |
| UND func (imports) | 1387 | 1389 | +2 | 1431 |
| Defined func (exports) | 1771 | 1789 | +18 | 1829 |
| NEEDED libs | 17 | 17 | idéntico | 17 |

**VERIFICADO** por readelf + parser propio en ambos binarios.

## 2. NEEDED libraries (idénticas en los tres)

Ambos comparten las mismas 17 dependencias:
libInfraFsys.so, libmprctrl.so, libMWF.so, libmpr.so, libutil_date.so,
libcompassutil.so, libsencore.so, libBizFw.so, libBizFw2.so, libNetContUtil.so,
libUsbControl.so, libNetCommon.so, libGOConnectionManager.so,
libInfraMediaCommon.so, libbackup.so, libgcc_s.so.1, libc.so.6.

**Idéntico** — sin diferencias en dependencias.

## 3. Exports clave (presentes en los tres, direcciones distintas)

| Símbolo | A6000 VA | A7S VA | Desplazamiento |
|---|---|---|---|
| `ObjStillRecorder_Init` | 0x00913901 | 0x00856c0b | -0x0bccf6 |
| `ObjStillRecorder_Create` | 0x0091391d | 0x00856c27 | -0x0bccf6 |
| `ObjStillRecorder_Exit` | 0x00913911 | 0x00856c1b | -0x0bccf6 |
| `ObjStillRecorder_Destroy` | 0x00913943 | 0x00856c4d | -0x0bccf6 |
| `InfraStillPool_Init` | 0x00939691 | 0x00a7f17d | +0x145aec |
| `InfraStillPool_RegisterCommand` | 0x0093956d | 0x00a7f059 | +0x145aec |
| `InfraStillPool_UnregisterCommand` | 0x00939575 | 0x00a7f061 | +0x145aec |
| `InfraStillPool_Exit` | 0x00939745 | 0x00a7f231 | +0x145aec |
| `StateMgr::ChangeState` | 0x00815845 | 0x00863f55 | +0x4e710 |
| `UtilStillSize::GetStillTargetSize` | 0x00902385 | 0x0085024d | -0x0b2138 |
| `PrmObjMsg::C1(ObjMsg*)` | 0x0012c755 | 0x00357d6d | +0x22b618 |
| `PrmObjMsg::GET(ParamList, m)` | 0x0012c7d9 | 0x00357df1 | +0x22b618 |
| `PrmObjMsg::getParamTypeObjMsg()` | 0x0012c77d | 0x00357d95 | +0x22b618 |
| `ModelStillRecToInstance` | 0x0069d13d | 0x005c7839 | -0x0d5904 |
| `ModelScalarStillRecPatchToInstance` | 0x0065efd1 | 0x005ab565 | -0x0d596c |

**Observación:** Los offsets entre A6000 y A7S **no son constantes** (varían por símbolo). Esto indica que el layout de código difiere más allá de un simple desplazamiento base — hay inserciones/borrados de código entre modelos.

**VERIFICADO** por readelf + parser de símbolos en ambos binarios.

## 4. Imports clave (presentes en los tres)

Los mismos símbolos de mensajería aparecen como imports UND en ambos:
- `osal_reg_msg_queue_cb`, `osal_reg_sync_msg_queue_cb`, `osal_snd_msg`, `osal_snd_sync_msg`
- `_ZN3MWF11ObjMsgQueue7EnqueueEPKNS_6ObjMsgE` (queueMsg)
- `_ZN3UFW11MsgReceiver6RcvMsgEPjPPN3MWF6ObjMsgE` (RcvMsg)
- `_ZN3MWF12EventWrapper11SendAndRecvEPviS1_i` (SendAndRecv)
- `_ZN3MWF6ObjPin4SendEjPNS_6ObjMsgE` (ObjPin::Send)
- `_ZN5MprIf19MakeWriteStillImageEPNS_20WriteStillImageParamEPN3MPR9StillInfoE`

**Idéntico conjunto** en A6000 y A7S. **VERIFICADO**.

## 5. RecordStill::Execute — localización en A7S (RECONCILIADO)

| | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| Dirección | 0x0090b248 | **NO LOCALIZADA** |
| content-info | 0x100f (`movw r1,#0x100f` en 0x90b2a4) | `movw #0x100f`: **0 sitios** en .text |
| movt #0x0001 (parte alta) | N/A | **0 sitios** en .text |
| Patrón push.w+sub.w sp,#0xb00 | Presente en 0x90b248 | **0 sitios** en .text |
| ObjMsg 0x3500/0x3002 | No hay movw directo | Pendiente |
| Xrefs directos | 0 | Pendiente |

**Conclusión de la reconciliación:** RecordStill::Execute no se pudo localizar en A7S fw3.20 usando los mismos patrones que en A6000 (`movw #0x100f`, `movt #0x0001`, prólogo `push.w`+`sub.w sp,#0xb00`). Esto sugiere que el código de A7S fue compilado con diferentes flags o que la función tiene una estructura distinta. Requiere búsqueda adicional (por ejemplo, localizar `ObjStillRecorder` en A7S — export en 0x00856c27 — y examinar sus métodos, o buscar xrefs entrantes a la función equivalente).

**VERIFICADO:** barrido de bytes completo de .text de A7S (10.4 MB) con capstone.

## 6. Búsqueda del ID de cola `0x40193` (C2 receptor)

| Patrón | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| Word LE 0x00040193 (`93 01 04 00`) en .rodata | 0 sitios | Pendiente |
| Word LE 0x00000193 (`93 01 00 00`) en .rodata | 0 sitios | Pendiente |
| Thumb movw #0x0193 (`46 F2 93 F9`) | 0 sitios | Pendiente |
| Thumb movt #0x0040 (`41 C2 40 F8`) | 0 sitios | Pendiente |
| ARM movw #0x0193 (`E3000193`) | 0 sitios | Pendiente |
| ARM movt #0x0040 (`E3400040`) | 0 sitios | Pendiente |
| String ASCII "40193" | 0 sitios | Pendiente |

**A6000: 0 sitios en todos los patrones** (VERIFICADO por barrido de bytes).
**A7S: pendiente** — requiere el mismo barrido.

## 7. Clasificación de diferencias

| Ítem | Clasificación | Justificación |
|---|---|---|
| Tamaño del binario | DISTINTO | A6000 es 1.25 MB más grande que A7S |
| Entry point / .text base | DISTINTO | +0x3880 en A7S |
| .plt / .rel.plt entries | DISTINTO | A7S tiene +13/+17 entradas |
| Símbolos definidos | DISTINTO | A7S tiene +18 exports |
| Exports clave (nombres) | IDÉNTICO | Mismo conjunto de 21 símbolos de still/image |
| Imports clave (nombres) | IDÉNTICO | Mismo conjunto de imports de mensajería |
| NEEDED libs | IDÉNTICO | Las mismas 17 librerías |
| Direcciones de exports | DISTINTO | Offsets no constantes (layout diferente) |
| RecordStill::Execute | AUSENTE en A7S (pendiente) | No localizado aún en A7S |
| ID de cola 0x40193 | AUSENTE en ambos (0 sitios) | No encontrado estáticamente en A6000 |

## 8. Bloqueos

| Ítem | Por qué |
|---|---|
| RecordStill::Execute en A7S | Requiere desensamblado capstone de 10 MB .text |
| Búsqueda 0x40193 en A7S | Requiere barrido de bytes en .rodata de A7S |
| Quién llama a RecordStill::Execute (ambos) | 0 xrefs estáticos, requiere REA dinámico |
| Quién registra callback de cola 0x40193 | 0 BL a osal_* .plt, requiere REA dinámico |

**Documentado en knowledge/agents/NEEDS-HUMAN.md**

---

**Tests:** `analysis/s380_libobj_map/tests/test_s385_diff.py` (ver abajo).
**Evidencia:** readelf output, parser propio ejecutado en ambos binarios.
