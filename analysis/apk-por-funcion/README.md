# APK de la cámara organizadas por función

Enlaces simbólicos (originales intactos) a la extracción de la cámara (`camera-extract/android/`, fw A6000 live), más herramientas propias. Las copias en `firmware/extracted/{fw321,a7s-fw320,a6300-fw201}` son del mismo conjunto de otros modelos/firmwares (SmartRemote fw321 idéntico byte a byte).

| Carpeta | APK | Función |
|---|---|---|
| 1-control-remoto-y-obturador | SmartRemote (`com.sony.imaging.app.srctrl`), ScalarWebAPIDdService, RemoteShutter | Control remoto por Wi‑Fi (Camera Remote API / Smart Remote Control), descripción de servicios WebAPI/DD; RemoteShutter es nuestra herramienta (`tools/remote-shutter`). **Foco del proyecto.** |
| 2-red-wifi | ScalarAHotspot (`...scalar.app.hotspot`), WifiSettings | Punto de acceso y ajustes Wi‑Fi |
| 3-apps-y-lanzador | ScalarALauncher, ScalarAAppManager, ScalarAInstaller, ScalarAMarket, ScalarADisclaimer | Lanzador PlayMemories Camera Apps, gestión/instalación/tienda de apps, avisos legales |
| 4-actualizacion-usb | ScalarAUsbDlApp | Descarga/actualización por USB |
| 5-proveedores-datos | AvindexProvider, MediaProvider, ApplicationsProvider, SettingsProvider | Content providers: índice AV, medios, apps, ajustes |
| 6-sistema-y-ui | ScalarASoftKeyboard, CertInstaller, DefaultContainerService, framework-res | Teclado, certificados, instalación de paquetes, recursos del framework |
| 7-ecosistema-comunitario | openmemories.tweak-1 | App comunitaria (ma1co/OpenMemories) instalada en la cámara viva |

Clasificación por nombre/paquete/manifiesto; no se decompiló cada APK.
