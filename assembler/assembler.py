import ply.lex as lex
import ply.yacc as yacc
import sys
import json
import argparse

reserved = {
    'move_immed_i' : 'MOVE_IMMED_I',
    'move_immed_f' : 'MOVE_IMMED_F',
    'move' : 'MOVE',
    'iadd' : 'IADD',
    'isub' : 'ISUB',
    'imul' : 'IMUL',
    'idiv' : 'IDIV',
    'imod' : 'IMOD',
    'igt' : 'IGT',
    'igeq' : 'IGEQ',
    'ilt' : 'ILT' ,
    'ileq' : 'ILEQ',
    'fadd' : 'FADD',
    'fsub' : 'FSUB',
    'fmul' : 'FMUL',
    'fdiv' : 'FDIV',
    'fgt' : 'FGT',
    'fgeq' : 'FGEQ',
    'flt' : 'FLT' ,
    'fleq' : 'FLEQ',
    'ftoi' : 'FTOI',
    'itof' : 'ITOF',
    'bz' : 'BZ' ,
    'bnz' : 'BNZ', 
    'jmp' : 'JMP',
    'hload' : 'HLOAD', 
    'hstore' : 'HSTORE',
    'halloc' : 'HALLOC',
    'call' : 'CALL',
    'ret' : 'RET' ,
    'save' : 'SAVE',
    'restore' : 'RESTORE',
    'iwrite' : 'IWRITE',
}

tokens = [
    'STATICDATA',
    'LABEL',
    'INSTRUCTION',
    'REGISTER',
    'COMMA',
    'FLOATLITERAL',
    'INTLITERAL'
    
] + list(reserved.values()) + [
    'LABELREFERENCE']


def t_STATICDATA(t):
    r'\.static_data'
    return t

t_ignore  = ' \t'

t_COMMA = r','

def t_REGISTER(t):
    r'(a|t)[0-9]+'
    return t

def t_LABEL(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*:'
    return t

def t_INSTRUCTION(t):
    r'[a-z_]+'
    a = reserved.get(t.value, None)
    if a == None:
        raise Exception(f'{t.value}')
    t.type = reserved.get(t.value, None)

    return t


def t_LABELREFERENCE(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    return t


def t_FLOATLITERAL(t):
    r'[0-9]+\.[0-9]'
    t.value = float(t.value)
    return t

def t_INTLITERAL(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_COMMENT(t): 
    r'\#.*' 
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Error: Illegal character '{t.value}'", file=sys.stderr)
    sys.exit(1)


lexer = lex.lex()

start = 'program'

def p_error(p):
    print(f"Syntax error in input! {p}")

def p_empty(p):
    'empty :'
    pass
    

def p_program(p):
    '''program : STATICDATA INTLITERAL element_list'''
    
    p[0] = {}
    p[0]['labels'] = {}
    p[0]['basic_blocks'] = []
    p[0]['.static_data'] = p[2]
    
    cur_basic_block_number = 0
    for basic_block in p[3]:
        
        for label in basic_block['labels']:
            p[0]['labels'][label] = cur_basic_block_number
            
        p[0]['basic_blocks'].append(basic_block['instructions'])
        cur_basic_block_number += 1
    
   



def p_element_list(p):
    '''element_list : element element_list
        | empty'''
    
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]


def p_label_list(p):
    '''label_list : label label_list
        | empty'''
        
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]


def p_element(p):
    '''element : label label_list instruction instruction_list'''
    p[0] = {}
    p[0]['labels'] = [p[1]] + p[2]
    p[0]['instructions'] = [p[3]] + p[4]
    


def p_instruction_list(p):
    '''instruction_list : instruction instruction_list
        | empty'''
        
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]


def p_label(p):
    '''label : LABEL'''
    p[0] = p[1][:-1]
    


def p_instruction(p):
    '''instruction : nullary_instruction
        | unary_instruction
        | binary_instruction
        | tertiary_instruction'''
    p[0] = p[1]


def p_tertiary_reg_list(p):
    '''tertiary_reg_list : REGISTER COMMA REGISTER COMMA REGISTER'''
    p[0] = [p[1], p[3], p[5]]

def p_tertiary_instruction(p):
    '''tertiary_instruction : IADD tertiary_reg_list
        | ISUB tertiary_reg_list
        | IMUL tertiary_reg_list
        | IDIV tertiary_reg_list
        | IMOD tertiary_reg_list
        | IGT tertiary_reg_list
        | IGEQ tertiary_reg_list
        | ILT tertiary_reg_list
        | ILEQ tertiary_reg_list
        | FADD tertiary_reg_list
        | FSUB tertiary_reg_list
        | FMUL tertiary_reg_list
        | FDIV tertiary_reg_list
        | FGT tertiary_reg_list
        | FGEQ tertiary_reg_list
        | FLT tertiary_reg_list
        | FLEQ tertiary_reg_list
        | HLOAD tertiary_reg_list
        | HSTORE tertiary_reg_list'''
    p[0] = [p[1]] + p[2]


def p_binary_reg_list(p):
    '''binary_reg_list : REGISTER COMMA REGISTER'''
    p[0] = [p[1], p[3]]

def p_binary_instruction(p):
    '''binary_instruction : HALLOC binary_reg_list
        | BNZ binary_reg_list
        | BZ binary_reg_list
        | ITOF binary_reg_list
        | FTOI binary_reg_list
        | MOVE binary_reg_list '''
    p[0] = [p[1]] + p[2]
    
def p_binary_instruction_(p):
    '''binary_instruction :  MOVE_IMMED_I REGISTER COMMA INTLITERAL
        | MOVE_IMMED_F REGISTER COMMA FLOATLITERAL '''
    p[0] = [p[1], p[2], p[4]]

def p_unary_instruction(p):
    '''unary_instruction : RESTORE REGISTER
        | SAVE REGISTER
        | CALL LABELREFERENCE
        | JMP LABELREFERENCE
        | IWRITE REGISTER'''
    p[0] = [p[1], p[2]]

def p_nullary_instruction(p):
    '''nullary_instruction : RET'''
    p[0] = [p[1]]

parser = yacc.yacc()


def modify_file_extension(file_name): 
    if file_name.endswith('.ami'): 
        return file_name[:-4] + '.json'
    return file_name + '.json'
    

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--infile", type=str, help="input file - will read from stdin if none specified")
    
    args = parser.parse_args()
    
    
    if args.infile == None:
        infile = sys.stdin
        outfile = sys.stdout
    else:
        try:
            infile = open(args.infile, 'r')
            outfile = open(modify_file_extension(args.infile), 'w')
            
        except:
            print("error with opening files", file=sys.stderr)
            sys.exit(1)
    
    f = yacc.parse(infile.read())
    
    
    with open("data.json", "w") as json_file:
        json.dump(f, outfile)
