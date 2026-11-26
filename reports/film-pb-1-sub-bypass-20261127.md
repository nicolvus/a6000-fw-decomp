# FILM-PB-1 · Parche de `isSupportContent`: quién la llama, qué variante y qué pasa después

27-11-2026. Sólo estático (cámara no accesible). **Espacio: VA de ELF de `libmpr.so` 3.21**
(`9a74a3bb…4c30`); en `.text` la VA **es** el offset de fichero (`addr == off == 0x120228`).
Evidencia en `evidence/film-pb-1-sub-bypass-20261127/`: `guion-llamadores.txt`, `pipeline-cadencia.txt`,
`ensayo-{solo-tvsystem,todo-1}.txt`.

## 1. Veredicto

- **Alcance inocuo**: `AviMMgr::isSupportContent` tiene **un solo consumidor**, el manejador
  `PlayMovie` (`0x437BC0`, opcode `0x4000001D`); grabación, índice/BD, miniaturas y stills no pasan
  por ella.
- **Pero no desbloquea el síntoma por sí solo**: la guarda A (`0x447A1E`) se evalúa **antes**
  (`0x437BFA` vs `0x437C2C`) y puede seguir devolviendo `0x1A` por otra vía.
- **Si pasa**, nada aguas abajo comprueba la cadencia hasta el decodificador: el 30p llegaría al
  visor y se vería, con riesgo de conversión 30→50/25 Hz (tirones, desfase de audio).
- **Variante recomendada: sólo-TvSystem (2 bytes, 2 sitios).** Conserva el rechazo por miniatura.

## 2. Todos los llamadores de `0x61A8F0`

| Vía | Resultado del barrido |
|---|---|
| `bl`/`blx` inmediato a `0x61A8F0`/`0x61A8F1` | **0** en las `.so` del rootfs 3.21 (todas) |
| Literales | `0x61A8F1` sólo en el slot `[0x8E6E58+0x58] = 0x8E6EB0`; `0x8E6E58` en `0x60AC6C` (ctor `0x60AA98`), `0x61909C` (D1 `0x618E0D`) y el *addend* R_ARM_RELATIVE de `.rel.dyn` (`0x10052C`) |
| `ldr rX,[rY,#0x58] ; blx rX` en libmpr | 46 sitios; **uno solo** con un `AviMMgr` demostrado |
| Ese sitio | **`0x447F52`** dentro del envoltorio **`0x447F26`** (`0x447F48 ldr r4,[r5]`, `0x447F52 ldr r4,[r4,#0x58]`, `0x447F5A blx r4`; `r5` = `ent` del resolutor `0x447810` → `0x66D0C8` → `[AviMMgrIf+0x24]`) |
| Llamador del envoltorio | **`0x437C2C`**, único (`calls 0x447F26`); está en `PlayMovie` |

Otros 45 sitios (`0x2DE418`, `0x2DEF4E`, **`0x455A46`** = `[r8]` de otra interfaz, `0x40247E`,
`0x625C4C…`, `0x6E8CE4`…) leen el campo/`slot` de otras clases: ninguno tiene procedencia
`AviMMgr` (no existe en la librería el idiom `[x+0x24] → [+0x58]`, y la fachada `AviMMgrIf` **no**
replica este slot: `[0x9067A8+0x58] = 0x66A6D0`, que loguea `GetLastEntryIdSync`). **Rutas que
dependen de su resultado:** sólo la petición de reproducción de película. Grabación
(`FeaCore::RecStart` usa `0x1EEFDC` directamente), índice/BD (`MMgrMp4IfoAcsr::SetLoadInfo`
`0x67B4B8`), miniaturas (`GetPlayThumbnailInfo` `0x6E8430` es **llamado por** la guarda, no al
revés) y stills (`[0x8E6E58+0x60] = 0x603DBC`) no pasan por `0x61A8F0`. Además el envoltorio es
**fail-open**: si el resolutor falla devuelve 1 (`0x447F5E movs r0,#1`).

