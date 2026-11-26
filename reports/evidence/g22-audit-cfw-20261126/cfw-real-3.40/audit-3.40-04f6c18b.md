# Auditoría CFW 3.40 — `04f6c18b`

- Artefacto: `/home/nicolas/cfwbuild/out-sinwbi/package-3.40/firmware_packed.dat` (dat)
- SHA-256: `04f6c18b0b4b782f819aebfc6be9821a5ff911fedce3b25b7a9400bf95e6cdf9`
- Fecha: 2026-11-26T03:41:58-0300
- Coste: 315.7 s
- Declaración: `/home/nicolas/cfwbuild/out-sinwbi/package-3.40/declara.json`
- **Veredicto: OK**

| Etapa | Comprobación | Resultado | Evidencia | Detalle |
|---|---|---|---|---|
| 1 | `contenedor.magia_dat` | OK | VERIFICADO | cabecera DAT de Sony (89 55 46 55 0d 0a 1a 0a) |
| 1 | `contenedor.orden_chunks` | OK | VERIFICADO | chunks: ['DATV', 'PROV', 'UDID', 'FDAT', 'DEND'] |
| 1 | `contenedor.sin_cola` | OK | VERIFICADO | 0 B tras DEND |
| 1 | `contenedor.dend_crc` | OK | VERIFICADO | almacenado 6fb98be0 / calculado 6fb98be0 |
| 1 | `contenedor.datv_prov` | OK | VERIFICADO | DATV=[256, 0] PROV=256 (isLens=0) |
| 1 | `contenedor.fdat_multiplo_1024` | OK | VERIFICADO | FDAT cifrado 170528768 B |
| 1 | `contenedor.bloques_suma` | OK | VERIFICADO | 166532 bloques; suma mala en [] |
| 1 | `contenedor.bloques_ultimo` | OK | VERIFICADO | bandera de último bloque mala en [] |
| 1 | `contenedor.bloques_longitud` | OK | VERIFICADO | longitudes anómalas en [] |
| 1 | `contenedor.bloques_padding` | OK | VERIFICADO | relleno del último bloque a 0xFF |
| 1 | `contenedor.descifrado_vs_fdat` | OK | VERIFICADO | 169861632 B frente a firmware_packed.fdat |
| 1 | `contenedor.fdat_magica` | OK | VERIFICADO | UDTRFIRM / 0100 |
| 1 | `contenedor.cabecera_crc` | OK | VERIFICADO | CRC-32 [12,512): 8f91ac39 / 8f91ac39 |
| 1 | `contenedor.version_valida` | OK | VERIFICADO | versión 3.40 (BCD) |
| 1 | `contenedor.modelo_a6000` | OK | VERIFICADO | modelo 0x41030035 (A6000 0x41030035) |
| 1 | `contenedor.region` | OK | VERIFICADO | región 0 |
| 1 | `contenedor.no_accesorio` | OK | VERIFICADO | fuera de la familia 0xA0xxxx |
| 1 | `contenedor.modo_luw` | OK | VERIFICADO | modo U / LUW N |
| 1 | `contenedor.filesystems` | OK | VERIFICADO | U@512+143360, P@512+0 |
| 1 | `contenedor.tar_dentro_fdat` | OK | VERIFICADO | tar@143872+169717760 de 169861632 B |
| 1 | `contenedor.tar_valido` | OK | VERIFICADO | 104 miembros, 1024 B de cola |
| 1 | `contenedor.updater_oficial` | OK | VERIFICADO | updater 143360 B sha256 b6d5175245c8fb26… (oficial 3.21 b6d5175245c8fb26…) |
| 1 | `contenedor.tar_sumas` | OK | VERIFICADO | 65 líneas verificadas; fallan [] |
| 1 | `contenedor.nflasha15_presente` | OK | VERIFICADO | 0700_part_image/dev/nflasha15 |
| 1 | `contenedor.nflasha15_tpzl` | OK | VERIFICADO | 2373 bloques de 65536 B; 84043264 B |
| 1 | `contenedor.nflasha15_cabe_en_particion` | OK | VERIFICADO | 84043264 B de 104857600 B |
| 1 | `contenedor.nflasha15_ldec` | OK | VERIFICADO | 0 violaciones: [] |
| 1 | `contenedor.nflasha15_bloque_0_igual_sony` | OK | VERIFICADO | bloque TPZL 0 idéntico al de Sony 3.21 (R55: recomponerlo colgó el LZP) |
| 1 | `contenedor.nflasha15_mismo_numero_bloques` | OK | VERIFICADO | 2373 bloques frente a 2373 de Sony |
| 1 | `contenedor.wbi_acoplamiento` | OK | VERIFICADO | el paquete no incluye `dev/nflasha5`: sin instantánea WBI, Loader3 arranca en frío (G11 §11/§12) — no hay acoplamiento que romper |
| 2 | `usr.base_sony` | OK | VERIFICADO | Sony 3.21 extraído de /home/nicolas/h-cfwreal/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15 |
| 2 | `usr.ficheros_quitados` | OK | VERIFICADO | 0 quitados; sin justificar 0: [] |
| 2 | `usr.cambios_declarados` | OK | VERIFICADO | 1 cambiados (0 sin declarar), 0 nuevos (0 sin declarar) |
| 2 | `usr.declaraciones_coherentes` | OK | VERIFICADO | 1 parcheados declarados; no coinciden [] |
| 3 | `estructura.elf` | OK | VERIFICADO | 1 ficheros nuevos/cambiados; 0 con problemas: [] |
| 3 | `estructura.parches` | OK | VERIFICADO | 1 ficheros cambiados; 0 con bytes sin declarar: [] |
| 3 | `estructura.uxc` | OK | VERIFICADO | 25 ficheros de cadenas UXC verificados; 196 con otro formato; errores: [] |
| 3 | `estructura.uxc_formato` | NO VERIFICADO | NO_VERIFICADO | uxc no soportados por uxc_strings.py (no son tablas de cadenas): 196, 0 cambiados: ['share/app/IRShooting.uxc', 'share/app/LayoutMaster_Menu.uxc', 'share/app/color_cmn.uxc', 'share/app/lang_cmn.uxc'] |
| 3 | `estructura.recursos` | OK | VERIFICADO | 1 recursos declarados: [] |
| 3 | `estructura.nvram` | NO VERIFICADO | NO_VERIFICADO | el CFW no declara qué ids de Backup/NVRAM escribe: el arnés no puede demostrarlo |
| 4 | `arranque.artefactos` | OK | VERIFICADO | vmlinuz, base.cpio.gz y stage/cam/usr |
| 4 | `arranque.qemu_vivo` | OK | VERIFICADO | QEMU sigue vivo hasta el final |
| 4 | `arranque.im_elf` | OK | VERIFICADO | im.elf no salió con IMEXIT |
| 4 | `arranque.primera_pantalla` | OK | VERIFICADO | primera pantalla a los 124.1 s (más 0.0 s de espera de hueco) |
| 4 | `arranque.pantalla_no_negra` | OK | VERIFICADO | primera pantalla, menú y disparo con contenido |
| 4 | `arranque.menu_abre` | OK | VERIFICADO | MENU cambió la pantalla |
| 4 | `arranque.capturas` | OK | VERIFICADO | 3 PNG guardados |
| 4 | `arranque.menu_frente_sony` | OK | INFERENCIA | píxeles con contenido CFW/Sony: [87845, 87845]; distintos 0.0 |
| 4 | `arranque.comparacion_sony` | OK | INFERENCIA | {'comparable': True, 'fraccion_distinta': 0.0, 'no_fondo': [87845, 87845]} |

