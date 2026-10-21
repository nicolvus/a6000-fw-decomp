# NVRAM antes/durante/después de forzar Silent=1 (S64)

`1-base`, `2-silent`, `3-revertido`, cada uno en `_mem` y `_flash`. `1-base_flash.bin` sha256 `db9e7324…5e8ca` es la línea base de las comparaciones de S65.

- Cámara: ILCE-6000, fw 3.21, 2026-10-20. Generado con: senser_silent_backup_diff.py.
- Solo lectura sobre la cámara salvo donde el doc de la fase indique escritura en RAM.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `1-base_flash.bin` | 852647 | `db9e7324f3cc8d65642bff7e6218f07f4e0356b769ee4edf00e1964cd5e5f8ca` |
| `1-base_mem.bin` | 852647 | `335f32589eeb1146af6c216a2dd6b0e79187f65794e55364bacf7bab81770b4b` |
| `2-silent_flash.bin` | 852647 | `db9e7324f3cc8d65642bff7e6218f07f4e0356b769ee4edf00e1964cd5e5f8ca` |
| `2-silent_mem.bin` | 852647 | `48be833ac54f9fb0b6117a973c229a5df6ffbc81c76b7e8daad9f13b2bd32831` |
| `3-revertido_flash.bin` | 852647 | `db9e7324f3cc8d65642bff7e6218f07f4e0356b769ee4edf00e1964cd5e5f8ca` |
| `3-revertido_mem.bin` | 852647 | `48be833ac54f9fb0b6117a973c229a5df6ffbc81c76b7e8daad9f13b2bd32831` |
| `SHA256SUMS` | 583 | `db91bc622facba324f103345e7981f526d6d78a5fb8f6e72f1c14768945420d3` |
