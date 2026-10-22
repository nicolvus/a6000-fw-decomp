# S117 — `[AUGI]`: la cabecera de 32 B y sus dos representaciones

> Hito de la **línea de ingeniería inversa general**. Todo lo que sigue sale de los bytes de
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21, 11 427 236 B, sha256
> `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`), con la convención
> verificada **vaddr = 0x43541000 + file_offset**. Solo análisis estático de bytes; sin REA,
> sin Ghidra, sin ejecutar firmware, sin cámara. Cada afirmación lleva su dirección y, cuando
> aplica, la cita literal del texto o de la instrucción. Lo no comprobado está marcado
> **NO VERIFICADO** (§10).
>
> Este hito cierra el punto que dejó abierto S83 §2.8 («Formato exacto de la cabecera AUGI»)
> en `analysis/s83_modules/minor_modules.md`. No repite S70–S115 ni toca `[SFRS]` (S116).

## 1. Qué es `[AUGI]` (sin expandir la sigla)

`[AUGI]` no es una etiqueta de traza de un subsistema como `[SFRS]` (S116) o `[CAM_IMAGER]`
(S115). En este firmware el token aparece en **dos familias de texto** que hablan de lo mismo:

- **impresores de una estructura** (`[CodecIF][AUGI][dec]…`, `[CodecIF][AUGI][enc]…`), cuyos
  nombres de campo son los de una cabecera de 32 B: `length`, `num_AUs`, `PTS`, `DTS`,
  `nextHRDBuffer`, `nextPTS`, `size_SPS`, `size_PPS`, `PictureType`, `seq_parameter_set_id`…
  (`0x43c6a909`–`0x43c6b517`);
- **un volcado de depuración** `[AUGI] campo = %d` con los mismos nombres
  (`0x43cd993d`–`0x43cd9c8d`).

Las clases que lo manipulan están nombradas en el propio binario: `DecExAugiConverter`,
`DecInAudioAugiConverter`, `DecInVideoAugiConverter`, `EncExAugiConverter`
(`0x43c6a8db`, `0x43c6acc5`, `0x43c6b02e`, `0x43c6b554`) y la entrada de API
`StrmEngEncCIIf::CodecEventCreateVAUGI` (`0x43c66fbf`). Es decir: **AUGI es el nombre de una
cabecera de bloque de códec y de las clases convertidoras que la leen y escriben**.

**La sigla no aparece expandida en ningún byte del binario**; aquí no se inventa su
significado (§10). Tampoco se afirma que `length` cuente carga útil, cabecera o ambas: eso no
está verificado.

## 2. Cifras verificadas

| magnitud | valor | cómo se obtiene |
|---|---:|---|
| cadenas que contienen `[AUGI]` | **75** | `data.find(b"[AUGI]")` normalizado al inicio real de la racha imprimible |
| cadenas con prefijo `[AUGI]` | 26 | conteo directo sobre el texto |
| cadenas con prefijo `[CodecIF]` | 49 | idem (`[CodecIF][AUGI]…`) |
| puntos de emisión (`ldr` + `add pc`) | **86** | pares PIC estrictos (§9) |
| cadenas sin referencia resuelta | **0** | `missing` vacío; el script aborta si no |
| funciones contenedoras | **6** | prólogo Thumb más cercano por delante |
| cadenas referenciadas por más de una función | 10 | 1 en tres funciones + 9 en dos |
| comprobación aritmética | 86 = 75 + 2 + 9 | una cadena con 3 sitios y nueve con 2 |
| primer / último `[AUGI]` | `0x43c6a28a` / `0x43cd9c8d` | dos clusters: `0x43c6a28a`–`0x43c6b517` y `0x43cd993d`–`0x43cd9c8d` |
| rango de código de los impresores | `0x436150ce`–`0x436163c0` | 4 funciones contiguas (≈5 KB) |
| rango del dumper | `0x4391ca90` (+ llamadas en `0x4391d12e`/`0x4391d136`) | función única |

