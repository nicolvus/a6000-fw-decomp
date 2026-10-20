# Validación de la investigación de obturación — 15-10-2026

## Continuación E020

- ACEPTO el enlace estático EFCS → banco → selector de exposición, con las
  condiciones documentadas en docs/capture/efcs-capture-selector.md. Se resolvió
  la copia explícita de 0x92c bytes entre los bloques que E019 distinguía.
- ACEPTO la derivación del indicador selector==3 a 0xfc0a1b80 en el backend
  Mobius: constructor, setter de base, wrapper y escritura conservados en
  `efcs-dfe-*.json`. No es una medición física de la cámara.
- RECHAZO que el valor 2 ya pruebe obturación completamente electrónica:
  también cambia registros y temporización; no hay señales de cortinas ni
  lectura de imagen verificadas. SilentShutter +0x238 no está unido a esta ruta.
- 26 pruebas correctas. Ruff: All checks passed. Mypy: no issues found en
  cuatro archivos de src. Código Python y dependencias sin cambios.
- SHA-256 original verificado; las exportaciones de funciones consultadas
  presentan cero discrepancias de hash. Las consultas fallidas siguen visibles.
- REA conserva 61 evidencias del blob; se verificó el ID ev_2891468c… y su hash.
  Las consultas nuevas son exportaciones nativas de Ghidra, sin atribuirles IDs REA.
- No hay Git inicializado para crear un commit. Sin push, ejecución de firmware
  ni escritura a cámara. La comparación inicialmente preparada con A7S quedó
  descartada por el usuario el16-10-2026; se continúa exclusivamente con A6300.

VEREDICTO: CAMBIOS — investigación funcional y validación de SilentShutter pendientes.

## Continuación E018/E019

- 26 pruebas correctas; ruff limpio; mypy limpio en cuatro archivos de src.
  No se modificó código Python ni se añadieron dependencias.
- Hash de av-cam original correcto y .text del envoltorio ELF idéntica byte a byte.
- 13 asociaciones de punteros y nueve destinos periféricos P2S contrastados
  directamente con los bytes originales: correctos.
- 35 exports de funciones Ghidra tienen el mismo SHA-256 de origen; las cinco
  consultas finales terminaron decompiladas y el proyecto quedó guardado.
- Autoanálisis amplio alcanzó300s: TIMEOUT, cobertura parcial. No se presenta
  las más de37000 funciones registradas como cobertura completa.
- Tres consultas sin función se conservaron explícitas:4383a0ec,43790588,
  43abb770. La segunda se continuó desde entrada4378fef4. No ocultar estados
  function_not_created bajo un resultado general «todo decompilado».
- Corrección de dos candidatos ZAF interiores mediante vtable; retiradas tres
  definiciones provisionales sin prueba de entrada ABI:437b4ed2,436d6520,4378f4d0.
  Sus exports históricos permanecen y no deben usarse como funciones válidas.
- Referencias directas finales a campos Silent/EFCS solo muestran sus handlers
  de escritura; las copias indirectas y la cobertura parcial impiden concluir
  ausencia total de lectores. Se documentaron por separado los lectores EFCS.
- Asociación adicional comprobada: GOT44023598→43fe995c; lista de119 punteros
  con terminador cero, índice1→4401ca2c. Es el registro modificado por el selector
  de SetExposure y entregado al formateador P2S por la rama de aplicación.
- Revisión final de12 documentos:30 enlaces Markdown locales correctos.
  Todos los119 registros de la lista están dentro de la imagen. Último export
  de referencias:37690 funciones registradas; cobertura sigue parcial.
- No cámara, firmware ejecutado ni parche. Sin commit: git rev-parse confirma
  que no existe repositorio Git utilizable; sin push.

Informes: docs/capture/silent-imager-consumers.md y imager-exposure-p2s.md.

## Continuación SilentShutter E015–E017

- 26 pruebas correctas (7 nuevas LIRO); fallo inicial por módulo ausente antes
  de implementar. Ruff limpio; mypy limpio en cuatro archivos de src.
- CLI sobre av-cam.bin original: LIROv4 y 220 comandos, sin duplicados ni
  punteros fuera de imagen según los límites suministrados.
- Factory768e, CamMgr, tabla indexada Off/On, receptor30001 y tabla40e3
  contrastados estáticamente. No se ejecutó firmware.
- Proyecto Ghidra persistente guardado, ocho candidatos decompilados; export
  silent-liro-functions.json verifica SHA-256 de toda la memoria original.
- Integridad final: original av-cam y .text del envoltorio ELF idénticos byte
  por byte; tabla220, punteros Silent/EFCS y proyecto existente verificados.
  Enlaces locales de los documentos principales: sin roturas.
- Dos intentos iniciales del script fallaron por conflicto de contexto; se
  corrigió la preparación y se verificó el export, no solo exit_code0.
- Resultado físico no verificado: almacenamiento/propagación de modo no
  demuestra control de integración o ausencia de movimiento mecánico.
- Registros previos conservados debajo. Último informe: docs/capture/silent-shutter-status.md.

## Pasada previa E012–E014

- 19 pruebas unitarias correctas: inventario 5, atlas 10, referencias Thumb 4.
- TDD nuevo: test_thumb_refs falló por módulo ausente; se implementó después.
- Ruff: `All checks passed!` en src/tests con el ejecutable indicado por AGENTS.
- Mypy: `Success: no issues found in 3 source files`, ignore-missing-imports.
- CLI real de thumb_refs: cuatro candidatos en libObj, conservados en
  efcs-thumb-candidates.json; validación independiente con LLVM.
- TBH/GOT EFCS/Silent resueltos con mapeo PT_LOAD y R_ARM_RELATIVE.
- SHA-256 del original y siete rangos del registro JSON comprobados; dos
  aristas TBH/GOT contrastadas contra bytes. Enlaces locales revisados: sin roturas.
- E014: cola candidata y transporte /dev/uipc analizados; misma instancia y
  resolución de biblioteca no demostradas. Exports OSAL (9 registros) y núcleo
  conservados, sesiones cerradas. No se identifica consumidor del sensor.
- Exports REA: ScalarDaemon 21, libcamera 6, libObj 115 registros; sesiones
  cerradas con snapshots. No equivalen a cobertura total o proyecto persistente.
- Conclusión física pendiente: no sensor identificado, lectura electrónica
  completa ni prueba de ausencia de accionamiento mecánico.
- Sin acceso a cámara ni modificación/ejecución del firmware.
- Sin commit: no hay Git utilizable y .git es de solo lectura; sin push.
