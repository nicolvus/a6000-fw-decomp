# Evidencia — FILM-PB-1 sub-auditoría `[CACHE]` / `[StillCache]` (26-11-2026)

Binario: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(fw 3.21, Thumb-2, primer LOAD `off 0x0 → VA 0x0`, por tanto **VA = offset de fichero**).

Reproducción de cualquier bloque:

```bash
python3 /tmp/elfhelper.py <libmpr.so> dis 0x7594e0 0x2d8
python3 /tmp/elfhelper.py <libmpr.so> calls 0x7594e0
```

| Fichero | Qué demuestra |
|---|---|
| `01-setarea-0x7594e0.txt` | `StreamCache::SetArea`: `cmp r4,sb` contra `[0xad4f68]`, log `BUFFER SIZE TOO SMALL : ` (`0x93e866`), `C1000002` |
| `02-minimo-nvram-0x3c0057.txt` | mínimo = `GetEepData(0x3c0057) << 10` → `[0xad4f68]`; flag `[0xad4f88]=1` |
| `03-startread-0x75dc8c.txt` | `StillCacheRead::StartRead`: alineación del offset, `dfs::seek` y traducción a `C3000101` |
| `04-seek-0x3b49b8.txt` | `dfs::File::Seek`: `0x3b49a2` (dev/handle/lista de abiertos), `[handle+0x1c]==2`, retorno `0x0E100001` |
| `05-vtable-slot-0x160.txt` | vtable `0x9d3f84`: slot `+0x160 = 0x9d40e4 = 0x003b49b9` |
| `06-codigos-cache.txt` | `0xC1000010` = literal `STREAMCACHE NOT SET AREA`; `0xC3000102` (read) frente a `0xC3000101` (seek) |
| `07-llamadores-setarea.txt` | las 10 llamadas a `SetArea` y el origen del tamaño (`[desc+0x138]`/`[desc+0x140]`) |
| `08-anillo-108-125.txt` | líneas 108-125 del anillo real (orden temporal de los dos fallos) |

## Cómo se ha obtenido

- Desensamblado: `/tmp/elfhelper.py` (Capstone, Thumb) y `.venv/bin/python3`.
- Límites de función: tabla `.ARM.exidx` del propio ELF (parseo puntual, no versionado).
- Tabla de nombres `INT_ERCD_*`: cadenas de `libmpr` en `0x7c8dcd`-`0x7c985e`; **no** hay tabla
  numérica que permita emparejar `0x0E100001` con un nombre (NO_VERIFICADO).
- No se ha usado `mcp_rea` para binarios ni se ha tocado la cámara.
