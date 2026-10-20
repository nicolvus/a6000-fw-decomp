# S45 — identidad del contexto y cierre físico pendiente

Sesión 18-10-2026. Última sesión de la serie explícita S40–S45;
el hito de control de modo/exposición IMX210 permanece abierto para S46+.
Continúa [S44](s44-register-consumer-mode-table.md), sin releer S31–S43 completos.

## VERIFICADO — método e integridad

Único proyecto abierto: `analysis/ghidra/silent-liro.gpr`, programa `av-cam.bin`,
siempre `-readOnly -noanalysis`, sin guardar ni crear funciones.
SHA-256 del archivo antes de decompilar y después de las consultas:
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
S41Export contrasta además todos los bytes cargados con el archivo.
El auditor S45 comprueba los manifiestos históricos de `.gpr/.rep`.
Sin firmware ejecutado, cámara, flasheo, instalaciones, producción ni push.
No se reabrieron OSAL bit31, AF ni el consumidor/virtual+a8 de S44.

Se aplicaron knowledge-navigation y contradiction-audit; `claim` de S44
se consultó antes de reutilizar sus conclusiones. Se consultaron exports
puntuales anteriores, no informes completos S31–S43.
Exports nuevos: `analysis/ghidra/s45-*.json/.c/.log`, inventario `s45-scan.json`,
resumen `s45-findings.json` y auditor `s45-audit.py`.
Dos intentos de listado cruzaron datos y fallaron; el listado válido se repitió
con límites de código (`s45-context-init3.log`). No se interpretan esos datos
como instrucciones ni se usa un pseudocódigo ausente como evidencia.

## VERIFICADO — origen concreto del contexto de 437b5b14

| Evidencia | Resultado |
|---|---|
| `437b4eb4`, listado `s45-root-call-listing.json` | Construye r4=`43eaadd8` mediante literal `437b4ef8` + PC `437b4eca`; llama `437b4df0` en `437b4ed2`. |
| `437b4df0`, llamada `437b4e10` | Conserva argumento1 y llama `437b5b14`. Esta pasa el mismo argumento a `4382dd78` en `437b5bda`. |
| `437b4f2c`, listado `s45-context-init-listing.json` | En su rama de preparación copia `0xb0` bytes del contexto recibido a `43eaadd8` (`437b4f6e`). Otra rama despacha directamente un trabajo; no afirmar copia incondicional. |
| `VD_Pre`, `43794096/9e` | Copia raíz `43e9b548` a `43e99514` con `43ae8faa`; reconstruye contexto `43e993a4` con `43ae8eae`. |
| `437940be/c4` | Entrega ese contexto reconstruido a `437b4f2c`, bajo guard del bit4. |
| `43ae8d56` | Inicializa contexto[0x14]=raíz+`1e6c`. Los siete helpers siguientes de `43ae8eae` no sobrescriben `+50`. |
| `43ae8faa` | Copia raíz+`1e6c` a destino+`1e6c`, tamaño `1a4`. |

Así, después de esa preparación, **C=`43e9b380`**, origen del contenido
`43e9d3b4`, por copia de `1a4` bytes. `43eaadd8+50` contiene cero en archivo:
la identidad procede de las escrituras de inicialización, no del valor inicial.
El barrido de xrefs omite código Thumb no definido: se recuperaron llamadas
y listados temporales sin modificar la base de Ghidra.

## PARCIAL — relación P/C y valor 2

P de `437b43b4` sigue siendo argumento1+`2bc`. Los llamadores
`437f88ec` y `43affe80` pasan su propio argumento1+`1198`, por tanto
P=argumento1_del_llamador+`1454` en esas rutas (`s45-p-origin.json`).
Esto no identifica ese argumento dinámico con ninguna de las raíces anteriores.

**NO_VERIFICADO:** copia o transformación entre P y C. C tiene ahora una
identidad recuperada, pero no está demostrada su equivalencia con P ni con
`43ef2474`. El snapshot de S44 copia condicionalmente `6b0` bytes desde P;
la preparación anterior copia `1a4` bytes desde otra raíz. Ni tamaños distintos
ni offsets iguales prueban que jamás exista otra copia intermedia.
Por ello no se transportan a C las condiciones de P+`95=2` de `4385cf2c`.
La copia C+94/+95→B+36/+37 en `4382dd78` permanece demostrada;
B=`43eae270`→G=`43ea6ad4`→`43842158` se conserva como antecedente S44,
sin atribuirle este productor de 2. Falta el escritor de `43e9d3b4+94/+95`
o una copia con identidad y orden temporal demostrados desde P.

## VERIFICADO — lector real de IMX210+3a0

`*(43fcc090+74)=43ad9203`: la vtable IMX210 publica el método Thumb
`43ad9202`, bytes `b0 f8 a0 03 70 47`:
`ldrh.w r0,[r0,#3a0]; bx lr`. Es un lector del objeto real, no un offset
coincidente en otro objeto. `s45-getter-listing.json` lo recupera fuera de una
función correctamente delimitada; el decompilador lo asociaba al cuerpo previo.

