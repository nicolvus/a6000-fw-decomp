# Decompilación: lanzador, proveedores de datos, sistema y UI

Fuente: `camera-extract/android/app/*.odex` (los APK no traen `classes.dex`). Cada `.odex` es un contenedor `dey\n100` cuyo DEX (`dex\n035`) se extrae con offset/longitud de la cabecera (u32 en 0x08/0x0C) → `dex/`. Decompilado con jadx 1.5.6 (JDK 21 en `~/.local/opt`) → `src/<App>/sources/`.

**REA no se usó**: su decompilador Android exige un JAR "JADX MCP" que no está configurado. Para pasar por REA habría que proporcionarlo (y un APK con `classes.dex`: se puede reempaquetar con `dex/<App>.dex`).

| Grupo | App | Clases | Contenido relevante |
|---|---|---|---|
| Lanzador | ScalarALauncher | 17 | `AllAppsGridView`, `AllAppsList`, `ScalarALauncherModel`, `IconCache` (rejilla de apps) |
| | ScalarAAppManager | 9 | `ScalarAManageApplications`, `ApplicationsState`, detalles/desinstalación |
| | ScalarAInstaller | 11 | `PackageInstallerActivity`, `decryptlib/` (AES, RSA, `SeedGenerator`: descifrado de paquetes) |
| | ScalarAMarket | 21 | navegador de la tienda, `ScalarADownloader`, `Encryptor`, SSL propio (`InsecureSSLSocketFactory`), `Xpd` |
| | ScalarADisclaimer | 12 | navegador/intro de avisos legales |
| Proveedores | AvindexProvider, MediaProvider, ApplicationsProvider, SettingsProvider | 3–4 c/u | content providers estándar de Android |
| Sistema y UI | ScalarASoftKeyboard (6), CertInstaller (7), DefaultContainerService (1) | | teclado, certificados, contenedor de paquetes |
| | framework-res | 0 | solo recursos, sin código |

Límites: jadx avisó de métodos mal decompilados en MediaProvider, AppManager, Disclaimer, Installer, Launcher y Market (buscar `JADX WARN` / `Code decompiled incorrectly`). Los `.odex` pueden traer instrucciones optimizadas (quickened). Sin `--res`: recursos no decodificados.

## Segunda tanda (restantes)

| Grupo | App | Clases Java | Notas |
|---|---|---|---|
| Control remoto | SmartRemote | 608 | `com.sony.imaging.app.srctrl` (`webapi/`, `shooting/`, `util/`, `caution/`) + framework Sony `base/`, `fw/`, `com.sony.mexi.*` (WebAPI/JSON) + servlet/Jetty empaquetado. 16 ficheros con avisos jadx |
| | ScalarWebAPIDdService | 10 | servicio AIDL `IDdService`, SSDP por JNI (`SsdpDeviceJni`) |
| | RemoteShutter (propio) | 1 | desde `tools/remote-shutter/out`, APK normal con `classes.dex` |
| Red | ScalarAHotspot | 11 | `Hotspot`, `StatusBroadcastReceiver`, `BatteryState`, pitidos |
| | **WifiSettings** | **0** | **NO decompilable**: el DEX tiene instrucciones quickened (p. ej. `INSTANCE_OF` con índices fuera de rango) y jadx no las lee; hace falta desodexar con baksmali + framework (`camera-extract/android/framework/*.odex`). El baksmali de apktool está recortado (sin soporte odex) |
| USB | ScalarAUsbDlApp | 25 | `ActionControl`, `RestParser`, `HttpParser`, `XpdParser`, `Encryptor` |
| Comunitaria | openmemories.tweak-1 | 20 | APK normal (`com.github.ma1co.openmemories.tweak`) |
| Sistema | framework-res | 0 | solo recursos |
