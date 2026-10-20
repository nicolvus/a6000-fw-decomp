/* S46: transcripción manual del listado Thumb temporal; no función creada
 * ni pseudocódigo inventado por el decompilador. Ver JSON de listados. */

/* 0x436c6f74 -> 0x436c7950, BL 0x436c7964 -> 0x43acee66.
 * 0x436c71f8 contiene literalmente 0xf3120000. */
void s46_vd_base_initialization(void) {
    /* str r1,[r0] en 0x43acee66; r0 = owner + 0xe10 + 4. */
    *(unsigned int *)0x43e16d2c = 0xf3120000;
}

/* 0x437dad78: r0=contexto; r1=destino C en VD_Pre.
 * La tabla 0x43ff8adc={0xce,0x43ff7414,1} contiene 0x437dad79.
 * Las lecturas u16 son little endian; no son etiquetas eléctricas. */
unsigned int s46_command_ce(unsigned int *context, unsigned char *destination) {
    unsigned int command = context[0x14];
    unsigned char *payload = *(unsigned char **)(command + 8);
    unsigned short *saved = (unsigned short *)0x43f7bbf4;
    memcpy(saved, payload, 4); /* 0x437dad88 */
    if (saved[0] != 0) {
        destination[0x94] = 1; /* 0x437dad92 */
        destination[0x95] = (unsigned char)saved[1]; /* 0x437dad9e */
    } else {
        destination[0x94] = 0; /* 0x437dad9a */
        destination[0x95] = 0; /* 0x437dad9e */
    }
    return 2;
}
