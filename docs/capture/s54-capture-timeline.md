# S54-E — Cronología lógica de captura (20-10-2026)

Modelo **de orden de código**, no de tiempos físicos: las llamadas pueden ejecutarse en tareas/IRQ distintas (cola OSAL, MFS5 CSIO, tick `0x93e6`).
`→` = orden demostrado en un mismo flujo; `⇢` = relación inferida entre componentes. Referencias: S21 (pulsación→CAIF), S53 (CAIF→Darwin), S54-A/B/C.

```mermaid
sequenceDiagram
  participant LIRO as BIONZ av-cam (Stage_CaComm 0x438c2538)
  participant D as Darwin FM3 (parser 0x17f8c / 0x18396)
  participant M as Bobinas P4D/P4E
  participant P as P4C (CA_1ST_CURTAIN_START)
  participant S as IMX210/IMX235 (vía DFE)
  LIRO->>D: CAIF ev1 22 B (mss-async ID 0x0c, MFS5)  [VERIFICADO envío; ID↔0x10300 INFERENCIA fuerte]
  Note over D: A7S: pkt[+0x12]&0x20 -> no_silent=0; A6000: bit descartado
  D->>D: 0x20544 despacha (a0<0, =0, >0) / A7S 0x20f52
  alt mecánica (tipo 1/2/3, y A7S no Silent)
    D->>M: P4E←1 · P4D←0 (orden según variante, ver informe 1 §4)
    D->>P: P4C←0
    D->>D: seguimiento ADC de fases (S+0x153)
  else sin mecanismo (A6000 tipo 0 · A7S Silent)
    D->>D: 0x20408, 0x210c0, espera w(t)
    D->>P: P4C←0
  end
  P-->>LIRO: ⇢ SENS_B / GPIO_9 (consumidor NO localizado)
  D-->>LIRO: respuestas MSS (ExposureEndNotify 2 B → ExposureEndRes op 0x40300)  [tabla de trazas VERIFICADA; flujo INFERENCIA]
  LIRO->>S: SetExposure / modo (A7S Silent: 0x4e/0x4f; A6000: ShutMode IMX210) [efecto eléctrico NO VERIFICADO]
```

## Escenarios

| Escenario | Orden demostrado | Relaciones solo hipotéticas |
|---|---|---|
| A7S mecánica | ev1 → parser → bobinas (E/D) → P4C←0 → ADC | consumo de P4C por BIONZ |
| A7S Silent | ev1 con `+0x12&0x20` → parser (`no_silent=0`) → `0x20dfa`, `0x21b5a`, w(t), P4C←0; sin bobinas ni ADC; reposición **sí** actúa (`no_silent=1`) | P4C como sincronía con el sensor IMX235 Silent |
| A6000 mecánica | idéntica a A7S mecánica | — |
| A6000 EFCS | misma ruta Darwin (la 1ª cortina electrónica es de BIONZ/LIRO, S50: `0xb6` inerte) | cómo/si BIONZ usa P4C en EFCS |
| A6000 tipo 0 (**solo modelo estático hipotético**) | idéntica a A7S Silent en exposición; **ninguna** bobina ni en reposición | que BIONZ aceptase esa ausencia de eventos mecánicos; tiempo/final del sensor |

## Lo que falta para un modelo temporal real

Reloj del tick de Darwin, latencia MFS5, consumidor de P4C en BIONZ, escritor del byte de tipo, registro del IMX210 para fin de integración.
No se atribuyen duraciones físicas.
