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

## Estado en una línea

3.23 instalado y confirmado en cámara real (27-10-2026): dispara en silencio y sin error. El 3.24 (vuelta al Darwin oficial) solo está
verificado offline y nunca se instaló en una cámara real.
