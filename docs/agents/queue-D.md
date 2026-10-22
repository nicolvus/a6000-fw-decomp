# Cola carril D (Beam Free) — módulos de línea general pendientes (S500+) (estado: TODO | DOING | DONE <hash> | BLOCKED <causa>)

Tema: decodificación de módulos de la línea general de la A6000 fw3.21 no cubiertos por A/B/C, con comparación A7S fw3.20 y A6300 fw2.01. Foco inicial: módulos de mayor tamaño y exclusivos de A6000 relevantes para captura/imagen.

- TODO S500 Decodificar `[VDF]` (243 trazas): visor, A6000 tiene 81 más que A7S/A6300. Identificar ficheros fuente, funciones emisoras, estructuras, comparación. Informe + tests + JSON.
- TODO S501 Decodificar `[STK]` (76 trazas): eliminado en A6300. Ficheros fuente, funciones, comparación.
- TODO S502 Decodificar `[EIS]` (estabilización electrónica) y su relación con captura.
- TODO S503 Decodificar `[ZPD]` (zero point detection / AF) y su relación con captura.
- TODO S504 Decodificar `[STABILIZER]`.
- TODO S505 Al vaciar, regenerar la cola con los siguientes módulos pendientes del censo S178 (priorizar exclusivos A6000 y los >40 trazas).