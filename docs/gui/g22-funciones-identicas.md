# G22-FUNCIONES — qué hace la cámara y en qué estado lo hace el arnés

**Estado (27-11-2026): inventario de funciones con su evidencia.** Una fila por función de la cámara
tal como la usa un usuario, con **cómo la emula el arnés**, **la medida que lo demuestra** y **el límite
real** que queda. No sustituye a las filas de [PENDIENTES](../PENDIENTES.md): las resume y enlaza.
Todo lo medido es con `qemu-system-arm` y el invitado real (`im.elf`, firmware 3.21 salvo donde se diga);
la cámara física **no** se ha usado en estas medidas.

Leyenda: **IGUAL** = el arnés produce el mismo efecto observable que la cámara; **EMULADO** = el efecto
se consigue, pero por una vía del anfitrión (no la cadena interna del firmware); **PARCIAL** = se ve o se
mide parte; **NO** = no emulado.

| # | Función de la cámara | Estado | Cómo lo hace el arnés | Medida que lo demuestra | Límite |
|---|---|---|---|---|---|
| 1 | Arrancar y pintar la OSD | IGUAL | `im.elf` con `LD_PRELOAD=sonyshim.so` sobre `qemu-system-arm -M virt`; la GPU la dibuja el invitado y el anfitrión copia el fotograma | `autoprueba.py`: primera pantalla en **114–137 s**, opacos **0,077–0,086**, 1363 listas ([evidencia](../../reports/evidence/g22-autoprueba-20261127/autoprueba.md)) | Arranque en frío lento y **cuelgue intermitente** «0 listas» (G22-CUELGUE) |
| 2 | Menú: abrir, navegar, cerrar | IGUAL | `openView(@V00E)` desde el shim al llegar la tecla MENÚ; cerrar vuelve a `view/STLREC` | Una pulsación = un cambio: opacos **0,08 → 1,00 → 0,08** ([G22-MENU](g22-arnes-ui-qemu.md)) | Navegar el menú a fondo dispara G22-CUELGUE |
| 3 | Dial de modos (Auto/P/A/S/M/Película/SCN) | IGUAL | Tecla `KEY_POS_MODE_DIAL 0x7025` con la posición; el firmware la lee y la vista pinta el modo | 7 posiciones con pantalla propia y rótulo; `REDIAL` reabre la vista con el modo del firmware ([G22-DIAL-POS](g22-dial-fn-rueda.md)) | **MR y panorámica** dan la misma pantalla: no se pueden distinguir (NO_VERIFICADO) |
| 4 | Rueda de control y dial trasero (Fn) | PARCIAL | Cada paso llega como `0x15070030`/`0x15070040` al `InputService` | G22-DIAL-FN: la rueda y el dial mueven el foco y los valores | No todos los destinos/asignaciones de la cámara están verificados |
| 5 | Zoom (óptico/clear image) | PARCIAL | `ObjMsg 0x7612/0x7614` emulado en `IssueCommandAsync` (`NOZOOM=1` lo apaga) | `docs/gui/g22-ajuste-zoom.md`: ranuras SET/ACT del `ModelCamera` y aviso `0x61` | El motor del zoom es del objetivo (BL); aquí es el efecto del modelo |
| 6 | Disparar una foto | EMULADO | El anfitrión compone el JPEG y lo deja en la SD; EXIF `ILCE-6000` | `autoprueba.py`: «1 foto nueva, modelo EXIF ILCE-6000» | La cadena interna del firmware (S1/S2 → `ModelStillRec` → `0x3003` a av-cam) sigue parada en la barrera del objetivo ([G85](g85-plan-trazas-camara-vm.md)) |
| 7 | Grabar vídeo | EMULADO | `captura.py` graba y al cerrar escribe el MP4 en la SD | `autoprueba.py`: «1 clip nuevo MP4», `PRIVATE/M4ROOT/CLIP/C0001.MP4` | Igual que 6: no es la cadena del firmware |
| 8 | Tarjeta SD: listar, bajar, importar, borrar, formatear | IGUAL | Imagen FAT32 real montada por el invitado (`sd_image.py`) y puntos `/sd/*` del anfitrión | `autoprueba.py`: 2 ficheros, descarga HTTP 200 (28 268 B), importar, borrar y formatear (`{"ok":true,"borrados":2}`) | El índice `AVF_INFO` vacío hace que el recuento del firmware no sea numérico (G22-REPRO) |
| 9 | Reproducción: abrir, miniaturas, ver una foto | NO (en curso) | La tecla sale del driver y, con `DESTKEYV=1`, llega a la vista (`dest=0x0c` → `libObj+0x10e8ec`) | La acción **4** no se ejecuta: `execAction` 0 disparos ([§7.3](g22-reproduccion-dispatch.md)); el reparto del bit 8 va a un `UtilityManager` con 8 oyentes y **ninguno es una vista** (§8) | Falta la traducción del id de entrada a evento de vista `0x1306cNNN` (G22-ACCION4) y el modelo de contenidos (G22-PBMEDIA); la vista ya se carga sola (G22-PBVISTA) |
| 10 | Iconos de batería, carga y jack USB | PARCIAL | Órdenes LIVE `B <0..100>` y `U <0|1>` al driver de entrada y a la respuesta emulada de CamMgr | Los mensajes llegan (`rcv_msg qid=0x7a0020`), `B 5`/`U 1` salen del configurador | **La pantalla no cambia** (0 px en 7 comparaciones): falta el modelo que consume `0x3001` ([G22-ESTADO-CAMARA](g22-estado-camara.md)) |
| 11 | Cargar por USB con la cámara encendida | IGUAL (dato de la cámara) | No se emula nada: la A6000 real **no carga** encendida | Medido en la cámara el 17-11-2026: «USB powered: false», estado 3, nivel 56 % ([G85](g85-plan-trazas-camara-vm.md)) | — |
| 12 | Conectarse a un PC (almacenamiento masivo / MTP) | NO | — | — | No emulado; el `viewUsbMassStorage`/`viewUsbMTP` existen en el registro de vistas pero no se abren |
| 13 | Sensor de imagen, AE y balance | EMULADO | Imagen fija, vídeo o cámara web por `sensor_web.py`; AE de escena constante a `ObjCamera` | `--sin-ae`/`--sin-sd` como controles; el fotograma sale del sensor emulado | El AE/AWB reales (BIONZ) no se ejecutan |
| 14 | Visor y sensor de ojo | NO | — | `KEY_TACT_FINDER`, `SLIKEY_EVF_OPEN/CLOSE` y `0x1000001x` no producen ningún cambio de `ObjDisplay` ([§5.18z](g22-arnes-ui-qemu.md)) | Es hardware del panel/visor, no una tecla del driver |
| 15 | Apagar y conservar el estado | IGUAL | `POST /salir` guarda `estado.zst` (118 MiB) y cierra QEMU; al arrancar se restaura en ≈ 7 s | `autoprueba.py`: cierre con código 0, estado de 118 MiB | `SIGSEGV` intermitente al cerrar **después** de guardar (G22-ARR3) y guardado de ≈ 8 s |
| 16 | Instalar/auditar un CFW antes de la cámara | IGUAL | `audita_cfw.py` (47 comprobaciones) y la misma auditoría **desde la página** (41 comprobaciones, AVISO en 39,2 s) | [G22-AUDIT-CFW](g22-auditoria-cfw.md) y `reports/evidence/g22-navegador-20261126/` | La puerta `contenedor.wbi_acoplamiento` solo distingue 3.39/3.40/3.41 (G22-CFW-ARRANQUE PARCIAL) |

## Lo que falta para el 100 %, en orden de valor

1. **Reproducción** (fila 9): dos eslabones localizados y en medida — el oyente del reparto multicast
   (`G22-OYENTE`) y la carga bajo demanda de `viewUnified3.so` (`G22-PBVISTA`).
2. **Batería/USB en pantalla** (fila 10): identificar el modelo que consume `0x3001` y el layout de av-cam.
3. **Estabilidad** (filas 1, 2 y 15): G22-CUELGUE (cuelgue al navegar), G22-CUELGUE-PROXY (interbloqueo
   de la OSAL emulada) y el `SIGSEGV` de cierre.
4. **Cadena interna de captura** (filas 6 y 7): la barrera del objetivo (BL/`CAM_INFO2` por DMAC8), que es
   lo que separa «foto del anfitrión» de «foto del firmware».
5. **USB a PC** (fila 12) y **visor** (fila 14), no emulados.

Cómo se comprueba todo esto de una vez: `.venv/bin/python scripts/gui/harness/autoprueba.py <work>
--perfil-dir <perfil> --puerto <puerto> --config <config.json>` (15 pasos, PASS/FAIL con informe en
Markdown y PNG por paso).
