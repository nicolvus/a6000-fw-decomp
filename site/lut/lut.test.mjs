// Pruebas del conversor web: node --test site/lut/
import assert from "node:assert/strict";
import { test } from "node:test";
import { aplicaColor, convierte, crc32, desempaqueta, leeLut, parseCube, referencia, tablaANodos } from "./lut.js";

function cuboTexto(n, f) {
  const filas = [];
  for (let r = 0; r < n; r++)
    for (let g = 0; g < n; g++)
      for (let b = 0; b < n; b++) {
        const v = f(r / (n - 1), g / (n - 1), b / (n - 1));
        filas.push(v.map((x) => x.toFixed(6)).join(" "));
      }
  return `TITLE "prueba"\nLUT_3D_SIZE ${n}\n` + filas.join("\n") + "\n";
}

const identidad = cuboTexto(5, (r, g, b) => [r, g, b]);
const calido = cuboTexto(5, (r, g, b) => [Math.min(1, r * 1.1), g * 0.9, b * 0.8]);

test("parsea y rechaza lo que no es una LUT 3D completa", () => {
  const c = parseCube(identidad);
  assert.equal(c.n, 5);
  assert.equal(c.cub.length, 125 * 3);
  assert.throws(() => parseCube(identidad.replace("LUT_3D_SIZE 5", "LUT_3D_SIZE 1")), /LUT_3D_SIZE/);
  assert.throws(() => parseCube("LUT_1D_SIZE 8\n0 0 0\n"), /3D/);
  assert.throws(() => parseCube("LUT_3D_SIZE 2\n0 0 0\n"), /faltan filas/);
});

test("la tabla es de 1064 B y la identidad deja los grises donde estaban", () => {
  const t = referencia(parseCube(identidad));
  assert.equal(t.length, 1064);
  const q = tablaANodos(t);
  assert.ok(q.every((v) => v >= -64 && v <= 63));      // los nodos de croma extremo salen del gamut y saturan (igual que en la cámara)
  for (const v of [0, 0.18, 0.5, 0.9, 1]) {
    const [r, g, b] = aplicaColor(v, v, v, q);
    assert.ok(Math.abs(r - v) < 2 / 255 && Math.abs(g - v) < 2 / 255 && Math.abs(b - v) < 2 / 255, `gris ${v}`);
  }
});

test("la previsualización sale del fichero que se descarga", () => {
  const { pkg, tabla } = convierte(calido);
  const leido = leeLut(pkg);
  assert.deepEqual([...leido.tabla], [...tabla]);
  assert.deepEqual([...leido.nodos], [...tablaANodos(tabla)]);
  assert.equal(leido.curva, null);
});

test("el paquete v1 lleva CRC válido y se vuelve a leer", () => {
  const { tabla, pkg } = convierte(calido);
  assert.equal(pkg.length, 1080);
  assert.equal(String.fromCharCode(...pkg.slice(0, 4)), "A6LT");
  assert.equal(new DataView(pkg.buffer).getUint32(8, true), crc32(tabla));
  const r = desempaqueta(pkg);
  assert.deepEqual([...r.tabla], [...tabla]);
  assert.equal(r.curva, null);
  const roto = pkg.slice();
  roto[100] ^= 1;
  assert.equal(desempaqueta(roto), null);
  assert.equal(leeLut(roto), null);
});

test("un LUT v2 con curva se lee y la curva se aplica antes de la tabla", () => {
  const { tabla } = convierte(identidad);
  const curva = new Uint8Array(2048);
  const dv = new DataView(curva.buffer);
  for (let i = 0; i < 1024; i++) dv.setUint16(2 * i, Math.round(i * 0.8), true);   // 0,8·x: oscurece los medios tonos
  const v2 = new Uint8Array(16 + 1064 + 2048);
  const dv2 = new DataView(v2.buffer);
  dv2.setUint32(0, 0x544c3641, true); dv2.setUint8(4, 2); dv2.setUint8(5, 1); dv2.setUint16(6, 1064, true);
  v2.set(tabla, 16); v2.set(curva, 16 + 1064);
  const todo = new Uint8Array(tabla.length + curva.length);
  todo.set(tabla); todo.set(curva, tabla.length);
  dv2.setUint32(8, crc32(todo), true);
  const leido = leeLut(v2);
  assert.ok(leido && leido.curva instanceof Uint16Array && leido.curva[512] === Math.round(512 * 0.8));
  const [r] = aplicaColor(0.5, 0.5, 0.5, leido.nodos, leido.curva);
  assert.ok(Math.abs(r - Math.round(0.5 * 1023) * 0.8 / 1023) < 3 / 255, String(r));
});

test("convierte() no depende del paquete para la previsualización", () => {
  const a = leeLut(convierte(identidad).pkg), b = leeLut(convierte(calido).pkg);
  assert.notDeepEqual([...a.nodos], [...b.nodos]);
  assert.deepEqual([...leeLut(convierte(identidad).pkg).pkg], [...convierte(identidad).pkg]);
});
