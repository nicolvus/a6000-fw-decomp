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

## Qué valida `ud_darwin_firmup.elf` (cuarta sesión, 26-10-2026, solo análisis)
Fuente: `nand-20261020/dev_nflasha1.bin` (FAT) → `boot/initrd.img` (cramfs) → `usr/bin/ud_darwin_firmup.elf` (8156 B, ARM Thumb, sin símbolos), desensamblado con `llvm-objdump`. `us_darwin_firm.sh` lo llama como `ud_darwin_firmup.elf darwin_boo.bin darwin_core.bin`; resultado ≠ 0 ⇒ «NG» y LED `0x63`.

| Hecho | Estado |
|---|---|
| Versión: `0x8a48` busca en el fichero la cadena ASCII `VER` seguida de `M.mm` (dígitos, ≤255 cada uno) → `u16 (M<<8)|mm`; devuelve 1 OK, 2 «not found», 3 «invalid». «Invalid» = formato de la cadena, **no** firma ni suma. `darwin_core.bin` fw321 lleva `VER0.78` en `0x2193c` (fuera de los bytes parcheados) | VERIFICADO |
| El paquete fw321 **no trae `darwin_boo.bin`**: `open` falla ⇒ versión boo = 0 ⇒ la condición «Core Firm-Up is not needed» (`0x9080`: exige boo ≠ 0, boo nueva = antigua y core igual) nunca se cumple: **el core se reescribe siempre**, sin depender de su versión | VERIFICADO |
| Transporte: SIO (`/dev/sio…`, `ioctl` de baudios) + GPIO CS (`UdtrGpio*`); trama con CRC-16-CCITT (`0x8b28`: semilla `0xffff`, polinomio `0x1021`, 0x7e B) y comprobación de `com_id`/`dwn_stat` en las respuestas. Integridad **del enlace**, no del contenido | VERIFICADO |
| No hay en el updater cálculo de suma ni firma sobre la imagen completa; la única suma de la imagen es el CRC-32 de `darwin.sum` (ya recalculado: `0e2620b4`) | VERIFICADO (código del ELF completo, 0x958 B de `.text`) |
| Que el **bootloader del propio MCU** (no incluido en el paquete) verifique la imagen antes de arrancarla | NO VERIFICADO (no hay binario que analizar) |

Consecuencia: del lado Linux el parche tipo 0 cumple todo lo que se comprueba (CRC-32 recalculado, cadena `VER` intacta). Lo que sigue sin probar: el bootloader del MCU, que la cámara acepte un FDAT reempaquetado y el efecto físico (fin de exposición sin cortinas, rearme). Matiz a T022: lo que descarta es el bloque ID `0x16` como portador del tipo; los mensajes `0x0f/0x12/0x13` no se leyeron, así que «sin vía RAM» es inferencia, no prueba.

## Buffers BIONZ→Darwin restantes (T023, solo lectura, 26-10-2026)
Emisores en `av-cam` (VERIFICADO por bytes, base de carga `0x43541000`; físico = virtual + `0x40000000`): las cabeceras `{03, NN, len}` se arman en `0x436b88e8` (`03 07`, 4 B, buffer `0x43f91e2e`, copia `0x436b8b8c`), `0x436b8aec` (`03 04`, 2 B, buffer `0x43f91f24`, **escrito a cero por el propio código antes de cada envío**) y `0x436b8864` (`03 08`, 10 B, buffer `0x43f91f1a`, copia `0x436b8ba8`), y coinciden con los IDs `0x12`, `0x0f` y `0x13` de la tabla de Darwin. Son los cinco únicos llamadores de `0x436ba234` en `0x43600000..0x43c00000`.

Lectura en la cámara: **los tres buffers están a cero** en reposo y tras dos disparos remotos; el paquete ev1 de 22 B (control) se lee igual que en T022.

Conclusión (INFERENCIA con evidencia fuerte): ninguno de los cinco mensajes BIONZ→Darwin lleva un tipo de mecanismo no nulo (si lo llevaran a 0, Darwin no movería las bobinas, y sí las mueve). El tipo lo fija Darwin por su cuenta. Límites: muestreo después del envío (supone que los buffers no se limpian, como el de 22 B), y no cubre otros canales hacia Darwin fuera de `0x436ba234`. **La vía por RAM en `av-cam` queda descartada en la práctica; solo queda el parche de Darwin (FDAT).**

