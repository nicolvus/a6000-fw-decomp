# S35 — Objetos DFE y frontera estática APL/IRQ (18-10-2026)

Continuación de la frontera final de [S34](s34-apl-dma-vd-interrupts.md), sin
reabrir programación APL ni temporización VD. Evidencia exclusivamente estática
de `av-cam.bin`, base `0x43541000`, SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.

**Resultado: FRONTERA ESTATICA AGOTADA para esta vía de cuatro objetos y la
identificación del factor por literales.** Los objetos y sus métodos quedan
resueltos; acceden a SGC DFE, sin lectura/ack APL recuperado. No se demuestra
la cadena banco APL → factor → callback → EC/LM ni el fin electrónico de
integración. Esto acota el subproblema; no demuestra imposibilidad estática
universal en otros caminos del firmware ni imposibilidad del hardware.

## VERIFICADO — identidad y vtables

`0x436d06d8` construye los cuatro objetos. Los slots son punteros a RAM,
no vtables ni importaciones pendientes de carga. RAM está a cero en el blob;
la identidad se obtiene de las escrituras de los constructores y RTTI ROM.
`0x436d2c70` instala Ofmt y `0x436d21fc` instala Ifmt.
La columna vtable indica el address point: punteros virtuales desde offset 0;
la cabecera ABI está ocho bytes antes.

| Slot → objeto | Tipo RTTI | Vtable | Método virtual +8 | Unidad |
|---|---|---|---|---|
| `0x44023400→0x43e7ef80` | `Camera::DFECore::Ofmt` | `0x43fcbf80` | `0x43ad828c` | 0 |
| `0x44024d10→0x43e7ee00` | Ofmt | `0x43fcbf80` | `0x43ad828c` | 1 |
| `0x44021914→0x43e7ee44` | `Camera::DFECore::Ifmt` | `0x43fcbe70` | `0x43ad79ae` | 0 |
| `0x4402603c→0x43e7eed4` | Ifmt | `0x43fcbe70` | `0x43ad79ae` | 1 |

RTTI Ofmt `0x43fe94e4→0x43c9284f`, Ifmt
`0x43fe9490→0x43c92694`. Los punteros de código ROM llevan bit Thumb.
Los dos métodos anteriores son también el `+8` de los objetos padres;
los indirectos que contienen despachan subobjetos en `this+0x10` y `this+0xc`.

| Padre / miembro | Objeto unidad 0 / 1 | Tipo RTTI del subobjeto | Vtable | +8 |
|---|---|---|---|---|
| Ofmt `+0xc` | `0x43e7ef58 / 0x43e7eec8` | `Ofmt_OfSgc` | `0x43fcbfc0` | `0x436d30e8` |
| Ofmt `+0x10` | `0x43e7eebc / 0x43e7efa4` | `Ofmt_OutSgc` | `0x43fcbff0` | `0x436d32a4` |
| Ifmt `+0xc` | `0x43e7ef38 / 0x43e7ef70` | `Ifmt_RcvSgc` | `0x43fcbee8` | `0x436d26e4` |
| Ifmt `+0x10` | `0x43e7ef14 / 0x43e7ee24` | `Ifmt_LnkSgc` | `0x43fcbd78` | `0x436d23e0` |

Ofmt ejecuta OutSgc y después OfSgc si `this+0x14 != 0`.
Ifmt llama primero `0x43ad7ea6(this+0x14)` y después LnkSgc y RcvSgc.
Constructores de los hijos: `0x436d3168`, `0x436d3328`, `0x436d27e8`,
`0x436d06ac→0x436d11c8→0x436d247c`. El constructor derivado de LnkSgc
sobrescribe la vtable base `Ifmt_BlkSgc` (`0x43fcbd40`); no se debe elegir
esa vtable base como tipo final de la unidad 0.

## VERIFICADO / PARCIAL — lecturas y escrituras efectivas

Los constructores guardan `base=0xfc000000` para unidad 0 y `0xfc001000`
para unidad 1 mediante `0x43ad6f32(this+4,base)`.
El getter `0x43ad6e42` recupera esa base. Cada método consulta bit 0,
emite diagnóstico si ya está activo y hace RMW del mismo registro a bit 0=1.

