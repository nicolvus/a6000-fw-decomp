// CLI mínima: node lut_cli.mjs ENTRADA.cube SALIDA.LUT   (para tests cruzados y uso sin navegador)
import { readFileSync, writeFileSync } from "node:fs";
import { convierte } from "./lut.js";

const [entrada, salida] = process.argv.slice(2);
if (!entrada || !salida) {
  console.error("uso: node lut_cli.mjs ENTRADA.cube SALIDA.LUT");
  process.exit(2);
}
try {
  const r = convierte(readFileSync(entrada, "utf8"));
  writeFileSync(salida, r.pkg);
  console.log(`LUT ${r.n}³ → ${salida} (${r.pkg.length} B)`);
} catch (e) {
  console.error(`error: ${e.message}`);
  process.exit(1);
}
