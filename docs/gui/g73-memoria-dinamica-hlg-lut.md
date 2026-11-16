# G73 — HLG y LUT con memoria dinámica y datos compactos (15-11-2026)

Cierra HLG-2 y LUT-C (g72): se retira `ZONA_VERIFICADA`; ya no se escribe en la zona viva. Solo ficheros del `.dat` (`av-cam`), sin CFW construido ni cámara. Código: `scripts/gui/avcam_dinamico.py`, `scripts/lut/lut_patch.py`, `scripts/gui/pp_curves_patch.py`; tests `tests/test_g67_hlg.py`, `tests/test_g71_lut.py`.

## 1. Asignador de `av-cam` (VERIFICADO en bytes)
- **`malloc(size)` = `0x43561164`**: trampolín `push {r3,lr}; … ldr r3,[r3,#0x14]; ldr.w r3,[r3,#0x1ac]; blx r3` (tabla de funciones del SO, `os+0x14`); r0 = tamaño, devuelve puntero o 0. **`free` = `0x43561180`** (slot `0x1b0`), que usa `operator delete` (`0x439b4230`). 23 llamadas; `0x436bbdb8`/`0x436bbdd0` hacen `malloc(0x100)` perezoso con celda global: el mismo patrón que las cuevas.
- No hay punto de arranque único conocido tras inicializar el montón (`0x437aa65c` es un constructor de paquete que se ejecuta en cada aplicación, no una vez), así que **la reserva es perezosa**: celda de 4 B a 0 = sin reservar; la primera ejecución reserva y guarda el puntero. Una sola reserva por arranque, sin `free`.

## 2. Reparto de memoria (solo los fragmentos verificados por g72)
| Zona | Uso |
|---|---|
| A `0x43BE3B28…0x43BE4330` (2056 B) | `+0x000` cueva HLG (celda, M de nivel, 58 nodos, 57 shifts, 3 colas de 26 B, código); `+0x400` cueva LUT (celda, desempaquetador, `f0`, `f1`) |
| B `0x43C1FF24…0x43C20C8C` (3432 B) | 3 tablas LUT de 1064 B (3 195 B con el sobrelectura de 3 B del lector) |
Ceros idénticos en fichero y en el volcado de RAM real (re-medido). `comprobar_zonas` y los tests exigen que cada escritura caiga en A o B, no se solape con otra, ni toque `0x43D620D9…0x43FA8F00` ni el hueco de G18 (`0x43FAF28C…0x43FB9000`: curvas, `pp_tone`, Color Chrome `0x43FB7C00`, Silent).

## 3. LUT (opción a, 21 bits)
Cada nodo (405, orden lógico `j·81+a·9+b`) = 3 deltas de 7 bits → 21 bits, **sin pérdida** (los datos ya son s7); 1064 B/tabla (3 tablas = 3192 B; sin empaquetar habrían cabido justo 4860 B, pero dejarían ~600 B para código HLG+LUT). La cueva (`f0` SA/r3 y `f1` MOV/r1, ganchos y bytes originales sin cambio) lee el ajuste; Off/fuera de rango = puntero original; LUT1…3 = `malloc(0x654)` (una vez) + desempaquetado con la `perm` del propio núcleo (`0x43BEF2AC`) cada vez que se elige. Unicorn: el búfer es **idéntico byte a byte** a `empaqueta_hw`; `malloc` se llama 1 vez; con `malloc` = 0 devuelve el puntero original (fábrica). Opción b (recurso de datos de flash por nombre): no buscada, innecesaria.

## 4. HLG (generado en ejecución)
Curva = 58 nodos u16 (1/16 de código) + 57 desplazamientos `s` (tramo de `2^s` entradas, 1…128, con quiebres forzados en la rodilla y en el recorte `E = 1`): `v = a + ((b−a)·j >> s)`, sin división; la rodilla de nivel se aplica a los nodos (`M` = 90/192/256 para 87/95/100 %). Error frente a la OETF real: **< 0,95 código** (se exige al construir el esquema) y ≤ 1 frente a `pp_hlg_curves.tabla` redondeada; la cueva Unicorn = réplica Python exacta. Datos totales: ~0,2 KB en vez de 12 KB.
- **Gancho**: `ldrb.w r3,[r3,#0x7ca]` en `0x43853ece` (selección de gamma `0x43853ec0`, primer uso de la gamma de PP). La cueva guarda `r0-r12,lr`, genera las 3 curvas (`malloc(0x304E)`), escribe `TAB+8g+4` (`0x44001404`, g = `0x1c…0x1e`) y los selectores 12–14 (`0x43CB56E6`) **solo si la reserva tuvo éxito**, y ejecuta la instrucción original.
- Fallo de `malloc` (= 0): no se escribe nada; selectores (0,0x0A) y punteros nulos originales ⇒ HLG1–3 no cambian la gamma (fábrica). Nunca se usa un puntero nulo.

## 5. Riesgos (NO verificados, sin cámara) → PENDIENTES HLG-3b
1. **Tamaño del montón del SO**: no medido (el SO está en el kernel; `malloc` es un servicio `os->0x1ac`). Se piden 12 366 B (HLG) + 1 620 B (LUT) una vez. Si falla, fábrica (probado en Unicorn).
2. **`0x44001404` y `0x43CB56E6` escribibles en ejecución**: son datos del bloque «ram» de la cabecera LIRO (G72) y el `pp_ram.sh` ya los escribe por `/dev/mem`, pero no se ha probado la escritura desde `av-cam`.
3. **Momento**: se asume que la selección de gamma `0x43853ec0` se ejecuta antes de que el núcleo lea el puntero de la curva; si otro consumidor lee antes, vería el puntero nulo (como sin parche).
4. **Búfer LUT**: el hardware/`memcpy` lee el búfer; se asume memoria normal (no DMA contiguo): si el SA exigiera memoria física contigua, habría que reservar con el asignador DMM.
