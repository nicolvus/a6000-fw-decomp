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
