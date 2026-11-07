# E26-R65 — La rama EFCS de Darwin: `t` = 0 al arrancar, µs y `S+0x48 = T − u16[G+0x42]` (07-11-2026, estático)

Capstone + Unicorn sobre `darwin_core.bin` 3.21 (base `0x4200`, SHA-256 `5f2be06d…`, idéntico al instalado según R58 §6) y bytes de `av-cam.bin`.
Continúa [R64](e26-r64-darwin-marca-efcs.md) (E26-R64-CORTINA) y [R62](e26-r62-auditoria-datos-estaticos-efcs.md) §4 (E26-R62-DARWIN-IP).
Prueba: `tests/test_e26_r65_darwin_efcs_tiempo.py` (emula `0x18a2e` y `0x19a12`).

Etiquetas: **VERIFICADO** (instrucciones/emulación) · **INFERENCIA**.

> **Corregido por [R66](e26-r66-bloques-darwin-en-nvram-1850000.md):** G es la propiedad NVRAM `0x1850000` (`G+0x42 = 3407`) y B es `0x1850001`, no BK4 `0x30102`. Las §4 (palanca `0x30102+0x8a`) y §5 («G no está en la NVRAM») quedan superadas. Auditoría [R68](e26-r68-auditoria-r65-r67.md): en §1–3 siguen vigentes los hechos de código; quedan **superadas** la última viñeta de §1, la última de §2 y la «lectura física» de §3 (con `G+0x42 = 3407` la rama `< −150` retrasa A, no causa el negro; R66 §3). Que `t` siga a 0 después del arranque es INFERENCIA (§1).

## 1. El tipo de mecanismo `t` arranca en 0 (VERIFICADO; cierra la duda de R64 §5)

* Tabla de carga dispersa `0x2a734`: `0x2a764 → 0x20002a00` (0x4d0 B, descompresión `0x4438`) y **`0x20002ed0`, 0xf8c B, puesta a cero `0x4494`** (`stmhs r1!, {r3–r6}` con ceros). `t = [0x20003cd8+0x20] = 0x20003cf8` cae dentro: vale **0 al arrancar**.
* Único escritor: `0x205e6` (órdenes BIONZ `0x62–0x65` → 1–4). Los 21 accesos con el literal `0x20003cd8` se revisaron: ninguno más escribe `+0x20`.
* Con `t = 0` y la marca de R63: EFCS on `S+0x31 = 0x02` → `0x196a2 = 0` (sin acciones de cortina delantera mecánica); EFCS off `0x40` → 1. **Es el comportamiento correcto**; la hipótesis A de R64 (Darwin trata EFCS como mecánico, `t` ∈ {1,2}) solo se daría si el BIONZ enviara `0x62`/`0x63`, cosa que no se vio en R59/R63.
* Consecuencia: con `t = 0`, EFCS on usa `r5 = 0` en `0x18d6e` y por tanto **`B+0x8a` / `B+0x86`, no `B+0x88`/`B+0x84`**. El efecto de `+0x88` con EFCS activado en R61/R64 (+0,14 ms) no lo explica el código: queda como deriva de escena (R64 §6 ya lo dejaba sin descartar).

## 2. Unidad de los tiempos: microsegundos (VERIFICADO; cierra la pregunta de R58 §13 y R64 §6)

* `0x19a12(Tv)`: `x = 0x1000 − Tv`; `((tabla[x & 0xff] + 0x800) · 1 000 000) >> (11 − x>>8)`. Emulado: Tv `0x1000` → 1 000 000, `0x1a00` (1/1024 s) → 976. `S+0x48` y todos los `s16` que se le suman (`B+0x84..0x8a`, `G+0x40/0x42`) están en **µs**.
* Los umbrales del bucle de espera (`50 000`, `60 000`, `25 000` en `0x18ee8–0x18f44`) cuadran con µs (patada de vigilancia cada 25 ms).
* Por tanto `+0x88 = 834` era +500 µs reales. Que la luz con EFCS desactivado subiera solo ≈0,16 ms (R64 §6) indica que la cortina no responde 1:1 al retardo o que la escena varió; no es un problema de unidad.