| Método | Getter de estado | Setter RMW | Registro unidad 0 / 1 |
|---|---|---|---|
| `0x436d30e8` | `0x436d30c8` | `0x436d30d8` | `0xfc0a1610 / 0xfc0a2610` |
| `0x436d32a4` | `0x436d3284` | `0x436d3294` | `0xfc0a1710 / 0xfc0a2710` |
| `0x436d26e4` | `0x436d26c4` | `0x436d26d4` | `0xfc0a1210 / 0xfc0a2210` |
| `0x436d23e0` | `0x436d23c0` | `0x436d23d0` | `0xfc0a1310 / 0xfc0a2310` |

RcvSgc retorna sin activar si `this+0xc != 0`. Se contrastaron los tail branches
del listing: Ghidra incorpora algunos setters en el pseudocódigo y un cuerpo
de RcvSgc incluye el setter anterior como rango adicional. Se identifican por
direcciones de instrucciones y destinos, sin inventar límites por proximidad.

**ACEPTO:** lectura de estado y escritura MMIO en SGC DFE.
**RECHAZO:** llamar a ese RMW un ack de fin DMA: el bit hardware no está
documentado aquí. Los métodos resueltos y sus helpers de registro no leen ni
reconocen `0xf3850400/0xf3950400/0xf3a50400`, sus offsets `+0x20/+0x34/+0x50/+0xa4`,
ni kick `…0500` (`+0x100`), ni `…0900` (literal `…0400+0x500`).
El helper Ifmt previo `0x43ad7ea6` actualiza contadores locales y llama
`0x436d2528/0x436d2518`: ambos hacen RMW de campos de 13 bits del registro
`base+0xa3310`, es decir `0xfc0a3310 / 0xfc0a4310`. También es otro banco,
sin lectura/ack APL. Su constructor `0x436d2598` fija las mismas bases.

**PARCIAL:** los nombres RTTI identifican clases, no la semántica eléctrica
de SGC ni una correspondencia de sus canales con APL. El desplazamiento
`0x1000` entre unidades tampoco prueba identidad con los tres bancos APL.

## VERIFICADO / NO_VERIFICADO — bit 0x00200000

Se recorrieron todos los bytes para literales de 32 bits y todas las instrucciones
ya reconocidas en el proyecto para operandos escalares iguales a `0x00200000`
o `0x03380000`: 479 coincidencias crudas sin alineación y 49 instrucciones.
No equivale a desensamblado completo ni encuentra toda construcción aritmética
de máscaras. Resultados íntegros: `s35-causes-scan.json`.

- La máscara completa aparece como inmediato de una sola instrucción reconocida:
  `0x436cf958`, en handler0. Sus tres coincidencias crudas en
  `0x439885ba`, `0x43988826`, `0x43fe91f2` no tienen xrefs Ghidra al literal.
  Las decompilaciones exploratorias forzadas de las dos primeras fueron
  **descartadas** y el export final conserva consultas de datos: coincidencia
  de bytes no demuestra entrada de función ni tabla IRQ.
- `0x43ad6980`: `0x436cfd20(2)` escribe `0xfc01f154=2`, luego escribe
  `0xfc01f010=0x00200000`. `0x43ad6a96` escribe selector 0 y el mismo bit
  en `0xfc01f014`. `0x436cf0c8`, caso 2, usa el primero al registrar un
  handler de índice 2. **Es un enable/disable de otro dominio de registros**;
  no identifica por sí mismo el bit 21 del argumento `fact` de handler0,
  registrado con índice 9. Igual número no implica igual fuente física.
- Las únicas coincidencias crudas del bit con xrefs registradas están en
  `0x43bc1d58` y `0x43bf3820`. La primera se pasa desde el constructor
  `0x436d72e8` a `0x436d8774` junto a muchas tablas de configuración; no se
  recuperó conexión a la máscara de handler0. La segunda se consume como
  tabla de **ushort** en `0x4382678c`, no como palabra de causas IRQ.
- El uso `0x436c8962` pertenece a flags de configuración de objetos en
  `0x436c85a8`; `0x43ae80c2/0x43ae81f4` convierten flags con
  `0x43786fc0`. No se recuperó vínculo de esos espacios de flags con `fact`.

