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
| — | — | — | — | (ninguna ejecutada; la cámara no estaba conectada el 26-10-2026) |
