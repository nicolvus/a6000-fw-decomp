# S58-E/F — Ciclo lógico y fronteras de integración

20-10-2026. Esta reconstrucción integra [productores AE](s58-ae-timing-producers.md), [emulación A7S](s58-imx235-full-emulation.md) y [diferencias](s58-a7s-silent-effective-diff.md). No es una cronología eléctrica medida.

## A6000

| Enlace | Evidencia | Estado |
|---|---|---|
| AE→Tv_i | entrada AEOUT3+0xfc al bucle 0x4383d704; escritor previo sin recuperar | PARCIAL |
| Tv_i→T→n_i/shd_i/fino_i→filas | 0x4382fa94, 0x4383d4d0, 0x4383c9dc; instrucciones y emulación por tramos | VERIFICADO aritmético |
| Filas→S→argumento | 0x43843a44, 0x43b0893c, 0x43849fb8; copia intermedia estática, selección y empaquetado emulados | PARCIAL de extremo a extremo |
| Argumento→sombra→SSB→Execute/P2S | S56/S57; ID1 bit3 y registros 3–8 | VERIFICADO en software |
| P2S→instante de aplicación del sensor | MMIO y handshake observados, periférico no modelado | NO VERIFICADO |
| Contador host→eventos Darwin | contador cap+0x4b9c hasta svd; serialización de parámetros S57 | VERIFICADO en rutas recuperadas |
| Evento/temporizador→fin físico de integración | ningún vínculo eléctrico recuperado | NO VERIFICADO |

No se ejecutó AE completo hasta el sensor con un contexto real. El bloque M, clk y Tv de un estado alcanzable son fronteras concretas; los ejemplos numéricos no las reemplazan.

## A7S Silent

Selección Silent y política de cortinas preceden a los métodos emulados: tipo 2→modos 0x4e/0x4f y clase 0; CAIF lleva el bit Silent a Darwin, que aplica la rama `no_silent`. Es evidencia histórica S52/S53, no ejecución nueva de ese sistema en S58. El índice muestra un conflicto de extracción sobre un enlace de S53; se conserva la evidencia concreta del parser, sin resolver ese conflicto mediante una inferencia nueva.

La parte ejecutada es `SetMode→SetExposure→SetRead→Execute→buffers P2S`, con stubs. Se observan diferencias de modo, parámetros de tiempos, bit 3, mensajes y una escritura a dispositivo 0x83. No se ejecutan el fin posterior, Darwin, IRQ, lectura de píxeles ni guardado.

## Eventos distintos

| Evento | Qué demuestra el firmware | Lo que no demuestra |
|---|---|---|
| Fin del temporizador host | transición y notificación `ExposureTimerEnd!` de A6000 estudiada en S57 | fin de carga de cada fila |
| Mensaje a Darwin | transporte de un estado/orden del host | accionamiento físico en ese instante |
| Fin mecánico | lógica de bobinas y seguimiento en Darwin, según modo | fin electrónico sin cortina |
| Fin de integración electrónica | sin observación directa | no se infiere del retorno de SetExposure |
| Inicio/fin de lectura | configuración y eventos de la cadena | instante de muestreo de cada fila |
| Fin del guardado | fuera de estos escenarios | no equivale al fin de exposición |

## Tres modelos físicos

1. **Segunda cortina mecánica termina la foto convencional.** Compatible con Darwin y cortinas del modo normal; no demuestra que el IMX210 carezca de temporización electrónica alternativa. Se necesitaría correlación óptica/eléctrica y posición de cortina.
2. **El sensor termina por temporización programada.** Apoyado indirectamente por la programación anticipada de números de tiempo y compatible con A7S Silent. Falta documentar qué gobiernan en el sensor; escribirlos no demuestra que cierren la integración del IMX210 a resolución completa.
3. **Señal externa/secuenciador BIONZ termina la integración.** Compatible con VD/XPI y con los límites de observación del bus. No se localizó una transición causal de esa señal al fin de integración.

No hay prueba decisiva que seleccione un modelo para IMX210. Los tres pueden coexistir según fase o modo; la ausencia de una orden final en una ruta no discrimina entre 2 y 3.

## VD y SyncMode

Se conserva [S57-F](s57-p2s-vd-synchronization.md): P2S SyncMode 2 escribe el valor 2 y usa banderas OSAL; CAMERA_MAIN_SYNC organiza trabajo vertical. S58 añade las fórmulas de filas, no una prueba de «aplicar en el próximo VD». No se ha seguido de nuevo el planificador de 7 KB: no aportaría por sí solo semántica del periférico. VdNum/svr/N comparten fuentes, con ramas distintas entre productor y validador.

## Frontera y experimento

Primero, sin hardware: recuperar M/Tv/clk y sus restricciones por modo, y el camino que consume O+0x3d7 en una inicialización A7S real. Después, para decidir entre modelos: datasheet o traza **pasiva autorizada** CIS0+XPI+VD, con exposiciones cortas/largas y modos de cortina conocidos; correlacionar paquetes con lectura y cierre mecánico. No se realizaron mediciones ni cambios de cámara.
