import sys, os
from lexer import lexer
from parser import parser
from convert import out
import painter as p

_help_ = """  lebu.py <FILE> [OPTIONS] 

  -h       Display help message
  -w       No warning messages
  -c       Output only C code
  -o       Specific output file
  -nomain  global code will be ignored
  -nobase  Do not include the lib/base.lb
  -noio    Do not include the lib/io.lb
"""
cc = "gcc"
sc_path = os.path.dirname(os.path.realpath(__file__))

args = sys.argv

def preprocess(file,jp=""):
  if file.startswith("lib/"):
    file = sc_path + "/" +file
  if not os.path.exists(file):
    print(p.bold+p.red+"Error: '"+p.ncol+file+"' not found"+jp)
    exit()

  fp = open(file)
  lns = fp.readlines()
  fp.close()
  top = ""
  code = ""
  for l in lns:
    m = l.strip()
    if m.startswith("import "):
      imp = l[8:-2]
      c,t = preprocess(imp,jp=" in '"+file+"'")
      code += c
      top += t
    elif m.startswith("#define ") or m.startswith("#include"):
      top += m + "\n"

    else: code += l
  return code, top

includes = ["lib/base.bn", "lib/io.bn"]

if len(args) <= 1:
  print(f"{p.bold}{p.red}Error:{p.ncol} No input file")
  exit()

fname = args[1]
od = os.getcwd()
if os.path.exists(fname):
  rd, rname = os.path.split(fname)
  wd, fname = os.path.split(os.path.realpath(fname))
  os.chdir(wd)
else:
  print(f"{p.bold}{p.red}Error:{p.ncol} No such file")
  exit()
ext = ""
compile = True

ofile = ".".join(fname.split(".")[:-1])
cfile = ".".join(fname.split(".")[:-1])

cc_flags = []
warn = True
show_o = True
nomain = False
arg_s = args[2:]
i = 0

while i < len(arg_s):
  arg = arg_s[i]
  if arg == "-w":
    warn = False
  if arg == "-noio" and "lib/io.bn" in includes: includes.remove("lib/io.bn")
  if arg == "-nomain":
    nomain = True
    cc_flags.append("-c")
    ofile += ".o"
  else: ofile += ext
  if arg == "-nobase" and "lib/base.bn" in includes:
    if warn: print(f"{p.bold}{p.purple}Warning:{p.ncol} not using lib/base.bn will take away many features that may lead to conversion errors")
    includes.remove("lib/base.bn")
  if arg == "-c":
    compile = False
  if arg == "-o":
    if compile: ofile = arg_s[i+1]
    else: cfile =  arg_s[i+1]
    show_o = False
    i += 1

  i+= 1

tmp_cfile = cfile + ".tmp.c"
if show_o or compile: cfile += ".c"

r_cfile = cfile if rd == "" else rd + os.sep + cfile
r_ofile = ofile if rd == "" else rd + os.sep + ofile

code, top = "", ""
for inc in includes:
  c, t = preprocess(inc)
  code += c
  top += t

c,t = preprocess(fname)

code += c
top += t

if not show_o: os.chdir(od) # return to the original directory if output path is mentioned

fp = open(tmp_cfile, 'w+')
try:
  parser.parse(code, lexer=lexer)
  fp.write(top+"\n")
  cd, main = out.final()
  fp.write(cd)
  if not nomain: fp.write("int main(){\n"+main+"}")

except:
  pass

fp.close()

pp = f"{cc} -E -P "+tmp_cfile+" -o "+cfile
os.system(pp)

if not compile and show_o: print("C File: "+p.bold+p.blue+r_cfile+p.ncol)

os.remove(tmp_cfile)
if compile:
  cc = f"{cc} "+" ".join(cc_flags)+" "+cfile+" -o "+ofile
  os.system(cc)
  if show_o: print("Executable: "+p.bold+p.green+r_ofile+p.ncol)
  os.remove(cfile)