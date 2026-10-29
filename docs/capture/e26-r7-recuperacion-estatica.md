# E26-RECOVERY R7 — informe final de ingeniería inversa exhaustiva

29-10-2026. Continúa [R6](e26-r6-recuperacion-bionz.md) y [R7B](e26-r7b-recuperacion-prelinux.md). Investigación exclusivamente offline, mediante REA y desensamblado ARM/Thumb sobre `av-cam.bin`, `loader3.bin` (extraído de `bootloader.bin`, SHA-256 `8fd98a41…`), `libupdaterbody.so`, `nand.ko`, `lld.ko`, `mumin.ko` y BossFirm/SRAM histórica ARM7. Sin conectar, encender, depurar ni modificar la cámara. Sin firmware generado para escritura.

---

## Resumen ejecutivo

Tras R7 no se ha encontrado ninguna ruta de restauración utilizable antes de `nflasha3`. Todas las vías pre-Linux examinadas terminan en:

1. **Bucle de LED infinito** (`FUN_c01f3b74`) ante cualquier fallo de inicialización o carga de kernel, sin retorno al selector ni selección de UPDATER.
2. **Salto directo al kernel** tras `FUN_c01f04b6`, tanto en modo COLD (dispositivo 3 / `nflasha3`) como en modo UPDATER (dispositivo 1 / `nflasha1`). El modo UPDATER no es un entorno de recuperación independiente: carga `vmlinux`+`initrd` desde `nflasha1` y salta al kernel, igual que COLD.
3. **Escrituras NAND solo existen en entorno Linux** (`nand.ko` + `lld.ko` + MuMin/BOSS → ARM7). No hay interfaz pre-Linux demostrada para invocarlas.
4. **No se ha demostrado escritura selectiva de `nflasha3`** preservando metadatos, ECC, bloques defectuosos y calibraciones.

La única vía de recuperación teóricamente identificada es el selector `updater/mode` en Loader3, pero su activación externa independiente no está demostrada y requiere BOSS, dispositivo 2 (FAT), dispositivo 1 (kernel/initrd) y todo el entorno de arranque funcional.

---

## 1. Prioridad A — Rutas de arranque del BIONZ (VERIFICADO EN BINARIO)

### 1.1 Punto de entrada: `FUN_c01f11ec` (0xc01f11ec)

El flujo de arranque de Loader3 comienza en `FUN_c01f11ec` (REA verificado, `r7b-cold-rea.json`):

```
FUN_c01f11ec:
  iVar2 = FUN_c01f0cca()      // inicialización completa de hardware
  if (iVar2 == 0) {
    iVar2 = FUN_c01f1de6()    // comprobación de estado BOSS/Backup
    if (iVar2 == 0) {
      local_10 = FUN_c01f2156()  // lee modo de arranque (*DAT_c01f248c)
      switch (local_10) {
        case 1,2,3,4,5,6,10,0xb,0xc:  iVar2 = FUN_c01f1312(&local_10);
        case 7,8,9,0xd,0xe:           iVar2 = FUN_c01f03e2(&local_10);
        default:                      error "LD3_E_Inv_bootmode"
      }
    } else {
      error "LD3_E_Chk_bootmode"
    }
  } else {
    error "LD3_E_Chk_bootmode"
  }
  FUN_c01f3b74(iVar2)   // ← SIEMPRE: bucle de LED infinito, sin retorno
```

**`FUN_c01f0cca` (0xc01f0cca)** — inicialización completa, verificado en `r5-rea.json`:
1. `FUN_c01f5130()` — Init Sync
2. `FUN_c01f55dc()` — Init Power
3. `FUN_c01f686c()` — Init UDIF_P
4. `FUN_c01f68a4()` — Init UDIF_D
5. `FUN_c01f2a48()` — Reinit BOSS (si falla → error `LD3_E_Reinit_BOSS`)
6. `FUN_c01f5f18()` — Wake DDR
7. `FUN_c01f39de()` — Wake DGU (si falla → retorna -0x12d)
8. Comprobación de flags DDR/serial/carga
9. `FUN_c01f2a4c(uVar6)` — Init BlkDev (si falla → error `LD3_E_Init_BlkDev`)
10. `FUN_c01f3d50()` — Init FAT (si falla → error `LD3_E_Init_FAT`)
11. `thunk_FUN_c01f49d2(uVar6)` — Switch_Bkup (si falla, intenta `FUN_c01f159a()`)
12. `FUN_c01f35c0()` — Init_DbgLv
13. `FUN_c01f5948()` — Init_Pwr2nd (si falla → retorna -0x12f)
14. `FUN_c01f21c6()` — (si falla → retorna -0x12f)
15. `FUN_c01f3514()`, `FUN_c01f4ef8()` — retorna 0