Las 75 cadenas se reparten así: **20** del impresor `enc`, **15** del dec «ex», **10** del dec
de audio, **15** del dec de vídeo, **25** del dumper y **1** del handler de `augicsv` (la suma
por función da 86 porque hay cadenas compartidas; las cadenas distintas son 75).

## 3. La cabecera de 32 B (copia «host», little-endian)

El layout sale del **dumper `0x4391ca90`**, que lee campo a campo con offsets fijos
(`0x4391caa0`–`0x4391cbb4`), y coincide con lo que escribe el escritor de audio
`0x435d63a0` (`0x435d6448`–`0x435d64ae`) y con el `rev` + recorrido de 32 B de
`0x436163c0`. Tamaño y paso:

- **32 B** y **stride 32**: `lsls r3, r1, #5` en `0x436163c2` (bytes `4b 01 88 b0`) y
  `lsls r4, r4, #5` en `0x436150ea` (bytes `64 01 03 e0`).
- La copia en memoria es **little-endian** (todos los `ldr`/`ldrh`/`str` del dumper y del
  escritor son nativos ARM, sin `rev`). La copia que viaja en el stream va **big-endian por
  palabra de 4 B** (§4).

| off | tipo | campo | evidencia (lectura / escritura) |
|---:|---|---|---|
| `+0x00` | u32 | `length` | lee `0x4391caa0: ldr r1,[r4]`; escribe `0x435d644c: str.w fp,[r8,sb]` |
| `+0x04` | u16 | `Reserved2` | lee `0x4391caaa: ldrh r1,[r4,#4]` |
| `+0x06` | u8 | `flags`: bit0 `end_flag`, bit1 `PS_flag`, bit2 `EP_flag`, bit3 `DTS_flag`, bits4-7 `Reserved1` | `0x4391cab2` (`ldrb`), `0x4391cab6` (`and #1`), `0x4391cac4`/`0x4391cad2`/`0x4391cae0` (`ubfx #1/#2/#3`), `0x4391caee` (`lsrs #4`) |
| `+0x07` | u8 | `Num_AUs` | lee `0x4391caf8: ldrb r1,[r4,#7]`; escribe `0x435d6448: strb r3,[r4,#7]` con `r3=1` |
| `+0x08` | u32 | `PTS` | lee `0x4391cb02: ldr r1,[r4,#8]`; escribe `0x435d64ae: str r2,[r4,#8]` |
| `+0x0c` | u32 | `DTS` | lee `0x4391cb0c: ldr r1,[r4,#0xc]` |
| `+0x10` | u32 | `nextHRDBuffer` | lee `0x4391cb16: ldr r1,[r4,#0x10]` |
| `+0x14` | u32 | `nextPTS` | lee `0x4391cb20: ldr r1,[r4,#0x14]` |
| `+0x18` | u8 | `pic_parameter_set_id` | lee `0x4391cb2a: ldrb r1,[r4,#0x18]` |
| `+0x19` | u8 | `num_PPS` | lee `0x4391cb34: ldrb r1,[r4,#0x19]` |
| `+0x1a` | u8 | bits0-4 `seq_parameter_set_id`, bits5-7 `num_SPS` | `0x4391cb40: and #0x1f`; `0x4391cb4e: lsrs #5` |
| `+0x1b` | u8 | bit0 `change_PPS_flag`, bit1 `change_SPS_flag`, bit2 `Reserved4`, bit3 `Reffered_flag` (sic), bits4-6 `PictureType`, bit7 `Reserved3` | `0x4391cb5a`/`0x4391cb68`/`0x4391cb76`/`0x4391cb84`, `0x4391cb92: ubfx #4,#3`, `0x4391cba0: lsrs #7` |
| `+0x1c` | u16 | `size_PPS` | lee `0x4391cbaa: ldrh r1,[r4,#0x1c]` |
| `+0x1e` | u16 | `size_SPS` | lee `0x4391cbb4: ldrh r1,[r4,#0x1e]` |

