# S156 — `[TP_R]`: el módulo de panel táctil de la fw3.21 de la A6000 (22-10-2026)

**VERIFICADO** con bytes (sin REA/Ghidra), regla **estricta**; 19 tests en
`tests/test_s156_tp_r.py`. Informe `analysis/s156_tp_r/tp_r.md` · JSON `tp_r.json`.

## Qué es
`[TP_R]` etiqueta un **módulo de panel táctil (TP)**: una *tarea* con cola OSAL propia,
temporizador, ciclo de vida `boot_init_tp`/`boot_exit_tp` y una **tabla de comandos de
depuración** registrada en el monitor `DebugVfcCmd` bajo el nombre `tp`
(`0x4366cae8` → `bl 0x435ab6f0`): `start`, `set_mode` ("Set TP Mode"), `print_xy`,
`dds_on` ("DDS On"), `dds_off` ("DDS Off"); tabla en `0x43fe3f28` (entradas de 12 B
`{nombre, descripción, handler}`). Código `0x4366c2a4`–`0x4366cd38` (18 funciones);
colas OSAL log `0x008f0139`, eventos `0x005c011c`, control `0x01010227`
(`osal_rcv_msg` bloqueante en `0x4366c864`); publica eventos de 12 B con ids
`0x112/0x113/0x114` y `0x136/0x13c`. **La sigla no se desarrolla**: no hay bytes que
expandan "TP" ni "DDS".

## Las 18 trazas
18 cadenas `[TP_R]` en `0x43c80f23`–`0x43c812f3`: **14 vivas** (20 sitios PIC en
**8 funciones**) y **4 muertas**; además **3** con la etiqueta antigua `[TP R]`, todas
muertas. Contenido: 10 errores de la API OSAL, `boot_init_tp/boot_exit_tp come`,
`unkown tp_type`, `unknown cmd`, `read size error`. Mapa función→traza (8 funciones:
`0x4366c388`, `0x4366c568`, `0x4366c624`, `0x4366c6e8` = `boot_exit_tp`, `0x4366c840`
= recepción, `0x4366c978`, `0x4366ca92` = despachador, `0x4366caf4` = `boot_init_tp`)
en `analysis/s156_tp_r/tp_r.md` §4.
## Relación con S151 y con `[DMMYSIOCOM]`
* **S151 CONFIRMADO**: las trazas no salen por `printf` sino por `0x4366c300`
  (`push {r3}` → `movs r2,#0x9a` → `osal_try_valloc_msg` → `vsnprintf` →
  `osal_snd_msg`), **miembro de la familia de reporters**, con el **GID de log
  `0x008f0139`**, el mismo que `[PANDA]`, `[ACCY]`, `[CAM_UTIL_*]` y `[CAMERA_MAIN_FC]`;
  recuentos estricto **43 / 0 / 0** (A6000/A7S/A6300, reproduce S151) y laxo
  **561 / 0 / 2**.
* **`[DMMYSIOCOM]` NO es el mismo código**: los 2 "textos comunes" que S130 encontró
  son las plantillas OSAL `ERR. osal_snd_msg…` / `ERR. osal_free_msg…`, que en la A7S
  (`0x43c73764`/`0x43c73792`) y el A6300 (`0x43d7296b`/`0x43d72999`) están bajo
  `[DMMYSIOCOM]`, módulo que **sigue intacto en la A6000** (`0x43c72e7d`/`0x43c72eab`,
  ref. `0x43628a5e`/`0x43628a80`); código en zonas distintas (DMM `0x43628xxx`; TP
  `0x4366cxxx`) ⇒ **falso positivo textual**.
## Diferencial
| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| `[TP_R]` (guion bajo) | **18** | 0 | 0 |
| `[TP R]` (espacio) | 3 (muertas) | **3** — 0 vivas | **4** — 0 vivas |
| trazas vivas del módulo TP | **14** | 0 | 0 |
| tabla de comandos | `0x43fe3f28` | `0x43fe54d0` | `0x441a59c0` |

El **módulo TP existe en los tres** (misma tabla de 5 comandos, mismo nombre `tp`); la
fw3.21 **añade 15 trazas** a un módulo antes silencioso (coherente con S128).
## Para la línea del obturador
**Ninguno**: barrido de las 21 cadenas (`shut`, `silent`, `electro`, `mech`, `sensor`,
`exposure`, `readout`, `imager`, `curtain`…) → la única coincidencia es `read` en
`[TP_R]: ERR. read size error` (tamaño leído por una llamada OSAL). **S51 (A/B/C = NO)
se mantiene**.

## NO VERIFICADO / abierto
Sigla "TP" y "DDS" sin desarrollar; `<Water>` y `ex_status`/`ex_info` sin interpretar;
**no hay nombre de fichero fuente** en el módulo; no se ha localizado el consumidor de
los eventos en la cola `0x005c011c`; nombres de `0x43561244`/`0x435613b0` deducidos del
texto de las trazas.
## Revisión del agente principal
*(vacío)*