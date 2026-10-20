# S49 — productor de configuración de captura: servicio `0x301d7`, clave `0xce`, campos `+0x1c/+0x1e`

Sesión 19-10-2026; continuación de [S48](s48-service-table-provider.md). Hito S46–S52 **abierto**.
Sin firmware ejecutado, sin cámara, sin flasheo, sin git. Evidencias en `analysis/s49/`.

## Resumen

Las 314×(1–2) coincidencias de `d7 01 03 00` en `libObj`, `libInfraMediaCommon`, `libsencore` y `adjstctl` son **una tabla
compartida de nombres de comandos, no productores**. Los productores reales son otros: (1) el puente USB/«Senser» de
`libsencore.so` y (2) cuatro funciones de `libObj.so` que solo usan las claves 0, 1 y 0x67. La tabla de servicios de
`av-cam.bin` la inicializa el módulo de kernel **`liro.ko`**. La clave `0xce` es el comando **`S_IMAGER_CURTAINMODE`**.

## VERIFICADO

1. **Tabla de nombres (no productor).** Registros de 72 B `{u16 bloque, u16 código, char nombre[64], u32 id_OSAL}`;
   en `libInfraMediaCommon` hay 314 con id `0x301d7`, bloque `0x0404`, código `(clave<<16)|0x0404`
   (`libsencore`: 4 series; `libObj`: 235+77+2+… ; `adjstctl.elf`: 314). Ningún código las referencia por
   PC‑relativo (`analysis/s49/scan.py`; `libObj`/`libInfraMediaCommon`/`libsencore` = 0) salvo `libsencore`, que
   usa la tabla grande `0x2d0a4` (1065 registros, `0x429`) en `TransactionStart`.
2. **Clave `0xce` = `S_IMAGER_CURTAINMODE`.** 223 de las 224 claves de la tabla de handlers de `av-cam.bin` en
   `0x43ff23b0` (S47) tienen nombre en esa tabla; `0xce`→handler `0x43789709`. Prefijos: `S_` ajustar/fijar, `A_` ajuste,
   `C_` comprobar, `G_` general (convención leída de los nombres, no de documentación).
3. **Callbacks VD_Pre de la familia de obturador** (`analysis/s49/rows2.json`, filas de 12 B `{clave, slot, clase}`):
   `0xce` slot `0x43ff7414`→`0x437dad79`; `0xed S_SHUT_MIN_MANU` →`0x437dadad`; `0xb7 A_NONLINEAR_ELEC_SHUT`→`0x43af7733`;
   `0xba A_MK_SHUT_BLAG_CHK`; `0x3f/0x4d A_MK_SHUT_N/O`; `0xb5 A_MK_SHUT_DSLR`. El callback de `0xce` y el de `0xed`
   leen el mismo par `(u16 a, u16 b)` del payload: `a≠0 → flag=1` y el valor `b` (`0xce`: `C+0x94=1, C+0x95=b&0xff`;
   `0xed`: `C+0xa0=1, C+0x9e=b`). Los callbacks `A_*` escriben en `C+0x60` el **id del comando de ajuste activo**
   (37 stores `str rX,[r1,#0x60]`: `0x3f,0x4d,0xb5,0xb7,0xba`…) y `0xb7` pone a 1 `C+0xbc/+0x10a/+0x114`.
   Conclusión: `+0x1c/+0x1e` = `(habilitar, valor)` de un comando de ajuste/servicio.
4. **Productor del paquete (userland).** `libsencore.so`: `SubsystemCommunicationCommand::TransactionStart` (`0x25fc8`)
   construye el mensaje OSAL de `0x140` B desde un `SenserPacket` USB: `msg+0x18=u16(param_3)` (bloque, `0x0404`),
   `msg+0x1a=u16(param_3+2)` (código/clave; bits `0x1800` = nivel de ajuste), `msg+0x1c…` = payload copiado con
   `Serialize(SenserIfReceive, …, ≤0x124)`. Busca `(bloque, código&0xff)` en la tabla `0x2d0a4` (paso `0x48`, tope `0x429`)
   y toma como **id OSAL** el último u32 del registro (`0x301d7`; bit31 si `selectLSI`); envía con `testcmd_sndmsg`
   (modo test) o por escenario `APP_TESTCMD`; `DoExecute` (`0x25b38`) usa `osal_snd_sync_msg`. Layout idéntico al que lee
   `0x437d9f9c` en `av-cam` (S47: `+0x18/+0x1a/+0x1c`). Los valores proceden, por tanto, del **host USB de servicio**
   (o de `adjstctl.elf` / `libtestcmd.so`, que imprime «adjust block/code, OSAL ID, cmdname»).
5. **Otros emisores con literal `0x301d7`.** Solo `libObj.so` (`0x7b4540` ping clave 0; `0x7b45a4` sondeo clave 1 con
   respuesta `0x108`; `0x7b464c` clave `0x67`=`S_LC_PRESET` con `(arg0,arg1)` en `+0x1c/+0x1e`; `0x7b46c4` envoltorio;
   llamado desde `0x7b4718`, que lee `Backup_read` — cadena de la brújula `compass_*`). No envían `0xce`. `libNetService`
   (`0x973e0`) es una coincidencia (literal de log). Búsqueda `movw #0x1d7/movt #3` en todos los ELF de `nflasha15`: 0.
