import ply.lex as lex

keywords = ["func", "if", "else", "while", "for", "return", "class", "in", "import"]

reserved = ()

tokens = (
  "NUMBER", "STRING", "FLOAT", "NAME", "CHAR", "SLCOM", "HSCOM", "MLCOM",
  "TIMES", "PLUS", "MINUS", "DIVIDE",
  "COMMA",  "COLON", "NEWLINE", "DOT", "DDOT",
  "DEQUALS", "EQUALS", "NEQUALS", "GEQUALS", "LEQUALS",
  "LPAREN", "RPAREN",
  "LSBRACK", "RSBRACK",
  "LCBRACK", "RCBRACK",
  "LABRACK", "RABRACK",
)

for keyword in keywords:
  name = keyword.upper()
  tokens += name,
  reserved += name,

t_TIMES = r'\*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_DIVIDE = r'/'

t_DEQUALS = r'\=\='
t_NEQUALS = r'\!\='
t_GEQUALS = r'\>\='
t_LEQUALS = r'\<\='

t_EQUALS = r'\='
t_COMMA = r'\,'
t_COLON = r'\;'

def escape(text):
  out = ""
  for i in range(len(text)):
    c = text[i]
    if c == "\\" and len(text) > i + 1 and text[i+1] in ("\\", '"'):
      continue
    out += c
  return out

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSBRACK = r'\['
t_RSBRACK = r'\]'
t_LCBRACK = r'\{'
t_RCBRACK = r'\}'
t_RABRACK = r'<'
t_LABRACK = r'>'
t_NEWLINE = r'\n'
def t_STRING(t):
  r'(\"([^\\"]|(\\.))*\")'
  t.value= escape(t.value)
  return t


t_CHAR = r'\'((.)|\\.)\''
t_ignore = " \t"
t_DOT = r'\.'
t_DDOT = r'\.\.'

t_SLCOM = r'//.*'
t_HSCOM = r'\#.*'
t_MLCOM = r'(/\*(.|\n)*?\*/)'



def t_ID(t):
  r'[a-zA-Z_\&\*][a-zA-Z0-9_\&\*]*'
  if t.value in keywords: t.type = t.value.upper()
  else: t.type = "NAME"
  t.value = t.value
  return t

def t_FLOAT(t):
  r'\d+\.\d+'
  t.value = t.value
  return t

def t_NUMBER(t):
  r'\d+'
  t.value = t.value
  return t

def t_error(t):
  print("[LEXER] Error: Invalid syntax: \""+t.value+"\"")
  exit()
  return t

lexer = lex.lex()