Los nombres son **los literales del firmware** (incluida la grafía `Reffered_flag` de
`0x43cd9c01`); no se normalizan. `Reserved1`…`Reserved4` son nombres del propio dumper, no
campos que este hito haya deducido.

## 4. La copia en stream: cada palabra de 4 B en big-endian

La cabecera no viaja tal cual: se **invierte byte a byte dentro de cada palabra de 4 B**. La
prueba es una función de 4 B, `0x43a5cb12`, cuyos bytes son `08 ba 70 47` = `rev r0,r1` /
`bx lr`, y tres usos del mismo patrón:

- `0x435d64e8`–`0x435d6500`: bucle del escritor que hace `bl 0x43a5cb12`, `str.w r0,[r7,r8]`
  y termina con `cmp.w r8,#0x20` (32 B).
- `0x43a7e32e` y `0x43a7e6aa`: dos copias de 32 B que invierten cada palabra
  (`cmp r3,#0x20` en `0x43a7e34c` y `0x43a7e6c8`). La primera la usa el impresor
  `0x43615eac` antes de leer los campos.

Efecto sobre los offsets (palabra `n` → bytes `4n..4n+3` invertidos):

| bytes en el stream | contenido | offset «host» |
|---:|---|---:|
| `0x00-0x03` | `length` (BE) | `+0x00` |
| `0x04` | `Num_AUs` | `+0x07` |
| `0x05` | `flags` (end/PS/EP/DTS/Reserved1) | `+0x06` |
| `0x06-0x07` | `Reserved2` (BE) | `+0x04` |
| `0x08-0x0b` | `PTS` (BE) | `+0x08` |
| `0x0c-0x0f` | `DTS` (BE) | `+0x0c` |
| `0x10-0x13` | `nextHRDBuffer` (BE) | `+0x10` |
| `0x14-0x17` | `nextPTS` (BE) | `+0x14` |
| `0x18` | `flags2` (change_PPS/change_SPS/Reserved4/Reffered/PictureType/Reserved3) | `+0x1b` |
| `0x19` | `seq_parameter_set_id` (bits0-4) + `num_SPS` (bits5-7) | `+0x1a` |
| `0x1a` | `num_PPS` | `+0x19` |
| `0x1b` | `pic_parameter_set_id` | `+0x18` |
| `0x1c-0x1d` | `size_SPS` (BE) | `+0x1e` |
| `0x1e-0x1f` | `size_PPS` (BE) | `+0x1c` |

Los cuatro bytes finales quedan **permutados en orden inverso** (`+0x18`→`0x1b`,
`+0x19`→`0x1a`, `+0x1a`→`0x19`, `+0x1b`→`0x18`): es la consecuencia del `rev` por palabra, no
un campo aparte.

## 5. Quién escribe y quién lee

### 5.1 Escritor de audio

`0x435d63a0` es el único escritor de AUGI identificado. El literal que resuelve en
`0x435d63f2`/`0x435d63f4` es `0x43c4b334`:

> `Int32 McAvcEncAudioSeqCtrlState::WriteAugi()`

y la cadena de fichero asociada es `seqCtrl/audio/mcAvcEncAudioSeqCtrlState.cpp`
(`0x43c4b36a`). Instrucciones verificadas:

| addr | instrucción | lectura |
|---|---|---|
| `0x435d640c` | `lsl.w r8,r2,#5` (bytes `4f ea 42 18`) | índice × 32 |
| `0x435d641a`–`0x435d6422` | `bfi` sobre `+6` | pone `end_flag` desde `[r7,#3]` bit7 |
| `0x435d6448` | `strb r3,[r4,#7]` (bytes `e3 71`) con `r3=1` | `Num_AUs = 1` |
| `0x435d644c` | `str.w fp,[r8,sb]` | `length` |
| `0x435d6472`–`0x435d6478` | `orr #4` | `EP_flag` |
| `0x435d64ae` | `str r2,[r4,#8]` | `PTS` |
| `0x435d64d2`–`0x435d6512` | `rev` por palabra + volcado de 32 B | copia stream (§4) |

