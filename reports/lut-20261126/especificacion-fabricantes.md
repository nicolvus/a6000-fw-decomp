# LUTs de usuario que entran DIRECTAMENTE en cámara — especificación web y contraste con este proyecto

**Fecha:** 25-11-2026 (local, America/Santiago) / 26-11-2026 UTC.
**Alcance:** investigación web con fuentes citables (manuales y help guides de fabricante). No se ha tocado el repositorio `a6000-main`; este informe vive fuera del árbol, en `/home/nicolas/Documentos/a6000/lut-webspec.md`.
**Qué es "entrar directamente en cámara":** el fichero (normalmente `.cube`) se copia a la tarjeta, la cámara lo importa a una ranura interna y lo aplica (monitor, grabación o ambos). Queda fuera: LUTs que solo se usan en post (Resolve, NLEs) y LUTs de monitores externos.

Convención de este informe: **✔ oficial** = manual/help guide/support del fabricante; **◐ secundario** = manual o texto del fabricante reproducido por un tercero (no he podido abrir el original); **⚠ no confirmado** = no he encontrado fuente que lo diga.

---

## 0. Resumen en una tabla

| Fabricante | ¿Importa LUT de usuario en cámara? | Rejillas aceptadas | Formato | 1D+3D en el mismo fichero | Fuente |
|---|---|---|---|---|---|
| **Sony** (Alpha y cine) | Sí, 16 ranuras `User1–User16` (+3 presets) | **17³ o 33³** (no 65³) | `.cube` 3D | **No** (solo 3D) | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) [S15](https://www.sony.com/electronics/support/articles/00253964) |
| **Canon** (C400/C80, vía Look File) | Sí (4 LUTs en C400) | 33³ documentado; C400/C80 admiten 3D | `.cube` en la raíz de la tarjeta | No en cámara (sí en **monitores** Canon: `.clut` 1D+3D) | [C1](https://color.ssw.imaging-saas.canon/color/en/pc/import/) [C2](https://www.manualslib.com/manual/3628753/Canon-Eos-C400.html) [C5](https://gdlp01.c-wss.com/gds/2/0300014362/02/lut-cg-en.pdf) |
| **Nikon** (ZR) | Sí, hasta 50 ficheros | **17³, 33³ o 65³** | `.cube` 3D en `NIKON/LUTS` | No documentado | [N1](https://onlinemanual.nikonimglib.com/zr/en/09-05-105.html) |
| **Fujifilm** (GFX ETERNA 55) | Sí, 16 ranuras | **17³, 33³ o 65³** | `.cube` 3D | No documentado | [F1](https://dl.fujifilm-x.com/technical-data/GFX_ETERNA_WhitePaper_251112%20v1.00.pdf) |
| **Panasonic** (LUMIX "Real Time LUT") | Sí, 39 ranuras (GH7); 10 (S5II) | **`.cube` de 2 a 33 puntos** (65³ no) | `.cube` 3D · `.vlt` (1D, VARICAM) | **No**; `.vlt` es 1D sola | [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) |
| **Blackmagic** (Pocket) | Sí, LUT de monitor/grabación | **33³ y 17³** | `.cube` 3D | No documentado | [B1](https://documents.blackmagicdesign.com/UserManuals/BlackmagicPocketCinemaCameraManual.pdf) [B2](https://usermanual.com/support/blackmagicdesign/web-manual/pocket-cinema-camera/settings) ◐ |
| **DJI** (Ronin 4D) | Sí, 16 LUTs | **33 puntos** | `.CUBE` en la raíz del soporte | No documentado | [D1](https://www.dji.com/ronin-4d/faq) |

**Dato transversal:** ninguna cámara de las revisadas documenta aceptar un `.cube` que combine `LUT_1D_SIZE` (shaper) + `LUT_3D_SIZE`. La combinación 1D+3D aparece en **monitores de referencia Canon** (`.clut`, 1D de 128/256/512/1024 + 3D de 9/17/33/65, float 32, rango 0–1) — [C5](https://gdlp01.c-wss.com/gds/2/0300014362/02/lut-cg-en.pdf).

---

## 1. Sony

### 1.1 Qué modelos aceptan LUT de usuario (y cuáles no)

| Modelo | Dónde se documenta | Rejilla | Nota | Fuente |
|---|---|---|---|---|
| ILME-FX3 | *Manage User LUTs* | 17/33 | importación por tarjeta y por C3 Portal (fw ≥4.00) | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) |
| ILME-FX30 | *Manage User LUTs* | 17/33 | mismo texto | [S3](https://helpguide.sony.net/ilc/2220/v1/en/contents/TP1000888940.html) |
| ILCE-7SM3 (A7S III) | *Manage User LUTs* | 17/33 | **solo con firmware Ver.4.00 o posterior** | [S2](https://helpguide.sony.net/ilc/2410/v1/en/contents/211h_manage_lut.html) |
| ILCE-6700 | *Manage User LUTs* | 17/33 | — | [S4](https://helpguide.sony.net/ilc/2320/v1/en/contents/211h_manage_lut.html) |
| ZV-E1 | *Manage User LUTs* | 17/33 | — | [S5](https://helpguide.sony.net/ilc/2310/v1/en/contents/211h_manage_lut.html) |
| ILCE-7CM2 / ILCE-7CR | *Manage User LUTs* | 17/33 | — | [S6](https://helpguide.sony.net/ilc/2360/v1/en/contents/211h_manage_lut.html) [S7](https://helpguide.sony.net/ilc/2370/v1/en/contents/211h_manage_lut.html) |
| ZV-E10 II / ILCE-7M5 (A7 V) | *Manage User LUTs* | 17/33 | — | [S8](https://helpguide.sony.net/ilc/2430/v1/en/contents/211h_manage_lut.html) [S9](https://helpguide.sony.net/ilc/2540/v1/en/contents/211h_manage_lut.html) |
| ILCE-1M2 (A1 II) | *Manage User LUTs* + *PPLUT1–PPLUT4* | 17/33 | la LUT de usuario se puede **hornear en la foto grabada** vía Picture Profile | [S10](https://helpguide.sony.net/ilc/2440/v1/en/contents/211h_manage_lut.html) [S19](https://helpguide.sony.net/ilc/2440/v1/en/contents/0412D_picture_profile.html) |
| ILME-FX2 / FX3A | *Manage User LUTs* | 17/33 | — | [S11](https://helpguide.sony.net/ilc/2530/v1/en/contents/211h_manage_lut.html) [S12](https://helpguide.sony.net/ilc/2510/v1/en/contents/211h_manage_lut.html) |
| DSC-RX1RM3 | *Manage User LUTs* | 17/33 | — | [S13](https://helpguide.sony.net/dsc/2510/v1/en/contents/211h_manage_lut.html) |
| ILME-FX5/FX5B | *Importing a Desired Base Look* | 17/33 | reglas explícitas de tamaño y de color de entrada | [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) |
| ILME-FX6 / FX9 | *Base Look* (manual de instrucciones) | 17/33 | misma familia de importación que FX5; **texto no extraíble en esta sesión** (PDF) | [S21](https://www.sony.com/electronics/support/res/manuals/5024/c3bfbc891ee0f149e46d142754fd6aa7/50244581M.pdf) ⚠ |
| **ILCE-1 (A1), ILCE-7RM5 (A7R V), ILCE-7M4 (A7 IV)** | **NO** configurables: la app *Monitor & Control* lo excluye expresamente | — | evidencia negativa oficial: "This is not configurable if the connected camera is an ILCE-1 / ILCE-7RM5 / ILCE-7M4" | [S18](https://helpguide.sony.net/promobile/mc/v1/en/contents/lut_import.html) |

> Ojo con las listas de terceros: la galería de LUTs de Sony Alpha Universe cita "FX30, FX2, FX3, FX5, FX6, FX9, ZV-E1, ZV-E10 II, A7C II, A7CR, A7 V, A7R VI, A6700, A9 III y A1" ([S20](https://www.sony.co.uk/alphauniverse/lut-gallery)); "A1" ahí no puede ser el ILCE-1, que [S18] excluye. Tomar la lista por modelo desde el Help Guide, no de la galería.

### 1.2 Reglas documentadas (Sony)

| Regla | Valor | Fuente |
|---|---|---|
| Formato | "CUBE file (.cube) for a 17-point or 33-point" 3D LUT | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) [S15](https://www.sony.com/electronics/support/articles/00253964) |
| Rejillas | **17³ y 33³**. 65³ no aparece en ninguna parte y el tope de tamaño lo impide (ver fila siguiente) | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) |
| Tamaño máximo | "The file size of a 33-grid CUBE file … is estimated to be approximately 1 MB. CUBE files exceeding this size cannot be imported" (línea cine, FX5) | [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) |
| Ruta (tarjeta SD) | `/Private/Sony/PRO/LUT` (FX5 lo escribe `/PRIVATE/SONY/PRO/LUT/`) | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) [S16](https://www.sony.com/electronics/support/articles/00283315) [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) |
| Ruta (CFexpress Type A) | `/Sony/PRO/LUT` | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) [S16](https://www.sony.com/electronics/support/articles/00283315) |
| Nombre | ≤63 caracteres alfanuméricos de un byte, **incluida** la extensión `.cube` | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) |
| Nombre en FAT16/FAT32 | "When using SD cards or SDHC cards, filenames for registering LUT files are displayed in the 8.3 format" | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) [S11](https://helpguide.sony.net/ilc/2530/v1/en/contents/211h_manage_lut.html) |
| Menú | `MENU → (Exposure/Color) → [Color/Tone] → [Manage User LUTs] → [Import/Edit]` (Alpha) · `[Paint/Look] → [Base Look] → [Import from Media(B)]` (cine) | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) |
| Ranuras | `User1–User16` + 3 presets (`S-Log3`, `s709`, `709(800%)`) | [S17](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888941.html) |
| Tarjeta | En cuerpos cine hay que usar la **ranura B** | [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) |
| Color de entrada esperado | **S-Gamut3.Cine/S-Log3 o S-Gamut3/S-Log3**; "If [Input] is not set correctly, the proper look will not be obtained" | [S15](https://www.sony.com/electronics/support/articles/00253964) [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) |
| Selector `Input` en Alpha | El Help Guide muestra dos opciones como **iconos que no se renderizan en texto** ("Selects either [ ] or [ ]") | [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html) ⚠ |
| Dominio / `DOMAIN_MIN`–`MAX` | **No documentado** por Sony. Tampoco `LUT_3D_INPUT_RANGE` | — ⚠ |
| 1D / shaper | **Solo 3D**: todos los documentos dicen "3D LUT"; no hay ninguna mención a 1D ni a shaper | [S15](https://www.sony.com/electronics/support/articles/00253964) |
| Reconstrucción tras Reset | Las LUTs importadas **no** se borran con `All Reset → Reset` (FX5) | [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) |
| Embeber la LUT en el fichero | Solo en cuerpos cine (`Embed LUT File`) y en Alpha vía `PPLUT1–4` | [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) [S19](https://helpguide.sony.net/ilc/2440/v1/en/contents/0412D_picture_profile.html) |

**Lectura para este proyecto:** el `.cube` de Sony es *una LUT 3D de 17 o 33 puntos, en un espacio logarítmico declarado (S-Log3/S-Gamut3.Cine), que la cámara aplica tal cual*. Sony no convierte el espacio: o le das la LUT en el espacio correcto o el look no sale ([S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html)). Es exactamente el problema que este repo tiene con los `.cube` de Film Lab/sosang (§3).

---

## 2. Otros fabricantes

### 2.1 Canon (EOS C400 / C80, y matiz de monitores)

| Regla | Valor | Fuente |
|---|---|---|
| Vía de importación | Copiar el `.cube` (Log2/Log3 → 709, **33grid**) a la **raíz** de la tarjeta; registrar en `Custom Picture → Edit CP File → Look File Setup → Register` | [C1](https://color.ssw.imaging-saas.canon/color/en/pc/import/) |
| Nº de LUTs | "up to four LUT files … as user LUTs" (C400); "only up to 20 LUTs can be displayed even if more than 20 are registered on the card" | [C2](https://www.manualslib.com/manual/3628753/Canon-Eos-C400.html) ◐ · [C1](https://color.ssw.imaging-saas.canon/color/en/pc/import/) |
| Dominio | "LUT files which include values outside of the 0 to 1 range in the data area are not supported" (C400) | [C2](https://www.manualslib.com/manual/3628753/Canon-Eos-C400.html) ◐ |
| Cabecera de rango | "LUT files with input ranges outside the 0 to 1 range in the header (`LUT_3D_INPUT_RANGE`) are not supported" (C80) | [C3](https://www.manualslib.com/manual/3598299/Canon-Eos-C80.html) ◐ |
| Tamaño / nombre | "LUT files 2 MB and larger, as well as files with a name containing over 65 characters are not supported" (C400) | [C2](https://www.manualslib.com/manual/3628753/Canon-Eos-C400.html) ◐ |
| 1D+3D en cámara | No documentado | — ⚠ |
| **1D+3D en monitor Canon** | `.clut`: tipo `gamma` (1D, 128/256/512/1024 puntos) o `gamut` (3D, 9/17/33/65), datos **32F, rango 0–1**, nombre ≤48 caracteres con extensión | [C5](https://gdlp01.c-wss.com/gds/2/0300014362/02/lut-cg-en.pdf) |

Manuales oficiales (PDF, tras registro): C400 [asia.canon/en/support/0304987201](https://asia.canon/en/support/0304987201) · C80 [sg.canon/en/support/0305055301](https://sg.canon/en/support/0305055301).

### 2.2 Nikon (ZR; único modelo Nikon con importación documentada)

| Regla | Valor | Fuente |
|---|---|---|
| Formato / rejilla | `.CUBE`, **17pt, 33pt o 65pt** 3D LUT | [N1](https://onlinemanual.nikonimglib.com/zr/en/09-05-105.html) |
| Ruta | `NIKON` → `LUTS` en la tarjeta | [N1](https://onlinemanual.nikonimglib.com/zr/en/09-05-105.html) |
| Nº de ficheros | Hasta **50** `CUBE` (los 50 más recientes); fw 1.10 | [N1](https://onlinemanual.nikonimglib.com/zr/en/09-05-105.html) · [N3](https://www.nikon.com.hk/en/articles/how-to-use-luts-on-nikon-zr) |
| Nombre | ≤90 caracteres (por encima de 30 se abrevian en pantalla) | [N1](https://onlinemanual.nikonimglib.com/zr/en/09-05-105.html) |
| Tarjeta | exFAT, ≥64 GB formateada en cámara | [N1](https://onlinemanual.nikonimglib.com/zr/en/09-05-105.html) |
| Espacio de entrada | LUTs para **Log3G10** (R3D NE) o creadas en editor; `REC.709` por defecto | [N1](https://onlinemanual.nikonimglib.com/zr/en/09-05-105.html) |
| 1D+3D | No documentado | — ⚠ |

### 2.3 Fujifilm (GFX ETERNA 55)

| Regla | Valor | Fuente |
|---|---|---|
| Formato / rejilla | "17-point, 33-point or 65-point CUBE file (.cube)" | [F1](https://dl.fujifilm-x.com/technical-data/GFX_ETERNA_WhitePaper_251112%20v1.00.pdf) |
| Nº de LUTs | Hasta **16** (`User LUT 1–16`) | [F1](https://dl.fujifilm-x.com/technical-data/GFX_ETERNA_WhitePaper_251112%20v1.00.pdf) |
| Nombre | ≤48 caracteres **incluida** la extensión `.cube` | [F1](https://dl.fujifilm-x.com/technical-data/GFX_ETERNA_WhitePaper_251112%20v1.00.pdf) |
| Dónde se aplica | `PROJECT → LUT SETTING`, por salida (tarjeta / LCD / SDI / HDMI) | [F2](https://fujifilm-dsc.com/en/manual/gfx-eterna-55/shooting_settings/look/) |
| 1D+3D | No documentado | — ⚠ |
| Resto de Fujifilm | Los `.cube` de Film Simulation de Fujifilm se descargan para **post**, no para importar en cámara | [F3](https://www.fujifilm-x.com/global/support/download/lut/) |

### 2.4 Panasonic (LUMIX "Real Time LUT" / `LUT Library`)

| Regla | Valor | Fuente |
|---|---|---|
| Formatos | `.cube` **y** `.vlt` (VARICAM 3DLUT Reference Manual Rev.1.0) | [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) |
| Rejilla `.cube` | "compatible with **2-point to 33-point** 3D LUT" → **65³ no** | [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) |
| Rango | "We recommend loading LUT files for **full range** … If the range property is different, the images may not be displayed or recorded correctly" | [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) |
| Ruta | **Raíz** de la tarjeta | [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) · [P3](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/lut/index.html) |
| Nombre | FAT32 (SD/SDHC): ≤8 caracteres sin extensión · exFAT (SDXC/CFexpress): ≤255 con extensión · solo alfanumérico | [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) · [P3](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/lut/index.html) |
| Nº de LUTs | **39** (GH7) · **10** (S5II) | [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) · [P6](https://www.panasonic.com/uk/consumer/cameras-camcorders/lumix-expert-advice-learn/lumix-expert-advice/using-real-time-luts.html) |
| Espacio de entrada | Se declara **dentro del propio `.cube`** como etiqueta de Photo Style bajo la línea de título; si falta o es incorrecta, **se asume [V-Log]** | [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) · [P2](https://eww.pavc.panasonic.co.jp/dscoi/DC-S9/html/DC-S9_DVQP3138_eng/0074.html) |
| 1D+3D | `.vlt` es una LUT **1D** (VARICAM), no una combinación; `.cube` es solo 3D | [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) · [P3](https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/lut/index.html) |

Panasonic es **el único** de la lista que (a) acepta un formato 1D puro (`.vlt`), (b) publica una recomendación explícita de rango (full) y (c) deja declarar el espacio de entrada dentro del fichero. Las tres cosas son directamente aplicables al validador de §4.

### 2.5 Blackmagic Design (Pocket 4K/6K/6K Pro)

| Regla | Valor | Fuente |
|---|---|---|
| Formato / rejilla | 33 puntos 3D `.cube` creados en DaVinci Resolve y 17 puntos convertidos a `.cube` de Resolve | [B1](https://documents.blackmagicdesign.com/UserManuals/BlackmagicPocketCinemaCameraManual.pdf) · [B2](https://usermanual.com/support/blackmagicdesign/web-manual/pocket-cinema-camera/settings) ◐ |
| Interpolación | tetraédrica de "alta calidad" | [B2](https://usermanual.com/support/blackmagicdesign/web-manual/pocket-cinema-camera/settings) ◐ |
| 65³ | No documentado (solo 33 y 17) | — ⚠ |
| Ruta / nombre | No lo he podido confirmar en el PDF oficial | — ⚠ |

El PDF oficial de BMD no es extraíble por la herramienta de lectura; la cita textual de arriba viene de una copia del manual en `usermanual.com`, marcada ◐.

### 2.6 DJI (Ronin 4D)

| Regla | Valor | Fuente |
|---|---|---|
| Formato / rejilla | Fichero **33-point** con sufijo `.CUBE` | [D1](https://www.dji.com/ronin-4d/faq) |
| Ruta | **Raíz** del soporte; menú `Display → LUT File Settings → LOOK` | [D1](https://www.dji.com/ronin-4d/faq) |
| Nº de LUTs | Hasta **16** | [D1](https://www.dji.com/ronin-4d/faq) |
| Nombre | "Please name the file with letters, numbers and underscores" | [D1](https://www.dji.com/ronin-4d/faq) |
| 1D+3D | No documentado | — ⚠ |

**Patrón de la industria:** 17³/33³ es el mínimo común (Sony, Canon, BMD, DJI); 65³ solo en los dos cuerpos de cine más nuevos (Nikon ZR, Fujifilm GFX ETERNA 55); Panasonic **limita a 33³**; nadie documenta 1D embebida en cámara; los topes de nombre son cortos (8.3 en FAT32, 48–63 caracteres en exFAT) y el tamaño se acota (Sony ~1 MB para 33³, Canon <2 MB).

---

## 3. «V-Log» y «STD» en los `.cube` de Film Lab / sosang

**Qué es qué.** `lee-juncheol/sosang` (el proyecto que antes se publicaba en `film-lab-jc.workers.dev`, hoy **https://sosang.app/**) exporta dos familias de `.cube` de 33³:

| Variante | Qué espera a la entrada | Qué lleva dentro | Fuente |
|---|---|---|---|
| **V-Log** (148 looks) | **V-Log / V-Gamut** (logarítmico Panasonic) | el look del motor spektrafilm, sin adaptación | [L1](https://github.com/lee-juncheol/sosang) [L2](https://raw.githubusercontent.com/lee-juncheol/sosang/main/README.md) |
| **STD** (148 × 10 cámaras) | **Panasonic "Standard"** de *esa* cámara (imagen ya revelada, tipo Rec.709) | adaptador `A_camera`: Standard → V-Log/V-Gamut, **seguido** del look V-Log, todo fundido en una sola LUT | [L2](https://raw.githubusercontent.com/lee-juncheol/sosang/main/README.md) [L3](https://raw.githubusercontent.com/lee-juncheol/sosang/main/docs/camera-std.md) |

El contrato está escrito en el README y en `docs/camera-std.md`:

> `STD_camera(x) = L_VLOG(A_camera(x))`
> "`A_camera` es la LUT de Standard→Panasonic V-Log/V-Gamut por modelo de V-Log Alchemy. `L_VLOG` son los valores serializados del look de spektrafilm o de la LUT V-Log de síntesis de FUJIFILM. El adaptador se evalúa **trilinear**, el look **tetraédrico**, y se genera una tabla de **33³**."
> — [L3](https://raw.githubusercontent.com/lee-juncheol/sosang/main/docs/camera-std.md)

Cámaras soportadas: GH6 (solo post), S5II, S5IIX, G9II, GH7, S9, S1IIE, S1RII, S1II, DC-L10 ([L2](https://raw.githubusercontent.com/lee-juncheol/sosang/main/README.md)). El adaptador sale de [V-Log Alchemy](https://github.com/shenmintao/V-Log-Alchemy) y **no** es la inversa exacta publicada por Panasonic ([L3](https://raw.githubusercontent.com/lee-juncheol/sosang/main/docs/camera-std.md)).

**Respuesta corta a la pregunta:** un `.cube` etiquetado **V-Log espera entrada logarítmica** (V-Log/V-Gamut) y **no** está pensado para una imagen Rec.709/STD. El `.cube` etiquetado **STD** es el que sí espera una imagen ya revelada, pero **de una LUMIX concreta** (su "Standard"), no de una A6000.

### 3.1 Qué pasa si aplicas un `.cube` V-Log a un JPEG Rec.709 de la A6000

La LUT no sabe de dónde viene la señal: **interpreta los códigos 0–1 como si fueran V-Log**. Los anclajes documentados son:

| Punto | V-Log | Rec.709 / BT.709 (JPEG de la A6000) | Fuente |
|---|---|---|---|
| Negro (0 % de reflectancia) | código **128/1023 ≈ 0,125** | **0,0** | [P5](https://pro-av.panasonic.net/en/cinema_camera_varicam_eva/support/pdf/VARICAM_V-Log_V-Gamut.pdf) |
| Gris 18 % | código **433/1023 ≈ 0,423** (IRE 42 %) | ≈ **0,409** (OETF BT.709) | [P5](https://pro-av.panasonic.net/en/cinema_camera_varicam_eva/support/pdf/VARICAM_V-Log_V-Gamut.pdf) · [P4](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0097.html) |
| Blanco 90 % | ≈ **0,59** (calculado con la fórmula publicada) | ≈ **0,958** | cálculo propio sobre [P5](https://pro-av.panasonic.net/en/cinema_camera_varicam_eva/support/pdf/VARICAM_V-Log_V-Gamut.pdf) · definición BT.709 |

Consecuencia (razonamiento sobre esos anclajes, **no medido aquí**):

- Las **sombras** de Rec.709 (0,00–0,12) caen *por debajo* del negro de V-Log (0,125): la LUT las trata como "negro o más negro" y se pierde el arranque de la escala.
- El **blanco** de Rec.709 (0,6–1,0) cae *muy por encima* del 90 % de V-Log (0,59): la LUT lo manda a la zona de recorte/rodilla alta, con lo que el contraste se aplasta y los colores saturados se desvían.
- El gris 18 % es el único punto que coincide casi por casualidad (0,409 vs 0,423): el error es pequeño **en el centro** y grande en los extremos. Es el patrón clásico de "log LUT sobre imagen revelada": look plano/lavado, negros lechosos y altas luces sucias.

Y Panasonic lo confirma por el otro lado: su manual [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) dice que si el `.cube` no lleva etiqueta de Photo Style **Panasonic asume V-Log**; y Film Lab avisa de que "una imagen sRGB genérica u otro Photo Style aplicado no sirve como validación de la conversión de la cámara" ([L2](https://raw.githubusercontent.com/lee-juncheol/sosang/main/README.md)).

**Límites que el propio sosang declara** ([L3](https://raw.githubusercontent.com/lee-juncheol/sosang/main/docs/camera-std.md)): las altas luces y los colores ya recortados en Standard **no se recuperan** con la inversa; y **no** se puede encadenar S2V + look V-Log "por si acaso" — se convierte dos veces. Tampoco sirve como validación cruzada aplicar el `.cube` de una cámara a otra: "다른 카메라 모델은 서로 대체하지 않습니다" (no se sustituyen modelos entre sí).

---

## 4. Recomendación práctica para este proyecto

### 4.1 Dónde estamos (recordatorio de las restricciones medidas)

| Hecho del proyecto | Valor | Doc |
|---|---|---|
| LUT 3D del BIONZ X | **5 × 9 × 9 en YCbCr**, deltas s7 (ΔY ±24,6 %, Δcroma ±36,9 %) | [g71](a6000-main/docs/gui/g71-lut3d-formato-y-cube.md), [g90](a6000-main/docs/gui/g90-lut-interpolacion-optimizacion-geometria.md) |
| ¿Ampliable? | **No**: bancos SRAM llenos; 5×9×9 es el máximo del mapa | [g93](a6000-main/docs/gui/g93-ampliar-lut-3d-17.md), [g90 §C](a6000-main/docs/gui/g90-lut-interpolacion-optimizacion-geometria.md) |
| Lector `.cube` del PC | 3D, **17/33/65**, `DOMAIN_MIN/MAX`, trilineal; `LUT_1D_SIZE` → error; **`LUT_3D_INPUT_RANGE` se ignora en silencio** | `scripts/lut/cube_a6000.py` |
| Lector `.cube` de la cámara | 3D, **2 ≤ n ≤ 64**, `DOMAIN_*` en Q16; **rechaza** `LUT_1D*` y `LUT_3D_INPUT*`; exige n³ filas exactas; trunca líneas a 95 caracteres | `scripts/lut/lut_sd_userland.py` (`lee_cube_q16` ≈ `linea()` en C) |
| Ruta en la SD | `X:/LUT/LUT1.cube` … `LUT6.cube` (6 ranuras, `Off` + `LUT 1…6`) | [g89 §2](a6000-main/docs/gui/g89-lut-sd-en-camara.md) |
| Paquete precalculado | `LUT/LUTn.LUT` (1080 B, cabecera + CRC32) tiene prioridad sobre el `.cube` | [g95](a6000-main/docs/gui/g95-lut-paquete-precalculado.md) |
| Vía software | `lutjpg` aplica el `.cube` completo (2…129³, tetraédrica) al JPEG | [LUT-SW-1](a6000-main/docs/PENDIENTES.md) |
| Espacio de entrada asumido | **sRGB 0–1 (full)**, decodificado a lineal → matriz → curva 1D → YCbCr BT.601 → LUT | [g71 §2](a6000-main/docs/gui/g71-lut3d-formato-y-cube.md), `cube_a6000.py` |

### 4.2 Especificación mínima de un `.cube` admitido ("LUT-A6000 v1")

| # | Requisito | Valor exigido | Por qué (fuente) |
|---|---|---|---|
| 1 | Tipo | **3D pura**. `LUT_1D_SIZE` prohibido, `LUT_1D_INPUT_RANGE` prohibido | Sony: "3D LUT" [S15](https://www.sony.com/electronics/support/articles/00253964); ninguna cámara documenta 1D+3D |
| 2 | Cabecera de rango | `LUT_3D_INPUT_RANGE` ausente o exactamente `0.0 1.0` | Canon rechaza lo demás [C3](https://www.manualslib.com/manual/3598299/Canon-Eos-C80.html) ◐ |
| 3 | Dominio | `DOMAIN_MIN 0 0 0` / `DOMAIN_MAX 1 1 1` (o ausentes = 0/1) | Sony/Panasonic no documentan otro; Canon exige datos en 0–1 |
| 4 | Rango | **Full** (0–1 ↔ 0–255), **no** legal 16–235 | Panasonic: "we recommend … full range" [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html) |
| 5 | Valores | Todos en `[0, 1]`, sin `NaN`/`Inf` | Canon: "values outside of the 0 to 1 range … are not supported" [C2](https://www.manualslib.com/manual/3628753/Canon-Eos-C400.html) ◐ |
| 6 | Rejilla | **33³ recomendada; 17³ aceptada**. 65³ → convertir a 33³ en el PC (la cámara rechaza n>64) | Sony 17/33 [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html); tope del lector de cámara `lee_cube_q16` |
| 7 | Orden de datos | Adobe/Iridas: **R varía más rápido**, n³ filas de 3 floats | implementación `lee_cube`/`lee_cube_q16` |
| 8 | Espacio de entrada declarado | **sRGB / Rec.709 display-referred**. Etiqueta en comentario, p. ej. `# INPUT: sRGB-D65-FULL` | precedente Panasonic (etiqueta en el `.cube`) [P1](https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html); Sony exige el espacio correcto [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html) |
| 9 | Looks logarítmicos | **Rechazados** salvo que el proyecto añada un adaptador explícito (como `A_camera` de sosang) | §3 · [L3](https://raw.githubusercontent.com/lee-juncheol/sosang/main/docs/camera-std.md) |
| 10 | Nombre y ruta | `LUT/LUTn.cube`, n = 1…6, ≤8 caracteres sin extensión, solo alfanumérico | Sony 63 caracteres y 8.3 en FAT32 [S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html); Panasonic/DJI igual de estrictos |
| 11 | Tamaño | ≤ 1 MB (33³ son ~0,9 MB de texto); tope duro 2 MB | Sony ~1 MB para 33³ [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html); Canon <2 MB [C2](https://www.manualslib.com/manual/3628753/Canon-Eos-C400.html) ◐ |
| 12 | Longitud de línea | ≤ 80 caracteres por línea, sin BOM, UTF-8/ASCII, comentarios `#` | el lector de la cámara corta la línea a 95 caracteres (`lee_cube_q16`) |
| 13 | Título | Opcional pero recomendado: `TITLE "<look> (sRGB-full, 33)"` | trazabilidad; sin coste en el lector |

### 4.3 Qué debería exigir el validador (y dónde se aplica)

| Comprobación | Severidad | Hoy en el repo |
|---|---|---|
| `LUT_3D_SIZE` presente una sola vez, entero 2…64 | **error** | sí (ambos lectores) |
| Exactamente `n³` filas de 3 números, sin cuarta columna ni texto | **error** | PC: no valida columnas extra; cámara: sí |
| `LUT_1D_*` / `LUT_3D_INPUT_RANGE` ≠ `0 1` | **error** | cámara sí; **PC no** (`cube_a6000.lee_cube` los ignora) ← arreglar |
| `DOMAIN_MIN/MAX` = 0/1 | **error** (o remuestrear y avisar) | se leen y se usan; no hay política declarada |
| Valores en `[0,1]`, finitos | **error** | no comprobado explícitamente |
| n > 64 (p. ej. 65³) | **error para la vía cámara**, aviso + conversión a 33³ en el PC | PC lo acepta; cámara lo rechaza |
| Fichero > 1 MB o línea > 80 caracteres | **aviso** | no comprobado |
| Etiqueta de espacio de entrada ausente, o log (V-Log/S-Log3/C-Log/LogC) | **error** (o aviso con conversión obligatoria) | no existe el concepto |
| Nodos que saturan el rango s7 (ΔY ±64) | **aviso** con recuento | se informa al ajustar ([g71 §2](a6000-main/docs/gui/g71-lut3d-formato-y-cube.md)) |
| ΔE2000 medio/p95/máx del ajuste 5×9×9 frente al `.cube` | **aviso** (p95 ≤ 3 como umbral de entrega) | se calcula ([g90](a6000-main/docs/gui/g90-lut-interpolacion-optimizacion-geometria.md), [g95](a6000-main/docs/gui/g95-lut-paquete-precalculado.md)) |
| Identidad razonable (la LUT no invierte el gris) | **aviso** | no |
| Nombre `LUTn.cube`, n ≤ 6 | **error** | sí (ranuras fijas) |

Nota: el lector de la cámara (`lee_cube_q16` / `linea()` en C) ya es **más estricto** que el del PC. La asimetría importa: un `.cube` que `cube_a6000` acepta puede acabar en ranura inválida en la cámara (65³, `LUT_3D_INPUT_RANGE`, más filas de las declaradas). El validador debería ser el **del camino más estricto** y ejecutarse en el PC antes de escribir la tarjeta.

### 4.4 Sobre "1D/shaper": qué haría falta para igualar a Sony/Panasonic

- La cadena del BIONZ X ya tiene la pieza equivalente a un shaper: la **curva 1D compartida T** (2048 u16) y la **curva de 512 puntos tras la gamma** ([g92](a6000-main/docs/gui/g92-auditoria-cadena-color-lut-general.md), [LUT-T-1](a6000-main/docs/PENDIENTES.md)). Es decir, el proyecto **puede** construir "T + 5×9×9", pero **no** leyendo un `.cube` con `LUT_1D_SIZE` dentro: hoy eso es un error de parseo.
- Si en el futuro se quiere aceptar `shaper + 3D` de un `.cube`, la vía natural es: leer el 1D, **integrarlo en T** (o en la gamma), y quedarse solo con el 3D para la tabla de 5×9×9 — exactamente el reparto que ya se mide en [g90 §B](a6000-main/docs/gui/g90-lut-interpolacion-optimizacion-geometria.md) (la película baja de 0,60 a 0,28 ΔE con T+LUT). Mientras eso no exista, "sin 1D embebida" es la regla correcta.

### 4.5 Conciliación con el trabajo en curso (G114, sin commitear)

En el árbol de trabajo hay documentación y código **de otra sesión, sin commitear**: `docs/gui/g114-lut-propios-especificacion.md`, `scripts/lut/cube_spec.py`, `tests/test_lut_spec.py`. No los he tocado. Contrastados con esta investigación:

**Coinciden** en lo esencial: `.cube` Adobe **3D**, **sin LUT 1D**, dominio **0…1**, valores dentro del dominio, entrada **Rec.709/sRGB de pantalla (no V-Log/S-Log)**, rejilla **33³ recomendada**, y ruta `LUT/LUT1…6`.

**Tres discrepancias concretas** que conviene resolver antes de dar la especificación por cerrada:

| Punto | G114 / `cube_spec.py` | Lo que dice la cámara / los manuales | Recomendación |
|---|---|---|---|
| 65³ | Aceptada (`N_MAX = 129`, recomendadas 17/33/**65**) — cota válida para `lutjpg` (2…129³) | **`lutsd.c:111` rechaza `n > 64`**: un 65³ en la SD deja la ranura inválida y cae al respaldo `.LUT`/fábrica | El validador debe distinguir **vía**: 65³ = OK para `lutjpg`, **error** para la vía SD/ISP (o convertir a 33³ en el PC) |
| `LUT_3D_INPUT_RANGE` | **Aviso** ("se interpreta como dominio 0…1") | **Canon lo rechaza** si no es `0 1` ([C3](https://www.manualslib.com/manual/3598299/Canon-Eos-C80.html) ◐); `cube_a6000.lee_cube` lo **ignora en silencio** | Subir a **error** (o exigir explícitamente `0.0 1.0`); es el fallo silencioso más probable al importar LUTs de terceros |
| Longitud de línea | No comprobada | `lutsd.c` trunca la línea a **95 caracteres** (`lee_cube_q16`) | Comprobar ≤95 (mejor ≤80) para que un `.cube` válido en el PC no falle solo en la cámara |

Añadido útil que G114 ya cubre y esta investigación respalda: rechazar LUTs **degeneradas** (identidad o constante) — Canon/Nikon/Sony no lo dicen, pero es el mismo tipo de comprobación que evita un look "que no hace nada" y aquí es barata.

---

## 5. Lo que NO he podido confirmar

1. **Sony, opciones del selector `Input`** en los Alpha: el Help Guide las publica como iconos y el texto extraído no las nombra ([S1](https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html)). Que sean "S-Log3 / 709(800%)" es mi inferencia a partir de [S14](https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html)/[S15](https://www.sony.com/electronics/support/articles/00253964), no un dato leído.
2. **Sony, dominio y `DOMAIN_MIN/MAX`**: no documentados. Tampoco si acepta 65³ en algún cuerpo (no aparece en ningún manual; el límite de ~1 MB lo haría impracticable).
3. **Sony FX6/FX9**: la ruta EXACTA y el texto de "17/33" están en el manual PDF, que no se ha podido extraer ([S21](https://www.sony.com/electronics/support/res/manuals/5024/c3bfbc891ee0f149e46d142754fd6aa7/50244581M.pdf)).
4. **Canon C400/C80**: las frases sobre 0–1, `LUT_3D_INPUT_RANGE`, 2 MB y 65 caracteres están **citadas de un espejo** del manual (ManualsLib); el original solo se descarga tras registro. El dato de "4 LUTs" y "33grid" sí está en la web oficial de Canon ([C1](https://color.ssw.imaging-saas.canon/color/en/pc/import/)).
5. **Blackmagic**: el PDF oficial no es legible por la herramienta; el texto de 33/17 puntos y tetraédrica procede de un espejo ([B2](https://usermanual.com/support/blackmagicdesign/web-manual/pocket-cinema-camera/settings) ◐). Ruta y límite de nombre, sin confirmar.
6. **Nikon**: solo el ZR (2025) tiene importación; no he verificado si Z8/Z9 la tienen (no la documentan).
7. **1D+3D en cámara**: afirmo "no documentado en ninguna" (ausencia de evidencia), no "imposible".
8. **Cuantificación del §3.1**: el negro/gris de V-Log está leído del manual; el 0,59 del 90 % y el efecto sobre un JPEG Rec.709 son cálculo/razonamiento propios, no una medición con una LUT real.

---

## 6. Fuentes (todas)

**Sony**
- S1 · FX3, *Manage User LUTs* — https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html
- S2 · A7S III, *Manage User LUTs* (fw ≥4.00) — https://helpguide.sony.net/ilc/2410/v1/en/contents/211h_manage_lut.html
- S3 · FX30 — https://helpguide.sony.net/ilc/2220/v1/en/contents/TP1000888940.html
- S4 · A6700 — https://helpguide.sony.net/ilc/2320/v1/en/contents/211h_manage_lut.html
- S5 · ZV-E1 — https://helpguide.sony.net/ilc/2310/v1/en/contents/211h_manage_lut.html
- S6 · A7C II — https://helpguide.sony.net/ilc/2360/v1/en/contents/211h_manage_lut.html
- S7 · A7CR — https://helpguide.sony.net/ilc/2370/v1/en/contents/211h_manage_lut.html
- S8 · ZV-E10 II — https://helpguide.sony.net/ilc/2430/v1/en/contents/211h_manage_lut.html
- S9 · A7 V (ILCE-7M5) — https://helpguide.sony.net/ilc/2540/v1/en/contents/211h_manage_lut.html
- S10 · A1 II (ILCE-1M2) — https://helpguide.sony.net/ilc/2440/v1/en/contents/211h_manage_lut.html
- S11 · FX2 — https://helpguide.sony.net/ilc/2530/v1/en/contents/211h_manage_lut.html
- S12 · FX3A — https://helpguide.sony.net/ilc/2510/v1/en/contents/211h_manage_lut.html
- S13 · RX1R III — https://helpguide.sony.net/dsc/2510/v1/en/contents/211h_manage_lut.html
- S14 · FX5, *Importing a Desired Base Look* (17/33, ~1 MB, rutas, Input/Output) — https://helpguide.sony.net/ilc/2630/v1/en/contents/look_import.html
- S15 · Sony Support 00253964, *Can a specified look (LUT) be imported for shooting?* — https://www.sony.com/electronics/support/articles/00253964
- S16 · Sony Support 00283315, *What is a LUT…* (rutas y User1–16) — https://www.sony.com/electronics/support/articles/00283315
- S17 · FX3, *Select LUT* (3 presets + 16) — https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888941.html
- S18 · *Monitor & Control* → *Importing a LUT* (A1 / A7R V / A7 IV excluidas) — https://helpguide.sony.net/promobile/mc/v1/en/contents/lut_import.html
- S19 · A1 II, *Picture Profile* (PPLUT1–4) — https://helpguide.sony.net/ilc/2440/v1/en/contents/0412D_picture_profile.html
- S20 · Sony Alpha Universe, *Ambassador LUT Gallery* (lista de modelos) — https://www.sony.co.uk/alphauniverse/lut-gallery
- S21 · FX6, manual PDF — https://www.sony.com/electronics/support/res/manuals/5024/c3bfbc891ee0f149e46d142754fd6aa7/50244581M.pdf

**Canon**
- C1 · *How to import LUTs* (33grid, raíz de la tarjeta, Look File) — https://color.ssw.imaging-saas.canon/color/en/pc/import/
- C2 · EOS C400, manual (espejo): 4 user LUTs, 0–1, 2 MB, 65 caracteres — https://www.manualslib.com/manual/3628753/Canon-Eos-C400.html
- C3 · EOS C80, manual (espejo): `LUT_3D_INPUT_RANGE` 0–1 — https://www.manualslib.com/manual/3598299/Canon-Eos-C80.html
- C4 · Descargas oficiales de manual: C400 https://asia.canon/en/support/0304987201 · C80 https://sg.canon/en/support/0305055301
- C5 · *User LUT Creation Guide* (monitores Canon, `.clut`, 1D+3D, grids 9/17/33/65, 32F 0–1) — https://gdlp01.c-wss.com/gds/2/0300014362/02/lut-cg-en.pdf

**Nikon**
- N1 · ZR, `g15: 3D LUT` (NIKON/LUTS, 17/33/65, ≤90 caract., exFAT, 50 ficheros) — https://onlinemanual.nikonimglib.com/zr/en/09-05-105.html
- N2 · Nikon USA, *Step by step guide to using LUTs on the ZR* — https://www.nikonusa.com/learn-and-explore/c/products-and-innovation/a-step-by-step-guide-to-using-luts-on-the-nikon-zr-cinema-camera
- N3 · Nikon HK, *How to use LUTs on Nikon ZR* (fw 1.10, 50 LUTs) — https://www.nikon.com.hk/en/articles/how-to-use-luts-on-nikon-zr

**Fujifilm**
- F1 · GFX ETERNA 55 White Paper (17/33/65, ≤48 caract., 16 LUTs) — https://dl.fujifilm-x.com/technical-data/GFX_ETERNA_WhitePaper_251112%20v1.00.pdf
- F2 · Manual, *Look* (`PROJECT → LUT SETTING`) — https://fujifilm-dsc.com/en/manual/gfx-eterna-55/shooting_settings/look/
- F3 · LUTs Film Simulation para post — https://www.fujifilm-x.com/global/support/download/lut/

**Panasonic**
- P1 · GH7, *[LUT Library]* (`.cube` 2–33 puntos, `.vlt`, full range, raíz, 8.3/255, 39 LUTs, etiqueta Photo Style) — https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0075.html
- P2 · S9, *[LUT Library]* ("If the Photo Style information is absent … [V-Log] is used") — https://eww.pavc.panasonic.co.jp/dscoi/DC-S9/html/DC-S9_DVQP3138_eng/0074.html
- P3 · Panasonic, *About LUT* (`.vlt`, nombres, FAT32/exFAT) — https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/lut/index.html
- P4 · GH7, *Log Recording* (V-Log: 18 % → IRE 42 %) — https://eww.pavc.panasonic.co.jp/dscoi/DC-GH7/html/DC-GH7_DVQP3109_eng/0097.html
- P5 · VARICAM, *V-Log/V-Gamut Reference Manual* (0 % = 128, 18 % = 433) — https://pro-av.panasonic.net/en/cinema_camera_varicam_eva/support/pdf/VARICAM_V-Log_V-Gamut.pdf
- P6 · Panasonic UK, *Real Time LUT* (S5II: 10 LUTs) — https://www.panasonic.com/uk/consumer/cameras-camcorders/lumix-expert-advice-learn/lumix-expert-advice/using-real-time-luts.html

**Blackmagic Design**
- B1 · Manual oficial (PDF) — https://documents.blackmagicdesign.com/UserManuals/BlackmagicPocketCinemaCameraManual.pdf
- B2 · Copia del manual (33/17 puntos, tetraédrica) — https://usermanual.com/support/blackmagicdesign/web-manual/pocket-cinema-camera/settings

**DJI**
- D1 · Ronin 4D, FAQ (33-point `.CUBE`, raíz, 16 LUTs, nombre) — https://www.dji.com/ronin-4d/faq

**Film Lab / sosang**
- L1 · Repositorio — https://github.com/lee-juncheol/sosang
- L2 · README (V-Log vs STD, 33³, trilinear/tetraédrica, cámaras) — https://raw.githubusercontent.com/lee-juncheol/sosang/main/README.md
- L3 · `docs/camera-std.md` (contrato `C_camera = L_VLOG(A_camera(x))`, límites) — https://raw.githubusercontent.com/lee-juncheol/sosang/main/docs/camera-std.md
- L4 · V-Log Alchemy (adaptadores Standard→V-Log) — https://github.com/shenmintao/V-Log-Alchemy
- L5 · App pública — https://sosang.app/
- L6 · Motor de color — https://github.com/andreavolpato/spektrafilm

**Documentación interna usada para el contraste** (no son fuentes web): `docs/gui/g71-lut3d-formato-y-cube.md`, `g89-lut-sd-en-camara.md`, `g90-lut-interpolacion-optimizacion-geometria.md`, `g92-auditoria-cadena-color-lut-general.md`, `g93-ampliar-lut-3d-17.md`, `g94-lut-resolucion-entrega-fidelidad.md`, `g95-lut-paquete-precalculado.md`, `docs/PENDIENTES.md` (filas `LUT-*`), `scripts/lut/cube_a6000.py`, `scripts/lut/lut_sd_userland.py`.
