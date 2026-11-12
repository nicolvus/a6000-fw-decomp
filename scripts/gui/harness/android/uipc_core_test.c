// Prueba en el anfitrión de uipc_core.c: dos «procesos» con bases distintas comparten mensajes, callbacks y semáforos.
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "uipc_core.h"

int main(void)
{
	static struct uc u; uint8_t *shm = calloc(1, UC_SHM); uint32_t o[4], m, r; struct uc_cb cb;
	uc_init(&u, shm);
	int a = uc_connect(&u, 0x40000000, o), b = uc_connect(&u, 0x50000000, o);
	assert(a == 0 && b == 1 && o[0] == 0x80000 && o[1] == 0x20000 && o[2] == 0x8000 && (o[3] >> 16) == 0x3f && shm[0x10] == 8);

	/* buzón: A envía, B recibe el mismo cuerpo con su propia base */
	assert(uc_valloc(&u, a, 0x10, 16, &m) == 0 && m >= 0x40000000 && m < 0x40080000);
	memcpy(shm + (m - 0x40000000), "hola", 5);
	assert(uc_rcv(&u, b, 0x3e014d, &r) == UC_AGAIN);
	assert(uc_snd(&u, a, 0x3e014d, m) == 0 && uc_rcv(&u, b, 0x3e014d, &r) == 0);
	assert(r - 0x50000000 == m - 0x40000000 && !strcmp((char *)shm + (r - 0x50000000), "hola"));
	assert(uc_snd(&u, a, 0x3e014d, 0x50000000) == UC_INVAL);   /* puntero fuera de la ventana de A */
	assert(uc_free(&u, b, r) == 0);

	/* callback: B registra la cola; lo enviado antes y después llega a su wait_cb */
	assert(uc_valloc(&u, a, 0, 8, &m) == 0 && uc_snd(&u, a, 0x910041, m) == 0);
	assert(uc_reg_cb(&u, b, 0x910041, 0x1234, 0x5679, 1) == 0);
	assert(uc_wait_cb(&u, b, &cb) == 0 && cb.cb == 0x5679 && cb.arg == 0x1234 && cb.msg - 0x50000000 == m - 0x40000000);
	assert(uc_wait_cb(&u, a, &cb) == UC_AGAIN && uc_wait_cb(&u, b, &cb) == UC_AGAIN);
	assert(uc_unreg_cb(&u, 0x910041) == 0 && uc_snd(&u, a, 0x910041, m) == 0 && uc_rcv(&u, a, 0x910041, &r) == 0 && r == m);

	/* semáforos e ids dinámicos */
	uint32_t s; assert(uc_dynamic_id(&u, UC_DYN_SEM, 0x12, &s) == 0 && (s >> 16) == 0x12 && (s & 0x8000));
	assert(uc_wai_sem(&u, s) == UC_AGAIN && uc_sig_sem(&u, s) == 0 && uc_wai_sem(&u, s) == 0 && uc_wai_sem(&u, s) == UC_AGAIN);
	assert(uc_dynamic_id(&u, 7, 0, &s) == UC_INVAL);
	assert(uc_valloc(&u, a, 0, 0x1000, &m) == UC_INVAL);
	puts("uipc_core OK");
	return 0;
}