6. **Inicializador de la tabla de servicios de `av-cam`.** `kmod/liro.ko` («LIRO 4‑MUSASHI», capa µITRON bajo Linux):
   `tsk_entry` abre `fn=/system/av-cam.bin` (configurado por `bin/im.elf`: «fn=/system/av-cam.bin load=1 debug=1»),
   comprueba magic `'LIRO'` (`av-cam.bin+4=0x4c49524f`) y versión 4, y hace
   `memcpy(hdr[0x14]+0x24, tabla_API, 0x344)` antes de llamar a `entry_pre`. Con `hdr[0x14]=0x435410b4` la tabla va en
   `0x435410d8`; el índice 113/114/119 cae en `0x4354129c/0x435412a0/0x435412b4` = **`osal_unreg_msg_queue_cb`,
   `osal_reg_sync_msg_queue_cb`, `osal_dynamic_id`** (relocaciones `.rel.init.data` de `liro.ko`). Los wrappers
   `0x43561298/0x435612b4/0x43561324` de S48 son exactamente esos: `(0x301d7,…)` desregistra, `(0x301d7,ctx,cb,0)` registra
   el callback `0x43789cc1`, `(0x52,0,ptr)` pide id dinámico. Resuelve el «proveedor» de S48.
7. **Invocador del callback.** El registro es `osal_reg_sync_msg_queue_cb` (cola de mensajes síncronos): el callback se
   ejecuta cuando algún cliente llama a `osal_snd_sync_msg` con el id `0x301d7` (p. ej. `libsencore DoExecute`), vía el
   OSAL del kernel. La semántica «síncrona en el hilo del emisor» es **inferida del nombre de la API**; no se analizó el kernel OSAL.

## PARCIAL / NO_VERIFICADO

- Qué componente emite `S_IMAGER_CURTAINMODE` **en funcionamiento normal** (fuera de la herramienta de servicio USB y
  `adjstctl`): no localizado. Ningún ELF de `nflasha15` contiene el código `0x00ce0404` ni emite clave `0xce` de forma directa.
- Valor real de `b` y su significado por modo: sin evidencia; el nombre `CURTAINMODE` es **inferido** (texto de la tabla),
  no demostración de que seleccione cortina mecánica/EFCS/electrónica.
- `libObj.so` (17 MB): la sesión REA superó el límite RSS 3,8 GB del demonio y se cerró (watchdog); se analizó por bytes
  y desensamblado `llvm-objdump`. No se usó Ghidra histórico: REA reconoció todas las funciones necesarias en las
  librerías pequeñas; las Thumb de `av-cam` se desensamblaron por bytes (copia ELF temporal), sin ver ausencia en REA.
- Emisión de los 311+ restantes nombres/ids de la tabla grande `0x2d0a4` (otros id OSAL) sin clasificar.

## Modalidades de captura y final electrónico de la exposición (comparación)

Los comandos del conjunto «obturador» entran por la **misma cola** `0x301d7` y se consumen en VD_Pre (clase 1) o por
tablas de configuración (clases 2/3/6): `A_MK_SHUT_N/O/DSLR/BLAG_CHK` (variantes de obturador mecánico),
`A_NONLINEAR_ELEC_SHUT` y `A_LINEAR_ELEC_SHUT` (modos de obturador **electrónico**), `S_SHUT_MIN_MANU`, `S_HIGH_SHUT`,
`S_IMAGER_CURTAINMODE`. Son **parámetros de ajuste/sincronización del imager** (flags en `C`), no la eliminación de
las cortinas mecánicas: nada demuestra aún qué modo de captura normal los pone ni que alguno finalice la exposición
sin cortina. `0xb6 A_LINEAR_ELEC_SHUT` no aparece en el barrido de `C+0x60`; su callback queda por localizar.

## Siguiente objetivo técnico (S50)

Localizar los consumidores de `C+0x94/+0x95`, `C+0x60`, `C+0xbc/+0x10a/+0x114` y de `A_LINEAR_ELEC_SHUT (0xb6)` dentro de
`av-cam` (REA `xrefs`/`trace_native_values` en sesión única) y relacionarlos con VD/obturador; opcional: decodificar el
protocolo Senser (`Usb::handle_input`) para fijar qué rol (servicio vs. app) puede enviar la clase `0x0404/0xce`.

## Integridad y reproducción

SHA‑256 de las 7 entradas en `analysis/s49/inputs.sha256`; `av-cam.bin` `b60c845c…56bb9` sin cambios; manifiestos
`firmware/ghidra-dir/silent-liro.final.sha256` verificados (0 discrepancias). Salidas REA brutas: `analysis/s49/rea-p*.jsonl.gz`.
Desensamblado de `av-cam`: `llvm-objcopy -I binary -O elf32-littlearm --rename-section .data=.text,alloc,load,readonly,code
analysis/rea-independent/input/av-cam.bin av.elf` y `analysis/s49/d.sh DIR_INI DIR_FIN` (base `0x43541000`).
