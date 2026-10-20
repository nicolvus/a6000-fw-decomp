# S48 — proveedor del servicio de registro `+0x1ec` y paquete `0x301d7`

Sesión 19-10-2026; continuación de [S47](s47-payload-producer-and-order.md). Hito S46–S52 **abierto**.
Método: REA (MCP, sesión única `session_daemon.py`, proyecto temporal `ephemeral-source-immutable`) sobre
`av-cam.bin` (SHA-256 `b60c845c…56bb9`, idéntico antes y después) + desensamblado Thumb con `llvm-objdump`
sobre una copia ELF en scratchpad. Ghidra histórico no usado. Sin firmware ejecutado.

## VERIFICADO

- `0x435612b4` = wrapper `blx [[[GOT 0x440205c0]+0x14]+0x1ec]`; `0x43561298` = igual con `+0x1e8`;
  `0x43561324` = igual con `+0x200`. GOT `0x440205c0=0x43541000`; `[0x43541014]=0x435410b4` (tabla de servicios).
- La tabla `0x435410b4…` tiene 8 palabras no nulas de 192 (`0x435410b8..0x435410d4`, no son punteros a código);
  los slots `+0x1e8/+0x1ec` (`0x4354129c/0x435412a0`) valen 0 en el blob. REA `xrefs`: solo los leen los wrappers
  (`0x435612a4`, `0x435612c0`); ningún escritor en la imagen. **El proveedor no está en `av-cam.bin`:** son
  slots de importación que rellena el cargador/host (conclusión por ausencia de escritores directos; un
  escritor indirecto no se descarta).
- Segundo uso de `0x301d7`: literal `0x4378a030`, cargado por `0x43789fe4` en la función **`0x43789fdc`**
  (código sin función definida en REA): `h = svc1e8(0x301d7, *0x43e953f0)` (`0x43789fe6`);
  `svc200(0x52, 0, *0x43e95400)` (`0x43789ff6`); luego `0x43788fd0(1,1,0xff,0xff…)`, `0x43788c2c(h)` y
  `0x43788fd0(b,b,b,h)`. La función con `svc1ec(0x301d7, 0x43e953f4, 0x43789cc1, 0)` (`0x4378a3d0`) es la
  siguiente; `0x43e953f0/0x43e953f4` son contiguos. Contrato `+0x1e8` (crear/obtener manejador por ID) y
  `+0x1ec` (registrar callback) **inferido** por uso, no por definición.
- Barrido de bytes `d7 01 03 00` en `av-cam.bin`: solo `0x4378a030` y `0x4378a4a8` (ambos literales ya explicados).

## NO_VERIFICADO / límites

- Productor de `paquete+0x1c/+0x1e` y del paquete `0x301d7`/clave `0xce`: queda **fuera de la imagen** (host que
  invoca el callback); no localizado. Sin evidencia para valor2=2.
- `libObj.so`, `libInfraMediaCommon.so`, `libsencore.so` contienen ~314–628 apariciones de `d7 01 03 00`:
  sin analizar (probable tabla compartida); candidato para S49 si se busca el emisor en userland.
- `procedure_callers` es parcial (omite referencias de código sin función). Sin evidencia nueva sobre obturador electrónico.
