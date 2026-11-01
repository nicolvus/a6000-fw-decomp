# Wiki CFW Sony a6000 — Silent Shutter

Guía para replicar, de principio a fin, el obturador **completamente silencioso** de la Sony A6000 (ILCE-6000) obtenido por
ingeniería inversa del firmware 3.21: el microcontrolador Darwin deja de mover las cortinillas mecánicas y el sensor controla la exposición.

> ⚠️ **Instalar firmware modificado puede inutilizar la cámara.** No hay recuperación independiente demostrada: un firmware posterior
> (3.25, no publicado) dejó la cámara del autor sin arrancar. Lee [Requisitos y riesgos](https://github.com/nicolvus/a6000-fw-decomp/wiki/1-Requisitos-y-riesgos) antes de empezar.

## Ruta de réplica

| Paso | Qué obtienes | Página |
|---|---|---|
| 1 | Entender qué necesitas y qué puede salir mal | [Requisitos y riesgos](https://github.com/nicolvus/a6000-fw-decomp/wiki/1-Requisitos-y-riesgos) |
| 2 | Repositorio, entorno Python y firmware oficial 3.21 desempaquetado | [Entorno y firmware oficial](https://github.com/nicolvus/a6000-fw-decomp/wiki/2-Entorno-y-firmware-oficial) |
| 3 | Copia de seguridad de la NVRAM de **tu** cámara | [Backup de NVRAM](https://github.com/nicolvus/a6000-fw-decomp/wiki/3-Backup-de-NVRAM) |
| 4 | Los `.dat` 3.23 y 3.24 construidos por ti (o los del release) y verificados | [Construir los paquetes](https://github.com/nicolvus/a6000-fw-decomp/wiki/4-Construir-los-paquetes) |
| 5 | Cámara en 3.23: obturador mecánico inactivo | [Instalar el 3.23](https://github.com/nicolvus/a6000-fw-decomp/wiki/5-Instalar-el-3.23) |
| 6 | Opcional: exposición uniforme por filas (parche en RAM) | [Capa 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/6-Capa-2-exposicion-uniforme) |
| 7 | Qué hacer si algo falla | [Volver atrás y recuperación](https://github.com/nicolvus/a6000-fw-decomp/wiki/7-Volver-atras-y-recuperacion) |

Todos los scripts y apps, con su uso: [Herramientas](https://github.com/nicolvus/a6000-fw-decomp/wiki/12-Herramientas).

Para entender el porqué: [Cómo funciona el parche](https://github.com/nicolvus/a6000-fw-decomp/wiki/8-Como-funciona-el-parche), [Resultados y límites](https://github.com/nicolvus/a6000-fw-decomp/wiki/9-Resultados-y-limites) y el
[mapa del repositorio](https://github.com/nicolvus/a6000-fw-decomp/wiki/10-Mapa-del-repositorio). Aviso legal: [Copyright y uso](https://github.com/nicolvus/a6000-fw-decomp/wiki/11-Copyright-y-uso).

## Qué está verificado y qué no

| Paso | Verificación |
|---|---|
| Construir los `.dat` 3.23 y 3.24 desde el firmware oficial | **Reproducido el 01-11-2026**: mismos SHA-256 que el release, 69/69 comprobaciones |
| Medir el guard sin flashear | Probado offline y con la cámara en MTP |
| Backup y restauración de NVRAM | Probados en hardware (20-10-2026) |
| Instalar el 3.23 | **Confirmado en cámara real** (T040/T041, 27-10-2026), desde un 3.22 intermedio |
| Instalar el 3.23 desde un 3.21 directo | Solo verificado offline (el guard lo acepta); no instalado así |
| Instalar el 3.24 | **Nunca instalado en una cámara real** |
| Capa 2 (parche en RAM) | Probada en T050; escala absoluta con ±25 % de incertidumbre |
| Instalar Tweak y RemoteShutter con las instrucciones de esta wiki | El autor ya los tenía instalados; los pasos escritos aquí vienen de la documentación y **no se han vuelto a ejecutar desde cero** |
| Capa 2 sin PC (desde la cámara) | Solo idea, sin implementar |

Glosario de términos y etiquetas: [Glosario](https://github.com/nicolvus/a6000-fw-decomp/wiki/13-Glosario).

## Estado en una línea

3.23 instalado y confirmado en cámara real (27-10-2026): dispara en silencio y sin error. El 3.24 (vuelta al Darwin oficial) solo está
verificado offline y nunca se instaló en una cámara real.
