# S53 — ¿Cambia la viabilidad de Silent en A6000? (19-10-2026)

Resultado: **Escenario B** del encargo — incompatibilidad concreta y reproducible en el firmware Darwin A6000.
Evidencia: [comparación](s53-darwin-a7s-a6000-comparison.md), [cortinas](s53-curtain-actuator-control.md).

## Pregunta central

**¿Darwin A6000 reconoce y ejecuta el comportamiento Silent de la A7S al recibir los indicadores CAIF?**
**No (VERIFICADO estáticamente).** Recibe el mismo paquete de 22 B por el mismo canal y lo analiza con el mismo parser, pero
descarta `pkt[+0x12]` bit 5; sus escritores de bobina (`0x20cb2`, `0x20d00`, `0x20d26…`, `0x20a8a`, `0x20aa4`) y el
arranque del seguimiento ADC (`0x20734`, `0x2083c`) no tienen la puerta `no_silent` de la A7S. Con el paquete Silent, la
A6000 accionaría las bobinas normalmente (según el código; no comprobado físicamente).

Naturaleza de la limitación: **firmware**, no hardware de control (mismo MCU FM3, mismas salidas P4D/P4E, misma secuencia).
No se ha comparado el mecanismo físico de cortinas ni si la A6000 tolera una exposición con cortina abierta.

## Qué faltaría para una implementación (análisis, no autorización)

| Bloque | Diferencia con A7S | Tipo |
|---|---|---|
| LIRO A6000 | no fija `+0x12|=0x20`, `+0x0d` modo 2 ni clase 0 (`0x4384149c/0x43841468/0x4384137c`); `+0x740` sin escritor; sin modos `0x4e/0x4f` (S52) | firmware principal |
| Darwin A6000 | 3 puntos ausentes: parser (≈18 B), argumento `no_silent` en primitivas/escritores/diferidos, puerta del seguimiento ADC | firmware MCU (requiere **reprogramar Darwin**) |
| IMX210 | final electrónico de una exposición fotográfica completa no demostrado (S51/S52) | sensor / datos de lectura |

La alternativa «tipo de mecanismo 0» (rama sin bobinas ya presente en A6000) es global: desactiva el mecanismo en todo el
controlador, también rearme y vídeo; no equivale a la ruta Silent condicionada por paquete. **NO VERIFICADO** su efecto.

## Decisión

**S51 se mantiene y se refuerza: no parchear ni flashear.** Silent completo en A6000 requeriría modificar **dos**
firmwares (LIRO y Darwin) más resolver el IMX210; reprogramar Darwin está fuera de las restricciones del proyecto.
Esto no demuestra imposibilidad física: la diferencia Darwin es pequeña y de software, pero su prueba exige ejecutar
firmware modificado.

## Pregunta secundaria — diferencias que quedan (LIRO + IMX210)

1. LIRO: producir tipo Silent 2 → clase 0, bit `0x20`, `+0x748`/`+0x740`, omisión de esperas CAIF3/`0x800000` (S52).
2. LIRO/IMX210: modo de lectura de foto completa sin `0x4e/0x4f`; serialización y comandos reales de integración.
3. Sincronía: en Silent A7S Darwin sigue pulsando `P4C` (`CA_1ST_CURTAIN_START`, hacia IC6000) tras el tiempo de
   exposición; qué hace LIRO con esa señal en A6000 está **NO VERIFICADO**.
4. Sin evidencia nueva del IMX210 en S53 (prioridad 6: no se reabrió).
