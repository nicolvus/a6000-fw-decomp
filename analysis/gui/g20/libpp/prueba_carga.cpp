extern "C" long write(int, const void*, unsigned long);
struct A { virtual int f() { return 7; } virtual ~A() {} };
struct B : A { int f() override { return 42; } };
static B b;
__attribute__((constructor)) static void hola() { A* a = &b; char m[] = "libpp: init f=__\n"; int v = a->f(); m[14] = '0' + v / 10; m[15] = '0' + v % 10; write(2, m, sizeof m - 1); }
extern "C" void __cxa_pure_virtual() {}
void operator delete(void*) {}