**`FUN_c01f1de6` (0xc01f1de6)** — comprobación de estado BOSS/Backup, verificado en `r5-rea.json`:
- Llama `FUN_c01f50f4()`; si retorna 2, verifica `FUN_c01f159a()`
- Lee configuración de Backup en `DAT_c01f1ef4 + 0x20`, `+4`, `+0x1b`
- Comprueba flags `BOM_chk_reboot`, `BOM_chk_keychat_off`, `BOM_chk_chg_key_off`
- Llama `FUN_c01f1d6a()`, `FUN_c01f1c70()`, `FUN_c01f5e74()`, `FUN_c01f281e()`, `FUN_c01f27c4()`
- Retorna 0 si todo OK, non-zero si hay error de estado BOSS/Backup

**`FUN_c01f2156` (0xc01f2156)** — obtiene modo de arranque: retorna `*DAT_c01f248c` (variable global).

### 1.2 Despacho por modo de arranque

| Modo | Función destino | Descripción |
|------|----------------|-------------|
| 3 | `FUN_c01f1378` | UPDATER: carga `vmlinux`+`initrd` desde dispositivo 1 |
| 1,2,4,5,6,10,0xb,0xc | `FUN_c01f09e4` | Arranque normal (0xc = COLD) |
| 7,8 | `FUN_c01f036c` | WARM/HOT — **no examinado aún** |
| 9 | `FUN_c01f129c` | — **no examinado aún** |
| 0xd | Load Image OFF | — |
| 0xe | Normal load HotOFF | — |
| >0xf / default | Error `LD3_E_Inv_bootmode` | → `FUN_c01f3b74` (LED bucle) |

### 1.3 Modo COLD: `FUN_c01f09e4` (0xc01f09e4)

Para modo 0xc (COLD), verificado en `r7b-cold-rea.json`:

```
FUN_c01f09e4 (modo 0xc):
  FUN_c01f6ada(1)           // Reset_Bkup
  FUN_c01f3514()
  FUN_c01f60c2()
  FUN_c01f5a68(mode)        // Pwr_bootmode — si falla → error
  FUN_c01f5614()            // Del_LOG
  FUN_c01f5eae()
  FUN_c01f2be6()            // si cualquiera falla → bVar1=false
  // limpieza de kLog si es necesario
  FUN_c01f2934()            // Init_boottime
  FUN_c01f5eae(), FUN_c01f5614() // logs de versión
  // comprobación de BIONZ/imager según modo
  // para 0xa,0xb: FUN_c01f16e2()
  // para 0xc: FUN_c01f2ba6()
  // lectura de configuración desde Backup/DAT
  FUN_c01f3c44()            // para modos 10,0xb
  FUN_c01f5b66()            // para modos 10,0xb
  FUN_c01f5b2a()            // carga de configuración
  // para modo 0xc: FUN_c01f2c06() (lectura de partición)
  // para modos 10,0xb: FUN_c01f2ba6()
  FUN_c01f5b2a()            // segunda carga de configuración
  FUN_c01f3564()            // para modo 2
  FUN_c01f2e20(3)           // para modos 2,0xa,0xb,0xc
  FUN_c01f2fe8(0x2000000\|0x100000) // carga de archivo de configuración
  // segundo bloque de carga para modos 2,0xa,0xb,0xc
  FUN_c01f3108()            // para modo 2
  FUN_c01f5afe()            // para modo 2
  FUN_c01f5bfe()            // carga de vmlinux/initrd
  FUN_c01f48cc()            // finalización
  return 0
```

**Punto crítico:** Si `FUN_c01f09e4` retorna non-zero (cualquier fallo en carga de kernel, lectura de partición, configuración, etc.), el flujo vuelve a `FUN_c01f1312`:

```
FUN_c01f1312:
  iVar1 = FUN_c01f09e4(&local_10);   // para COLD
  if (iVar1 == 0) {
    ... // éxito: salir UDIF, llamar FUN_c01f4e0c, FUN_c01f0590, retornar 0
  }
  // iVar1 != 0:
  pop {r4,pc}   // retorna iVar1 (non-zero)
```

De vuelta en `FUN_c01f11ec`:
```
iVar2 = FUN_c01f1312(&local_10);
if ((iVar2 != 0) || (iVar2 = FUN_c01f04b6(local_10), iVar2 != 0))
    goto LAB_c01f1262;   // → FUN_c01f3b74(iVar2)
```

### 1.4 Salto al kernel: `FUN_c01f04b6` (0xc01f04b6)

Verificado en `r7b-cold-rea.json` y `r5-rea.json`:

