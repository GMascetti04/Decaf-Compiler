import ply.yacc as yacc
from decaf_lexer import tokens
import decaf_ast
import decaf_typecheck
import sys

precedence = (
    ('right', 'ASSIGNMENT'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQUALITY' ,'NOTEQUALS'),
    ('left' , 'GREATER', 'LESS', 'GREATEROREQUAL', 'LESSOREQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'NOT', 'UMINUS')
)

start = 'program'


red_text = '\033[91m'
white_text = '\033[0m'

def p_error(p):

    if p == None:
        print(f"{red_text}Parsing Error: Unexpected end of file.{white_text}")
        sys.exit()
    

    input_str = p.lexer.lexdata

    start_line_pos = input_str.rfind('\n', 0, p.lexer.lexpos) + 1

    col_num = p.lexpos - start_line_pos + 1

    end_line = input_str.find('\n', start_line_pos + 1)

    if end_line == -1:
        end_line = len(input_str)

    bad_line = input_str[start_line_pos : end_line]

    below_line = [' '] * len(bad_line)
    below_line[col_num-1] = '~'
    below_line_str = ''.join(below_line)
    

    print(f"{red_text}Parsing Error: Syntax error at line {p.lexer.lineno} and involving character '{p.value}' at position {col_num}{white_text}", file=sys.stderr)

    
    print("---", file=sys.stderr)
    print(bad_line, file=sys.stderr)
    print(red_text + below_line_str + white_text, file=sys.stderr)
    print("---", file=sys.stderr)
    print(f"{red_text}Compilation Failed{white_text}", file=sys.stderr)

    sys.exit(1)



def p_empty(p):
    'empty :'
    pass
    

def p_program_empty(p):
    '''program : empty'''
    p[0] = decaf_ast.AST()


### Section 2: Program Definition
def p_program(p):
    '''program : program class_declaration'''

        
    p[1].add_class_record(p[2])
    p[0] = p[1]

    

def p_program_error(p):
    '''program : program error'''
    p[0] = None

### Section 2: Class Declarations
def p_class_declaration(p):
    'class_declaration : CLASS IDENTIFIER class_extends_modifier LBRACE  class_body_declarations_list RBRACE'
    p[0] = decaf_ast.Class_Record(p[2], p[3], p[5])




def p_class_extends_modifier(p):
    '''class_extends_modifier : EXTENDS IDENTIFIER
            | empty'''
    if len(p) == 2:
        p[0] = None
    else:
        p[0] = p[2]


#cannot be empty
def p_class_body_declarations_list(p):
    '''class_body_declarations_list : class_body_declarations_nullable class_body_declaration '''

    #returns a list of all class declarations in order!
    p[0] = p[1]
    p[0].append(p[2])



def p_class_body_declarations_nullable(p):
    '''class_body_declarations_nullable : class_body_declarations_nullable class_body_declaration 
          | empty'''

    if len(p) == 2:
        p[0] = []
    else:
        t = p[1]
        t.append(p[2])
        p[0] = t

    

def p_class_body_declaration(p):
    '''class_body_declaration : field_declaration 
            | constructor_declaration
            | method_declaration
    '''
    p[0] = p[1]

### Section 2: Fields
def p_field_declaration(p):
    'field_declaration : modifier var_declaration'
    
    res = []
    
    for i in p[2]:
        res.append(decaf_ast.Field_Record(i.get_name(),"temp id", "temp class", p[1][0], p[1][1],  i.get_type()))
        
    p[0] = res

    

def p_modifier(p):
    'modifier : visibility_optional static_optional'
    p[0] = (p[1], p[2])    

def p_visibility_optional_private(p):
    '''visibility_optional : PRIVATE '''
    p[0] = 'private'

def p_visibility_optional_public(p):
    '''visibility_optional : PUBLIC '''
    p[0] = 'public'

def p_visibility_optional_default(p):
    '''visibility_optional : empty '''
    p[0] = 'private'

def p_static_optional_static(p):
    '''static_optional : STATIC '''
    p[0] = 'static'



def p_static_optional_instance(p):
    '''static_optional : empty'''  
    p[0] = 'instance'  

def p_type(p):
    '''type : INT
            | FLOAT
            | BOOLEAN
            | IDENTIFIER
    '''
    p[0] = p[1]

def p_var_declaration(p):
    'var_declaration : type variable variables_list SEMICOLON'

    name_list = [p[2]] + p[3]
    
    var_dec_list = []
    
    for name in name_list:
        var_dec_list.append(decaf_ast.Variable_Declaration(p[1], name))


    p[0] = var_dec_list





def p_variables_list(p):
    '''variables_list : COMMA variable variables_list
            | empty'''
            
    if len(p) == 2:
        p[0] = []
    else:
        res = []
        res.append(p[2])
        res.extend(p[3])
        p[0] = res

#no arrays for now
def p_variable(p):
    'variable : IDENTIFIER'
    p[0] = p[1]

### Section 2: Methods and Constructors
def p_method_declaration(p):
    '''method_declaration : modifier type IDENTIFIER LPAREN formals RPAREN block'''
    p[0] = decaf_ast.Method_Record(p[3], "temp id", 'temp containing class', p[1][0], p[1][1], p[5], p[2], p[7])


def p_method_declaration_void_args(p):
    '''method_declaration : modifier VOID IDENTIFIER LPAREN formals RPAREN block'''
    p[0] = decaf_ast.Method_Record(p[3], "temp id", 'temp containing class', p[1][0], p[1][1], p[5], 'void', p[7])

def p_method_declaration_void_nullary(p):
    '''method_declaration :  modifier VOID IDENTIFIER LPAREN RPAREN block'''
    p[0] = decaf_ast.Method_Record(p[3], "temp id", 'temp containing class', p[1][0], p[1][1], [], 'void', p[6])


def p_method_declaration_return_nullary(p):
    '''method_declaration : modifier type IDENTIFIER LPAREN RPAREN block'''

    #name, id, containing_class, visibility, applicability, parameters, return_type, body
    p[0] = decaf_ast.Method_Record(p[3], "temp id", 'temp containing class', p[1][0], p[1][1], [], p[2], p[6])

def p_formal_parameters_list(p):
    '''formal_parameters_list : COMMA formal_parameter formal_parameters_list
            | empty'''

    if len(p) == 2:
        p[0] = []
    else:
        res = []
        res.append(p[2])
        res.extend(p[3])
        p[0]  = res

def p_formals(p):
    'formals : formal_parameter formal_parameters_list'
    
    res = []
    res.append(p[1])
    res.extend(p[2])
    
    p[0] = res
    


def p_formal_parameter(p):
    'formal_parameter : type variable'
    p[0] = (p[1], p[2])


#p[0] is tuple containing variable table and constructor body
def p_constructor_declaration(p):
    '''constructor_declaration : modifier IDENTIFIER LPAREN RPAREN block
          | modifier IDENTIFIER LPAREN formals RPAREN block'''

    if len(p) == 6:
        p[0] = decaf_ast.Constructor_Record(p[2], p[1][0], [], p[5])
    else:
        p[0] = decaf_ast.Constructor_Record(p[2], p[1][0], p[4], p[6])

   
        


### Section 3: Statements
def p_block(p):
    'block : LBRACE statement_list RBRACE'

    p[0] = decaf_ast.Block_Stmt(p[2])

   

   


#returns list of statements in order which they occur
def p_statement_list(p):
    '''statement_list : statement_list statement 
        | empty'''

    if len(p) == 2:
        p[0] = []
    else:
        t = p[1]
        if p[2] == None:
            p[2] = "NONE (TODO FIX)"
       
        t.append(p[2])
        p[0] = t

        



def p_statement(p):
    '''statement : if_statement
    | while_loop
        | for_loop
        | return_statement
        | block
        | var_declaration
        | statement_expression SEMICOLON
    '''
    p[0] = p[1]

def p_statement_break(p):
    '''statement : BREAK SEMICOLON'''
    p[0] = decaf_ast.Break_Statement()
    
def p_statement_continue(p):
    '''statement : CONTINUE SEMICOLON'''
    p[0] = decaf_ast.Continue_Statement()

def p_statement_semicolon(p):
    '''statement :  SEMICOLON'''
    p[0] = None
    

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN statement 
        | IF LPAREN expression RPAREN statement ELSE statement'''
    p[0] = decaf_ast.If_Statement(p[3], p[5], decaf_ast.Skip_Statement() if len(p) == 6 else p[7])


def p_while_loop(p):
    'while_loop : WHILE LPAREN expression RPAREN statement'
    p[0] = decaf_ast.While_Statement(p[3], p[5])


def p_for_loop(p):
    'for_loop : FOR LPAREN for_loop_initializer SEMICOLON for_loop_conditional SEMICOLON for_loop_initializer RPAREN statement'
    p[0] = decaf_ast.For_Statement(p[3], p[5], p[7], p[9])
    
def p_for_loop_initializer(p):
    '''for_loop_initializer : statement_expression'''
    p[0] = p[1]

def p_for_loop_initializer_empty(p):
    '''for_loop_initializer : empty'''
    p[0] = decaf_ast.Skip_Statement()


def p_for_loop_conditional(p):
    '''for_loop_conditional : expression'''
    p[0] = p[1]

def p_for_loop_conditional_empty(p):
    '''for_loop_conditional : empty'''
    p[0] = decaf_ast.Skip_Statement()


def p_return_statement(p):
    '''return_statement : RETURN expression SEMICOLON
        | RETURN SEMICOLON'''
    
    if len(p) == 3:
        p[0] = decaf_ast.Return_Statement(decaf_ast.Skip_Statement())
    else:
        p[0] = decaf_ast.Return_Statement(p[2])

       


### Section 4: Expressions
def p_literal_false(p):
    '''literal : FALSE
    '''
    p[0] = decaf_ast.Constant_Expression(p[1], decaf_typecheck.BaseType.BOOL)

def p_literal_true(p):
    '''literal :  TRUE
    '''
    p[0] = decaf_ast.Constant_Expression(p[1], decaf_typecheck.BaseType.BOOL)

def p_literal_null(p):
    '''literal : NULL
    '''
    p[0] = decaf_ast.Constant_Expression(p[1], decaf_typecheck.BaseType.NULL)

def p_literal_str(p):
    '''literal : STRINGLITERAL
       
    '''
    p[0] = decaf_ast.Constant_Expression(p[1], 'string')

def p_literal_float(p):
    '''literal : FLOATLITERAL
    '''
    p[0] = decaf_ast.Constant_Expression(p[1], decaf_typecheck.BaseType.FLOAT)

def p_literal_int(p):
    '''literal : INTLITERAL'''
    p[0] = decaf_ast.Constant_Expression(p[1], decaf_typecheck.BaseType.INT)

######

def p_expression(p):
    '''expression :  primary
    '''
    p[0] = p[1]



def p_expression_binary_op_mult(p):
    '''expression :  expression MULTIPLY expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.MULTIPLY, p[1], p[3])

def p_expression_binary_op_div(p):
    '''expression :  expression DIVIDE expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.DIVIDE, p[1], p[3])

def p_expression_binary_op_plus(p):
    '''expression :  expression PLUS expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.ADD, p[1], p[3])

