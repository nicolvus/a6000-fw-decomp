# NEEDS-HUMAN — elementos que requieren cámara o decisión humana

| Ítem | Sesión | Por qué requiere humano/cámara | Estado |
|---|---|---|---|
| Prueba P1: observar `0x83e9bd50` (G+0x808) en cambios de menú | S384/S51 | Requiere cámara física A6000 + autorización de usuario | BLOCKED |
| Prueba P7: prueba objetiva (hélice/LED) para obturador electrónico | S384/S51 | Requiere cámara física A6000 + autorización de usuario | BLOCKED |
| Pruebas P2–P8 del physical-test-plan | S384/S51 | Requieren cámara física A6000 + autorización de usuario | BLOCKED |
| Análisis REA de libObj.so | S380–S383 | La apertura funciona; la consulta exacta expiró a los 300 s. Sesión cerrada tras la auditoría | PENDIENTE LOCAL; no se ha demostrado que requiera humano |
| Quién llama a RecordStill::Execute (0x90b248) | S381/S382 | Dos sitios BL confirmados; los supuestos llamadores 0x7484dc y 0x755af8 eran falsos | PENDIENTE ESTÁTICO; no requiere humano por ahora |
| Quién registra callback de cola `0x40193` | S384 | Patrones históricos inválidos; falta análisis de flujo del ID y del callback | PENDIENTE ESTÁTICO; runtime solo si se agota esa vía |
| Escritores de `svr_num`/`VdNum` (S134) | S134 | No localizados estáticamente (relleno por copia de struct en runtime) | BLOCKED |

Ninguna prueba física ha sido ejecutada. S51 sigue A=NO, B=NO, C=NO sin cambios.