```
FUN_c01f04b6(mode):
  if (mode != 3) {
    // logging de modo de kernel, etc.
  }
  // obtener dirección del kernel desde *DAT_c01f0768
  if (mode == 2 || mode == 10 || mode == 0xb) {
    // leer dirección desde Backup/DAT
  } else if (*DAT_c01f0768 != 0) {
    // ya hay dirección
  } else {
    uVar3 = FUN_c01f31ba();   // retorna *DAT_c01f3308
  }
  *DAT_c01f0768 = uVar3;      // guardar dirección de entrada del kernel
  FUN_c01f2214(0);
  FUN_c01f3450();
  if (mode == 3) {
    FUN_c01f028c();           // post-load específico de modo 3
  }
  uVar4 = FUN_c01f4fb0();
  log "LDR Jump to kernel 0x_X__luus"
  if (*puVar1 == 0) {
    log "LD3_E_addr_is_NULL"
    return 0xfffffed1 (-0x12e)   // → FUN_c01f3b74 (LED bucle)
  }
  if ((*puVar1 & 3) != 0) {
    log "LD3_E_addr_is_unaligned"   // ← PERO AÚN SALTA AL KERNEL
  }
  FUN_c01f5078();               // preparación pre-salto (no examinado)
  (*(code *)*puVar1)();         // ← SALTO AL KERNEL
  return 0;
```

**Hallazgo clave:** Si la dirección del kernel es NULL, se retorna -0x12e → `FUN_c01f3b74` (bucle LED). Si está desalineada, se registra error pero **aún así se salta al kernel**. No hay comprobación de integridad ni firmware de sustitución.

### 1.5 Manejador de error: `FUN_c01f3b74` (0xc01f3b74)

Verificado en `r7b-cold-rea.json`:

```
FUN_c01f3b74(param_1 = código de error negado):
  FUN_c01f6d0c();                    // inicialización
  uVar6 = delay(-param_1, 1000);     // retraso basado en código de error
  uVar4 = delay(high(uVar6), 100);
  delay(-param_1, 100);
  log "ERROR__Blinking_LED_LDR2__d_LNG__"  (uVar6, uVar4, ...)
  log "ERROR__Loader_boot_failed__"
  FUN_c01f3884();                    // init LED/hardware (no examinado)
  FUN_c01f5008();                    // init UART (no examinado)
  iVar3 = DAT_c01f3c40;
  iVar5 = iVar3 >> 1;
  iVar1 = iVar3 >> 2;
  iVar2 = iVar3 >> 3;
  do {                               // ← BUCLE INFINITO
    FUN_c01f379a();                  // toggle LED (no examinado)
    FUN_c01f6d18(uVar6, iVar3);      // LED on/off con patrón
    FUN_c01f4f88(iVar5);             // retraso
    FUN_c01f6d18(uVar4, iVar1);
    FUN_c01f4f88(iVar5);
    FUN_c01f6d18(extraout_r1, iVar2);
    FUN_c01f4f88(iVar3);
  } while (true);                    // NUNCA RETORNA
```

**Conclusión:** `FUN_c01f3b74` es un punto sin retorno. Cualquier error en la cadena de arranque (fallo de inicialización BOSS, fallo de lectura FAT, fallo de carga de kernel, dirección NULL del kernel) termina en este bucle de parpadeo de LED. No hay:
- Retorno al selector de modo
- Selección automática de UPDATER
- Carga de una copia secundaria del kernel
- Estado de servicio accesible
- Apagado controlado

### 1.6 Modo UPDATER: `FUN_c01f1378` (0xc01f1378)

Verificado en `r5-rea.json`:

```
FUN_c01f1378():
  FUN_c01f60c2();
  log "LD3_Pwr_bootmode_c01f0e14";
  FUN_c01f5a68(3);                   // Pwr_bootmode con modo 3
  FUN_c01f5b2a();
  log "LD3_Run_Config_init_HW__c01f0fbc";
  FUN_c01f3108();                    // init HW
  log "LD3_Load_vmlinux_initrd_c01f1524";
  uVar1 = FUN_c01f068a();            // ← carga vmlinux+initrd desde dispositivo 1
  *DAT_c01f1540 = uVar1;
  FUN_c01f5afe(3);
  return 0;
```

Después de que `FUN_c01f1378` retorna 0, `FUN_c01f1312` continúa:
```
FUN_c01f3670(2, s_LD3_Exit_UDIF_drvs);
FUN_c01f68ac();
FUN_c01f3670(2, s_LD3_Exit_UDIF_plat);
FUN_c01f6888();
iVar1 = FUN_c01f4e0c(mode, 1);
if (iVar1 == 0) {
  FUN_c01f0590(mode);   // logging de backup/claves
  iVar1 = 0;
}
return iVar1;
```

Luego en `FUN_c01f11ec`:
```
if ((iVar2 != 0) || (iVar2 = FUN_c01f04b6(local_10), iVar2 != 0))
    goto LAB_c01f1262;   // → LED bucle
```

**Hallazgo clave para Prioridad C:** El modo UPDATER (3) **no es un entorno de recuperación independiente**. Carga `vmlinux.bin` e `initrd.img` desde el dispositivo 1 (`nflasha1`, FAT) mediante `FUN_c01f068a()`, y luego salta al kernel exactamente igual que el modo COLD. Requiere:
- BOSS inicializado (`FUN_c01f0cca` tuvo éxito)
- Dispositivo 2 montado con FAT (para leer `updater/mode`)
- Dispositivo 1 montado con FAT (para leer `\\boot\\vmlinux.bin` y `\\boot\\initrd.img`)
- `FUN_c01f068a()` debe tener éxito (carga de archivos desde FAT)