## FDAT tipo 0 generado y verificado (sin instalar, 26-10-2026)
Script `scripts/darwin_fdat_build.py`; salida en `analysis/darwin-patch/fdat/` (ignorada por git: deriva de firmware de Sony).

| Paso / comprobación | Resultado | Estado |
|---|---|---|
| Control del empaquetador: `fwtool pack` con `firmware.tar` + `updater.img` + `config.yaml` originales | reproduce `firmware.fdat` oficial **byte a byte** (SHA-256 `603b42ec…`) | VERIFICADO |
| `firmware.tar` modificado: parche en sitio de los datos de `0640_darwin/darwin_core.bin` y `0641_darwin_sum/darwin.sum` (mismos tamaños) | solo cambian 15 B: 7 en `0x915a78..7f` (= Darwin `0x20c78`) y 8 del CRC (`9ff7148c`→`0e2620b4`); cabeceras tar, orden y tamaño (212 011 520 B) intactos | VERIFICADO |
| Versión del FDAT | `3.22` (el updater rechaza 3.21 sobre 3.21, «Invalid version», 20-10) | elegido |
| FDAT generado | `firmware_packed.fdat` 212 155 392 B, SHA-256 `ddc2d5db41cfd049…`; también `firmware_packed.dat` (contenedor completo, `c19a1463…`). Reproducible: dos ejecuciones dan el mismo hash | VERIFICADO |
| Descifrado con `fwtool unpack` del `.fdat` y del `.dat` | sin errores (fwtool comprueba magia, CRC-32 de cabecera y suma de 16 bits + bandera de último bloque en cada bloque); `firmware.tar` descifrado = el modificado, `updater.img` = el oficial, `darwin_core.bin` = `darwin_core_tipo0.bin`, `darwin.sum` con `0e2620b4`; config: modelo `0x41030035`, región 0, versión 3.22, cripto `CXD90014` | VERIFICADO |

No verificado: que la cámara acepte el FDAT (el descifrado de `fwtool` usa las mismas claves que el updater, pero la cámara puede comprobar más), el bootloader del MCU, y el efecto físico. **No se ha instalado nada.**

## Instalación (T024, 26-10-2026) — autorizada expresamente por el usuario
- Antes: backup NVRAM `analysis/camera-dumps/20261026-232912-pre-T024-darwin-tipo0/` y FDAT de **recuperación** = paquete oficial 3.21 reempaquetado como **3.23** (`analysis/darwin-patch/fdat/recuperacion-323/`, ignorado por git; descifrado: `firmware.tar` y `updater.img` idénticos a los oficiales). El guard solo acepta versiones mayores que la instalada, así que la vuelta al Darwin oficial exige ≥3.23.
- `pmca-console firmware -f firmware_packed.dat`: 3.21 → 3.22, escritura 100 %, `Done`; la cámara reinicia y `pmca info` da 3.22. **La cámara acepta un FDAT propio con `darwin_core.bin` modificado y lo arranca** (VERIFICADO). El bootloader del MCU no lo rechazó (VERIFICADO de hecho, sin conocer su lógica).
- Comportamiento (observación del usuario): live view normal; al disparar la cortina cierra y reabre «extremadamente rápido» (INFERENCIA: sin imanes, las cortinas no quedan retenidas y corren en cuanto el motor las suelta); fotos de exposición normal en las tomas mostradas. A 1 s con «RR exp. larga» activa, imagen casi negra con bordes desplazados: la resta del fotograma oscuro, que sin cortina capta también la escena; **con RR desactivada sale normal** (VERIFICADO por el usuario).
- Sin verificar: EXIF de los originales (velocidad/ISO de cada toma), que la exposición la termine el sensor a velocidades rápidas (rodadura, bandas con luz artificial), rearme, vídeo y desgaste mecánico de las cortinas sin retención.
- EXIF de los originales (T024, `analysis/camera-dumps/20261026-T024-darwin-tipo0/fotos/`, no versionado): tras el flasheo, con la misma escena, la luminancia media crece con el tiempo fijado (1/15 → 167, 1/8 → 199; 1/4 → 120, 1/2 → 164, 0,7 s → 183). **La duración de la exposición sigue controlada sin cortinas retenidas** ⇒ la termina el sensor (INFERENCIA fuerte; cubre 1/60–1 s, no velocidades rápidas ni deformación por rodadura).