## 3. La rama EFCS de `0x18a2e`: `S+0x48 = T − u16[G+0x42]` (VERIFICADO por emulación)

`0x18d6e` calcula `S+0x48 = 0x19a12(Tv)` y lo sobrescribe con `0x18a2e(T)`:

| `S+0x31 & 3` | Compuerta | `S+0x48` |
|---|---|---|
| 0 (EFCS off con `t` = 0) | `S+0x60` bit 0 = 0 | `T + s16[G+0x40]` |
| ≠ 0 (EFCS on, `0x02`) | `S+0x60` bit 1 = 0 | **`T − u16[G+0x42]`** |

`G = 0x20000480` (código externo `0x10100`, 0x80 B). Después, con EFCS on (`r5 = 0`), `0x18d6e` usa `ip = S+0x3a` (sin el término `G+0x42` que sí suma EFCS off) y decide por `S+0x48`:

| `S+0x48` (µs) | Acción (EFCS on) |
|---|---|
| > 50 | `r8 = S+0x48 + s16[B+0x8a]` (≥ 1) → `0x19948(r8)` = `0x2041e` (evento con espera `r8`, estado 9) y `0x198bc` = `0x202f2(0)` (evento inmediato) |
| −150 … 50 | `0x19978` → `0x20544` (ambos casi simultáneos) |
| < −150 | `0x202f2(−(S+0x48 + s16[B+0x86]))` y `0x2041e(0)`: el evento de `0x2041e` sale **inmediatamente** y el otro se retrasa |

Lectura física (**INFERENCIA fuerte**): con cortina delantera electrónica, Darwin adelanta la segunda cortina mecánica en `u16[G+0x42]` para compensar su latencia de arranque; la exposición efectiva es `T − G42 + B8a − (latencia real)`. Si la latencia real de la cortina es menor que `G+0x42` (o el reinicio del sensor llega tarde respecto al evento inmediato), la pérdida es **constante en tiempo**, independiente de T, y para `T` ≲ la pérdida no llega luz:

* explica la **pérdida constante δ ≈ 1,27 ms de 1/250 a 1/750** (R57 §8) y el **negro desde 1/1000** (T = 1000 µs → `S+0x48 ≈ T − G42` cae en la rama `< −150` si `G42` ≳ 1,15 ms: la segunda cortina sale de inmediato);
* explica que **EFCS desactivado funcione**: las dos cortinas son mecánicas y comparten latencia; Darwin no resta `G+0x42` (lo suma a `ip`);
* el cambio de régimen entre 5 y 8 ms (E26-R62-UMBRAL) **no** sale de Darwin: en `0x18d6e` no hay ningún umbral en ese rango (solo `Tv ≥ 0x1400` = 1/16 s y los de §3). Queda en el BIONZ (`0x4383fa40`, R62 §2).

## 4. Las palancas para compensar, por orden (VERIFICADO el flujo; efecto NO MEDIDO)

1. **`B+0x8a` (BK4 `0x30102+0x8a`, hoy 234 µs)**: se suma solo en EFCS on y `S+0x48 > 50`. Subirlo ≈ +1270 µs (a ≈1500) debería devolver la exposición de 1/250–1/750; no arregla 1/1000+ mientras `S+0x48` caiga en la rama `< −150` (ahí manda `B+0x86`, hoy 0, que retrasa el otro evento).
2. **`u16[G+0x42]`**: es lo que produce el desplazamiento. No hay en la NVRAM ninguna propiedad con la forma de G (BK4 `0x30102` va a `B`, no a `G`). El BIONZ lo escribe con el registro `0x1850000`; su origen no se ha cerrado (§5).
3. **`S+0x60` bit 1**: anula la resta. `S` es la imagen del paquete `0x0c` desplazada 0x30 (`S+0x31 = pkt[1]`), así que `S+0x60` sería `pkt[0x30]`; el paquete observado por SWD (R59 §8) no llega tan lejos (INFERENCIA: lo rellena otro mensaje o queda a 0).