Si cualquiera de estos falla, se va a `FUN_c01f3b74` (bucle LED).

### 1.7 Grafo completo de rutas de arranque

```
                          Alimentación + secuencia Darwin (condicionadas)
                                       |
                                       v
                              BootROM histórico (0xffff0000)
                                       |
              +----------------------+----------------------+
              | rama normal                              | condiciones de modo no identificadas
              v                                          v
                    L2                              RX[Receptor serie: memoria + salto]
                    (Loader2)                                              |
              INFO, BOSS,                                                sin cadena de escritura NAND demostrada
              lectura NAND                                               |
              carga fragmentos 5,6 de L3                                 |
                                       v                                       v
                                L3[Loader3 íntegro]                    no es vía de recuperación
                                       |
                                       v
                    +----------------+----------------+----------------+
                    |                |                |                |
                    v                v                v                v
              modo 3           modos 1,2,4,5,6      modos 7,8         modos 9,0xd,0xe
              (UPDATER)        10,0xb,0xc (COLD)    (WARM/HOT)        (otros)
                    |                |                |                |
                    v                v                |                v
            FUN_c01f1378     FUN_c01f09e4       FUN_c01f036c     FUN_c01f129c
            (carga kernel      (carga kernel      (no examinado)   (no examinado)
             desde dev1)       desde dev3)                                    |
                    |                |                |                |
                    v                v                |                v
            +-------+-------+  +----+----+             |             +--+--+
            |               |  |         |             |             |     |
            v               v  v         v             v             v     v
           kernel       FUN_c01f04b6?  (sin retorno    (sin retorno   (sin
           desde      salto al        conocido al     conocido al    conocido al
           nflasha1   kernel          selector)       selector)      selector)
           (device 1)   (device 3)
                                                      |
                                                      v
                                              FUN_c01f3b74
                                              bucle LED infinito
                                              (sin retorno)
```

### 1.8 Respuestas a las preguntas de Prioridad A

| Pregunta | Respuesta | Clasificación |
|----------|-----------|---------------|
| Fuentes de arranque alternativas | Solo dispositivo 1 (UPDATER) y dispositivo 3 (COLD). Ambas cargan kernel y saltan a él. | VERIFICADO EN BINARIO |
| Diferencias COLD/WARM/HOT/UPDATER | COLD: dispositivo 3, reset backup, carga kernel. UPDATER: dispositivo 1, carga kernel+initrd, mismo salto. WARM/HOT (7,8): `FUN_c01f036c` no examinado. | VERIFICADO / NO EXAMINADO |
| Condiciones automáticas de recuperación | **NINGUNA encontrada**. Cualquier fallo → `FUN_c01f3b74` (bucle LED). | VERIFICADO EN BINARIO |
| Manejo de fallos de carga de kernel | `FUN_c01f04b6`: si dirección NULL → -0x12e → bucle LED. Si desalineada → log + salta igual. | VERIFICADO EN BINARIO |
| Fallback ante errores BOSS | Ninguno. `FUN_c01f0cca` fallo BOSS → `FUN_c01f3b74`. | VERIFICADO EN BINARIO |
| Fallback ante particiones inválidas | Ninguno. `FUN_c01f3d50` (FAT) fallo → `FUN_c01f3b74`. | VERIFICADO EN BINARIO |
| Selección de particiones redundantes | Ninguna. Loader3 lee fragmentos 5 y 6 secuencialmente, no como copias redundantes. | VERIFICADO EN BINARIO |
| Valores persistentes de Backup | Leídos en `FUN_c01f0cca` y `FUN_c01f1de6`, pero no se demuestra que permitan recuperación. | INFERENCIA RESPALDADA |
| Estados de reinicio | `FUN_c01f3b74` bucle infinito; `FUN_c01f6ada(1)` resetea backup en COLD. | VERIFICADO EN BINARIO |
| Señales de servicio | `FUN_c01f3884`, `FUN_c01f5008`, `FUN_c01f379a`, `FUN_c01f6d18`, `FUN_c01f4f88` — no examinados. | NO EXAMINADO |
| Configuraciones de fábrica | No identificadas como vía de recuperación. | NO DEMOSTRADO |
| Entradas alternativas del BootROM | Receptor serie en ROM (ver R7B), sin cadena de escritura NAND demostrada. | PARCIAL (R7B) |

**Comprobación central — ¿Qué ocurre cuando COLD falla al cargar el kernel?**

**RESPUESTA:** `FUN_c01f09e4` retorna error → `FUN_c01f1312` retorna error → `FUN_c01f11ec` llama `FUN_c01f3b74()` → **bucle infinito de parpadeo de LED** con mensajes "ERROR__Blinking_LED_LDR2" y "ERROR__Loader_boot_failed__". **No reintenta, no selecciona copia secundaria, no regresa al selector, no entra en estado de servicio, no apaga.** No hay ninguna rama de fallback en el código examinado.

---

