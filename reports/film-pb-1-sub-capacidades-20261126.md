# FILM-PB-1 / sub-capacidades — ¿hay una tabla por modelo/región que apague el vídeo y deje la foto?

26-11-2026. Estático puro (cámara no accesible, sin flashear). Objetos: `libmpr.so` (10.321.204 B),
`libObj.so` (17.436.172 B) y, como origen del dato, `libmprctrl.so` (221.700 B), todos de
`firmware/extracted/fw321/…/nflasha15_unpacked_unpacked/lib/`. Evidencia:
`reports/evidence/film-pb-1-sub-capacidades-20261126/`. Herramienta: `python3 /tmp/elfhelper.py`
(capstone, Thumb-2), `struct` sobre `.rodata/.data` y `references/pmca` para los volcados de NVRAM.

**Espacios (comprobado, ver `06-espacios-elf.txt`)** — `libmpr.so` mide `0x9D7D34`; 1.er LOAD
(`off 0x0 → VA 0x0`, VA == offset) cubre `.text 0x120228-0x7A3E83` y `.rodata 0x7A3E90-0x95674F`;
2.º LOAD (`off 0x9BB1C8 → VA 0x9C31C8`) cubre `.data VA 0x9C42E8-0x9DF807` (off `0x9BC2E8…`) y
`.bss VA 0x9DF808-0xADBB03`, **con +0x10000**: todo VA ≥ `0x9C31C8` tiene offset `VA-0x10000`.
`libObj.so`: `.text 0xE2B70-0xBC958C`, `.rodata 0xBC9598-0xE91FB2`, 2.º LOAD **+0x8000**.

## Resumen (≤20 líneas)

1. **No existe tabla por modelo:** `0x41030035` y `ILCE` aparecen **0 veces** en `libmpr.so` y `libObj.so`. El modelo entra como *cadena* (`MprCtrl::GetModelName`, NVRAM `0x3E0005`, 16 B → "ILCE-6000") y sólo se copia en el bloque `0xAD28F8` (`MprIf::SnapShotBootInit`, `0x712010`, strlen ≤ 12): **no indexa nada**.
2. La tabla de capacidades real es **una palabra de bits** en `libmpr.so`: `SupportContents` = **`0xAD28E4`**, que `MprCtrl::GetSupportContentTypes` (`libmprctrl 0x11DDC`) arma leyendo **6 bytes de EEPROM**; `MprCtrl::GetAviManagedContentTypes` (`0x11FC0`) repite el mismo mapa.
3. Mapa de bits, verificado por los extractores que usa el comando de debug (`0x3CD67C`…`0x3CD6AE`): **bit0 DCF · bit1 MP4 MPEG4 · bit2 MP4 AVC · bit3 AVCHD · bit4 M2PS · bit5 DVD**; bit7/8/9 existen sin nombre (7/8/9 se alimentan de `0x3C0408/0x3C0409/0x3C044D`).
4. Se inyecta con `MprIf::SetCreateParam_SupportContentTypes` (`0x71CB98` → `0x7122A0`) y **`MprIf::Create` la exige** (`0x71CC20`: si `0xAD3900==0` devuelve `0xA` y no hay MPR). La consulta es `IsSupport(bits)` = `0x3EC010` (`(bits & ~mask)==0`) con **78 llamadas**.
5. Quién la consulta: `AviMMgr` crea el acceso a vídeo (`MdvIf`, `0x60B4C4`) sólo si hay AVCHD/MP4/M2PS, fija banderas por tipo (`0x620C1E`, `0x620F64`), `ResumeMgr::BackupWrite` numera por tipo (`0x75F100`) y el acsr MP4 ordena por tipo (`0x6820DC`).
6. **Valor medido en los 30 volcados**: `mask = 0x30D` = DCF + MP4 AVC + AVCHD + bit8 + bit9. El bit de AVCHD está **a 1**: esta cámara **no** está configurada «sin vídeo».
7. Nadie escribe esos 6 ids (sólo `BackupLib::GetEepData`): son de fábrica. El id que selecciona la capacidad es la EEPROM, **no** el modelo; `0x3E0005` dice `"ILCE-6000"` en los 30 volcados (coincide con el modelo real).
8. En `libObj.so` no hay tabla por modelo: el equivalente es `IMCFG.funcInfo` (DVD/PCApp/USBHost/DemoMovie…, cadenas `0xBCF70A-0xBD0599`, leído por `Backup_read(%08X)`) y `DefInh/INH_FEATURE_*` (factores de medio/temperatura). Ninguno tiene flag «no reproducir película». `ModelCautionConfig.so` (6.616 B, `.data`=4 B) no aporta tablas.
9. **Corrección colateral:** `TvSystem` de esta cámara es **0 = NTSC** (`0x010704FD=1` → tabla `{1,0}` en `libmprctrl 0x2180C`), no PAL; `AviMMgr::isSupportContent` (`0x61A8F0`) **acepta** los clips `30000/1001`. La hipótesis PAL de [causa-sistema-tv](film-pb-1-causa-sistema-tv-20261127.md) queda contradicha por la NVRAM.
10. **Conclusión**: no hay vía modelo/región que desactive el vídeo dejando la foto. El fallo (`SetArea` 0, IFO que no carga) es de **área de memoria / carga**, no de capacidad.