def p_expression_binary_op_minus(p):
    '''expression :  expression MINUS expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.SUBTRACT, p[1], p[3])

def p_expression_assign(p):
    '''expression :  assign '''
    p[0] = p[1]

def p_expression_unary_op_not(p):
    '''expression :  NOT expression '''
    p[0] = decaf_ast.Unary_Expression(decaf_ast.Operation.NEGATE, p[2])

def p_expression_unary_op_minus(p):
    '''expression : MINUS expression %prec UMINUS'''
    p[0] = decaf_ast.Unary_Expression(decaf_ast.Operation.UMINUS, p[2])

    
def p_expression_binary_op_or(p):
    '''expression : expression OR expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.OR, p[1], p[3])
    

def p_expression_binary_op_and(p):
    '''expression : expression AND expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.AND, p[1], p[3])

def p_expression_binary_op_notequals(p):
    '''expression : expression NOTEQUALS expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.NOTEQUALS, p[1], p[3])

def p_expression_binary_op_notequality(p):
    '''expression : expression EQUALITY expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.EQUALS, p[1], p[3])

def p_expression_binary_op_less(p):
    '''expression : expression LESS expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.LESSTHAN, p[1], p[3])

def p_expression_binary_op_greater(p):
    '''expression : expression GREATER expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.GREATERTHAN, p[1], p[3])

def p_expression_binary_op_lessorequal(p):
    '''expression : expression LESSOREQUAL expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.LESSOREQUAL, p[1], p[3])

