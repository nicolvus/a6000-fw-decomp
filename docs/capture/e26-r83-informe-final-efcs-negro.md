# E26-R83 — Informe final: fotos negras con EFCS activado a 1/1000 y más rápido (07-11-2026)

Cierra la investigación R65–R82. Todo es estático salvo una medida de solo lectura (R71). No se escribió nada en la cámara.

Etiquetas: **VERIFICADO** (bytes/instrucciones/emulación) · **MEDIDO** · **INFERENCIA** · **SOLO CÁMARA**.

## 1. Resumen

* **Síntoma (MEDIDO, R57, R62, R71):** con EFCS activado la exposición pierde ≈1,25 ms: ≈1,25 ms constante hasta unos 4,3 ms de exposición, ≈0 a 8 ms, con un degradado de ≈0,5 ms de arriba abajo. A 1/1000 y más rápido la foto sale negra. Pasa también con el firmware oficial 3.37.
* **Causa:** el firmware y los datos de esta cámara no la producen (confianza alta, VERIFICADO). La causa más probable es física, en el obturador o su circuito (confianza media). Qué pieza falla: confianza baja, solo se decide en la cámara.
* **Que EFCS funcionara antes no está demostrado:** no hay ninguna foto de referencia con firmware de Sony y EFCS a ≥1/1000 anterior al 03-11. Dos momentos posibles de daño: el atasco del obturador del 20-10 y la apertura de la cámara del 03-11 para soldar la sonda SWD.
* **Compensación:** existe un parche de Darwin con tabla por velocidad (R82), verificado por emulación y preparado sin instalar. Compensa, no repara: sirve de 1/1000 hacia abajo y deja el degradado de arriba abajo sin corregir.

## 2. Qué se descartó y con qué evidencia

| Hipótesis | Estado | Evidencia |
|---|---|---|
| Datos de Darwin cambiados | Descartada | G y B (NVRAM `0x1850000/01`) idénticos en los 28 volcados desde el 20-10 (R66). El `darwin_core` de recuperación es idéntico byte a byte al 3.21 (R58) |
| NVRAM `0x30102`/`0x30100` | Descartada | No son bloques de Darwin; los experimentos de R61–R64 no tocaron Darwin (R66, R69) |
| El BIONZ reprograma el reinicio según T | Descartada | Con el EFCS de Sony, `0x438417b6` lee `[0x30097+0x15] = 0` (27 volcados) y deja `record+0x64 = record+0x1c`, fijo. `0x4383fa40` no interviene (R74, R75) |
| Umbral de 6 ms (`0x3012b = 0x1760`) | Coincidencia | `0x43842158` solo se consulta si `+0x15 = 0` y no actúa con EFCS; `pkt[1] = 0x02` a 1/500 y 1/125 lo descarta (R74, R75) |
| NVRAM `0x30087` como palanca del reinicio | Descartada | Su valor va a `StillInfo+0x2b4` (procesado en Linux), no al sensor (R73) |
| Ganchos del planificador (`0x43f9b37c…`) | Cerrado con límite | Variables de depuración, solo se escriben por orden de servicio y son volátiles (R73) |
| Interacción de Darwin según B−A | Descartada | A y B corren el mismo código en ambas ramas, en máquinas y temporizadores distintos; el pulso de P4E dura 5 ms fijos; el rearme y la FSM ADC no dependen de B (R75, R77–R79) |
| Cortina simplemente más rápida o retardo fijo de imán | Descartada como única causa | 1/250, 1/200 y 1/125 comparten rama de Darwin y la pérdida pasa de 1,26 ms a 0 (R74, ajuste de R57 §8) |
| Línea P4C cortada | Sin indicio | En 42 disparos llegan al BIONZ las señales del mecanismo y del sensor, y el fin de exposición sigue a B de Darwin (4,2 ± 0,5 ms frente a 4,57 ms entre 1/1000 y 1/125) (R71). P4C no se identificó |
| Ajuste de servicio de Sony | Sin indicio | Level 3 completo leído: ningún ajuste del obturador. Level 2 solo visible en parte: sin ajuste de obturador en lo visible; datos de ajuste en la placa SY-1028 |

## 3. Lo que se sabe del mecanismo

