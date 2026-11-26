// App de LUT propios: .cube (o .LUT ya generado) → fichero de la SD + previsualización del fichero final.
import { aplicaColor, aplicaCube, convierte, leeLut, parseCube } from "./lut.js";

const MAX_LADO = 900;                    // suficiente para juzgar el color y rápido en cualquier portátil
const $ = (id) => document.getElementById(id);
const lista = $("lista"), error = $("error"), sinFoto = $("sin-foto");
const lienzos = $("lienzos"), opcionExacta = $("opcion-exacta"), exacto = $("exacto");
const antes = $("antes"), despues = $("despues"), detalle = $("detalle"), tituloDespues = $("titulo-despues");

let entradas = [];                       // {nombre, tipo, n, titulo, pkg, lut: {nodos, curva}, sha, ranura, cube}
let foto = null;                         // {imagen: ImageData}
let seleccion = 0;

function fallo(msg) {
  error.textContent = msg;
  error.hidden = !msg;
}

const hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
const sha256 = async (bytes) => hex(await crypto.subtle.digest("SHA-256", bytes));

function descarga(e) {
  const url = URL.createObjectURL(new Blob([e.pkg], { type: "application/octet-stream" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = `LUT${e.ranura}.LUT`;
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
    const rec = e.lut.nodos.reduce((n, v) => n + (v === 63 || v === -64 ? 1 : 0), 0);
    meta.textContent = `${e.tipo === "LUT" ? "paquete " + (e.lut.curva ? "v2 con curva" : "v1/v2 sin curva") : e.n + "³"} · ` +
      `${e.pkg.length} B · ${rec} nodos al tope · sha256 ${e.sha.slice(0, 12)}…`;
    const sel = document.createElement("select");
    for (let r = 1; r <= 6; r++) sel.append(new Option(`ranura ${r}`, r, false, r === e.ranura));
    sel.addEventListener("change", () => { e.ranura = Number(sel.value); pintaLista(); });
    const boton = document.createElement("button");
    boton.textContent = `Descargar LUT${e.ranura}.LUT`;
    boton.addEventListener("click", () => descarga(e));
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
  const usarExacto = exacto.checked && e.cube;
  for (let o = 0; o < src.data.length; o += 4) {
    const r = src.data[o] / 255, g = src.data[o + 1] / 255, b = src.data[o + 2] / 255;
    const v = usarExacto ? aplicaCube(e.cube, r, g, b) : aplicaColor(r, g, b, e.lut.nodos, e.lut.curva);
    dst.data[o] = Math.round(Math.min(Math.max(v[0], 0), 1) * 255);
    dst.data[o + 1] = Math.round(Math.min(Math.max(v[1], 0), 1) * 255);
    dst.data[o + 2] = Math.round(Math.min(Math.max(v[2], 0), 1) * 255);
    dst.data[o + 3] = src.data[o + 3];
  }
  antes.getContext("2d").putImageData(src, 0, 0);
  despues.getContext("2d").putImageData(dst, 0, 0);
  tituloDespues.textContent = usarExacto ? `Cube exacto · ${e.n}³` : `Fichero LUT${e.ranura}.LUT · tabla 5×9×9` + (e.lut.curva ? " + curva" : "");
  detalle.textContent = `Viendo «${e.titulo || e.nombre}» tal como se guardará: LUT${e.ranura}.LUT · ${e.pkg.length} B · ` +
    `sha256 ${e.sha}` + (usarExacto ? " (comparación con el .cube exacto, no es el fichero)" : "");
  lienzos.hidden = false;
  opcionExacta.hidden = !e.cube;
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

/** Acepta `.cube` (se convierte) o `.LUT` v1/v2 (se usa el fichero tal cual). */
async function carga(archivos) {
  fallo("");
  for (const f of [...archivos].slice(0, 6)) {
    try {
      const esLut = /\.lut$/i.test(f.name);
      let pkg, n = null, titulo = "", cube = null;
      if (esLut) {
        pkg = new Uint8Array(await f.arrayBuffer());
      } else {
        const texto = await f.text();
        cube = parseCube(texto);
        const r = convierte(cube);
        pkg = r.pkg;
        n = r.n;
        titulo = r.titulo;
      }
      const lut = leeLut(pkg);
      if (!lut) throw new Error("no es un paquete A6LT v1/v2 íntegro (cabecera o CRC32)");
      const sha = await sha256(pkg);
      entradas.push({ nombre: f.name, tipo: esLut ? "LUT" : "cube", n, titulo, pkg, lut, sha, cube,
                      ranura: Math.min(entradas.length + 1, 6) });
    } catch (err) {
      fallo(`${f.name}: ${err.message}`);
    }
  }
  seleccion = Math.min(seleccion, Math.max(0, entradas.length - 1));
  pintaLista();
  if (foto) pintaFoto();
}

$("cubes").addEventListener("change", (ev) => carga(ev.target.files));
$("foto").addEventListener("change", async (ev) => {
  if (!ev.target.files[0]) return;
  try { await cargaFoto(ev.target.files[0]); } catch (err) { fallo(`no se pudo leer la foto: ${err.message}`); }
});
exacto.addEventListener("change", pintaFoto);
