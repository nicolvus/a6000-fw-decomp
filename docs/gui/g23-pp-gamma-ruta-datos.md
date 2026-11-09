# G23 — Picture Profile: ruta solo-datos para Gamma, sin `libpp.so` (estático, 09-11-2026)

Revisa el orden de entrega de [G20](g20-menu-pp-construccion.md) §2. Nada probado en cámara ni en qemu.

## Hechos medidos

| Pregunta | Medida | Consecuencia |
|---|---|---|
| ¿Los nodos de opción son código? | Los objetos `cmnViewSettingNode*` son `.bss` (construidos en `_INIT`), pero sus **listas de propiedades** (`cmnViewSettingPropertyList*`, `R`) y los **arrays de hijos** (`cmnViewSettingNodes<X>Default`, `D`, con su `…NumOf…Default`) son datos | se puede editar etiqueta (id de `string_*.uxc`), valor `0xf/0x10`, y reapuntar/contar hijos sin código nuevo |
| ¿Hay nodos hijos ociosos suficientes? | Ajustes ocultos (`no_activas_a6000`): AfTrackingSpeed 3, LocalAreaLimitation 3, DualRecImageSize **8**, AfIlluminator 2, CtrlDialWheelSetup 2, CustomAfAreaDisplay/Number 2, MoviePushAutoFocus 2, SilentShutter 2, WheelLock 2 | hay ≥ 10 nodos prestables para las 7–10 opciones de Gamma; G20 §1 solo miró el máximo por ajuste (3) |
| ¿El descriptor del elemento `Normal` es dato? | Sí: `D[pid]` en `0x8C268` apunta a descriptores de 19 palabras (G22: `silent_descriptor.py` ya los clona a un `PT_LOAD` nuevo con sus relocaciones) | misma técnica para Gamma: `@M00B`, escritura `0x40`, clave `0x214`; lectura `0x49`, clave `0x216` |
| Descriptores `@M00B` de la A6000 con varias opciones numéricas | p. ej. pid `0x37`, `0x13`, `0x14`, `0x44`, `0x4d`, `0xe7` (palabra de modelo [8] = `0x301`/`0x401`/`0x3401`) | plantillas candidatas para las tablas opción→valor (S2/S3) |

## Conflicto a evitar

El **ProcessId `0x12`** ya está reservado por G22 (`silent_descriptor.py`, Silent Shooting). Gamma debe usar otro pid oculto
(candidato: `LocalAreaLimitation`, 3 hijos, o `AfIlluminator`; comprobar su `D[pid]` con `process_bindings.py`).

## Layout del descriptor (VERIFICADO, desensamblado de `CmnViewProcessDataElementNormal::getDataModel*`, 09-11-2026)

`desc` (19 palabras): `+0x04` cautions por opción (no se usan, solo se indexan) · `+0x15` **nº de opciones** · `+0x18` modelo · `+0x1c` nº de modelos.
Modelo (9 palabras): `+0` nombre · `+4` update · `+8` evento de escritura · `+0xc` id de lectura · `+0x10` array de claves de escritura · `+0x14` de lectura ·
`+0x18` tipos por clave (0 bool, 1 número) · `+0x1c` tabla opción→valor, índice `opción·nclaves + clave` · `+0x20` nclaves · `+0x21` nº de entradas.
Corrige la lectura previa de «S0/S1/S2/S3»: son arrays planos, no estructuras de 12 palabras.

## Hecho: `scripts/gui/pp_gamma_descriptor.py` (pid `0x3c`)

Descriptor nuevo en un `PT_LOAD` añadido (como `silent_descriptor.py`): `@M00B`, escritura `0x40`/clave `0x214`, lectura `0x49`/clave `0x216`,
7 opciones con valores (4, 5, 3, 6, 7, 8, 9) = Movie, Still, ITU709, Cine1–4. Tests `tests/test_g23_gamma_descriptor.py` (3, verdes, con los de G22).
La `.so` parcheada carga y ejecuta su init en `qemu-arm` con el sysroot de la cámara (`LD_PRELOAD` con `libObj.so`; no se leyó la memoria con gdb).

## Hecho: `scripts/gui/build_pp_gamma_menu.py` (paquete de prueba, sin instalar)

Reutiliza el ajuste oculto **AfIlluminator** como menú «Gamma» (7 opciones): listas de propiedades de la raíz y de 7 nodos ociosos
(AfIlluminator ×2, CtrlDialWheelSetup ×2, WheelLock ×2, AfTrackingSpeed1) **editadas en sitio** (mismo tamaño, 5 y 6 tripletas: no se toca ningún `movs`);
`NumOfAfIlluminatorDefault` = 7 (el constructor de la raíz lo lee en ejecución: `ldr r2,[r3]`, `CautionConfig.so:0x138fcc`); array de hijos nuevo en un `PT_LOAD` RW
con 7 `R_ARM_ABS32`; raíz con ProcessId `0x3c`; entrada nueva en las 5 páginas con `add_menu_entry.py` (delta `0x15b8`; el de Silent, `0xeb0`, se reprodujo con `nm`);
textos nuevos (Gamma, Still, ITU709, Cine1–4) copiados de la A6300 a 7 ranuras libres de los 25 idiomas latinos (sin los de G09).
Verificado: 5 tests (`test_g23_gamma_menu.py`, `test_g23_gamma_descriptor.py`) y carga conjunta de los tres `.so` + `libObj` en `qemu-arm`: los tres ejecutan su init (incluida la construcción de la raíz con 7 hijos) sin fallo.

## Límites y supuestos NO verificados

- Valor interno de opción (`0xf/0x10`): se pone el índice de la opción (0–6); no se ha comprobado cómo lo usa la vista frente a la tabla opción→valor del descriptor.
- Los nodos hijos siguen referenciados por los arrays originales de sus ajustes ocultos (nunca mostrados); si el nodo guarda puntero al padre, el último en construirse manda. Sin leer memoria con gdb.
- La clase del nodo raíz (`CmnViewSettingNodeAfIlluminator`) podría tener comportamiento propio; no se ha leído.
- `viewUnified2` y `CautionConfig` de este paquete **no se combinan** todavía con los de Silent (G22/3.54): ambos parchean las mismas páginas y `CautionConfig`.
- Idiomas no latinos sin textos nuevos (como G09/G10-C). Sin curvas en RAM (G18) solo Movie/ITU709 son distintos; nada probado en cámara.

## Lo que falta

1. Leer memoria en qemu (gdb) del array y de la raíz tras el init; leer la clase de la raíz.
2. Combinar con Silent/3.56 en un único paquete (pages de `viewUnified2`, `CautionConfig`) y auditarlo.
3. Con autorización: instalar y comprobar en cámara que Gamma Cine1 = modo de prueba del 3.56.
4. Después: resto de parámetros PP (30), selector PP1–PP10 y Copy/Reset (G20 §2 b–d) con la misma técnica.
