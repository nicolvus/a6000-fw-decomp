import sys, runpy, os
S=os.path.dirname(os.path.abspath(__file__)); H="/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/scripts/gui/harness"
sys.path.insert(0,S)
import ae
c=os.environ.get("ISO_COD")
if c: ae.ISO_CODIGO[0]=int(c,0)
sys.path.insert(0,H)
sys.argv=[H+"/live.py"]+sys.argv[1:]
runpy.run_path(H+"/live.py",run_name="__main__")
