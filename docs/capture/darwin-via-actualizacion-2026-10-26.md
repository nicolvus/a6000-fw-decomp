# Vía de parcheo de Darwin por actualización oficial — 26-10-2026

Motivo: el obturador mecánico en tipo 2 se atribuye a que el Darwin de la A6000 descarta `pkt[+0x12]` bit 5 (S53). ¿Se puede cambiar Darwin sin abrir la cámara?

## Hallazgos (VERIFICADO por ficheros del repo)
- La imagen de Darwin **sí está disponible**: `firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin` (157 276 B; A6300 2.01 y A7S 3.20 también). Es la que ya se analizó (S53).
- El updater (`nflasha1`, volcado `nand-20261020`) contiene `ud_darwin_firmup.elf`, `ud_darwin_init.elf`, `ud_darwin_reboot.elf`, `us_darwin_firm.sh`, `us_darwin_init.sh`.
- `udtrbody.bin_unpacked/config/config.xml` (en `nflasha15`): para `darwin_sum/darwin.sum` ejecuta `us_crc32sum.sh darwin file` y luego `us_darwin_firm.sh darwin` (en hilo). `darwin.sum` = `0,9ff7148c,0002665c,…,darwin_core.bin` (solo CRC-32 y tamaño).
- Por tanto, una actualización oficial reescribe el MCU Darwin, y la integridad que comprueba el updater es CRC-32, no firma (coherente con `custom-fw-recovery-and-install.md`: FDAT cifrado, no firmado).

## Qué implicaría un parche (INFERENCIA / NO_VERIFICADO)
1. Modificar `darwin_core.bin` (p. ej. portar de la A7S la lectura de `S+0xd0` b5 y la puerta `no_silent` en `0x20cb2/0x20d00`), recalcular `darwin.sum` y reempaquetar FDAT con versión ≠ instalada.
2. Instalar con `pmca-console firmware`. NO VERIFICADO: que el MCU o `ud_darwin_firmup` validen algo más que el CRC; que la cámara acepte un FDAT propio de extremo a extremo.
3. Además hace falta que el firmware principal produzca el paquete Silent (S53: LIRO A6000 no fija bit `0x20`, modo 2 ni clase 0): el parche de Darwin solo no basta.
4. Riesgo: un Darwin defectuoso (controla bobinas/cortinas, ADC) puede dejar la cámara sin disparar y sin recuperación por software; la recuperación por USB depende de que el updater (`nflasha1`) siga intacto y de que `ud_darwin_firmup` pueda reflashear. Va contra la regla vigente «sin flasheo».

## Corrección
Frases previas del tipo «no hay volcado de Darwin» se refieren a la **lectura en vivo** del MCU (P6, negativa), no a su firmware: la imagen oficial existe y está analizada.

## Revisión del parche preparado (sin instalar)
Artefactos en `analysis/darwin-patch/` (el `.bin` no se versiona: deriva de firmware de Sony).

| Punto | Resultado | Estado |
|---|---|---|
| CRC-32 original de `darwin_core.bin` = `9ff7148c` = el de `darwin.sum` | coincide; el cálculo local reproduce la suma del updater | VERIFICADO |
| Parche | `0x20c78..0x20c7f` = `b 0x20c8e` + 3 `nop`; `0x20c74` devuelve siempre 0 (7 bytes distintos de 8 tocados; mismo tamaño) | VERIFICADO (desensamblado del resultado) |
| Efecto buscado | tipo de mecanismo 0 ⇒ `0x20cb2/0x20cd4/0x20c90` omiten las bobinas P4D/P4E (rama sin bobinas ya presente) | VERIFICADO estáticamente; efecto físico NO VERIFICADO |
| CRC-32 del parcheado | `0e2620b4` (`darwin.sum.tipo0`) | calculado |
| Alcance | **global**: ninguna bobina se acciona en ningún modo (también rearme y vídeo), no solo con Silent (S53 §«alternativa tipo 0») | VERIFICADO estático |
| Fin de la exposición | sin cortinas, la exposición solo la termina el sensor; el fin electrónico del IMX210 en foto completa NO está demostrado (S51/S52). Riesgo de imágenes sobreexpuestas o sin lectura válida | NO VERIFICADO |
| Rearme tras tipo 0 | S54 H54-5: «tipo 0 ≠ en reposición»; el rearme podría quedar mal | NO VERIFICADO |
| ¿Valida algo más el MCU/`ud_darwin_firmup`? | desconocido (`ud_darwin_firmup.elf` no desensamblado) | NO VERIFICADO |
| FDAT propio | NO generado; el empaquetado de extremo a extremo (212 MB) nunca se ejecutó y no hay prueba de que la cámara acepte una `nflasha*`/`0640_darwin` modificada | NO VERIFICADO |

