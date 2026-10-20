# S38 — DMM/OSAL y frontera de resolución en av-cam

18-10-2026. Análisis estático local; sin firmware ejecutado, cámara, flasheo,
instalaciones ni push. Resultado: **el enlace backend DMM → extents YC no
queda cerrado**. Receptor y escritor de respuesta siguen NO_VERIFICADO.

## VERIFICADO — integridad y método

Se leyeron íntegros S37 y S28, CURRENT y CONTEXT; `search.py claim` no
devolvió correcciones registradas para S37/S28/S33/S34. Esto no garantiza
ausencia de correcciones en prosa. Se usó la navegación de conocimiento
antes de investigar direcciones, incluida la advertencia histórica del pool.

Original: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/`
`nflasha3_unpacked_unpacked/av-cam.bin`, 11427236 bytes, base `0x43541000`.
SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Cada export verifica original y bytes de memoria del proyecto antes de exportar.
Se reutilizó exclusivamente `analysis/ghidra/silent-liro.gpr` con
`-readOnly -noanalysis`; el script no crea funciones, no cambia contexto ni
marca memoria constante. Manifiestos antes/después validan .gpr y archivos
de .rep; no se escribieron binarios ni el proyecto.

La técnica S28 se aplicó a literales, sus referencias, funciones contenedoras,
campos del mensaje y wrappers de recepción/envío; no se dedujo propietario
a partir del nombre de un cliente. Export íntegro de las funciones existentes,
con pseudocódigo y listado, en `s38-scan`, `s38-transport` y `s38-routing`.
Los límites de funciones son los existentes: por ejemplo, el cuerpo Ghidra
435676fc incluye instrucciones desde 4356761c; no es un ABI nuevo validado.

## VERIFICADO / PARCIAL — pool, campos y servidor no recuperado

Barrido byte a byte, incluso desalineado: **85** palabras `0x0061003c`.
De ellas **16 no tienen referencias Ghidra**; cero operandos escalares
completos `0x61003c` en instrucciones ya definidas. Esto no cubre toda
construcción MOVW/MOVT, aritmética, código no definido ni altas externas.
El primer export contiene 73 consultas, 72 decompiladas y una ausente
(cabecera 43541000); los otros exports amplían helpers y campos auxiliares.

| Función / sitio | Evidencia recuperada | Clasificación |
|---|---|---|
| 4359321c, llamada 43593262 | Solicitud DMM cmd 1, 0x18 bytes; usa literal 435932a4=61003c | VERIFICADO: cliente |
| 435932a8, llamada 435932e8 | Cmd 4, flag 2; mismo pool | VERIFICADO: cliente |
| Literales 435932a0/43593318 | Ambos contienen bf0274; se pasan a 43a49628 | VERIFICADO: campo auxiliar distinto del pool |
| 43a49628 | Guarda argumento en objeto+0xc | VERIFICADO |
| 435aa068 / 435aa20c | Reserva por 435612d0(pool,...), copia payload y campo auxiliar; llama wrapper sync/async | VERIFICADO |
| 43a49adc | Guarda el campo auxiliar en payload-4 | VERIFICADO |
| 43651694 / 436519c0 | Cmd 6/5, pool 61003c, campo auxiliar 56015c | VERIFICADO: otros clientes |
| 43561260 | Recepción importada por tabla+1e0 | VERIFICADO: wrapper, no servidor |
| 43561524 | Llamada indirecta por tabla+2e4 | VERIFICADO: wrapper, no allocator local |

**ACEPTO:** 61003c sirve como pool compartido por servicios diferentes.
**RECHAZO:** inferir un dispatcher DMM local solo por ese literal o por
llamadas de reserva/envío. A diferencia de S28, no se recuperó un bucle que
reciba ese ID, una tabla de comandos servida por él, ni un alta con callback.
Tampoco se demostró el servidor de bf0274; es un campo auxiliar comprobado,
no un destino efectivo adjudicado sin implementar el transporte externo.

**PARCIAL:** los clientes corroboran la familia de protocolo S37, pero
pool compartido y semejanza de solicitudes no identifican el proveedor
del slot 2e4. No se corrige la observación S37 de que libmprctrl llama
osal_snd_msg con 61003c; se limita su interpretación como servidor local.
**NO_VERIFICADO:** alta/servidor real, traducción de envolturas y escritor
de reply+0x10/+0x14. No hay cuerpo servidor encontrado que decompilar.

## VERIFICADO — no hay resolución ELF consultable

`readelf -dW`, `readelf -rW`, `nm -D` y `nm` sobre el original retornan 1:
«Not an ELF file» / «file format not recognized». Evidencia literal en
`analysis/ghidra/s38-object-tools.txt`. Los primeros bytes son
`0a0000ea4f52494c04000000`: instrucción ARM y ORIL (representación little
endian de la magia LIRO), versión 4. **No es un ejecutable ELF monolítico**
identificable con estas herramientas, sino un blob LIRO.

**RECHAZO:** afirmar DT_NEEDED hacia libmprctrl.so o libInfraScalarMpr.so
desde av-cam, o interpretar los errores como una ejecución correcta que
mostró una sección dinámica vacía. No hay tabla dinámica ELF consultable.

Cadena contrastada con bytes y listado:
`[43561538]=00abd9b6 + PC 4356152e + [4356153c]=16dc = 440205c0`;
`[440205c0]=43541000`; `[base+14]=435410b4`;
`[435410b4+2e4]=[43541398]=0`. El slot de recepción +1e0 también es cero
en archivo. No existe ahí una dirección de función que se pueda seguir.

**FRONTERA ESTATICA AGOTADA**, exclusivamente para resolver el valor externo
del slot +2e4 por símbolos/relocaciones ELF de este blob. La búsqueda local
no recuperó el receptor, pero sus lagunas no prueban su inexistencia universal.
**INFERENCIA:** el entorno de carga debe proporcionar la interfaz para que
esas llamadas funcionen. S20 documenta previamente carga/API desde liro.ko
([antecedente](s20-mailbox40193-osal-architecture.md)); S38 no audita ese
módulo ni identifica qué símbolo suyo satisface exactamente +2e4. Cerrar
ese binding exige salir de este blob al loader/tabla de kernel.

## NO_VERIFICADO — P, APL y captura física

Sin escritor de respuesta ni mismo ID/clave recuperado, no hay enlace nuevo
desde los pares remotos a P+18c/P+194/P+bc ni a f3850400/f3950400/f3a50400.
No se atribuyen dominio físico/bus/virtual, píxeles, pitch, fin DMA ni cierre
electrónico de exposición. Los resultados S31–S37 se conservan.

## Próximo paso exacto

Prioridad siguiente de captura: **enum de formato PARCIAL de S33**.
Seguir `input+0x38 ← P+0x1b4 ← context[2]+0x28` y el conversor
`0x43814d24` hasta sus consumidores de configuración APL; contrastar bits
de formato, stride y tamaño con tablas/operaciones inequívocas. Remapeos
0→2,1→0,2→1,3→5,4→3,5→4 y agrupación APL no autorizan nombres YUV.
Entregable: tabla valor software → campo hardware → geometría/pitch,
dejando sin nombre cada caso que carezca de evidencia. No reabrir como
primer paso los 26 llamadores AllocShare ni confundir kick con fin DMA.

## Validación

Auditor `analysis/ghidra/s38-audit.py`: primero falló por export elegido
incorrectamente para el wrapper 2e4; corregido para consultar s38-scan,
luego falló por findings ausente antes de crearlo. Verifica SHA, ORIL,
cadena PIC, slots cero, integridad del proyecto y fallos de herramientas ELF;
imprime la tabla clasificada final. No valida comportamiento físico.

Resultado final: auditor PASS; Ruff/mypy del auditor PASS; mypy src PASS.
Ruff src/tests conserva nueve avisos previos en cuatro tests sin tocar.
Conocimiento: **67 PASS**. Mantenimiento obligatorio en cinco pasos:
grafo estable **1455 entidades / 2768 relaciones**. Exports scan/transport/
routing: 72/76/81 decompilaciones completas respectivamente (hay duplicados
entre exports, no son 229 funciones distintas).

**VEREDICTO: CAMBIOS** para el cierre backend→YC solicitado; **ACEPTO** la
frontera limitada y el siguiente objetivo concreto. No hay .git disponible;
cambios sin commit.