## Barrido de velocidades (T025, 26-10-2026)
Con la app y escena fija (M, f/3,5, ISO 640, RR larga apagada): luminancia media **plana de 1/4000 a 1/250 (≈63)** y creciente después (1/125 → 69, 1/60 → 80, 1/30 → 97, 1/15 → 120). El suelo de exposición es mayor en la parte baja de la imagen (≈5 ms arriba frente a ≈35 ms abajo, ajuste aproximado). INFERENCIA fuerte: con tipo 0 el inicio de la exposición sigue controlado, pero el **final lo marca la lectura progresiva del sensor** (≈30 ms), no el tiempo fijado. Corrige la lectura de T024: «la exposición escala con la velocidad» solo vale por encima de ≈1/60; **el parche tipo 0 no da un obturador electrónico utilizable a velocidades rápidas**. Para eso haría falta que el firmware principal programe también el reinicio progresivo del sensor alineado con la lectura (lo que hace el modo Silent de la A7S), que la A6000 no tiene (S53, E1).

## Tipo 2 forzado en RAM con Darwin tipo 0 (T026, 26-10-2026)
Con el selector forzado a tipo 2 (`G+0x784`=2, parche de T020) y control sin parche inmediatamente después, el barrido 1/4000–1/15 da la misma luminancia (dentro de ±3 % salvo 1/60 y 1/15) y el mismo suelo plano de 1/4000 a 1/500. **La ruta tipo 2 del firmware principal no programa un final electrónico de la exposición** (VERIFICADO en estas condiciones: modo M, f/3,5, ISO 640, RR apagada). Queda como única vía la programación directa del barrido de reinicio del IMX210, bloqueada sin hoja de datos (D5).

## EFCS activada frente a desactivada (T027, 27-10-2026)
Mismo suelo de exposición y mismo perfil por franjas con la EFCS activada y desactivada (diferencias ≤ 8 de luminancia media, EFCS off algo más clara a velocidades rápidas). Con tipo 0 el ajuste EFCS no cambia el inicio de la exposición de forma medible: no permite atribuirlo al reinicio electrónico del EFCS ni a la cortina sin retención. La idea de reaprovechar los tiempos del EFCS (retrasar el reinicio y ajustar su ritmo al de la lectura) sigue siendo hipótesis, sin evidencia a favor.

## Siguiente palanca: forzar ShutMode del IMX210 (estático, 27-10-2026)
Antecedentes (S52/S56, vigentes): el `SetExposure` del IMX210 (`0x436d6f6c`, vtable `0x43fcc090+0x28`) lee el modo de obturación en `0x436d6fb6 ldrb.w r9,[r1,#9]` (`param+9`) y despacha con `tbb` los ShutMode 0–4 (`0x436d70be`). La A7S programa su modo Silent con **ShutMode 0** (clase 0 → `param+9`); la A6000 tiene la rama 0 (y la 4, con la misma función de temporización `0x436d6f50`) pero su política normal no la usa (S52: «ninguna ruta normal la alimenta»). Hasta ahora no se podía probar: con cortinas activas el resultado quedaba enmascarado.
- Bytes verificados en `av-cam.bin` (Capstone): `0x436d6fb6` = `91 f8 09 90` (`ldrb.w r9,[r1,#9]`). Parche en RAM propuesto (físico `0x836d6fb6`): `4f f0 00 09` (`mov.w r9,#0`) o `4f f0 04 09` (`mov.w r9,#4`). Mismo tamaño; reversible.
- Alcance: afecta a **toda** llamada a `SetExposure` mientras esté activo (también vista en directo); por eso se aplica solo durante el barrido y se revierte.
- Prueba propuesta (T028): barrido 1/4000–1/15 con ShutMode 0, con ShutMode 4 y control. Si el brillo baja de forma proporcional de 1/250 a 1/4000, el IMX210 sí termina la exposición electrónicamente con ese ShutMode.
`scripts/camera_tipo2_sweep.py` admite ahora otros parches por `RAMPATCH=DIR:ORIG:NUEVO`.

