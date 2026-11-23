# G99 — CFW 3.89 «Film»: receta nativa de RecipeLab + LUT 5×9×9 + curva por la gamma extendida (23-11-2026)

Petición: en el 3.88 instalado «no aplicaba todos los looks y en la mayoría casi no hay diferencia con la foto normal, no así con JPEGCAM o RecipeLab».
Hacerlo «estático» (elegido: receta nativa fija por look + LUT fija) y mezclar lo de JPEGCAM con lo de RecipeLab para obtener los looks más fieles.
Código: `scripts/lut/film_userland.py` (`RECIPELAB`, `RECETA_DE`, `REC_ID`, `receta_bytes`), `scripts/lut/userland/films.c` (`receta`, `lee_val`, `pon_val`);
tests `tests/test_g97_films.py` (11, Unicorn).

## 1. Diagnóstico (estático, sin cámara)
- **El diseño de los looks no es flojo.** Simulados sobre 8000 píxeles de las 33 ARW (JPEG Estándar → curva → LUT cuantizada), cada look cambia
  respecto a la foto normal entre **3,5 y 11,2 ΔE2000** de media: cine (Vision3, Eterna, Reala, F-64D, Verita) 10–11; Kodak y Fuji de foto 4–7;
  Fuji Sim 4,3–8,5. El hardware simulado queda a 0,4–1,4 ΔE del objetivo. Más de 5 ΔE se ve claramente.
- **Por tanto, si en la cámara apenas se nota, lo que falla es la vía del hardware**, que sigue sin verificar en la cámara:
  - la escala de la LUT: las unidades (ΔY 1/256, ΔC 0,75/256) salen del generador de software de `av-cam` (G71 §1b), no de una medida del ISP;
  - la curva por `c68[8]` (G98), verificada solo en Unicorn;
  - el transporte del blob userland → `av-cam` en cada cambio.
- **Las apps sí se ven porque usan ajustes nativos.** RecipeLab escribe estilo, saturación, contraste, nitidez, balance de blancos, EV y DRO en el Backup;
  JPEGCAM pone `Camera.Parameters` (estilo, matriz, Color Depth, desplazamiento de balance, DRO) y la curva por `setExtendedGammaTable`.
- **«LUT fija en `av-cam»` no cabe.** Los 38 looks necesitan ≥ 43 KB (1064 B de tabla + curva) y `av-cam` solo tiene 5,5 KB de ceros
  verificados (G72 §4). Las tablas siguen viajando desde el userland en el blob del Backup `0x150005`, con el reintento y la verificación del 3.88.
- **La saturación y el Color Depth nativos no se pueden modelar** (G23 §1, etapa 5: el firmware solo reenvía los valores a otro procesador).
  Por eso la LUT no se reajusta como residuo sobre la receta.

## 2. Qué hace el 3.89
- **Mezcla por look:**
  - **RecipeLab** pone la receta nativa de esa misma película: estilo, saturación, contraste, nitidez, modo de balance (AWB o kelvin), A-B, G-M,
    EV y DRO (24 recetas de su catálogo de 77; las películas que no tiene usan la de cine más cercana, «Classic Cinema»).
  - **JPEGCAM**: su vía de la curva (gamma extendida), que ya usa el 3.88, y su idea de combinar ajustes nativos con una tabla de color.
    Sus 24 recetas son estilos inventados, no películas, así que no se toman sus valores. La LUT 5×9×9 del CFW hace lo de su matriz y Color Depth, pero por tono.
  - **Encima**, la LUT 5×9×9 y la curva 1D de sosang, como en el 3.88.
- **Codificación idéntica a `Params.writes` de RecipeLab:**
  - G-M se guarda con el signo cambiado.
  - A-B y G-M también van a su ranura AWB (`0x107067f`/`0x107067e`) o K (`0x1070683`/`0x1070682`).
  - EV también va a `0x1070c7f`.
  - DRO se divide en principal (`0x1070104`: 0 Off, 1 Auto, Lv+1) y nivel (`0x1070775`).
  - El kelvin (`0x1070018` = K/100) solo se escribe con el modo K.
- **Tus ajustes se respetan:**
  - Al pasar de Off a un look, el hilo guarda en el blob (`+0x1800`) los 16 valores que toca la receta.
  - Al volver a Off los devuelve; entre looks se conserva la copia original.
  - El blob anota en `+10` el look cuya receta está puesta, así que tras reiniciar no la reescribe.
- **Escritura segura:** cada id se lee entero y solo se cambia su primer byte; un id que no exista no se toca.

**Evidencia (Unicorn):**
- Tests nuevos:
  - las recetas cubren los 38 looks y se codifican como RecipeLab (Portra 400 y Vision3 500T con kelvin);
  - Off → Portra 400 → Vision3 500T → Off deja exactamente los valores del usuario;
  - un arranque con la receta ya puesta no la reescribe.
- Los 8 tests de G98 siguen en verde; G86/G89/G92/G97: 64 tests en verde.

**CFW 3.89:**
- Fichero: `build/cfw_film389/pkg-3.89/package-3.89/firmware_packed.dat`, sha256 `f82c5d7bf1cd0b69caeabe977b96fb52337eaba6f5b06363f8e968304cc6edbe`.
- Auditoría `--darwin-v3 --sin-wbi --bionz-g22`: `todo_ok`.
- Sin instalar.

## 3. Límites
- **Cuándo se aplica la receta: NO_VERIFICADO.** El hilo escribe el Backup en el mismo proceso que la app de la cámara. RecipeLab lo hace con la app
  de cámara cerrada, y esta los relee al volver. Lo seguro es que se aplique al **apagar y encender**; si la app la relee antes (al salir del menú
  o cambiar de modo), no se ha visto.
- **El menú Estilo Creativo y el balance mostrarán los valores de la receta mientras haya un look.** Si los cambias a mano con un look puesto, al volver a
  Off se recuperan los de antes del primer look.
- **Receta + LUT van apiladas sin reajuste**, porque no hay modelo de la saturación nativa. Si la LUT funciona a escala completa en la cámara,
  el look puede pasarse de fuerte. Se corrige midiendo una foto real de cada look.
- Ids de RecipeLab tomados de su código. No se ha comprobado en este Backup que existan todos en la ILCE-6000; RecipeLab los usa en ella y los que no existen no se escriben.
- Las recetas con modo K fijan la temperatura (p. ej. Vision3 500T a 3200 K): es el look de RecipeLab, no un balance automático.