## 5. Origen de `G` en el BIONZ (REA + bytes; NO CERRADO)

* Tabla de bloques del BIONZ `0x43fe8c38` (4 registros de 0x24 B, a través de la GOT `0x44020c04`; leída en `0x436bc7d4` y `0x436bc804`): `{0x185, banderas, id, 0x436bc515, búfer, dir. Darwin, tamaño}`:

  | id | banderas | Darwin | tamaño | Bloque |
  |---|---|---|---|---|
  | `0x1850001` | `0xf` | `0x20280` | 0x180 | B |
  | `0x1850000` | `0xf` | `0x10100` | 0x80 | **G** |
  | `0x1850004` | `0x1f` | `0x20000500` | 0x100 | lectura |
  | `0x1850005` | `0x1f` | `0x30100` | 0x100 | lectura (BK4 `0x30100`) |

  `FUN_436bc804` busca por `(dir., tamaño)` y exige la bandera `0x10`: solo atiende las lecturas. `0x436bc514` (llamada indirecta) envía `len` bytes de un búfer que le pasa el llamador; el campo búfer de G está a 0, así que el origen lo pone quien lo invoca. REA no da llamadores directos (0 xrefs a `0x436bc514/5`).
* **Ninguna propiedad de la NVRAM tiene la forma de G:** no hay grupo 1 en `backup_flash.bin` (16 102 propiedades). El emparejamiento por índice de las tablas `0x43ff2fac`/`0x43ff345c` (IDs) ↔ `0x43ff3200` (punteros) da `0x3002d`, pero esa propiedad tiene 3 392 B y `+0x42 = 6`; **no se toma como origen** (emparejamiento sin verificar).
* `B+0x84..0x8a` = 17629 / 0 / 334 / 234 µs, iguales el 20-10 y el 05-11.
* Conclusión: el valor de `u16[G+0x42]` no sale del binario ni de los volcados. Hay dos maneras de obtenerlo: leer la memoria de Darwin `0x200004c2` (SWD de Darwin, `CN4906` 11/12, R52 §8), o capturar por el SWD del BIONZ el búfer del envío `0x1850000` al arrancar, como en R59 §8.

## 6. Qué queda cerrado y qué no

* **Cerrado (estático):** E26-R64-CORTINA (la decisión es `0x196a2` con `t = 0` → correcta para EFCS), la unidad de `+0x88` (µs), la fórmula completa de E26-R62-DARWIN-IP para EFCS on (`ip = S+0x3a`; `G+0x42` entra restando a `S+0x48`, no en `ip`).
* **Causa probable del fallo (INFERENCIA):** un desfase entre `G+0x42` (la latencia de la segunda cortina que Darwin supone) y la latencia real. Código, NVRAM y NAND son iguales que el 20-10 (R57 §12, R58 §9). Por tanto, o `G` ya no llega con el mismo valor (su origen no está en la NVRAM, §5), o la mecánica cambió al abrir la cámara (R58 §13).
* **Prueba barata que lo decide (con autorización; NVRAM, reversible con `scripts/e26_r61/bk4_variante.py` y restauración):** `0x30102+0x8a` de 234 a ≈1500 µs (+1270). Si a 1/250–1/750 la exposición con EFCS activado sube hasta la de EFCS desactivado, la rama del §3 queda demostrada como la que pierde la luz, y `B+0x8a` sirve de compensación. A 1/1000 o más rápido mandan además `B+0x86` y la rama `< −150`.
* **No cerrable sin cámara:** el valor vivo de `G+0x42`, la latencia real de la cortina y si `B` se copia 1:1 desde BK4 `0x30102` (R58 §13, todavía INFERENCIA).
