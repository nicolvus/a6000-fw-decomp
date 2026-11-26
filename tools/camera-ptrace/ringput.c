/* ringput — deposita una línea en el anillo del monitor EX-PC de la A6000 sin ptrace ni dd:
 * mmap(/dev/mem, 0x8000, 0x82df9000) y escribe en buf[B..] avanzando B (cabecera [X]=A, [X+4]=B).
 * uso: ringput FISICA "texto"      (la física del anillo es el offset del mapeo /dev/mem)
 * Salida: "A=x B=y n=z" antes y después.
 */
typedef unsigned long ulong;
static long sc4(long n,long a,long b,long c,long d){
  register long r7 __asm__("r7")=n; register long r0 __asm__("r0")=a;
  register long r1 __asm__("r1")=b; register long r2 __asm__("r2")=c; register long r3 __asm__("r3")=d;
  __asm__ volatile("svc 0":"+r"(r0):"r"(r7),"r"(r1),"r"(r2),"r"(r3):"memory"); return r0;
}
static long sc6(long n,long a,long b,long c,long d,long e,long f){
  register long r7 __asm__("r7")=n; register long r0 __asm__("r0")=a;
  register long r1 __asm__("r1")=b; register long r2 __asm__("r2")=c; register long r3 __asm__("r3")=d;
  register long r4 __asm__("r4")=e; register long r5 __asm__("r5")=f;
  __asm__ volatile("svc 0":"+r"(r0):"r"(r7),"r"(r1),"r"(r2),"r"(r3),"r"(r4),"r"(r5):"memory");
  return r0;
}
static long s2(long n,long a,long b){return sc4(n,a,b,0,0);}
static long s4(long n,long a,long b,long c,long d){return sc4(n,a,b,c,d);}
#define SYS_write 4
#define SYS_open 5
#define SYS_mmap2 192
#define PROT_RW 3
#define MAP_SHARED 1
static char b[400], *P;
static char *ps(char*p,const char*s){while(*s)*p++=*s++;return p;}
static char *hx(char*p,ulong v){char t[16];int i=0;*p++='0';*p++='x';if(!v){*p++='0';return p;}
 while(v){t[i++]="0123456789abcdef"[v&15];v>>=4;}while(i)*p++=t[--i];return p;}
static char *it(char*p,long v){char t[12];int i=0;if(v<0){*p++='-';v=-v;}if(!v){*p++='0';return p;}
 while(v){t[i++]=(char)('0'+v%10);v/=10;}while(i)*p++=t[--i];return p;}
static void out(void){s4(SYS_write,1,(long)b,(long)(P-b),0);}
static ulong ph(const char*s){ulong v=0;if(s[0]=='0'&&(s[1]=='x'||s[1]=='X'))s+=2;
 for(;;){char c=*s;if(c>='0'&&c<='9')v=(v<<4)|(ulong)(c-'0');else if(c>='a'&&c<='f')v=(v<<4)|(ulong)(c-'a'+10);
 else break;s++;}return v;}
__attribute__((used)) static int main_c(long *sp){
  long argc=sp[0]; char **av=(char**)(sp+1); ulong fis; char *txt; long fd; ulong *ring; ulong A,B,n;
  int i; char cr=0x0d;
  if(argc<3){P=ps(b,"uso: ringput FISICA texto\n");out();return 2;}
  fis=(ulong)ph(av[1]); txt=av[2];
  fd=s4(SYS_open,(long)"/dev/mem",2,0,0);           /* O_RDWR */
  if(fd<0){P=ps(b,"open /dev/mem falló ");P=it(P,fd);*P++='\n';out();return 1;}
  { long r=sc6(SYS_mmap2,0,0x8000L,PROT_RW,MAP_SHARED,fd,(long)(fis>>12));
    if((ulong)r>0xfffff000UL){P=ps(b,"mmap falló ");P=hx(P,(ulong)(-r));*P++='\n';out();return 1;}
    ring=(ulong*)r; }
  A=ring[0]; B=ring[1];
  P=ps(b,"A=");P=it(P,(long)A);P=ps(P," B=");P=it(P,(long)B);
  for(n=0;txt[n];n++){
    ((char*)(ring+4))[(B+n)&0x3ff]=txt[n];
  }
  ((char*)(ring+4))[(B+n)&0x3ff]=cr; n++;
  B=(B+n)&0x3ff; ring[1]=B;
  P=ps(P," -> B=");P=it(P,(long)B);*P++='\n';out();
  for(i=0;i<0;i++){}
  return 0;
}
__attribute__((naked)) void _start(void){__asm__ volatile("mov r0, sp\n bl main_c\n mov r7, #1\n svc 0");}
