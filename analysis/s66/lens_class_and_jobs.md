# S66 (subtarea F) — Clase `Camera::Lens`, ODL (carga de datos ópticos) y jobs de montura

**Alcance:** línea de ingeniería inversa **general** de la cámara: la capa de objetos de la lente en
`av-cam.bin` (A6000 fw3.21). Sin relación con SilentShutter.

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

---

## 1. La clase `Camera::Lens` (VERIFICADO por literales de traza)

El blob incluye los **nombres de las funciones** (strings de traza), lo que da el esqueleto de la clase:

| Función | Dirección | Observación |
|---|---|---|
| `Camera::Lens::Initialize(UPM_BOOT_FACTOR*)` | `0x43721624` | se inicializa con los factores de arranque |
| `Camera::Lens::SetAberrationDataInfo(__uint16_t)` | `0x436fd9b4` | fija el parámetro de datos de aberración |
| `Camera::Lens::job_Mount_SaveAberrationDataHndl(__uint16_t)` | `0x436fda1c` | job: guarda los datos de aberración |
| `Camera::Lens::job_Mount_LoadAberrationDataHndl()` | `0x436fdab0` | job: carga los datos de aberración |
| `Camera::Lens::job_Mount_CloseAberrationDataHndl()` | `0x436fdb4e` | job: cierra el buffer de datos |
| `Lens::HS_M_L S` | `0x4378fef4` | tarea HS_Main (la misma de S61) dentro del ámbito de la lente |

Los tres "jobs" comparten la misma estructura: `Open` de un recurso **YC** (`[LENS_YC]: %s: Open
error (0x%x)` / `Close error`), trabajo y `Close`; el prefijo `[LENS_YC]` identifica al canal de
comunicación por el que llegan los datos ópticos.

## 2. `Camera::Lens::ODL` — el cargador de datos ópticos (VERIFICADO)

| Método | Dirección |
|---|---|
| `ODL::Alloc(ALLOC_ARG*)` | `0x43721aa8` |
| `ODL::AllocLensAberrationData(__uint16_t*)` | `0x43721af8` |
| `ODL::Free(FREE_ARG*)` | `0x43721b34` |
| `ODL::FreeLensAberrationData(__uint16_t)` | `0x43721b6c` |
| `ODL::Load(LOAD_ARG*)` | `0x43721b9c` |
| `ODL::LoadLensAberrationData(__uint16_t)` | `0x43721b9c` (mismo bloque) |

**Hecho clave (VERIFICADO):** `ODL::Load` **no abre ficheros**: usa `AsyncSend` /
`AsyncRecieve` (`0x43721bf6` / `0x43721c20`) y distingue "wrong message received"
(`0x43c9b075`). Es decir, la carga de los datos por lente (los ficheros `/lens/VX91xx_lensfile.bin`)
se pide **a otro servicio por mensaje asíncrono**; el acceso real al fichero está fuera de
`av-cam.bin`.

Consecuencia para la búsqueda del código de carga (subtarea B): el punto de entrada en `av-cam.bin`
es `Camera::Lens::ODL::Load` → `AsyncSend`/`AsyncRecieve`, y el *servicio* que responde (y que
posiblemente abre `/lens/VX91xx_lensfile.bin`) está en otro binario del firmware (userland:
p. ej. `libInfraMediaMount.so` / `libInfraLensCommunicator.so`).

## 3. Barrera de lente (`LensBarrier`) (VERIFICADO, parcial)

- Log único: `[LensBarrier] KikiLog Move` (`0x43ca7e4a`), referenciado por dos funciones
  (`0x437cf490`, `0x437cf5f0`) que emiten el evento al framework de traza **KikiLog**
  (`0x439c5004`).
- Etiquetas de estado `LENS_BARRIER` (`0x43cb4cc6`) y `MOUNT_LC` (`0x43cb4c9b`) presentes sin
  referencias PIC directas (se usan como cadenas de traza/estado).
- INFERENCIA: la A6000 lleva una **cortina/barrera de lente** (elemento mecánico del cuerpo) que
  se mueve al montar/desmontar; el movimiento se registra como evento KikiLog.

## 4. Abierto (NO_VERIFICADO)

1. Identidad del servicio que atiende `AsyncSend/AsyncRecieve` y que abre los ficheros de lente.
2. Contenido del mensaje (`LOAD_ARG`/`ALLOC_ARG`/`FREE_ARG`) y su versión.
3. Quién decide *qué* fichero de lente corresponde a la lente montada (cruce con
   `ATTACH_INFO`/`ALPHA_LENS_INFO`).
4. GPIO/servicio que mueve la barrera de lente (`LensBarrier`).
