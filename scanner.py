import ply.lex as lex
reserved = {
    'for':"FOR",
    'return':"RETURN",
    'break':"BREAK"
}

tokens = (
    'TYPE',
    'ID',
    'FOR',
    'INTEGER',
    'FRACTION',
    'OR',
    'AND',
    'EQ',
    'NEQ',
    'LE',
    'GE',
    'SHL',
    'SHR',
    'DPLUS',
    'DMINUS',
)

t_AND = r'&&'
t_OR = r'\|\|'
t_EQ = r'=='
t_NEQ = r'!='
t_LE = r"<="
t_GE = r'>='
t_SHL = r'<<'
t_SHR = r'>>'
t_DPLUS = r'\+\+'
t_DMINUS = r'\-\-'

literals = "+-*/%=|^&<>[]{}(),;"

def t_TYPE(t):
    r'(int|float|char|void)'
    return t

def t_FRACTION(t):
    r'[1-9][0-9]*\.[1-9][0-9]*'
    return t

def t_INTEGER(t):
    r'[1-9][0-9]*'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9]*'
    t.type = reserved.get(t.value,"ID")
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore  = ' \t'

def t_error(t):
    print("Illegal character '%s'" % t.value)
    t.lexer.skip(1)

lexer = lex.lex()

'''
lexer.input('123.324 314')
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
'''