# G79 — XAVC S sin la restricción de tarjeta (parche de `libObj`, probado en Unicorn y en el arnés)

Fecha 16-11-2026 (G75 Tarea 27), a petición del usuario («quítale la restricción de XAVC S») en lugar de emular una SDXC. Sin cámara ni CFW construido.

## 1. La restricción (VERIFICADO por bytes y MEDIDO)
- Tras montar la tarjeta, `ObjMedia` (`libObj+0x942156`) comprueba dos cosas:
  - si el sistema de ficheros no es exFAT (`[+0x2c8] ≠ 4`), pone el factor **`0x20000`** de su estado de inhibición (`SetInhStatus` `0x94a8a4`);
  - si es exFAT pero la clase de `Fsys` (`[+0x2a2]`) no es SDXC (`0x8402`, o `0x8004/0x8005`), también lo pone.
- Con ese factor, MOVIE en XAVC S da «Esta tarjeta de memoria no admite la grabación de películas XAVC S» (texto `0xf633`).
- MEDIDO con trazas: la llamada que lo pone es `lr = libObj+0x94219f` (`r1 = 0x20000`).
- La tabla de nombres del registro está desplazada una posición: el registro lo imprime como «`INH_IMPOSSIBLE_TYPE_FS_EXFAT`», aunque por su valor es `INH_IMPOSSIBLE_TYPE_FS`.
- Hallazgo de paso: con una imagen exFAT de 64 GB el arnés monta bien (`Fsys_MountAsync … OK 'A'`, tipo de FS 4). Aun así `Fsys` da a la tarjeta la clase `0x8400` en lugar de `0x8402`. Es la discrepancia que ya anotó g22 §5.39. No se siguió, a petición del usuario.

## 2. Parche (`scripts/gui/xavcs_card_patch.py`, solo `libObj.so`, 2 bytes)
- `mov r0, r4` en `0x94217e` (el destino de «no exFAT» y de «clase no SDXC») pasa a `b.n 0x942202`, la salida normal: el factor no se pone nunca.
- MP4 y AVCHD no cambian: con FAT32 ya graban de fábrica.
- **Prueba en Unicorn** (`tests/test_g79_xavcs_tarjeta.py`, sobre el `libObj` real):

  | Tarjeta | De fábrica | Con el parche |
  |---|---|---|
  | FAT32 SDHC | `0x20000` | nada |
  | exFAT SDXC | nada | nada |
  | exFAT con clase `0x8400` | `0x20000` | nada |

  Es idempotente y cambia solo 2 bytes.
- **Riesgo en la cámara (NO_VERIFICADO):** en FAT32 un fichero no puede pasar de 4 GB, unos 11 min de XAVC S a 50 Mbps. `libmpr` tiene división automática de contenido XAVC S (`AutoDivideXavcContentCmd`), pero no está comprobado que corte por tamaño. Si no corta, la grabación se detendría (o fallaría) al llegar a 4 GB. Con SDXC/exFAT nada cambia.

## 3. Arnés (MEDIDO, perfil `e2e45`, SD de fábrica del arnés: 4 GB FAT32; overlay `pkg-e2e-xavcs` = 120p de G70 + este parche)
- Tras montar ya no aparece el factor. XAVC S se elige (`0x1070087` = 9).
- MOVIE **entra en grabación**: «REC» en rojo con el icono de vídeo P (`docs/gui/img/g75/t27-xavcs-rec.png`). `libmpr` abre la base de datos XAVC S de la tarjeta (`PRIVATE\M4ROOT\MEDIAPRO.XML`, `CUEUP.XML`, `DISCMETA.XML`).
- **Siguiente bloqueo (E2E-15):** la interfaz se queda en «REC» sin contador y no responde a un segundo MOVIE. A av-cam no llega la EE de vídeo `0x4000` ni nada del codificador. El inicio de la grabación espera algo de av-cam o del codificador, que el arnés no emula (camino de captura, E2E-10).
