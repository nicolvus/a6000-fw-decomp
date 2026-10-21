# Prueba S64 de escritura de SilentShutter en RAM

Etapas `0-antes`, `1-escritura`, `2-tras-escribir-1`, `3-persistencia`, `4-revertir`, `5-tras-revertir`: página 0x83edf000 y transcripciones. Resultado: la escritura en RAM no persiste ni cambia el obturador (ver doc S64).

- Cámara: ILCE-6000, fw 3.21, 2026-10-20. Generado con: senser_silent_backup_diff.py / shell.
- Solo lectura sobre la cámara salvo donde el doc de la fase indique escritura en RAM.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `0-antes/SHA256SUMS` | 88 | `d91b90c445689e7af94c871aa2e067657b11dd26d1550af4b145537949ee9847` |
| `0-antes/mem_83edf000_1000.bin` | 4096 | `cb0e23ef80c8592ad7a6b461d703246821192b687d3cf05096728f67823321a7` |
| `1-escritura/shell.txt` | 408 | `7911ead75fe767e73eea438d1b21a91b4d2fcaf8790829ec913979bc9a63e036` |
| `1b-test-echo/shell.txt` | 497 | `d0cfa23ec167d0944349403a7a40d0409752bb973bfbcde9db25827ef1112380` |
| `1c-comprobacion/SHA256SUMS` | 88 | `9e4d2879d9c159160204f68a5acd40ad0194ced4ff528c87f094c4ed53c459f8` |
| `1c-comprobacion/mem_83edf000_1000.bin` | 4096 | `732a1cf4bb4c842e5f50d988c87d40227ca739e64f5371d9041bf0403b4f5779` |
| `2-tras-escribir-1/SHA256SUMS` | 88 | `c4405a92af30f1583254222e3d1fff11e834577287986bc6c7dcac39952c6d06` |
| `2-tras-escribir-1/mem_83edf000_1000.bin` | 4096 | `874e7b53a864b142cde971b2a43d22a6df32bb05816ea639a5b594b729641a10` |
| `3-persistencia/SHA256SUMS` | 88 | `3ea387f23fbcad071528de1e82ee2e18d0679b08b9c8966d847dbd8e2edad95c` |
| `3-persistencia/mem_83edf000_1000.bin` | 4096 | `df7af1c93a7a4fc156f27a69d14b5ef29499915ecb296167e2fb4660fa6ad2c2` |
| `4-revertir/shell.txt` | 408 | `b74e9e01379c8fe4e0939c80dae77b06a164f3155841fc43347b39719264d88e` |
| `5-tras-revertir/SHA256SUMS` | 88 | `ce5b03d4e6201b0c9bc5953818cbf290c844f1f342320750f4c43da7a2a83d42` |
| `5-tras-revertir/mem_83edf000_1000.bin` | 4096 | `3d669b9c3ff4456c9e1aa27d52255b54754489be70841b7e00a61e9424a76004` |
