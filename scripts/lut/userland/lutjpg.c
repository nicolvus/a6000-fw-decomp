/*
 * lutjpg — aplica un .cube 3D COMPLETO (cualquier LUT_3D_SIZE, p. ej. 33³ o 65³)
 * a un JPEG, en la propia cámara (Linux del A6000, Cortex-A5 sin NEON) o en el PC.
 *
 * El ISP del BIONZ X solo admite 5×9×9 (G90 §C); esto es la vía por software para
 * fotos: lee el JPEG de la SD (/android/mnt/sdcard, FUSE), interpola tetraédricamente
 * cada píxel y escribe un JPEG nuevo conservando los marcadores APP1 (EXIF) y el
 * submuestreo de croma. Proceso por filas: memoria ≈ LUT (N³·6 B) + unas filas.
 *
 * Uso: lutjpg [-q calidad] LUT.cube entrada.jpg salida.jpg
 * Compilación: scripts/lut/lutjpg.py (zig cc + libjpeg-turbo estática).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include <jpeglib.h>

typedef struct {
    int n;                 /* nodos por eje */
    float dmin[3], dmax[3];
    unsigned short *t;     /* n³·3 valores 0…65535, índice ((b·n+g)·n+r)·3 (orden .cube) */
} Lut;

static int lee_cube(const char *ruta, Lut *L)
{
    FILE *f = fopen(ruta, "r");
    char linea[512];
    long total = 0, k = 0;
    if (!f) return -1;
    L->n = 0; L->t = NULL;
    for (int c = 0; c < 3; c++) { L->dmin[c] = 0.f; L->dmax[c] = 1.f; }
    while (fgets(linea, sizeof linea, f)) {
        char *p = linea;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '#' || *p == '\r' || *p == '\n' || *p == 0) continue;
        if (!strncmp(p, "LUT_1D_SIZE", 11)) break;            /* 1D: no soportado */
        if (!strncmp(p, "LUT_3D_SIZE", 11)) {
            L->n = atoi(p + 11);
            if (L->n < 2 || L->n > 129) break;
            total = (long)L->n * L->n * L->n;
            L->t = malloc(total * 3 * sizeof *L->t);
            if (!L->t) break;
            continue;
        }
        if (!strncmp(p, "DOMAIN_MIN", 10)) { sscanf(p + 10, "%f %f %f", &L->dmin[0], &L->dmin[1], &L->dmin[2]); continue; }
        if (!strncmp(p, "DOMAIN_MAX", 10)) { sscanf(p + 10, "%f %f %f", &L->dmax[0], &L->dmax[1], &L->dmax[2]); continue; }
        if ((*p >= '0' && *p <= '9') || *p == '-' || *p == '+' || *p == '.') {
            float v[3];
            if (!L->t || k >= total || sscanf(p, "%f %f %f", &v[0], &v[1], &v[2]) != 3) { k = -1; break; }
            for (int c = 0; c < 3; c++) {
                float x = v[c] < 0.f ? 0.f : v[c] > 1.f ? 1.f : v[c];
                L->t[k * 3 + c] = (unsigned short)(x * 65535.f + .5f);
            }
            k++;
            continue;
        }
        /* TITLE y otras palabras clave: se ignoran */
    }
    fclose(f);
    if (!L->t || k != total) { free(L->t); L->t = NULL; return -1; }
    return 0;
}

/* Tabla por canal: valor de 8 bits → índice de celda y fracción Q16 (dominio aplicado). */
typedef struct { unsigned short i[256]; unsigned int f[256]; } Eje;

static void prepara_eje(const Lut *L, int c, Eje *e)
{
    float span = L->dmax[c] - L->dmin[c];
    for (int v = 0; v < 256; v++) {
        float x = span > 0.f ? (v / 255.f - L->dmin[c]) / span : 0.f;
        if (x < 0.f) x = 0.f;
        if (x > 1.f) x = 1.f;
        float p = x * (L->n - 1);
        int i = (int)p;
        if (i >= L->n - 1) i = L->n - 2;
        e->i[v] = (unsigned short)i;
        e->f[v] = (unsigned int)((p - i) * 65536.f + .5f);
    }
}

/* Interpolación tetraédrica (la habitual en .cube: Resolve, OCIO). */
static void aplica_fila(const Lut *L, const Eje E[3], JSAMPLE *px, JDIMENSION w)
{
    const int n = L->n, sr = 3, sg = 3 * n, sb = 3 * n * n;
    for (JDIMENSION x = 0; x < w; x++, px += 3) {
        unsigned int fr = E[0].f[px[0]], fg = E[1].f[px[1]], fb = E[2].f[px[2]];
        const unsigned short *b0 = L->t + E[0].i[px[0]] * sr + E[1].i[px[1]] * sg + E[2].i[px[2]] * sb;
        int o1, o2;                       /* desplazamientos de los dos vértices intermedios */
        unsigned int w0, w1, w2, w3;      /* pesos Q16 de c000, v1, v2, c111 */
        if (fr >= fg) {
            if (fg >= fb)      { o1 = sr;      o2 = sr + sg; w1 = fr - fg; w2 = fg - fb; w3 = fb; w0 = 65536 - fr; }
            else if (fr >= fb) { o1 = sr;      o2 = sr + sb; w1 = fr - fb; w2 = fb - fg; w3 = fg; w0 = 65536 - fr; }
            else               { o1 = sb;      o2 = sr + sb; w1 = fb - fr; w2 = fr - fg; w3 = fg; w0 = 65536 - fb; }
        } else {
            if (fb > fg)       { o1 = sb;      o2 = sg + sb; w1 = fb - fg; w2 = fg - fr; w3 = fr; w0 = 65536 - fb; }
            else if (fb > fr)  { o1 = sg;      o2 = sg + sb; w1 = fg - fb; w2 = fb - fr; w3 = fr; w0 = 65536 - fg; }
            else               { o1 = sg;      o2 = sr + sg; w1 = fg - fr; w2 = fr - fb; w3 = fb; w0 = 65536 - fg; }
        }
        const unsigned short *v1 = b0 + o1, *v2 = b0 + o2, *v3 = b0 + sr + sg + sb;
        for (int c = 0; c < 3; c++) {
            /* Σ peso·valor ≤ 65536·65535 < 2³²; salida de 16 a 8 bits con redondeo */
            unsigned int s = (w0 * b0[c] + w1 * v1[c] + w2 * v2[c] + w3 * v3[c] + 32768u) >> 16;
            px[c] = (JSAMPLE)((s * 255u + 32767u) / 65535u);
        }
    }
}