## /usr frente a Sony

- Añadidos (0): —
- Cambiados (1): `share/app/string_english.uxc`
- Quitados (0): —

## WBI (`nflasha5`) frente a `nflasha15`

- Miembro en el paquete: `ninguno` (magia WBI no)
- TOC del `nflasha15` movido respecto a Sony 3.21: False
- `nflasha5` idéntico al de Sony 3.21: None
- Regla (G11 §11): si el TOC se mueve, el WBI de Sony debe invalidarse (`--sin-wbi`); si no, la cámara reanuda la instantánea con los offsets y la caché del `/usr` de Sony.

## Arranque en el arnés

- Perfil `cfwreal`, puerto 8641, coste 141.6 s
- Capturas: disparo, menu, primera
- Comparación con Sony: {'comparable': True, 'fraccion_distinta': 0.0, 'no_fondo': [87845, 87845]}

## Límites

Emulación de la UI con un kernel ajeno y el shim: un OK aquí no demuestra el comportamiento en cámara.
Loader2/3, Darwin, el hardware y las tablas de recursos que no se declaren siguen siendo riesgo de cámara.
Los ids de Backup/NVRAM solo se comprueban si el CFW los declara; si no, quedan NO VERIFICADOS.
El WBI solo se compara con el de Sony 3.21 (miembro y TOC); el TOC interno de un WBI regenerado no se descomprime aquí.
