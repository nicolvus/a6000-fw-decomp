# Parche de Darwin (solo preparado, NO instalado) — 26-10-2026

`darwin_core_tipo0.bin`: copia de `fw321/.../0640_darwin/darwin_core.bin` con `0x20c78..0x20c7f` (en dirección Darwin, base `0x4200`) = `b 0x20c8e; nop; nop; nop`, es decir `0x20c74` devuelve siempre tipo de mecanismo 0 (sin bobinas, rama que ya existe en la A6000).
`darwin.sum.tipo0`: línea de suma con el CRC-32 recalculado (tamaño igual, 157 276 B).
No se ha generado FDAT ni se ha instalado nada. Informe: `docs/capture/darwin-via-actualizacion-2026-10-26.md`.
`fdat/` (ignorado por git): `firmware_packed.fdat`/`.dat` versión 3.22 con este parche, generado y verificado por descifrado con `scripts/darwin_fdat_build.py`. **No instalado.**
