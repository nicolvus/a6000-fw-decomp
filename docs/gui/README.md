# Carril GUI — reconstrucción de la interfaz de la A6000

Carril **independiente** del obturador/sensor. No reutiliza conclusiones de captura y no las modifica.

**Pregunta que responde**: cómo se dibuja, se estructura y se modifica la interfaz de la cámara (textos,
iconos, disposición, mensajes, entradas de menú, páginas, *overlays*) y qué capacidad real hay de cambiarla
de forma **reversible**.

**Estado**: reconocimiento hecho (G1). Motor y capas de composición identificados. **Ninguna modificación
probada**: la matriz de abajo está en nivel 1–2 salvo donde se indique.

---

## 1. Mapa en una página (VERIFICADO)

```
   /usr/bin/im.elf            lanzador ELF (23 KB): dlopen + base de datos IMDB
        │ dlopen("/usr/lib/libObj.so")
        ▼
   /usr/lib/libObj.so         motor de UI (17,4 MB, C++ "ux::")
        ├── ux::gfxeng        GraphicsEngine, Sprite, TextSprite, ResourceUpdater
        ├── ux::resmgr        ResourceManager (base de datos, fuentes, imágenes)
        ├── ux::wgtlay        layout (LayoutConverter, LayoutGroupManager)
        ├── ux::core          texto/tipografía (TextLayout, registerFontFaceFile)
        ├── ViewBase / DefRootView / InputService / HighlightManager
        └── libMWF.so, libBizFw*.so, libmpr*.so, libInfra*.so, libc …
        │ carga bajo demanda
        ▼
   /usr/lib/viewUnified2..8.so   vistas (módulos .so, varias pantallas cada uno)
        │ abre
        ▼
   /usr/share/app/*.uxc|.uxb|.xdb   238 recursos: 66 idiomas, 146 ficheros de vista, estilos, colores,
                                    layouts maestros, fuentes .ltt/.ttf
        │ dibuja
        ▼
   WindowServer / ViewSystem (EGL/GLES) → /dev/fb0
```

Evidencia y detalle: [G01 — arquitectura](g01-arquitectura.md).

## 2. Hechos que condicionan todo lo demás

1. **La GUI no está en `av-cam.bin`.** Está en la pila Linux de la cámara (partición `/usr`). Un cambio de
   interfaz es sustitución de recursos o de código de usuario, no un parche del BIONZ. Esto separa el carril
   del trabajo del obturador y cambia el modelo de riesgo (ver §6).
2. **No hay cadenas literales alcanzables en `.text`.** Se exploró `.uxc` y el motor con `movw/movt` y literales:
   cero referencias. El motor usa identificadores de recurso. Por eso el método de trabajo es símbolos
   dinámicos, vtables y estructuras, no *xrefs* a texto.
3. **El nombre del `.so` de vista no identifica la pantalla.** `viewUnified2.so` sirve a varias vistas
   (traza: `080/011/088_viewUnified2.so`). La selección viene de datos, no del fichero.
4. **REA no puede abrir `libObj.so`** (plazo del proveedor agotado a 900 s con 17 MB). Se trabaja con la tabla
   de símbolos dinámicos y Capstone. Un resultado vacío de REA en este carril **no** prueba ausencia.
5. **La tabla PLT ya está resuelta** (2 419 de 2 420 stubs), así que las llamadas externas del motor se pueden
   nombrar: es la base para seguir el compositor.

## 3. Tareas del carril (ids G)

| ID | Tarea | Estado | Entregable / criterio de cierre |
|---|---|---|---|
| G1 | Reconocimiento: inventario, capas, arranque, dependencias, PLT | **CERRADO** | [G01](g01-arquitectura.md), `scripts/gui/{inventory,elf_scan}.py`, `analysis/gui/g01-inventory.json`, `tests/test_gui_elf_scan.py` |
| G2 | Formato de contenedor `.uxc`/`.uxb`/`.xdb` (cabecera, tabla, *payload*, codificación de texto) | ABIERTO | Parser reproducible + editor de ida/vuelta sobre un `.uxc` de prueba; cerrar la codificación de `string_<idioma>.uxc` |
| G3 | Compositor: quién escribe `/dev/fb0`, `ViewSystem::updateFrame`/`drawFramebuffer`, `swap`, regiones sucias | ABIERTO (parcial) | Cadena de llamadas desde el bucle principal hasta el *swap*, y punto de enganche estable |
| G4 | Menús: estructuras `CmnViewMenuData`/`CmnViewMenuItemStruct`, `cmn_menuTableUtil`, `LayoutMaster_Menu.uxc` | ABIERTO | Volcado verificable de un menú real y su correspondencia con las entradas visibles |
| G5 | Texto y fuentes: `.ltt`, `registerFontFaceFile`, `TextSprite::drawText/setString/setFont` | ABIERTO | Ruta de una cadena desde el recurso hasta el píxel, con un texto cambiado y verificado |
| G6 | Entrada: `InputService`, `GestureAnalyzer`, mapeo de teclas/rueda/dial | ABIERTO | Correspondencia evento físico → acción, con una acción alterada de forma reversible |
| G7 | Ajustes: cómo un ajuste de menú llega al *middleware* y de ahí al comportamiento | ABIERTO | Un ajuste nuevo visible en pantalla y leído por el software de negocio |
| G8 | **Modificación reversible**: sustitución de recursos y/o inyección de código en `/usr` (LD_PRELOAD, reemplazo de `.so`, *overlay*) | ABIERTO (decisión pendiente) | Cambio visible, persistente tras reinicio, con vuelta atrás verificada y sin riesgo de arranque |

