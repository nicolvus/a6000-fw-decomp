"""Reproduce S58-C/D/E sin cámara: escenarios, diferencias por etapa y bus completo.

Desde la raíz: python3 analysis/s58/reproduce.py. Requiere Unicorn y Capstone
ya instalados; conserva el firmware original y escribe solo evidencia derivada.
"""
import json
from pathlib import Path

from a9_a7s_scenarios import MODES, scenario
from a10_true_matrix import R, modes, value


def differences(left, right):
    return [dict(register=key, before=left.get(key), after=right.get(key))
            for key in sorted(left.keys() | right.keys()) if left.get(key) != right.get(key)]


def main():
    output = Path(__file__).parent / 'out'
    output.mkdir(exist_ok=True)
    scenarios = [scenario(mode, shut=shut) for mode in MODES for shut in (0, 1)]
    for result in scenarios:
        if result['err'] or any(result['ret'].values()):
            raise RuntimeError(f"Escenario incompleto: {result['mode']:#x}")
    comparisons = []
    by_mode = {result['mode']: result for result in scenarios if result['shut'] == 0}
    for left, right in ((0x4c, 0x4e), (0x4d, 0x4f), (0x4e, 0x4f), (0x0b, 0x4e), (0x0b, 0x35)):
        a, b = by_mode[left], by_mode[right]
        stages = {stage: differences(a['snaps'][stage], b['snaps'][stage])
                  for stage in a['snaps']}
        wire = lambda result: {f'{dev:02x}:{addr:02x}': data
                               for dev, addr, data in result['device_seq']}
        comparisons.append(dict(before=left, after=right, stages=stages,
                                transmitted=differences(wire(a), wire(b))))
    gain = [scenario(mode, agc=agc) for mode in (0x0b, 0x4e, 0x4f)
            for agc in (0x1000, 0x1001, 0x2000)]
    matrix = [dict(device=row['dev'], address=row['addr'],
                   values={f'{mode:02x}': value(row, mode) for mode in modes}) for row in R]
    (output / 'a7s_scenarios.json').write_text(json.dumps(scenarios, separators=(',', ':')) + '\n')
    (output / 'a7s_effective_diff.json').write_text(json.dumps(dict(
        comparisons=comparisons, gain_scenarios=gain, matrix=matrix), separators=(',', ':')) + '\n')
    print(f'{len(scenarios)} escenarios; {len(gain)} límites AGC; {len(comparisons)} comparaciones; {len(matrix)} filas')


if __name__ == '__main__':
    main()