## 2. Prioridad B — BOSS/MuMin (VERIFICADO EN BINARIO)

Las primitivas de escritura ya documentadas en [R7](e26-r7-recuperacion-estatica.md) se confirman y amplían:

### 2.1 Interfaces del controlador (verificación en binario)

| Capa | Función | Dirección | Operación | Requiere Linux |
|------|---------|-----------|-----------|----------------|
| muminblk | `muminblk_request` | 0x1020c | lectura/escritura lógica por sectores | SÍ |
| muminblk | `muminblk_ioctl` → `nand_ioc_pwrite_normal` | 0x284bc | escritura de páginas físicas (selector 0x6e06) | SÍ |
| muminblk | `muminblk_ioctl` → `nand_ioc_perase_normal` | 0x28298 | borrado físico (selector 0x6e04) | SÍ |
| muminblk | `muminblk_ioctl` → `nand_ioc_lerase` | 0x28624 | borrado lógico (selector 0x6e08) | SÍ |
| MuMin | `mumin_vbm_write_vpages` | 0x24490 | escritura de páginas virtuales (marca bloque usado) | SÍ |
| MuMin | `mumin_pbm_write_vpages` | 0x21ba8 | despacho PBM por puntero | SÍ |
| LLD | `mumin_devif_write_pages_in_pblk` | 0x153dc | construye solicitud NAND → `boss_hw_arm7_comm_set_firmware_api_param(9, 0x2800, …)` | SÍ |
| LLD | `mumin_devif_erase_pblk` | 0x10b64 | → misma API con primer argumento 0x0c | SÍ |
| ARM7 | despachador | 0x0ec8 | índices 9 (escritura) y 12 (borrado) | SÍ (via LLD) |

### 2.2 `boss_hw_nandc_recovery_check` (0x17b8c)

Verificado en `r7-recovery-check-rea.json`:
- Solo actúa cuando `param_1 == -0x20001` o `param_1 == -0x2713`
- Obtiene direcciones base de ARM7 SRAM, clkrst3 y registros NAND
- Escribe `0x1f01` en clkrst3+0xd8, `0` en ARM7_SRAM+0x3f40, espera, escribe `0x1f00` en clkrst3+0xd4
- Lee registro NAND +0x410, hace `tst r3, #0x2000`
- Si bit 0x2000 no está set: bucle de espera con `FUN_c01f1b07c` (udelay) comparando con umbral en `0x17d18`
- **Interpretación:** manejo interno de recuperación del controlador NAND ante errores específicos. No es selección de UPDATER ni recuperación de arranque.

### 2.3 Cadena de llamadas de escritura (verificación en binario)

```
escritura de páginas:
  muminblk_request (0x1020c)
    → mumin_ext_write_scts (0x26e80) → __mumin_write_ltus (0x139fc) → mumin_ebm_write_ltus (0x1a638)
    → mumin_devif_write_pages_in_pblk (0x153dc) → boss_hw_arm7_comm_set_firmware_api_param(9, 0x2800)
borrado:
  mumin_devif_erase_pblk (0x10b64) → boss_hw_arm7_comm_set_firmware_api_param(0x0c, …)
```

### 2.4 Operaciones antes de Linux

**Ninguna demostrada.** Todas las operaciones de escritura/borrado de BOSS/MuMin/LLD requieren el controlador Linux inicializado (`muminblk` necesita mutex, kmem_cache, etc.). No hay interfaz de servicio pre-Linux para invocar estas operaciones.

### 2.5 Restauración selectiva de `nflasha3`

**NO DEMOSTRADA.** Las operaciones de escritura existen en Linux pero:
- No hay aislamiento de partición `nflasha3` demostrado
- No hay preservación de metadatos, ECC, OOB, bloques defectuosos
- No hay interfaz externa invocable desde cámara bloqueada
- `nand_ioc_pwrite_normal` valida dimensiones contra geometría pero no demuestra seguridad de partición

---

## 3. Prioridad C — Actualizador como entorno de recuperación (VERIFICADO EN BINARIO)

### 3.1 `FUN_c01f1378` — modo UPDATER (mode 3)

Como se documentó en §1.6, el modo 3:
1. Llama `FUN_c01f60c2()` (init)
2. `FUN_c01f5a68(3)` — power bootmode modo 3
3. `FUN_c01f3108()` — init HW
4. `FUN_c01f068a()` — carga `\\boot\\vmlinux.bin` y `\\boot\\initrd.img` desde dispositivo 1
5. Retorna 0 → `FUN_c01f04b6(3)` salta al kernel

**No hay entorno de recuperación separado.** El modo UPDATER es idéntico al COLD en su destino final: arrancar el kernel Linux. La única diferencia es el dispositivo de origen (1 vs 3).

### 3.2 Matriz de condiciones para entrar al actualizador

