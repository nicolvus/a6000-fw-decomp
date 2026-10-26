# Registro de pruebas en cámara (solo software, USB)

Decisión del usuario (26-10-2026): la cámara no se abre; todo por software con la cámara conectada por USB.

## Protocolo (obligatorio)

1. **Antes de cada prueba**: backup completo con `scripts/senser_backup_dump.py` (NVRAM mem+flash, bootrom, status, info) en `analysis/camera-dumps/AAAAMMDD-HHMMSS-pre-TNN/`; se comprueba `SHA256SUMS`. Si la prueba toca RAM, volcado de las páginas implicadas antes y después.
2. **Cada prueba lleva número de registro `T001, T002…` (no se reutilizan), fecha-hora, el ID del plan (P*) y el backup que la precede.**
3. Orden del plan 2: `P0 → P20 → P18 → P16 → P13 → P14 → P15 → P17 → P19 → P21`. Se detiene si una prueba no es limpia (reinicio, obturador atascado) y se restaura el backup.
4. Disparo remoto por telnet/adb a cargo de Claude. Sin `CameraSequence` ni escrituras de drive_mode sin plan de recuperación.
5. Cada fila se actualiza en el mismo commit que su resultado; `PENDIENTES.md` se actualiza al cerrar.

## Registro

| N.º | Fecha-hora | Plan | Backup previo | Resultado |
|---|---|---|---|---|
| T001 | 26-10-2026 19:56 | P0 (backup) | — (referencia: `nvram-referencia-20261020-214913`) | Backup NVRAM + bootrom en `analysis/camera-dumps/20261026-195607-pre-T001-P0/`, `SHA256SUMS` OK. Bootrom idéntico a la referencia; flash/mem difieren en 15 propiedades (contadores/fechas, sin reinicio de ajustes). Cámara en modo normal tras el volcado (telnet y adb responden) |
| T002 | 26-10-2026 ~20:00 | preparación de P20: instalar `RemoteShutter.apk` (`ar.shutter`) | T001 | Instalación `Success` (escribe en `/data`). `am start` no arrancó: «current activity is being kept for the user»; puerto 8080 cerrado. Resuelto: con la app abierta por el usuario el puerto 8080 abre |
| T003 | 26-10-2026 19:58 | P20 (`dmesg`/`/log` en 3 disparos) | T001 (solo lectura; sin cambios de estado entre ambos salvo T002) | `analysis/camera-dumps/20261026-195829-T003-P20/`. 3 disparos remotos OK (`done`). `dmesg` idéntico antes y tras cada disparo (8 787 B, solo líneas de arranque/`cfg80211`; 0 trazas `[MODULO]`); `/log` vacío. **Las trazas de los módulos decodificados no salen por `dmesg`: P20 descartada como fuente.** Sin hacer: cambio de menú (necesita al usuario). Residuo mío en la cámara: `/tmp/d0.txt` (7 913 B, RAM-vfat) |
| T004 | 26-10-2026 20:01–20:20 | P18 (gates `+3/+6` de `0x83f72d00`) | T001 | `analysis/camera-dumps/20261026-200149-T004-P18/`. 32 B del objeto = **todo 0 en las 4 condiciones**: reposo con la app abierta (1 lectura), disparo remoto (70 lecturas cada 0,1 s, 7 s, `done 380645`), live view de la cámara sin la app (≈130 lecturas cada ~0,15 s en 20 s) y medio pulsado mantenido por el usuario durante esa ventana (sin sincronizar el instante exacto; el usuario indicó que la app no enfoca, así que se hizo en la pantalla normal). `G+0x808` = `0x120983c8`; `+0x210` = 0 en reposo. **Conclusión: `+3`/`+6` no cambian en ejecución en estas condiciones; refuerza «constantes de configuración». Límite: no se cubrieron otros tipos de obturador/drive** |
| T005 | 26-10-2026 20:10 | herramienta: `RemoteShutter.apk` v2 (botón SHUTTER, estado y tecla en pantalla, salir con MENU/atrás/izquierda, mata el proceso al salir) | T001 | Instalación `Success` (escribe en `/data`). Sin cambio en `/shoot`/`/status` |
