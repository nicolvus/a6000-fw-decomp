#!/bin/sh
# itera.sh [pasos]: ejecuta la LIRO VM y desensambla el bucle donde gira la tarea más atascada (siguiente regla MMIO que falta).
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); O=${TMPDIR:-/tmp}/liro_itera.json
"$R/.venv/bin/python" "$D/liro_vm.py" --pasos "${1:-10000000}" --informe "$O" | tail -1
PCS=$("$R/.venv/bin/python" -c "import json,sys;d=json.load(open('$O'));g=d['giros'];print(' '.join(x.split('pc=')[1].split()[0] for x in g[:1]))")
"$R/.venv/bin/python" -c "import json;d=json.load(open('$O'));print(d['giros'][:4]);print([x for x in d['registro'] if 'ERROR' in x or 'reposo' in x][-3:])"
[ -n "$PCS" ] && cd "$D" && "$R/.venv/bin/python" bucle.py $PCS 2>/dev/null
