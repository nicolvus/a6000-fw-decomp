# S113 — `[CAM_DMM]`: el gestor de memoria dinámico de la cámara

**Hito de la línea de ingeniería inversa general** (no afecta a la decisión del obturador
electrónico: S51 sigue con A/B/C = NO).

Informe: [analysis/s113_cam_dmm/dmm_module.md](../../analysis/s113_cam_dmm/dmm_module.md) ·
Datos: `summary.json`, `func_map.json` · Test: `tests/test_s113_cam_dmm.py`.

## Hallazgo central

`[CAM_DMM]` es el **servidor de memoria dinámica** del firmware: 54 trazas (todas de error)
en `0x43cce6ae`–`0x43ccf1c3`, con la implementación concentrada en **25 funciones
contiguas** (`0x439011d8`–`0x43903d5c`).

## Qué se ha reconstruido (verificado contra bytes)

1. **11 operaciones**: `AllocNew`, `AllocNewRdv` (**rendezvous**, confirmado por
   `MemoryHandle::AllocRendezvous` `0x43cceb4c`), `AllocShare`, `Free`, `FreeRdv`, `Open`,
   `Close`, las cuatro `MemoryHandle::*`, y las tres asíncronas `AsyncAllocNew`,
   `AsyncAllocRule`, `LoadExtraMap`.
2. **4 clases de error** del DMM: `ERR_DMM_RET_CODE` (10), `ERR_DMM_DIFFERENT_COMP` (10, con
   `msg_id`/`my_id` → *la unidad es de otro componente*), `ERR_DMM_HANDLE` (4), `ERR_DMM_OPEN`
   (5); y 4 de capa **OSAL** (`ERR_OSAL_MSGQ`, `ERR_OSAL_HANDLE`, `ERR_OSAL_UIPC`,
   `rcv Invalid Src!`) en las operaciones asíncronas → la frontera **DMM↔OSAL** es real
   (S38).
3. **Mapa función→traza**: una función por operación y un bloque asíncrono
   (`AsyncAllocNew` `0x439037c0` con 24 trazas, `AsyncAllocRule` `0x43903b80` con 17,
   `LoadExtraMap` `0x43903d5c` con 8).
4. **El userland es cliente, no reimplementación**: los símbolos exportados de `DmmAccess`
   en `libmprctrl.so` (`DmmAllocateNEWAndOpen_body`, `DmmShare`, `DmmCloseORFree_body`,
   `DmmOpen`, `GetUnitHandleFromDmmAlloc`, `GetDMMRetMsg`, `CheckOSALRetCode`…) se
   corresponden uno a uno con la API del firmware (S37).
5. **Diferencial A7S fw3.20**: 0 trazas con el prefijo, pero **50 de las 54** tienen mensaje
   equivalente sin etiqueta; las 4 restantes son `AllocNew`, que en la A7S se registraba como
   `AllocNew(DMM_OPTION_NOUNIT_WARN): ERR_DMM_RET_CODE!: %x` (`0x43cb4f99`) y que la fw3.21
   sustituyó por cuatro mensajes detallados.

## Abierto / NO VERIFICADO

- Los valores numéricos de `ERR_DMM_*` y `ERR_OSAL_*` (el firmware solo imprime el nombre).
- El formato del mensaje OSAL de la capa asíncrona y la tabla de reglas de `AsyncAllocRule`.
- Qué "mapa extra" carga `LoadExtraMap`.
- Nada de esto cambia S51.

## Scripts

`analysis/s113_cam_dmm/extract_dmm.py`: extracción de las 54 cadenas, mapa función→traza
(esquema PIC + prólogos Thumb) y diferencial con la A7S.
