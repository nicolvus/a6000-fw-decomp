# NEEDS-HUMAN — elementos que requieren cámara o decisión humana

| Ítem | Sesión | Por qué requiere humano/cámara | Estado |
|---|---|---|---|
| Prueba P1: observar `0x83e9bd50` (G+0x808) en cambios de menú | S384/S51 | Requiere cámara física A6000 + autorización de usuario | BLOCKED |
| Prueba P7: prueba objetiva (hélice/LED) para obturador electrónico | S384/S51 | Requiere cámara física A6000 + autorización de usuario | BLOCKED |
| Pruebas P2–P8 del physical-test-plan | S384/S51 | Requieren cámara física A6000 + autorización de usuario | BLOCKED |
| Daemon REA para libObj.so | S380–S383 | Ghidra no analiza ELF PIE de 17 MB con dependencias faltantes (libInfraFsys.so, libmprctrl.so, etc.) | BLOCKED |
| Quién llama a RecordStill::Execute (0x90b248) | S381/S382 | 0 xrefs estáticos, 0 literales, llamada vía puntero de función en runtime | BLOCKED (necesita REA dinámico) |
| Quién registra callback de cola `0x40193` | S384 | 0 BL a `osal_reg_msg_queue_cb` .plt, llamada vía GOT indirecto | BLOCKED (necesita REA dinámico) |
| Escritores de `svr_num`/`VdNum` (S134) | S134 | No localizados estáticamente (relleno por copia de struct en runtime) | BLOCKED |

Ninguna prueba física ha sido ejecutada. S51 sigue A=NO, B=NO, C=NO sin cambios.
