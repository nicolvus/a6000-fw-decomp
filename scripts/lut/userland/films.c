/* G97 — simulaciones de película en la cámara, userland (se inyecta en `viewUnified2.so`, proceso de `libObj`; mismo arranque por `DT_INIT` que G89).
 * Los 38 looks (LUT 5×9×9 empaquetada a 21 bits + curva 1D de 1024 u16 tras la gamma) van como datos de solo lectura en este mismo segmento (`films_datos.h`,
 * generado por `film_userland.py`). El menú «Film» tiene NFILAS filas (ajustes CFW de 1 B en el Backup, ≤ 7 opciones: Off + looks). Cada SONDEO_US el hilo lee las
 * filas; manda la última fila que cambió a un look (si se pone en Off, la primera fila que siga con look). Al cambiar el look activo escribe en el id de Backup
 * `BK_ID` (16 KB) el blob «FILM» con su tabla y su curva, y después el id de 1 B `ACK_ID` = nº del look (0 = Off): `av-cam` solo vigila ese byte.
 * La primera vez (blob sin magia «FILM», p. ej. tras otro CFW) pone a 0 las filas y el ACK: esos ids pueden traer valores de ajustes anteriores.
 * Sin libc ni datos globales escribibles (clang -fropi): el estado va en `struct ctx` (malloc); las funciones llegan por `dlsym`.
 * Contratos (g89 §2): Backup_read(id, buf) · Backup_write(id>>16, id, buf). */
typedef unsigned int u32;
typedef int i32;
typedef unsigned short u16;
typedef unsigned char u8;

#include "films_datos.h" /* NLOOKS, NFILAS, FILA_ID[], FILA_BASE[], FILA_N[], ACK_ID, LOOK_LUT[][1064], LOOK_T[][1024], LOOK_USA_T[] */

#define BK_TAM 16384
#define BK_ID 0x150005u
#define MAGIC 0x4D4C4946u /* "FILM" */
#define TAM_TABLA 1064
#define OFF_T 0x1000
#define SONDEO_US 300000u
#define VERIFICA 10

struct api {
    i32 (*b_read)(u32, void *);
    i32 (*b_write)(u32, u32, const void *);
    void *(*m_alloc)(u32);
    i32 (*s_usleep)(u32);
};

struct ctx {
    struct api a;
    u8 blob[BK_TAM];
    u8 tmp[BK_TAM];
    u8 celda[NFILAS];
    i32 activo, escrito, vueltas;
};

void *memset(void *p, int v, u32 n) {
    u8 *q = p;
    while (n--) *q++ = (u8)v;
    return p;
}

void *memcpy(void *d, const void *s, u32 n) {
    u8 *q = d;
    const u8 *r = s;
    while (n--) *q++ = *r++;
    return d;
}

/* Valor de una fila (índice de opción; fuera de rango = 0 = Off). */
static i32 fila(struct ctx *c, i32 r) {
    u8 b[8] = {0};
    if (c->a.b_read(FILA_ID[r], b) < 0) return 0;
    return b[0] < FILA_N[r] ? b[0] : 0;
}

static i32 lee_ack(struct ctx *c) {
    u8 b[8] = {0};
    if (c->a.b_read(ACK_ID, b) < 0) return 0;
    return b[0] <= NLOOKS ? b[0] : 0;
}

static void escribe_byte(struct ctx *c, u32 id, i32 v) {
    u8 b[8] = {0};
    b[0] = (u8)v;
    c->a.b_write(id >> 16, id, b);
}

/* 1 si el Backup ya guarda exactamente c->blob. */
static i32 blob_igual(struct ctx *c) {
    if (c->a.b_read(BK_ID, c->tmp) < 0) return 0;
    for (i32 i = 0; i < BK_TAM; i++)
        if (c->blob[i] != c->tmp[i]) return 0;
    return 1;
}

/* Fila y opción de un look (1…NLOOKS) → fila r con FILA_BASE[r] < look ≤ FILA_BASE[r] + FILA_N[r] − 1. */
static i32 fila_de(i32 look) {
    for (i32 r = 0; r < NFILAS; r++)
        if (look > FILA_BASE[r] && look < FILA_BASE[r] + FILA_N[r]) return r;
    return -1;
}

