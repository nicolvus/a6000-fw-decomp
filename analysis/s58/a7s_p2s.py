"""S58-C: decodifica las tramas que el código real de la A7S (Execute) escribe en la FIFO del P2S (0xf3c00340 + 4*i, 1 byte por palabra).
Segmentación: un disparo = secuencia de escrituras a 0xf3c00808 (1,0,1) emitida en 0x436f26f0..0x436f26f4 (rutina real 0x436f26ae..). Cada trama de FIFO = 81|len|81|ADDR8|DATA..."""
FIFO, FIFO_END = 0xf3c00340, 0xf3c00600
def transactions(writes):
    txs, cur = [], {}
    for pc, a, sz, v, tag in writes:
        if FIFO <= a < FIFO_END: cur[(a - FIFO) // 4] = v & 0xff
        elif a == 0xf3c00808 and pc == 0x436f26f0:             # disparo (flanco 1 de la secuencia 1,0,1)
            txs.append(bytes(cur[i] for i in range(max(cur) + 1)) if cur else b''); cur = {}
    if cur: txs.append(bytes(cur[i] for i in range(max(cur) + 1)))
    return txs
def regs(txs):
    """Vista compatible del dispositivo 0x81; usar device_regs para el bus completo."""
    return [(a, v) for dev, a, v in device_regs(txs) if dev == 0x81]

def device_regs(txs):
    """Conserva dispositivo, duplicados y orden; acepta el terminador 00 de la FIFO."""
    seq = []
    for payload in txs:
        i = 0
        while i < len(payload):
            if payload[i:] == b'\x00':
                break
            if i + 2 > len(payload) or payload[i] != 0x81:
                raise ValueError('Cabecera P2S inválida')
            n = payload[i + 1]
            body = payload[i + 2:i + 2 + n]
            if n < 3 or len(body) != n or body[0] not in (0x81, 0x83):
                raise ValueError('Trama P2S incompleta o dispositivo desconocido')
            seq.extend((body[0], body[1] + k, value) for k, value in enumerate(body[2:]))
            i += 2 + n
    return seq