Lo llaman al menos dos wrappers: `0x43a5cb26` (`bl 0x435d63a0` en `0x43a5cb4c`) y
`0x43a5d182` (`bl 0x435d63a0` en `0x43a5d1a8`). Su nombre de clase es el de la firma RTTI; que
el hito lo llame «escritor de audio» se debe a `[ENCAUDSMPL]`/`[ENCAUDSTAT]` en las cadenas
vecinas, **no** a que se haya verificado qué datos empaqueta.

**No se ha identificado un escritor de vídeo equivalente**: `0x4360b6f0` es la entrada de API
`void StrmEngEncCIIf::CodecEventCreateVAUGI(UInt32, const UInt32*)` (literales en
`0x4360b712` y `0x4360b73e` → `0x43c66fbf`), pero el cuerpo que materializa la cabecera de
vídeo no está localizado (§10).

### 5.2 Lector / dumper

`0x4391ca90` vuelca la cabecera con 25 trazas `[AUGI] … = %d`; la primera es
`[AUGI] ----------------------------------\n` (`0x4391ca96` → `0x43cd993d`) y la última
`[AUGI] size_SPS              = %d\n` (`0x4391cbb6` → `0x43cd9c8d`). Se le llama con
`bl 0x4391ca90` desde `0x4391d12e` y `0x4391d136`, dentro de la función `0x4391d01c`. Usa
`0x43b35c50` como salida (no el `printf` habitual `0x435ab880`). El nombre del dumper es
**NO VERIFICADO**; su papel, no: lee el layout de §3 offset a offset.

## 6. Las 6 funciones

«Sitios» = pares `ldr`+`add pc` que resuelven a una cadena con `[AUGI]`; «cadenas» = distintas.

| función | nombre / papel | sitios | cadenas | evidencia |
|---|---|---:|---:|---|
| `0x436150ce` | handler del comando de depuración `augicsv` (a/v) | 1 | 1 | `0x436150e0` → `0x43c6a25c` `Usage: augicsv <a(audio)|v(video)>`; `0x43615108` → `0x43c6a28a` `[AUGI][PRINT] size[%d] %s`; `lsls r4,r4,#5` en `0x436150ea` |
| `0x43615eac` | `DecExAugiConverter::Print(void*)` | 15 | 15 | `0x43615ebc` → `0x43c6a8db` `virtual void DecExAugiConverter::Print(void*)` |
| `0x4361610c` | `DecInAudioAugiConverter::Print(void*)` | 10 | 10 | `0x43616116` → `0x43c6acc5` `virtual void DecInAudioAugiConverter::Print(void*)` |
| `0x43616200` | `DecInVideoAugiConverter::Print(void*)` | 15 | 15 | `0x4361620a` → `0x43c6b02e` `virtual void DecInVideoAugiConverter::Print(void*)` |
| `0x436163c0` | `EncExAugiConverter::Print(UInt16, const void*)` | 20 | 20 | `0x436163d2` → `0x43c6b554`; stride 32 en `0x436163c2` |
| `0x4391ca90` | volcado de depuración del bloque | 25 | 25 | `0x4391ca96` → `0x43cd993d`; `0x4391cbb6` → `0x43cd9c8d` |

El nombre de `0x436150ce` y el de `0x4391ca90` son **NO VERIFICADO**; los otros cuatro salen
de la firma RTTI que el propio código pasa a la traza. Las direcciones de función son
**prólogos Thumb heurísticos** (el `push` más cercano por delante), no símbolos del firmware.

## 7. Tres vistas distintas: no son la misma estructura

La cabecera de 32 B de §3 **no** es la estructura que leen los tres impresores dec. Son tres
vistas separadas, y confundirlas produce offsets falsos:

