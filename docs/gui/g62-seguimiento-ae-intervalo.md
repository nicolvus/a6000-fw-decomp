# G62 — «Seguim. AE» del intervalómetro: nivel 1 (bloqueo AE en la serie) implementado; nivel 2 (suavizado) con direcciones y sin implementar (15-11-2026)

Objetivo «Interval AE Tracking Sensitivity / Exposure Smoothing» (wiki 16). Sobre la cueva de [g61](g61-intervalometro-libobj.md). Solo ficheros del `.dat` (`libObj.so`, `viewUnified2.so`, `CautionConfig.so`, `string_*.uxc`); sin CFW construido; sin tocar `scripts/gui/harness/`. Código: `scripts/g61/intervalo_patch.py` (ampliado), tabla `scripts/cfw_ajustes.py`, tests `tests/test_g61_intervalo.py` y `python3 scripts/g61/intervalo_patch.py`. Resultado: **nivel 1 implementado y probado en Unicorn sobre los bytes reales, ajuste verificado en el arnés; nivel 2 no implementado (§4).**

## 1. Cómo se activa el AEL desde `libObj` (VERIFICADO estático)
- Nombres (tabla de `libObj` `0xfdb5ec`, `MSGID_*` = `0x7500 + i − 1`, `PARAMID_*` = `0x9500 + i − 726`, `VALUEID_*` = `i − 2076`, calibrada con `0x75fa` de g22): `MSGID_SET_AEL_CMD` = **`0x75be`**, `PARAMID_AEL` = **`0x96e6`** (`_SET`/`_ACT` `0x96e7/8`), `VALUEID_AEL_ON` = **`0x1d5`**, `VALUEID_AEL_OFF` = **`0x1d6`**. Alternativa no usada: `MSGID_SET_AELOCK_MODE_CMD` `0x7610` + `PARAMID_AELOCK_MODE` `0x9795` (modo normal/puntual: `0x2d6/0x2d7`, off `0x2d8`).
- Receptor: `ObjCamera` se suscribe a `0x75be` (`0x98be22`); su conversor (`0x9a4420`) acepta el mensaje, lee `PARAMID 0x96e6` y traduce `0x1d5`→1 / `0x1d6`→0 (`0x9a446c`), y lo reenvía a `av-cam` como mensaje crudo tipo 5, **id `0x405e`**, con el valor en los 4 B siguientes (`0x9a44c8…`). `av-cam` (LIRO) es quien aplica el bloqueo: **ningún código del modelo de `libObj` emite `0x75be`** (sin `movw #0x75be` ni palabra `0x000075be` fuera de ese receptor; los textos `SetAELockForLiro`/`CamMsgConv` son del conversor av-cam→libObj, `0x4c157c`).
- Emisión desde código nuevo: la misma secuencia que `0x67b4b0` (emisor de `0x750a`, mismo objeto `ActionObject`): `ObjMsg(0x3100, 0x75be)` (`blx 0xde540`), `ParamStd<int,7>(valor)` (`0xdf00c`), `AddParam(0x96e6)` (`0xe01a8`), destructor del parámetro (`0xdd7a8`), `0x42067c(8)` = objeto 8 (`ObjCamera`), `IssueCommandAsync` (`0xdc144`) y destructor del mensaje (`0xddd94`). Sin `SetCommonRelayParam` (el emisor `0x67b4b0` tampoco lo usa).

## 2. Nivel 1: ajuste «Seguim. AE» (Normal/Bloqueado) y cueva
- Ajuste en la carpeta «CFW» (`cfw_ajustes`): «Seguim. AE», id de Backup `0x1070216`, pid `0xEF`, Normal (índice 0, de fábrica) / Bloqueado. La carpeta «CFW» pasa a 7 ajustes en **dos páginas** (6 + 1: «Seguim. AE» está en la página 2).
- Cueva (mismo cuerpo de la función muerta `0x2648d8`, ampliado de `0x300` a `0x500` B; ocupa ~`0x400`; sigue sin referencias, el test las comprueba):
  - pieza `ael(r0 = 0x1d5/0x1d6)`: emite el mensaje de §1;
  - `inicio` (`0x67de2c`): además del contador, pone a 0 el indicador de bloqueo (`CTR+4`, misma cola de página del `.bss`);
  - `toma` (`0x66df4e`): con «Intervalo» ≠ Off, al contar la **toma 1** y con «Seguim. AE» = Bloqueado, llama a `ael(0x1d5)` y marca `CTR+4 = 1`; las tomas siguientes reutilizan esa exposición;
  - nuevo gancho `libera` (`0x66deb0`, `bl 0x67da50` = cancelar el tick, salida común de «fin de serie» y de la rama `REPEAT == 0`; bytes `0ff0cefd`): si `CTR+4 = 1`, lo borra y llama a `ael(0x1d6)`; después ejecuta el `bl 0x67da50` original con `r0` intacto.
