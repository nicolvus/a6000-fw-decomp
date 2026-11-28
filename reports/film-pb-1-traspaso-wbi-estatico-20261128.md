# FILM-PB-1 — Traspaso de investigación estática WBI del CFW 4.05

Fecha: 28-11-2026. Caso abierto. Objetivo: obtener una `nflasha5` que reanude el CFW con menú Silent y reproducción de vídeo. La petición actual exige construcción y verificación estáticas.

## Estado

No hay una WBI final del CFW verificada ni una garantía de funcionamiento. Se prepararon una imagen intermedia `prof` y un perfil sintético para investigar la fase de optimización de Sony. Son experimentales y no constituyen un paquete listo para instalar.

Este informe corrige la explicación de [WBI propio](film-pb-1-wbi-propio-20261127.md) en cuanto atribuye la pantalla negra únicamente a que la instantánea se tomó durante el apagado. La pila del CFW y la de la WBI de fábrica sitúan ambas capturas en la llamada `write` de `im.elf` para `warm`, con el mismo retorno. El punto de captura por sí solo no demuestra la causa.

## Evidencia

- La captura CFW original `analysis/camera-dumps/20261127-wbi-nflasha5/dev_nflasha5.bin` tiene firma `prof`, vector `0x800523a4`, 1.397 secciones y estado interno SSBOOT 0. SHA-256 `aaf5919e34ab156c7014cfc64ba5543ba5dc52e984f975d33f828614346d8ca6`.
- La WBI de fábrica tiene firma `WBI1`, vector `0x800523bc`, 1.164 secciones y estado 2. SHA-256 `fe080cda9f330537f36d7e9e283ecd69e4e8096d974dbdd16d598a8cbdcf3f04`.
- El miembro `nflasha5` del paquete 4.07 coincide con la captura CFW desde el byte 4 hasta el final. Cambiar la firma no completa la optimización.
- En los mapas de `im.elf`, los tres segmentos añadidos de `viewUnified2.so` se solapan con `CautionConfig.so` si se conserva la base de la imagen Sony. No basta copiar esos segmentos a la WBI de fábrica.
- El perfilador de la captura CFW tiene listas de eventos vacías en los cuatro núcleos. No aporta un registro real de accesos posterior a la reanudación.
- Loader3 contiene una comparación explícita con `prof` en `0xc01f2ba6`. En modo 12 la rama en `0xc01f0b8a` consulta esa comparación. El registro histórico `resultado-ciclos-1-2.txt` muestra `MODE#12` y el inicio de perfilado en una prueba anterior. Esto corrige la afirmación general de [D17](evidence/g22-silent-wbi-20261127/D17.md) de que `prof` siempre fuerza arranque frío. El resultado depende del modo y condiciones de arranque.
- En la memoria restaurada del CFW, `/log` figura montado desde `/dev/nflasha11`, el optimizador tiene configurada la ruta `/log/ssbi_prof.bin` y no aparece una entrada de ese nombre en la caché de dentries inspeccionada. Esto no demuestra que un fichero colocado en disco sea visible tras restaurar cachés y estado del sistema de archivos.

## Insumos y límites

En `build/wbi_silent/insumos-optimizacion-405/`, fuera del material versionado:

- `nflasha5-prof-optimize.bin` conserva los datos de la captura y cambia el vector a `0x800523ac`, con un único byte diferente. Se verificaron los checksums de metadatos y las longitudes de las 1.397 secciones.
- `ssbi_prof.bin` es sintético. Pide 2.001 páginas de 31 rutas y no incluye eventos de memoria anónima. Se verificó su formato y la relectura idéntica en copias temporales de `nflasha11`. Las tres copias proceden de volcados con el mismo hash y no son tres controles independientes.
- `verificacion.json`, `comprobacion-independiente.json`, `pilas-suspension.json` y `montajes-en-capturas.json` documentan hashes, instrucciones, pilas y montajes. Los scripts de investigación están en `/tmp/a6000-wbi-mapas.ogxBEShi/`, ubicación temporal.

Los bytes del kernel capturado muestran que el vector preparado selecciona estado 2 y que la rama correspondiente llama al optimizador antes de volver a suspender. La ejecución completa de esa rama, la visibilidad coherente del perfil, la creación de `WBI0`, su sellado como `WBI1` y el funcionamiento de Silent y vídeo siguen sin demostrarse. La simple inclusión de páginas en el perfil no prueba que conserve todos los accesos necesarios.

## Continuación concreta

1. Analizar estáticamente las cachés FAT y los metadatos restaurados de `/log` para determinar si el perfil sintético escrito en una imagen de partición coherente sería visible al optimizador.
2. Verificar las condiciones completas de Loader3 que seleccionan el modo 12 y el salto por el vector preparado.
3. Determinar cómo producir y comprobar una imagen optimizada y su estado de reanudación a partir de los datos disponibles, incluyendo páginas anónimas, estado de dispositivos y coherencia de `/usr`.
4. Mantener separadas las pruebas históricas en cámara de las verificaciones actuales en PC. No tratar un checksum o una cabecera válida como prueba de Silent y vídeo.

Referencias adicionales: [informe consolidado anterior](film-pb-1-informe-wbi-nflasha5-20261128.md), [resultados históricos de los ciclos](evidence/film-pb-1-ssbi-20261126/resultado-ciclos-1-2.txt) y [formato del perfil](evidence/film-pb-1-ssbi-20261126/B3.md).
