# E26-R70 — Cierre de los cabos abiertos de R65–R69: subida de P4C, máquina de `ip` y lectores de `G+0x42` (07-11-2026, estático)

Continúa [R69](e26-r69-revision-informes-efcs.md). Capstone sobre `darwin_core.bin` 3.21. Prueba: `tests/test_e26_r70_secuencias_darwin.py`.

## 1. Máquinas de secuencias de Darwin (VERIFICADO)

Darwin ejecuta secuencias de bytes con un intérprete común (`0x1e33e`/`0x1e234`). Cada máquina tiene un descriptor con `{tabla de acciones {id, función}, n.º de acciones, &índice, &acción, &puntero de secuencia}`. `0x1e150(descriptor, secuencia)` arranca una secuencia; un id ≥ n termina. Las funciones que arrancan secuencias cargan el descriptor y le restan un desplazamiento (`sub.w r1, r0, #k`): las secuencias están justo antes del descriptor.

| Descriptor | Estado | Acciones | Uso visto aquí |
|---|---|---|---|
| `0x28fdc` | `0x200036f8` | `0x28ff8`, 0x31 | secuencia de captura (`0x1961c`) |
| `0x296f0` | `0x20003748` | `0x2970c`, 0xf | secuencia posterior (`0x1e6ba`) |
| `0x28dd4` | `S` = `0x200036d8` | `0x28df0`, 0x32 | máquina de `S` |
| `0x2a094` | `0x20003908` | `0x2a0cc`, 0xa | máquina de `ip` (`0x237cc`) |

## 2. Cuándo sube P4C (cierra R67 §1, INFERENCIA → VERIFICADO)

1. **Preparación:** `0x1811a` (desde `0xce14` ← `0x6c78`) hace `S+0x54 |= 4`, `0x196b6`, **`0x17cee` → `0x16e7a`: P4C ← 1**, y después `0x1961c`, que arranca la secuencia de captura. Las cinco variantes (`0x28fdc − 0x54/0x44/0x34/0x22/0x12`, según `S+0x32`, `S+0x3c` y `S+0x44` bit 0) contienen la acción **0x1f** = `0x190fc`.
2. **Disparo (acción 0x1f, `0x190fc`):** llama a `0x18d6e` (arma A y B, R66 §3; con `S+0x32 = 0` usa `0x18fa0`) y **después** a `0x1e6ba`, que arranca la secuencia `0x296e6` = `0d 05 02 03 0a 04 06 09`.
3. **Rearme:** la acción 5 de esa secuencia (`0x1ea5c`) arranca en la máquina de `S` la secuencia `0x28dc5` = `30 0f 10 2f **14** 15 16 17 18 2f 19 1a 1b 1c`. Los pasos `0x30/0x10/0x2f` esperan condiciones de hardware (`[S+8]`, `0x1eff6(3)` cada 200 µs, `0x1f01a`) y `0x0f` vigila un plazo de 15 ms. La acción **0x14** = `0x175ea` → `0x16e7a`: **P4C ← 1 otra vez**.

**Consecuencia:** P4C está a 1 desde la preparación, antes de que se arme A. **A siempre produce un flanco de bajada**: en la rama larga (A inmediato) y en la corta (A retrasado). Da igual que el rearme ocurra antes o después de A. Si el rearme llegara antes de un A retrasado, P4C seguiría a 1 y A lo bajaría igualmente. Así que en Darwin no hay ningún motivo para que falte el flanco a 1/1000. Si falta, el fallo es físico, y eso es lo que mide E26-R66-RESET.

## 3. Máquina de `ip` (`0x237cc`) (cierra R69 §2 con límite)

`0x1a738(·, ip)` llama a `0x237cc`. Esta función copia el tiempo y le resta 4000 µs si la diferencia de tiempos supera 4000 µs y el byte `+0xa` vale 1. Después arranca la secuencia `00 01 09` de la máquina `0x2a094`. Sus acciones escriben los puertos **P4A (`0x228`), P42 (`0x208`), P05 (`0x14`), P35 (`0x194`) y P56 (`0x298`)**, y **ninguno de P4B–P4E** (VERIFICADO, prueba). Por tanto `ip` no toca las líneas de cortina ni la de `CA_1ST_CURTAIN_START`. El esquema no da nombre a esos cinco pines, así que su función concreta queda sin identificar. Es un límite, no un pendiente: no interviene en la pérdida.

## 4. Lectores de `G+0x42` a través de `0x182d8` (cierra R66 §4 con límite)

`0x182d8` devuelve `G+0x42` si `B+0xcd & 3 = 0`; hoy `B+0xcd = 0` (R66 §2). Hay cuatro llamadores: `0x22a30`, `0x22aa0`, `0x22abe` y `0x23a54`. Los elige `0x1a6ac` según el modo `[0x2000392e]`, y este lo llaman `0x183e2` ← `0x189f4`. Todos hacen lo mismo: **solo con la bandera `[0x20003932] & 3 = 0`** calculan un límite de la forma `constante − G+0x42`, con un suelo. Por ejemplo, `0x23a54` da `máx(52000 − G42, 41000)`; con la bandera a 1 no restan nada. Son plazos de decenas de ms, no la separación A–B. **Efecto de tocar `G+0x42`:** −1270 µs en `G+0x42` alargaría esos plazos 1270 µs, con efecto desconocido. Es otro motivo para no usar `G+0x42` como palanca, y E26-R66-B86 sigue descartado.

## 5. Precisión sobre la bajada de P4E

`0x207be` y `0x207e8` son acciones de una máquina de secuencias (punteros en `0x29e14/0x29e1c`), la que informes antiguos llaman «FSM ADC». `0x207be` baja P4E (`0x20cd4`) y espera `(X+0x31 − X+0x32)·100` µs. R66 §3 y R68 §2 («seguimiento ADC») y R69 §2 («paso temporizado de la lista») describen la misma llamada y no se contradicen.

## 6. Estado

* Inferencias de R67 §1 (cuándo sube P4C): **VERIFICADO**.
* Papel de `ip` y de `0x182d8`: **CERRADOS con límite**, sin efecto sobre A–B ni sobre las líneas de cortina.
* Candidato BIONZ `0x4383fa40` (R66 §3): **CERRADO como candidato débil**. No tiene escritor de `+0x1c` (E25-16) y la causa se mide con E26-R66-RESET.
* Sigue abierto: **E26-R66-RESET** (cámara y autorización), con el procedimiento de R69 §4. El criterio se refuerza: en Darwin, A siempre genera el flanco (§2), así que si no se ve el pulso en el BIONZ el fallo es físico.
