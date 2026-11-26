// LUT propios para la Sony A6000 — misma matemática que el firmware (scripts/lut).
// El paquete `.LUT` (v1) es idéntico al que produce `lut_sd_userland.referencia()` en el PC:
//   cabecera `A6LT` · versión 1 · 0 · 1064 (u16) · CRC32 IEEE · 0 · tabla 405 nodos × 21 bits.
// La previsualización aplica EXACTAMENTE esa tabla con la cadena modelada de la cámara
// (`cube_a6000.Cadena` con M = I y T = sRGB: sRGB → YCbCr BT.601 → LUT 5×9×9 de deltas s7 → RGB).
// Límite conocido: no modela demosaico, NR ni la gamma propia del JPEG; el resto de la cadena es el del repo.

export const TAM_TABLA = 1064;
export const TAM_PKG = 1080;
export const SLOTS = 6;
const MAGIC = 0x544c3641;            // "A6LT"
const UY = 1 / 256;                  // 1 unidad s7 de ΔY en 0…256
const UC = 0.75 / 256;               // 1 unidad s7 de Δ croma (0,75 códigos de ±128)
const NY = 5, NC = 9;

const floor = Math.floor;
const shr = (a, b) => floor(a / 2 ** b);

// ---------- .cube ----------
/** Analiza un `.cube` 3D y devuelve `{n, lo, hi, cub}` en Q16 (o lanza Error con el motivo). */
export function parseCube(texto) {
  let n = 0, lo = [0, 0, 0], hi = [65536, 65536, 65536], cub = null, filled = 0, titulo = "";
  for (const cruda of String(texto).split(/\r?\n/)) {
    const ln = cruda.split("#")[0].slice(0, 200).trim();
    if (!ln) continue;
    if (ln.startsWith("TITLE") && !titulo) {
      titulo = ln.slice(5).trim().replace(/^"|"$/g, "");
    } else if (ln.startsWith("LUT_3D_SIZE")) {
      const m = ln.slice(11).trim().match(/^\d+/);
      n = m ? Number(m[0]) : 0;
      if (n < 2 || n > 64 || cub) throw new Error(`LUT_3D_SIZE inválido o repetido (${n}); se admiten 2…64`);
      cub = new Int32Array(n * n * n * 3);
    } else if (ln.startsWith("DOMAIN_MIN") || ln.startsWith("DOMAIN_MAX")) {
      const dst = ln[8] === "I" ? lo : hi;
      const v = ln.slice(10).trim().split(/\s+/).slice(0, 3).map(Number);
      if (v.length !== 3 || v.some((x) => !Number.isFinite(x))) throw new Error(`dominio inválido: ${ln}`);
      for (let k = 0; k < 3; k++) dst[k] = Math.round(v[k] * 65536);
    } else if (ln.startsWith("LUT_1D") || ln.startsWith("LUT_3D_INPUT")) {
      throw new Error("solo se admiten LUT 3D (.cube de un solo LUT_3D_SIZE)");
    } else if (/^[-+.\d]/.test(ln)) {
      if (!cub) throw new Error("filas antes de LUT_3D_SIZE");
      if (filled >= n * n * n) throw new Error(`hay más filas que ${n}³`);
      const v = ln.split(/\s+/).slice(0, 3).map(Number);
      if (v.length !== 3 || v.some((x) => !Number.isFinite(x))) throw new Error(`fila inválida: ${ln}`);
      for (let k = 0; k < 3; k++) cub[filled * 3 + k] = Math.round(v[k] * 65536);
      filled++;
    }
  }
  if (!cub) throw new Error("falta LUT_3D_SIZE");
  if (filled !== n * n * n) throw new Error(`faltan filas: ${filled} de ${n ** 3}`);
  return { n, lo, hi, cub, titulo };
}

// ---------- tabla 5×9×9 (réplica de lutsd.c `nodos`) ----------
const clamp16 = (v) => (v < 0 ? 0 : v > 65536 ? 65536 : v);

function ycc(r, g, b) {
  const y = shr(19595 * r + 38470 * g + 7471 * b, 16);
  return [y, shr((b - y) * 36984, 16), shr((r - y) * 46743, 16)];
}

function trilineal(c, x) {
  const i0 = [0, 0, 0], f = [0, 0, 0];
  for (let k = 0; k < 3; k++) {
    const den = c.hi[k] - c.lo[k];
    let u = 0;
    if (den > 0 && x[k] > c.lo[k]) u = floor(((x[k] - c.lo[k]) * 65536) / den);
    if (u > 65536) u = 65536;
    u *= c.n - 1;
    let i = shr(u, 16);
    if (i > c.n - 2) i = c.n - 2;
    i0[k] = i;
    f[k] = u - i * 65536;
  }
  const out = [0, 0, 0];
  for (let ch = 0; ch < 3; ch++) {
    let acc = 0;
    for (let d = 0; d < 8; d++) {
      const dr = d & 1, dg = (d >> 1) & 1, db = (d >> 2) & 1;
      let w = shr((dr ? f[0] : 65536 - f[0]) * (dg ? f[1] : 65536 - f[1]), 16);
      w = shr(w * (db ? f[2] : 65536 - f[2]), 16);
      const idx = (((i0[2] + db) * c.n + i0[1] + dg) * c.n + i0[0] + dr) * 3 + ch;
      acc += w * c.cub[idx];
    }
    out[ch] = shr(acc, 16);
  }
  return out;
}

