# G61 — Intervalómetro sobre el autodisparador continuo de `libObj` 3.21: ajustes «Intervalo» y «N. disparos», cueva con contador y parada (15-11-2026)

Implementa lo decidido tras [g60](g60-autodisparador-continuo.md). Solo ficheros del `.dat` (`libObj.so`, `viewUnified2.so`, `CautionConfig.so`, `string_*.uxc`); sin CFW construido; sin tocar `scripts/gui/harness/`. Código: `scripts/g61/intervalo_patch.py`, tabla `scripts/cfw_ajustes.py`, tests `tests/test_g61_intervalo.py` (5) y `python3 scripts/g61/intervalo_patch.py`. Resultado: **implementado y probado en Unicorn sobre los bytes reales; ajustes verificados en el arnés; Focus Bracket sin implementar (§6).**

## 1. Ajustes (carpeta «CFW», g56)
- «Intervalo»: id de Backup `0x1070214`, pid `0xED`, Off/2 s/5 s/10 s/30 s/60 s/5 min (el byte es el índice; el valor son segundos).
- «N. disparos»: id `0x1070215`, pid `0xEE`, 10/30/60/100/300/999/Sin tope (7 opciones, tope G36; índice 0 = 10, por lo que con «Intervalo» ≠ Off y sin tocar este ajuste se para a las 10 tomas; «Sin tope» = 0).
- La carpeta «CFW» pasa a 6 ajustes (Bulb Timer, CFW test, Focus Bracket, Focus Br. paso, Intervalo, N. disparos), una sola página.

## 2. Retardo (3 ganchos)
La constante está **en milisegundos**: el tick suma `+0x1b8 += +0x1a0` (periodo 100 de arranque) y compara con `+0x1bc` (`0x2710` = 10 000 = 10 s). Las copias de las tres constantes terminan todas en `str.w r3,[r4,#0x1bc]`: `0x67e18e`, `0x688742`, `0x689aee` (`c4f8bc31` en las tres; la cuarta `0x689b16` es el caso «sin espera», r3 = 0, y no se toca). Cada una pasa a `bl cueva_espera`, que: si r3 = 0 (modo sin espera) o `REPEAT` (`+0x1a4`) = 0 (autodisparador simple) deja la de fábrica; si no, lee «Intervalo» con la **lectura nativa de Backup** (`blx 0xdd5f4`, id en r0 y búfer en r1, igual que `0x688684`; el búfer se pone a 0 antes) y, si el índice ≠ 0, r3 = segundos·1000. Después ejecuta el `str.w` original.

## 3. Contador y parada
- Inicio (`0x67de2c`, `str.w r1,[r4,#0x1b4]` con r1 = 1, arranque de `TIMER_REQ_CMD`): `bl cueva_inicio` ejecuta el `str.w` y pone el contador a 0.
- Fin de toma (`0x66df4e`, `bl 0x131f28`): `bl cueva_toma`. Con «Intervalo» ≠ Off incrementa el contador; si N ≠ 0 y contador ≥ N: contador = 0, `REPEAT` = 0, `+0x1c8` = 0 y `b.w 0x66deae`, la misma salida que usa la rama «`REPEAT == 0`» de ese manejador (cancela el tick `0x67da50`, estado 0, restaura los valores por defecto `0x68c62a`, avisa con `0x753f`). Si no, `b.w 0x131f28` con r0–r3 y `lr` restaurados: el rearme de fábrica, idéntico.
- Contador: palabra en la **cola de página del `.bss`** (VA `0x10e2c00`; el `.bss` acaba en `0x10e2bd0` = `0xfd25a4 + 0x11062c` y la página se mapea hasta `0x10e3000`), direccionada PC-relativa (`adr.w` + literal `CTR − lit`). Es el único «lugar de RAM» sin ninguna referencia posible; el campo de objeto se descartó: en `0x660000–0x6a0000` casi cada palabra entre `+0x194` y `+0x300` se usa y no se pudo acotar el tamaño del objeto.

## 4. Cueva validada (límite: no es una zona de ceros)
`libObj` 3.21 **no tiene** zonas a cero ni relleno en `.text` (barrido: 0 huecos ≥ 20 NOP o ≥ 48 B a cero); los 15 huecos de ≥ 256 B a cero están en `.rodata` dentro de tablas de caracteres con referencias alineadas. Se usa el **cuerpo de la función `0x2648d8`** (9 524 B, `.ARM.exidx` la delimita): sin ninguna referencia (ni `bl`/`b.w`/`blx` en `.text`, ni palabra alineada con su dirección|1 —vtables—, ni literal PC-relativo `ldr+add pc`), no exportada en `.dynsym`; el test la comprueba (palabras y `exidx`) y que los parches tocan solo los ganchos y `0x2648d8..+0x300`. Ocupa ~0x250 B. Los demás parches de `libObj` del CFW (g22 eco, G30) no tocan ninguna de estas direcciones. Riesgo: «sin referencias» es criterio negativo (misma salvedad que g56 §2).

