# S54-D — IMX210: exposición electrónica (20-10-2026)

**Sin evidencia nueva sobre el sensor en S54.** Se aplicó el criterio del encargo (§7: iniciar D tras llegar a la frontera estática de P4C y tipo 0): ambas líneas
cerraron en frontera (ver [P4C](s54-p4c-signal-trace.md), [BIONZ](s54-bionz-darwin-sync.md), [tipo 0](s54-mechanism-type-zero.md)). Esta sección consolida
lo ya demostrado (S50–S52) y lo que S54 añade para el sensor.

## Lo que S54 aporta al tema del sensor

1. **Darwin no depende del sensor:** la rama «sin mecanismo» (tipo 0 / Silent A7S) solo usa temporización propia + P4C←0. Cualquier fin electrónico de integración
   tendría que originarse en BIONZ/IMX210; Darwin ya no es obstáculo para la parte mecánica (VERIFICADO a nivel de código, no físico).
2. **P4C llega a pines de BIONZ (`SENS_B`, `GPIO_9`)** (esquema): hay un canal físico Darwin→BIONZ además del enlace MSS. Si BIONZ lo usa para sincronizar el barrido
   del IMX210 es NO VERIFICADO (H54-3).
3. Las primitivas GPIO de BIONZ están localizadas (`0x43b5e2bc/22e/29a`); no hay `gpio_set` con pines de sensor identificados.

## Estado heredado (sin cambios)

| Punto | Estado | Fuente |
|---|---|---|
| ShutMode 0 de IMX210 existe (`0x436d6f6c`, rama `0x70d0`, campo `0x4401ca2e` b2=0,b7=0,b6=1,b4=0) | VERIFICADO (RAM de configuración) | S52 |
| Efecto eléctrico de esos bits | NO VERIFICADO (sin datasheet; serialización al bus no recuperada) | S52 |
| Modos de lectura completa `0x0b`, `0x2f` (6000×4000) | VERIFICADO (tabla); compatibilidad con Silent NO demostrada | `imx210-video-readout.md` |
| IMX235 modos `0x4e/0x4f` ausentes en IMX210 | VERIFICADO | S52 |
| Inicio/fin electrónico de exposición fotográfica completa | **NO VERIFICADO** | — |

## Frontera exacta

Cerrar H54-7 exige una de dos cosas que la ROM no da: (a) datasheet/mapa de registros del IMX210 o del DFE CXD90027 (frontera B5), o (b) traza pasiva
de la interfaz serie del sensor durante una captura (S51). No se copiaron tablas entre sensores. **H54-7: NO VERIFICADO.**