/** 405 nodos → 1064 B (21 bits/nodo), idéntico byte a byte a `lutsd.c` (`G90`: corrección Δ²/12). */
export function referencia(c) {
  const sat = (q) => (q < -64 ? -64 : q > 63 ? 63 : q);
  const z = new Int32Array(405 * 3);
  for (let i = 0; i < 405; i++) {
    const j = floor(i / 81), a = floor(i / 9) % 9, b = i % 9;
    const y = j * 16384, cb = a * 8192 - 32768, cr = b * 8192 - 32768;
    const r = clamp16(y + shr(91882 * cr, 16));
    const bl = clamp16(y + shr(116131 * cb, 16));
    const n16 = shr((y * 65536 - 19595 * r - 7471 * bl), 16);
    const g = clamp16(shr(n16 * 111642, 16));
    const u = ycc(r, g, bl), t = ycc(...trilineal(c, [r, g, bl]));
    z[3 * i] = shr(t[0] - u[0] + 8, 4);
    z[3 * i + 1] = shr((t[1] - u[1]) * 5456 + 32768, 16);
    z[3 * i + 2] = shr((t[2] - u[2]) * 5456 + 32768, 16);
  }
  const bits = new Uint8Array(TAM_TABLA);
  for (let i = 0; i < 405; i++) {
    const j = floor(i / 81), a = floor(i / 9) % 9, b = i % 9;
    const q = [0, 1, 2].map((k) => {
      let l = 0;
      for (const [ok, paso] of [[j > 0 && j < 4, 81], [a > 0 && a < 8, 9], [b > 0 && b < 8, 1]]) {
        if (ok) l += z[3 * (i + paso) + k] - 2 * z[3 * i + k] + z[3 * (i - paso) + k];
      }
      return sat(shr(z[3 * i + k] - shr(21 * l, 8) + 8, 4));
    });
    const w = ((q[0] & 127) << 14) | ((q[1] & 127) << 7) | (q[2] & 127);
    for (let k = 0; k < 21; k++) {
      const bit = i * 21 + k;
      if ((w >> k) & 1) bits[bit >> 3] |= 1 << (bit & 7);
    }
  }
  return bits;
}

// ---------- paquete `.LUT` v1 ----------
export function crc32(bytes) {
  let c = 0xFFFFFFFF;
  for (let i = 0; i < bytes.length; i++) {
    c ^= bytes[i];
    for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xEDB88320 & -(c & 1));
  }
  return (c ^ 0xFFFFFFFF) >>> 0;
}

/** Envuelve la tabla en el paquete v1 de 1080 B que lee el userland de la cámara. */
export function paquete(tabla) {
  if (tabla.length !== TAM_TABLA) throw new Error(`la tabla debe ser de ${TAM_TABLA} B`);
  const b = new Uint8Array(TAM_PKG);
  const dv = new DataView(b.buffer);
  dv.setUint32(0, MAGIC, true);
  b[4] = 1;                 // versión
  b[5] = 0;                 // usa_T
  dv.setUint16(6, TAM_TABLA, true);
  dv.setUint32(8, crc32(tabla), true);
  dv.setUint32(12, 0, true);
  b.set(tabla, 16);
  return b;
}

/** Carga si el paquete es íntegro (v1 o v2), como `lut_pkg.desempaqueta`. */
export function desempaqueta(bytes) {
  const b = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  if (b.length < 16) return null;
  const dv = new DataView(b.buffer, b.byteOffset, b.byteLength);
  if (dv.getUint32(0, true) !== MAGIC || dv.getUint16(6, true) !== TAM_TABLA) return null;
  const ver = b[4], crc = dv.getUint32(8, true);
  if (ver === 1 && b.length === TAM_PKG) {
    const carga = b.slice(16);
    return crc32(carga) === crc ? { tabla: carga, curva: null } : null;
  }
  if (ver === 2 && b.length === 16 + TAM_TABLA + 2048) {
    const carga = b.slice(16, 16 + TAM_TABLA), curva = b.slice(16 + TAM_TABLA);
    const buf = new Uint8Array(carga.length + curva.length);
    buf.set(carga); buf.set(curva, carga.length);
    return crc32(buf) === crc ? { tabla: carga, curva: b[5] ? curva : null } : null;
  }
  return null;
}

