# E26-R34 — `serial_entry` emulado con todas las combinaciones de banderas (31-10-2026)

Emula `serial_entry` (`0xffff0fa0–0xffff1060`) sustituyendo `get_flag0`, `get_flag1` y
`serial_receiver` (`rx_packet`, `0x876`) por valores controlados, igual que `r20_bootrom_selector.py`
hace con `main`. Corrige el §2 de [R23](e26-r23-bootrom-flujo-completo.md), que describía un bucle
de reintento que los bytes no tienen. Sin hardware. Script:
`analysis/e26-recovery/r33_serial_entry_flags.py`. Test: `tests/test_e26_r34_serial_entry_flags.py`.

Etiquetas: **BINARIO** · **EMULACIÓN** (Unicorn, sustitución de llamadas) · **CORRECCIÓN**.

## 1. Árbol de decisión verificado (BINARIO)

```
svc = [0xc0010010+4]            ; copia de GPIO4.22, puesta por `main`
si svc != 0: rx_packet()  ---------------------------------------------┐
si no:                                                                 │
  g1 = get_flag1()               ; 1.ª lectura                        │
  si g1 == 1: SALTAR a la sección final (sin llamar a rx_packet)  ----│-> SECCION_FINAL
  si no:                                                               │
    g1b = get_flag1()            ; 2.ª lectura                        │
    si g1b != 0 (cualquier valor, no solo "ni 0 ni 1"): error 0x1001   │
    si no:                                                             │
      si get_flag0() != 0: error 0x1001   ; sentido opuesto al de `main`
      si no: rx_packet()  <-------------------------------------------┘

rx_packet() -> r4
  si r4 != 0:
    si r4 == 0x3001: r4 = 0x1001
    error_blink(r4)               ; SIEMPRE, sin reintento
  si no (r4 == 0, paquete aceptado):
    g1c = get_flag1()             ; 3.ª lectura posible
    si g1c != 0: SECCION_FINAL
    si no: error_blink(0x1001)    ; aceptado pero sin motivo fijado = error, no reintento

SECCION_FINAL:
  jump_ram()                      ; si retorna (no debería): error_blink(0x2005)
```

Confirmado por bytes: los dos únicos saltos hacia la llamada a `rx_packet` (`0xffff0ff2`) vienen de
`0xffff0fb8` (`svc != 0`) y `0xffff1032` (`get_flag0() == 0`); ningún salto llega allí desde el tramo
de error ni desde el de aceptación. **No hay bucle de reintento dentro de `serial_entry`.**

## 2. Lo que corrige a R23 §2

| R23 §2 (pseudocódigo original) | Bytes (este informe) |
|---|---|
| «`get_flag1() == 1`: ir a RECEPCION» | `get_flag1()==1` (1.ª lectura) **salta** la recepción; va directo a la sección final sin llamar a `rx_packet`. |
| «`get_flag1()` ni 0 ni 1: ir a SIN_RECEPCION» | Cualquier 2.ª lectura `!= 0` (incluido 1) es error `0x1001` directo; nunca llega a recibir. |
| «SIN_RECEPCION: si `get_flag1() != 0`: REGISTRO_MOTIVO; si no: trace(5); ir a RECEPCION (bucle)» | Tras aceptar un paquete (`rx_packet() == 0`), una 3.ª lectura de `get_flag1()`: `!=0` → sección final; `==0` → error `0x1001` **directo**. No hay bucle ni reintento. |
| «REGISTRO_MOTIVO: trace(9/10); trace(11); jump» | `trace(9)` pertenece al tramo de **error** (`0x1034`); `trace(10)`/`trace(11)` (= `0xa`/`0xb`) pertenecen al tramo de **salto** (`0x1044`/`0x104c`). Son dos tramos distintos, no una secuencia continua. |

El resto de R23 (el `get_flag0()!=0` → error `0x1001`, de sentido opuesto al de `main`) ya estaba
correcto y se confirma aquí.

## 3. Consecuencia

Con `MODEREG` bit 0 = 1 (R32) y sin recibir nada por serie, el único camino que no termina en el
LED de error (`0x1001`) dentro de `serial_entry` exige que `rx_packet()` devuelva 0 **y** que
`get_flag1()` quede a un valor distinto de 0 antes de volver a comprobarlo; eso solo lo puede poner
la propia rutina de recepción como efecto de haber procesado un paquete concreto (R9 §3: el único
que toca `[0xc0010008]`/el flag es el paquete de tipo salto, `0xFFFF`). Un intento que no deja esa
marca —paquete rechazado, error de sincronismo, o un paquete aceptado que no fija el motivo— acaba
en el mismo LED `0x1001`, sin una segunda oportunidad dentro de la misma llamada.

## 4. Límites

- `rx_packet`/`serial_receiver` (`0x876`) se trata como caja sustituible, igual que en R20/R33; su
  lógica interna (si puede procesar más de un paquete antes de devolver el control) ya está fuera
  del alcance de este informe y pertenece a R9/R21.
- No se ha emulado la forma de onda real (eso es R21); aquí solo se verifica la lógica de banderas
  de `serial_entry`, con los valores de retorno de sus llamadas fijados a mano.
- El límite de pasos del emulador (`MAX_STEPS`) es una protección del script, no una propiedad del
  BootROM: sirve para cortar si alguna combinación de prueba futura reintrodujera un bucle no
  previsto en este modelo.
