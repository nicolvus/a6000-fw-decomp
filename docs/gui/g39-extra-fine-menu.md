# G39 — «Extra fine» en el menú Calidad de la A6000 (15-11-2026)

**Resultado: parche probado en el arnés, sin CFW.** Corrige [G37](g37-calidad-jpeg-extra-fine.md), que lo descartó solo con cadenas: el firmware trae Extra fine, pero el menú Calidad de la A6000 no la ofrece. No se construyó ni se instaló CFW (regla del usuario); solo hay un parche de 8 bytes y su prueba en el arnés.

## 1. Qué ofrece el menú de serie
- Captura del arnés con el fw 3.21 de Sony: `docs/gui/img/g39-calidad-sony-321.png` (MENU → cámara, pág. 1 → Calidad): **RAW, RAW & JPEG, Fina, Estándar**. Sin Extra fine. (`g39-menu-pagina1-sony-321.png`: la pantalla previa.)
- Tabla id de proceso → `WRAPPER_IMAGE_QUALITY` → etiqueta (`wrapperImageQuality.so+0x16ae`, `tbb` con tabla `03 06 08 0a 0c`; `_getImageQualityByModelValue` +0x15b0 confirma que 3 = EXFINE):

| id proceso (`0xf/0x10` del nodo) | WRAPPER_IMAGE_QUALITY | Etiqueta | Nodo `cmnViewSetting*` |
|---|---|---|---|
| 0 | 1 | RAW | `StlImageQualityRAW` |
| 1 | 2 | RAW & JPEG | `StlImageQualityRAW_JPEG` |
| 2 | 3 | Extra fine (`JPG_QUALITY_EXFINE`, `[Quality]:2`) | `StlImageQualityExtraFine` |
| 3 | 4 | Fine | `StlImageQualityFine` |
| 4 | 5 | Standard | `StlImageQualityStandard` |

## 2. La puerta por modelo (causa)
`CmnViewSettingNodeStlImageQuality::_getSubNode` (`CautionConfig.so+0x108b6c`) lee el id `0x1070316` y, según `1<<id`: máscara `0x61a00002` → lista `Type01` (RAW, RAW+J, Fine, Standard: 4 nodos); máscara `0xf0000` → `Type02` (Fine, Standard); resto → `Default` (5 nodos, con Extra fine). El menú de la A6000 cae en `Type01`. Los literales del pool están en `0x108be0` (nodos Type01, GOT+0x7e38) y `0x108be4` (cuenta, GOT+0x9e20); los de `Default` son GOT+0x93f8 / +0x84ac.

## 3. Parche y prueba
- `scripts/gui/quality_exfine_patch.py ENTRADA.so SALIDA.so`: cambia esos dos literales a los de `Default`. 8 bytes; valida los bytes originales; idempotente. Test: `tests/test_quality_exfine_patch.py`. Mismos desplazamientos en el `CautionConfig.so` de Sony 3.21 () y en el del CFW 3.81 (`pkg-381w`, 2 182 928 B; el parche no cambia el tamaño).
- Prueba en el arnés (copia parcheada de `CautionConfig.so` del CFW 3.81 en un overlay propio `cam/usr/lib/`, perfil propio, sin tocar `scripts/gui/harness/`): `docs/gui/img/g39-calidad-extrafina-parche.png` muestra **RAW, RAW & JPEG, Extrafina (icono X.FINE), Fina, Estándar**.
- Límite: en el arnés elegir cualquier calidad no persiste (vuelve a RAW, también con Fina; causa G27-A), así que no se vio `[Quality]:2(EXFINE)`. Que llega al núcleo se prueba estáticamente: nodo `0xf=0x10=2` → tabla `tbb` → enum 3 → `_getImageQualityByModelValue` (b==2) → EXFINE, el mismo camino que la α6300.

## 4. Valores TGT/MAX (opción «Extra fine+»)
- Pares nombre→BKID en `libmprctrl.so+0x32dc4` (132 entradas; las `APSC_DRJPG` son ids ≈ 0x5013x). Antes y después del parche: **no cambian** (no se tocan). En los volcados `backup_flash.bin` de la cámara (`20261020-first`, `20261105-post-apagado-limpio`) los 90 valores `APSC_DRJPG_{L,M,S}_*_{STD,FINE,EXFINE}_{TGT,MAX}` son **0**: no hay tamaños objetivo almacenados que subir, y el tamaño objetivo sirve al contador de fotos restantes (`GetStillTargetFileSize`), no está demostrado que fije la tasa del codificador.
- Por eso no se implementó «Extra fine+» (valor propio): sin un valor numérico que escalar ni medida de un JPEG real habría sido inventar. Queda en G37-B.

## 5. Límites
Sin cámara: no se probó que el JPEG Extra fine salga bien ni su tamaño; la lista de Calidad del menú Fn no se comprobó con el parche; el menú de reproducción/iconos usan `ACT_IconStillRecImageQuality` (existe, sin verificar). Tamaño de fichero esperado del CFW: igual al de 3.81 (el parche no cambia tamaños) y no se construyó.