| vista | 32 B invertidos? | offsets leídos | cita |
|---|---|---|---|
| `0x43615eac` (`DecEx`) | **sí** (`bl 0x43a7e32e` sobre una copia en pila) | `+0x00 length`, `+0x04 offset`, `+0x08` (bit0 `EP_flag`, bits2-3 `PTS_DTS_flag`), `+0x09 AUGI_type`, `+0x0a num_AUs`, `+0x0c PTS`, `+0x10 DTS`, `+0x14 STC_Offset_Sign`, `+0x15 discontinuity_cc`, `+0x17` (bit4 `end_flag`, bit5 `start_up_flag`, bits0-3 `discontinuity_flags`), `+0x18 STC_Offset` | `bl 0x43a7e32e` en `0x43615eb6`; `ldr [sp]` en `0x43615ec2`; `ldr [sp,#4]` en `0x43615ed0`; `ldrb [sp,#0xa]` en `0x43615ede`; `ldrb [sp,#9]` en `0x43615eee`; `and #1` en `0x43615f16`; `ubfx #2,#2` en `0x43615f02`; `ldrb [sp,#0x17]` en `0x43615f3c` (`ubfx #5,#1`/`#4,#1`/`and #0xf` en `0x43615f46`/`0x43615f5a`/`0x43615f6e`); `ldrb [sp,#0x15]` en `0x43615f7e`; `ldrb [sp,#0x14]` en `0x43615f8e`; `ldr [sp,#0x18]` en `0x43615f9e` |
| `0x4361610c` (`DecInAudio`) | no | `+0x00 length`, `+0x08 pts_dts_flag`, `+0x09 augi_type`, `+0x0c pts`, `+0x10 pts_33` (u8), `+0x1c stc_offset`, `+0x20 stc_offset_33`, `+0x21 stc_offset_sign`, `+0x22 end_flag` | `ldrb [r5,#0x10]`, `ldr [r5,#0x1c]`, `ldrb [r5,#0x20..0x22]` |
| `0x43616200` (`DecInVideo`) | no | los de audio más `+0x04 offset`, `+0x14 dts`, `+0x18 dts_33` (u8), `+0x24 e_ptm`, `+0x28 e_ptm_33`, `+0x29 stc_offset_sign_33`, `+0x2a end_flag_33` | lecturas directas hasta `[r5,#0x2a]` |

Consecuencia: **`+0x04` es `Reserved2` en la cabecera de 32 B y `offset` en la vista DecEx**;
`+0x06` es `flags` (end/PS/EP/DTS) en la cabecera y **no se lee** en ninguna vista dec;
`+0x1b` es `flags2` (change/PictureType) en la cabecera y **no aparece** en las vistas dec.
Son estructuras de propósito distinto que comparten los primeros campos (`length`, PTS).

Dos funciones más usan la vista dec sin ser impresores:

- `0x43a7e384` rellena 32 B y fija `[sp+9]=2` (`AUGI_type`) y `[sp+0x17]=0x10` (bit4
  `end_flag`): usa el layout **dec-side**, no el de 32 B de §3.
- `0x43a7e70c` rellena solo los bytes `0`, `4`, `5`, `8` y `0xc` desde un struct de `0x34` B.
  Su papel exacto es **NO VERIFICADO**.

## 8. Diferencial A6000 fw3.21 vs A7S fw3.20

Blob A7S: `firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/
nflasha3_unpacked_unpacked/av-cam.bin` (sha256
`b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`). Comparación texto a
texto, ignorando especificadores de formato (`%…` → `%`):

| magnitud | valor |
|---|---:|
| cadenas en A6000 fw3.21 | 75 |
| cadenas en A7S fw3.20 | 75 |
| **comunes** | **75** |
| exclusivas de A6000 | **0** |
| exclusivas de A7S | **0** |
| primer / último en A6000 | `0x43c6a28a` / `0x43cd9c8d` |
| primer / último en A7S | `0x43c6740f` / `0x43cca5a5` |

El **conjunto de textos es idéntico**; lo que cambia es la **posición** (el bloque se desplaza
unos `0x2e7b` B y el orden de las cadenas no coincide). No se ha comparado el código que las
emite ni el layout en la A7S: **NO VERIFICADO** si la cabecera de la A7S tiene los mismos
offsets.