`43ad90b6` carga objeto desde el contenedor, su vtable y virtual+74.
El getter `436d6118` proporciona ese contenedor a `438c828c`, que también
llama al wrapper de exposición `436d6320` sobre él. Se conserva la identidad
IMX210 establecida por constructor/factoría, sin atribuir a otros objetos los
lectores de +3a0 del inventario global.

En `438c835e` el retorno del wrapper queda en r6. Bajo condiciones
objeto_de_captura+740=0 y consulta `43a12c64()!=3`, calcula:

`q = división_entera(1000 * captura[56c], retorno_436c28d0)`;
`captura[570] = división_entera(1000000 * (IMX210[3a0]+1), q)`.

El literal `438c845c` es exactamente 1000000. Se documenta la aritmética
sin asignar unidades eléctricas no recuperadas. El store está en `438c8388`.
El valor se usa antes de restaurar captura[570] al valor anterior al final.

## PARCIAL — timing hasta acción del controlador

`438c828c→43795dec(tipo,captura+548,...)→43ad3b92→436c74c8`.
El adaptador pasa captura+56c/+570 como argumentos3/4. El controlador
guarda argumento4−1 en objeto+38; después entrega ese valor y argumento3−1
a `43ad2bd6`. Este escribe:

`*(u32*)(base+220) = (argumento3-1)*65536 + (argumento4-1)`.

Hay retorno temprano si la configuración almacenada coincide: la escritura
no es incondicional. **VERIFICADO:** dependencia del timing calculado hasta
una escritura indirecta del controlador; ya no es solo cálculo sin consumidor.

`436c2270` obtiene el controlador desde global `43e78f3c`.
Inicialización Thumb `436c2520`, store `436c254a`: global=owner+`e10`;
PIC=`4401eee4`, slot=`4402045c`, owner=`43e15f18`, objeto=`43e16d28`.
La base empleada por `43acee62(objeto+4)` es `*(43e16d2c)` y vale cero
en el archivo. Falta su escritor de inicialización. Por tanto **NO_VERIFICADO**
que el destino base+220 de esta ruta sea un banco MMIO concreto. No se
confunde con los bancos del transporte de registros ya probados en S44.

**INFERENCIA:** la transformación ajusta una duración del controlador en
función del timing IMX210. **NO_VERIFICADO:** inicio/fin físico de integración,
VD efectivo, lectura YC válida y ausencia de movimiento de cortinas.

## NO_VERIFICADO — semántica eléctrica ID0 frente a IDs3–8/144–149

S44 demuestra selección del byte ID0 y transporte a bancos físicos de comandos;
eso no aporta el nombre eléctrico de los bits del sensor. S45 no recuperó
datasheet, strings ni tabla con identidad que etiquete ID0 o esos IDs como
integración/read-enable/VD. La dirección MMIO del transportador no identifica
por sí sola la función del registro del sensor. No se afirma ausencia universal
de strings ni agotamiento de esta rama: no se completó un inventario semántico.

## Pendiente real

P→C sigue PARCIAL. Lector IMX210+3a0 cerrado; su efecto sobre el controlador
está seguido hasta base+220, pero la base física y el efecto eléctrico faltan.
También faltan semántica ID0 y demostración de fin electrónico/cortinas.
La serie explícita S40–S45 termina aquí; **el hito continúa abierto en S46+**.
No hay frontera estática agotada: quedan escritores y copias concretos por
resolver. No se activa Línea E ni se abre A6300; no se transportan offsets.

## Próximo paso exacto

1. Resolver escritores de `43e9d3b4+94/+95` (raíz `43e9b548+1e6c`),
   incluyendo construcción mediante offsets partidos/copias, y contrastarlos
   con P=padre+1454 y snapshot43ef2474 antes de propagar valor2 a B/G.
2. Resolver el store de base en `43e16d2c` desde inicialización de owner
   `43e15f18`; contrastar el destino +220 y sus bits con el controlador VD.
   No repetir la búsqueda del getter+74 ni consumidor/virtual+a8 de S44.
3. Solo con base y semántica recuperadas, evaluar vínculo con integración,
   lectura/VD y cortinas. No declarar cierre físico por una escritura indirecta.

## Validación

Auditor S45: primer ensayo falla por resumen ausente; siguiente detecta una
transcripción decimal incorrecta de raíz/C; corregida contra los literales,
PASS. Contrasta SHA, memoria exportada, `.gpr/.rep`, contexto, getter y constante.
`pytest tests/knowledge -q`:67 PASS(6.72s). Ruff auditor PASS; mypy src+auditor
PASS(6 archivos). Ruff src/tests conserva nueve avisos previos en tests ajenos,
sin avisos nuevos en lo tocado. Mantenimiento completo ejecutado: ambos builds
1455 entidades/2777 relaciones/58 CORRECTS/SUPERSEDES, grafo estable;
56 correcciones y55 preguntas exportadas. Detalle en `knowledge/PROGRESS.md`, S45.
Sin `.git` utilizable: cambios sin commit.

**ACEPTO** contexto concreto y consumidor real del timing hasta controlador,
con las condiciones descritas. **RECHAZO** alias P/C por offset y cierre de
integración o MMIO de base+220 sin resolver su base.
**VEREDICTO: CAMBIOS** para cierre físico del hito.
