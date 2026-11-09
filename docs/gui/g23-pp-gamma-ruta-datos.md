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

## Lo que falta (en orden)

1. ~~Tabla opción→valor y `pp_gamma_descriptor.py`~~ hecho.
2. Textos Movie/Still/ITU709/Cine1–4 en `string_*.uxc` (25 idiomas) si el A6000 no los trae.
3. Editar listas de propiedades y arrays de hijos (`add_menu_entry.py`) y textos `.uxc`; probar carga en qemu-user como G09 §5e.
4. Solo si 1–3 fallan: `libpp.so` de G20 §2.

Las curvas en RAM (G18, 3.56) siguen siendo condición para que Still/Cine1–4 se vean distintos; requiere autorización para instalar.
