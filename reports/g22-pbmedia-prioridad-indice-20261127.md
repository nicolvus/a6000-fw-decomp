# G22-PBMEDIA: prioridad del índice en la SD de prueba

Con `SD_MEDIA=1`, la imagen de prueba debe contener la foto y el índice generados juntos. La copia posterior del árbol de la tarjeta anfitriona los sobrescribía si ya existían archivos con esos nombres: con `SD_MEDIA_CAB=0`, una construcción real produjo `AVIN0001.INP` de 512 bytes, copiado del anfitrión, en vez del índice generado de 128 bytes. La misma colisión afectaba a `DSC00001.JPG`. Esto invalida la suposición de que esa opción determina necesariamente el contenido del índice; no demuestra qué contenían las tarjetas de las pruebas históricas.

Se copia primero la tarjeta anfitriona y después los archivos de prueba, únicamente dentro de la imagen FAT. El resto de los archivos de la tarjeta permanece en la imagen y los archivos originales no cambian. Una prueba de regresión reproduce las dos colisiones y comprueba también un archivo no conflictivo. En la misma tarjeta, la imagen corregida contiene `AVIN0001.INP` y `.BNP` de 128 bytes.

La estructura de los registros sigue siendo una hipótesis y este cambio no demuestra que el firmware la lea ni que la reproducción funcione. G22-PBMODEL continúa abierto: medir la lectura y el modelo en el invitado con la imagen corregida.

## Arranque y medición en el invitado

En el perfil `viz3` con el índice corregido, el arranque inicial no abrió la vista: `OPENVIEW: sin viewManagerIf::openView`. Al abrir `view/ROOT` y `view/STLREC` manualmente, el medio llegó a `getModelInfo(model/MEDIA, 0) = 1`; `@M010` siguió en 0 y el fotograma llegó a solo 3 listas, insuficiente para validar la galería. La tecla convirtió a acción 4 y pidió `view/INDEX_PLAYBACK`, pero no se verificó una rejilla.

Se probó aparte esperar hasta que `libObj` ofreciera `openView`: eso no basta. En `viz4`, `STARTEV` informó de dependencias ausentes y al abrir automáticamente `view/ROOT`, antes de que el gestor estuviera listo, `im.elf` cayó con SIGSEGV en `libObj+0x7f25e6`, dirección `0x10`. Se retiró ese cambio experimental. La reparación debe esperar el estado real del gestor y de los eventos, no solo la presencia del símbolo. [Extracto de ambos registros](evidence/g22-pbmedia-colision-20261127/arranques.txt).
