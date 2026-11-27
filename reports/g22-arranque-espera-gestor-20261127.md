# G22 — esperar el gestor antes de abrir la vista

En los arranques lentos, el hilo `openviewer` podía buscar `openView` antes de que `libObj` terminara de cargarse y abandonar. Esperar solo el símbolo tampoco era suficiente: el intento previo cayó en `libObj+0x7f25e6` con `r0=0` al abrir la raíz. Los bytes Thumb de `0x1251cc..0x1251d4` cargan el puntero global y llaman a `0x7f25e0`; en `0x7f25e6` este accede a `[r0+0x10]`. REA sobre `libObj` agotó el plazo de 300 s; la comprobación es por desensamblado de bytes, no por decompilación.

El hilo espera hasta 300 s a que estén disponibles `libObj`, `openView`, `pViewManager`, el objeto del gestor y su gestor de modelos en `+0x18`. Si se han pedido eventos iniciales, espera también sus dos símbolos. Si no están listos, termina sin llamar a `openView`. Una prueba ejecuta la función C con dependencias que aparecen tarde o nunca y comprueba los eventos y el límite.

Dos arranques fríos independientes (`viz5`, `viz6`) publicaron los tres eventos, abrieron `view/ROOT` y `view/STLREC` y llegaron a dibujar la pantalla de disparo. En el segundo, antes de pulsar reproducción, el estado fue 24 listas y opacidad 0,0823. No se ha demostrado estabilidad 3/3 ni equivalencia completa con la cámara. En el primero, después de instrumentar PLT y abrir reproducción, `im.elf` terminó con SIGSEGV; esa medición no permite asignar la causa a una trampa concreta.

En el segundo arranque, sin esas trampas, `model/MEDIA` devolvió 1 y `@M010` 0. La tecla de reproducción abrió `view/INDEX_PLAYBACK` (capa `0x17`), pero la pantalla quedó negra y el estado final fue 0 listas y opacidad 0. `model/INDEX_PB` respondió 1 en los códigos 0 y 1; crear `@M010` manualmente no cambió su retorno 0. El invitado siguió respondiendo. El siguiente eslabón es la creación/inicialización real del navegador y su cadena de contenidos; no se ha demostrado que el registro sintético del índice sea válido.

Evidencia: [extracto de registros](evidence/g22-arranque-gestor-20261127/arranques.txt), [antes](evidence/g22-arranque-gestor-20261127/viz6-before.png), [después](evidence/g22-arranque-gestor-20261127/viz6-after.png). Sin cámara ni firmware ejecutado en hardware.