// ---------- previsualización (cadena de la cámara) ----------
/** 1064 B (21 bits/nodo) → 405 deltas s7 `[ΔY, ΔCb, ΔCr]`. */
export function tablaANodos(tabla) {
  const q = new Int8Array(405 * 3);
  for (let i = 0; i < 405; i++) {
    let w = 0;
    for (let k = 0; k < 21; k++) {
      const bit = i * 21 + k;
      if ((tabla[bit >> 3] >> (bit & 7)) & 1) w += 2 ** k;
    }
    const d = (v) => ((v & 127) ^ 64) - 64;      // 7 bits con signo, como `empaqueta_hw`
    q[3 * i] = d(w >> 14);
    q[3 * i + 1] = d(w >> 7);
    q[3 * i + 2] = d(w);
  }
  return q;
}

function pesos(y, cb, cr) {
  const gy = Math.min(Math.max(y, 0), 1) * (NY - 1);
  const gb = (Math.min(Math.max(cb, -0.5), 0.5) + 0.5) * (NC - 1);
  const gr = (Math.min(Math.max(cr, -0.5), 0.5) + 0.5) * (NC - 1);
  const g = [gy, gb, gr];
  const i0 = [0, 0, 0], f = [0, 0, 0];
  const dim = [NY, NC, NC];
  for (let k = 0; k < 3; k++) {
    i0[k] = Math.min(floor(g[k]), dim[k] - 2);
    f[k] = g[k] - i0[k];
  }
  const idx = [], w = [];
  for (let dy = 0; dy < 2; dy++)
    for (let db = 0; db < 2; db++)
      for (let dr = 0; dr < 2; dr++) {
        idx.push((i0[0] + dy) * 81 + (i0[1] + db) * 9 + i0[2] + dr);
        w.push((dy ? f[0] : 1 - f[0]) * (db ? f[1] : 1 - f[1]) * (dr ? f[2] : 1 - f[2]));
      }
  return { idx, w };
}

/** Un color sRGB (0…1) → el mismo color tras la cadena de la cámara con la tabla dada. */
export function aplicaColor(r, g, b, nodos) {
  const y = 0.299 * r + 0.587 * g + 0.114 * b;
  const cb = (b - y) / 1.772, cr = (r - y) / 1.402;
  const { idx, w } = pesos(y, cb, cr);
  let dy = 0, dcb = 0, dcr = 0;
  for (let k = 0; k < 8; k++) {
    dy += w[k] * nodos[3 * idx[k]];
    dcb += w[k] * nodos[3 * idx[k] + 1];
    dcr += w[k] * nodos[3 * idx[k] + 2];
  }
  const y2 = y + dy * UY, cb2 = cb + dcb * UC, cr2 = cr + dcr * UC;
  const r2 = y2 + 1.402 * cr2, b2 = y2 + 1.772 * cb2;
  return [r2, (y2 - 0.299 * r2 - 0.114 * b2) / 0.587, b2];
}

/** Aplica la tabla a un `ImageData` (sRGB) y devuelve otro `ImageData` con el resultado. */
export function aplicaImagen(imagen, nodos) {
  const src = imagen.data, out = new Uint8ClampedArray(src.length);
  for (let o = 0; o < src.length; o += 4) {
    const [r, g, b] = aplicaColor(src[o] / 255, src[o + 1] / 255, src[o + 2] / 255, nodos);
    out[o] = Math.round(Math.min(Math.max(r, 0), 1) * 255);
    out[o + 1] = Math.round(Math.min(Math.max(g, 0), 1) * 255);
    out[o + 2] = Math.round(Math.min(Math.max(b, 0), 1) * 255);
    out[o + 3] = src[o + 3];
  }
  return new ImageData(out, imagen.width, imagen.height);
}

/** Interpolación trilineal del `.cube` exacto (para comparar con la tabla de la cámara). */
export function aplicaCube(c, r, g, b) {
  const x = [r, g, b];
  const i0 = [0, 0, 0], f = [0, 0, 0];
  for (let k = 0; k < 3; k++) {
    const den = c.hi[k] - c.lo[k];
    let u = den > 0 ? ((x[k] * 65536 - c.lo[k]) / den) * (c.n - 1) : 0;   // dominio en Q16
    u = Math.min(Math.max(u, 0), c.n - 1);
    i0[k] = Math.min(Math.floor(u), c.n - 2);
    f[k] = u - i0[k];
  }
  const out = [0, 0, 0];
  for (let ch = 0; ch < 3; ch++) {
    let acc = 0;
    for (let d = 0; d < 8; d++) {
      const dr = d & 1, dg = (d >> 1) & 1, db = (d >> 2) & 1;
      const w = (dr ? f[0] : 1 - f[0]) * (dg ? f[1] : 1 - f[1]) * (db ? f[2] : 1 - f[2]);
      const idx = (((i0[2] + db) * c.n + i0[1] + dg) * c.n + i0[0] + dr) * 3 + ch;
      acc += w * c.cub[idx];
    }
    out[ch] = acc / 65536;
  }
  return out;
}

/** Un `.cube` (texto) → `{tabla, pkg, nodos, n, titulo}`. Lanza Error con el motivo si no vale. */
export function convierte(texto) {
  const c = parseCube(texto);
  const tabla = referencia(c);
  return { tabla, pkg: paquete(tabla), nodos: tablaANodos(tabla), n: c.n, titulo: c.titulo };
}
