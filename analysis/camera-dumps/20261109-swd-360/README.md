# SWD 09-11-2026 — CFW 3.60 instalado (solo lectura, AP0, sin parar la CPU)

- `rd.log`/`rd2.log`: `+0x210` (EFCS) = 0, `+0x238` (Silent) = 0, tipo de Color Mode `+0x138` = 0, gamma `+0x153` = 0. La cueva `0x43fb7400`, la ranura de curvas `0x43faf300`, los punteros `0x440014b8/c0` y los ganchos (`0x437a4db2`, `0x437a4b62`, `0x437a44fa`, `0x437aafe0`, `0x437aa816`) están con sus bytes ORIGINALES: `pp_ram.sh` no ha escrito nada.
- `poll.log`: vigilancia de `cfg+0x100…+0x440` mientras el usuario intenta Silent On y varios ajustes de Picture Profile: solo cambian `+0x11c/+0x120/+0x124` (transitorios de 0,3 s); `+0x210`, `+0x238`, `+0x138…` y `+0x153` NO cambian: ninguna orden de escritura llega a `av-cam`.
- `klog.bin`: 1 MiB del log del kernel (`0x83400000`), sin errores de Silent ni de PP (no versionado).
