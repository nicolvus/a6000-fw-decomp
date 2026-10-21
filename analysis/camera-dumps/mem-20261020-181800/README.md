# Lecturas de RAM por dirección física (18:18)

Archivos `mem_<dirección física>_<tamaño hex>.bin` leídos con `dd` sobre `/dev/mem`.

- Cámara: ILCE-6000, fw 3.21, 2026-10-20. Generado con: camera_telnet.py / shell de service mode.
- Solo lectura sobre la cámara salvo donde el doc de la fase indique escritura en RAM.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `SHA256SUMS` | 440 | `18541a3be69a2c947208b2b56cfe648f5e16cd3dcdb2eb03294a01f2a50e6f14` |
| `mem_82d90000_1000.bin` | 4096 | `d44d99c9d1784015cb33c8535daefe26d9509c9674b0652cb30ba0baea8e7c9f` |
| `mem_8303e000_1000.bin` | 4096 | `5e2f14465a26ebd84d5de2d5f13ccfed23f905ac2297d91e9954cb26311c64d0` |
| `mem_83438000_8000.bin` | 32768 | `f166dba43116a3b5252448ea30aaccd27a451a19b32547c31d13d99f7fa1131e` |
| `mem_93383000_1000.bin` | 4096 | `2f4856ea36475eed8a0aface9d5009d4f2fa1306bde40f8257dcdf365ba92298` |
| `mem_965de000_1000.bin` | 4096 | `b582493f27615d92d94e63179f3c35a1c80929cf9b96e8d25f3e24480c735948` |