* **Orden de las señales (VERIFICADO, R67, R70, R77):** P4C sube en la preparación (`0x1811a` → `0x17cee`) antes del armado. La acción `0x1f` (`0x190fc`) arma A y B (`0x18d6e`). A baja P4C y P4D; B sube P4E (`2ND_CURTAIN_MG`) y lo baja 5 ms después. Tras el armado el rearme vuelve a subir P4C.
* **Temporización de Darwin con EFCS (VERIFICADO, R65, R66):** `S+0x48 = T − u16[G+0x42]`, con `G+0x42 = 3407 µs`. `B − A = T − 3401` (rama corta) o `T − 3428` (larga); entre `S+0x48 = −150…50` va a la rama intermedia `0x20544`.
* **La pérdida sigue a `B − t0`, no al flanco A (INFERENCIA, R75):** en la rama corta, mover A 2 ms no cambia la pérdida. Falta saber qué instante físico es `t0` (armado o preparación): **E26-R75-T0**.
* Darwin y el BIONZ no contienen ningún dato propio de esta cámara que explique la pérdida. Lo único propio no volcado es la configuración `[0x20000050]` que pone el cargador de Darwin (**E26-R72-DARWIN-CFG**). Hoy no es 0, porque Darwin suelta la segunda cortina (R71).

## 4. Fuentes públicas (R74, verificadas)

* Kasson (a7RII): con EFCS, a 1/4000 la parte superior recibe ≈1/3 de la luz; a 1/8000, casi nada. Recomienda no pasar de 1/1000. Es un efecto de diseño de décimas de milisegundo, mucho menor que 1,25 ms.
* Guía de ayuda de la A6000: avisa de «ghosting» con objetivos de gran diámetro y de brillo desigual con objetivos de otros fabricantes. Con el 16–50 nativo no aplica.
* iFixit (NEX-3N, no A6000): la unidad de obturador usa imán de neodimio, muelle de retorno con rueda de tensión y cables flex frágiles.
* No hay procedimiento público para recalibrar el obturador de la A6000.

## 5. Compensación: el parche de Darwin (R76–R82)

**Diseño elegido (vía A, R82):** se reescribe en su sitio el inicio de la rutina de temporización `0x18d6e..0x18e0f` (162 B) con codificaciones más cortas para integrar la búsqueda en tabla. No hace falta ningún hueco. La imagen mide lo mismo (157 276 B), solo cambian 139 bytes y no toca los parches 3.30–3.38.

* Tabla: 14 entradas `{s16 Tmax−G42, u16 c}` en `G+0x48..0x7f` de la NVRAM (propiedad `0x1850000`, hoy a ceros). Se aplica solo con EFCS y `S+0x60` bit 1 = 0. Una `c` fuera de [0, 2000] µs se ignora, y con la tabla a ceros el parche es neutro.
* **Verificación triple:** (1) emulación diferencial original/reescrita con 1 000 000 de estados al azar y 786 432 combinaciones exhaustivas, sin ninguna diferencia; (2) modelo Python escrito a mano a partir del desensamblado, idéntico en todos los estados; (3) imagen con el código añadido al final: retardos A/B idénticos en los 1866 códigos Tv de ≈1/4000 a 1/22, sin la rama intermedia.
* Error de exposición modelado: ≤2,2 % en la escala de 1/3 EV (media del cuadro).

**Cómo se llegó aquí (errores corregidos por el camino):**

| Intento | Resultado |
|---|---|
| `B+0x86 +1250` (R66) | Se satura: solo cubre T < 2,13 ms (R68) |
| `G+0x42 −1250` | Corrige todo pero sobreexpone ≈+0,25 EV a 1/125 y más lentas, y alarga plazos de `0x182d8` (R70) |
| Parche con cave en `0x13d5a` (R76) | **Bloqueado en R81:** esa función está viva (se llama desde `0x1516c`); el método de «funciones muertas» fallaba; no hay huecos ≥40 B |
| Tabla en `G+0x44` | Corregido en R76b: Darwin lee `G+0x44..0x47` |
| Scripts del repo | Reparados en R80: faltaba `keystone` y el import apuntaba a un módulo inexistente; cave sin límite de bucle ni validación de `c` |
| Lógica lineal a tramos | Descartada en R82: error 7–12 % frente a 2,2 % |

**Límites del parche:**

