# G109 — Una sola build con PP + Film + Extra fine + ISO (hasta 128000) (24-11-2026)

Continúa [G108](g108-bucle-iso-y-zonas.md). Petición del usuario: mezclar las cuatro funciones en un CFW con el ISO limitado a 128000. Nada instalado.

## 1. Por qué no cabían (MEDIDO)

**Núcleo (hueco G18).** PP llena `0x43faf290…0x43fb7981` (33 659 B cambiados de 34 546). Film (0x29c B) e ISO (cueva + tabla de EXIF) iban a las ranuras de curvas de PP y la build se rechazaba.
- Arreglo: `ZONA_G18 = 0x43fb7e80…0x43fb8ee0` (4 KB sin referencias en `huecos.py`, bytes vivos a 0; Silent usa `0x43fb7e00…+0x6a`). Con PP, Film e ISO ya no se rechazan: `F.bionz_pp` se construye y `test_g104_iso_avcam::test_cadena_cfw_film` lo comprueba.

**Partición `nflasha15` (nuevo).** La primera build mezclada se empaquetó, pero `viewUnified4.so` quedó truncado dentro de la imagen ext2 (`debugfs write: Could not allocate block`; `debugfs -f` devuelve 0 aunque falle) y `fwtool unpack` fallaba con «Not enough bytes returned».
- Sony deja **7 164 bloques de 1 KB libres**. El crecimiento neto de la mezcla era **8 320** (pp 5 776, film 5 046).
- Causa: cada pasada de `rueda_film._anade` copiaba la tabla de relocaciones (≈ 0,7 MB en `libObj` y `viewUnified2`). La mezcla hacía 3 pasadas en `libObj` y 3 en `viewUnified2`.
- Arreglo: la primera pasada deja holgura (256 entradas) y una marca; las siguientes amplían la tabla en el sitio y solo añaden palabras y código. `libObj` pasa de +2,1 MB a +0,75 MB y `viewUnified2` de +2,3 MB a +0,83 MB.

## 2. ISO hasta 128000
`iso_ui_patch.N_CFW = 4` (64000, 80000, 102400, 128000). Las demás filas siguen hechas pero no se muestran; `libObj`/núcleo mantienen los códigos hasta 409600. `test_g104_iso_filas::test_cfw_hasta_n_cfw`.

## 3. Build
`build/cfw_func393/todo` (`build_cfw_film.py --funciones pp,film,exfine,iso`, 3.93): `.dat` sha256 `fd4d853c0527a41fd782010b281808f190464899b1dfed8bce8512297c52c14e`. `audit_package_nflasha15 --darwin-v3 --sin-wbi --bionz-g22` = `todo_ok`; `fwtool unpack` completo; 152 tests de G25/G86/G97–G108 en verde.

**Efecto lateral:** el cambio de `_anade` altera el diseño de `libObj`, `viewUnified2/4/7` y `CautionConfig` de **todas** las builds. Las de G107/G108 (`pp`, `iso`, `film`…) y la `pp` instalada conservan el diseño anterior; si se quieren iguales hay que reconstruirlas.

**Sin verificar:** arranque en el arnés de la mezcla, el hueco G18 con PP en cámara, ISO con la NVRAM real, Film (botones pegados, sin causa), LUT/HLG/S&Q.

## 4. Resultado en cámara de `todo` y build `sin_iso` (24-11-2026)
- `todo` (`fd4d853c…`) instalada por USB (`--reflash`, «Done», versión 3.93): **la cámara se reinicia en bucle**. Causa sin aislar; sospechosos: Film/ISO en la cola de G18 junto a PP, o el nuevo `_anade` (cambia el diseño de todas las librerías).
- `sin_iso` = pp + film + exfine (`build/cfw_func393/sin_iso`, `.dat` sha256 `a99578e7d17d6fc96cb2b74fdbdbe5ab1a1ae240935f03a41b7fae600ec86243`), a petición del usuario. Auditoría `todo_ok` tras reconocer en `audit_package_nflasha15` cualquier mezcla de pp/film/iso. Sin instalar: la cámara sigue en bucle y falta recuperarla por SWD (R48).

## 5. `sin_iso` en la cámara (24-11-2026, dicho por el usuario)
- Instalada por USB tras recuperar por SWD (R48: el actualizador entró con la batería puesta; la primera escritura dio «updater response error» y tras un ciclo de energía terminó con «Done»). **Arranca** (el bucle de `todo` no era de PP/Film/Extra fine; queda entre ISO y su interacción con el resto).
- **Funciona todo menos el menú Fn:** con PP guardado, pasar de PP1 a PP2 en la franja Fn **reinicia** la cámara. El menú normal va bien.
- Sin causa. En el arnés no se puede reproducir (G102 §4: elegir un perfil no se queda y no sale orden a `av-cam`). Hipótesis por comprobar: nodos Fn de PP (SRNum `0x27+k`, raíz Fn de 38 a 48 hijos) combinados con el nodo Film de la franja.