## 4. Matriz de modificabilidad (niveles de capacidad)

| Nivel | Significado | Estado en este carril |
|---|---|---|
| 1 | Identificado (símbolo, dirección, fichero) | **SÍ** para el motor, las vistas y los recursos |
| 2 | Estructura reproducida (formato, campos, semántica) | **Parcial**: ELF/PLT sí; `.uxc` no |
| 3 | Cambio en copia local y verificación estática del resultado | **NO** |
| 4 | Cambio aplicado en la cámara y visible | **NO** |
| 5 | Cambio persistente tras reinicio | **NO** |
| 6 | Reversión verificada | **NO** |
| 7 | Cambio paramétrico (varias variantes sin recompilar) | **NO** |
| 8 | Mecanismo general reutilizable | **NO** |
| 9 | UI alternativa completa | **NO** |
| 10 | Validación física sistemática | **NO** |

## 5. Decisiones de método vigentes

- **REA primero solo donde puede**: para `libObj.so` (17 MB) no es viable; se documenta la limitación y se usa
  `scripts/gui/elf_scan.py`. Para módulos pequeños (`viewUnified3..8.so`, `cmn_menuTableUtil.so`) REA sigue
  siendo la primera opción.
- **Capstone con `skipdata`** y `.plt` en modo ARM (no Thumb).
- **Verificar contra bytes**, no contra el desensamblado: cada afirmación de este carril debe poder repetirse
  con un comando de `elf_scan.py` o una prueba de `tests/test_gui_elf_scan.py`.
- **Sin ejecución, sin cámara, sin flasheo**: este carril avanza solo con lectura de artefactos hasta que el
  usuario autorice una prueba concreta en la cámara.
- Cada informe distingue `VERIFICADO` / `INFERENCIA` / `NO_VERIFICADO` y no inventa símbolos ni direcciones.

## 6. Riesgos específicos de este carril

| Riesgo | Detalle |
|---|---|
| Arranque | `im.elf` es el lanzador de la UI: si no arranca, la cámara queda sin pantalla aunque el resto funcione. Cualquier cambio en `/usr` debe ser reversible **sin** depender de la UI |
| Verificación de integridad | Si la partición verifica firmas o hashes, sustituir `.so`/`.uxc` puede impedir el arranque de la UI; hay que determinarlo antes de escribir nada |
| Recursos compartidos | `master_*.uxc` y `LayoutMaster_Menu.uxc` afectan a muchas pantallas a la vez: mejor empezar por un `view*.uxc` concreto |
| Fuentes | Sustituir `.ltt` puede romper el ajuste de texto de todos los idiomas |
| Idiomas | 66 ficheros `string_*.uxc`: un cambio de texto debe replicarse o aislarse por idioma |

## 7. Documentos del carril

| Documento | Contenido |
|---|---|
| [g01-arquitectura.md](g01-arquitectura.md) | Reconocimiento: inventario, capas de símbolos, arranque, carga de vistas, compositor, tabla PLT, límites |
| G02 (pendiente) | Formato `.uxc`/`.uxb`/`.xdb` |
| G04 (pendiente) | Estructuras de menú |
| G08 (pendiente) | Mecanismo de modificación y reversión |

Herramientas: `scripts/gui/inventory.py` (inventario reproducible), `scripts/gui/elf_scan.py`
(`sym`, `str`, `refs`, `dis`, `func`, `xrefs`, `plt`, `resolve`).
Evidencia: `analysis/gui/`. Pruebas: `tests/test_gui_elf_scan.py`.
