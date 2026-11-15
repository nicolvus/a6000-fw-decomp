# G69 — Etapas de color del BIONZ X, «Color Chrome / Film» y LUT: implementado el ajuste, LUT 3D hallada (15-11-2026)

Objetivos de wiki 16 (Fujifilm X-T3 «Color Chrome Effect», X-T5 «Film simulation», Sony ZV-E1 «Importación de LUTs»). Solo ficheros del `.dat` (`av-cam`, `viewUnified2.so`, `CautionConfig.so`, `string_*.uxc`); sin CFW construido; sin tocar `scripts/gui/harness/`. Código: `scripts/g69/color_chrome_patch.py` (cueva + gancho + Unicorn), ajuste `color_chrome` en `scripts/cfw_ajustes.py` (id de Backup `0x1070219`, pid `0xF2`), tests `tests/test_g69_color_chrome.py`, demo de ISP `scripts/g69/demo_isp.py`. Resultado: **Color Chrome y 3 estilos tipo película implementados (parcial, sin cámara)**; **LUT 3D programable ENCONTRADA** (5×9×9), lo que cambia el plan de «Importar LUT» (§4).

## 1. Tabla de etapas (A6000 fw3.21, `av-cam` VERIFICADO salvo lo marcado)
| Etapa | Existe | Dónde / formato | Foto / Live View | Programable desde el `.dat` |
|---|---|---|---|---|
| Matriz 3×3 | sí | 9 s16 por índice (`0x437a4b40`, tabla tipo→id `0x43ca66f2`); S-Gamut propias de G27 | ambos (mismo mensaje de colorimetría) | sí (G27 ya lo hizo) |
| Curva 1D por canal | sí | gamma por número, 8 ranuras de 0x1020 B en el hueco `0x43FAF300…` (G25/G32c/G67) | ambos | sí |
| Saturación, Fase, Color Depth ×6 | **valores sí, pesos no** | builder `0x437aa65c` (`0x437aa856…0x437aa8ec`): `pkt+0x24` = Sat, `pkt+0x25` = Fase, `pkt+0x2a…0x2f` = Color Depth (R `2a`, Y `2b`, G `2c`, C `2d`, B `2e`, M `2f`; s8 −7…+7), `pkt+0x29` = indicador «hay Color Depth». El peso por tono y la escala los aplica el procesador de imagen, **no están en `av-cam`** (G32/G34); `0x437a1e00…` calcula además 6 ganancias de sector `strh [r6,#0x8a2…0x8ac]` = parámetro × `[obj+0x3ca…0x3cf]` | ambos | **valores: sí** (este informe); pesos: no |
| **LUT 3D** | **SÍ** | ver §3 | ambos (modos SA / MOV-MON / CAP) | sí en principio; sin probar |
| Efecto de imagen (Posterización, Color parcial, Cámara de juguete…) | sí | `picture_effect` (`0x438b341c`, `YAP:picture_effect`) en el YC; cadena propia (`VPH_API pictureeffect`) | LV y foto | no investigado (PIX-F1) |

## 2. «Color Chrome / Film» (ajuste CFW)
- Gancho: el `strb.w r2,[r7,#0x29]` de `0x437aa8ec` (`87f82920`) pasa a `bl cueva` (`0x43FB7C00`, entre el código de `pp_tone` y la cueva de Silent `0x43FB7E00`; 208 B). Lee el Backup (`cfw_ajustes.leer_asm`), suma la fila de la opción a `pkt+0x24` y `pkt+0x2a…0x2f`, recorta a ±7 y fuerza `pkt+0x29 = 1`. **Off = ningún byte cambia** (salto directo y `strb` original).
- Opciones (Sat, R, Y, G, C, B, M; + = más profundo/oscuro y más saturado): **Débil** 0, +2 en los 6; **Fuerte** 0, +4 en los 6; **Clásico** (Classic Chrome) −2, +2/−1/+2/+2/+3/+1; **Vivo** (Velvia) +3, +2/+1/+3/+2/+3/+2; **Suave** (Pro Neg. Std) −1, −2/−1/−1/−1/−1/−1. Pesos **estimados**, no medidos en cámara; no es la ciencia de color de Fujifilm.
- **Se pisan los ajustes del usuario**: no se sustituyen, **se suman** al Color Depth/Saturación del Picture Profile/estilo creativo y se recorta a ±7 (el valor de usuario ya extremo no sube); con Saturación = −8 (B&N de G27) no se toca. Al volver a Off todo queda como estaba (no se escribe nada en los ajustes del usuario).
- Un único ajuste con 6 opciones porque **solo queda 1 id de Backup libre** del hueco `0x1070210…19` (g56 §2): los 10 están usados. Un «Film Sim» separado de «Color Chrome» exige ids nuevos (CCH-F4).
- Aproximación honesta: el Color Chrome real es una corrección de **luminancia dependiente de la saturación**; Color Depth actúa por sector de tono (sin distinguir saturación; el procesador probablemente lo pondera por croma, no medido). La versión fiel sería la LUT 3D (§3, CCH-F3).
- **Límite**: el paquete se rearma cuando cambia el Picture Profile/estilo, no al cambiar este ajuste; tras elegir Débil/Fuerte puede hacer falta tocar el PP o reencender (sin medir en cámara).

