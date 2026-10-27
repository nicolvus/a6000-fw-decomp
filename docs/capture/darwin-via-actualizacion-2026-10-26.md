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
