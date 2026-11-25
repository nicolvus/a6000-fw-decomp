/* G97 — simulaciones de película en la cámara, userland (se inyecta en `viewUnified2.so`, proceso de `libObj`; mismo arranque por `DT_INIT` que G89).
 * Los 38 looks (LUT 5×9×9 empaquetada a 21 bits + curva 1D de 1024 u16 tras la gamma) van como datos de solo lectura en este mismo segmento (`films_datos.h`,
 * generado por `film_userland.py`). El menú «Film» tiene NFILAS filas (ajustes CFW de 1 B en el Backup, ≤ 7 opciones: Off + looks). Cada SONDEO_US el hilo lee las
 * filas (+ la lista única del menú Fn, G100); manda la última fila que cambió y las demás se sincronizan con ese look (Off en ella = Off). Al cambiar el look activo escribe en el id de Backup
 * `BK_ID` (16 KB) el blob «FILM» con su tabla y su curva, y después el id de 1 B `ACK_ID` = nº del look (0 = Off): `av-cam` solo vigila ese byte.
 * La primera vez (blob sin magia «FILM», p. ej. tras otro CFW) pone a 0 las filas y el ACK: esos ids pueden traer valores de ajustes anteriores.
 * Sin libc ni datos globales escribibles (clang -fropi): el estado va en `struct ctx` (malloc); las funciones llegan por `dlsym`.
 * G110: la receta nativa de cada look (balance AWB/K + A-B/G-M, estilo + contraste/saturación/nitidez, DRO, PP Off) NO la escribe este hilo: el Backup solo
 * guarda y `libObj` no se entera. La aplica `films_antes`, que corre en el hilo de la GUI (gancho de `CmnViewProcessDataMgr::setValue`) con los mismos
 * setters que el menú; la copia de los ajustes del usuario va en el blob (`OFF_REC`, `struct copia`), que este hilo conserva al reescribirlo.
 * `films_gris` (gancho de `isGrayedOut`) pone en gris lo que el look fija o anula, y Film mientras haya un PP.
 * Contratos (g89 §2): Backup_read(id, buf) · Backup_write(id>>16, id, buf). */
typedef unsigned int u32;
typedef int i32;
typedef unsigned short u16;
typedef short i16;
typedef unsigned char u8;

#include "films_datos.h" /* NLOOKS, NFILAS, FILA_ID[], FILA_PID[], FILA_BASE[], FILA_N[], ACK_ID, LOOK_LUT, LOOK_T, LOOK_USA_T, RECETA_GUI, PID_PP_*, OFF_REC */

#define BK_TAM 16384
#define BK_ID 0x150005u
#define MAGIC 0x4D4C4946u /* "FILM" */
#define TAM_TABLA 1064
#define OFF_T 0x1000
#define SONDEO_US 300000u
#define VERIFICA 10
#define NCAT (NFILAS - 1) /* G100: la última fila es la lista única del menú Fn (Off + los 38, base 0) */

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

/* Copia de los ajustes del usuario antes del primer look (blob + OFF_REC; valores en el dominio de los wrappers de la GUI). */
struct copia {
    i32 hay;
    i32 wb[4];      /* modo, K, A-B, G-M (WrapperWhiteBalance) */
    i32 cs[4];      /* código de estilo del Backup, contraste, saturación, nitidez */
    i32 dro;        /* WRAPPER_DRO_HDR */
    i32 pp;         /* índice del selector PP (0 = Off) */
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
    for (i32 r = 0; r < NCAT; r++)
        if (look > FILA_BASE[r] && look < FILA_BASE[r] + FILA_N[r]) return r;
    return -1;
}

/* Blob del look `n` (0 = Off): cabecera + tabla en la ranura 0 + curva. Escribe el Backup solo si cambia y lo relee: el ACK (lo único que vigila
 * `av-cam`) solo se escribe cuando el blob ya está entero en el Backup; si no, `escrito` queda sin cambiar y el siguiente sondeo lo reintenta. */