struct err { struct jpeg_error_mgr m; jmp_buf salto; };
static void sale(j_common_ptr ci) { (*ci->err->output_message)(ci); longjmp(((struct err *)ci->err)->salto, 1); }

int main(int argc, char **argv)
{
    int q = 98, a = 1;
    if (argc > 2 && !strcmp(argv[1], "-q")) { q = atoi(argv[2]); a = 3; }
    if (argc - a != 3 || q < 1 || q > 100) {
        fprintf(stderr, "uso: lutjpg [-q 1-100] LUT.cube entrada.jpg salida.jpg\n");
        return 2;
    }
    Lut L;
    if (lee_cube(argv[a], &L)) { fprintf(stderr, "lutjpg: .cube 3D no válido: %s\n", argv[a]); return 3; }
    Eje E[3];
    for (int c = 0; c < 3; c++) prepara_eje(&L, c, &E[c]);

    FILE *fi = fopen(argv[a + 1], "rb");
    FILE *volatile fo = NULL;   /* se modifica tras setjmp */
    if (!fi) { perror(argv[a + 1]); return 4; }
    if (!strcmp(argv[a + 1], argv[a + 2])) { fprintf(stderr, "lutjpg: la salida no puede ser la entrada\n"); return 2; }

    struct jpeg_decompress_struct di;
    struct jpeg_compress_struct co;
    struct err ed, ec;
    JSAMPARRAY fila = NULL;
    di.err = jpeg_std_error(&ed.m); ed.m.error_exit = sale;
    co.err = jpeg_std_error(&ec.m); ec.m.error_exit = sale;
    if (setjmp(ed.salto) || setjmp(ec.salto)) {
        jpeg_destroy_decompress(&di); jpeg_destroy_compress(&co);
        if (fo) { fclose(fo); remove(argv[a + 2]); }   /* nunca dejar un JPEG a medias */
        fclose(fi); free(L.t);
        return 5;
    }
    jpeg_create_decompress(&di);
    jpeg_create_compress(&co);
    jpeg_stdio_src(&di, fi);
    for (int m = 1; m < 16; m++) jpeg_save_markers(&di, JPEG_APP0 + m, 0xffff);  /* EXIF, MPF… */
    jpeg_read_header(&di, TRUE);
    di.out_color_space = JCS_RGB;
    jpeg_start_decompress(&di);

    fo = fopen(argv[a + 2], "wb");
    if (!fo) { perror(argv[a + 2]); longjmp(ed.salto, 1); }
    jpeg_stdio_dest(&co, fo);
    co.image_width = di.output_width;
    co.image_height = di.output_height;
    co.input_components = 3;
    co.in_color_space = JCS_RGB;
    jpeg_set_defaults(&co);
    jpeg_set_quality(&co, q, TRUE);
    co.write_JFIF_header = di.saw_JFIF_marker;   /* los JPEG de Sony llevan solo EXIF */
    if (di.jpeg_color_space == JCS_YCbCr && di.num_components == 3)
        for (int c = 0; c < 3; c++) {
            co.comp_info[c].h_samp_factor = di.comp_info[c].h_samp_factor;
            co.comp_info[c].v_samp_factor = di.comp_info[c].v_samp_factor;
        }
    jpeg_start_compress(&co, TRUE);
    /* APP2 «MPF» apunta a imágenes añadidas tras el EOI que no se copian: se omite */
    for (jpeg_saved_marker_ptr mk = di.marker_list; mk; mk = mk->next)
        if (!(mk->marker == JPEG_APP0 + 2 && mk->data_length >= 4 && !memcmp(mk->data, "MPF", 4)))
            jpeg_write_marker(&co, mk->marker, mk->data, mk->data_length);

    fila = (*di.mem->alloc_sarray)((j_common_ptr)&di, JPOOL_IMAGE, di.output_width * 3, 1);
    while (di.output_scanline < di.output_height) {
        jpeg_read_scanlines(&di, fila, 1);
        aplica_fila(&L, E, fila[0], di.output_width);
        jpeg_write_scanlines(&co, fila, 1);
    }
    jpeg_finish_compress(&co);
    jpeg_finish_decompress(&di);
    jpeg_destroy_compress(&co);
    jpeg_destroy_decompress(&di);
    fclose(fi);
    if (fclose(fo)) { perror(argv[a + 2]); remove(argv[a + 2]); free(L.t); return 6; }
    free(L.t);
    return 0;
}
