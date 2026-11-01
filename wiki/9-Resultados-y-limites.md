# 9. Resultados y límites

## Qué se midió con el 3.23

- **Imágenes completas** (JPEG 6000×4000 y ARW 6024×4024) sin obturador mecánico.
- **Disparo y rearme:** 36/36 disparos en ráfagas de 6 y 10/10 sueltos; rearme de 0,7–1,0 s; latencia de 2,6–2,9 s a velocidades rápidas.
- **Exposición** (E25-10): sin cortina trasera la fila `i` integra T + ≈7 ms + 15,2 µs·i (lectura ≈ 61 ms), así que de 1/4000 a 1/500 la velocidad apenas escala.
  Con la [capa 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/6-Capa-2-exposicion-uniforme) la exposición es uniforme.

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
| 3.25 | Integrado con selector EFCS/Electronic | **La cámara no arranca** |
| 3.26 | Recuperación con contenido oficial 3.21 | Preparada y verificada offline; solo sirve si se vuelve a entrar al actualizador |
