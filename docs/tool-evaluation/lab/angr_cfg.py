import sys, time, angr, logging
logging.disable(logging.CRITICAL)
p = angr.Project(sys.argv[1], auto_load_libs=False)
print("arch", p.arch.name, "entry", hex(p.entry), "obj", type(p.loader.main_object).__name__, "min/max", hex(p.loader.min_addr), hex(p.loader.max_addr))
t = time.time()
cfg = p.analyses.CFGFast(normalize=True, show_progressbar=False)
print("cfgfast_s", round(time.time() - t, 1), "functions", len(cfg.kb.functions), "nodes", len(cfg.graph.nodes), "edges", len(cfg.graph.edges))
big = sorted(cfg.kb.functions.values(), key=lambda f: -f.size)[:5]
for f in big: print(hex(f.addr), f.name, f.size, "blocks", len(list(f.blocks)))