def p_expression_binary_op_greaterorequal(p):
    '''expression : expression GREATEROREQUAL expression'''
    p[0] = decaf_ast.Binary_Expression(decaf_ast.Operation.GREATEROREQUAL, p[1], p[3])

    


def p_primary(p):
    '''primary : literal
            | this
            | SUPER
            | LPAREN expression RPAREN
            | new_object
            | left_hand_side
            | method_invocation
    '''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_this(p):
    '''this : THIS'''
    p[0] = decaf_ast.This_Expression()

def p_new_object(p):
    '''new_object : NEW IDENTIFIER LPAREN RPAREN
        | NEW IDENTIFIER LPAREN arguments RPAREN
            
    '''
    if len(p) == 6:
        p[0] = decaf_ast.New_Object_Expression(p[2], p[4])
    else:
        p[0] = decaf_ast.New_Object_Expression(p[2], [])


def p_assign(p):
    '''assign : left_hand_side ASSIGNMENT expression  '''
    p[0] = decaf_ast.Assign_Expression(p[1], p[3])
 


def p_assign_post_inc(p):
    '''assign :  left_hand_side INCREMENT '''
    p[0] = decaf_ast.Auto_Expression(p[1], 'inc', 'post')


def p_assign_pre_inc(p):
    '''assign : INCREMENT left_hand_side '''
    p[0] = decaf_ast.Auto_Expression(p[2], 'inc', 'pre')


