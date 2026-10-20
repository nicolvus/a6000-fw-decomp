# Plan activo: botón → imagen visible

## Checkpoint 16-10: tarea inicial de fases resuelta y próximas dependencias

Leer [máquina de estados Darwin](darwin-state-machine.md). Reconstruidos
los cuatro destinos TBB por firmware, transiciones y campos modificados.
Notificación A6300 `1d3a8→22e3e(1)→24666(1)→20c2a→23e16` condicionada
por variante e ID de secuencia; falta enlazar su instalación/interrupción.
Bit80 retiene la etapa; fase4 no demuestra final de captura.
Identificados escritores42668000+offset en ambos firmwares y escritores de
inhibición+170 en A6300. No se ha demostrado relación con Silent.
Caracterizados productores de nueve bytes adicionales CAIF; ABI serie
contrastado con otro productor mediante REA, sin receptor remoto identificado.

1. Resolver instalación de notificación `1d3a8` y ruta A6000 hasta `2089c`.
2. Seguir productores de `200034e4+444` y contexto `d48a`; discriminar ciclo
   general de inhibición específica de captura. No llamarlo Silent aún.
3. Identificar banco42668000 y salidas+11c/+234/+238 con evidencia del bloque.
4. Resolver receptor de cola740017, canal y parser10300; comparar longitudes,
   campos y compatibilidad sin asumir Darwin. Seguir globales4415af72..76.
5. Conectar lo anterior con modos/clases IMX y entrega de fotograma. Mantener
   hipótesis A/B/C abiertas hasta evidencia específica del IMX210.

Etapa autorizada: análisis estático, emulación local y documentación. Sin
comandos sobre cámaras ni instalaciones. La entrega de sesión es un informe
con resultados y fronteras; no declarar obturación electrónica funcional.

## Fronteras históricas y continuidad

Frontera Darwin: leer darwin-shutter-entrypoints.md y silent-caif-transport.md.
Usar solamente proyectos `*-darwin-rom`, ROMbase4200 validada; los antiguos
con base0 son una hipótesis descartada. Seguir consumidores ADC canal8:
A6000wrapper2109c (calls2067a/206a6/206c8), A6300wrapper24da2
(calls23770/2379c/237be), y los callbacks principales de tabla2b534.
La conexión entre Darwin y el receptor CAIF todavía debe demostrarse.

Pista descartada16-10: `43919c04 → 43ba72ba → 4380fc78` transmite
registros a KikiLog, cola0110027c. Receptor y contador comprobados con REA
y símbolos/reubicaciones del módulo; leer silent-kikilog.md. Seguir otros
consumidores de4415af79 y banco+16f, no atribuir esa omisión a cortinas.

Frontera actual: leer a6300-silent-comparison.md. Modo Silent A6300 `4e`
llega desde `438be684` al callback `43bda462` y SetMode `43717dbc`.
A6000 `437f7f98` carece de esa rama y su IMX210 rechaza `4e`.
Seguir ahora la clase real de exposición A6300, sin equiparar SilentType2
con selector2: `438c0008` → `4391bd40` copia banco+ec/+17c a captura+674;
selector en +67d. `4391a6f4` escribe banco+f5 desde global44096d68;
`43918ed0` obtiene esa global de `4391d440` tras `4391cd24`.
Wrapper SetExposure correcto43717de4 (df8 era una instrucción interior,
ya reparada). Los resultados permanecen estáticos; no declarar activación.

Instrucción16-10-2026: referencia comparativa histórica **ILCE-6300**; desde 19-10-2026 la
referencia vigente es **A7S 3.20** (instrucción del usuario). Comparar desde
firmware oficial A7S 3.20, sin asumir equivalencia de sensor ni copiarparches.
Seguir Silent→estado→clase→secuencia→controlador y contrastar conA6000.

Continuación E020: leer efcs-capture-selector.md. Copia demostrada de EFCS:
43844e80 común+0x210→43eb2680+0x41c;4384b268→437b03c8 copia0x92c a
43ea976c;4383fc48 selecciona banco;43842158→43eefb7c→43eedecc;
43841070 escribe registro fotograma+0x6d;4383fd6c copia registro+0x64 a
captura+0x64c por437f8a50, clase en+9.438c828c aplica SetExposure, con
sobrescrituras para clases dispositivo2/3 y condiciones de backend.
Clases normales1/3/5, anulación diagnóstica0..7. Clase2 NO probada silent.
Nuevo selector437ea8cc, prólogo verificado; campos+73a/+4b80 no sonSilent.
Switch final438b83a0 resuelto: diagnóstico, no consumidor común+238.
Seguir interpretación clase2 y coordinación mecánica; Silent sigue pendiente.

Continuación E018/E019: leer silent-imager-consumers.md e imager-exposure-p2s.md.
Coordinador StrtExps4381106c→43ae935a→SetExposure436d6320→IMX210436d6f6c;
aplicación virtual38→436d839c→listas436d75f8→formateadorP2S→436d5ed0.
Selector de exposición: salida+9 ← fuente43eb35d0+cd ← banco*10hex+0d;
productor437b617c/43843a44/43849fb8. Seguir el origen de los bancos, no forzar enums.
EFCS tiene lecturas +210; Silent +238 sigue sin consumidor físico demostrado.
Falso lector43792fb4 descartado: subestructura+5a4, no bloque común.
Proyecto Ghidra persistente ampliado, autoanálisis timeout300s, cobertura parcial.
Usar QuerySilentLiro.java incremental; NO ExportSilentLiro.java que limpia metadatos.

Último encargo: terminar SilentShutter. E015/E016 reconstruyen el tramo de
software hasta receptor LIRO; E017 identifica un controlador IMX210 en el blob.
Continuar desde silent-shutter-status.md: aún falta ligar el estado al fin de
integración/lectura física y resolver todas las inhibiciones. No declarar que
un receptor o una respuesta exitosa prueban fotografía electrónica completa.

Actualización del usuario: **priorizar obturación, EFCS y posibilidad de final
electrónico**. Resultado vigente: shutter-investigation.md (E012), protocolo
en ../capture-pipeline.md (E013). Se resolvieron despacho 0x1008 y las ramas
EFCS/Silent hasta envío OSAL; receptor físico y lectura siguen abiertos.

Prioridad indicada por el usuario: terminar primero la investigación del proceso
de captura y configuraciones. Trabajo estático y documental; instalación de
dependencias autorizada. Ninguna autorización para escribir firmware en cámara.

1. Separar entrada física, pulsación parcial/completa y orden de captura por app.
2. Resolver despacho e IPC desde orden hasta el coordinador nativo.
3. Inventariar parámetros y categorías de imagen con evidencia y alcance por modo.
4. Identificar exposición, captura y estados del coordinador; distinguir sensor real
   de órdenes de software y temporizadores.
5. Seguir lectura, procesado, RAW/JPEG, metadatos y guardado.
6. Separar live view, visualización automática tras captura y reproducción del archivo.
7. Producir secuencia, tabla de configuraciones, registros de funciones/aristas y
   límites por tramo. Conservar preguntas no demostradas sin declararlas resueltas.

Método: reutilizar atlas y exports existentes. REA/Ghidra para funciones y xrefs;
proyecto Ghidra persistente si los límites efímeros/plazos de REA hacen costosa una
biblioteca grande. Toda alternativa debe registrar versión, perfil y motivo.
Hashes originales verificados. No confundir una dependencia DT_NEEDED con IPC,
una notificación con captura física o un preview con el archivo final.
