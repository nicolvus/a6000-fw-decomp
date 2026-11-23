# G97 — CFW 3.87 «Film»: Silent + 38 looks de sosang ajustados a la A6000 (23-11-2026)

Código: `scripts/lut/sosang_a6000.py` (adaptador A6000→escena desde 33 ARW + JPEG embebido, objetivo V-Log/STD, ajuste T+LUT), `scripts/lut/userland/films.c` + `film_userland.py` (hilo en viewUnified2.so con los 38 looks; selección y blob «FILM» en el Backup 0x150005 + ACK 0x1070218), `scripts/lut/film_patch.py` (av-cam: LUT, máquina y curva tras la gamma, LUT-T-1), `scripts/gui/build_cfw_film.py`. Tests `tests/test_g97_films.py` (6, Unicorn). Datos: `analysis/lut/g97/`; paneles `img/g97-prueba-DSC03769-*.jpg`.

- Adaptador: ΔE mediana 1,7 (33 fotos, RAW registrado sobre el JPEG). Hardware sobre píxeles reales: mediana 0,89 ΔE. Cámara simulada vs película sobre el RAW de DSC03769: mediana 2,0 ΔE.
- CFW 3.87: `build/cfw_film/pkg-3.87/package-3.87/firmware_packed.dat` sha256 0fac4425cdaf4bb02832fc147fdc0cfe9a5e345b846f7755a1f958d946e6ebe3, auditoría 29/29, SIN instalar. Arnés UI: menú Ajustes personalizados p4 muestra «Silent Shooting» y la carpeta «Film» (2 páginas, 8 filas); la fila Kodak 1 guarda «Kodachrome».
- Límites: la entrada de la LUT se supone el JPEG Estándar (LUT de fábrica ≈ identidad); el camino Backup userland→av-cam y la curva en vivo sin verificar en cámara; usar Estilo Creativo Estándar.

