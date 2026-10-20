"""Límite conservador: reserva el contexto máximo entero, sin asumir caché."""
from decimal import Decimal

MILLION = Decimal(1000000)
MAX_INPUT = 1100000  # Superior a 1M/1Mi documentados; incluye todo el contexto.
MAX_OUTPUT = 8192
RESERVATION = (Decimal(MAX_INPUT) * Decimal('0.3')
               + Decimal(MAX_OUTPUT) * Decimal('1.2')) / MILLION


def actual_cost(usage: dict, peak: bool) -> Decimal:
    prompt = usage['prompt_tokens']
    hit = usage['prompt_cache_hit_tokens']
    miss = usage['prompt_cache_miss_tokens']
    output = usage['completion_tokens']
    if any(not isinstance(x, int) or x < 0 for x in (prompt, hit, miss, output)):
        raise ValueError('Invalid usage')
    if hit + miss != prompt or prompt > MAX_INPUT or output > MAX_OUTPUT:
        raise ValueError('Usage exceeds reservation or inconsistent cache counters')
    # completion_tokens ya incluye reasoning_tokens: no sumar dos veces.
    factor = Decimal(2 if peak else 1)
    return factor * (Decimal(hit) * Decimal('0.003')
                     + Decimal(miss) * Decimal('0.15')
                     + Decimal(output) * Decimal('0.6')) / MILLION


class Guard:
    def __init__(self, spent: Decimal = Decimal(0)):
        self.spent = spent
        self.pending = False

    def reserve(self) -> Decimal:
        if self.pending or self.spent >= Decimal('0.85'):
            raise ValueError('Pending/uncertain charge or preventive threshold')
        if self.spent + RESERVATION > 1:
            raise ValueError('Next worst-case request exceeds USD 1')
        self.pending = True
        return RESERVATION

    def settle(self, model: str, usage: dict, peak: bool) -> Decimal:
        if not self.pending or model not in ('deepseek-flash', 'DeepSeek-V4.1-Flash-1017'):
            raise ValueError('Unexpected effective model or no reservation')
        cost = actual_cost(usage, peak)
        if cost > RESERVATION:
            raise ValueError('Charge exceeds reservation')
        self.spent += cost
        self.pending = False
        return cost
