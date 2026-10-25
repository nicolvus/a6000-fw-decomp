# S305 — corrección de la entrada y acceso al estado por GOT

Actualizado el 25-10-2026. **La pregunta original de S305 estaba superada por
[S303 rev.3](s303-ref-tree-43ff3200.md)** y no debía figurar como análisis de
`FUN_43858390` pendiente. Ver el [seguimiento de los cinco puntos](capture-static-followup-2026-10-25.md).

## Entradas y flujo comprobados

- `0x43858390` contiene `mov r3,sb`: es interior de **`0x43858338`**,
  a +`0x58`. No tiene el prólogo que se le atribuía.
- REA vuelve a resolver ese punto a `FUN_43858338`, con **3948 bytes**
  distribuidos en cuatro rangos: `43858338..4385834d`,
  `43858358..43858eab`, `438591d4..4385948b`,
  `43859520..43859669` (extremos incluidos).
- El supuesto dumper `0x438581e8` también tenía un sesgo +`0x58`;
  es interior de `0x43858190`. Las trece llamadas atribuidas al viejo
  caller quedan **rechazadas**, no reinterpretadas como un bucle.
- Los dos sitios directos al dumper real son `0x43859868` y
  `0x43859892`, en `0x43859710`; REA y S303 los documentan.
- El pseudocódigo completo de `0x43858338` se recuperó en esta sesión:
  selecciona una función de salida según su segundo argumento y condiciona
  salidas a bits del objeto de estado, incluidos +3/+6. Esto acredita
  lectura/diagnóstico, no un bucle de captura de trece iteraciones.

## GOT y productor indirecto del estado

El acceso `0x4378bb6c` a `0x4401f080 → 0x43ff3200` ya estaba probado
en S303. Se verifican además dos consumidores que indexan esa tabla:

1. `0x4378bfa0` registra **148** ternas `{clave, callback, contexto}`
   mediante `0x435614d0`. El servicio instalado en +`0x2c8` es
   **`Backup_reg_cb`**, demostrado por la relocación de `liro.ko`.
2. La fila **18** contiene `0x43f72d02`; ambas tablas de claves le
   asignan **`0x3000b`**. El callback es `0x43ae8b7a` (puntero Thumb
   `0x43ae8b7b`) y llama `memcpy(arg4,arg3,arg2)`.
3. `0x4378c1e4` pasa `tabla[indice]` a `0x435613b0`, servicio
   +`0x298` = **`Backup_read`**. Su núcleo en `backup.ko` obtiene
   `Data_GetSize` y copia al destino de kernel.
   Se ha localizado un productor por copia del objeto; tamaño y datos
   efectivos de la clave permanecen **NO_VERIFICADO**.

Por ello, «no hay escritores de +3/+6» solo describía los accesos directos
del barrido S300/S301. No excluía esta escritura por copia. No se afirma que
se haya observado un valor concreto de esos gates ni su efecto físico.

## Evidencia y reproducción

- [Verificador y datos](../../analysis/s380_libobj_map/followup_audit.py),
  [resultado](../../analysis/s380_libobj_map/followup_audit.json) y
  [regresiones](../../analysis/s380_libobj_map/tests/test_followup_audit.py).
- [REA: cuerpo real y cobertura](../../analysis/s380_libobj_map/followup_evidence/av-more.jsonl),
  [callback](../../analysis/s380_libobj_map/followup_evidence/av-backup.jsonl),
  [API instalada](../../analysis/s380_libobj_map/followup_evidence/liro-rea-elevated.jsonl),
  [Backup](../../analysis/s380_libobj_map/followup_evidence/backup-more-rea.jsonl).
- Ghidra histórico solo lectura para los consumidores que REA no reconoce:
  [export](../../analysis/s205_imager_s0_writer/staging_followup.json).
  La cobertura vacía de REA no prueba ausencia.

**ACEPTO** el acceso GOT y la procedencia indirecta localizada.
**RECHAZO** el caller `0x43858390` y las trece llamadas del informe anterior.
S305 deja de ser una tarea sobre una entrada inexistente. Permanecen abiertos
el contenido/tamaño efectivo de Backup y la semántica de los gates.
**VEREDICTO: CAMBIOS**.
