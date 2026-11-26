// App de LUT propios: .cube → .LUT para la SD + previsualización con la cadena de la cámara.
import { aplicaColor, aplicaCube, convierte, parseCube } from "./lut.js";

const MAX_LADO = 900;                    // suficiente para juzgar el color y rápido en cualquier portátil
const $ = (id) => document.getElementById(id);
const lista = $("lista"), error = $("error"), sinFoto = $("sin-foto");
const lienzos = $("lienzos"), opcionExacta = $("opcion-exacta"), exacto = $("exacto");
const antes = $("antes"), despues = $("despues"), detalle = $("detalle"), tituloDespues = $("titulo-despues");

let entradas = [];                       // {nombre, n, titulo, tabla, pkg, nodos, cube}
let foto = null;                         // {imagen: ImageData}
let seleccion = 0;

function fallo(msg) {
  error.textContent = msg;
  error.hidden = !msg;
}

function descarga(e, ranura) {
  const url = URL.createObjectURL(new Blob([e.pkg], { type: "application/octet-stream" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = `LUT${ranura}.LUT`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}

function pintaLista() {
  lista.textContent = "";
  entradas.forEach((e, i) => {
    const li = document.createElement("li");
    const fila = document.createElement("div");
    fila.className = "fila";
    const nombre = document.createElement("span");
    nombre.className = "nombre";
    nombre.textContent = e.titulo || e.nombre;
    const meta = document.createElement("span");
    meta.className = "meta";
    const rec = e.nodos.reduce((n, v) => n + (v === 63 || v === -64 ? 1 : 0), 0);
    meta.textContent = `${e.n}³ · ${e.pkg.length} B · ${rec} valores al tope (±63)`;
    const sel = document.createElement("select");
    for (let r = 1; r <= 6; r++) sel.append(new Option(`ranura ${r}`, r, false, r === i + 1));
    sel.addEventListener("change", () => descarga(e, Number(sel.value)));
    const boton = document.createElement("button");
    boton.textContent = "Descargar .LUT";
    boton.addEventListener("click", () => descarga(e, Number(sel.value)));
    const ver = document.createElement("button");
    ver.textContent = "Ver en la foto";
    ver.addEventListener("click", () => { seleccion = i; pintaFoto(); });
    fila.append(nombre, meta, sel, boton, ver);
    li.append(fila);
    lista.append(li);
  });
}

function pintaFoto() {
  if (!foto || !entradas.length) return;
  const e = entradas[Math.min(seleccion, entradas.length - 1)];
  const src = foto.imagen;
  const dst = new ImageData(new Uint8ClampedArray(src.data.length), src.width, src.height);
  const usarExacto = exacto.checked;
  for (let o = 0; o < src.data.length; o += 4) {
    const r = src.data[o] / 255, g = src.data[o + 1] / 255, b = src.data[o + 2] / 255;
    const v = usarExacto ? aplicaCube(e.cube, r, g, b) : aplicaColor(r, g, b, e.nodos);
    dst.data[o] = Math.round(Math.min(Math.max(v[0], 0), 1) * 255);
    dst.data[o + 1] = Math.round(Math.min(Math.max(v[1], 0), 1) * 255);
    dst.data[o + 2] = Math.round(Math.min(Math.max(v[2], 0), 1) * 255);
    dst.data[o + 3] = src.data[o + 3];
  }
  antes.getContext("2d").putImageData(src, 0, 0);
  despues.getContext("2d").putImageData(dst, 0, 0);
  tituloDespues.textContent = usarExacto ? `Cube exacto · ${e.n}³` : "Cámara · tabla 5×9×9";
  detalle.textContent = `Viendo «${e.titulo || e.nombre}» en la ranura ${entradas.indexOf(e) + 1}. ` +
    (usarExacto ? "Referencia del propio .cube (mejor que lo que puede hacer la cámara)." : "Es lo que aplica la tabla de 405 nodos que va a la tarjeta.");
  lienzos.hidden = false;
  opcionExacta.hidden = false;
  sinFoto.hidden = true;
}

async function cargaFoto(archivo) {
  const bmp = await createImageBitmap(archivo);
  const escala = Math.min(1, MAX_LADO / Math.max(bmp.width, bmp.height));
  const w = Math.max(1, Math.round(bmp.width * escala)), h = Math.max(1, Math.round(bmp.height * escala));
  for (const c of [antes, despues]) { c.width = w; c.height = h; }
  const off = new OffscreenCanvas(w, h);
  const ctx = off.getContext("2d");
  ctx.drawImage(bmp, 0, 0, w, h);
  foto = { imagen: ctx.getImageData(0, 0, w, h) };
  pintaFoto();
}

async function cargaCubes(archivos) {
  fallo("");
  for (const f of [...archivos].slice(0, 6)) {
    try {
      const texto = await f.text();
      const r = convierte(texto);
      entradas.push({ nombre: f.name, n: r.n, titulo: r.titulo, tabla: r.tabla, pkg: r.pkg, nodos: r.nodos, cube: parseCube(texto) });
    } catch (err) {
      fallo(`${f.name}: ${err.message}`);
    }
  }
  seleccion = Math.min(seleccion, Math.max(0, entradas.length - 1));
  pintaLista();
  if (foto) pintaFoto();
}

$("cubes").addEventListener("change", (ev) => cargaCubes(ev.target.files));
$("foto").addEventListener("change", async (ev) => {
  if (!ev.target.files[0]) return;
  try { await cargaFoto(ev.target.files[0]); } catch (err) { fallo(`no se pudo leer la foto: ${err.message}`); }
});
exacto.addEventListener("change", pintaFoto);