## ShutMode 0/4 forzado en RAM (T028, 27-10-2026) — primer cambio real del sensor
Barridos con ShutMode 0, control y ShutMode 4 (Darwin tipo 0). Control: suelo plano de 1/4000 a 1/250 (≈76) y subida desde 1/125 (como T025–T027). **ShutMode 0 y 4: ≈93–96 de 1/4000 a 1/30, solo sube a 1/15; perfil por franjas distinto** (más luz arriba a velocidades rápidas; la parte baja pierde luz al alargar el tiempo). Ambos modos dan casi lo mismo, coherente con que comparten la función de temporización `0x436d6f50`.
- VERIFICADO: forzar `param+9` cambia la integración del sensor en foto completa ⇒ **el reinicio electrónico del IMX210 es programable desde el firmware principal** y la rama ShutMode 0/4 (la que usa la A7S en Silent) actúa sobre él.
- INFERENCIA: los tiempos de la rama 0/4 se calculan con parámetros que no encajan con la lectura completa (exposición casi fija ~1/60 e invertida en la parte baja). Siguiente paso estático: emular `0x436d6f50` frente a la rama 1/3 (`0x436d6f34`/`0x4355faf0`) para varios tiempos de exposición con el arnés S52 y ver qué campos (SHR y similares en `0x4401c67a…0x4401c812`) cambian; después ajustar esos valores con otro parche en RAM.

## Qué hace realmente ShutMode en `SetExposure` IMX210 (estático + lectura en vivo, 27-10-2026)
Desensamblado completo de `0x436d6f6c..0x436d7292` (Capstone sobre `av-cam.bin`):
- Prólogo común a **todos** los ShutMode: `r5=param+0`, `r6=param+4`, `r7=param+6` (u16) se reparten en bytes/nibbles a seis campos de registro (`+2` de cada estructura sombra): son los tiempos del sensor (SHR y similares, S52). **No dependen del ShutMode.**
- El `tbb` solo cambia (a) 4 bits del campo ID1 (b2/b7/b4/b6, tabla S52) y (b) la espera `[obj+0x3a0]` (ms), que S56 asocia al mensaje a Darwin `0x107`:
  - modo 1: `(tabla1[obj+0x17c].w4 >> 8) · param+0 / 1000 + 1` (`0x436d6f34`, entradas de 0x30 B);
  - modo 2: igual que 1 + `(param+0x14+1)·0x26aa >> 16`, y copia `param+8/+0x14` a dos registros;
  - modo 3: `param+0x10 / 1000 + 1` (`0x4355faf0` = división);
  - modos 0 y 4: `(tabla2[obj+0x17c].h0 >> 8) + 1` (`0x436d6f50`, entradas de 0xc B) ⇒ **constante por modo de lectura, independiente del tiempo de exposición**.
- Por tanto T028 se explica (INFERENCIA fuerte) por la espera constante de los modos 0/4, no por un cambio en los tiempos del sensor: con tipo 0, la exposición efectiva ≈ espera hasta la lectura + barrido de lectura.
- Objeto `C_ImagerCtrl_IMX210`: **única instancia en físico `0x83e7f4a8`** (vtable `0x43fcc090`; volcado del 20-10 y RAM viva hoy). En reposo `+0x170=0x11` (ruta de salida temprana). Muestreo durante disparos (`scripts/camera_imx210_obj.py` y muestreo en bucle): `+0x3a0` toma **4** a 1/4000 y **58** a 1/15 en la ruta normal (escala con la velocidad), y 17 en reposo. El muestreo en bucle mezcló estados (lecturas no atómicas): valores orientativos, NO VERIFICADO el ShutMode normal.
- Siguiente prueba (en RAM, reversible): forzar ShutMode 1 y 3 para identificar cuál usa la captura normal, y el modo 3 con b2 borrado (`0x436d717c` `orr r2,#4` → `bic r2,#4`) para separar el efecto de los bits del de la espera.