| Condición | Estado | Clasificación |
|-----------|--------|---------------|
| `updater/mode` existe en dispositivo 2 | Verificado en prefijo Loader3 | VERIFICADO EN BINARIO |
| BOSS inicializado | Requerido por `FUN_c01f0cca` | VERIFICADO EN BINARIO |
| Dispositivo 2 montado con FAT | Requerido por `FUN_c01f3d50` | VERIFICADO EN BINARIO |
| Dispositivo 1 montado con FAT | Requerido por `FUN_c01f068a` | VERIFICADO EN BINARIO |
| `\\boot\\vmlinux.bin` y `\\boot\\initrd.img` legibles | Requerido por `FUN_c01f068a` | VERIFICADO EN BINARIO |
| Productor pre-Linux de `updater/mode` | **No identificado** | NO DEMOSTRADO |
| Activación independiente de la bandera | **No identificada** | NO DEMOSTRADO |
| UPDATER sin Linux normal | **Sí** (selección en Loader3, antes de Linux) | VERIFICADO EN BINARIO |
| UPDATER sin `nflasha3` | **Sí** (carga desde dispositivo 1) | VERIFICADO EN BINARIO |

### 3.3 Productores de `updater/mode`

**Ningún productor pre-Linux identificado** en el prefijo de Loader3 examinado. La bandera debe crearse por algún componente antes del arranque (posiblemente Linux normal o una herramienta de servicio), pero no se ha encontrado en el código estático.

---

## 4. Prioridad D — Causalidad TPZL hasta ARM7

### 4.1 Estado actual (ya documentado en e26-recovery.md)

- `nand.ko` advierte "Offset for lded_read should be 0" pero no rechaza inmediatamente
- El residuo `offset & 0x1ff` se copia al descriptor LDEC (`+8`)
- `mumin_devif_ldec_read` (0x11048) lo pasa al descriptor enviado por LLD
- LLD lo entrega a `boss_hw_arm7_comm_set_firmware_api_param(9, 0x2800, …)`
- En ARM7, `0x3f4` lee descriptor+0x0c/+0x10, **no se observa uso explícito de +8** en los tramos examinados
- Tabla ARM7 envía índice 6 a `0x22d4` (rutina no reconocida por REA, verificada con Capstone)

### 4.2 Conclusión

**NO DEMOSTRADO:** incompatibilidad funcional del residuo TPZL 256. No hay evidencia de rechazo por hardware ARM7, ni código de error identificable. Las advertencias ECC son independientes de la alineación (ECC corregible reportado por controlador). Falta el firmware ARM7 actual para certificar el comportamiento.

---

## 5. Prioridad E — 21 páginas faltantes de Loader3 (INFO6)

### 5.1 Estado (verificado en archivos)

- INFO6 = die0, plane1, block2, pages 0–20
- Runtime esperado: 0xc0205800–0xc0210000
- Candidato Loader3 (primeras 43 páginas) SHA-256 `8fd98a41…` encontrado en respaldo
- INFO6 **no tiene correspondencia identificada** en BLDR ni en volcados RAM
- Dos volcados RAM de 1 GiB buscados con 5 anclas de 64 B del prefijo válido: **ninguna coincidió**

### 5.2 Inventario de fuentes

| Fuente | ¿Contiene INFO6? | ¿Identidad verificable? |
|--------|------------------|------------------------|
| BLDR `bootloader.bin` | Solo primeras 43 páginas (prefijo) | SÍ (sha256 cotejado) |
| Volcados RAM (2×1 GiB) | No (anclas no coincidieron) | NO |
| Otras copias de Loader3 | No encontradas entre respaldos | NO |
| Firmware oficial A6000 | No disponible localmente | NO |

**Conclusión:** No hay fuente adecuada para recuperar las 21 páginas INFO6. Este punto se cierra con límite documental.

---

## 6. Prioridad F — Mecanismos de servicio del BIONZ

### 6.1 BootROM receptor serie (R7B)

Verificado en `r7b-bootrom-rea.json`:
- `0xffff0876` y `0xffff0634`: recepción por muestreo de bit 1 de `0xf2915010` (MISC_MODEREG, bit 1 = BOOT_SERIAL_IN per CXD90014)
- Reconstruye 8 bits, comprueba paridad, escribe bytes en buffer
- Tipos 0 y 0xFFFF: guarda valor o dirección de salto
- Tipo 0xFFFF guarda dirección de salto en `0xc000500c`, luego `0xffff0144` la carga y ejecuta salto indirecto
- **Sin conexión física identificada** (R4003 XX en esquema, sin población verificada)
- **Sin cadena de escritura NAND demostrada**

### 6.2 ¿Existe software para comunicarse con BIONZ antes de nflasha3?

**NO DEMOSTRADO.** El receptor serie de BootROM existe estáticamente, pero:
- No se identifica la red física (pin, conector, continuidad)
- No se demuestra que un interlocutor externo pueda activar la entrada
- No hay demostración de que el código cargado pueda restaurar NAND preservando metadatos
- No se identifica con USB, CN4906 ni UART Darwin

---

## 7. Análisis comparativo con otras Sony

