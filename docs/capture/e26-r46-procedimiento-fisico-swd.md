# E26-R46 — Procedimiento físico del camino 1 (SWD al BIONZ), sin osciloscopio

Fecha: 02-11-2026. **Borrador sin ejecutar.** Ninguna medida ni conexión se ha hecho. Requiere autorización expresa del usuario para cada fase (CLAUDE.md: sin acceso físico salvo autorización por caso).

Base: [R40](e26-r40-jtag-swd-bionz.md), [R41](e26-r41-caminos-estaticos-restantes.md), [R42](e26-r42-busqueda-externa-y-esquema-jtag.md), [E26-RECOVERY](e26-recovery.md), [R37](e26-r37-cierre-estatico-recuperacion.md)–[R39](e26-r39-estatico-profundo.md).

Etiquetas: **ESQUEMA** (leído del manual de servicio) · **INFERENCIA** · **NO MEDIDO**.

## 0. Qué se sabe y qué no

| Dato | Estado |
|---|---|
| SWCLK = bola W25, SWDIO = bola W26 de IC6000 (BIONZ), hacia CN4906 pines 11/12 a través de R4911/R4912 | ESQUEMA |
| R4911/R4912 y la huella de CN4906 figuran «XX» (sin montar) | ESQUEMA; **confirmado por el usuario (02-11-2026): R4911, R4912, R4915, R4916 y CN4906 sin montar** (solo huellas) |
| TDI/TCK/TMS atados a D_3.15V_MSS (JTAG clásico inservible); FUSE_EN (T12) también a 3,15 V | ESQUEMA |
| Tensión lógica de SWD ≈ 3,15 V | INFERENCIA (por la alimentación del bloque); **NO MEDIDO** |
| Ningún cargador (BootROM/Loader2/Loader3/ARM7) toca el DAP (0xf2710000) | BINARIO (R40) |
| eFuses de seguridad podrían deshabilitar la depuración | **NO DEMOSTRADO**, es la mayor incógnita |
| Objetivo tras abrir SWD: escribir `\updater\mode` en `nflasha2` (R37/R38) o reescribir `nflasha3` | ESTÁTICO; vía de escritura desde BIONZ no ejecutada |

Si en el paso F3 las resistencias no están montadas o el eFuse bloquea el DAP, el camino 1 **se descarta** y se pasa al camino 3 (NAND).

## 1. Lista de materiales a comprar

Sin osciloscopio: todo el diagnóstico se hace con multímetro y con el propio sondeo SWD (si el DAP responde, la señal es válida).

| # | Material | Para qué | Notas |
|---|---|---|---|
| 1 | **Sonda SWD con tensión de referencia de destino** (J-Link EDU Mini o equivalente) **o** una Raspberry Pi Pico con firmware `debugprobe` (CMSIS-DAP) | Hablar SWD con el BIONZ | Preferible la J-Link (mide VTref y adapta nivel). La Pico trabaja a 3,3 V fijos: válido si la línea mide 3,15–3,3 V; **no usar** si mide 1,8 V |
| 2 | Multímetro con continuidad y escala de 20 V CC | Medir continuidad, tensión y masa | Imprescindible |
| 3 | Soldador de temperatura regulable, punta fina (≤ 0,5 mm), estaño 0,3–0,5 mm con flux | Soldar hilos a pads 0402/0603 o a la huella de CN4906 | |
| 4 | Cable de cobre esmaltado 0,1–0,2 mm (cable de wire-wrapping 30–38 AWG) | Hilos a los pads | |
| 5 | Pinzas de punta fina y pinzas antiestáticas | Manipular | |
| 6 | Lupa de joyero 10× o microscopio USB | Ver pads | Muy recomendable |
| 7 | Flux en gel y malla desoldadora | Retrabajar sin quemar | |
| 8 | Kit de destornilladores de precisión (Phillips 00/000) y palanca de plástico | Abrir la cámara | |
| 9 | Alimentador externo regulado 3,8–4,2 V con limitador de corriente, o batería NP-FW50 cargada; **batería ficticia (dummy) opcional** | Alimentar sin riesgo de caída | Limitar a 1 A |
| 10 | Tapete antiestático y pulsera | ESD | |
| 11 | Cinta Kapton, bolsas pequeñas y etiquetas | Proteger y rotular tornillos y cintas flex | |
| 12 | Opcional: conector Pogo de 4–6 pines con soporte, o pinza SOIC clip si CN4906 queda accesible | Conexión no permanente | |
| 13 | Opcional: analizador lógico barato de 8 canales (24 MHz) | Ver actividad si el DAP no responde | Sustituye al osciloscopio para señales digitales de baja velocidad; no es necesario para empezar |

Presupuesto orientativo: 40–120 € según la sonda (el soldador y el microscopio son lo que más varía).

## 2. Preparación (sin tocar la cámara)