## 1. Búsqueda de tabla por modelo: negativa, y por qué (objetivo 1)

| búsqueda | `libmpr.so` | `libObj.so` |
|---|---:|---:|
| literal `u32 0x41030035` (LE y BE) | 0 | 0 |
| ASCII `41030035` / `ILCE-6000` / `ILCE` | 0 | 0 |

`0x41030035` es el **modelo de la cabecera FDAT** del paquete de actualización
(`docs/capture/e26-r31…`, `docs/findings.md` E001), no un id de ejecución: tampoco aparece en los
`backup_flash.bin` (comprobado LE/BE en 3 volcados). El identificador de modelo que usa el
firmware en marcha es una **cadena**:

```
MprCtrl::GetModelName(char* buf)          libmprctrl 0x12390
  BackupLib::GetDataSize(0x003E0005)      -> tamaño de la propiedad (16 B)
  BackupLib::GetEepData(0x003E0005, n, buf)  -> "ILCE-6000"
```

y su único destino es el bloque de identidad de arranque:

```
MprIf::SnapShotBootInit(param)            libmpr 0x71CE64  (copia 0x10 B y llama 0x712010)
  0x712010: r6=[param+0] (char* modelo) ; bl 0x1EEF80 (strlen) ; cmp #0xC ; bhi -> error 5
            0x144FA4 (strcpy) destino = 0xAD28F8
            r3=[param+4] ; cmp #1 ; bhi -> error 5 ; str r3,[0xAD28F8+0x28]   ; TvSystem
```

Es decir: el modelo **no selecciona ninguna tabla**; sólo se guarda como texto (≤ 12 caracteres)
para mostrarlo/log. `libObj.so 0x7E6ED6-0x7E6EF8` es el llamador que arma ese `param` con
`GetTvSystem()` en `+0x18` y `GetModelName()` en `+0x14`.

## 2. La tabla que sí existe: `SupportContents` (0xAD28E4) desde 6 bytes de EEPROM

`MprCtrl::GetSupportContentTypes` (`libmprctrl 0x11DDC`, 376 B) — desensamblado completo en
`01-mprctrl-capacidades.dis.txt`:

| EEPROM | si el byte vale 1 | si no / error de lectura |
|---|---|---|
| `0x3C0368` | `mask = 9` (bit0 + **bit3**) | `mask = 1` (bit0) |
| `0x3C036C` | `mask |= 0x10` (bit4) | — |
| `0x3C036D` | `mask |= 0x04` (bit2) | — |
| `0x3C0408` | `mask |= 0x80` (bit7) | — |
| `0x3C0409` | `mask |= 0x100` (bit8) | — |
| `0x3C044D` | `mask |= 0x200` (bit9) | — |

`MprCtrl::GetAviManagedContentTypes` (`0x11FC0`) es **la misma tabla duplicada** (mismos 6 ids,
mismos bits): se pasa a `MprIf::SetAviManagedContentTypes(mediaId, mask)` en `libmprctrl 0x10AD6`.

Entrega y puerta en `libmpr.so`:

```
MprIf::SetCreateParam_SupportContentTypes(mask)    0x71CB98 -> 0x7122A0
    0x7122A0: 0x711B14(dest=0xAD28E4, src=&mask)   ; copia bit a bit (máscara de bits válidos)
              [0xAD28F4] = (mask & 8) ? 0 : 1      ; "Definition"
    luego   [0xAD3900] = 1                          ; gate de configuración completa
MprIf::SetCreateParam_SupportDefinition(def)       0x71CBAC -> 0x7122DC
    si def==0: [0xAD28E4] = 8 ; [0xAD28E4] |= 0xB5 ; [0xAD28F4] = def
MprIf::Create(...)                                 0x71CC20
    if ([0xAD3900] == 0) return 0xA                 ; sin modelo configurado no hay MPR
```

Consulta: `IsSupport(bits)` en `libmpr 0x3EC010`

```
3ec010  ldr r3,=0xAD28E4 ; ldr r3,[r3] ; bics.w r3,r0,r3 ; ite ne/eq -> 0/1
        return (bits & ~SupportContents) == 0        ; "¿están TODOS los bits pedidos?"
```

