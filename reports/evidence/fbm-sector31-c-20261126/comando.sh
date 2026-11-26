#!/bin/sh
# Repetición completa del parche C (FILM-PB-1 · sector FBM 0x31 persistente).
# Todo QEMU sobre copias; la cámara no se toca.  ~4 pasadas de 150 s.
set -e
D=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$D/../../../.." && pwd)          # raíz del repo
H=$R/reports/evidence/film-pb-1-sub-fbm-create-20261126   # lanzador + shim del sub-arnés FBM
OUT=$R/build/cfw_fbm_sector31_c
cd "$R"
. "$R/.venv/bin/activate" 2>/dev/null || true

# 1. build (final + control negativo) y auditorías
python3 "$D/parche_fbm31_c.py" | tee "$D/auditoria-parche-c.txt"
python3 "$D/parche_fbm31_c.py" --fn-dummy --out "$OUT/control-fn-dummy/libmpr.so" \
  | tee "$D/auditoria-control-fn-dummy.txt"
# 2. pre-vuelo Unicorn
python3 "$D/emula_cueva_c.py" "$OUT/libmpr.so" | tee "$D/emulacion-cueva-c.txt"
# 3. desensamblados citados
python3 "$D/dis_evidencia.py" > "$D/dis-funciones-c.txt"

# 4. C1 — primer arranque con el parche, imagen D1 prístina: crea y escribe 1 300 B
FBMFIN='--- IMEXIT' FBMEXTRA="FBMPROBE=1 NF4DUMP=1 NF4IMG=1" \
  python3 "$H/fbm_run.py" 200 "$D/runC1" "$OUT/libmpr.so" > "$D/runC1.driver.log" 2>&1
python3 "$D/resumen_imagen.py" "$D/runC1/nflash4.img" | tee "$D/imagen-diferencias.txt"
# las tres páginas cambiadas se quedan como evidencia; la imagen de 10 MiB NO se versiona
for par in 9D400 BD400 380000; do
  python3 -c "import sys;d=open(sys.argv[1],'rb').read();o=int(sys.argv[2],16);open(sys.argv[3],'wb').write(d[o:o+0x400])" \
    "$D/runC1/nflash4.img" "$par" "$D/pagina-$par.bin"
done
rm -f "$D/runC1/nflash4.img"
python3 "$D/reconstruye_imagen.py" /tmp/nflasha4-tras-C1.img | tee "$D/reconstruccion.txt"
IMG=/tmp/nflasha4-tras-C1.img

# 5. C2 — LA PRUEBA: segundo arranque con el libmpr DE FÁBRICA sobre la imagen de C1
FBMNFLASH4="$IMG" FBMFIN='--- IMEXIT' FBMEXTRA="FBMPROBE=1 NF4DUMP=1" \
  python3 "$H/fbm_run.py" 200 "$D/runC2" "" > "$D/runC2.driver.log" 2>&1

# 6. C3 — riesgo: parche cargado con el sector ya presente (0 escrituras)
FBMNFLASH4="$IMG" FBMFIN='--- IMEXIT' FBMEXTRA="FBMPROBE=1 NF4DUMP=1" \
  python3 "$H/fbm_run.py" 200 "$D/runC3" "$OUT/libmpr.so" > "$D/runC3.driver.log" 2>&1

# 7. control negativo: fn = dummy de fábrica 0x2B5185 (se cae; 394 B)
FBMFIN='--- IMEXIT' FBMEXTRA="FBMPROBE=1 NF4DUMP=1" \
  python3 "$H/fbm_run.py" 200 "$D/runX-control-fn-dummy" "$OUT/control-fn-dummy/libmpr.so" \
  > "$D/runX-control-fn-dummy.driver.log" 2>&1

# 8. resumen de lo medido
for f in runC1 runC2 runC3 runX-control-fn-dummy; do
  echo "== $f"
  grep -a "gancho@7126e6\|PROBE t=25s idx=10 \|CheckExistSector(0x31)\|ReadFirstPackData\|NF4DIFF bytes\|alive=" \
    "$D/$f/consola.log" | sed 's/\r//' | cut -c1-170
done
