# S53 — Conclusiones (19-10-2026)

Fase cerrada con el **criterio de finalización 1 y 2**: parser CAIF localizado y comparado funcionalmente; incompatibilidad
concreta y reproducible en Darwin A6000. Prueba: `python3 -m unittest tests.test_s53_darwin_caif` (10/10; suite 42/42).

## Hallazgos (VERIFICADO salvo indicación)

1. Darwin = FM3 MB9AF004BGL, Cortex-M3, base `0x4200` (A7S confirmada). IRQ por un único manejador + tabla ROM `0x4300`.
2. Enlace BIONZ X (IC6000) ↔ Darwin: MFS5 CSIO en P36–P38 (`MSS_*_DWN`, esquema A6000), protocolos «mss-sync» (128 B)
   y «mss-async» (tabla de IDs).
3. El paquete CAIF ev1 de 22 B llega como mensaje mss-async **ID `0x0c`** (código `03 01`, 22 B) en ambas ROM
   (identidad con op `0x10300`: INFERENCIA fuerte). Offsets 1:1 con el constructor LIRO.
4. **Parser:** A7S `0x18396`, A6000 `0x17f8c`. Idénticos salvo que A7S guarda `pkt[+0x12]&0x20` en `S+0xd0.b5` y fuerza
   clase 2. A6300 (con Silent) tiene la misma inserción. A6000 la descarta.
5. **A7S:** predicado `no_silent` (`0x19a86`, `0x216c2`) que impide escribir P4D/P4E (`1ST/2ND_CURTAIN_MG` en el
   esquema A6000; A7S por inferencia), toma la rama de exposición «sin mecanismo» (solo temporización + P4C) y omite el
   seguimiento de posición ADC. **Esta es la rama Silent física del MCU.**
6. **A6000:** mismas funciones sin argumento: bobinas siempre accionadas (si tipo de mecanismo 1/2/3).
7. Modo 2 de `pkt[+0x0d]`: sin consumidor de los bits 6-7 en ninguna ROM (búsqueda negativa, PARCIAL).

## Límites

- Polaridad física de P4D/P4E y estado de reposo de las cortinas: NO VERIFICADO.
- Pines A7S: inferidos (sin esquema A7S).
- No se buscó en Darwin el receptor del mensaje tipo 3/`0x22` (C1) ni de las respuestas CAIF3.
- Búsquedas negativas limitadas al pseudocódigo Ghidra (2002/2055 funciones sembradas) y a barridos capstone.
- Sin cámara, sin ejecución, sin emulación.

## Decisión

**S51 se mantiene** (no parchear). Escenario B: falta lógica de firmware en Darwin A6000, además de LIRO e IMX210.
Ver [viabilidad](s53-a6000-silent-feasibility.md).

## Próximos experimentos (no iniciados)

1. Pasivo y autorizado: traza lógica de `MSS_SO_DWN` y de `1ST/2ND_CURTAIN_MG` en una A6000 para confirmar ID `0x0c` y
   polaridad (sin escribir nada).
2. Estático: seguir `P4C`/`CA_1ST_CURTAIN_START` en LIRO A6000 (consumidor de la señal de inicio de exposición).
3. Estático: efecto global del tipo de mecanismo 0 (`0x1b080(0)&7`, byte `0x20000000+0x50`) y su origen.
4. IMX210 solo con datasheet o traza pasiva de la interfaz serie del sensor (S51).
