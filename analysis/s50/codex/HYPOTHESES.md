# Hipótesis S50 B (por resolver contra REA)

| ID | Hipótesis comprobable | Prueba/discriminante | Evidencia contraria conocida |
|---|---|---|---|
| H1 | Clase 2 de SetExposure permite fin electrónico | Semántica de ID1 bits d4/94, IDs100/101, tiempo+3a0 y secuencia externa sin cierre | Ningún significado eléctrico de bits documentado; secuencia externa ordinaria solicita CAIF |
| H2 | Una secuencia interna sin CAIF basta | Resolver fila externa + selector interno y guardas | S21: filas normales +a0..+118 pasan por Stage_CaComm |
| H3 | cap+74f=0 permite omitir petición mecánica manteniendo foto | Cuerpo Stage_CaComm, productor/identidad de campo, efecto en estados | Puede ser estado de reintentos, cancelación o prerrequisito, no selector físico |
| H4 | Fila externa+12c aporta foto sin cierre | Resolver inicializador y fila43b1c0e2, cap+4b70=7 y exposición0 | Rama relacionada con reproceso; CAIF evento12 no tiene semántica física demostrada |
| H5 | Clases1/2/3/6 de S49 equivalen a clases de obturación | Seguir quién consume el tercer campo de las filas y discriminar dominios | DESCARTADA: son cantidades de callbacks, verificadas por437da2f2..31e y listas de punteros; 437da100 además pasa cantidad de filas a43af6870, otro contador distinto |
| H6 | Hardware impide cualquier foto electrónica completa | Evidencia de circuito/modo de sensor que excluya reset/lectura por filas completa | No hay datasheet con significado de bits; existen modos6000x4000 y EFCS pero no bastan para probar posibilidad |
| H7 | VD/callback/finDMA prueba fin de exposición | Cerrar origen físico y asociación con fotograma | S32/S34 distinguen ventana/software, DMA y exposición |

No se debe convertir falta de prueba en descarte físico. Global electrónico y electrónico por filas son objetivos distintos; el usuario requiere inicio/fin electrónicos sin cierre, no simultaneidad global.