Verificado en `r7b-compare-scripts.json`:
- `loader_writer.sh` idéntico (SHA-256 `2f38d367…`) en A6000 3.21, A7S 3.20, A6300 2.01
- Bajo Linux, extrae loader, recopila MIS/DGU/Backup, comprueba MD5, llama `pformat_normal.elf` y `pformat_safe.elf` sobre `/dev/nflasha`
- **Identidad del script no demuestra igualdad de ejecutables, ROM, firmware ARM7, geometría ni acceso pre-Linux**

No se encontraron implementaciones de recuperación documentadas en otros modelos que se apliquen a la A6000.

---

## 8. Investigación orientada a la recuperación

| # | Pregunta | Respuesta | Clasificación |
|---|----------|-----------|---------------|
| 1 | ¿Qué descubrimos? | Grafo completo de rutas de arranque; COLD fallo → bucle LED; UPDATER = carga kernel desde dev1 y salta; escrituras NAND solo en Linux | VERIFICADO EN BINARIO / ARCHIVOS |
| 2 | ¿Qué componente permite recuperar? | Ninguno demostrado antes de nflasha3 | NO DEMOSTRADO |
| 3 | ¿Se puede usar sin Linux? | Selector mode en Loader3 (pre-Linux), pero activación externa no demostrada | PARCIAL |
| 4 | ¿Se puede usar sin Loader3? | No | DESCARTADO |
| 5 | ¿Se puede usar sin Darwin funcional | UPDATER carga desde nflasha1, pero necesita BOSS+FAT+dispositivo1 | PARCIAL (dependencias) |
| 6 | ¿Permite leer almacenamiento? | Loader2 lee NAND (interno), Linux MuMin lee páginas | VERIFICADO (interno/Linux) |
| 7 | ¿Permite escribir almacenamiento? | MuMin/LLD escriben páginas y borran bloques, pero solo en Linux | VERIFICADO (solo Linux) |
| 8 | ¿Depende de interfaz física no validada? | Receptor serie BootROM sin red física identificada | SÍ (no validada) |
| 9 | ¿Riesgo para calibraciones? | Escritura sin mapeo lógico-físico/ECC/bad-blocks podría destruir calibraciones | ALTO (no demostrado seguro) |
| 10 | ¿Qué información falta? | Firmware ARM7 actual, funciones FUN_c01f036c/FUN_c01f129c/FUN_c01f5078/FUN_c01f028c, productor de `updater/mode`, fuente INFO6 | FALTANTE |

---

## 9. Grafo final de rutas de arranque (entregable)

```
Alimentación + Darwin
       |
       v
   BootROM (0xffff0000)
       |
       +-- rama normal --> Loader2 --> INFO + BOSS + fragmentos 5,6 de Loader3
       |
       +-- condiciones modo --> Receptor serie (memoria + salto, sin cadena NAND)
                                 |
                                 v
                          Loader3 (0xc01f0000–0xc0205800)
                                 |
                                 v
                    FUN_c01f0cca (init completo: Sync,Power,UDIF,BOSS,DDR,DGU,BlkDev,FAT,Backup,Pwr2nd)
                                 |
                    +------------+------------+
                    |                         |
                   OK                       ERROR
                    |                         |
                    v                         v
              FUN_c01f1de6 (BOSS/Backup)   FUN_c01f3b74 (BUCLE LED, sin retorno)
                    |
                    +------------+------------+
                    |                         |
                   OK                       ERROR
                    |                         |
                    v                         v
              FUN_c01f2156 (modo = *0xc01f248c)  FUN_c01f3b74 (BUCLE LED, sin retorno)
                    |
        +-----------+-----------+-----------+-----------+
        |           |           |           |           |
        v           v           v           v           v
      modo 3     1,2,4,5,6   7,8         9         0xd,0xe
     (UPDATER)  10,0xb,0xc  (WARM/HOT)      (otros)
     (COLD está en 0xc)
        |           |           |           |
        v           v           |           v
   FUN_c01f1378  FUN_c01f09e4   |       FUN_c01f129c
     (dev1)      (dev3, COLD)   |           |
        |           |           |           |
        v           v           |           v
   carga vmlinux+  carga kernel   |           (sin retorno
   initrd desde   desde nflasha3  |           al selector)
   nflasha1                               |
        |           |           |           |
        v           v           |           v
   FUN_c01f04b6(3) FUN_c01f04b6  |           |
   (salta al kernel) (salta al   |           |
   kernel)           kernel)     |           |
        |           |           |           |
        v           v           |           v
   KERNEL ARRANCA  KERNEL ARRANCA  |           (sin retorno
                                     |           al selector)
                                     v
                              FUN_c01f3b74
                              BUCLE LED INFINITO
                              (sin retorno)
```

---

## 10. Clasificación de hallazgos

