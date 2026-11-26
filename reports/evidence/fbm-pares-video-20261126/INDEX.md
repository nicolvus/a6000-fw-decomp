# Evidencia — tabla de pares (userID,mediaID) → sector FBM y su cruce con la Sector Manager Info Table

Sesión 26-11-2026. Sólo lectura: no se tocó la cámara ni se escribió en NAND. Sin `git`.

Fuentes:
* `analysis/camera-extract/usr/lib/libmpr.so` — 10 321 204 B, fw 3.21, SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`.
  `.text` `0x00120228`-`0x007A3E84` · `.rodata` `0x007A3E90`-`0x00956750` · `.data` `0x009C42E8`-`0x009DF808` · `.bss` `0x009DF808`-`0x00ADBB04`.
  Offset en fichero = VA para el primer `PT_LOAD`; `.data`: VA `0x9C42E8` = off `0x9BC2E8`.
* `analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin` — 1 GiB de RAM física desde la física `0x80000000`
  (offset en fichero = física − `0x80000000`).
* `analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` — 10 485 760 B (10 MiB de la partición FBS).

| Fichero | Qué contiene |
|---|---|
| `tabla_pares.py` / `tabla_pares.txt` | vuelca las 37 filas de `0x9D23FC`, localiza sus copias físicas, localiza la SMT de `0xA3699C`, y publica la tabla cruzada de 30 filas |
| `diff_copias.py` / `diff_copias.txt` | compara las dos copias físicas de la tabla de pares con la imagen del `.so` (4 filas con estado de runtime en `+0x10`/`+0x14`) |
| `nflasha_sectores.py` / `nflasha_sectores.txt` | censo de los 30 sectores FBM (cabecera, firma, registros, trailer) en `dev_nflasha4.bin` y rutas `ms:/` legibles |
| `busqueda_4088.md` | barrido exhaustivo de `[X+0x4088]` / `[X+0x408c]` (0 aciertos) y quién registra/libera la pareja (`0x2B1E34`) |
