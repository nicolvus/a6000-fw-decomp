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

## Lo que falta (en orden)

1. Decodificar las estructuras S2/S3 de un descriptor `@M00B` multi-opción (p. ej. pid `0x37`) para escribir la tabla opción→valor
   de Gamma (Movie 4, Still 5, ITU709 3, Cine1–4 6–9; G20 §1). La palabra de modelo [8] (`0x201`…) parece codificar nº de claves/valores.
2. Construir `pp_gamma_descriptor.py` (hermano de `silent_descriptor.py`) con el pid elegido.
3. Editar listas de propiedades y arrays de hijos (`add_menu_entry.py`) y textos `.uxc`; probar carga en qemu-user como G09 §5e.
4. Solo si 1–3 fallan: `libpp.so` de G20 §2.

Las curvas en RAM (G18, 3.56) siguen siendo condición para que Still/Cine1–4 se vean distintos; requiere autorización para instalar.