| Hallazgo | Clasificación | Fuente |
|----------|--------------|--------|
| COLD fallo → `FUN_c01f3b74` bucle LED infinito, sin retorno | VERIFICADO EN BINARIO | r7b-cold-rea.json, r5-rea.json |
| `FUN_c01f04b6` salta al kernel (NULL → error, desalineado → log + salta) | VERIFICADO EN BINARIO | r7b-cold-rea.json |
| Modo UPDATER (3) carga kernel desde dev1 y salta, sin entorno separado | VERIFICADO EN BINARIO | r5-rea.json |
| Escrituras/borrados NAND en MuMin/LLD, solo en Linux | VERIFICADO EN BINARIO | r7-nand-rea.json, r7-mumin-rea.json, r7-lld-rea.json |
| `boss_hw_nandc_recovery_check` maneja errores NAND, no es UPDATER | VERIFICADO EN BINARIO | r7-recovery-check-rea.json |
| No hay productor pre-Linux de `updater/mode` | NO DEMOSTRADO | r7b-cold-rea.json |
| Receptor serie BootROM sin cadena de escritura NAND | PARCIAL (R7B) | r7b-bootrom-rea.json |
| INFO6 (21 páginas) sin fuente identificada | NO DEMOSTRADO | r7b-info6-inventory.json, r7b-info6-ram-search.json |
| Residuo TPZL 256 sin rechazo demostrado por ARM7 | NO DEMOSTRADO | r7b-ldec-arm7-rea.json, r7b-ldec-linux-rea.json |
| Escritura selectiva de nflasha3 preservando metadatos | NO DEMOSTRADO | r7-nand-rea.json |
| Comparación loader_writer.sh entre modelos | VERIFICADO EN ARCHIVOS | r7b-compare-scripts.json |

---

## 11. Pendientes actualizados (IDs nuevos)

| ID | Estado | Origen | Criterio de cierre |
|----|--------|--------|-------------------|
| E26-R7-A-COLD | CERRADO | R7 §1 | FUN_c01f3b74 = bucle LED sin retorno, verificado en binario |
| E26-R7-A-UPDATER | CERRADO | R7 §1.6 | FUN_c01f1378 carga kernel desde dev1 y salta, sin entorno separado |
| E26-R7-B-BOSS | CERRADO | R7 §2 | Primitivas de escritura verif. en binario, solo Linux |
| E26-R7-C-UPDATER-MODE | ABIERTO | R7 §3.3 | Productor pre-Linux de `updater/mode` no identificado |
| E26-R7-D-TPZL-ARM7 | NO DEMOSTRADO | R7 §4 | Falta firmware ARM7 actual para certificar comportamiento |
| E26-R7-E-INFO6 | CERRADO CON LÍMITE | R7 §5 | Sin fuente adecuada para 21 páginas INFO6 |
| E26-R7-F-SERVICE | PARCIAL | R7 §6 | Receptor serie BootROM sin red física ni cadena NAND |

---

## 12. Conclusión final

**No existe una ruta de restauración utilizable antes de `nflasha3` basada en evidencia estática actual.**

- El modo COLD falla a bucle de LED infinito (`FUN_c01f3b74`) sin retorno al selector, sin selección de UPDATER, sin carga de copia secundaria.
- El modo UPDATER (3) carga `vmlinux`+`initrd` desde `nflasha1` (dispositivo 1) y salta al kernel, exactamente igual que COLD. No es un entorno de recuperación independiente.
- Todas las operaciones de escritura/borrado NAND (MuMin, LLD, BOSS → ARM7) requieren el entorno Linux inicializado. No hay interfaz pre-Linux demostrada.
- No hay productor pre-Linux de `updater/mode` identificado.
- No se ha demostrado escritura selectiva de `nflasha3` preservando metadatos, ECC, bloques defectuosos y calibraciones.

**La única vía de recuperación teóricamente identificada** es el selector `updater/mode` en Loader3, pero requiere:
1. BOSS inicializado (depende de `FUN_c01f0cca` completo)
2. Dispositivo 2 con FAT montado (para leer `updater/mode`)
3. Dispositivo 1 con FAT montado (para leer `vmlinux.bin`+`initrd.img`)
4. `FUN_c01f068a()` con éxito (carga de archivos desde FAT)
5. Un productor externo que cree `updater/mode` antes del arranque (no identificado)

Si se agotan las rutas estáticas razonables, las dependencias físicas irreducibles son: firmware ARM7 actual, red física del receptor serie BootROM, y una fuente para INFO6. Ninguna está disponible en el estado actual de la investigación.

---

**Evidencia:** `analysis/e26-recovery/r7b-cold-rea.json`, `r5-rea.json`, `r7-nand-rea.json`, `r7-mumin-rea.json`, `r7-lld-rea.json`, `r7-recovery-check-rea.json`, `r7b-updater-rea.json`, `r7b-bootrom-rea.json`, `r7b-info6-inventory.json`, `r7b-info6-ram-search.json`, `tpzl-comparison.json`, `r7b-compare-scripts.json`.

**Próximo paso:** Actualizar PENDIENTES, STATE, CURRENT, PROGRESS; regenerar índice de subsistemas; hacer commit y push a `origin/main` con cuenta `nicolvus`.
