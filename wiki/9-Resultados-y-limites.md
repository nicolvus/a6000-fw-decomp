# 9. Resultados y límites

## Qué se midió con el 3.23

- **Imágenes completas** (JPEG 6000×4000 y ARW 6024×4024) sin obturador mecánico.
- **Disparo y rearme:** 36/36 disparos en ráfagas de 6 y 10/10 sueltos; rearme de 0,7–1,0 s; latencia de 2,6–2,9 s a velocidades rápidas.
- **Exposición** (E25-10): sin cortina trasera la fila `i` integra T + ≈7 ms + 15,2 µs·i (lectura ≈ 61 ms), así que de 1/4000 a 1/500 la velocidad apenas escala.
  Con la [capa 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/6-Capa-2-exposicion-uniforme) la exposición es uniforme.

## Obturador electrónico en el firmware (desde el 3.30)

- **Dispara con obturador electrónico** desde el [3.30](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r54-paquete-330-envio-pkt0e.md)
  (envío en línea de `pkt[0x0e]` + compuerta de Darwin); el 3.35 iguala la exposición a la mecánica y el
  [3.77](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r87-disparo-remoto-y-recalibracion.md) deja el Silent
  nivelado de 1/1250 a 1/50 sin el parche de RAM de la [capa 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/6-Capa-2-exposicion-uniforme).
- **EFCS activo:** negro desde 1/1000 (≈1,27 ms perdidos), también con el firmware de Sony; causa física
  ([R74](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r74-conclusion-final-efcs-negro.md),
  [R83](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r83-informe-final-efcs-negro.md)).
- **Vídeo:** los CFW de la serie 3.93/4.0x **no reproducen** los clips grabados (FILM-PB-1, abierto).
- Las funciones añadidas (Film Simulation, Picture Profile, Extra Fine, ISO) van en builds separadas de la serie 3.93 sobre la base Silent.

## Puntos débiles

- Solo con la capa 1 (3.23) la exposición no es uniforme.
- Rango medido de 1/4000 a 1/30; desde 1/15 vuelve el disparo normal; 1/8000 solo emulado; exposición larga electrónica no implementada.
- Efecto rolling por la lectura de ≈ 61 ms.
- La capa 2 necesita telnet, RemoteShutter y se aplica en cada disparo o ráfaga.
- Sin medir: flash, vídeo, Live View con parches, y la operación 5 de Darwin (P40/P41=3) y P4B/P4C.
- Escala absoluta con incertidumbre ±25 %.
- Riesgo de base: flashear firmware modificado sin recuperación independiente demostrada.

## Versiones

| Versión | Qué hace | Resultado |
|---|---|---|
| 3.21 | Oficial de Sony | Obturador mecánico normal |
| 3.22 | Darwin «tipo 0» (bobinas apagadas); paquete intermedio del autor | Instalada (T024); arranca. Efecto deducido del código |
| 3.23 | 3.22 + B1a | Instalada (T040); dispara en silencio y sin error |
| 3.24 | Darwin oficial con número 3.24 | Preparada, no instalada |
| 3.25 | Integrado con selector EFCS/Electronic | **La cámara no arranca** (no publicado) |
| 3.25c | 3.25 con `nflasha3` en el formato de Sony | Verificado offline (30/30, emulación sin fallos) e **instalado como 3.27** (03-11-2026); el selector no llegó a verse en el paquete a Darwin ([R52](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r52-prueba-fisica-selector-327.md)) |
| 3.26 | Recuperación con contenido oficial 3.21 | Instalado por el actualizador oficial para recuperar la cámara del autor ([R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md)) |
| 3.27 | 3.25c con cabecera 3.27 | Instalado (03-11-2026); arranca, obturador electrónico sin validar |
| 3.30 – 3.35 | Obturador electrónico real y calibración | Instalados y probados en cámara |
| 3.77 | Silent calibrado en `av-cam` | Validado en RAM; base de los CFW siguientes |
| 3.93 | Una build por función sobre la base Silent (`base`/`film`/`pp`/`exfine`/`iso`) | Instaladas y probadas de una en una; `pp` es la última auditada; `iso` no arranca |
| 4.01 – 4.04 | Receta de Film por la GUI, iconos Fn y bisección del vídeo | 4.01/4.02 instaladas; 4.03/4.04 construidas y auditadas, sin instalar |
