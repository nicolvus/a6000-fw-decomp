# S310 — `0x43ad9704` es un thunk de llamada virtual, no un constructor de mensajes

Octava sesión del carril B. S308 concluyó que el código de modo Silent se pasa a
`0x43ad9704` y lo describió como «constructor/despachador de mensajes» (INFERENCIA). Al
desensamblar la función, esa descripción es **incorrecta en el mecanismo**: es un **thunk de
llamada virtual**.

## Qué es

`0x43ad96fa`:

```asm
43ad96fa  push {r3, lr}
43ad96fc  ldr  r3, [r0]          ; r3 = objeto
43ad96fe  ldr  r3, [r3, #0x64]   ; r3 = vtable[0x64]
43ad9700  blx  r3                ; llamada virtual
43ad9702  pop  {r3, pc}
```

Es el patrón `obj->vtable[slot](...)`. La familia contigua usa distintos slots:

| Entrada | Slot | Primeras instrucciones |
|---|---|---|
| `0x43ad96fa` | `0x64` | `push {r3,lr}` / `ldr r3,[r0]` / `ldr r3,[r3,#0x64]` |
| `0x43ad9712` | `0x94` | `ldr r0,[r0]` / `push {r3,lr}` / … |
| `0x43ad9720` | `0x58` | `ldr r0,[r0]` / … |
| `0x43ad972c` | `0x74` | `ldr r0,[r0]` / … |
| `0x43ad9744` | `0x40` | `ldr r0,[r0]` / … |
| `0x43ad9750` | `0x18` | `ldr r0,[r0]` / … |

`0x43ad9704` no carga el slot en sus primeros bytes: hace `ldr r0,[r0]` y **tail-call** a
`0x43ad9ada` (`b.w`), que es quien completa la llamada virtual.

## Consecuencia para el flujo silent

El modo (`0x4e/0x4f`) sale del selector, se guarda en `[sp+0x2c]` y se pasa como argumento a
una **llamada virtual** de un objeto cuyo tipo no se resuelve aquí. Por tanto:

- **No** hay un «mensaje» con campos identificables en este punto; hay un despacho dinámico.
- El consumidor real del modo depende del objeto/vtable y queda **NO_VERIFICADO**.
- El enlace silent → bloque de tiempos sigue sin demostrarse (S308).

## Límites

- No se resuelve el objeto (`r0`) ni su vtable; haría falta seguirlo hasta su construcción o
  identificar la clase por RTTI/vtable.
- La lectura de slots es directa de las instrucciones; la semántica de cada slot es
  desconocida.
- Sin firmware ejecutado, sin cámara, sin flasheo. S51 no cambia.

```sh
python3 analysis/s310_vtable_thunk/build_thunk.py
python3 analysis/s310_vtable_thunk/verify_thunk.py
python3 -m unittest tests.test_s310_vtable_thunk -v
```