**ACEPTO:** bit incluido en el filtro de handler0 y ausente del conversor de
condiciones `0x43ad68e0`. **NO_VERIFICADO:** su nombre/causa física y banco.
El bit aislado no satisface ninguna condición no nula creada por ese conversor;
handler0 puede acumularlo, pero eso no crea un quinto callback.
No se encontró otra tabla de inicialización que asocie ese bit o la máscara
completa a estado APL. El alcance de búsqueda anterior no prueba su inexistencia
en código no reconocido, máscaras calculadas o información externa al blob.

## FRONTERA ESTATICA AGOTADA — cierre de este subproblema

**RECHAZO** la cadena propuesta APL → IRQ → callback →
`EC_VD_Post(0x4378f848)` / `int_LM_Send1st_Handler(0x43792750)`:
no existe una cadena recuperada que permita documentarla como cierre.
Los destinos virtuales sí son estáticos y quedan resueltos; no se atribuye
el bloqueo a una vtable que supuestamente solo resolvería el cargador.
La frontera encontrada es **bancos distintos y ausencia de correspondencia
hardware entre estado APL, factor DFE y tupla unidad/handle/frame/VD**.

**INFERENCIA:** esta activación SGC puede participar en un flujo de datos
mayor. Esa posibilidad no demuestra que su estado sea fin APL ni fin de integración.
**NO_VERIFICADO:** ciclo físico completo, cuadro propio/siguiente y captura
completamente electrónica. No hay cámara conectada ni verificación física real.

Para superar esta frontera hace falta una especificación fiable del bloque
hardware (routing APL→IRQ, significado del bit 21 y semántica de estado/ack),
o una **traza pasiva correlacionada** en cámara real durante una captura normal:
VD/lectura del sensor, transacciones de estado/ack APL y DFE, entrada de IRQ,
y observación de unidad/handle/secuencia al callback y consumidor. Una traza
solo de VD no basta. Debe obtenerse sin flashear ni cambiar firmware; si no
hay interfaz de traza capaz de observar esos MMIO internos, hace falta acceso
de instrumentación autorizado o documentación del SoC. No se ha realizado.

## Próximo paso exacto

La incógnita estática siguiente más útil es el **proveedor DMM importado en
`0x43561524`, tabla `base+0x14`, entrada `+0x2e4`** de S33: identificarlo,
seguir quién satisface Rendezvous `P+0x18c/+0x194` y secundario `P+0xbc`, y
conservar la identidad del handle hasta el lector real YC, con extents,
pitch/formato y propiedad/reciclaje. No se investiga esa importación en S35.
Aunque se resuelva, el fin de integración seguirá necesitando evidencia propia.

## Evidencia y validación

- [Hallazgos](../../analysis/ghidra/s35-findings.json),
  [barrido de causas](../../analysis/ghidra/s35-causes-scan.json),
  [auditor](../../analysis/ghidra/s35-audit.py),
  [resultado](../../analysis/ghidra/s35-audit.json).
- Exports JSON/C `s35-objects*` en `analysis/ghidra/`, con listing, xrefs,
  constructores, RTTI, métodos y helpers. Etiquetas S32 del exportador reutilizado.
  El escáner `S35Scan.java` no modifica el proyecto.
- Antes de la primera apertura se capturó `s35-integrity.json`; auditor
  primero falló por exports ausentes, luego PASS de SHA, slots, vtables,
  registros, máscara y hashes persistentes. Ghidra siempre
  **`-readOnly -noanalysis`**, bytes del proyecto contrastados con blob antes
  de cada export S32 y anotaciones transitorias revertidas.
- Binario y proyecto preservados; sin ejecutar firmware, cámara, paquetes,
  flasheo ni push. Sin `.git`: cambios sin commit.
- Ruff del auditor y mypy de `src`/auditor PASS; `ruff check src tests`
  conserva nueve avisos previos en cuatro tests ajenos, sin cambios allí.
- `pytest tests/knowledge -q`: **67 PASS**. Mantenimiento en cinco pasos,
  con total estable entre reconstrucciones antes y después de los derivados.

**VEREDICTO: CAMBIOS** respecto de ciclo físico demostrado. La acotación
estática de esta vía queda completada; el comportamiento físico sigue abierto.
