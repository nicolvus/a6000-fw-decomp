"""Recalcula labels.json para las etiquetas de labels_scope.json (alcance fijado: pendientes y documentadas con líneas abiertas antes de OTROS)."""
import json, sys
sys.path.insert(0, "analysis/camera_closure")
import labels as L
scope = json.load(open("analysis/camera_closure/labels_scope.json"))
out = {}
for k in sorted(scope):
    out[k] = L.evaluate(k)
    out[k]["estado_previo"] = scope[k]
json.dump(out, open("analysis/camera_closure/labels.json", "w"), indent=1, ensure_ascii=False)
print(len(out))
