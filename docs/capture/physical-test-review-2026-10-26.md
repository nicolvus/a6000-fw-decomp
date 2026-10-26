# Revisión de las pruebas físicas en cámara (P1–P24) — 26-10-2026

Alcance: contrastar **todas** las pruebas físicas del repositorio con la evidencia estática posterior, con lo ya hecho en cámara
(S64, volcados del 20-10-2026) y con las propuestas sueltas en otros informes. **No se ejecutó nada en cámara**; solo se leyó el volcado
`analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin` (RAM en reposo tras arrancar, no versionado) y los `README` de
`analysis/camera-dumps/`. Fuentes revisadas: [plan P1–P8](physical-test-plan.md), [S402 (P9–P12)](s402-physical-test-mapping.md),
[plan 2 (P13–P21)](physical-test-plan-2.md), [tesis](tesis-obturador-electronico.md), [S64](s64-silent-ram-nvram-test.md), S55, S57, S31, S134, S384, S328, S101, S135.
Etiquetas: `VERIFICADO` / `INFERENCIA` / `NO_VERIFICADO`. Conclusión S51 (A=NO, B=NO, C=NO): **inalterada**.

## 1. Resultado

- **Numeradas: P1–P21, y no hay otras con ese rango** (los `P22…P39` que aparecen en el repositorio son nombres de pines del MCU).
- **Ninguna queda descartada por la evidencia estática.** Las reservas se resumen abajo.
- **Se añaden P22, P23 y P24**: pruebas físicas que otros informes proponen o dan por necesarias y que no estaban numeradas.
- Se corrigen tres premisas erróneas del plan y se anotan dos pruebas que dependen de hardware que el proyecto no tiene.

## 2. Inventario único

Veredicto: **VIGENTE** (útil y sin descartar), **AJUSTADA** (vigente con la corrección indicada), **PARCIAL** (parte ya resuelta con datos existentes) o **BLOQUEADA** (falta una herramienta o hardware). Riesgo: B bajo, M medio, A alto.

