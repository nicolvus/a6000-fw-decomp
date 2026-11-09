# G25 — ITU709(800%) y S-Log2 en la A6000 (libObj + núcleo, solo datos; 09-11-2026)

Continúa [G24](g24-menu-picture-profile-completo.md) §6. **Offline**: nada instalado ni probado en cámara. Herramientas: capstone, Unicorn y `llvm-objdump` (REA no estaba disponible en esta sesión; los hechos se comprueban contra bytes).

## 1. Qué significan los valores (VERIFICADO con bytes de la A7S)

`…PictureProfileGamma::convertValueIdToBackupValue` (A7S `cmn_view_processDataMgr.so 0x981ad`) traduce el valor del menú (igual que `f` de la A6300) al valor de app:
Movie 0→4, Still 1→5, Cine1–4 2–5→6–9, ITU709 6→3, **ITU709(800%) 7→10, S-Log2 8→11**. La `libObj` de la A7S (`App2Obj` `0x3d2120`, inversa `0x3d1888`) convierte la app a VALUEID:
**10 → `0x481` (ITU709(800%)), 11 → `0x480` (S-Log2)**; la `libObj` de la A6000 ya registra ambos nombres (`VALUEID_PP_GAMMA_ITU709_800/SLOG2`) y `CamMsgConv` los pasa a los selectores 10 y 11 (G17 §1).
La A7S no tiene S-Log3 (la UI llega a 8).

## 2. Parche de `libObj.so` (`patch_libobj_pp.patch_gamma`, 77 bytes)

El caso 7 de `pvt_ChangePictureProfileParamApp2Obj` (`0x4b4774`, 10 valores con `tbb`) se reescribe como búsqueda en una tabla de 12 halfwords (0x1b7…0x3a1, `0x481`, `0x480`) en el mismo espacio de 80 B;
la inversa (`Obj2App`, `0x4b4390`) salta a un trampolín de 38 B (`0x4b479c`) que añade `0x480→11` y `0x481→10` y conserva el resto. **Verificado con Unicorn** (`tests/test_g25_gamma_libobj.py`): los valores 0–9 dan lo mismo que antes,
10/11 dan `0x481`/`0x480`, 12 se rechaza, la inversa es exacta y otros casos (BG, Black Level, Phase) no cambian.

## 3. Núcleo (`pp_curves_patch.py`): sin tocar código

El código de la A6000 solo trata las gammas ≤ `0x1b` (switch de parámetros y lista de la rodilla). Parchear código en la imagen en ejecución (como las curvas) no es fiable: los parches se hacen por `/dev/mem` desde Linux
y el núcleo puede tener la caché de instrucciones sin invalidar. Solución: las curvas `0x1c` (S-Log2, selector 10) y `0x1d` (ITU709(800%), selector 11) de la A7S se instalan con los números **`0x14` y `0x15`**,
que el código ya trata igual que las demás gammas de cine (mismos casos del switch y de la rodilla) y cuyo hueco de curva de vídeo está vacío en la A6000. Se reescribe `+0x1014` con el número nuevo. Entradas 10/11 del selector → `(0x14,0x14)`, `(0x15,0x15)`.
**Verificado**: `tests/test_g25_gamma_curves.py` (curvas idénticas a la A7S salvo `+0x1012` y `+0x1014`; punteros vacíos antes) y emulación Unicorn de la selección de gamma (`analysis/gui/g18/emu_gamma.py`): selector 10 → `0x14`, 11 → `0x15`, el resto igual que en G18.
Diferencia con la A7S: ésta usa campos propios `cfg+0x4a8/+0x4aa` para el exposure-por-curva de 0x1c/0x1d; aquí valen los de 0x14/0x15 (`+0x3b6/+0x3b8`).

## 4. Menú

`build_pp_menu.py … --gamma-slog` (opt-in, junto con `libObj` parcheado): Gamma = Movie 4, Still 5, Cine1–4 6–9, ITU709 3, **ITU709(800%) 10, S-Log2 11** (orden de la A6300).

## 5. Límites y pendiente

- `analysis/gui/g25/` trae `pp_ram.sh`, `pp_curvas.bin` (28 900 B) y `manifest.json` regenerados (9 curvas, 23 escrituras; `av-cam.pp.bin` no se guarda, 11 MB). El script, con el busybox de la cámara bajo `qemu-arm` y `/dev/mem` simulado con un fichero, pasa la comprobación previa de originales y verifica cada escritura (`pp_ram: OK`); la memoria final no es comparable porque `dd` trunca un fichero regular (en `/dev/mem` real el truncado se ignora, G18 §3). Falta empaquetarlo en un CFW; instalar requiere autorización. Con el `libObj` parcheado y sin estas curvas, elegir las opciones nuevas no cambia la imagen.
- NO verificado: que el respaldo NVRAM de PP admita 10/11 (límites del `INFO_DATA_PICTUREPROFILE_BKUP`), que el campo del núcleo `+0x1012`=4 sea correcto para estas curvas, ni el resultado en cámara.
- **S-Log3**: sin fuente en la A7S. Pendiente (¿`av-cam` de la A6300?).
- **Color Mode B&W y S-Gamut/S-Gamut3(.Cine)**: faltan `PP_COLOR_*` en la `libObj` y matrices en el núcleo (datos distintos, no resueltos).
- **Reset**: evento sin determinar.
