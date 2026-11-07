# E26-R68 — Auditoría de R65–R67 y del triaje del 07-11-2026 (07-11-2026, estático)

Se revisaron contra el código (`darwin_core.bin` 3.21, Capstone) y los volcados las afirmaciones de [R65](e26-r65-darwin-efcs-on-resta-g42.md), [R66](e26-r66-bloques-darwin-en-nvram-1850000.md), [R67](e26-r67-eventos-a-b-p4c-p4e.md), las filas de `PENDIENTES` y `knowledge/CURRENT.md`.
Prueba nueva: `test_retardo_de_a_se_satura_a_1` en `tests/test_e26_r67_eventos_darwin.py`.

## 1. Errores encontrados y corregidos

| # | Dónde | Qué decía | Qué es correcto | Evidencia |
|---|---|---|---|---|
| 1 | R65 §3, fila E26-R62-DARWIN-IP, CURRENT (fila R65) | «Si `S+0x48 < −150` la segunda cortina sale de inmediato → **explica** la pérdida constante y el negro desde 1/1000» | Con `G+0x42 = 3407` esa rama sale en todas las velocidades por debajo de ≈ 3,26 ms y **retrasa A** en lugar de B. La separación `B − A = T − 3401` es continua: la rama no explica la pérdida (R66 §3) | `0x18e4c–0x18e88`; valores de R66 §2 |
| 2 | R65 §2 y §1 (última viñeta) | «`+0x88 = 834` era +500 µs reales» y el efecto de `+0x88` interpretado en Darwin | `0x30102` no es el bloque B (R66 §1): esos experimentos no tocaron Darwin | R66 §1 |
| 3 | R66 §4, E26-R66-B86, CURRENT | `0x1850001+0x86` +1270 compensa «1/320 y más rápido» | **Se satura:** si `S+0x48 + B86 ≥ 0` el retardo de A es 1 µs. Solo compensa T < 2131 µs (≈ 1/470 y más rápido). Entre 2131 y 3257 µs la exposición queda fija en ≈ 2,1 ms (a 1/320, −32 %) y entre 3257 y 3457 µs no hay corrección. La palanca coherente es `G+0x42`, con efectos secundarios | `0x18e6a adds; 0x18e76 bmi; mov.w r0,#-1; rsbs` (test nuevo) |
| 4 | CURRENT, tabla «Estado global» | Cámara en 3.26; hito del obturador = 3.23; fila del objetivo de recuperación | La cámara lleva el **3.37 oficial** (R57, R63), con la variante BIONZ `0x30102+0x88 = 834` todavía escrita (R64 §6, inocua para Darwin). El obturador electrónico funciona con el 3.30–3.35 (R54–R56). La recuperación está cerrada | R57 §5, R63, R64 §6 |

## 2. Afirmaciones rebajadas de VERIFICADO a INFERENCIA

* **`t` = 0 durante el uso** (R65 §1). Está verificado que vale 0 **al arrancar** (zona que se pone a cero). No se ha localizado el emisor BIONZ de las órdenes `0x62–0x65`, así que podría fijarse en el arranque. A favor de `t` = 0: con `t` ∈ {1, 2}, EFCS activado tomaría la rama mecánica (`S+0x48 = T − 435`) y sobreexpondría, en vez de perder luz.
* **Flujo backup → Darwin** (R66 §1). Están verificados la tabla `0x43fe8c38`, los IDs y tamaños 1:1 con `0x1850000–05` y el registro con la bandera 8. Que el sistema de backup llame a `0x436bc514` con el contenido de esa misma propiedad es INFERENCIA fuerte: no se ha trazado la llamada.
* **«B suelta la segunda cortina»** (R66 §3, R67). Verificado: B pone P4E (`2ND_CURTAIN_MG`) a 1, y P4E vuelve a 0 después por el seguimiento ADC (`0x207c2/0x207ec`) o por las rutas de reposición (`0x1f698`, `0x206f6`). Que la cortina arranque al subir P4E, y no al bajar, es INFERENCIA.
* **«0x30102 no llega a Darwin»** (R66 §1) queda así: no es el bloque B y no se ha encontrado otra vía.
* **E26-R49-DARWIN-0x63** (triaje): «sin NG en las instalaciones posteriores» significa que ningún informe R50–R57 registra un NG; no hay un registro sistemático.

## 3. Comprobado y vigente

* `S+0x48 = T − u16[G+0x42]` con EFCS activado, y `T + s16[G+0x40]` con EFCS desactivado, ambos con su compuerta en `S+0x60` (emulación).
* Las tres ramas de `0x18d6e` y sus correcciones: `< −150` usa `B+0x86/0x84` y `B+0xc7`; −150…50 va a `0x20544` (flancos con esperas activas) y usa `B+0xc8`; `> 50` usa `B+0x8a/0x88` y `B+0xc6`. Antes se describió la rama intermedia como «casi simultánea»; queda precisado.
* `B+0x84..0x8a` solo se leen en `0x18d6e`. `G+0x42` tiene cinco lectores.
* G y B (`0x1850000/01`) son idénticos en los 28 volcados; los µs de `0x19a12`; A = P4C ← 0 y B = P4E ← 1.
* Triaje: las 67 filas cerradas tienen su motivo en la fila, y ninguna borra evidencia. Las 15 que quedan son físicas, necesitan autorización, son del repositorio o son del carril GUI.

## 4. Pendientes afectados

* **E26-R66-B86:** corregido (§1.3). Ya no es la propuesta recomendada. Para compensar en todas las velocidades rápidas, la opción coherente es `0x1850000+0x42` (3407 → ≈ 2137), con sus efectos secundarios sin evaluar; con B86 y B8a solos quedan huecos entre 2131 y 3457 µs.
* Ningún pendiente cerrado se reabre.
