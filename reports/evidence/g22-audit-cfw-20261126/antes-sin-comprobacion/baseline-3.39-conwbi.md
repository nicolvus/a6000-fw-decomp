# Auditoría CFW 3.39 — `833619df`

- Artefacto: `/home/nicolas/cfwbuild/out-conwbi/package-3.39/firmware_packed.dat` (dat)
- SHA-256: `833619dfffd23c4357f150dc0bc29fa330fe74abf7d2303aad81fe8f775f66b5`
- Fecha: 2026-11-26T03:15:44-0300
- Coste: 57.6 s
- Declaración: `ninguna`
- **Veredicto: AVISO**

| Etapa | Comprobación | Resultado | Evidencia | Detalle |
|---|---|---|---|---|
| 0 | `modo.rapido` | OK | INFERENCIA | solo contenedor y /USR (sin estructura ni arranque) |
| 1 | `contenedor.magia_dat` | OK | VERIFICADO | cabecera DAT de Sony (89 55 46 55 0d 0a 1a 0a) |
| 1 | `contenedor.orden_chunks` | OK | VERIFICADO | chunks: ['DATV', 'PROV', 'UDID', 'FDAT', 'DEND'] |
| 1 | `contenedor.sin_cola` | OK | VERIFICADO | 0 B tras DEND |
| 1 | `contenedor.dend_crc` | OK | VERIFICADO | almacenado 908273e7 / calculado 908273e7 |
| 1 | `contenedor.datv_prov` | OK | VERIFICADO | DATV=[256, 0] PROV=256 (isLens=0) |
| 1 | `contenedor.fdat_multiplo_1024` | OK | VERIFICADO | FDAT cifrado 212987904 B |
| 1 | `contenedor.bloques_suma` | OK | VERIFICADO | 207996 bloques; suma mala en [] |
| 1 | `contenedor.bloques_ultimo` | OK | VERIFICADO | bandera de último bloque mala en [] |
| 1 | `contenedor.bloques_longitud` | OK | VERIFICADO | longitudes anómalas en [] |
| 1 | `contenedor.bloques_padding` | OK | VERIFICADO | relleno del último bloque a 0xFF |
| 1 | `contenedor.descifrado_vs_fdat` | OK | VERIFICADO | 212155392 B frente a firmware_packed.fdat |
| 1 | `contenedor.fdat_magica` | OK | VERIFICADO | UDTRFIRM / 0100 |
| 1 | `contenedor.cabecera_crc` | OK | VERIFICADO | CRC-32 [12,512): a92d0975 / a92d0975 |
| 1 | `contenedor.version_valida` | OK | VERIFICADO | versión 3.39 (BCD) |
| 1 | `contenedor.modelo_a6000` | OK | VERIFICADO | modelo 0x41030035 (A6000 0x41030035) |
| 1 | `contenedor.region` | OK | VERIFICADO | región 0 |
| 1 | `contenedor.no_accesorio` | OK | VERIFICADO | fuera de la familia 0xA0xxxx |
| 1 | `contenedor.modo_luw` | OK | VERIFICADO | modo U / LUW N |
| 1 | `contenedor.filesystems` | OK | VERIFICADO | U@512+143360, P@512+0 |
| 1 | `contenedor.tar_dentro_fdat` | OK | VERIFICADO | tar@143872+212011520 de 212155392 B |
| 1 | `contenedor.tar_valido` | OK | VERIFICADO | 105 miembros, 1024 B de cola |
| 1 | `contenedor.updater_oficial` | OK | VERIFICADO | updater 143360 B sha256 b6d5175245c8fb26… (oficial 3.21 b6d5175245c8fb26…) |
| 1 | `contenedor.tar_sumas` | OK | VERIFICADO | 66 líneas verificadas; fallan [] |
| 1 | `contenedor.nflasha15_presente` | OK | VERIFICADO | 0700_part_image/dev/nflasha15 |
| 1 | `contenedor.nflasha15_tpzl` | OK | VERIFICADO | 2373 bloques de 65536 B; 84043264 B |
| 1 | `contenedor.nflasha15_cabe_en_particion` | OK | VERIFICADO | 84043264 B de 104857600 B |
| 1 | `contenedor.nflasha15_ldec` | OK | VERIFICADO | 0 violaciones: [] |
| 1 | `contenedor.nflasha15_bloque_0_igual_sony` | OK | VERIFICADO | bloque TPZL 0 idéntico al de Sony 3.21 (R55: recomponerlo colgó el LZP) |
| 1 | `contenedor.nflasha15_mismo_numero_bloques` | OK | VERIFICADO | 2373 bloques frente a 2373 de Sony |
| 2 | `usr.base_sony` | OK | VERIFICADO | Sony 3.21 extraído de /home/nicolas/h-cfwreal/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15 |
| 2 | `usr.ficheros_quitados` | OK | VERIFICADO | 0 quitados; sin justificar 0: [] |
| 2 | `usr.cambios_declarados` | AVISO | VERIFICADO | 1 cambiados (1 sin declarar), 0 nuevos (0 sin declarar) |
| 2 | `usr.declaraciones_coherentes` | OK | VERIFICADO | 0 parcheados declarados; no coinciden [] |

## /usr frente a Sony

- Añadidos (0): —
- Cambiados (1): `share/app/string_english.uxc`
- Quitados (0): —

## Límites

Emulación de la UI con un kernel ajeno y el shim: un OK aquí no demuestra el comportamiento en cámara.
Loader2/3, Darwin, el hardware y las tablas de recursos que no se declaren siguen siendo riesgo de cámara.
Los ids de Backup/NVRAM solo se comprueban si el CFW los declara; si no, quedan NO VERIFICADOS.