## Alternativa sin flasheo (a investigar antes que nada)
El tipo de mecanismo de Darwin es el byte `0x20000050+ch`, que el firmware principal le envía por CAIF (categoría `0x2d`, entrada 33, S54); el escritor/emisor del valor no está localizado. Si la cámara lo envía en cada arranque o disparo, sería posible forzar el tipo 0 con un parche **en RAM** de `av-cam` (reversible, como T020) en lugar de reflashear Darwin. Falta localizar ese emisor en `av-cam`.

## Recomendación
No instalar. El parche tipo 0 es probablemente el experimento Darwin más pequeño que existe, pero apaga las bobinas en todos los modos y no resuelve el fin de exposición del sensor. Primero localizar el emisor del tipo de mecanismo (vía RAM, sin flash); solo si no hay vía RAM y el usuario lo autoriza expresamente, evaluar el FDAT.

## Búsqueda del emisor del tipo de mecanismo (segunda sesión, 26-10-2026) — NO LOCALIZADO
Objetivo: saber si `av-cam` envía a Darwin el byte `[0x20000050+ch]` (tipo de mecanismo) para forzarlo por RAM. Resultado: **emisor no hallado**; lo establecido:

| Hecho | Estado |
|---|---|
| Tabla de manejadores CAIF categoría `0x2d` en `0x2a1a0`: 8 B por entrada `(cabecera 0x2d000N, manejador)`; entrada 33 (`0x2a2a8`) = `0x1b0b3` (valida el canal). Otros manejadores no nulos: ids 0 `0xd4b9`, 1 `0xd97d`, 14 `0x1bd7b`, 15 `0x1cd7b`, 16 `0xd92b`, 17 `0x1b167`, 31 `0x1cd97` | VERIFICADO |
| La carga inicial de RAM de Darwin (tabla de arranque `0x2a744`) solo cubre `0x20002a00..` (descompresión `0x4d0` B) y `0x20002ed0..` (cero, `0xf8c` B). La región `0x20000000..0x20002a00` (incluye `+0x50`) **no** se inicializa desde la ROM: la rellena el firmware en ejecución (mensajes o copias) | VERIFICADO |
| En Darwin no hay formación de puntero `base+0x50` ni literal `0x20000050` (reconfirmado) | VERIFICADO (cobertura de literales/`add #0x50`) |
| En `av-cam`, la tabla `{cmd,size,texto}` de 51 entradas está en `0x43fe8730..`; `0x0400018a` = `Sens:AdjCmd DwnCamera` (12 B), `0x0400018c` = `DwnCamera Done`. Ninguna constante `0x0400018a/18c/188/189/180` aparece en código ni en pools (fuera de la propia tabla): son identificadores de la herramienta de ajuste (S143: utilidad de calibración del sensor, no de obturador) | VERIFICADO |
| Referencias a las cadenas `Sens:*` por pools PIC y por GOT (225 bases probadas, formas `ldr pc`/`ldr.w imm12`): ninguna coincidencia fiable | NEGATIVO con cobertura limitada |

Conclusión: el valor llega a Darwin por un camino no identificado (probablemente un bloque copiado por mensaje desde el firmware principal). **No se puede afirmar que exista una vía de RAM** ni que no exista. Sigue abierto: (a) cartografiar con REA los emisores CAIF hacia Darwin (categoría `0x2d`); (b) verificar `sio3/sio4` como enlace Linux↔Darwin; (c) solo entonces, el FDAT.