## 5. Pruebas
- Bytes originales de los 5 ganchos, `apply_bytes` determinista, rechaza una imagen ya parcheada; destino de los `b.w` verificado con Capstone (Keystone codifica el `b.w` absoluto con +2: se resta 2 al ensamblar).
- Unicorn sobre `libObj` real (Backup de `0xdd5f4` simulado; las llamadas ajenas se anotan y omiten): arranque (contador con basura → 0) y 12 eventos `0x9502/0xf000` desde `0x66df10`.
  - Off (e imagen original): espera 10 000 en las tres copias, 12 rearmes, estado 1 (de fábrica).
  - 5 s y N = 10 (modo 0): espera **5 000** en las tres copias; rearmes `[1]*9 + [0]*3`: la décima toma sale por `0x66deae` (llama a `0x67da50`, estado 0, `REPEAT` 0, contador 0) y los eventos 11–12 ya no rearman; el rearme conserva `obj`, `+0x268`, `0x5c`, `+0x1a0`.
  - Sin tope: 12 rearmes, contador 12; 5 min: 300 000; modo 2: 0; `REPEAT` = 0: fábrica; byte fuera de tabla: Off.
- **Arnés** (overlay y perfil propios `g61`, puerto 8761, con `cfw_ajustes.construir` + `libObj` parcheado; sin tocar `scripts/gui/harness/`): Ajustes **verificados** (perfil `g61`, puerto 8761, overlay con `libObj` parcheado; qemu parado y perfil borrado): Ajustes personalizados p. 4 → «CFW» muestra los seis ajustes (`img/g61-carpeta-cfw-seis-ajustes.png`); «Intervalo» ofrece Off/2 s/5 s/10 s/30 s/60 s… con desplazamiento (`img/g61-intervalo-lista.png`); tras elegir 5 s y «N. disparos» = 30 (`img/g61-intervalo-5s-n30-guardados.png`) el `nvram.json` queda con `"1070214": "02"` y `"1070215": "01"` (índices). Sin `SIGSEGV`. **No se disparó con el autodisparador continuo**: el arnés no tiene la ruta de menú de Drive (g60 §4) ni un disparo que genere `0x9502`; no hay cuenta de tomas en traza (INTERVAL-F2 abierto en esa parte).

## 6. Focus Bracket: documentado, no implementado
Hace falta enviar desde `libObj` el mensaje `0x765a` (→ `SequenceBracketAF` → `0x3027` a `lc_BracketAF`, g57 §6) con `jobId` y paso s8. Su emisor `0x6543e4` es un método de `ModelScalarCameraPatch` (usa `this`: `0x132374`, `0x65411c`) y el objeto del autodisparador no tiene referencia a él; reproducir el envío a mano (`0xde4cc/0xdf454/0xe1668/0xe16b4/0xde4d8`, como `0x67b4b0` hace con `0x750a`) es posible pero sin objeto receptor verificado; y la cueva no puede **esperar** a que el motor pare (`0x43adcc22` es de `av-cam`): `lc_BracketAF` contesta con otro `0x9502/0xf000` que el autodisparador confundiría con el fin de toma. Los ajustes «Focus Bracket»/«Focus Br. paso» (g57) siguen en el menú sin consumidor en este modo. Pendiente `FOCUSSHIFT-HOOK`.

## 7. Límites
- **Sin cámara**: la espera, el contador y el aviso final (`0x753f` con `0xffff0003`, el mismo que la salida de error con `REPEAT = 0`; la UI puede mostrarlo como cancelación) no están medidos; el estado se restablece a los valores por defecto (modo 2: Drive vuelve a disparo único).
- «Intervalo» se lee al fijar el modo (las tres copias) y «N. disparos» en cada toma: cambiar «Intervalo» con el Drive ya elegido no surte efecto hasta volver a elegirlo.
- Si la lectura de Backup falla: «Intervalo» = Off (fábrica) y «N. disparos» = 10.
- El contador vive en cola de página del `.bss` (si el cargador mapeara solo hasta el fin exacto del `.bss`, escribiría fuera: sin medir en cámara; páginas de 4 KiB o más lo cubren).
- La espera entre tomas es retardo + tiempo de captura, como de fábrica.