## 3. Parche mínimo: dos variantes

| | V-A «todo-1» | V-B «sólo-TvSystem» |
|---|---|---|
| Sitios | `0x61A8F0` | `0x61AA04` y `0x61AA30` |
| Antes → después | `84 b0 2d e9` → `01 20 70 47` (`movs r0,#1 ; bx lr`) | `19 d1` → `21 d1` y `03 d1` → `0b d1` (`bne 0x61AA4A`, Valid, en vez de `bne 0x61AA3A`, Invalid) |
| Bytes | 4 | **2** |
| Efecto | sale en la primera instrucción; nunca decide | los dos desajustes de sistema caen en la rama «Valid TvSystem detected» → `0x61AA4A` → `0x61AA18` → `0x61AA6C movs r0,#1` |
| Pierde | el `return 0` por `GetPlayThumbnailInfo` (`0x61A9E4` → `0x61AA5C` → `0x61AA68 mov r0,r6`, `r6=0` de `0x61A984`), las trazas y **la llamada** a `0x6E8430` | nada más que el rechazo por sistema; el resto del predicado y sus llamadas quedan igual |

**Menos arriesgada: V-B.** Motivos: (1) conserva el único otro `return 0`, que es una precondición
real (contenido sin miniatura/índice válido) y evita intentar reproducir lo que el visor no podrá
alimentar; (2) no elimina la llamada a `GetPlayThumbnailInfo`, cuyo efecto lateral (carga de info
en cachés del accesor) no está verificado; (3) es la mitad de bytes y deja trazas coherentes
(«Valid TvSystem», no «Unknown frameRate»); (4) los caminos que ya devolvían 1 no cambian.
Reversión trivial en ambos casos: 4 bytes, sin tocar vtable ni relocaciones.

`reports/evidence/film-pb-1-sub-bypass-20261127/parche_guarda.py --variante solo-tvsystem|todo-1`
genera la copia en `/tmp`, exige que el conjunto de bytes distintos sea exactamente el previsto,
valida el ELF resultante (ELF32 LE, ET_DYN, EM_ARM, 5 phdrs, 25 shdrs) y desensambla la zona.
Medido: V-B cambia `0x61AA04:19>21` y `0x61AA30:03>0b` (`cmp -l` = 2 líneas); V-A cambia los 4
bytes de `0x61A8F0`. Salidas: `4c314b14…` y `6fa1e23e…`. El `.so` de fábrica no se toca.

## 4. Si la guarda acepta el clip, ¿lo puede mostrar la cámara?

1. **Orden real**: `0x437BFA bl 0x447A1E` (guarda A) → si falla, log `" Pb Disable!! ref) dsm get"`
   y `0x1A` (`0x437C0A`) **sin consultar** `isSupportContent` (`0x437C2C`). Parchear B sólo sirve si
   A ya devuelve 1.
2. **Qué mira A** (ct=6): `[this+8]->vt+0x154()` ≠ 0 y `GetPlayMovieStatus(6)` `0x60945C`:
   `0x609674 bl 0x67B6E0` (GetInhInfo) y cierre `0x60967C ldr r5,[r7,#0x104]` /
   `0x609680 bic r5,r5,#0x40000000` / `0x609684 orr r5,r6` ⇒ `0` si algo no está a cero.
3. **GetInhInfo (`0x67B6E0`) sí compara sistema y clip**: `0x67B768 bl 0x1EEFDC` y, si
   `TvSystem==1` exige bandera 0 y si `TvSystem==0` exige 1 (`0x67B77E`–`0x67B78E`), marcando
   `0x4` en `out+0` (`0x67B790`). La bandera sale de `MMgrMp4IfoAcsr::SetLoadInfo` (`0x67B4B8`):
   `(1<<f)&0x2A9` → NTSC(0) (`0x67B5E2`, «TvSystem is NTSC»), `(1<<f)&0x154` → PAL(1) (`0x67B5CC`,
   «TvSystem is PAL»). **Matiz importante**: `GetPlayMovieStatus(6)` lee `out+4`, no `out+0`; ese
   bit `0x4` lo consume otro slot (`[0x8E6E58+0x64] = 0x6090E4`, que lee `[r7+0x100]` en
   `0x60930C`). Es decir: la doble comprobación existe, pero no en la misma puerta.
