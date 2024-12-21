import ply.lex as lex
import sys 


reserved = {
    'boolean' : 'BOOLEAN',
    'break' : 'BREAK',
    'continue' : 'CONTINUE',
    'class' : 'CLASS',
    'else' : 'ELSE',
    'extends' : 'EXTENDS',
    'false' : 'FALSE',
    'float' : 'FLOAT',
    'for' : 'FOR',
    'if' : 'IF',
    'int' : 'INT',
    'new' : 'NEW',
    'null' : 'NULL',
    'private' : 'PRIVATE',
    'public' : 'PUBLIC',
    'return' : 'RETURN',
    'static' : 'STATIC',
    'super' : 'SUPER',
    'this' : 'THIS',
    'true' : 'TRUE',
    'void' : 'VOID',
    'while' : 'WHILE'
}

tokens = [
    'IDENTIFIER',
    'LBRACE',
    'RBRACE',
    'SEMICOLON',
    'LPAREN',
    'RPAREN',
    'COMMA',
    'ASSIGNMENT',
    'EQUALITY',
    'FIELDACCESS',
    'INTLITERAL',
    'LESS',
    'GREATER',
    'PLUS',
    'FLOATLITERAL',
    'STRINGLITERAL',
    'AND',
    'OR',
    'MINUS',
    'NOT',
    'MULTIPLY',
    'DIVIDE',
    'NOTEQUALS',
    'GREATEROREQUAL',
    'LESSOREQUAL',
    'INCREMENT',
    'DECREMENT'
] + list(reserved.values())


 
def t_MULTILINECOMMENT(t):
    r'/\*(.|\n)*?\*/'
    pass
 

t_ignore  = ' \t'


t_LBRACE = r'{' 
t_RBRACE = r'}'
t_LPAREN = r'\(' 
t_RPAREN = r'\)'
t_COMMA = r','
t_SEMICOLON = r';'
t_ASSIGNMENT = r'='
t_EQUALITY = r'=='
t_FIELDACCESS = r'\.'
t_LESS = r'<'
t_GREATER = r'>'
t_PLUS = r'\+'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MINUS = r'-'
t_NOT = r'!'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOTEQUALS = r'!='
t_GREATEROREQUAL = r'>='
t_LESSOREQUAL = r'<='
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'


def t_FLOATLITERAL(t):
    r'[0-9]+\.[0-9]'
    t.value = float(t.value)
    return t

def t_INTLITERAL(t):
    r'\d+'
    t.value = int(t.value)
    return t



def t_STRINGLITERAL(t):
    r'"[^"]*"'
    t.value = str(t.value)
    return t

def t_COMMENT(t):
    r'//.*'
    pass




def t_IDENTIFIER(t):
    r'[a-zA-Z][_a-zA-Z0-9]*'
    t.type = reserved.get(t.value,'IDENTIFIER')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Error: Illegal character '%s'" % t.value[0])
    sys.exit()


lexer = lex.lex()



def lex_file(data):
    lexer.input(data)

   
    while True:
        tok = lexer.token()
        if not tok: 
            break 
    
    print("YES")




if __name__ == "__main__":
    file = open(sys.argv[1], 'r', encoding="utf-8")
    data = file.read()
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok: 
            break  
        print(tok)


