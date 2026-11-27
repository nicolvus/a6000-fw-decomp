"""La vista no debe abrirse antes de que estén listos gestor y eventos."""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(not shutil.which("cc"), reason="falta compilador C")
def test_arranque_espera_gestor_y_eventos(tmp_path):
    src = (ROOT / "scripts/gui/harness/shim/sonyshim.c").read_text()
    function = src[src.index("static void *openviewer"):src.index("static void *injector")]
    harness = r'''
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>
static void *lobj_h, *manager;
static void *manager_fields[8];
static int ticks, opens, events, never;
static int view(const char *name, int arg) { (void)name; (void)arg; opens++; return 0; }
static void *lookup(void *h, const char *name) {
    (void)h;
    if (strstr(name, "openView")) return (void *)view;
    if (!strcmp(name, "pViewManager")) return &manager;
    if (strstr(name, "EventC1") || strstr(name, "pushEvent")) return ticks >= 9 ? (void *)view : 0;
    return 0;
}
static int tick(useconds_t us) {
    (void)us; ticks++;
    if (ticks == 3) lobj_h = (void *)1;
    if (ticks == 6 && !never) { manager_fields[3] = (void *)1; manager = manager_fields; }
    return 0;
}
#define dlsym lookup
#define usleep tick
#define efp(...) ((void)0)
static void espera_calma(unsigned n, const char *v) { (void)n; (void)v; }
static unsigned long hexv(const char *s, const char **end) { return strtoul(s, (char **)end, 16); }
static int num(const char *s) { return atoi(s); }
static void acquire_status(int n) { (void)n; }
static void model_create(const char *s) { (void)s; }
static void startev(const char *s) { (void)s; if (manager && ticks >= 9) events++; }
'''
    main = r'''
int main(int argc, char **argv) {
    (void)argc; int mode = atoi(argv[1]); never = mode == 1;
    setenv("OPENVIEW", "view/ROOT", 1);
    setenv(mode == 2 ? "POSTROOTEV" : "STARTEV", "11004002", 1);
    openviewer(0);
    if (never) return opens != 0 || events != 0 || ticks > 3100;
    return opens != 1 || events != 1;
}
'''
    path = tmp_path / "test.c"
    path.write_text(harness + function + main)
    exe = tmp_path / "test"
    subprocess.run(["cc", "-std=gnu11", str(path), "-o", str(exe)], check=True, capture_output=True)
    for mode in ("0", "1", "2"):
        subprocess.run([str(exe), mode], check=True)