1. **Respaldo R1 verificado** en soporte externo (pendiente de E25-04). No se abre la cámara antes. **NO_VERIFICADO**
2. `gh auth switch -u nicolvus`; trabajar en la rama con el estado limpio.
3. Instalar OpenOCD y/o pyOCD; comprobar que la sonda se detecta (`openocd -f interface/<sonda>.cfg`) **sin** conectarla a la cámara.
4. Tener a mano: [R40](e26-r40-jtag-swd-bionz.md), el PDF del esquema (páginas 23, 38, 50, 51) y el manual del BIONZ (bolas W25/W26/H26/T12).
5. Decidir antes qué se escribirá si el DAP responde (ver §6) y no improvisar con la cámara abierta.

## 3. Fases

Cada fase termina con un criterio de parada. **Si no se cumple, se detiene y se documenta; no se pasa a la siguiente.**

### F1 — Abrir y fotografiar (cámara apagada, batería fuera)
1. Quitar batería y tarjeta. Esperar 5 min para descargar condensadores.
2. Abrir la carcasa siguiendo el manual de servicio; guardar tornillos por zona en bolsas etiquetadas.
3. Desconectar la cinta flex con cuidado (levantar el pestillo, no tirar).
4. Fotografiar **ambas caras** de la placa SY-1028 con regla, iluminación rasante y alta resolución.
5. Localizar en las fotos: CN4906, R4911, R4912, IC6000, IC5700 y CL701/CL703–CL707.
- **Parada:** si no se llega a la zona sin desmontar la placa, parar y decidir con el usuario si se continúa.

### F2 — Identificación (cámara apagada)
1. Con la lupa, comparar lo observado con el plano del esquema (PDF 50/51).
2. Anotar si R4911/R4912 están **montadas** o vacías; anotar si CN4906 está montado o solo hay huella.
3. Marcar en la foto los dos pads de R4911/R4912 y la masa más cercana.
- **Estado:** R4911/R4912 **sin montar** (confirmado). Queda comprobar CN4906 y qué pad de cada resistencia va al BIONZ (lado W25/W26) y cuál a CN4906. Sin esas dos resistencias no hay camino a CN4906: hay que cerrar el circuito (F5).

### F3 — Continuidad pasiva (cámara apagada, batería fuera)
1. Medir continuidad entre cada pad de R4911/R4912 y su pin de CN4906 (11 y 12).
2. Medir que la masa de la sonda (pin GND de CN4906) está a masa de la placa.
3. Medir resistencia entre los pads de SWCLK/SWDIO y masa: debe ser alta (≥ kΩ) y sin cortos. Un valor bajo o cero detiene el procedimiento.
4. Con el esquema en la mano, confirmar que **no** se mide continuidad entre estos pads y alimentaciones.
- **Criterio:** pads identificados, sin cortos, masa común confirmada.

### F4 — Tensión con la cámara alimentada (sin sonda conectada)
1. Alimentar con fuente limitada a 1 A (o batería).
2. Encender y medir con el multímetro (rango CC 20 V): D_3.15V_MSS, y los pads SWCLK/SWDIO frente a masa. Anotar los valores con la cámara bloqueada (LED de error).
3. Medir también `NTRST`/`XRESET_CR` (H26) si es accesible.
4. Apagar de inmediato tras anotar.
- **Criterio:** los pads de SWD miden entre 3,0 y 3,3 V (lógica a 3,15 V) o alta impedancia. Si miden 1,8 V o cualquier otro valor, **no** conectar una sonda de 3,3 V; usar J-Link con VTref o parar.

### F5 — Conexión de hilos (cámara apagada)
1. Soldar hilos finos a: SWCLK (W25), SWDIO (W26), GND, y opcionalmente NTRST/reset.
2. Fijar los hilos con Kapton para evitar tirones. Longitud ≤ 15 cm.
3. R4911/R4912 están vacías (confirmado). Dos variantes; elegir una con el usuario:
   - **5a (preferida):** soldar un hilo directamente al **pad de R4911/R4912 del lado del BIONZ** (la red que llega a W25/W26). Menos soldaduras y no depende de CN4906.
   - **5b:** montar resistencias de 0 Ω (0402 o 0603 según la huella; medir el pad) en R4911/R4912 y soldar los hilos a los pads de CN4906 11/12. Restaura el diseño original pero exige más soldaduras en pads pequeños.
   En ambos casos son acciones irreversibles; anotar la elección y fotografiar el resultado.
   **Valor para 5b (decisión):** el esquema (lámina de CN4906) no da valor: R4911, R4912, R4913, R4915 y R4916 figuran solo «XX». Se elige **0 Ω** (sin atenuación ni incógnitas en un enlace de depuración); si no hay, **22 Ω** como valor mínimo razonable, y como límite superior 47 Ω. Misma resistencia en las dos líneas, mismo tamaño de huella (medirla antes de comprar), medir el valor con el multímetro antes de soldar. Con 5a el hilo equivale a 0 Ω.
   Nota: los pines 11/12 de CN4906 comparten nodo con TCK_DWN/TMS_DWN de Darwin (R29); Darwin solo los alcanza por R4915/R4916, confirmadas sin montar (02-11-2026), así que no compite con la sonda. CN4906 también está sin montar: los pines 11/12 son solo pads de huella (paso fino); por eso **se prefiere 5a** y 5b queda como alternativa menos práctica.
