# S330 — Instancias del constructor `0x436f3fc0` (carril B)

22-10-2026. Carril B. Sesión S330. **Solo lectura estática de los blobs; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

¿Existe alguna instancia del constructor paramétrico `0x436f3fc0(obj, idx)` con `idx != 0`? Si no existe, las filas 1..33 de T1/T2/T3 no son alcanzables por código estático y la correspondencia fila↔modo queda sin soporte.

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| Solo hay **un** `BL` al constructor en todo el blob, en `0x436f2a8a` | **VERIFICADO** | Barrido de todos los `BL`/`BLX` (`0xF000…`/`0xD000…`): 1 coincidencia; re-verificado con capstone |
| El `idx` de esa llamada es una **constante 0** (`movs r1,#0` en `0x436f2a7e`) | **VERIFICADO** | Desensamblado del bloque |
| El constructor **no** aparece como literal de 32 bits (ni `…c0` ni `…c1`) ni en la vtable `0x43fce050` | **VERIFICADO** | 0 literales, 0 slots |
| La llamada vive en una **factoría singleton**: construye el objeto una vez, lo registra (`0x439a2794`) y lo publica en el slot `0x440245cc → 0x43e8d994` | **VERIFICADO** | Desensamblado `0x436f2a7c..0x436f2aaa` |
| La factoría no tiene `BL` directo: se invoca por tabla/init (no resuelto) | **NO_VERIFICADO** | 0 `BL` a `0x436f2a7c`; no se localiza el puntero |
| Las filas 1..33 de T1/T2/T3 **no se aplican** por esta vía | **INFERENCIA (alta)** | Un solo objeto, `obj+0x2b4 = 0` → se lee la fila 0 |
| Una factoría en runtime podría crear otra instancia | **NO_VERIFICADO** | Fuera del alcance estático |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. Barrido de llamadas

Se decodificaron **todos** los `BL`/`BLX` del blob por aritmética Thumb-2 (no por la lista de funciones de REA) y se filtró por destino `0x436f3fc0`:

- `0x436f2a8a` → `bl 0x436f3fc0` (único).
- `0` literales `c0 3f 6f 43` y `0` literales `c1 3f 6f 43`.
- Vtable `0x43fce050`: 45 entradas hasta el terminador en el slot 45; ninguna apunta al constructor.

## 2. La llamada: `idx` constante

```
0x436f2a7c: push {r4, r5, r6, lr}
0x436f2a7e: movs r1, #0          ; idx = 0
0x436f2a80: ldr r4, [pc, #0x28]
0x436f2a82: ldr r3, [pc, #0x2c]
0x436f2a84: add r4, pc
0x436f2a86: ldr r5, [r4, r3]     ; r5 = *(0x440245cc) = 0x43e8d994
0x436f2a88: mov r0, r5
0x436f2a8a: bl 0x436f3fc0        ; ctor(obj, 0)
0x436f2a8e: ldr r3, [pc, #0x24]
0x436f2a90: mov r0, r5
0x436f2a92: ldr r1, [r4, r3]
0x436f2a94: ldr r3, [pc, #0x20]
0x436f2a96: ldr r2, [r4, r3]
0x436f2a98: bl 0x439a2794        ; registro (módulo escalar)
0x436f2a9c: ldr r3, [pc, #0x1c]
0x436f2a9e: mov r1, r5
0x436f2aa0: ldr r0, [r4, r3]
0x436f2aa2: pop.w {r4, r5, r6, lr}
0x436f2aa6: b.w 0x43ad96ca       ; publica el singleton
```

El objeto se guarda en el slot `0x440245cc` (base GOT `0x44024540 + 0x8c`), que en el blob vale `0x43e8d994`. El constructor escribe `obj+0x2b4` con `r6 = r1` en `0x436f40fe` (`str.w r6, [r4, #0x2b4]`, bytes `c4 f8 b4 62`), confirmando S327.

## 3. Consecuencia

Un único objeto, construido con `idx = 0`, publicado como singleton → `obj+0x2b4 = 0` durante toda la vida del proceso:

- T1/T2/T3 solo aportan su **fila 0**, que corresponde al modo `0x0b` (24 MP) en la lista `0x43fee370`.
- Las diferencias por modo que S326 midió en T2 (incluida la huella de `0x4c`/`0x4d`) **no se aplican por esta vía**. Siguen siendo datos estáticos del binario, no comportamiento.

Esto refuerza el resultado de S327 y acota la interpretación de S326: la tabla T no es el mecanismo por el que el A7S cambia registros entre modos; ese papel lo cumple la matriz de 69 filas aplicada por el slot 40 (`0x436f3928`).

## Límites

- Solo estático: una factoría construida en runtime (por ejemplo desde un módulo cargado) podría instanciar el objeto con otro `idx`; no se ha demostrado que no exista.
- No se localiza el puntero/tabla que invoca `0x436f2a7c` (0 `BL` directos): su vía de entrada es NO_VERIFICADA.
- No se asigna semántica a las filas 1..33 ni al campo `+0x2b4`.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s330_ctor_instances/build_ctor_instances.py
.venv/bin/python analysis/s330_ctor_instances/verify_ctor_instances.py   # 21 comprobaciones, 0 fallos
.venv/bin/python -m unittest tests.test_s330_ctor_instances               # 8 tests
```

Artefactos: `analysis/s330_ctor_instances/ctor_instances.json`, `build_ctor_instances.py`, `verify_ctor_instances.py`, `tests/test_s330_ctor_instances.py`.
