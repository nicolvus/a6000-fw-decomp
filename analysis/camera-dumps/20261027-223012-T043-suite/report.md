| velocidad | rep | ms | lum | sat % | oscuro % | bandas | audio pico dB / transitorios |
|---|---|---|---|---|---|---|---|
| 1/4000 | 0 | 2638 | 225.8 | 40.9 | 0.0 | 5.48 | - |
| 1/4000 | 1 | 2624 | 225.7 | 40.6 | 0.0 | 5.48 | - |
| 1/1000 | 0 | 2772 | 225.8 | 40.7 | 0.0 | 5.49 | - |
| 1/1000 | 1 | 2785 | 225.8 | 40.7 | 0.0 | 5.48 | - |
| 1/250 | 0 | 2739 | 226.3 | 41.6 | 0.0 | 5.5 | - |
| 1/250 | 1 | 2810 | 226.3 | 41.7 | 0.0 | 5.49 | - |
| 1/60 | 0 | 2075 | 190.4 | 7.0 | 0.0 | 5.13 | - |
| 1/60 | 1 | 2050 | 191.6 | 8.4 | 0.0 | 5.15 | - |
| 1/15 | 0 | 2139 | 152.4 | 0.0 | 0.0 | 4.63 | - |
| 1/15 | 1 | 2178 | 153.6 | 0.0 | 0.0 | 4.65 | - |

| ráfaga | disparos | ms por disparo | rearme ms | reintentos de apertura | lum |
|---|---|---|---|---|---|
| 8×1/250 gap 0 | 8 | [2875, 2805, 2812, 2773, 2787, 2859, 2744, 2801] | [862, 899, 725, 755, 673, 714, 791] | [0, 0, 0, 0, 0, 0, 0, 0] | [225.8, 225.8, 225.9, 226.0, 225.9, 225.9, 225.9, 225.8] |
| 5×1/250 gap 500 | 1 | [2726] | [] | [0] | [226.4] |
| 4×1/15 gap 0 | 4 | [2139, 2081, 2062, 2089] | [837, 843, 805] | [0, 0, 0, 0] | [153.6, 152.5, 152.5, 153.0] |

Estado final de ráfagas: 8×1/250 → done 265932 ms=2801 n=18; 5×1/250 → shoot-error java.lang.RuntimeException: Fail to connect to cameraex service; 4×1/15 → done 368611 ms=2089 n=23

Veredicto: todos_done=NO, sin_shoot_error=NO, sin_franjas_negras=SÍ, sin_dmesg_errores=SÍ, tamaño_1616x1080=SÍ, rearme_estable=SÍ, exposicion_escala_con_velocidad=SÍ
dmesg: 0 líneas nuevas, 0 con palabras de error
