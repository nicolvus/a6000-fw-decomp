# FM3 GPIO ↔ cortinillas (IC5700 MB9AF004B) — Darwin A6000 3.21

Fuentes: manuales en `references/manuals/` (ver MANIFEST.md); Darwin A6000
`0640_darwin/darwin_core.bin` sha256 `5f2be06d…0bf4` (base ROM `0x4200`);
scripts `scripts/schematic_pin_nets.py`, `scripts/fm3_gpio_literals.py`
(test: `python3 -I tests/test_fm3_gpio_literals.py`).

## 1. Bit-band → registro (VERIFICADO, manual FM3 cap.10 + mapa de registros)
GPIO base `0x40033000`: PFRx `+0x000`, PCRx `+0x100`, DDRx `+0x200`, PDIRx
`+0x300`, PDORx `+0x400` (4 bytes/puerto), EPFRnn `+0x600+4n`.
Alias = `0x42000000 + (reg-0x40000000)*32 + bit*4`; base de banco en Darwin:
PFR `0x42660000`, PCR `…62000`, DDR `…64000`, PDIR `…66000`, PDOR `…68000`, EPFR/ADE `…6a000/6c000`.

| Alias | Registro | Pin | Red (esquema A6000 hoja 6-11, CN4900) |
|---|---|---|---|
| `0x42668234` | PDOR4 b13 | P4D (SIN2_2) | **1ST_CURTAIN_MG** |
| `0x42668238` | PDOR4 b14 | P4E (SOT2_2) | **2ND_CURTAIN_MG** |
| `0x42668230` | PDOR4 b12 | P4C (SOT2_1) | CA_1ST_CURTAIN_START |
| `0x4266822C` | PDOR4 b11 | P4B (SIN2_1) | CA_RELEASE_LOCK_MSS |
| `0x4266811C` | PDOR2 b7 | P27/INT03 | (red no resuelta aún) |
| P50/P51/P52 | SIN3/SOT3/SCK3 | | CAM_SI_1 / CAM_SO_1 / CAM_SCK_1 (enlace con el ASIC principal → SIO3 CAIF) |
SHUTTER_PI y SHUTTER_ID llegan por pines ADC de IC5700 (hoja 6-11, borde inferior); SHUTTER_PI_ON por salida del borde superior.

Estado: pin↔red **VERIFICADO** por coincidencia de coordenadas del texto vectorial Y por inspección visual del recorte de la hoja (bolas H7, J7, G6, H6). **Idéntico en A6300** (hoja 25: mismas P4B–P4E).
Cadena de potencia (CN-1027 hoja 6-33, VERIFICADO visual): 1ST/2ND_CURTAIN_MG → puertas de FET (Q6832 MTM765200LBF «SHUTTER DRIVE») → bobinas 1C/2C del CN302 (10 pines), con SHUTTER_5.5V como alimentación; SHUTTER_PI_ON (Q6830) enciende el LED del fotointerruptor PI-A/PI-C/PI-E/PI-K, SHUTTER_ID del propio bloque. Cables: FP-2045 CN4900 pines 8–11 (SHUTTER_PI, 1ST, PI_ON, 2ND).

## 2. Descarte importante: P4D/P4E NO son serie (VERIFICADO estático)
- Tabla de configuración de pines Darwin: función `0x55D0` (modo por entradas de 4 bytes: byte0 = puerto[0:2] | modo<<3; byte1 = pull[0:1], nivel inicial[2:3]; bytes2-3 = máscara), invocada desde `0x57F2`/`0x5BC2`. Perfiles de 152 bytes en ROM `0x25BFC` + n·0x98 (n=0..5). Modo 1 = **salida GPIO** (DDR=1, PFR=0), modo 2 = entrada GPIO, 1 y 2 decodificados de `0x55FA…0x5640`; los modos 3,5,6,7,8,11 (otras rutinas `0x5400/0x5456/0x5512`, ADE/PFR) NO decodificados.
- En **los seis perfiles** el puerto 4 modo 1 incluye la máscara `0x6000` (P4D+P4E) con nivel inicial 0 (`par 0,0`): ambos arrancan como GPIO salida en bajo. P4B/P4C también salida.
- `0x56C6` (selección de reubicación MFS2: `PFR4` b13/b14 =1 solo en el caso 2) solo se llama con 0 y 0xFF (`0x1D07C`, `0x1D1D2`) → no activa SIN2_2/SOT2_2. MFS2 queda en reubicación _0 (P48/P49).

## 3. Escritores en tiempo de ejecución (A6000)
Todos usan `0x51C0` (`str r1,[r0,r2]`, r2=`0x42668000`, r0 = offset del alias):
| Función | Efecto | Llamadores |
|---|---|---|
| `0x20C90` | P4D=1 (1ª cortinilla) | 1f694 1f8a2 1f914 20154 |
| `0x20CB2` | P4D=0 | 20286 20300 2063e 206f2 209d4 20a00 20a8e 20af8 |
| `0x20D00` | P4E=1 (+`5C9E`,`210C0`,`5C88`) | 203c2 20448 20ac0 |
| `0x20CD4` | P4E=0 | 1f698 206f6 207c2 207ec |
Todas pasan por el filtro `0x20C74` = `0x1B080(0)&7 ∈ {1,2,3}` (si no, retorna sin escribir). Esto confirma que el control es **independiente del estado Silent** (coincide con el checkpoint) y que el comportamiento depende de un byte de «tipo de hardware» cuyo origen sigue NO VERIFICADO.
Escrituras de inicialización `0x56E8/0x56EC` son PFR (no PDOR) y sólo del caso 2 de `0x56C6`.

## 4. Pendiente
- Resolver origen del tipo (`0x1B080` → tabla `0x1B0E0`/`0x1B0E4+0x50`).
- Pines ADC de SHUTTER_PI / SHUTTER_ID (ADE/AN) y su lectura `ShutPIAdValue` (`0x1B422`).
- Red de P27 y de los demás alias del encargo.