def p_assign_post_dec(p):
    '''assign : left_hand_side DECREMENT '''
    p[0] = decaf_ast.Auto_Expression(p[1], 'dec', 'post')


def p_assign_pre_dec(p):
    '''assign : DECREMENT left_hand_side '''
    p[0] = decaf_ast.Auto_Expression(p[2], 'dec', 'pre')

def p_left_hand_side(p):
    '''left_hand_side : field_access 
        | local_access'''
    p[0] = p[1]

def p_field_access(p):
    '''field_access : primary FIELDACCESS IDENTIFIER'''
    p[0] = decaf_ast.Field_Access_Expression(p[1], p[3])

def p_local_access(p):
    '''local_access : IDENTIFIER'''
    p[0] = decaf_ast.Variable_Reference(p[1])


def p_expression_list(p):
    '''expression_list : COMMA expression expression_list
        | empty'''
        
    if len(p) == 2:
        return None
    
    res = []
    res.append(p[2])
    if p[3] != None:
        res.extend(p[3])
    
    p[0] = res

def p_arguments(p):
    '''arguments : expression expression_list'''
    
    res = []
    
    res.append(p[1])
    if p[2] != None:
        res.extend(p[2])
    
    p[0] = res

def p_method_invocation(p):
    '''method_invocation : field_access LPAREN RPAREN
            | field_access LPAREN arguments RPAREN'''

    if len(p) == 5:
        arg_array = p[3]
    else:
        arg_array = []

    p[0] = decaf_ast.Method_Call_Expression(p[1].get_base_expression(), p[1].get_field_name(), arg_array)
    



def p_statement_expression(p):
    '''statement_expression : assign 
        | method_invocation'''
    p[0] = decaf_ast.Expression_Statement(p[1]) 
    




yacc.yacc()



#returns the ast
def generate_ast(file) -> None | decaf_ast.AST:
    r = yacc.parse(file)

    if r == None:
        return None

    type_correct = r.type_check()
    if type_correct == True:
        return r
            
    else:
        return None