| ID | Qué mide | Veredicto | Utilidad / motivo y ajuste | Riesgo |
|---|---|---|---|---|
| P0 | Backup NVRAM, recuperación, línea base | VIGENTE | Obligatoria. Existen backups del 20-10 (`20261020-first`, `nvram-referencia-20261020-214913`); repetir uno antes de cada sesión | B |
| P1 | Valor de `G+0x808` y `G+0x784` en reposo y al cambiar menús | **AJUSTADA** | Prerrequisito de P2–P4. En el volcado del 20-10 `G+0x808` (`0x83e9bd50`) = `0x120983c8`, **no 0** como decía el plan; `&7` = 0 ⇒ tipo 0 (coherente con S101), y `G+0x784` = 0. La palabra parece un identificador/puntero, no un selector pequeño: P1 debe confirmar si cambia con el menú. | B |
| P2 | Forzar `G+0x808` sin disparar | **AJUSTADA** | Escribir `1` pisa los otros 29 bits. Escribir `0x120983c9` (conserva los bits altos, `&7` = 1) cambia solo lo que lee el selector `0x4379316a`. Probar también `…c8` (control) y `…ca`. | B-M |
| P3 | Idem con disparo remoto + P7 | **AJUSTADA** | Mismo ajuste. La [tesis R2](tesis-obturador-electronico.md) decía «`G+0x808=2` ⇒ tipo 2»: según S101, **1 ⇒ tipo 2 y 2..6 ⇒ tipo 1**. Corregido en la tesis | M |
| P4 | Forzar `G+0x784=2` en el disparo | VIGENTE | S53 dice que Darwin A6000 descarta el bit `0x20`, así que lo esperable es «tipo 2 sin efecto»; sigue siendo la única forma de separar el selector del consumidor. Solo tras P2/P3 limpias | M-A |
| P5 | Traza lógica `GPIO_9`/P4C y `MSS_SO_DWN`, mecánico vs EFCS | VIGENTE (máxima) | Única vía a E6/E11 y a los criterios R1/R5 de la tesis. **Solo los casos A6000 son realizables**: los casos «Silent A7S» de S402 exigen una A7S, que el repositorio no tiene. Requiere abrir la cámara | B (abrir: M) |
| P6 | ¿El shell de servicio llega a Darwin o a su bootloader? | VIGENTE | S402 la justificaba con «LIRO `0x40e3` ausente en A7S», **ya corregido** (existe, S402 cierre estático). Quedan las diferencias 3 y 7. El shell ya lee toda la RAM (1 GiB, 20-10), así que la pregunta útil es solo si alcanza el espacio del MCU | M |
| P7 | Imagen: hélice/LED, rolling shutter, bandas de flicker | VIGENTE (máxima) | Criterio objetivo para todo lo demás. **P17 es la misma medición** (línea base): se fusionan | B |
| P8 | `+0x210`=1 («disparo múltiple») vs EFCS del menú | VIGENTE | S64: único efecto reproducible. El espejo `+0x210` vale 1 en reposo en el volcado del 20-10 (`0x83edf894` = 1), lo que refuerza que es un ajuste y no una ráfaga puntual. Solape con P19 (latencia/ráfaga): ejecutarlas juntas | B-M |
| P9 | Bus serie del sensor en Silent A7S vs A6000 | **BLOQUEADA** (A7S) | El caso A7S no es posible. Queda el caso A6000 mecánico vs EFCS, que es P22 | A |
| P10 | Forzar el campo de captura a 2 y mirar el bit CAIF `0x20` | **AJUSTADA** | S402 toma `captura+0x804` del **A6300**; en la A6000 el campo que lee `0x43841070` «solo escribe 0 o 1» (S401) y su offset no está identificado. **Prerrequisito estático**: fijar ese offset antes de escribir. Sin P5 no hay forma de ver el bit | M |
| P11 | Secuencia completa de escrituras de Darwin | VIGENTE (depende de P5) | Es análisis posterior a P5; no añade riesgo | B |
| P12 | Reposición tras aborto con tipo 0/2 | VIGENTE (baja prioridad) | Útil solo si P3 da tipo 2 efectivo. Riesgo mecánico real: tras `CameraSequence` S64 dejó la cámara sin arrancar | M |
| P13 | `0xfc02a00c` (máscara DFE/CISIF) en ejecución | **AJUSTADA** | Vigente (S341 predice `0xf00`/`0xfff`). **Riesgo infravalorado**: el barrido de `0xF0020000-0xF0024000` reinició la cámara 5 veces (20-10) y los `0xF0…` por telnet dan `Bad address`. Usar solo RMEM por shell de servicio, una página por sesión, y parar al primer fallo. El único MMIO leído con éxito es `0xf1000000+0x100` | M |
| P14 | Canales `w0` (`0xf3122300…`, `0xfc0a3100/4100`) | VIGENTE | Mismo ajuste de riesgo que P13 | M |
| P15 | `0xf292b000` (+0) | VIGENTE | Solo si P13 va limpia. Cierra E13 solo en parte (identidad sin hoja de datos) | M |
| P16 | Segunda matriz `0x43e80160` | **PARCIAL** | El volcado del 20-10 ya la muestra **con datos** (201 palabras no nulas en 1 KiB; primera palabra 0, nulos los primeros 20 B), mientras S328 la daba a cero en la imagen estática. `INFERENCIA`: hay productor en ejecución (o la zona es compartida); no se sabe quién escribe ni si el bucle recorre esos datos. La prueba pasa a ser **dinámica** (¿cuándo se llena, cambia con drive mode?) | B |
| P17 | Línea base de P7 | **FUSIONADA con P7** | Misma medición; se ejecuta primero | B |
| P18 | Gates `+3/+6` del estado IMX210 (`0x83f72d00`) | **PARCIAL** | En reposo, 32 B a cero en el volcado del 20-10 (coherente con Backup `0x3000b` = gates a 0). Falta live view, medio pulsado y disparo | B |
| P19 | Latencia y ráfaga, mecánico vs EFCS | VIGENTE | Complemento de P8; sin riesgo | B |
| P20 | `dmesg`/logs durante un ciclo de disparo | VIGENTE | Barata y puede dar de golpe la vista temporal de los módulos decodificados (S181–S200, S500–S627). Conviene hacerla **primero** | B |
| P21 | Modos fuera del vocabulario (`0x4c`, `0x4e`) | **AJUSTADA** | `camera_drivemode_override.py` escribe el byte `D+0x86` **directamente en RAM**: no pasa por el setter que S324/S333 muestran que rechaza `>0x47`. Prueba, por tanto, si el consumidor aguas abajo tolera un valor que el setter nunca dejaría pasar, no el «rechazo» que prometía el plan. Sigue siendo opcional | M-A |
| **P22** (nueva) | Traza lógica de `CIS0_SCK/SI/XCS`, `CIS0_VD`, `CIS0_IMG_RST` y XPI (CN0400 pin 6) en foto mecánica 1/1000 s, 1/4 s y EFCS | VIGENTE (nueva) | Propuesta en S55, S57 y S31 («captura pasiva de VD/lectura/interrupciones»), listada como F4 pero sin número. Decodificar con `analysis/s56/p2s_emu.frames`; buscar `CC→C4` de ID1, flancos de XPI y fin respecto de VD. Es la prueba que podría dar el «fin de integración electrónico» (E9, R4 de la tesis). Absorbe el caso A6000 de P9. Requiere abrir la cámara | M |
| **P23** (nueva) | Lectura de `0xf2a1xxxx` (registros BIONZ/GPIO) justo tras el flanco de `GPIO_9`, mecánico vs EFCS | VIGENTE (nueva) | S55 la pide («implica registrar `0xf2a1xxxx`»). Complemento de P5 sin abrir la cámara. Misma cautela de MMIO que P13 | M |
| **P24** (nueva) | Valores que solo existen en ejecución: rectángulos de entrada de `0x436c25d0` (E20), `params[+9]` = 2/3 y activación de `RecordImage`/cola `0x40193`, `[estado+8]` (S134, S384) | **BLOQUEADA** | S134 y S384 piden «trazado dinámico» y los remiten a «P1», que solo lee `G+0x808`: **la referencia era incorrecta**. Estos valores están en registros o pila; no se leen con `dd` sobre RAM. Hace falta un depurador/hook en cámara que no existe | — |

