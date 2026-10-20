# Tipos de unidad DMM y disposición del YC — sesión 14

Alcance: estático. ELF (Ghidra = ELF + 0x10000). Evidencia reproducible: `scripts/dump_dmm_unit_types.py` → `analysis/dmm-unit-types.json` (374 tipos); decompilados `analysis/ghidra/libobj-effect-*.json`.

## 1. Qué es `unitType` (VERIFICADO)

`unitType` es un **identificador de clase de unidad del gestor de memoria DMM** (módulo de kernel `kmod/dmm.ko`). La definición está en `ConfigData` (`.rodata`, 63 976 B): lista de registros `{unitType, 0, extentId…, 0xffffffff}`; cada tipo se compone de uno o más *extents* (bloques) cuyas dimensiones están en la tabla de extents del mismo `ConfigData` (tamaños NO decodificados). El tipo **fija tamaño y composición** del buffer; no es un código de formato de píxel.

- `DmmAccess::DmmAllocate(uint unitType)` / `DmmAllocateAndOpen(uint unitType)` reciben el tipo (argumento cargado de un literal; ejemplo en `0x90a850`/`0x90a902`).
- Unidad = entrada de 392 B en `.bss` de dmm.ko; handle u16 = `serial(6 bits)<<10 | índice(10 bits)` (comprobación `handle>>10 == byte[+0x2a3]`).
- Contadores por unidad: `+0x2a0` **alloc** (refcount de asignación: `Free` decrementa si >1), `+0x2a1` **open**, `+0x2a2` **rdv** (rendezvous), `+0x2a3` serial, `+0x2a4` estado (`Free` acepta 1–5 y 7; pasa a 4 = liberación diferida si `rdv`≠0). Cabecera de `/proc/dmm_units`: `handle type status alloc open rdv serial relation address size extent`.

## 2. Valores conocidos

| unitType | extent | Significado | Evidencia | Estado |
|---|---|---|---|---|
| `0x50b3f` | `0xed` | YC de still **1920×1080** («STL_YCC_1920P») | `0x1704e4` devuelve 1920×1080; mensaje «Cant Alloc STL_YCC_1920P» tras la 1ª reserva de `0x15fa74`; en el PlayData de PbCap es el `decBufferInfo` | tamaño VERIFICADO; nombre INFERENCIA por orden de cadenas |
| `0x220b2e` | `0x13d` | YC **640×480** | `0x1704e4` devuelve 640×480; tabla de clases de tamaño (idx 1 y 2) | VERIFICADO tamaño |
| `0xe0b00` | `0xe4` | «SDS_YCC» (YC con cabecera SDS) | «Cant Alloc SDS_YCC»; en PbCap es el `ycBufferInfo` | INFERENCIA |
| `0x243` | — (no está en la lista de 374) | alternativa del `dec` en la variante super-resolución | `0x15f37c`: `DmmAllocate(0x243)` | VERIFICADO el valor; significado NO |
| `0x173762 / 0x84d6d / 0x50d17 / 0x170d0c / 0x170d0b` | `0x4e / 0xa0 / 0xe8 / 0x53 / 0x52` | las 5 áreas de **salida** de `Execute` (JPEG principal, miniatura, screennail, …) | `0x90a810` las pasa a `DmmAllocate*(uint)`; las cinco existen en dmm.ko | VERIFICADO que son tipos |

**Corrección:** las sesiones 12–13 describían esos cinco números como «reservas en bytes». Son **tipos de unidad**. El tamaño real depende del extent (no decodificado).

Clases de tamaño (objeto de entrada de ObjEffect):
- `0x17206c`: `unitType = tabla[clase]`, tabla `{0, 0x220b2e, 0x220b2e, 0x50b3f}` (clase < 4; GOT `0x102f6a8` → datos `0xbf0a8c`).
- `0x15e1f8` (destino de WriteStill por clase de la petición): `0 → 640×360`, `1 → 640×480`, `2 → 1920×1080` (por defecto 640×360). Coincide con las tres cadenas `PBCAP_SIZE_*`. El recorder pide la clase en `0x1026` (`tabla[this+0x12c]`, 4 si >4).

## 3. Disposición del YC (qué se sabe)

