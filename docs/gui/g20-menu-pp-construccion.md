# G20 — Menú Picture Profile en la A6000: cómo se construye (estático, 08-11-2026)

Sigue a [G19](g19-menu-pp-capa-modelo.md) §2c (la API PP existe en la `libObj` de la A6000). Este documento fija **cómo** añadir la
interfaz. Scripts: `analysis/gui/g20/` (`deps.py`, `vtcompat.py`, `modelcalls.py`, `libpp/prueba_carga.cpp`).

## 1. Hechos medidos

| Pregunta | Medida | Consecuencia |
|---|---|---|
| ¿Qué necesitan las clases PP de la A7S? (`deps.py`) | 349 funciones, 34 KB. Fuera de ellas solo `CmnViewPictureProfileCommon` (en `viewUnified2.so` de la A7S, sin equivalente en la A6000) y 23 funciones que la A6000 sí tiene | el código de la A7S es casi autónomo |
| ¿Se puede trasplantar en binario? (`vtcompat.py`) | vtable de `CmnViewProcessDataElementCustomBase`: **A7S 24 ranuras, A6000 22**. Desde la ranura 6 cambian (`getValue(int&,int&,int&)` nueva en la A7S) | **no**: cada llamada virtual de la A7S iría a otra ranura. Descartado |
| Modelo de lectura y escritura (`modelcalls.py`) | A6000 y A7S ejecutan el id `0x1e` tanto con `@M00B` como con `model/CAMERA`. La A7S lee PP con `get model/CAMERA 0x49` en 22 sitios, la A6000 en ninguno | `@M00B` ≡ `model/CAMERA` (INFERENCIA fuerte); hoy ninguna vista de la A6000 lee PP |
| Valores de gamma que admite el modelo de la A6000 (`App2Obj` caso 7, `0x4b477a`) | 0–9 → VALUEID `0x1b7…0x1ba`, `0x39c…0x3a1`. Sin `0x480/0x481` | **Movie 4, Still 5, ITU709 3, Cine1–4 6–9**. ITU709(800%) y S-Log2 no existen en la A6000 (necesitan `libObj` + núcleo, fase 4) |
| Nodo oculto reutilizable (`settings-sweep.json`) | el máximo son 3 opciones (`AfTrackingSpeed`, `LocalAreaLimitation`) | la gamma (7 opciones) y el resto necesitan **nodos nuevos**, es decir, código en un constructor |
| ¿Se puede compilar código propio? | clang + lld: `--target=armv7a-linux-gnueabi -mthumb -mfloat-abi=softfp` (mismo ABI EABI5 que la cámara) | **VERIFICADO**: `prueba_carga.cpp` (clase con despacho virtual y constructor) carga y se ejecuta en qemu con el `ld.so` de la cámara (glibc 2.11.2): «libpp: init f=42» |
| Sección dinámica de `cmn_view_processDataMgr.so`, `CautionConfig.so` y `viewUnified2.so` | 1 `DT_NULL`, sin entradas libres | para cargar una biblioteca nueva hay que mover `.dynamic`/`.dynstr` a un segmento nuevo (como el `.rel.dyn` de `add_menu_entry.py`) |

## 2. Diseño elegido

Una biblioteca nueva **`libpp.so`** (C++ propio compilado con clang contra los `.so` de la A6000, no código de la A7S) con:
1. Las clases de elemento PP, derivadas de `CmnViewProcessDataElementNormal`/`CustomBase` de la **A6000** y con la lógica de la A7S
   (REA, G19 §2c). Escritura `requestModelExecute("@M00B", 0x40, {0x1f8+4i: v})` y lectura `getModelInfo("model/CAMERA", 0x49)` → `0x1f8+4i+2`.
   Perfil: `0x274`.
2. Los nodos de menú (`CmnViewSettingNode`) como símbolos propios, construidos en su constructor.
3. Carga: `DT_NEEDED libpp.so` en `cmn_view_processDataMgr.so` (sección dinámica movida). Esa biblioteca amplía además las tablas de
   ProcessId (`0xe8` → `0xe8 + n`) y el caso nuevo de `factoryElement`. Las páginas de `viewUnified2.so` apuntan a los nodos nuevos con `add_menu_entry.py`.

Orden de entrega (cada paso con su prueba en qemu): (a) solo **Gamma** con sus 7 valores; (b) los otros 30 parámetros; (c) selector PP1–PP9
y Copy/Reset; (d) pantallas propias. Nada de esto se ha probado en cámara.