4. **No** conectar VTref/alimentación de la sonda a la placa salvo que la sonda lo exija (la J-Link usa VTref de lectura).
5. Revisar con el multímetro la continuidad hilo → pad y la ausencia de cortos con pines vecinos.
- **Criterio:** cuatro hilos fijos y sin cortos.

### F6 — Primer contacto con el DAP (cámara alimentada, bloqueada)
1. Conectar la sonda por USB al PC, con los hilos aún sueltos del lado de la placa.
2. Conectar GND primero, luego SWCLK/SWDIO.
3. Alimentar la cámara y lanzar un escaneo SWD en solo lectura: `openocd -f interface/<sonda>.cfg -c "transport select swd" -c "adapter speed 100" -c "init; dap info; exit"` (100 kHz, para empezar).
4. Si responde: anotar IDCODE, número de APs y estado de `CTRL/STAT` (protección, `CDBGPWRUPREQ`).
5. Si no responde: repetir con velocidad más baja (10–50 kHz), con y sin reset (NTRST/XRESET_CR), y comprobar polaridad/orden. Si sigue sin respuesta, usar el analizador lógico (si se compró) para ver si hay actividad.
- **Criterio de éxito:** IDCODE válido. **Criterio de abandono:** sin respuesta tras revisar tensión, conexión y velocidad; o respuesta indicando depuración deshabilitada (eFuse). En ese caso se descarta el camino 1.

### F7 — Lectura (solo lectura, sin escribir)
1. Detener el núcleo (`halt`) y leer registros y la memoria `0xc0001200` (tabla de clave del bloque 0 de `nflasha0` ya cargada en RAM si el arranque llegó a BootROM/Loader).
2. Leer `[0xc006000c]` y el buffer de log de RAM (`0xc006001c…`, ver R41 §3) para confirmar el código de error real. Esto valida o refuta el −302 inferido.
3. Volcar a archivo la RAM útil (≥ 1 MiB desde `0xc0000000`) y guardar con SHA-256.
- **Criterio:** valor de error confirmado, memoria volcada y verificada.

### F8 — Decisión sobre la escritura
Con el DAP abierto hay dos opciones; **se elige una con el usuario antes de ejecutar nada**.

| Opción | Acción | Riesgo |
|---|---|---|
| A. Crear `\updater\mode` en `nflasha2` (R37) | Desde el BIONZ, usando la capa lógica de MuMin (R39), escribir la entrada de 1 byte | Debe respetar ECC y mapeo; mal hecho puede corromper `nflasha2` (calibraciones) |
| B. Reescribir `nflasha3` con la imagen válida del 20-10 (R30) | Volcar la imagen a RAM y llamar a la rutina de escritura | Escritura grande en NAND; hay que respetar bloques defectuosos |

Antes de cualquiera: respaldo previo de `nflasha2` y de lo legible de `nflasha3` (lectura por la misma capa lógica).

### F9 — Cierre
1. Retirar la sonda, desoldar los hilos y dejar la placa limpia (o retirar con pinzas finas y flux).
2. Remontar la cámara en el orden inverso, comprobar el arranque con batería.
3. Instalar el 3.26 oficial por USB solo si la cámara arranca el actualizador (paquete ya preparado, R37).
4. Documentar medidas, fotos, valores y decisiones en un informe nuevo; actualizar `docs/PENDIENTES.md` y `wiki/14-Estado-actual.md`; commit y push.

## 4. Condiciones de parada globales

- Corto o lectura anómala en F3.
- Tensión distinta de 3,0–3,3 V en F4 sin sonda adaptable.
- La cámara emite olor, calor o consumo anormal (> 1 A) en cualquier momento.
- El DAP indica depuración deshabilitada (F6).
- Cualquier duda sobre qué se escribe o dónde: no escribir.

## 5. Qué NO se hace sin autorización específica

- Soldar o montar componentes en la placa (F5).
- Encender la cámara con hilos conectados (F6).
- Cualquier escritura en NAND (F8).

## 6. Límites

- Todo el procedimiento es teórico: población de R4911/R4912, tensión real, eFuse y capacidad del DAP **no están medidos**.
- La compatibilidad de OpenOCD/pyOCD con el DAP del CXD90014 no está demostrada; puede requerir un script propio.
- La ruta de escritura de la NAND desde el BIONZ (MuMin) no se ha ejecutado; solo existe análisis estático y emulación (R39).
- Se supone SWD a ~3,15 V por la alimentación del bloque JTAG; no hay medición.