| Aspecto | Resultado | Estado |
|---|---|---|
| Cabecera | Cada YC SDS lleva una **cabecera de 0x800 B** (`YcSdsAcsr`, ctor `0x141b84(handle, unitType, phys, 0x800,…)`); contiene colorimetría (+0x14c), rango Y (+0x14d), rectángulo de recorte, etc. ObjEffect copia colorimetría/yRange de ahí a `0x1072/0x1073` | VERIFICADO el uso; contenido completo NO VERIFICADO |
| Canvas | `0x1036 = {align_up(w,64), align_up(h,16)}`; región `0x1038 = {w,h}` reales; layout `{0,0}` | VERIFICADO (función ELF `0x146ac8` = `a*ceil(v/a)`) |
| Stride | no existe campo; el canvas alineado 64×16 es la única pista (¿ancho de línea alineado a 64 px?) | NO VERIFICADO |
| Planos Y y C | no se identifican fuera de dmm.ko/FEA; los tipos de 1 solo extent sugieren una región contigua | NO VERIFICADO |
| Submuestreo | no hay campo; para 1920×1080 el extent real no está decodificado | NO VERIFICADO |
| ¿Lineal o propio? | cada extent es un bloque contiguo; el layout interno lo fija el motor SDF/FEA | NO VERIFICADO |

## 4. Respuestas 1–10 del encargo

1. **Valores de PbCap:** `dec = 0x50b3f` (o `0x243`), `yc = 0xe0b00` (VERIFICADO en `0x15ebfc`).
2. **Valores del YC del visor (EE):** NO VERIFICADO. ObjEffect lo registra en tiempo de ejecución («Input YC.unitType [0x%x]») pero no hay constante estática; los tipos de los buffers de la cámara no se localizaron.
3. **Qué representa cada valor:** clase de unidad (tamaño/composición) — no formato.
4. **Lineal:** por extent, sí; layout interno NO VERIFICADO.
5. **Planos Y/C:** NO VERIFICADO.
6. **Información adicional fuera de RegionInfo:** **sí**, la cabecera SDS de 0x800 B (colorimetría, yRange…).
7. **Stride:** NO VERIFICADO.
8. **Alineaciones:** canvas 64×16 (VERIFICADO). `MprLib::EncodeStillOnMemory` (ver §5) avisa si un parámetro tiene `& 0x1ff != 0` (512 B).
9. **Errores ante tipo incompatible:** NO VERIFICADO para FEA; en dmm.ko existe `DMM_RET_ERR_UNIT_TYPE`.
10. **¿Convertir un tipo en otro con servicios existentes?** Sí: SDF resize/rotate (`ObjMsg(0x3900,0x3000)` de ObjEffect) rellena una unidad de un tipo desde otra (SDS_YCC → STL_YCC_1920P); también «super-resolución».

## 5. Rutas MPR con geometría explícita (nuevas)

- `MprLib::EncodeStillOnMemory` (mcmd `EncodeStillOnMemory`, ELF `0x717eb0`; Ghidra `0x727eb0`, `analysis/ghidra/libmpr-encodestill-onmemory-impl.json`): parámetros `{formato(1/6/8/0x10), srcVirtAddr, srcSizeX, srcSizeY, dstSizeX, dstSizeY, dstTgtSize, dstBufVirtAddr, dstBufSize, …}`. Traduce direcciones virtuales a unidad+offset con `0x5f6e70` (equivalente a `[MemInfo]GetUnitInfo`), recorta el destino a 1920×1080 (alinea a 8/16) y espera un evento (`0x3001`). **Exige que el origen esté dentro de una unidad DMM.** Es comando de mantenimiento; no hay llamador de producción localizado.
- `PlayStillSingleByAddress` (`FeaIf` `0x44e711`, mcmd con `[UnitHandle][UnitType][PhysAddr][Size][Width][Height]`) y `StillColorSpace`/`RotateDegree`: decodificación por dirección con geometría explícita.

## 6. NO VERIFICADO

Tamaños de los extents `0xed/0x13d/0xe4`, formato exacto del cuerpo del YC, tipos de unidad del visor y de la cámara, comportamiento de FEA ante tipos no previstos, significado de los 6 bits altos del handle fuera del serial.
