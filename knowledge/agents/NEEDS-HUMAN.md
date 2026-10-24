# NEEDS-HUMAN — elementos que requieren cámara o decisión humana

| Ítem | Sesión | Por qué requiere humano/cámara | Estado |
|---|---|---|---|
| Prueba P1: observar `0x83e9bd50` (G+0x808) en cambios de menú | S384/S51 | Requiere cámara física A6000 + autorización de usuario | BLOCKED |
| Prueba P7: prueba objetiva (hélice/LED) para obturador electrónico | S384/S51 | Requiere cámara física A6000 + autorización de usuario | BLOCKED |
| Pruebas P2–P8 del physical-test-plan | S384/S51 | Requieren cámara física A6000 + autorización de usuario | BLOCKED |
| Análisis REA de libObj.so | S380–S383 | La apertura funciona; la consulta exacta expiró a los 300 s. Sesión cerrada tras la auditoría | PENDIENTE LOCAL; no se ha demostrado que requiera humano |
| Quién llama a RecordStill::Execute (0x90b248) | S381/S382 | Dos sitios BL confirmados; los supuestos llamadores 0x7484dc y 0x755af8 eran falsos | PENDIENTE ESTÁTICO; no requiere humano por ahora |
| Registro y arranque de cola `0x40193` | S384 corregido | [Receptor e instalador recuperados](../../docs/capture/queue-40193-flow-2026-10-23.md): `0x4379e93c` instala `0x4381d16d` en descriptor `0x43ea048c`/campo+0x14=`0x46`. Falta consumidor de arranque, callback OSAL Linux y enlace Linux↔LIRO | PENDIENTE ESTÁTICO; no requiere humano por ahora |
| Escritores de `svr_num`/`VdNum` (S134) | S134 | No localizados estáticamente (relleno por copia de struct en runtime) | BLOCKED |

Ninguna prueba física ha sido ejecutada. S51 sigue A=NO, B=NO, C=NO sin cambios.
