# G67 — HLG1/2/3 como Gamma de Picture Profile, y estado de S-Log2/S-Log3 (15-11-2026)

Offline: nada instalado, ningún CFW construido, sin cámara. Parcial.

## 1. S-Log2 y S-Log3: reconciliado (sin trabajo nuevo)
| Pieza | Estado | Dónde |
|---|---|---|
| Curvas de gamma en el núcleo (S-Log2 = A7S `0x1c` → gamma `0x14`; S-Log3 = A6300 `0x1f` → `0x17`) | hecho, comparado byte a byte con la fuente | `pp_curves_patch.py` ([g25](g25-gamma-slog2-itu709-800.md), [g26](g26-slog3-color-mode-a6300.md)) |
| Nodo de menú Gamma + valores de app (S-Log2 = 11, S-Log3 = 2) | hecho, Unicorn | `patch_libobj_pp.patch_gamma`, `pp_menu_spec.GAMMA_COMPLETA` |
| Compensación por gamma en el núcleo para S-Log3 | hecho, Unicorn | `pp_slog3_core_patch.py` ([g32c](g32c-slog3-nucleo.md)) |
| Color Mode S-Gamut/S-Gamut3(.Cine) | hecho en datos (g26 §3, g27) | `patch_color`, `pp_color_patch.py` |
| Integración | CFW 3.81 construido, sin instalar | `knowledge/CURRENT.md` |
| ISP emulado (G23) | aplica gamma en la ventana en vivo | `scripts/gui/isp/` |
| Falta | efecto en imagen y elección de S-Log2/S-Log3 en cámara; ISO mínimo de S-Log3; Gamma Disp. Assist | PENDIENTES (G32-C, G36-A) |

## 2. HLG: no existe de fábrica
Búsqueda de `hlg` (sin distinguir mayúsculas) en `av-cam.bin` de la A6000, la A7S y la A6300 y en las `.so` extraídas de la A6000: solo coincidencias dentro de código/datos binarios (p. ej. `…hlg\0` en una cadena de bytes de instrucciones), ninguna cadena de usuario ni nombre `PP_GAMMA_HLG`. Ni la A6300 ni la A7S traen HLG (aparece con la α7R III, no disponible aquí). Hay que generar las curvas.

## 3. Tablas (`scripts/gui/pp_hlg_curves.py`, formato de la curva S-Log3)
Formato VERIFICADO: 2048 u16 (entrada = luz de escena lineal, salida = código de 10 bits) + cola de 26 B (`+0x1012` = 4, `+0x1014` = gamma). La curva S-Log3 de la A6300 resulta ser exactamente `S-Log3(i·0,00271)` (10 bits; error ≤ 3,4 códigos fuera de las ~30 primeras entradas): se reutiliza esa escala de entrada (gris 18 % en i ≈ 66).
- OETF ARIB STD-B67 / BT.2100 (a, b, c estándar), E = 0,265·x (blanco difuso 100 %; gris 18 % → 38 % de señal), código = 64 + 876·y.
- HLG1/2/3 = nivel máximo 87 / 95 / 100 % (valores del encargo; **sin fuente Sony verificable aquí**): por encima de y = 0,80 una rodilla lineal hasta el nivel. APROXIMADO: la rodilla real de Sony no está disponible; el suelo del negro (64) tampoco es el de la tabla S-Log3 (baja a 42 en i = 0).
- Gammas `0x1c`–`0x1e`, selectores 12–14 (el código de la A6000 las trata por la rama por defecto, como `0x17`).
Resultados: gris 18 % → 394; máximo 826 / 896 / 940.

## 4. Integración
- `pp_curves_patch.py … --hlg=1,2,3`: escribe curva, puntero y selector. **El hueco de G18 está lleno** (9 huecos: 8 curvas + cueva de color/tono): las curvas van a `HLG_REGION = 0x43F9C000`, dentro de una zona a cero de 2,3 MB (`0x43d620d9`), **no verificado que no se use en ejecución** (HLG-2).
- `patch_libobj_pp.patch_gamma(d, hlg=True)`: tablas de 15 valores (app 12–14 → VALUEID `0x586–0x588`, inventados por continuidad con `0x585`); el trampolín se desplaza 6 B (hay 12 libres).
- Menú: `pp_menu_spec.GAMMA_HLG`, `build_pp_menu.py --gamma-slog --hlg`: Gamma = 13 opciones → 2 filas de 6 y 7 (≤ 7, tope de G36) y **sigue en 6 páginas**: sin conflicto de lista.

## 5. Pruebas
`tests/test_g67_hlg.py` (13 casos): monotonía, extremos y niveles de las tres tablas, OETF en 1/12, 1 y 0, bloque con el formato exacto de S-Log3, bytes originales (región a cero, punteros vacíos), el parche sin `--hlg` no cambia, y Unicorn sobre `libObj` real: valores 0–11 iguales que antes, 12–14 ↔ `0x586–0x588`, 15 y `0x589` rechazados. Con `tests/test_g25_*` y `test_g26_*`: verde; ruff sin avisos nuevos.
Arnés (perfil y overlay propios, `--puerto 8667`): el overlay con `libObj`/`viewUnified2`/`.uxc` de HLG arranca en frío y abre el menú sin fallo; **no se llegó a la fila Gamma** (la navegación por teclas por la pestaña de cámara no avanzó de página en la sesión), así que **no hay captura de la opción**. qemu detenido y perfil borrado.
Un `git stash -q` accidental (cuatro segundos) se deshizo con `pop`; cambios ajenos intactos.

## 6. Límites
Sin cámara: no se sabe si el núcleo acepta selectores 12–14 ni si la curva se aplica; los niveles y la rodilla son aproximados; el ISP emulado no acepta curvas nuevas sin tocar `scripts/gui/isp/` (no comprobado).