4. **Sistema ↔ código**: `MprIf::SetRecTvScanMode` (`0x72335E` ff, tabla `tbb` en `0x723356`)
   devuelve impares `{3,5,7,9}` con `TvSystem≠1` y pares `{2,4,6,8}` con `TvSystem==1` ⇒
   `TvSystem()==0 = NTSC`, `==1 = PAL`; 30p cae en impar y 25p en par (p. ej. 7/6, modo 12, relación NO_VERIFICADA). Encaja
   con la partición par/impar del [informe de causa](film-pb-1-causa-sistema-tv-20261127.md) y con
   que un 30p se rechace con la cámara en PAL.
5. **Arranque del motor**: tras A y B, `0x437C70` → `0x447DA8` → `[0x8E6E58+0xB4] = 0x608698`
   (`MovieReadStart`): **ninguna comprobación de cadencia**; sólo estado (`0x64C298`,
   `[this+0x7E4]`, `0x64C228`) y `0x31000007 ER_SEQUENCE`. Los demás usos de `0x1EEFDC` en la zona
   del reproductor (`0x2D9FB0`, `0x2E2722`, `0x2E2DBC`, `0x2EC970`) son tablas índice-sistema
   (`0x7F74B8`, `0x7F9464`, `0x7F9FC8/0x7F9FD0` = `[0,1]` y `[3,2]`, `0x7FC10C`) que eligen
   constantes; no rechazan contenido.
6. **Visor**: `DOWNCON: NTSC 60i60p/30p24p`, `PAL 50i50p/25p` (`docs/capture/s505-vef.md:17`) es
   el camino de señal de `av-cam.bin`; **NO_VERIFICADO** que la reproducción lo use.

**Respuesta**: con A en verde y V-B aplicada, el clip de 30p **debería** entrar al decodificador y
mostrarse; la salida del visor iría a 50 Hz (50i/25p) con conversión de cadencia: 30→25 cuadros
implica repetir/descartar (judder visible en paneos) y, si el audio no se re-muestrea, desfase
progresivo. Riesgo: reproducción a tirones y desincronía de audio, **no** corrupción ni escritura.
Si el decodificador rechaza el stream, el fallo saldrá con otro código o como motor parado (no
`0x1A`). En un sistema NTSC el mismo clip no habría pasado por aquí.

## 5. Correcciones y límites

- **Corrige** el [informe de causa](film-pb-1-causa-sistema-tv-20261127.md) §1: `Unknown frameRate
  %d` **no** devuelve 0; `0x61AA5A b 0x61AA18` → `0x61AA1C b 0x61AA6C movs r0,#1`. La cadena del
  otro rechazo es `isSupportContent : GetPlayThumbnailInfo [$x]` (`0x8E53DC`).
- **Corrige** «`PbStart 0x307F54`»: en libmpr esa VA cae en una función de log (`0x2FB510`, cadenas
  `"- category ["`); lo real es `MoviePlayerPbStart` (`0x7F9698`, xref `0x2E0F6C`) y
  `SetPbStartParam` (`0x7FEBF4`, xref `0x2F725C`); en libObj es un `BizPrintf` de la clase base.
- **NO_VERIFICADO**: valores en ejecución de `TvSystem()` y de `[info+0x124]`; que `SetLoadInfo`
  corra antes de la reproducción (sus llamadores `0x627C6C`, `0x628676` no se han trazado);
  identidad de los slots `+0x44`/`+0x124` como setter/getter de la bandera (inferida por uso); que
  el bit `0x4` no bloquee por la vía de `0x6090E4`; el uso de la conversión VEF en reproducción de
  fichero; y **ninguna medida en cámara** (ni de este parche ni del síntoma).
