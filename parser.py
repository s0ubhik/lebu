import ply.yacc as yacc
from lexer import tokens
from convert import walk

precedence = (
   ('left', 'PLUS', 'MINUS'),
   ('left', 'TIMES', 'DIVIDE'),
   ('right', 'EQUALS'),

   ('right', 'DEQUALS'),
   ('right', 'NEQUALS'),
   ('right', 'GEQUALS'),
   ('right', 'LEQUALS'),
   ('right', 'RABRACK'),
   ('right', 'LABRACK'),

   ('right', 'NUMBER'), # to differentiate between tuple and number
   ('right', 'NAME'),   # to differentiate between function call and variable name
   ('right', 'LPAREN', 'LSBRACK'),
)

def p_code(p):
  '''
  code : stmts
  '''

  for i in p[1]:
    walk(i)

def p_stmts_single(p):
  '''
  stmts : stmt
  '''
  p[0] = [p[1]]

def p_stmts_multi(p):
  '''
  stmts : stmt COLON stmts
        | stmt NEWLINE stmts
  '''
  p[0] = [p[1], *p[3]]

def p_stmt(p):
  '''
  stmt : expr
       | assign
       | empty
       | function
       | if
       | while
       | for
       | return
       | class
       | comment
  '''
  p[0] = p[1]

def p_comment_sl(p):
  '''
  comment : SLCOM
  '''
  p[0] = ("comm", [p[1][2:].strip()])

def p_comment_hs(p):
  '''
  comment : HSCOM
  '''
  p[0] = ("comm", [p[1][1:].strip()])

def p_comment_ml(p):
  '''
  comment : MLCOM
  '''
  p[0] = ("comm", p[1][2:-2].split("\n"))


def p_suite_stmt(p):
  '''
  suite : stmt
  '''
  p[0] = p[1]

def p_suite_multi_stmt(p):
  '''
  suite : LCBRACK stmts RCBRACK
  '''
  p[0] = p[2]

def p_empty(p):
  '''
  empty :
  '''
  p[0] = None

def p_expr_call(p):
	'''
	expr : call
	'''
	p[0] = p[1]

def p_expr_const(p):
  '''
  expr : const
  '''
  p[0] = p[1]

def p_const_num(p):
  '''
  const : NUMBER
  '''
  p[0] = ("const", p[1], "num")

def p_const_flt(p):
  '''
  const : FLOAT
  '''
  p[0] = ("const", p[1], "float")

def p_const_chr(p):
  '''
  const : CHAR
  '''
  p[0] = ("const", p[1], "char")


def p_const_str(p):
  '''
  const : STRING
  '''
  p[0] = ("const", p[1], "str")

def p_const_arr(p):
  '''
  expr : array
  '''
  homo = True
  if p[1] == []: homo = False # empty
  else:
    i = p[1][1][2]
    for j in p[1]:
      if i != j[2]: homo = False

  p[0] = ("array", homo, p[1])

def p_arg_lst_none(p):
	'''
	arg_list : LPAREN RPAREN
	'''
	p[0] = []

def p_arg_lst_sngle(p):
	'''
	arg_list : LPAREN expr RPAREN
	'''
	p[0] = [p[2]]

def p_arg_lst(p):
	'''
	arg_list : LPAREN lst RPAREN
	'''
	p[0] = p[2]

def p_array_lst(p):
	'''
	array : LSBRACK lst RSBRACK
	'''
	p[0] = p[2]

def p_array_lst_single(p):
  '''
  array : LSBRACK expr RSBRACK
  '''
  p[0] = [p[2]]


def p_lst(p):
  '''
  lst : expr COMMA
  '''
  p[0] = [p[1]]

def p_lst_lst(p):
  '''
  lst : expr COMMA lst
  '''
  p[0] = [p[1], *p[3]]

def p_lst_expr(p):
  '''
  lst : expr COMMA expr
  '''
  p[0] = [p[1], p[3]]

def p_expr_var_arr(p):
  '''
  expr : id LSBRACK expr RSBRACK
  '''
  p[0] = ("var", p[1], p[3])

def p_expr_var(p):
  '''
  expr : id
  '''
  p[0] = ("var", p[1])

def p_expr_plus_minus(p):
  '''
  expr : expr PLUS expr
       | expr MINUS expr
       | expr TIMES expr
       | expr DIVIDE expr
  	   | expr DEQUALS expr
  	   | expr NEQUALS expr
  	   | expr RABRACK expr
  	   | expr LABRACK expr
  	   | expr GEQUALS expr
  	   | expr LEQUALS expr
  '''
  p[0] = (p[2], p[1], p[3])

def p_expr_group(p):
  '''
  expr : LPAREN expr RPAREN
  '''
  p[0] = p[2]

def p_method(p):
  '''
  method : NAME
  '''
  p[0] = p[1]

def p_mth_(p):
  '''
  method : method DOT NAME 
  '''
  p[0] = p[1]+"."+p[3]

def p_call_arg_method(p):
  '''
  call : method DOT NAME arg_list
  '''
  p[0] = ("call_m", p[1], p[3], p[4])


def p_call_arg(p):
  '''
  call : NAME arg_list
  '''
  p[0] = ("call", p[1], p[2])


def p_assign_arr(p):
  '''
  assign : id LSBRACK expr RSBRACK EQUALS assign
         | id LSBRACK expr RSBRACK EQUALS expr
  '''
  p[0] = ("assign", p[1], p[6], p[3])


def p_assign(p):
  '''
  assign : id EQUALS assign
         | id EQUALS expr
  '''
  p[0] = ("assign", p[1], p[3])


def p_id_typ(p):
  '''
  id : NAME method
  '''
  p[0] = [p[1], p[2]]

def p_id_dot(p):
  '''
  id : method
  '''
  p[0] = [None, p[1]]

def p_function_def(p):
  '''
  function : FUNC id arg_list suite
  '''
  p[0] = ("func", p[2], p[3], p[4])

def p_if_else(p):
  '''
  if : IF expr suite else
  '''
  p[0] = ("if", p[2], p[3], p[4])

def p_if(p):
  '''
  if : IF expr suite
  '''
  p[0] = ("if", p[2], p[3], [])

def p_else(p):
  '''
  else : ELSE suite
  '''
  p[0] = ("else", p[2])

def p_while(p):
  '''
  while : WHILE expr suite
  '''
  p[0] = ("while", p[2], p[3])

def p_return(p):
  '''
  return : RETURN expr
  '''
  p[0] = ("return", p[2])

def p_class(p):
  '''
  class : CLASS NAME suite
  '''
  p[0] = ("class", p[2], p[3])


def p_for(p):
  '''
  for : FOR expr IN expr DDOT expr suite
  '''
  p[0] = ("for", "in",p[2], p[4], p[6], p[7])

def p_error(p):
  pass
parser = yacc.yacc()