## ShutMode real y bit 2 (T029–T031, 27-10-2026)
- **VERIFICADO en vivo (T031):** la vista en directo usa ShutMode 0 (ID1 `0x40`) y la foto normal ShutMode 3 (ID1 `0xd4`, con estados intermedios `0x48/0x44/0xdc`). Corrige la lectura de T029/T030: forzar 1 o 3 en `0x436d6fb6` alteraba también la vista en directo y atascaba la captura (T030 terminó tarde: `done 303051`); T028 (0/4) no la alteraba porque la vista en directo ya usa 0.
- Por tanto T028 = foto con los bits y la espera de la vista en directo: exposición casi constante (espera de tabla) con los mismos registros de tiempo.
- **Bit 2 borrado solo en la rama de foto (T031):** dispara, pero la imagen sale corrupta (lavada, magenta, rayas horizontales). b2 cambia el modo de funcionamiento o de lectura del sensor; sin hoja de datos no se puede saber qué otros registros habría que acompañar.
- Estado: las palancas de ShutMode están agotadas sin datos del sensor. Un obturador electrónico en foto completa exigiría cambiar los registros de tiempo (`param+0/+4/+6`) de la foto para que el reinicio recorra el sensor al ritmo de la lectura, como hace la vista en directo (ShutMode 0) a menor resolución; su semántica sigue sin hoja de datos (D5).

## Registro de exposición electrónica en la vista en directo (T033, 27-10-2026, solo lectura)
- **VERIFICADO en vivo:** en la vista en directo (ShutMode 0, ID1 `0x40`) solo r5 (`param+0`) sigue a la velocidad: 1240 a 1/4000, 1205 a 1/2000, 1059 a 1/1000, 691 a 1/500, 651 de 1/250 a 1/15, 2–3 a 1/8 y 1/4. r6/r7 quedan en 1.
- INFERENCIA: r5 es el registro de inicio del reinicio electrónico (exposición mayor ⇒ r5 menor). No es lineal con el tiempo en los puntos medidos y se satura en 651, así que la escala (líneas por segundo, longitud de cuadro) no está determinada; a 1/8 y 1/4 la vista en directo cambia probablemente de cadencia.
- Siguiente: comparar con el r5 de la propia foto (ShutMode 3) en un estado estable, y solo con autorización expresa, probar en la foto un r5 de la vista en directo.
- **T034 (RAM, un disparo):** forzar r5=1240 en la foto (ShutMode 3) no cambia la luminancia (121,8 → 119,9). La ruta parcheada sí se ejecuta (la vista en directo queda en 1240). INFERENCIA: en ShutMode 3 el sensor no usa r5 como inicio del reinicio electrónico; habría que combinarlo con el modo de la vista en directo (ShutMode 0, T028), lo que no se ha probado.
- **T035 (RAM, un disparo por variante):** ShutMode 0 + r5=1240 en la foto oscurece respecto de ShutMode 0 solo (143,7 → 121,7), con imagen completa y sin corrupción. El efecto se concentra en la mitad superior de la imagen. **Primera señal de exposición electrónica controlable en la foto completa**; falta barrer r5 para medir la relación con cada franja de filas.
- **T036 (barrido de r5 con ShutMode 0):** luminancia 143,5 (sin r5) → 138,5 (300) → 121,7 (1240) → 93,1 (2500); con 5000, 10000 y 16000 vuelve a 144 (sin efecto). La exposición de la foto completa es controlable por r5 en un rango < 5000, pero con degradado vertical (a 2500: 30 arriba, ≈110 abajo). Falta igualar el ritmo del reinicio con el de la lectura de la foto; candidatos: r6/r7 (`param+4/+6`) y la temporización de la rama ShutMode 0.
- **T039 (más puntos de r5 con ShutMode 0):** a 1/250 la luminancia baja de 151,8 a 4,8 al subir r5 hasta 4200, y con r5 ≥ 4300 vuelve a 152. Entre 4000 y 4200 la imagen es **corta y casi uniforme** (octavos de 5 a 3 en 4200), completa y sin rayas: **obturación electrónica de la foto completa con exposición corta, controlada por r5**. Límite entre 4200 y 4300. A 1/30 aparece una banda casi sin exposición cuya posición depende de r5, sin explicar. Falta: escala de tiempo (lineal en RAW o con referencia de luz), paso fino 4200–4300, comportamiento por velocidad y deformación con objetos en movimiento.