## 3. LUT 3D (VERIFICADO estático)
- Cadenas `[CAMERA_MAIN_CC]: Create3DLUT … Level:%d ConvSD:%d BlkOfs Cr/Cb`, `Copy3DLUT`, `LutMode Change SA/MOV/MON/CAP`, `LUT Write Cnt`, `CamCore 3D-Lut table Write Start/End`; código en `0x437a1bea…0x437a24ac` y `0x4381d2a0…0x4381d386`.
- Rejilla **5×9×9 = 405 nodos × 4 B = `0x654` B**. Empaquetador `0x437a198c(j, a, b, {c0,c1,c2}, dest)`: `dest[perm[j·81 + a·9 + b]] = (c0&0x7f)<<16 | (c1&0x7f)<<8 | (c2&0x7f)` (3 componentes de 7 bits); `perm` = tabla u16 de 405 entradas en `0x43bef2ac`, **permutación de 0…404 verificada** (orden de escritura del hardware).
- Origen: bucle 9×9×5 (`0x437a22e2…0x437a24ac`) con la referencia en `[obj+0xd4]`, 3 planos de 405 B a `+0`, `+0x195`, `+0x32a` (fila de 9 = `0x51`); **no determinado** de dónde sale ese puntero (¿preset de Backup `CX79100_*`, que ya trae matrices y conjuntos, G27?) ni qué eje es Y/Cb/Cr.
- Salida al hardware: `0x4381d2fc…0x4381d308`: `0x43b67a68(handle, {0, [obj+0xc4]})` con el búfer de `0x654` B (o `memcpy 0x439c5320` de `0x654` B a otro destino).
- **No medido**: semántica de los ejes y de los 7 bits (¿deltas con signo?), en qué momento se escribe a cada modo, y que cambiar la tabla altere la imagen (sin cámara). Se descartaron ISP: el modelo de G23 no emula esta etapa.

## 4. Importar LUT (.cube)
- **Versión literal descartada**: la LUT del hardware tiene 405 nodos de 7 bits (5×9×9), no 17³/33³ (4 913 / 35 937 nodos de 16-32 bit): un `.cube` no se puede cargar tal cual.
- **Alternativa factible**: remuestrear el `.cube` a la rejilla 5×9×9 (ajuste de mínimos cuadrados o interpolación en ese espacio) y escribir los 405×3 valores en la tabla de referencia. Dos caminos: (a) tabla fija en el `.dat` generada offline (sin SD); (b) leer el `.cube` de la SD en el firmware: **no comprobado** que `av-cam` pueda leer un fichero en ese punto (hay `DCIM/` y acceso FAT, pero no se ha hallado una llamada de lectura de usuario fuera de los procesos de captura). Pendiente CCH-F5.

## 5. Pruebas
- `tests/test_g69_color_chrome.py` (5): bytes originales del gancho, cueva a cero, diff acotado a gancho + cueva, idempotencia (se rechaza una imagen ya parcheada), Off y byte fuera de tabla = comportamiento de fábrica (Unicorn sobre el tramo `0x437aa856…0x437aa8f0` del builder con cfg falso), cada fila = usuario + fila recortada a ±7 con `pkt+0x29 = 1`, Sat −8 intacta, y que la cueva no pisa las de Silent ni `pp_tone`. `tests/test_cfw_ajustes.py`: 10 ajustes con ids/pids distintos.
- **Arnés** (overlay y perfil propios `g69`, puerto 8769, solo menú; qemu parado y perfil borrado): Ajustes personalizados → «CFW» → página 2 muestra **«Color Chrome: Off»**; la lista ofrece Off/Débil/Fuerte/Clásico/Vivo/Suave (`img/g69-color-chrome-lista.png`); tras elegir «Fuerte» se ve «Color Chrome: Fuerte» (`img/g69-color-chrome-fuerte.png`) y `nvram.json` queda con `"1070219": "02"`. El arnés no ejecuta el consumidor de `av-cam`.
- **ISP emulado** sobre `/home/nicolas/Desktop/16161111/DSC03799.ARW` (`img/g69-isp-color-chrome.png`: Off | Débil | Fuerte / Clásico | Vivo | Suave): saturación media (HSV) 0,308 → 0,352 → 0,394 / 0,273 → 0,456 → 0,250. **El modelo (G23) trata Color Depth como ganancia de croma por tono, sin oscurecer** (luma ~constante): muestra la dirección, no la magnitud ni el oscurecimiento real.

## 6. Pendientes
CCH-F1…F5 en [PENDIENTES](../PENDIENTES.md).