con **78** puntos de llamada en `.text` (`bits 0x1:5 · 0x2:1 · 0x4:9 · 0x8:10 · 0x10:6 · 0x80:4`
y el resto en cadenas de `adds r0,#N`).

## 3. Quién la consulta y qué habilita (objetivo 2)

- **`AviMMgr` crea el acceso de vídeo sólo si hay tipos de película** (`0x60B4C4`):
  `if (IsSupport(0x8) || IsSupport(0x2) || IsSupport(0x4) || IsSupport(0x80) || IsSupport(0x100))`
  `→ new MdvIf` (`0x60B4EE`); si no, salta a `0x60B53C`. Con `mask=0x30D` **sí entra**.
- **Banderas por tipo** (`0x620C1E`-`0x620C7E`): `[this+0x2F9] = IsSupport(8) && check`,
  `[+0x2FA] = IsSupport(0x10) && check`, `[+0x2FB] = (IsSupport(4)||IsSupport(2)) && check`,
  `[+0x2FC] = IsSupport(0x80) && check`.
- **Accesores por tipo** (`0x620EA4`-`0x620F8E`): crea y registra un objeto por cada bit soportado
  (`[+0x77C]`, `[+0x784]`, `[+0x788]`, `[+0x78C]`).
- **`ResumeMgr::BackupWrite`** (`0x75F100`) asigna el *slot* de reanudación recorriendo
  `1,2,4,8,0x10,0x80,0x100,0x200` con `IsSupport` — el índice depende de la máscara.
- **acsr MP4** (`0x6820DC`): elige el id de tipo (`8/0x10/6/1/0x100/0x200`) por `IsSupport`.
- `AviMMgr 0x61DCEC`: `if (!IsSupport(8)) goto 0x61DE4C` (rama sólo-AVCHD).
- Comando de depuración `MprIfMcmd::DebugDispInfo` (función `0x72AE0C`; bloque de impresión en
  `0x72AEC0`): imprime
  `l SupportContents : 0x%X` y luego `+ AVCHD / + MP4 AVC / + MP4 MPEG4 / + M2PS / + DCF / + DVD`.
  **Es la vía para leer la máscara en la cámara sin desmontar nada.**

**No hay flag «movie pb disable» en esta capa.** Los textos « Pb Disable!! ref) dsm get» (`0x85A51C`)
y «dsmTrickModeFlag» son anotaciones de ingeniero sin servicio ni cliente detrás
(ya barrido en [dsm-guarda-a](film-pb-1-sub-dsm-guarda-a-20261128.md) §7). La entrada a la
reproducción `MprIf::EnterMoviePb` (`libmpr 0x13DFF`) **no** llama a `0x3EC010` en ninguna parte
de su cuerpo: la capacidad no decide si se reproduce, decide qué se instancia.

## 4. ¿El id puede no coincidir con el modelo? (objetivo 3)

- Los 6 ids de capacidad **sólo se leen**: `0x3C0368/6C/6D/408/409/44D` aparecen en `libmprctrl`
  únicamente en los dos pools de literales de los getters (`0x11F1C` y `0x120F4`). No hay
  `SetEepData` ni escritura desde `/setting` en ninguna de las tres librerías.
- Quien sí podría desviarse es el **byte** `0x010704FD` (TvSystem) y la cadena `0x3E0005` (modelo),
  porque son datos de la NVRAM y los reescribe un *restore* de backup o la propia cámara al
  resetear ajustes. En los 30 volcados analizados **no** se desvían: modelo `"ILCE-6000"` y
  `0x010704FD=1` en todos.
- Escenario teórico de desajuste: si los 6 bytes quedaran a `0` (o el *backup* se restaurara de otro
  modelo), `mask = 0` ⇒ `MprIf::Create` devuelve `0xA` y **no arranca ni el vídeo ni la foto**
  (la puerta `0xAD3900` es común). No es un interruptor selectivo de vídeo.
- `IMCFG` (libObj, `[MCMD]`/`[IMCfg] m_funcInfo.*`, `0xBD039B`-`0xBD05EF`) es el otro registro de
  capacidades (SATA/BGM/MP3/DVD/PCApp/Map/USBHost/Simulate/PCRemote/**DemoMovie**/AirShot/
  LiveStreaming). Se lee con `Backup_read(%08X)`: los ids se imprimen en tiempo de ejecución y
  **NO_VERIFICADO** cuáles son; ninguno de sus campos es «reproducir película».
- `DefInh/INH_FEATURE_*` (libObj, `MWF::InhMgr`/`InhInfo`, `0xBD2AF9` «is inhibited!»): el catálogo
  de features inhibibles es `INH_FEATURE_ALL / _MOVREC / _MOVREC_START / _REC_TRIGGER`, y los
  factores son de medio, temperatura, corriente, HDMI/línea, rotación, etc. **No hay
  `INH_FEATURE` de reproducción de película**, y los factores se calculan en ejecución (no son un
  registro de NVRAM por modelo), así que no dependen del modelo ni de la región.

