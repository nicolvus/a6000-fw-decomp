# Contrato común (todas las tareas Codex)
Proyecto: Sony A6000 fw 3.21, SilentShutter. SOLO análisis estático/emulación local. No conectar cámara, no flashear, no modificar firmwares originales, no instalar paquetes (ni Ruff/Mypy).
Idioma: documentos en español. Etiqueta cada conclusión: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO. Cita direcciones reales.
Lee primero: CONTEXT.md (secciones "parte 7/8/9"), docs/capture/silent-integration-design.md, docs/capture/electronic-still-low-resolution.md.
Reutiliza antes de re-descompilar: analysis/ghidra/*.json (libobj-*, liro-*, libmpr-writestill, sfra-*, sdf-*, ddl-*), scripts/elf_thumb_callers.py, scripts/elf_string_xrefs.py, scripts/sfra_outcalls.py.
Convenciones: av-cam (LIRO) base lógica 0x43541000 Thumb-2, usar VA directa; libObj/libmpr: dirección Ghidra = VA ELF + 0x10000. Límites de función en .so stripped pueden estar mal; no concluyas "desconectado" solo por BL (hay llamadas indirectas/GOT).
Ghidra headless: NO uses analysis/ghidra/a6000-libs (compartido). Copia el proyecto (cp -r analysis/ghidra/a6000-libs.rep analysis/ghidra/a6000-libs.gpr a analysis/ghidra/_cx_<ID>/) y trabaja ahí con scripts/libobj_dec.sh como plantilla (analyzeHeadless -noanalysis -readOnly, DecompAt.java). Borra la copia al terminar si no es necesaria.
Escribe SOLO tus archivos de salida listados; NO edites CONTEXT.md, RESEARCH_TASKS.md ni docs ajenos (el coordinador integra). Scripts nuevos en scripts/ con prueba en tests/ (python3 -I, sin dependencias nuevas).
Entrega final (stdout): máx. 25 líneas: hallazgos clave con etiquetas, archivos creados, bloqueos exactos y siguiente tarea sugerida.