- Keystone codifica mal `blx`/`b.w` absolutos según la posición (en este parche se vio `blx 0xdd5f8` en vez de `0xdd5f4`): las ramas a destino absoluto se codifican aparte (`_ens`, marcador + `bl`/`b_w`/`_blx` propios) y el test las decodifica con Capstone.

## 3. Pruebas
- `tests/test_g61_intervalo.py` (7) y `python3 scripts/g61/intervalo_patch.py`: bytes originales de los 6 ganchos, idempotencia, ramas de la cueva a destino exacto, cueva sin referencias y Unicorn sobre `libObj` real (Backup simulado; las llamadas ajenas se anotan y omiten):
  - original, «Normal», «Intervalo» Off y byte fuera de tabla: **ningún** mensaje AEL en 12 tomas;
  - «Bloqueado», 5 s, N = 10: mensaje `ObjMsg(0x3100, 0x75be)` + `AddParam(0x96e6)` con valor `0x1d5` **solo en la toma 1**; en la toma 10 (la serie acaba por `0x66deae`) el mismo mensaje con `0x1d6`, indicador a 0, estado 0; el resto de la lógica de g61 (esperas, 9 rearmes) intacta;
  - «Bloqueado», sin tope: `0x1d5` una vez, sin `0x1d6` (la serie sigue), 12 rearmes.
- **Arnés** (overlay y perfil propios `g62`, puerto 8762, `cfw_ajustes.construir` + `libObj` parcheado): ver §5.

## 4. Nivel 2 (suavizado Bajo/Medio/Alto): no implementado; puntos localizados (INTERVAL-AE-F2)
Fórmula prevista: compensación = k·(EV_medido − EV_anterior) − (EV_medido − EV_anterior), k = 0,25/0,5/1.
- **Imponer la compensación (viable, no implementado)**: `MSGID_SET_EXPOSURE_BIAS_CMD` = `0x759e`, `PARAMID_EXPOSURE_BIAS` = `0x9652` (`_STEP` `0x9653`, `_SW` `0x9654`; `…_NUMER/DENOM` `0x9803/0x9804`). La pieza `ael` sirve de plantilla (cambiar id de mensaje/parámetro); falta fijar la **codificación del valor** (entero en pasos de 1/3 EV según `EXPOSURE_BIAS_STEP`; no medida) y el efecto sobre el AE de `av-cam`.
- **Leer el EV medido (bloqueante)**: lo que `libObj` recibe de `av-cam` son la velocidad/diafragma/ISO **ya decididos** (`0x2014` → `0x8531`, `0x951c/0x951d`, [g40](g40-velocidad-maxima.md); ISO `0x1002` → `0x951e`), no la luz medida. Candidatos sin verificar: `PARAMID_EV_ERROR` `0x95b2` / `EV_ERROR_SHIFTED` `0x95b3` (`EV_ERROR_VALID` `0x95b1`) y `RECOMMENDED_EXPOSURE_INDEX` `0x993e`; nadie en `libObj` los lee todavía y en el arnés el AE no corre (`ae.py` los fabrica), así que no se pueden validar sin cámara. Con exposición Tv/Av/ISO ya decidida se podría estimar EV = f(Tv, Av, ISO) como sustituto, pero con AE por toma ya compensado por el bias anterior (bucle realimentado) y sin medida real de la escena: descartado como diseño.
- Estado por toma necesario: EV_anterior (palabra más en `CTR+8`), y la lectura del EV medido **después** del AE de la toma y **antes** del disparo siguiente (el gancho `0x66df4e` es antes del siguiente tick, no del AE).

## 5. Arnés
Ajustes personalizados p. 4 → «CFW»: página 1 con los seis ajustes de g61 (`img/g62-carpeta-cfw-pagina1.png`); página 2 con «Seguim. AE: Normal» (`img/g62-seguim-ae-pagina2.png`, derecha desde la última fila); la lista ofrece Normal/Bloqueado (`img/g62-seguim-ae-lista.png`); tras elegir «Bloqueado» (`img/g62-seguim-ae-bloqueado-guardado.png`) el `nvram.json` queda con `"1070216": "01"`. Qemu parado y perfil `g62` borrado. **No se disparó una serie**: el arnés no ejecuta el AE ni el autodisparador continuo (g61 §5).

## 6. Límites
- **Sin cámara**: no se ha medido que `av-cam` aplique el bloqueo con ese mensaje (el mensaje y su receptor son estáticos); el arnés no ejecuta el AE real (`ae.py`) ni el disparo continuo (g60 §4).
- ObjCamera contestará con `0x75bf` (CMP) y el evento `0x85xx` de AEL; el modelo no los consume (no medido el efecto de un CMP sin receptor).
- Si la serie se cancela por una vía que no pase por `0x66deb0` (p. ej. apagar, cambiar el modo de Drive), el AEL queda activo hasta pulsarlo o volver a empezar una serie; con «Normal» no hay nada que liberar.
- «Seguim. AE» se lee en la toma 1 de cada serie (no en el arranque): cambiarlo durante la serie solo surte efecto en la siguiente.
- Misma salvedad de g61 sobre cueva «sin referencias» y la cola de página del `.bss` (ahora 8 B).
