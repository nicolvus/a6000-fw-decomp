# S348 — el callback por entrada del ODL es un adaptador de `memcpy` (y el 13 es la longitud copiada)

> **Alcance:** estático. Solo se leen los `av-cam.bin` de los tres firmware. Sin firmware en
> ejecución, sin cámara, sin flasheo. Autoridad = **bytes**; los desensambladores solo se usan
> para leer, y el verificador re-decodifica a mano.

S347 dejó el campo `0x000d` como **tamaño del bloque (13 B)** con tres usos independientes y
una pregunta abierta: el consumidor A entrega al servicio importado, por cada id, la terna

```
{palabra_de_tabla (id | 13<<16), callback, item_i}      r0 = &companion[i]
```

¿Qué es ese `callback`? S348 lo identifica: **un adaptador de `memcpy`**.

## 1. El callback no es específico de datos: es `memcpy`

| Modelo | puntero (Thumb) | shim | veneer | implementación | usuarios |
|---|---|---|---|---|---|
| A7S fw3.20 | `0x43adb6e1` | `0x43adb6e0` | `0x43b7a028` | `0x439b3918` (ARM) | 1 (`0x43705702`) |
| A6000 fw3.21 | `0x43ada547` | `0x43ada546` | `0x43b7f878` | `0x439c5320` (ARM) | 1 (`0x436eb2e2`) |
| A6300 fw2.01 | `0x43b9199f` | `0x43b9199e` | `0x43c44c18` | `0x43a60384` (ARM) | 1 (`0x43734bee`) |

- **VERIFICADO:** cada puntero es **impar** (Thumb) y lo carga exactamente el `ldr`+`add pc`
  del bucle de la tabla (un solo usuario por modelo; 0 literales absolutos).
- **VERIFICADO:** el shim es **byte a byte idéntico** en los tres modelos (10 B + `pop.w`):

  ```
  10b5        push {r4,lr}
  0c46        mov  r4,r1
  1846        mov  r0,r3
  1146        mov  r1,r2
  2246        mov  r2,r4
  bde81040    pop.w {r4,lr}
  <b.w>       b   <veneer>
  ```

  Semántica: **`memcpy(dst=arg4, src=arg3, len=arg2)`** — el 4.º argumento es el destino, el
  3.º la fuente y el 2.º la **longitud**.
- **VERIFICADO:** el veneer es `bx pc` + `nop` (`7847c046`) seguido de un `b` **ARM**; el
  destino es código ARM. Las tres implementaciones comparten la huella de la `memcpy` clásica:

  ```
  e92d4001   push {r0,lr}
  e2522004   subs r2,r2,#4
  ba000020   blt  ...
  e210c003   ands ip,r0,#3
  ```

- **VERIFICADO:** la palabra de especificación de cada entrada lleva `13` en la mitad alta en
  los tres modelos (id en la baja), igual que la tabla de S347.

## 2. ¿Se copian los 13 B? (INFERENCIA ALTA)

El servicio importado recibe por entrada: el destino (`r0 = &companion[i]`), la palabra de
especificación, **la `memcpy`** y el item. La única longitud por entrada que se le entrega es
el `13` de la mitad alta de la palabra. Por tanto:

- **INFERENCIA ALTA:** el servicio copia **13 bytes** hacia el buffer del consumidor; el
  sentido del flujo es **entrada** (bloque recibido), no petición. Encaja con S347: el camino
  de carga reserva un bloque de 13 B y lo enlaza a la cabecera de 24 B del mensaje.
- **NO_VERIFICADO:** la llamada en sí (qué argumentos pasa el servicio al callback). Su cuerpo
  vive en la interfaz importada (slots `+0x2b0/+0x2c8/+0x2cc`), que se parchea al cargar el
  módulo; no hay implementación local.

## 3. Nota de compilación

La implementación de `memcpy` está en **ARM** y se alcanza por un veneer `bx pc`, mientras el
resto del módulo es Thumb-2. Es la firma de una **librería compilada aparte** (o de otro
toolchain) enlazada en el blob; no hay tabla de símbolos que la nombre, así que la
identificación es **por huella de instrucciones**.

## 4. Límites

- Solo lectura estática; sin runtime.
- La identificación de `memcpy` es por huella (4 palabras) y por la forma del bucle de copia;
  no hay símbolo.
- El callback es **uno solo por modelo y con un solo usuario**: no se puede comparar con otros
  servicios para ver longitudes alternativas en este binario.
- S51 (A/B/C) **no cambia**: aberración del objetivo, no obturador.

## 5. Reproducción

```sh
.venv/bin/python analysis/s348_odl_callback/build_odl_callback.py    # odl_callback.json
.venv/bin/python analysis/s348_odl_callback/verify_odl_callback.py   # 87 comprobaciones
.venv/bin/python -m unittest tests.test_s348_odl_callback             # 6 tests
.venv/bin/ruff check analysis/s348_odl_callback tests/test_s348_odl_callback.py
.venv/bin/mypy --ignore-missing-imports analysis/s348_odl_callback tests/test_s348_odl_callback.py
```

Artefactos: `analysis/s348_odl_callback/{build_odl_callback.py,verify_odl_callback.py,odl_callback.json}`
y `tests/test_s348_odl_callback.py`.