## 9. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 75 cadenas y sus dos clusters | `scan_augi.py` busca `b"[AUGI]"`, retrocede al inicio de la racha imprimible y deduplica |
| 86 sitios y 75/75 resueltos | emparejamiento PIC estricto (§9.1); `missing` vacío y la suma por función es 86 |
| 6 funciones | prólogos `push {…,lr}` / `push.w` por delante del sitio |
| stride 32 y tamaño 32 | `lsls #5` en `0x436163c2` (bytes `4b 01`) y `0x436150ea`; bucle `cmp #0x20` en `0x435d64fc` |
| `rev` por palabra | `0x43a5cb12` = bytes `08 ba 70 47` (`rev r0,r1` / `bx lr`) |
| layout de §3 | 14 lecturas del dumper `0x4391ca90` y escrituras del escritor `0x435d63a0`, instrucción a instrucción |
| tres vistas dec distintas | lecturas con `[sp,…]` tras `0x43a7e32e` vs lecturas directas `[r5,…]`, con offsets incompatibles |
| identidad de las 4 clases | literales RTTI `0x43c6a8db`, `0x43c6acc5`, `0x43c6b02e`, `0x43c6b554` |
| escritor = `WriteAugi` | literal `0x43c4b313` `Int32 McAvcEncAudioSeqCtrlState::WriteAugi()` y fichero `0x43c4b36a` |
| A7S 75/75 | mismo extractor y normalización sobre el blob A7S |

### 9.1 Regla PIC aplicada

Igual que en S116: barrido con fronteras Thumb (4 B si el halfword es prefijo de instrucción
de 32 bits, si no 2), se empareja **solo el `ldr` inmediatamente anterior del mismo registro**
en la misma función, y `destino = palabra_literal + (addr_add + 4)` **sin alinear**. Los
candidatos lejanos producían colisiones reales (la misma palabra literal reutilizada por otro
registro) y se descartaron. El script aborta si una cadena queda sin referencia o un sitio sin
función.

## 10. NO VERIFICADO / abierto

- **Significado de la sigla `AUGI`** y de `AUs`, `PS`, `EP`, `DTS`, `STC`, `HRD`, `PTS`,
  `e_ptm`: el firmware no las expande; no se han inventado expansiones.
- **Semántica de los valores**: qué significan `AUGI_type`, `PictureType` (3 bits), los cuatro
  `Reserved`, `discontinuity_flags`/`discontinuity_cc`, `start_up_flag`, `STC_Offset_Sign`,
  `e_ptm`. Solo constan offsets y nombres.
- **Qué cuenta `length`** (¿carga útil? ¿cabecera incluida? ¿siguiente AU?) y qué contiene
  `nextHRDBuffer`/`nextPTS`.
- **Escritor de vídeo**: no localizado; `0x4360b6f0` es solo la entrada de API.
- **Relación entre la cabecera de 32 B y la vista dec**: comparten `length` y PTS en el mismo
  offset, pero el resto no coincide; no se ha verificado si una se convierte en la otra ni
  dónde.
- **Papel de `0x43a7e70c`** (rellena 5 bytes sueltos desde un struct de `0x34` B).
- **Contenido de `size_SPS`/`size_PPS`**: no se han localizado ni decodificado los bytes SPS/PPS.
- **Nombre del handler `0x436150ce`** y del dumper `0x4391ca90`.
- **Layout en la A7S**: los textos son idénticos, pero no se ha comprobado que los offsets y
  el `rev` sean los mismos.
- La atribución a función es **heurística** (prólogo Thumb), no símbolos del firmware.

## 11. Ficheros de este hito y reproducción

| fichero | contenido |
|---|---|
| `augi_strings_raw.json` | las 75 cadenas con vaddr/offset/texto/refs/funcs |
| `augi_refs.json` | los 86 sitios PIC, destino → direcciones |
| `augi.json` | resumen: recuentos, cadenas, funciones, `layout`, `identities`, `dec_views`, `writers`, diferencial A7S |
| `scan_augi.py` | extractor único y reproducible (regenera los tres JSON) |
| `docs/capture/s117-augi.md` | nota corta de captura |
| `tests/test_s117_augi.py` | tests sobre bytes reales |

