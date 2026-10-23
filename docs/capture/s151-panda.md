# S151 — el módulo `[PANDA]` (10 trazas) de la A6000 fw3.21

**VERIFICADO** (26 tests, `tests/test_s151_panda.py`): `[PANDA]` son **10 cadenas
contiguas** `0x43c9a599`–`0x43c9a7c8`, todas con la forma
`[PANDA]: Panda_SendMessage: <canal> osal_<valloc|snd>_msg error!\n` (5 canales × 2
tipos: `Pre1`, `Pre2`, `Post1`, `Post2`, `Async`). **10/10 referenciadas**, **15 sitios**
(regla estricta) en **4 funciones**: `F1_init` `0x437073cc` (5 valloc),
`F4_pre` `0x43707f8c` (4), `F5_post` `0x437081b8` (4), `F6_async` `0x437083e4` (2), más
el **logger privado** `0x43707324` (misma familia que el de `[CAMERA_MAIN_FC]`
`0x437b7158`: mensaje OSAL de 0x9a B por el **GID de log `0x008f0139`**).

**Qué es**: la **capa de envío de mensajes del subsistema de lente** (`Camera::Lens`,
zona `LENS_MOUNT`): un gestor con 5 canales y **7 colas OSAL** (ids `0x00f900bc`,
`0x00f90078`, `0x00f900d5`, `0x00f90191`, `0x00f90184`, `0x00f90520`, `0x00f90521`),
5 buffers de 0x40 B reservados con GID `0x00740017` y enviados por el thunk
`0x43561228`. `F1_init` lo llama `void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)`
(`0x43721624`, cadena `0x43c9ae4e`).

**Base textual de "Panda"**: sólo dos, y ninguna desarrolla la sigla — (a) el nombre de
función `Panda_SendMessage` en el propio texto; (b) los parámetros del drive de iris
`uc_PandaADErrorOpen` (`0x43c99267`, tabla `0x43febe04`) y `uc_PandaADErrorClose`
(`0x43c9927b`, tabla `0x43febe14`). **0** clases RTTI, **0** ficheros `*Panda*`, **0**
cadena independiente `PANDA` ⇒ **`[PANDA]` no es un módulo de logging registrado** (al
contrario que `LENS_MOUNT`) y la sigla queda **sin desarrollar**.

**Diferencial**: token **10 / 0 / 0** (A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01) y
**0/10** textos interiores en los otros dos → confirma S130. **Pero el código sí existe en
los tres**: los 7 ids de cola aparecen **1 vez en cada blob**, en el pool literal de la
función equivalente (`0x437073cc` ↔ `0x43729910` (A7S) ↔ `0x437648d0` (A6300)), con el
**mismo prólogo y la misma secuencia de `bl`**, salvo las llamadas al reporter de error
(F1: 19 vs 14 llamadas; F4: 7 vs 6; F5: 5 vs 4) ⇒ **lo propio de la fw3.21 de la A6000
es el logging, no la función** (patrón S130/S132/S136). `Camera::Lens::ODL` está en los
tres (15 apariciones cada uno).

**Línea del obturador**: 0/10 menciones de obturador, disparo, sensor o tiempos. El único
vínculo de "Panda" con un mecanismo es el par `uc_PandaADError*`, de la tabla del
**drive analógico del iris** (`0x43febd54`–`0x43febe60`) → **sin efecto en S51**.

**NO VERIFICADO**: significado de la sigla; fichero fuente (el código PANDA no contiene
ningún nombre de fichero); significado de `Pre1/Pre2/Post1/Post2/Async`; ids de cola
`0x00f9xxxx`; GID `0x00740017`; id de log `0x16`; papel de `0x00910042`; cola de datos que
recibe los mensajes de lente; equivalente A6300 de `F4/F5/F6`.

[Informe](../../analysis/s151_panda/panda.md) · [datos](../../analysis/s151_panda/panda.json).
Siguiente: decodificar los ids de cola y el GID `0x00740017`; averiguar qué tarea consume
los 5 canales y qué significan "pre"/"post"/"async" en la lente.