/* Blob del look `n` (0 = Off): cabecera + tabla en la ranura 0 + curva. Escribe el Backup solo si cambia y lo relee: el ACK (lo único que vigila
 * `av-cam`) solo se escribe cuando el blob ya está entero en el Backup; si no, `escrito` queda sin cambiar y el siguiente sondeo lo reintenta. */
i32 films_escribe(struct ctx *c, i32 n) {
    memset(c->blob, 0, BK_TAM);
    *(u32 *)c->blob = MAGIC;
    c->blob[4] = 1;
    c->blob[5] = (u8)n;
    c->blob[6] = NLOOKS;
    if (n > 0) {
        memcpy(c->blob + 16, LOOK_LUT[n - 1], TAM_TABLA);
        c->blob[8] = 1;
        if (LOOK_USA_T[n - 1]) {
            memcpy(c->blob + OFF_T, LOOK_T[n - 1], 2048);
            c->blob[9] = 1;
        }
    }
    i32 igual = blob_igual(c);
    if (!igual) {
        c->a.b_write(BK_ID >> 16, BK_ID, c->blob);
        if (!blob_igual(c)) return 0;
    }
    if (lee_ack(c) != n) escribe_byte(c, ACK_ID, n);
    if (lee_ack(c) != n) return 0;
    c->escrito = n;
    return !igual;
}

/* Arranque: primera vez sin blob «FILM» → filas y ACK a 0; si no, el look activo es el ACK si su fila lo sigue mostrando (si no, la primera fila con look). */
void films_inicio(struct ctx *c) {
    i32 primera = c->a.b_read(BK_ID, c->tmp) < 0 || *(u32 *)c->tmp != MAGIC;
    c->activo = 0;
    for (i32 r = 0; r < NFILAS; r++) {
        if (primera && fila(c, r)) escribe_byte(c, FILA_ID[r], 0);
        c->celda[r] = (u8)(primera ? 0 : fila(c, r));
    }
    if (!primera) {
        i32 k = lee_ack(c), r = fila_de(k);
        if (k && r >= 0 && c->celda[r] == k - FILA_BASE[r]) c->activo = k;
        for (r = 0; r < NFILAS && !c->activo; r++)
            if (c->celda[r]) c->activo = FILA_BASE[r] + c->celda[r];
    }
    films_escribe(c, c->activo);
}

/* Un sondeo: devuelve 1 si cambió el look activo (y se escribió). */
i32 films_paso(struct ctx *c) {
    for (i32 r = 0; r < NFILAS; r++) {
        i32 v = fila(c, r);
        if (v == c->celda[r]) continue;
        c->celda[r] = (u8)v;
        if (v) c->activo = FILA_BASE[r] + v;
        else if (fila_de(c->activo) == r) {
            c->activo = 0;
            for (i32 s = 0; s < NFILAS && !c->activo; s++)
                if (c->celda[s]) c->activo = FILA_BASE[s] + c->celda[s];
        }
    }
    if (++c->vueltas >= VERIFICA) {             /* cada ~3 s: el Backup sigue con el blob y el ACK del look activo (si no, se reescriben) */
        c->vueltas = 0;
        c->escrito = -1;
    }
    if (c->activo == c->escrito) return 0;
    films_escribe(c, c->activo);
    return 1;
}

/* Entrada del hilo (pthread_create(&t, 0, films_hilo, dlsym)). */
typedef void *(*dlsym_t)(void *, const char *);
void *films_hilo(dlsym_t dl) {
    struct ctx *c;
    void *(*ma)(u32) = dl(0, "malloc");
    void *(*h)(const char *, i32) = dl(0, "dlopen");
    void *bk;
    if (!ma || !h) return 0;
    bk = h("libbackup.so", 1);
    if (!bk) return 0;
    c = ma(sizeof *c);
    if (!c) return 0;
    memset(c, 0, sizeof *c);
    c->a.m_alloc = ma;
    c->a.s_usleep = dl(0, "usleep");
    c->a.b_read = dl(bk, "Backup_read");
    c->a.b_write = dl(bk, "Backup_write");
    if (!c->a.s_usleep || !c->a.b_read || !c->a.b_write) return 0;
    films_inicio(c);
    for (;;) {
        films_paso(c);
        c->a.s_usleep(SONDEO_US);
    }
}