i32 films_escribe(struct ctx *c, i32 n) {
    memset(c->blob, 0, BK_TAM);
    if (c->a.b_read(BK_ID, c->tmp) >= 0)                 /* la copia del usuario la escribe la GUI (films_antes): se conserva */
        memcpy(c->blob + OFF_REC, c->tmp + OFF_REC, sizeof(struct copia));
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

/* Un solo look activo: lo muestran su fila de categoría y la lista única; las demás filas quedan en Off. */
static void sincroniza(struct ctx *c) {
    i32 rc = fila_de(c->activo);
    for (i32 r = 0; r < NFILAS; r++) {
        i32 v = r == NCAT ? c->activo : r == rc ? c->activo - FILA_BASE[r] : 0;
        if (fila(c, r) != v) escribe_byte(c, FILA_ID[r], v);
        c->celda[r] = (u8)v;
    }
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
        for (r = 0; r < NCAT && !c->activo; r++)
            if (c->celda[r]) c->activo = FILA_BASE[r] + c->celda[r];
    }
    sincroniza(c);
    films_escribe(c, c->activo);
}

/* Un sondeo: manda la última fila que cambió (Off en ella = Off) y las demás se sincronizan; devuelve 1 si se escribió el look. */
i32 films_paso(struct ctx *c) {
    i32 cambio = 0;
    for (i32 r = 0; r < NFILAS; r++) {
        i32 v = fila(c, r);
        if (v == c->celda[r]) continue;
        c->celda[r] = (u8)v;
        c->activo = v ? FILA_BASE[r] + v : 0;
        cambio = 1;
    }
    if (cambio) sincroniza(c);
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

/* ---------- G110: hilo de la GUI (ganchos de vu2; ver film_gui_vu2.py) ----------
 * Funciones de vu2 por dirección (símbolos absolutos `--defsym`, enlazado en la VA real del segmento: con -fropi la dirección se calcula relativa al PC).
 * Thumb con el bit 0; los stubs PLT (ARM) sin él. */
extern const char V_GETVALUE[], V_SETVALUE[], V_WB_CTOR[], V_WB_GET[], V_WB_SET[], V_CS_CTOR[], V_CS_SET[], V_DRO_CTOR[], V_DRO_GET[],
    V_DRO_CONV[], P_DLOPEN[], P_DLSYM[], P_MALLOC[], P_FREE[];
/* Dirección opaca: obliga a llamar por registro (`blx`), que respeta el bit 0 (Thumb) y entra en ARM en los stubs PLT. */
static inline const void *dir(const char *p) {
    __asm__("" : "+r"(p));
    return p;
}
#define F(t, s) ((t)dir(s))
typedef i32 (*getv_t)(void *, i32, i32 *);
typedef i32 (*setv_t)(void *, i32, i32);
typedef void (*ctor_t)(void *);
typedef i32 (*wbget_t)(void *, void *, i32 *, i32 *, i32 *, i32 *, i32);
typedef i32 (*wbset_t)(void *, void *, i32, i32, i32, i32);
typedef i32 (*csset_t)(void *, void *, i32, i32, i32, i32, i32);
typedef i32 (*droget_t)(void *, void *, i32 *, i32);
typedef i32 (*droconv_t)(void *, i32, i32 *);
#define CS_ID_STYLE 0x1070175u /* código de estilo y ajustes actuales (los de RecipeLab) */
#define CS_ID_CON 0x1070178u
#define CS_ID_SAT 0x1070187u
#define CS_ID_SHA 0x107018Au
#define PID_WB 0x17
#define PID_DRO 0x18
#define PID_CS 0x19
#define PID_EFECTO 0x1A
#define WB_KELVIN 0xC
/* CAM-394/G111 §9: setWhiteBalance sale sin escribir si `WrapperWhiteBalance::isInhOn(modo)` (factor del modelo) dice inhibido; la receta lo salta solo
 * para su propio objeto, marcado con estas dos palabras. */
#define WB_MARCA0 0x4D4C4946u
#define WB_MARCA1 0x4E495742u

/* Código de estilo del Backup (1 Estándar … 13 Sepia, orden de RecipeLab) → WRAPPER_CREATIVE_STYLE (tablas por estilo de CustomCreativeStyle::setValue). */
static const u8 CS_ENUM[14] = {0, 1, 2, 11, 12, 13, 3, 4, 5, 6, 7, 8, 9, 10};

static i32 lee(void *mgr, i32 pid) {
    i32 v = 0;
    return F(getv_t, V_GETVALUE)(mgr, pid, &v) ? v : -1;
}

/* Look (0…NLOOKS) que deja `val` en la fila de pid `pid`; -1 si el pid no es de Film. */
static i32 look_de(i32 pid, i32 val) {
    for (i32 r = 0; r < NFILAS; r++)
        if (FILA_PID[r] == pid) return val > 0 && val < FILA_N[r] ? FILA_BASE[r] + val : 0;
    return -1;
}

static i32 lee_byte(i32 (*rd)(u32, void *), u32 id, u8 *buf) {
    return rd(id, buf) < 0 ? 0 : (i32)(signed char)buf[0];
}

static void pon(void *mgr, void *vbp, const i32 *wb, i32 cs_code, const i32 *cs, i32 dro, i32 pp) {
    u32 o[4];
    if (PID_PP_SEL != 0 && pp >= 0) F(setv_t, V_SETVALUE)(mgr, PID_PP_SEL, pp);         /* PP primero: el resto se aplica ya sin perfil */
    F(ctor_t, V_WB_CTOR)(o);
    o[2] = WB_MARCA0;                                    /* el objeto del wrapper es solo la vtable: la marca va detrás y `films_tramo_wbinh` la reconoce */
    o[3] = WB_MARCA1;
    F(wbset_t, V_WB_SET)(o, vbp, wb[0], wb[1], wb[2], wb[3]);
    o[2] = o[3] = 0;
    if (cs_code > 0 && cs_code < 14) {
        F(ctor_t, V_CS_CTOR)(o);
        F(csset_t, V_CS_SET)(o, vbp, CS_ENUM[cs_code], 0, cs[0], cs[1], cs[2]);
    }
    i32 v = 0;
    F(ctor_t, V_DRO_CTOR)(o);
    if (F(droconv_t, V_DRO_CONV)(o, dro, &v)) F(setv_t, V_SETVALUE)(mgr, PID_DRO, v);   /* sin setDroHdr: su isInhOn mira el gris de DRO */
}

/* Antes de que la GUI guarde un valor en una fila de Film: al pasar a un look guarda la copia del usuario (si no la hay) y pone la receta; al pasar a
 * Off devuelve la copia. Va antes del setValue original para que el hilo, que lee la fila después, encuentre ya la copia en el blob. */
void films_antes(void *mgr, i32 pid, i32 val) {
    i32 n = look_de(pid, val);
    if (n < 0) return;
    typedef void *(*dlopen_t)(const char *, i32);
    void *bk = F(dlopen_t, P_DLOPEN)("libbackup.so", 1);
    if (!bk) return;
    i32 (*rd)(u32, void *) = F(dlsym_t, P_DLSYM)(bk, "Backup_read");
    i32 (*wr)(u32, u32, const void *) = F(dlsym_t, P_DLSYM)(bk, "Backup_write");
    u8 *buf = F(void *(*)(u32), P_MALLOC)(BK_TAM);
    if (!rd || !wr || !buf) return;
    void *vbp = ((void **)mgr)[1];
    if (rd(BK_ID, buf) < 0) memset(buf, 0, BK_TAM);
    struct copia *k = (struct copia *)(buf + OFF_REC);
    u8 b8[16];
    u32 o[4];
    if (n) {
        if (k->hay != 1) {
            memset(k, 0, sizeof *k);
            F(ctor_t, V_WB_CTOR)(o);
            F(wbget_t, V_WB_GET)(o, vbp, &k->wb[0], &k->wb[1], &k->wb[2], &k->wb[3], 0);
            k->cs[0] = lee_byte(rd, CS_ID_STYLE, b8);
            k->cs[1] = lee_byte(rd, CS_ID_CON, b8);
            k->cs[2] = lee_byte(rd, CS_ID_SAT, b8);
            k->cs[3] = lee_byte(rd, CS_ID_SHA, b8);
            F(ctor_t, V_DRO_CTOR)(o);
            F(droget_t, V_DRO_GET)(o, vbp, &k->dro, 0);
            k->pp = PID_PP_SEL != 0 ? lee(mgr, PID_PP_SEL) : -1;
            k->hay = 1;
            wr(BK_ID >> 16, BK_ID, buf);
        }
        const i16 *r = RECETA_GUI[n - 1];
        i32 wb[4] = {r[0], r[1], r[2], r[3]}, cs[3] = {r[5], r[6], r[7]};
        pon(mgr, vbp, wb, r[4], cs, r[8], 0);
    } else if (k->hay == 1) {
        pon(mgr, vbp, k->wb, k->cs[0], k->cs + 1, k->dro, k->pp);
        k->hay = 0;
        wr(BK_ID >> 16, BK_ID, buf);
    }
    F(void (*)(void *), P_FREE)(buf);
}

/* isGrayedOut(pid): 1/0 decide; -1 = sigue la cadena original (gris de EFCS con Silent). */
i32 films_gris(void *mgr, i32 pid) {
    i32 film = PID_DRO <= pid && pid <= PID_EFECTO, pp = PID_PP_PRIMERO <= pid && pid <= PID_PP_ULTIMO;
    i32 wb = pid == PID_WB, fila = look_de(pid, 0) >= 0;
    if (!film && !pp && !wb && !fila) return -1;
    i32 n = lee(mgr, FILA_PID[NFILAS - 1]);
    if (n > 0 && n <= NLOOKS && (film || pp || (wb && RECETA_GUI[n - 1][0] == WB_KELVIN))) return 1;
    if (fila && PID_PP_SEL != 0 && lee(mgr, PID_PP_SEL) > 0) return 1;
    return -1;
}

/* Trampolines (Thumb). Los saltos a vu2 van por `bx` a una dirección relativa al PC (`.word destino - .`): el enlazador resuelve la resta con los
 * símbolos absolutos, válida sea cual sea la base de carga. `films_tramo_set` sustituye el prólogo de setValue (`push {r3,r4,r7,lr}; add r7,sp,#0`);
 * `films_tramo_gris` el de isGrayedOut (o el salto previo de pid_space, que pasa a ser V_GRIS_SIGUE). */
__asm__(".text\n.syntax unified\n.thumb\n"
        ".global films_tramo_set\n.type films_tramo_set,%function\n.thumb_func\nfilms_tramo_set:\n"
        "  push {r0, r1, r2, r3, r4, r5, r6, lr}\n"
        "  bl films_antes\n"
        "  ldm sp, {r0, r1, r2, r3}\n"
        "  bl films_orig_set\n"
        "  add sp, #16\n"
        "  pop {r4, r5, r6, pc}\n"
        ".thumb_func\nfilms_orig_set:\n"
        "  push {r3, r4, r7, lr}\n"
        "  add r7, sp, #0\n"
        "  ldr r12, 1f\n"
        "2: add r12, pc\n"
        "  bx r12\n"
        ".p2align 2\n1: .word V_SET_CONT - (2b + 4)\n"
        ".global films_tramo_gris\n.type films_tramo_gris,%function\n.thumb_func\nfilms_tramo_gris:\n"
        "  push {r0, r1, r2, lr}\n"
        "  bl films_gris\n"
        "  cmp r0, #0\n"
        "  blt 3f\n"
        "  add sp, #8\n"
        "  pop {r2, pc}\n"
        "3: pop {r0, r1, r2, lr}\n"
        "  ldr r12, 4f\n"
        "5: add r12, pc\n"
        "  bx r12\n"
        ".p2align 2\n4: .word V_GRIS_SIGUE - (5b + 4)\n"
        ".global films_orig_gris\n.type films_orig_gris,%function\n.thumb_func\nfilms_orig_gris:\n"
        "  push {r7, lr}\n"
        "  add r7, sp, #0\n"
        "  ldr r12, 6f\n"
        "7: add r12, pc\n"
        "  bx r12\n"
        ".p2align 2\n6: .word V_GRIS_CONT - (7b + 4)\n"
        /* `films_tramo_wbinh` sustituye el prólogo de WrapperWhiteBalance::isInhOn (`push {r4,r5,r7,lr}; mov r5,r0`): objeto marcado → 0 (no inhibido). */
        ".global films_tramo_wbinh\n.type films_tramo_wbinh,%function\n.thumb_func\nfilms_tramo_wbinh:\n"
        "  ldr r3, [r0, #8]\n"
        "  ldr r12, 8f\n"
        "  cmp r3, r12\n"
        "  bne 9f\n"
        "  ldr r3, [r0, #12]\n"
        "  ldr r12, 10f\n"
        "  cmp r3, r12\n"
        "  bne 9f\n"
        "  movs r0, #0\n"
        "  bx lr\n"
        "9: push {r4, r5, r7, lr}\n"
        "  mov r5, r0\n"
        "  ldr r12, 11f\n"
        "12: add r12, pc\n"
        "  bx r12\n"
        ".p2align 2\n8: .word 0x4D4C4946\n10: .word 0x4E495742\n11: .word V_WBINH_CONT - (12b + 4)\n");
