# Sony A6000 Hardware & Firmware Reverse Engineering Project

## Objetivo

Construir una base técnica reproducible sobre hardware, firmware, arquitectura,
arranque, recuperación e interfaces de captura de ILCE-6000. La viabilidad del
obturador electrónico es un subproyecto; su resultado no condiciona el valor ni
el éxito del proyecto general. Se conservan íntegros los hallazgos E001–E009,
hashes, fuentes, firmware y snapshots anteriores.

La carpeta local mantiene el nombre histórico `sony-a6000-electronic-shutter`
para conservar rutas absolutas de REA y procedencia de evidencias. El nombre
del proyecto y su organización documental se amplían sin mover los originales.

## Dos líneas coordinadas

| Línea | Entregables actuales | Siguiente pregunta |
|---|---|---|
| Arquitectura general | Inventario físico inicial, atlas de 679 ELF, dependencias declaradas | ¿Qué carga cada entorno y cómo se inicia? |
| Pipeline de captura | E007–E009, funciones y grafos previos, subproyecto de obturador | ¿Quién consume el buffer de conversión SilentShutter? |

Son líneas de investigación que avanzan de forma coordinada; no implican
ejecución sobre hardware ni que se hayan delegado a agentes independientes.
Índices: `docs/architecture/README.md` y `docs/capture/README.md`.

## Secuencia de profundización

1. Completar desconocidos del inventario físico con evidencia de placa o
   documentación de servicio verificable; no atribuir chips por sus nombres comerciales.
2. Resolver ocho dependencias ambiguas y mapear cargadores, scripts y montajes.
3. Seguir libsdcom/IPC, controladores y fronteras entre sensor y procesamiento.
4. Documentar arranque normal, actualización y recuperación por separado.
5. Mantener modificaciones candidatas aisladas y basadas en pruebas. No se
   habilitan escrituras, flasheo ni pruebas en cámara con este cambio de alcance, salvo
   autorización expresa del usuario para un caso concreto.

## Reutilización

El atlas usa caché de metadatos por SHA-256 del binario, SHA-256/versión de readelf
y versión del esquema. Verifica los hashes originales antes de reutilizarla.
Las reglas de asociación se recalculan sin volver a ejecutar readelf. Los
snapshots REA conservan evidencias, pero los snapshots actuales de Ghidra son
sesiones efímeras con cero primitivas reproducibles: no prometen eliminar el
coste de importar de nuevo. Consultar primero la evidencia exportada y abrir
una sola sesión persistente para nuevas preguntas relacionadas.
