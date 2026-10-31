# E26-R35 — `serial_receiver`/`rx_packet` (`0xffff0876`) recibe varios paquetes por llamada (31-10-2026)

Responde si la rutina que `main` y `serial_entry` llaman para recibir un paquete serie
(`0xffff0876`, tratada como caja sustituible en [R20](e26-r20-bootrom-selector.md),
[R34](e26-r34-serial-entry-flags.md) y en la emulación de R21) puede procesar más de un paquete
antes de devolver el control. Sin hardware. Método: desensamblado completo de la función
(`0xffff0876`–`0xffff0bd2`, 279 instrucciones en dos tramos continuos separados por un pool de
literales en `0x944–0x99f`) y resolución de todos sus literales `ldr r,[pc,#imm]`. Test:
`tests/test_e26_r35_serial_receiver_multipaquete.py`.

Etiquetas: **BINARIO** · **CORRECCIÓN** (de una hipótesis propia de esta misma sesión, no de un
informe ya publicado).

## 1. Respuesta

**Sí.** La función tiene un bucle interno que vuelve a sincronizar y recibir otro paquete
(`0xffff089c`) tras procesar el anterior. Solo devuelve el control cuando se cumple una condición
de coincidencia de tipo entre el primer paquete recibido y uno posterior.

## 2. Mecanismo verificado por bytes

Variables locales relevantes (registros de alto nivel, `fp`/`sl`/`sb` del AAPCS): `fp` = «ya se
recibió un primer paquete» (arranca en 0, `0xffff0888`); `sl` = tipo del primer paquete; `sb` = 0
constante.

```
0x89c: [sincronismo de 60 flancos + recepción de un paquete de 7 B: tipo, valor/direccion, CRC8]
       -> si falla (timeout, CRC, tamaño): devuelve codigo de error (0x1001/0x2004/0x2005/0x3001...)
       -> si tiene exito: tipo = [sp+0x10]

si tipo == 0 (escritura):           motivo_de_main = valor; [0xc0010004] = 1;  ir a 0xb84
si tipo == 0xFFFF (salto):          [0xc000500c] = direccion; [0xc0010008] = 1; ir a 0xb84
si no (cualquier otro tipo):                                                   ir a 0xb84

0xb84: si fp == 0:
         sl = tipo; fp = 1
         ir a 0x89c                          ; SIEMPRE, sea cual sea el tipo del 1.er paquete
       si no (fp == 1):
         si sl != tipo: ir a 0x89c            ; tipo distinto del primero: sigue recibiendo
         si no (sl == tipo):                  ; coincide con el tipo del primero
           si [0xc0010004] != 0 o [0xc0010008] != 0: devuelve 0 (exito)
           si no: devuelve 0x2004
```

Confirmado por bytes:
- Los únicos dos saltos que llegan a `0x89c` dentro de toda la función son `0xffff0b90` y
  `0xffff0b96`, y ambos están dentro de este bloque — no hay otra entrada al bucle.
- Los tres `ldr r,[pc,#imm]` en `0xb80`, `0xb9a` y `0xbbc` resuelven a la **misma** palabra del
  pool de literales (desplazamiento de archivo `0xbfc`), con valor `0xc0010004`. Las tres
  instrucciones la usan con desplazamientos distintos: `0xb80` escribe en `[r,#4]` =
  `0xc0010008` (valor `1`), `0xbbc` escribe en `[r]` = `0xc0010004` (valor `1`), `0xb9a` lee
  ambas (`ldrd r1,r0,[r0]`) y las combina con `orrs`.
- `0xc0010004` y `0xc0010008` son exactamente las variables de `get_flag0()`/`get_flag1()`
  (`0xffff0bd4`/`0xffff0bda`, R23/R34): la **única** otra referencia a esa constante en todo el
  ROM está en el pool que usan esas dos rutinas (`0x948`). No hay una tercera copia.

## 3. Consecuencia

El bucle exige **al menos dos paquetes** para terminar (el primero siempre se sigue de otro
intento, sin excepción). La condición de salida es que el tipo del paquete actual coincida con el
del primero recibido en esa llamada; qué paquete concreto puso a `1` `[0xc0010004]` o
`[0xc0010008]` es independiente de cuál es el que cierra el bucle — basta con que **alguno** de
los paquetes de la secuencia haya sido de tipo `0` o `0xFFFF` para que el chequeo final acepte.
Un paquete de un tipo que no sea ni `0` ni `0xFFFF` no activa ninguno de los dos flags, pero
tampoco produce un error por sí solo: solo hace avanzar el bucle.

**Matiza una lectura propia de esta sesión** (no de un informe publicado): el chequeo final no
exige específicamente que se haya visto un paquete de salto (`0xFFFF`); exige `get_flag0() OR
get_flag1()`, y un paquete de escritura (`tipo 0`) sacia esa condición igual que uno de salto.

## 4. Alcance sobre `main`

`main` también llama a esta misma función (`0xffff115c`, documentado en R23 §1 como
`block_read_byte(&clave)`) para obtener la «clave» que luego comprueba con CRC
([R32](e26-r32-moderreg-valor-real.md)/[R33](e26-r33-veracidad-clave-nflasha0.md)). Por ser la
misma rutina, esa llamada también puede resolver varios paquetes internamente antes de devolver el
valor que `main` usa como clave — el valor no tiene por qué proceder de un único paquete recibido
en un solo intercambio. No se ha trazado si esto cambia algo de R32/R33 (ambas hablan de la clave
leída de `nflasha0`, no de la clave recibida por serie); se deja anotado como límite, no como
corrección.

## 5. Límites

- No se ha emulado la forma de onda para construir una secuencia real de varios paquetes
  (eso exigiría extender el modelo de R21 a tramas múltiples); la prueba es de control de flujo
  por bytes, no de ejecución.
- `[0xc0010004]`/`[0xc0010008]` son globales: no se ha comprobado si sobreviven entre llamadas
  distintas a `serial_entry` dentro del mismo arranque (estado persistente en SRAM) ni qué los
  reinicia; `serial_entry` solo llama a esta función una vez por invocación (R34), así que dentro
  de una misma invocación no hay contaminación cruzada, pero no se ha trazado qué pasa entre
  invocaciones sucesivas.
- No se ha determinado si el campo «tipo» admite valores distintos de `0`/`0xFFFF` sin que algún
  chequeo anterior (CRC, longitud) lo rechace primero; aquí solo se confirma que, si llega a
  `0xffff0b6c`, ningún código reacciona a un tipo «otro» aparte de no activar los flags.
