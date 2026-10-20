"""S60: genera analysis/s60-evidence-matrix.json (cada entrada indica quién ejecutó la prueba y si Claude la verificó de forma independiente)."""
import json
from pathlib import Path
R = Path(__file__).resolve().parents[2]
A6, A7 = 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9', 'b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e'
C, G = 'Claude Sonnet 5.5', 'GPT-6 Sol'
TC, TS = 'tests/test_s60_claude.py', 'tests/test_s60_sol.py'
def e(id, by, model, claim, address, status, method, test, limits, indep=None):
    return dict(id=id, executed_by=by, model=model, sha256=A6 if model == 'A6000' else A7, claim=claim, address=address, status=status,
                validation_method=method, test=test, limitations=limits, independently_verified_by_claude=indep)
entries = [
 e('S60-C1', C, 'A7S', '0x438f6864(unit,id,a,b) es una API de trazas de todo el firmware (381 llamadores); 0x1000/0x1001 son 2; registro tipo 2/clase 3/carga 12 B a la cola 0x8f013a, no bloqueante', '0x438f6864, 0x43ada07a, 0x43ada0b4', 'VERIFICADO', 'Capstone + Unicorn con OSAL sustituido (alloc/send)', f'{TC}::TraceRecord', 'OSAL es un stub del arnés: no prueba el consumidor real'),
 e('S60-C2', C, 'A7S', 'El retorno del envío se descarta (0x436f5baa sobrescribe r0); fallo de envío → marcador tipo 0xf en 0x8f0313; el emisor no espera ni sincroniza', '0x436f5b98..0x436f5bb2, 0x438f68c8..0x438f68fe', 'VERIFICADO', 'bytes + Unicorn (send_rc=1)', f'{TC}::TraceRecord, NoReceiver', 'No excluye que otro actor lea la cola y actúe'),
 e('S60-C3', C, 'A7S', '0x1000 = eco de SetExposure (svd<<16|shd, spl<<24); 0x1001 = eco de SetRead (ganancia); cada parámetro cambia el mensaje', '0x436f5b98..0x436f5bb2', 'VERIFICADO', 'ctor real + escenarios modo 0x0b', f'{TC}::MessageContent', 'Empaquetado exacto de bits de 0x1001 no desglosado'),
 e('S60-C4', C, 'A7S', 'Los literales de handle 0x8f013a/0x8f0313/0x8f0139 aparecen solo en emisores (87+ con idéntico patrón) y no hay receptor por literal; consumidor NO localizado en la imagen', 'barrido completo av-cam.bin', 'PARCIAL', 'barrido Capstone de literales, movw/movt y envoltorios OSAL', f'{TC}::NoReceiver', 'Una búsqueda vacía no prueba ausencia; el drenaje puede usar handles construidos en tiempo de ejecución'),
 e('S60-C5', C, 'A7S', '0x439b3918 = memcpy ARM (3993 llamadores); 0x438f7114 = printf de trazas (4230 llamadores); 0x43544270 = decodificador de estado→campos de sombra (3er método, único llamador 0x43ada4be)', '0x439b3918, 0x438f7114, 0x43544270', 'VERIFICADO / PARCIAL (0x43544270)', 'Capstone, barrido de llamadores', f'{TC}', 'Efecto eléctrico de 0x43544270 no demostrado'),
 e('S60-C6', C, 'A7S', 'Silent (0x4c..0x4f) no emite 0x1000/0x1001; la diferencia foto/Silent en esta ruta es solo traza', '0x436f5b84..0x436f5b96', 'VERIFICADO', 'Unicorn, 4 modos', f'{TC}::MessageContent', 'Con depuración 0xff; byte [dbg+0xc] puede forzar la emisión'),
 e('S60-C7', C, 'A6000', 'El bloque de 24 B obj+0xe20 (= payload+0x20 de Sol) lo escriben dos productores vía el accesor 0x43ae8504: A (0x437ab510, 6 pares idénticos de obj+0x168/0x16a) y B (0x43aecbfa, 5 pares de obj8+0x48..0x5f + sexto par por tabla 0x437a5a6c); son 6 pares (u16,u16), no un tiempo directo', '0x43ae8504, 0x437ab510, 0x43aecbfa, 0x437a5a6c', 'VERIFICADO (escritores) / HIPÓTESIS (semántica)', 'barrido de accesores 0x43ae84xx + Capstone', f'{TC}::A6000Block', 'Origen de obj+0x168/0x16a y de obj8+0x48.. y condiciones A/B (0x43aeb0cc, [cfg+0x3a]) sin resolver; no se demuestra que sean M de temporización'),
 e('S60-C8', C, 'A6000', 'El accesor de obj+0xe04 (0x43ae84da) solo tiene un llamador (0x4376682c) que escribe un único byte; obj+0xe04..e53 es un registro de estado compuesto por muchos productores (e08:1, e0c:7, e20:2, e3c:5 llamadores)', '0x43ae84da, 0x4376682c', 'VERIFICADO', 'barrido de accesores', 'tests/test_s60_claude.py (json de llamadores)', 'No se analizaron todos los productores'),
 e('S60-G1', G, 'A6000', 'Receptor del despachador: tarea 0x43806e38 (recv 0x3030f, timeout -1) → 0x438069f0 → libera; emisores de respuesta 0x43b00fe6 (caso 3→4) y 0x43b00f62 (caso 9→10) vía 0x43806400 a 0x8003030f', '0x43806e38, 0x43806400, 0x43b00fe6, 0x43b00f62', 'VERIFICADO', 'Sol: Capstone+Unicorn; Claude: bytes', f'{TS}', 'Bit 31 del handle de envío vs 0x3030f del receptor sin resolver; quién envía las peticiones 3/9 no localizado', True),
 e('S60-G2', G, 'A6000', 'CORRECCIÓN a S60-01: tabla TBH 0x43806a04 usa base pc=0x43806a08; manejadores caso 4→0x43806c28 y caso 10→0x43806d06 (Sol: …c24/…d02); los cuerpos citados coinciden', '0x43806a04', 'VERIFICADO (corrección Claude)', 'Capstone + lectura de tabla', f'{TC}::A6000Block::test_sol_dispatch_table', 'Error de 4 B en la dirección de entrada en s60-sol.md; sin efecto en sus conclusiones', True),
 e('S60-G3', G, 'A6000', 'Orden de publicación rol 1: obj+d64→db4, luego obj+e04→d64 y d60→c4c; mensajes 4/10 transportan obj+e04; escritor último de e04 no localizado', '0x43b00dd4..0x43b00e1a', 'VERIFICADO (orden) / PARCIAL (origen)', 'Sol: Unicorn; Claude: desensamblado', f'{TS}', 'Valores inyectados sintéticos; ver S60-C8 para los productores del registro', True),
 e('S60-G4', G, 'A6000', 'Tv: entrada AEOUT3+0xfc+2i → 0x4382fa94 → 0x4383d4d0; clk P+0x4c0 NO VERIFICADO; N/svr/VdNum PARCIAL; 0x0b/0x2f NO VERIFICADO', '0x4383dfb6..0x4383e01a', 'PARCIAL / NO VERIFICADO', 'Sol: REA + Capstone', f'{TS}', 'Sin verificar de forma independiente por Claude en S60 (límite de uso de GPT, sin auditoría)', False),
]
hyp = [
 ('H60-1', 'VERIFICADO', 'Los mensajes 0x1000/0x1001 son registros de traza que reflejan parámetros ya programados; no son órdenes ni sincronización'),
 ('H60-2', 'PARCIAL', 'El consumidor de la cola de trazas 0x8f013a no está en la imagen por referencia directa'),
 ('H60-3', 'PARCIAL', 'Los 24 B +0xdd0 del A6000 se componen de 6 pares (u16,u16) con dos productores localizados; su semántica de tiempo es HIPÓTESIS'),
 ('H60-4', 'NO VERIFICADO', 'Fin de integración electrónica del IMX210 / IMX235; S51 A=NO, B=NO, C=NO'),
]
out = dict(phase='S60', date='2026-10-20', baseline='S59', sha256=dict(A6000=A6, A7S=A7), entries=entries,
           hypotheses=[dict(id=i, status=s, text=t) for i, s, t in hyp],
           gpt_cross_validation='NO OBTENIDA: codex exec devolvió "usage limit" (exit 1) en la auditoría; ver docs/capture/s60-cross-validation.md',
           s51=dict(A='NO', B='NO', C='NO'))
(R / 'analysis/s60-evidence-matrix.json').write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(entries), 'entradas')