## 5. Conclusión (objetivo 4)

**No hay una vía por la que el modelo o la región desactiven el camino de vídeo dejando el de foto.**

1. No existe tabla indexada por modelo (`0x41030035` no aparece; el modelo es una cadena que sólo
   se copia en `0xAD28F8`).
2. La única tabla de capacidades (`0xAD28E4`) sale de 6 bytes de NVRAM y en esta unidad vale
   **`0x30D`**: DCF + **AVCHD** + **MP4 AVC** + bit8 + bit9. Está en la configuración «con vídeo».
3. La región sólo influye como `TvSystem` (`0xAD2920`), y su efecto se limita a **aceptar o rechazar
   cadencias** en `AviMMgr::isSupportContent` (`0x61A8F0`). Aquí `TvSystem = 0` (NTSC) y los clips
   son `30000/1001` ⇒ **se aceptan**. (Contradice la hipótesis PAL de
   [causa-sistema-tv](film-pb-1-causa-sistema-tv-20261127.md) §2; el valor estaba en la NVRAM, no
   en una suposición.)
4. Por tanto el síntoma (ningún IFO cargado, `StreamCache::SetArea` con tamaño 0) viene de la
   **tabla de buffers del modo / área de memoria**, no de un filtro de capacidad. Encaja con
   [dmm-area](film-pb-1-sub-dmm-area-20261126.md), con una corrección: allí `m_systemType`
   (`[0x9DEFE0]`, off `0x9CEFE0`) vale **0**, no 1, y no tiene relocación que lo cambie; su regla
   «VA = offset» sólo vale para el 1.er LOAD (`.data/.bss` van a `VA-0x10000`).

## 6. Qué se puede comprobar sin flashear

1. **Leer la máscara en la cámara**: comando de depuración MPR «dispinfo» (cadena
   `l SupportContents : 0x`) → debe imprimir `0x30D` y las seis líneas `+ AVCHD … + DVD`.
2. **Cadencia**: `AviMMgr::isSupportContent` acepta 24p y la familia de 60 Hz con `TvSystem=0`;
   si se sube un clip de 50p/25p debe rechazarse («Invalid TvSystem detect»). Sirve de control
   positivo del mapa de bits.
3. Con el arnés: `MprIfMcmd` permite llamar a `DebugDispInfo` sin cámara; y el `SetArea` pedido se
   ve en el anillo con `CMD(SET_AREA)`.

## 7. Límites

- Todo es estático; la lectura de los 6 bytes se ha hecho sobre los volcados
  (`analysis/camera-dumps/*/backup_flash.bin`, 30 y no 32: dos parejas son `backup_mem`), no en la
  cámara. **NO_VERIFICADO** que el `Backup_read` de ejecución devuelva lo mismo que el volcado.
- Los bits 7, 8 y 9 no tienen nombre en el comando de debug: su semántica es **INFERIDA** (tipos
  extra que también instancian accesor `[+0x788]/[+0x78C]`), no verificada.
- `IMCFG` y `DefInh/INH_FEATURE_*` quedan descritos por sus cadenas y sus funciones de acceso;
  falta fijar los ids EEPROM exactos del `IMCFG`.
- No se ha usado `mcp_rea` para binarios; todo con `python3 /tmp/elfhelper.py` + `struct`.

## Evidencia

`reports/evidence/film-pb-1-sub-capacidades-20261126/`

| fichero | contenido |
|---|---|
| `01-mprctrl-capacidades.dis.txt` | `GetTvSystem 0x11D74`, `GetSupportContentTypes 0x11DDC`, `GetAviManagedContentTypes 0x11FC0`, `GetModelName 0x12390` |
| `02-issupport-y-bits.dis.txt` | tabla `{1,0}` de TvSystem en `0x2180C`, `IsSupport 0x3EC010`, getter `0x3E52C0`, extractores de bit por tipo |
| `03-consumidores.dis.txt` | setters/puerta `0x71CB98/0x71CBAC/0x71CC20`, `AviMMgr 0x60B4C4 / 0x61DCEC / 0x620C1E / 0x620F64`, `ResumeMgr 0x75F100`, acsr MP4 `0x6820DC`, debug `0x72AEC0` |
| `04-identidad-arranque.dis.txt` | `SnapShotBootInit 0x71CE64 → 0x712010`, llamador `libObj 0x7E6ED6`, getter TvSystem `0x1EEFDC` |
| `05-nvram-capacidades.py` / `.txt` | máscara, 6 bytes, modelo y TvSystem en los 30 volcados |
| `06-espacios-elf.txt` | LOADs y secciones de `libmpr.so`, y en qué sección cae cada VA citado por el informe `dmm-area` |