## Mensajes BIONZ→Darwin: emisores localizados (tercera sesión, 26-10-2026)
Sin REA (el demonio de `av-cam.bin` se abrió y se cerró: el resto era vtable/Thumb a mano); con barrido de bytes + capstone.

**Darwin, tabla mss-async `0x27c68`** (16 B por ID desde `0x0b`: `{tx, rx, longitud, código}`; VERIFICADO). Mensajes con buffer de recepción (BIONZ→Darwin), código `03 NN 02`:
| ID | NN | Longitud | Nota |
|---|---|---|---|
| `0x0c` | 1 | 22 B | paquete CAIF ev1 de captura (ya conocido) |
| `0x0f` | 4 | 2 B | |
| `0x12` | 7 | 4 B | |
| `0x13` | 8 | 10 B | |
| `0x16` | 0x0b | **210 B** | bloque de parámetros grande |

**av-cam**: el despachador `0x437db85e(evento, payload)` (tabla `tbb` en `0x437db89e`, 14 eventos) envía cada mensaje. Evento 1 → `0x436b8a50(payload+0x40)`: copia 22 B a `0x43f91e32` (cabecera `03 01`). **Evento 11 → `0x436b8a70(payload+0x56)`: copia 0xd2 B a `0x43f91e48` y la cabecera `{03, 0x0b, len 0xd2}` va en `0x436b88ac` → `0x436ba234`** (VERIFICADO por bytes; coincide con ID `0x16` de Darwin). Otros eventos usan `0x43acab4a..62`, `0x436b8b8c` (payload+0x12a) y `0x436b8ba8` (+0x12e).
El evento 11 lo emite `0x438d079c`: rellena `obj+0x56` (210 B) con `0x43af0b64`/`0x43af0b70` (envoltorios de métodos virtuales `0x43b0f5c2/…/0x43b0f678` a partir de `capture+0x3388` y `capture+0x20`) y lo envía.

**Hipótesis (INFERENCIA, no demostrada):** el bloque de 210 B es el único mensaje BIONZ→Darwin lo bastante grande para llevar los 24 bytes de tipo de mecanismo (`[0x20000050+ch]`). Lo que falta es (a) ver su contenido real y (b) hallar en Darwin el consumidor del ID `0x16` (no es el buffer `0x200032cc` del camino 0x21/0x31/0x41 de `0x11fac`).

**Prueba pendiente (solo lectura, sin riesgo):** leer en la cámara `0x83f91e48` (0xd2 B) y comprobar si hay 24 bytes con valores 0–3 y qué canal es el mecánico. Intentada: la cámara no respondía (`No route to host`). Si el bloque contiene el tipo, la ruta por RAM sería parchear **en `av-cam`** el campo antes del envío (reversible, como T020).

## Lectura en la cámara (T022, solo lectura) — el bloque de 210 B NO lleva el tipo de mecanismo
- Direcciones reales confirmadas: el paquete CAIF ev1 de 22 B está en `0x83f91e32` (físico) y contiene tras el disparo `00 02 00 16 bd 13 00 00 00 00 53 0e 00 40 00 00 00 00 00 90 00 00`: clase `+1`=2, `+0d`=`0x40`, **`+0x12`=0 (sin bit `0x20`)**. VERIFICADO en vivo (coincide con la inferencia de S53: la A6000 no produce el bit Silent).
- El bloque de 210 B (`0x83f91e48..0x83f91f1b`) está **entero a cero**, antes y después de un disparo.
- Razonamiento: si el bloque se hubiera enviado con el tipo de mecanismo, el tipo valdría 0 y Darwin no accionaría las bobinas (`0x20c74`→0), pero el obturador mecánico funciona. Si no se envía, el tipo llega por otra vía. En ambos casos **el ID `0x16` no es el portador del tipo de mecanismo** (supone que el buffer estático no se limpia tras el envío, como ocurre con el de 22 B).
- Queda: el tipo probablemente no viaja desde el firmware principal, sino que Darwin lo toma de su propia configuración (la ruta «DD»/MFS3 de S53, o constante de fábrica). **Eso elimina la vía de RAM en `av-cam` para forzar el tipo 0.** Solo quedaría el parche del propio Darwin (FDAT), que sigue sin autorizar.
