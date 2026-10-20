#!/bin/sh
# Uso: scripts/ghidra_dec.sh salida.json 0xADDR... — decompila con el proyecto silent-liro (solo lectura) y escribe JSON
out=$1; shift
env JAVA_HOME="$PWD/tools/providers/jdk-21.0.12.1+1" timeout 550 tools/providers/ghidra_12.1.4_PUBLIC/support/analyzeHeadless analysis/ghidra silent-liro -process av-cam.bin -noanalysis -readOnly -scriptPath analysis/ghidra -postScript QuerySilentLiro.java "$PWD/$out" "$@" >/dev/null 2>&1
python3 -I -c "
import json,sys
for x in json.load(open(sys.argv[1]))['functions']: print('//',x['entry'],x['status']);print(x['pseudo_code'])" "$out"
