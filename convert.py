var_types = {"main": {}, "malloc": {'size': 'int'}}
declared = {"main": []}
dtypes = ["int", "float", "char*"]
classes = []
rev = ["str", "arr", "int"]
objs = {}
funcs = {"main": ['int'], "malloc": ['void*', None, None, True], "input" : ["str",None,None,False]}

class Output():
  def __init__(self):
    self.out = ""
    self.main = ""
    self.code = ""
    self.tmp = ""
    self.header = ""
    self.i = 2

  def w(self, text):
    text = " "*self.i + text
    if self.out == "main": self.main += text
    elif self.out == "none": pass
    else: self.code += text

  def final(self):
    return self.code,self.main

out = Output()
out.out = "main"
#out.header += "#include<stdio.h>\n#include<stdlib.h>\n"

def type_(a):
  if a == "num": typ = "int"
  elif a == "str": typ = "char*"
  elif a == "float": typ = "float"
  else: typ = a

  return typ

def r_type(a):
  if a=="int": f = "num"
  elif a == "char*": f = "str"
  elif a == "float": f = "float"
  else: f = a
  return f

def walk(a, As=False, fn="main"):
  global out
  if a == None: return

  if a[0] == "const":
    return a[1], a[2]

  if a[0] == "assign":
    arr_suf = ""

    if a[2][0] == "call" and a[2][1] in classes:
      objs.update({a[1][1]: a[2][1]})

    v = walk(a[2], As=True, fn=fn)

    if "*"+a[1][1] in var_types[fn]:
      name = "*" + a[1][1]
      name_ = "*(" + a[1][1]

    else:
      name = a[1][1]
      name_ = a[1][1]

    if v[-1] == "arr": arr_suf="[]"

    auto_v = v[1]

    if a[1][0] == None: typ = type_(v[1]) # from const (auto)
    else: typ = type_(a[1][0]) # manual

    if len(a) == 4:
      i = walk(a[3], As=True, fn=fn)
      if name[0] == "*":
        arr_suf = "+"+i[0]
      else: arr_suf = "["+i[0]+"]"

      typ = var_types[fn][name]


    for r in rev:
      ar = "arr" if arr_suf == "[]" else None
      if r in (a[1][0], v[1], ar, r_type(v[1])):
        if "arr" in (a[1][0], v[1], ar, r_type(v[1])): r = "arr"
        objs.update({a[1][1]: r})


    if (a[1][1] not in var_types[fn].keys() or a[1][1] not in declared[fn]) and "*"+a[1][1] not in declared[fn] and "*"+a[1][1][1:] not in declared[fn]: # if already declared
      if typ != "": spc = typ + " "
      else: spc = typ
      if ("." in name):
        spc = ""
      if out.out != "none": declared[fn].append(a[1][1])
    else:spc = ""

    br = ")" if name_[:2] == "*(" else ""

    out.w(spc + name_ + arr_suf + br + " = " + v[0] + ';\n');
    if typ != "": var_types[fn].update({a[1][1]: typ})

  if a[0] == "var":
    name = a[1][1]
    typ = var_types[fn].get(name)

    if len(a) == 3:
      if len(a[2]) == 3:
        name = name + "[" + a[2][1] + "]"
      else:
        name = name + "[" + a[2][1][1] + "]"

    if "*"+name in var_types[fn]: name = "*"+name
    return name, typ

  if a[0] in ("+", "-","/","*", "==", "!=", ">=", "<=", "<", ">"):
    l = walk(a[1], As=True, fn=fn)
    r = walk(a[2], As=True, fn=fn)
    typ = r[1]
    if l[1] in dtypes and r[1] in dtypes:
      if dtypes.index(l[1]) > dtypes.index(r[1]): typ = l[1]
      elif dtypes.index(l[1]) < dtypes.index(r[1]): typ = r[1]

    if l[1] in ("str", "char*") and r[1] in ("str", "char*") and a[0] == "+":
      return walk(("call", "str_con", [('var',['char*',l[0]]),('var',['char*',r[0]])]),As=True,fn=fn)

    return l[0] + " " + a[0] + " " +r[0], typ

  if a[0] == "if":
    cond = walk(a[1], As=True, fn=fn)
    out.w("if ("+cond[0]+") {\n")
    out.i += 2
    for w in a[2]:
      walk(w,fn=fn)
    out.i -= 2

    out.w("}")

    if a[3] != []:
      i = out.i
      out.i = 0
      out.w(" else { \n")
      out.i = i
      out.i += 2
      for w in a[3][1]:
        walk(w, fn=fn)
      out.i -= 2
      out.w("}")

    out.w("\n")


  if a[0] == "define_func":
    if funcs[a[1]][2] == False:
      out_org = out.out
      i_org = out.i
      out.out = "none"
      old_args = dict(var_types[a[1]])


      for h in funcs[a[1]][1]:
        if h == None: continue
        v = walk(h, fn=a[1])

      out.out = "code"
      out.i = 0

      typ = type_(funcs[a[1]][0])
      if typ == None: typ = "void"
      out.w(typ + " " + a[1] + " (")

      argss = []
      for v in funcs[a[1]][3]:
        if v[0] == "*" and not a[1].startswith("arr_"): v_ = v[1:]
        else: v_ = v
        ty = type_(var_types[a[1]][v_])
        if ty == "char[]":
          ty = "char"
          v += "[]"
        argss.append(ty + " " + v)
        declared[a[1]].append(v_)

      out.w(",".join(argss) + ") {\n")


      out.i += 2
      for h in funcs[a[1]][1]:
        if h == None: continue
        v = walk(h, fn=a[1])
      out.i -= 2

      out.w("}\n\n")
      out.out = out_org
      out.i = i_org

      var_types[a[1]] = old_args
      funcs[a[1]][2] = True


  if a[0] == "call_m":
    pf = objs.get(a[1])
    name = pf + "_" + a[2]

    if name in var_types and "this" in var_types[name].keys():
      args = [("var", [pf, a[1]])] + a[3]
    else:
      args = a[3]

    if pf in rev:
      args.insert(0, ('var', [var_types[fn].get(a[1]), a[1]]))

    return walk(("call", name, args), As=As, fn=name)

  if a[0] == "raw":
    return a[1]

  if a[0] == "call":
    args = []
    name = a[1]
    raw_args = a[2]
    typ = "void"

    if name == "volatile_c":
      out.w(a[2][0][1][1:-1] + "\n")
      return

    if name in classes:
      name = a[1] + "_init"
      typ = a[1]

    if name not in funcs:
      for j in a[2]:
        v = walk(j, As = True)
        args.append(v[0])

      x = name + "(" + ",".join(args) + ")", typ
      if As == True: return x
      else: out.w(x[0]+";\n")
      return

    i = 0
    if name not in var_types:
       print("ERROR: function '"+name+"' not defined\n")
       exit()
    for v in var_types[name]:
      j = raw_args[i]
      if v != "this":
        m = walk(j)
      else:
        m = [j[1][1], j[1][0]]
      args.append(m[0])
      var_types[name][v] = m[1]
      i += 1

    if funcs[name][2] == False: walk(("define_func", name))

    x = name + "(" + ",".join(args) + ")", funcs[name][0]
    if As == True: return x
    else: out.w(x[0]+";\n")

  if a[0] == "func":
    typ_o = a[1][0]
    name = a[1][1]
    vrs = a[2]
    var_types.update({name: {}})
    declared.update({name: []})

    arg_names = []
    for v in vrs:
      if v[1][0] != None: typ = v[1][0]
      else: typ = None
      var_types[name].update({v[1][1]: typ})
      arg_names.append(v[1][1])

    funcs.update({name: [typ_o, a[3], False, arg_names]})


  if a[0] == "return":
    v = walk(a[1], As=True, fn=fn)
    out.w("return " + v[0] + ';\n')
    if funcs[fn][0] == None: funcs[fn][0] = v[-1]

  if a[0] == "array":
    args = []
    for i in a[2]:
      args.append(i[1])

    if a[1] == True: typ = type_(a[2][0][2])
    else: typ = "arr"
    return "{"+",".join(args)+"}", typ, "arr"

  if a[0] == "struct":
    out.w(a[1] + " " + a[2] + ";\n")

  if a[0] == "while":
    cond = walk(a[1], fn=fn)
    out.w("while ( "+cond[0]+" ){\n");
    out.i += 2
    for h in a[2]:
      if h == None: continue
      v = walk(h, fn=fn)
    out.i -= 2
    out.w("}\n")


  if a[0] == "for":
    st = walk(a[3])
    en = walk(a[4])
    vr = a[2][1][1]

    var_types[fn][vr] = "int"
    out.w("for (int "+vr+" = "+st[0]+"; "+vr+" >= "+st[0]+" && "+vr+" <= "+en[0] + " ; "+vr+"++){\n");
    out.i += 2
    for h in a[5]:
      if h == None: continue
      v = walk(h, fn=fn)
    out.i -= 2

    out.w("}\n")

  if a[0] == "comm":
    out.w("/* ")
    i = out.i
    out.i = 0

    if len(a[1]) > 1:
      out.i = i
      j = 1
      for com in a[1]:
        jj = "\n" if j < len(a[1]) else ""
        out.w(com.strip()+jj)
        j += 1
      out.i = 0
    else:
      out.i = 0
      out.w(a[1][0])

    out.w(" */\n")
    out.i = i

  if a[0] == "class":
    name = a[1]
    body = a[2]
    out_org = out.out
    i_org = out.i
    out.out = "code"
    classes.append(name)
    out.i=0
    out.w("typedef struct t_" + name.upper() + " {\n")
    out.i += 2

    for st in body:
      if st == None: continue
      if st[0] == "var":
        j = type_(st[1][0])
        out.w(j + " " + st[1][1] + ";\n")

    out.i -= 2
    out.w("} "+name+";\n\n")
    out.out = out_org
    out.i = i_org
    has_init = False

    for st in body:
      if st == None: continue
      if st[0] == "func":

        if st[1][1][0] == "_":
          st[1][1] = name + st[1][1]
        else: st[1][1] = name + "_" + st[1][1]

        if st[1][1] == name + "_init":
          has_init = True
          st[1][0] = name
          st[3].insert(0, ("struct", name, "this"))
          st[3].append(("return", ("var", [name, "this"])))

        for i in range(len(st[2])):
          arg = st[2][i]
          if arg[1][1] == "this":
            st[2][i][1][0] = name

        v = walk(st)

    if not has_init:
      walk(('func', [name, name+'_init'], [], [('struct', name, 'this'), ('return', ('var', [name, 'this']))]))