Nota sobre equivalencias: `0x43xxxxxx` virtual = `0x83xxxxxx` físico (dirección de P1: `0x83e9bd50` = `G+0x808` con `G=0x83e9b548`; verificado contra el volcado).

## 3. Contradicciones y errores corregidos

1. **P1/S101**: «`G+0x808` = 0 en reposo» → es `0x120983c8` (`&7` = 0). Conclusión de S101 (tipo 0 por defecto) **intacta**.
2. **Tesis R2**: «`G+0x808=2` ⇒ tipo 2» → es **1** (S101). Nota añadida en la tesis.
3. **S402, diferencia 1**: «handler `0x40e3` ausente en A7S» sigue en la tabla de mapeo, aunque S402 (cierre estático) lo rectifica. Nota añadida; P6 ya no depende de esa fila.
4. **S134/S384**: remiten a «P1» para un trazado dinámico que P1 no hace → recogido como P24.
5. **P16 vs S328**: S328 (ceros en la imagen) y el volcado vivo (datos) no se contradicen, pero la premisa «sin productor» de P16 no se sostiene en ejecución. Se anota; S328 no se modifica.
6. **P9/P5/P7 (S402)** incluían casos «Silent A7S» imposibles sin una A7S.

## 4. Hallazgos sin cámara (volcados del 20-10, `INFERENCIA`)

- `arm7sram_0x0_0x4000.bin` (16 KiB, leído y «sin interpretar») empieza con una tabla de vectores ARM (`ldr pc,[pc,#…]`): es código ARM7, **no** el bootloader Cortex-M3/Thumb de Darwin (S70). Sirve para análisis estático, no para cerrar P6.
- El BK4 (852 647 B) ya contiene el Backup de la cámara; el contenido de la clave `0x3000b` podría leerse sin tocar la cámara. Ambos puntos pasan a E21.

## 5. Orden consolidado

Sin riesgo: `P0` → `P20` → `P7/P17` → `P19` → `P1` → `P18` → `P16` → `P8`.
Con RAM escrita: `P2` → `P3` → `P4` → (`P10` tras fijar el offset) → `P12`.
MMIO (solo por RMEM, una página por sesión): `P13` → `P14` → `P15` → `P23`.
Abren la cámara: `P5` → `P22` → `P11`. Shell de servicio: `P6`. Opcional: `P21`. Bloqueada: `P24`.
Cada prueba se detiene si la anterior no es limpia; todas necesitan autorización expresa y backup previo (reglas de [§0](physical-test-plan.md)).

## 6. Límites

No se verificó que las herramientas (`camera_*.py`, `senser_*.py`) sigan funcionando en la cámara actual. La utilidad es una valoración mía a partir de lo que cada resultado cambiaría en S51, no una medición. La revisión de P16/P18 usa una sola instantánea en reposo.