Reproducir:

```
.venv/bin/python analysis/s117_augi/scan_augi.py
.venv/bin/python -m pytest tests/test_s117_augi.py
```

## 12. Revisión del agente principal (correcciones aplicadas)

1. **La cabecera no era una sola estructura**: el borrador mezclaba la cabecera de 32 B con
   los campos de los impresores dec y asignaba `+0x04 offset`, `+0x09 AUGI_type` o `+0x2a` a
   la cabecera. Comprobado instrucción a instrucción: son **tres vistas** (§7), y solo
   `DecEx` invierte 32 B; las otras dos leen la estructura directamente.
2. **Byte order**: el borrador decía «big-endian» sin matiz. La copia host es
   **little-endian**; el stream invierte **cada palabra de 4 B** (`rev`), no el bloque entero
   (§4). La diferencia se ve en los cuatro bytes `+0x18`–`+0x1b`, que quedan en orden inverso.
3. **Recuento**: el borrador hablaba de «~70 cadenas» y no separaba sitios de cadenas. Ahora
   son **75 cadenas / 86 sitios / 6 funciones**, con la aritmética de las 10 compartidas
   explícita.
4. **Regla PIC**: el borrador emparejaba cualquier `ldr` anterior del registro; eso producía
   colisiones. Se fijó la regla estricta de §9.1 y se validó resolviendo 75/75.
5. **Escritor**: el borrador atribuía el volcado a `0x4391cc2c`, cuyos literales apuntan a
   `[CONFIG] code_work_area…`; descartado. El escritor real es `0x435d63a0`
   (`WriteAugi`), con el literal resuelto en `0x435d63f2`/`0x435d63f4` → `0x43c4b313`.
6. **Diferencial A7S**: el borrador suponía cambios de texto. Falso: las **75 cadenas son
   idénticas**; solo cambia la posición.
7. **Siglas**: el borrador expandía `AUGI` y `AU`. Retirado; §10 lo declara NO VERIFICADO.

---

## Revisión del agente principal (21-10-2026)

**Verificado byte a byte (correcto):**

1. **Recuento**: 75 apariciones de `[AUGI]` → **26 cadenas** con el prefijo `[AUGI]` y 49 con
   `[CodecIF][AUGI]…`; en la A7S fw3.20 **exactamente las mismas** 75 apariciones y las mismas
   26 cadenas → bloque **idéntico** en ambas cámaras.
2. **Dos familias de texto** (impresores de estructura en `0x43c6a909`–`0x43c6b517` y volcado
   `[AUGI] campo = %d` en `0x43cd993d`–`0x43cd9c8d`), dos *clusters* de cadenas.
3. **Clases convertidoras** nombradas en el binario: `DecExAugiConverter` `0x43c6a8db`,
   `DecInAudioAugiConverter` `0x43c6acc5`, `DecInVideoAugiConverter` `0x43c6b02e`,
   `EncExAugiConverter` `0x43c6b554`, y la entrada de API
   `StrmEngEncCIIf::CodecEventCreateVAUGI` `0x43c66fbf` → **AUGI es el nombre de una cabecera de
   bloque de códec**, no el de un subsistema de trazas.
4. **Rigor**: el informe **no expande la sigla** (no aparece en ningún byte) y **no afirma** qué
   cuenta `length`; además el script aborta si alguna cadena queda sin referencia.
5. **Cobertura**: 86 puntos de emisión y **0** cadenas sin referencia; la comprobación
   aritmética (86 = 75 + 2 + 9: una cadena con 3 sitios y nueve con 2) es una validación
   interna buena.

**Nota**: el recuento de sitios (86) depende de la regla de emparejamiento; con la *kill
analysis* del escáner canónico puede variar. Véase
`analysis/s106_imaging_cap/pic_xref_methodology.md`.