| N.º | Fila | Menú | Look (sosang) | Papel | Curva | ΔE fotos | ΔE HW en DSC03769 | ΔE cámara vs RAW | nodos al tope |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Kodak 1 | Ektachrome | Kodak Ektachrome 100 | — | T_grises | 0.51 | 0.66 | 2.05 | 158 |
| 2 | Kodak 1 | Ektar 100 | Kodak Ektar 100 | kodak_portra_endura | T_grises | 0.63 | 0.75 | 2.01 | 93 |
| 3 | Kodak 1 | Gold 200 | Kodak Gold 200 | kodak_ektacolor_edge | T_intervalos | 0.59 | 0.94 | 2.22 | 62 |
| 4 | Kodak 1 | Kodachrome | Kodak Kodachrome 64 | — | T_grises | 0.43 | 0.55 | 2.02 | 150 |
| 5 | Kodak 1 | Portra 160 | Kodak Portra 160 | kodak_portra_endura | T_grises | 0.56 | 0.66 | 1.89 | 148 |
| 6 | Kodak 1 | Portra 400 | Kodak Portra 400 | kodak_portra_endura | T_grises | 0.64 | 0.87 | 2.13 | 96 |
| 7 | Kodak 2 | Portra 800 | Kodak Portra 800 | kodak_portra_endura | T_grises | 0.60 | 0.79 | 2.00 | 62 |
| 8 | Kodak 2 | Portra800 +1 | Kodak Portra 800 (Push 1) | kodak_portra_endura | T_grises | 0.83 | 1.04 | 2.31 | 61 |
| 9 | Kodak 2 | Portra800 +2 | Kodak Portra 800 (Push 2) | kodak_portra_endura | T_grises | 1.05 | 1.15 | 2.43 | 70 |
| 10 | Kodak 2 | Ultramax 400 | Kodak Ultramax 400 | kodak_ektacolor_edge | T_intervalos | 0.60 | 0.87 | 2.07 | 56 |
| 11 | Kodak 2 | Verita 200D | Kodak Verita 200D | kodak_2383 | T_grises | 0.64 | 0.79 | 1.72 | 58 |
| 12 | Kodak 2 | Vision3 200T | Kodak Vision3 200T | kodak_2383 | T_grises | 0.66 | 0.88 | 1.71 | 74 |
| 13 | Kodak 3 | Vision3 250D | Kodak Vision3 250D | kodak_2383 | sin_T | 0.58 | 0.78 | 1.70 | 178 |
| 14 | Kodak 3 | Vision3 500T | Kodak Vision3 500T | kodak_2383 | T_grises | 0.63 | 0.89 | 1.71 | 78 |
| 15 | Kodak 3 | Vision3 50D | Kodak Vision3 50D | kodak_2383 | sin_T | 0.59 | 0.76 | 1.65 | 171 |
| 16 | Fuji 1 | C200 | Fujifilm C200 | fujifilm_crystal_archive_typeii | T_grises | 0.78 | 0.91 | 2.21 | 46 |
| 17 | Fuji 1 | Pro 400H | Fujifilm Pro 400H | fujifilm_crystal_archive_typeii | T_grises | 0.75 | 0.91 | 2.14 | 40 |
| 18 | Fuji 1 | Provia 100F | Fujifilm Provia 100F | — | sin_T | 0.58 | 0.62 | 2.11 | 238 |
| 19 | Fuji 1 | Velvia 100 | Fujifilm Velvia 100 | — | sin_T | 0.85 | 1.12 | 2.53 | 200 |
| 20 | Fuji 1 | X-Tra 400 | Fujifilm X-Tra 400 | fujifilm_crystal_archive_typeii | T_grises | 0.86 | 1.00 | 2.27 | 62 |
| 21 | Fuji 1 | Eterna 250 | Fujifilm Eterna 250 | kodak_2383 | T_intervalos | 0.76 | 1.11 | 1.66 | 61 |
| 22 | Fuji 2 | Eterna 250D | Fujifilm Eterna 250D | kodak_2383 | sin_T | 0.50 | 0.75 | 1.62 | 204 |
| 23 | Fuji 2 | Eterna 400 | Fujifilm Eterna 400 | kodak_2383 | T_grises | 0.55 | 0.74 | 1.51 | 77 |
| 24 | Fuji 2 | Eterna 500 | Fujifilm Eterna 500 | kodak_2383 | T_grises | 0.64 | 0.89 | 1.80 | 85 |
| 25 | Fuji 2 | Eterna V160 | Fujifilm Eterna Vivid 160 | kodak_2383 | T_grises | 0.58 | 0.81 | 1.73 | 88 |
| 26 | Fuji 2 | Eterna V250D | Fujifilm Eterna Vivid 250D | kodak_2383 | sin_T | 0.56 | 0.81 | 1.74 | 216 |
| 27 | Fuji 2 | Eterna V500 | Fujifilm Eterna Vivid 500 | kodak_2383 | T_grises | 0.59 | 0.72 | 1.60 | 87 |
| 28 | Fuji 3 | F-64D | Fujifilm F-64D | kodak_2383 | sin_T | 0.69 | 0.92 | 1.79 | 162 |
| 29 | Fuji 3 | Reala 500D | Fujifilm Reala 500D | kodak_2383 | T_grises | 0.64 | 0.74 | 1.63 | 71 |
| 30 | Fuji Sim 1 | Astia | FUJIFILM ASTIA | — | sin_T | 1.13 | 1.34 | 2.32 | 327 |
| 31 | Fuji Sim 1 | Classic Chr. | FUJIFILM CLASSIC CHROME | — | sin_T | 0.96 | 1.25 | 2.39 | 291 |
| 32 | Fuji Sim 1 | Classic Neg | FUJIFILM CLASSIC Neg | — | sin_T | 0.95 | 1.29 | 2.25 | 411 |
| 33 | Fuji Sim 1 | Eterna | FUJIFILM ETERNA | — | sin_T | 0.78 | 1.07 | 2.04 | 269 |
| 34 | Fuji Sim 1 | Eterna BB | FUJIFILM ETERNA Bleach Bypass | — | sin_T | 0.82 | 1.18 | 1.92 | 526 |
| 35 | Fuji Sim 1 | Pro Neg | FUJIFILM PRO Neg | — | sin_T | 1.01 | 1.33 | 2.35 | 257 |
| 36 | Fuji Sim 2 | Provia | FUJIFILM PROVIA | — | sin_T | 1.06 | 1.33 | 2.26 | 283 |
| 37 | Fuji Sim 2 | Reala Ace | FUJIFILM REALA ACE | — | sin_T | 1.12 | 1.37 | 2.53 | 400 |
| 38 | Fuji Sim 2 | Velvia | FUJIFILM VELVIA | — | sin_T | 1.42 | 1.54 | 2.81 | 157 |