* **No corrige el degradado vertical.** Darwin solo fija dos instantes iguales para todo el cuadro. Con `c` igual a la pérdida media, la parte alta recibe más luz que la baja:

  | Velocidad | Arriba / abajo |
  |---|---|
  | 1/4000 | abajo sigue negro |
  | 1/2000 | 1,6 EV |
  | 1/1000 | 0,74 EV |
  | 1/500 | 0,36 EV |
  | 1/250 | 0,18 EV |

  Útil de 1/1000 hacia abajo. Corregir 1/2000 y 1/4000 exigiría cambiar el barrido del sensor en el BIONZ, que no se ha estudiado.
* A 1/500 (T = 1953 µs) la velocidad cae junto a la rama intermedia `0x20544`, no modelada: si la pérdida real fuera ≈8 % mayor, el error podría llegar a ≈7 %.
* La reescritura elimina un `str` intermedio de `S+0x48` y añade un bucle de hasta 14 vueltas. El emulador no modela temporizadores ni el NVIC.

**Vía solo NVRAM (sin tocar el firmware):** `B+0x86` = 1256 y `G+0x42` = 2157, con volcados generados en `analysis/camera-dumps/20261107-r82-nvram/` (no versionado). Hay que volcar de nuevo y regenerar antes de escribir. Además comprueba la premisa nunca probada: que la NVRAM llega a Darwin.

## 6. Recomendación y orden de pruebas en la cámara (todo con autorización)

1. **Pruebas físicas, sin escribir nada** (E26-R74-FISICO), repitiendo 1/1000 y 1/250 con EFCS tras cada paso: retirar la sonda SWD; reasentar el flex del obturador (CN4900) y comprobar continuidad de P4C y P4E; batería frente a adaptador de corriente, en frío y en caliente; revisar o cambiar la unidad del obturador. Si alguna cambia el resultado, no hace falta compensar.
2. **Prueba NVRAM** (E26-R82-NVRAM): copia previa con `senser_backup_dump.py`, escribir `B+0x86 = 1256` con `senser_backup_restore.py`, medir. Confirma si la NVRAM llega a Darwin y la forma real de la pérdida. Reversible restaurando el volcado.
3. **Parche con tabla** (E26-R82-CAMARA): solo si 1 no resuelve y 2 confirma la vía. Construir con `efcs_tabla_diff` (`scripts/e25_27/build.py`, preparado sin conectar), con la tabla a ceros primero (neutro), comprobar EFCS activado y desactivado, y después escribir la tabla calibrada por NVRAM con dos tandas de fotos (`scripts/e26_r76/e26_r76_calibrar_efcs.py`). Reversión: reinstalar 3.37.
4. Medir `B − t0` (E26-R75-T0) con un analizador lógico o con dos disparos extra; el usuario descartó el analizador.

## 7. Pendientes que quedan

| ID | Tipo |
|---|---|
| E26-R74-FISICO | Físico, cámara |
| E26-R75-T0 | Cámara o analizador lógico |
| E26-R74-COMP / E26-R82-NVRAM | Opcional, escribe NVRAM, autorización |
| E26-R82-CAMARA | Opcional, paquete propio, autorización |
| E26-R82-ANEXO | Opcional, solo si fallara la vía A |
| E26-R72-DARWIN-CFG | Solo con SWD de Darwin |
| E26-R49-SONDA | Físico, retirar la sonda (después de las pruebas que la necesiten) |
| E25-11 | Integrar al firmware la corrección del obturador electrónico (autorización) |

Pendiente de verificar fuera de la cámara: la sección «ADJUSTMENT» del manual de servicio Level 2 versión 1.4 (acceso con sesión; no se pudo abrir).

## 8. Informes de la serie

R65 (rama EFCS de Darwin) · R66 (bloques de Darwin = NVRAM `0x1850000/01`) · R67 (eventos A/B = P4C/P4E) · R68 (auditoría) · R69 (revisión de R56–R64) · R70 (P4C, `ip`, `G+0x42`) · R71 (medida SWD, 42 disparos) · R72–R73 (`0x30087`, ganchos) · R74 (conclusión) · R75 (verificación de R74 y de Darwin) · R76/R76b (calibración propia) · R77–R79 (orden temporal y límites de Darwin) · R80 (auditoría del parche) · R81 (bloqueo del cave) · R82 (parche v3 en sitio).

## 9. Límites de este informe

No se leyó el manual de servicio Level 2 completo ni se usaron fuentes tras acceso con sesión. REA se usó en R73 y de forma limitada después; el resto es Capstone, Unicorn y volcados. La conclusión física se apoya en descartar las causas de firmware y de datos, no en haber medido una pieza concreta.
