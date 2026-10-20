/* Programa de laboratorio propio: simula una coordinación de captura (no es código Sony). */
#include <stdio.h>
#include <unistd.h>
__attribute__((noinline)) int expose(int shutter_us, int iso) { return shutter_us * iso / 100; }
__attribute__((noinline)) int capture(int mode) { return expose(mode ? 250 : 4000, 200) + 1; }
int main(void) {
  for (int i = 0; i < 6; i++) { printf("capture(%d)=%d\n", i % 2, capture(i % 2)); fflush(stdout); usleep(300000); }
  return 0;
}
