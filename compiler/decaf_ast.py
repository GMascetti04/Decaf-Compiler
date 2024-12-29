import sys
import decaf_typecheck
from typing import List, Tuple, Optional, Dict
from enum import Enum



class Operation(Enum):
    MULTIPLY = 'mult'
    DIVIDE = 'div'
    ADD = 'add'
    SUBTRACT = 'sub'
    NEGATE = 'neg'
    UMINUS = 'uminus'
    OR = 'or'
    AND = 'and'
    NOTEQUALS = 'neq'
    EQUALS = 'eq'
    LESSTHAN = 'lt'
    GREATERTHAN = 'gt'
    LESSOREQUAL = 'leq'
    GREATEROREQUAL = 'geq'

def combine_resolve_maps(map1, map2):

    new_map = {}

    for key in set(map1.keys()).union(map2.keys()):
        new_map[key]= map1.get(key, []) + map2.get(key, [])

    return new_map


def print_error_msg(msg):
    red_text = '\033[91m'
    white_text = '\033[0m'

    print(f"{red_text}Error: {msg}{white_text}", file=sys.stderr)

class UnresolvedIdentifier:
    
    def __init__(self, name : str):
        self.name = name

class LocalVariableKind(Enum):
    FORMAL = 'formal'
    LOCAL = 'local'


class VariableTableEntry:
    def __init__(self, id : int, name : str, kind : LocalVariableKind, type : decaf_typecheck.BaseType | decaf_typecheck.ClassObjectType):
        self.id = id
        self.name = name
        self.kind = kind
        self.type = type
        
    def to_dict(self):
        res = {}
        res['id'] = self.id
        res['name'] = self.name
        res['kind'] = self.kind.value
        res['type'] = str(self.type)
        return res
    
    def __str__(self):
        
        return f'VARIABLE {self.id}, {self.name}, {self.kind}, {self.type}'
    
        

class Variable_Table:

    def to_dict(self):
        res = []
        for entry in self.vars:
            res.append(entry.to_dict())
        return res


    def __init__(self):
        
        self.vars : List[VariableTableEntry] = []
        self.cur_id : int = 1
        
    def get_variables(self) -> List[VariableTableEntry]:
        return self.vars

    def add_variable(self, entry : VariableTableEntry):
        self.vars.append(entry)

    def __str__(self):
        return_str = ""
        for i in self.vars:
            return_str += f'{str(i)}\n'
        return return_str



class Variable_Declaration:

    def __init__(self, data_type_name : str, name : str):


        type_name_map = {'int' : decaf_typecheck.BaseType.INT, 'boolean' : decaf_typecheck.BaseType.BOOL, 'float' : decaf_typecheck.BaseType.FLOAT}

       
        self.name = name
        
        if data_type_name not in type_name_map:
            self.type = decaf_typecheck.ClassObjectType(data_type_name)
        else:
            self.type = type_name_map[data_type_name]

    def get_name(self):
        return self.name
    
    def type_check(self, ast, cur_class):
        
        
        
        if isinstance(self.type, decaf_typecheck.ClassObjectType):
            if ast.get_class_record(self.type.get_class_name()) == None:
                print(f"Error: class {self.type.get_class_name()} is not defined")
                return False
        
        return True

    def compute_type(self):
        return self.type
    
    def get_type(self):
        return self.type
    


#can have nested blocks
class Block_Stmt:
    
    def to_dict(self):
        res = []
        for statement in self.statements:
            res.append(statement.to_dict())
        return res

    def get_this_expressions_to_resolve(self) -> List:
        return self.this_expressions_to_resolve

    def type_check(self, ast, cur_class):
        
        for var_dec in self.var_declarations:
            if var_dec.type_check(ast, cur_class) == False:
                return False
        
        for statement in self.statements:
            if statement.type_check(ast, cur_class) == False:
                return False
        return True

    def get_var_names_to_resolve(self):
        
        return self.unresolved_locals

    def __init__(self, statements = []):

        self.statements = []
        self.var_declarations = []
        self.unresolved_locals = {}
        var_to_id = {}
        var_to_type = {}
        
        self.this_expressions_to_resolve = []
        
        for statement in statements:
            
            if isinstance(statement, list):
            
                for list_element in statement:
                    if isinstance(list_element, Variable_Declaration):
                        
                        if list_element.get_name() in var_to_id:
                            print(f'ERROR: reuse of name {list_element.get_name()}')
                            #sys.exit()
                
                        var_to_id[list_element.get_name()] = AST.get_new_variable_id()
                        var_to_type[list_element.get_name()] = list_element.get_type()

                        AST.add_local_var_cache(list_element.get_name(), var_to_id[list_element.get_name()], list_element.compute_type())
                        
                        self.var_declarations.append(list_element)

            elif isinstance(statement, Variable_Declaration):
                if statement.get_name() in var_to_id:
                    print(f'ERROR: reuse of name {statement.get_name()}')
                    #sys.exit()
                
                var_to_id[statement.get_name()] = AST.get_new_variable_id()
                var_to_type[statement.get_name()] = statement.get_type()

                AST.add_local_var_cache(statement.get_name(), var_to_id[statement.get_name()], statement.compute_type())
                
                self.var_declarations.append(statement)
                
                
                
            else:
               
                vars_to_resolve = statement.get_var_names_to_resolve()
                

                self.this_expressions_to_resolve.extend(statement.get_this_expressions_to_resolve())

                for var_name, var_object_array in vars_to_resolve.items():
                    if var_name in var_to_id:
                        for i in var_object_array:
                            i.set_id(var_to_id[var_name]) 
                            i.set_type(var_to_type[var_name])
                    else:
                        
                        if var_name in self.unresolved_locals:
                            self.unresolved_locals[var_name].extend(var_object_array)
                        else:
                             self.unresolved_locals[var_name] = var_object_array
                        
                        
                                          
                #self.statements.append(copy.deepcopy(statement))
                self.statements.append(statement)
    
    def get_statements_list(self) -> List:
        return self.statements

    def __str__(self):

        return_str = "Block(["

        for i in range(0, len(self.statements) - 1):
            return_str += str(self.statements[i]) + ','
        
        if len(self.statements) > 0:
            return_str += str(self.statements[-1]) 
            
        return_str += "])"

        return return_str

class If_Statement:
    
    def to_dict(self):
        res = {}
        res['type'] = 'if'
        res['condition'] = self.if_expression.to_dict()
        res['then_statement'] = self.then_statement.to_dict()
        res['else_statement'] = self.else_statement.to_dict()
        return res
  
    def get_this_expressions_to_resolve(self) -> List:
        return list(set(self.if_expression.get_this_expressions_to_resolve() + self.then_statement.get_this_expressions_to_resolve() + self.else_statement.get_this_expressions_to_resolve()))
  
    def __init__(self, if_expression, then_statement, else_statement):
       self.if_expression = if_expression
       self.then_statement = then_statement
       self.else_statement = else_statement


    def get_statements_list(self):
        return [self]

    def type_check(self, ast, cur_class):
        
        data_type = self.if_expression.compute_type(ast, cur_class)
        
        if data_type == decaf_typecheck.BaseType.ERROR:
            return False
        
        if data_type != decaf_typecheck.BaseType.BOOL:
            print_error_msg(f"If statement condition must be boolean. Got type {data_type} instead")
            return False

        if self.then_statement.type_check(ast, cur_class) == False:
            return False

        if self.else_statement.type_check(ast, cur_class) == False:
            return False

        return True

    def get_var_names_to_resolve(self):

        then_resolve_map = {}

        if self.then_statement != None:
            then_resolve_map = self.then_statement.get_var_names_to_resolve()

        else_resolve_map = {}

        if self.else_statement != None:
            else_resolve_map = self.else_statement.get_var_names_to_resolve()
            
        condition_resolve_map = {}
        
        condition_resolve_map = self.if_expression.get_var_names_to_resolve()
        

        return combine_resolve_maps(combine_resolve_maps(then_resolve_map, else_resolve_map),condition_resolve_map)
    
    def __str__(self):
       return f'If({self.if_expression},{self.then_statement},{self.else_statement})'

class While_Statement:

    def to_dict(self):
        res = {}
        res['type'] = 'while'
        res['condition'] = self.loop_condition.to_dict()
        res['body'] = self.loop_body.to_dict()
        return res

    def type_check(self, ast, cur_class):
            if self.loop_condition.compute_type(ast, cur_class) != decaf_typecheck.BaseType.BOOL:
                print("ERROR: while loop condition is not boolean")
                return False

            return self.loop_body.type_check(ast, cur_class)
        
    def get_this_expressions_to_resolve(self) -> List:
        return list(set(self.loop_condition.get_this_expressions_to_resolve() + self.loop_body.get_this_expressions_to_resolve()))        

    def get_var_names_to_resolve(self):
        res = combine_resolve_maps(self.loop_condition.get_var_names_to_resolve(), self.loop_body.get_var_names_to_resolve())
        
        return res
  
    def __init__(self, loop_condition, loop_body):
        self.loop_condition = loop_condition
        self.loop_body = loop_body
  
    def __str__(self):
        return f'While({self.loop_condition},{self.loop_body})'

class For_Statement:
    
    def to_dict(self):
        res = {}
        res['type'] = 'for'
        res['initialize_expression'] = self.initializer_expression.to_dict()
        res['loop_condition'] = self.loop_condition.to_dict()
        res['update_expression'] = self.update_expression.to_dict()
        res['body'] = self.loop_body.to_dict()
        return res

    def get_this_expressions_to_resolve(self) -> List:
        return list(set(self.initializer_expression.get_this_expressions_to_resolve() + self.loop_condition.get_this_expressions_to_resolve() + self.update_expression.get_this_expressions_to_resolve() + self.loop_body.get_this_expressions_to_resolve()))

    def type_check(self, ast, cur_class):
        if not isinstance(self.loop_condition, Skip_Statement) and self.loop_condition.compute_type(ast, cur_class) != decaf_typecheck.BaseType.BOOL:
            print("ERROR: for loop condition not boolean")
            return False

        res = self.loop_body.type_check(ast, cur_class) and self.initializer_expression.type_check(ast, cur_class) and self.update_expression.type_check(ast, cur_class)

       

        if res == False:
            print("ERROR: in for statement")

        return res


    def get_var_names_to_resolve(self):

        init_res = {}
        if self.initializer_expression != None:
            init_res = self.initializer_expression.get_var_names_to_resolve()

        init_loop_cond = {}
        if self.loop_condition != None:
            init_loop_cond = self.loop_condition.get_var_names_to_resolve()

        init_update = {}
        if self.update_expression != None:
            init_update = self.update_expression.get_var_names_to_resolve()

        body_res = {}
        if self.loop_body != None:
            body_res = self.loop_body.get_var_names_to_resolve()

        res =  combine_resolve_maps(combine_resolve_maps(init_res, init_loop_cond), combine_resolve_maps(init_update, body_res))

        
        return res

  
    def __init__(self, initializer_expression, loop_condition, update_expression, loop_body):
        self.initializer_expression = (initializer_expression)
        self.loop_condition = (loop_condition)
        self.update_expression = (update_expression)
        self.loop_body = (loop_body)

    def __str__(self):
        return f'For({self.initializer_expression},{self.loop_condition},{self.update_expression},{self.loop_body})'


class Expression_Statement:
    
    def to_dict(self):
        res = {}
        res['expression'] = self.expression.to_dict()
        return res
    
    def get_expression(self):
        return self.expression
    
    def type_check(self, ast, cur_class):
        
        if self.expression.compute_type(ast, cur_class) == decaf_typecheck.BaseType.ERROR:
            return False
        
        return True
    
    def get_var_names_to_resolve(self):
        return self.expression.get_var_names_to_resolve()
    
    def get_this_expressions_to_resolve(self):
        return self.expression.get_this_expressions_to_resolve()
  
    def __init__(self, expression):
       
       self.expression = (expression)


    def __str__(self):
       return f'Expr-stmt({self.expression})'

class Break_Statement:
    
    def to_dict(self):
        res = {}
        res['type'] = 'break'
        return res
  
    def get_var_names_to_resolve(self):
        return {}
    
    def type_check(self, ast, cur_class):
        return True
    
    def get_this_expressions_to_resolve(self):
        return []
  
    def __init__(self):
        pass


    def __str__(self):
       return f'Break'

class Continue_Statement:
    
    def to_dict(self):
        res = {}
        res['type'] = 'continue'
        return res
    
    def type_check(self, ast, cur_class):
        return True
    
    def get_var_names_to_resolve(self):
        return {}
    
    def get_this_expressions_to_resolve(self):
        return []

    def __init__(self):
       pass


    def __str__(self):
       return f'Continue'

class Skip_Statement:
    
    
    def to_dict(self):
        res = {}
        res['type'] = 'skip'
        return res
    
    def compute_type(self, ast, cur_class):
        return 'void'
    
    
    def get_this_expressions_to_resolve(self):
        return []
    
    def get_var_names_to_resolve(self):
        return {}
  
    def __init__(self):
        pass
  
    def type_check(self, ast, cur_class):
        return True
  
    def __str__(self):
        return f'Skip'    

class Assign_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'assign'
        res['lhs'] = self.left_hand_side.to_dict()
        res['rhs'] = self.right_hand_side.to_dict()
        res['data_type'] = str(self.type)
        return res
        
    
    def get_this_expressions_to_resolve(self) -> List:
        return list(set(self.left_hand_side.get_this_expressions_to_resolve() + self.right_hand_side.get_this_expressions_to_resolve()))

    def get_type(self):
        return self.type

    def compute_type(self, ast, cur_class):
        
        if self.left_hand_side.compute_type(ast, cur_class) == decaf_typecheck.BaseType.ERROR or self.right_hand_side.compute_type(ast, cur_class) == decaf_typecheck.BaseType.ERROR:
            
            self.type = decaf_typecheck.BaseType.ERROR
            return self.type
            
            
        if not decaf_typecheck.is_subtype(self.right_hand_side.get_type(), self.left_hand_side.get_type(), ast):
            self.type = decaf_typecheck.BaseType.ERROR
           
            print_error_msg("RHS of = operator must be a subtye of LHS")
            
            return self.type
            
        self.type = self.right_hand_side.get_type()
        
        return self.type
        

    def get_var_names_to_resolve(self):
        return combine_resolve_maps(self.left_hand_side.get_var_names_to_resolve(), self.right_hand_side.get_var_names_to_resolve())


    def __init__(self, left_hand_side, right_hand_side):
        self.left_hand_side = left_hand_side
        self.right_hand_side = right_hand_side

    def __str__(self):
        return f'Expr(Assign({self.left_hand_side},{self.right_hand_side}, {self.left_hand_side.get_type()}, {self.right_hand_side.get_type()}))'

class Field_Access_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'field_access'
        res['base_expression'] = self.base_expression.to_dict()
        res['field_name'] = self.field_name
        res['field_id'] = self.id_of_field
        res['data_type'] = str(self.type)
        return res

    def get_type(self):
        return self.type

    
    def compute_type(self, ast, cur_class): 
        
        
        
        if isinstance(self.base_expression, Variable_Reference):
            
            if self.base_expression.id == False:
                rec = ast.get_class_record(self.base_expression.var_name)
                
                if rec == None:
                    self.type = decaf_typecheck.BaseType.ERROR
                    print("ERROR: could not resoleve type name")
                    raise Exception(f"Could not find class record: {self.base_expression.var_name}")
                    return self.type
                else:
                    self.base_expression = Class_Reference_Expression(self.base_expression.var_name)
        
        
        type_val : str = self.base_expression.compute_type(ast, cur_class)
        
        if isinstance(type_val, decaf_typecheck.ClassObjectType):
            
            field_class_name = type_val.get_class_name()
              
            self.id_of_field = ast.compute_id_from_field(field_class_name, self.field_name)
            
            self.type = ast.compute_type_from_field(field_class_name, self.field_name)
                
        elif isinstance(type_val, decaf_typecheck.ClassLiteralType):
                
            field_class_name = type_val.get_class_name()
            
            self.type = ast.compute_type_from_field(field_class_name, self.field_name)
            self.id_of_field = ast.compute_id_from_field(field_class_name, self.field_name)
            
        else:
            raise Exception(f"not implemented yet: {type(type_val)} - {self.base_expression}")
        
        return self.type
        
    def get_this_expressions_to_resolve(self):
        return self.base_expression.get_this_expressions_to_resolve()

    def get_var_names_to_resolve(self):
        return self.base_expression.get_var_names_to_resolve()

    def get_base_expression(self):
        return self.base_expression

    def get_field_name(self):
        return self.field_name

    def __init__(self, base_expression, field_name):
        self.base_expression = base_expression
        self.field_name = field_name
        self.type = None 
        


    #Field-access(This, x)
    def __str__(self):
        return f'Field-access({self.base_expression}, {self.field_name}, {self.id_of_field})'





class Binary_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'binary'
        res['lhs'] = self.left_expr.to_dict()
        res['rhs'] = self.right_expr.to_dict()
        res['data_type'] = str(self.type)
        return res
    
    def get_this_expressions_to_resolve(self) -> List:
        return list(set(self.left_expr.get_this_expressions_to_resolve() + self.right_expr.get_this_expressions_to_resolve()))

    def compute_type(self, ast, cur_class):

        if self.operation in [Operation.ADD, Operation.SUBTRACT ,Operation.MULTIPLY, Operation.DIVIDE]:
            if self.left_expr.compute_type(ast, cur_class) == decaf_typecheck.BaseType.INT and self.right_expr.compute_type(ast, cur_class) == decaf_typecheck.BaseType.INT:
                self.type = decaf_typecheck.BaseType.INT
                return self.type

            a = [decaf_typecheck.BaseType.INT, decaf_typecheck.BaseType.FLOAT]
            if self.left_expr.compute_type(ast, cur_class) in a and self.right_expr.compute_type(ast, cur_class) in a:
                self.type = decaf_typecheck.BaseType.FLOAT
                return self.type
                        
            print_error_msg("Arithmetic operations must happen on number")
                        
            self.type = decaf_typecheck.BaseType.ERROR
            return self.type 

        if self.operation in  [Operation.LESSTHAN, Operation.LESSOREQUAL, Operation.GREATERTHAN, Operation.GREATEROREQUAL]:
            a = [decaf_typecheck.BaseType.INT, decaf_typecheck.BaseType.FLOAT]
            if self.left_expr.compute_type(ast, cur_class) not in a or self.right_expr.compute_type(ast, cur_class) not in a:
                print_error_msg("Arithmetic comparisons must happen on number")
                
                self.type = decaf_typecheck.BaseType.ERROR
                return self.type
            self.type = decaf_typecheck.BaseType.BOOL
            return self.type

        if self.operation in [Operation.AND, Operation.OR]:
            if self.left_expr.compute_type(ast, cur_class) == decaf_typecheck.BaseType.BOOL and self.right_expr.compute_type(ast, cur_class) == decaf_typecheck.BaseType.BOOL:
                self.type = decaf_typecheck.BaseType.BOOL
                return self.type
            print_error_msg("Logical comparisons must happen on boolean")
            self.type = decaf_typecheck.BaseType.ERROR
            return self.type
        
        if self.operation in [Operation.EQUALS, Operation.NOTEQUALS]:
            if self.left_expr.compute_type(ast, cur_class) == self.right_expr.compute_type(ast, cur_class):
                self.type = decaf_typecheck.BaseType.BOOL
                return self.type
               
            self.type = decaf_typecheck.BaseType.BOOL
            return self.type
        
        raise Exception("not implemented")

        

    def get_type(self):
        return self.type

    def get_var_names_to_resolve(self):
        res = combine_resolve_maps(self.left_expr.get_var_names_to_resolve(), self.right_expr.get_var_names_to_resolve())
        
        return res

    def __init__(self, operation, left_expr, right_expr):
        self.operation = operation
        self.left_expr = left_expr
        self.right_expr = right_expr

    def __str__(self):
        return f'Binary({self.operation}, {self.left_expr}, {self.right_expr})'

class Unary_Expression:

    def get_type(self):
        return self.type

    def compute_type(self, ast, cur_class):

        if self.operation == 'uminus':
            if self.expression.compute_type(ast, cur_class) in [decaf_typecheck.BaseType.INT, decaf_typecheck.BaseType.FLOAT]:
                self.type = self.expression.compute_type(ast, cur_class)
                return self.expression.compute_type(ast, cur_class)
        else:
            if self.expression.compute_type(ast, cur_class) == decaf_typecheck.BaseType.BOOL:
                self.type = decaf_typecheck.BaseType.BOOL
                return self.type

        self.type = decaf_typecheck.BaseType.ERROR
        return self.type
    
    def get_this_expressions_to_resolve(self):
        return self.expression.get_this_expressions_to_resolve()

    def get_var_names_to_resolve(self):
        return self.expression.get_var_names_to_resolve()

    def __init__(self, operation, expression):
        self.operation = operation
        self.expression = expression

    def __str__(self):
        return f'Urnary({self.operation}, {self.expression})'
 


class Constant_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'constant'
        res['val'] = self.val
        res['data_type'] = str(self.type)
        return res
    
    def get_this_expressions_to_resolve(self) -> List:
        return []

    def get_var_names_to_resolve(self):
        return {}
    
    def get_type(self):
        return self.type

    def compute_type(self, ast, class_name):
        return self.type

    def __init__(self, val, data_type):
        self.val = val
        self.type = data_type

    def __str__(self):

        if self.type == decaf_typecheck.BaseType.INT:
            return f'Constant(Integer-constant({self.val}))'
        elif self.type == decaf_typecheck.BaseType.BOOL:
            return f'Constant(Boolean-constant({self.val}))'
        
        return f'Constant({self.val})'

class This_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'this'
        return res
    
    def get_var_names_to_resolve(self):
        return {}
    
    def get_this_expressions_to_resolve(self):
        return [self]
    
    def __init__(self):
        self.type = None #user(A) - whera A is the current class
    
    def compute_type(self, ast, cur_class):
        return self.type
    
    def get_type(self):
        return self.type
    
    def set_type(self, type_name):
        self.type = type_name
    
    def __str__(self):
        return f'This'

class Super_Expression:
    
    def __init__(self):
        pass

    def __str__(self):
        return 'Super'



class Return_Statement:
    
    def to_dict(self):
        res = {}
        res['type'] = 'return'
        res['expression'] = self.expression.to_dict()
        return res
    
    
    def get_statements_list(self):
        return [ self ]
    
    
    def get_this_expressions_to_resolve(self) -> List:
        if self.expression == None:
            return []
        return self.expression.get_this_expressions_to_resolve()

    def type_check(self, ast, cur_class):
        
        if self.expression.compute_type(ast, cur_class) == decaf_typecheck.BaseType.ERROR:
            return False
    
        return True

    def get_var_names_to_resolve(self):
        if self.expression == None:
            return {}
        return self.expression.get_var_names_to_resolve()

    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return f'Return({self.expression})'
    
class Constructor_Record:
    
    def to_dict(self):
        res = {}
        res['id'] = self.id
        res['visibility'] = self.visibility
        res['parameters'] = self.params
        res['variables'] = self.variable_table.to_dict()
        res['body'] = self.body.to_dict()
        return res
    
    def type_check(self, ast, class_name):
        return self.body.type_check(ast, class_name)

    def get_this_expressions_to_resolve(self) -> List[This_Expression]:
        return self.this_expressions_to_resolve

    def get_variable_table(self) -> Variable_Table:
        return self.variable_table

    def get_num_params(self) -> int:
        return len(self.params)
    
    def get_constructor_body(self) -> Block_Stmt:
        return self.body

    #body is a block -assume for now that is contains no other block
    def __init__(self, id, visibility, parameters, body):
        self.id = AST.get_new_constructor_id()
        self.visibility = visibility
        self.params = []
        self.body = body
        self.variable_table = Variable_Table()
        self.this_expressions_to_resolve : List = body.get_this_expressions_to_resolve()

        self.compute_parameters_and_var_table(parameters, body)

    def compute_parameters_and_var_table(self, params, body):

        local_var_cache = AST.get_local_var_cache()

        params_to_id = {}
        params_to_type = {}
        
        for param in params:
            params_to_id[param[1]] = AST.get_new_variable_id()
            
        
            
            type_name_map = {'int' : decaf_typecheck.BaseType.INT, 'boolean' : decaf_typecheck.BaseType.BOOL, 'float' : decaf_typecheck.BaseType.FLOAT}
            
            if param[0] in type_name_map:
                params_to_type[param[1]] = type_name_map[param[0]]
            else:
                params_to_type[param[1]] = decaf_typecheck.ClassObjectType(param[0])
            
      

        for var_name, var_object_array in body.get_var_names_to_resolve().items():
            if var_name in params_to_id:
                for i in var_object_array:
                
                    i.set_id(params_to_id[var_name])
                    i.set_type(params_to_type[var_name])
                

        for i in params:
            #self.variable_table.add_variable(params_to_id[i[1]],i[1], 'formal', i[0])
            self.variable_table.add_variable(VariableTableEntry(params_to_id[i[1]],i[1], 'formal', i[0]))
            self.params.append(params_to_id[i[1]])

        for i in local_var_cache:
            self.variable_table.add_variable(i[1],i[0], 'local', i[2])

        AST.clear_local_var_cache()

            

        
    

      


    def __str__(self):
        return_str = f'CONSTRUCTOR: {self.id}, {self.visibility}\n' + f'Constructor parameters: {(", ".join(map(str, self.params))) }\n' + f'Variable Table:\n' + str(self.variable_table) + f'Constructor Body:\n{self.body}'

        return return_str

    

class Method_Record:
    
    def to_dict(self):
        res = {}
        res['id'] = self.id
        res['visibility'] = self.visibility
        res['parameters'] = self.params
        res['variables'] = self.variable_table.to_dict()
        res['body'] = self.body.to_dict()
        return res

    def get_this_expressions_to_resolve(self) -> List[This_Expression]:
        return self.this_expressions_to_resolve

    def set_containing_class(self, class_name):
        self.containing_class = class_name

    def type_check(self, ast, cur_class):

        return self.body.type_check(ast, cur_class)
        
           

    
    def __init__(self, name, id, containing_class, visibility, applicability, parameters, return_type, body):

        self.name = name
        self.id = AST.get_new_method_id()
        self.containing_class = containing_class
        self.visibility = visibility
        self.applicability = applicability
        
        
        
        type_name_map = {'int' : decaf_typecheck.BaseType.INT, 'boolean' : decaf_typecheck.BaseType.BOOL, 'float' : decaf_typecheck.BaseType.FLOAT, 'void' : decaf_typecheck.BaseType.VOID}
        
        
        
        if return_type in type_name_map:
            self.return_type = type_name_map[return_type]
        else:
            self.return_type = decaf_typecheck.ClassObjectType(return_type)
        
        #self.return_type = return_type
        self.body = body
        self.params = []
        self.this_expressions_to_resolve = body.get_this_expressions_to_resolve()

        self.variable_table = Variable_Table()

        self.compute_parameters_and_var_table(parameters, body)
        
    def get_id(self):
        return self.id
        
    def get_return_type(self):
        return self.return_type    
    
    def get_method_body(self) -> Block_Stmt:
        return self.body
        
    def get_variable_table(self) -> Variable_Table:
        return self.variable_table
    
    def get_param_count(self) -> int:
        return len(self.params)

    def compute_parameters_and_var_table(self, params, body):

        local_var_cache = AST.get_local_var_cache()

        params_to_id = {}
        params_to_type = {}
        for param in params:
            
            params_to_id[param[1]] = AST.get_new_variable_id()
            
            type_name_map = {'int' : decaf_typecheck.BaseType.INT, 'boolean' : decaf_typecheck.BaseType.BOOL, 'float' : decaf_typecheck.BaseType.FLOAT}
            
            if param[0] in type_name_map:
                params_to_type[param[1]] = type_name_map[param[0]]
            else:
                params_to_type[param[1]] = decaf_typecheck.ClassObjectType(param[0])
            

        for var_name, var_object_array in body.get_var_names_to_resolve().items():
            if var_name in params_to_id:
                for i in var_object_array:
                    i.set_id(params_to_id[var_name])
                    i.set_type(params_to_type[var_name])
                

        for i in params:
            self.variable_table.add_variable(VariableTableEntry(params_to_id[i[1]], i[1], LocalVariableKind.FORMAL, i[0]))
            self.params.append(params_to_id[i[1]])

        for i in local_var_cache:
            self.variable_table.add_variable(VariableTableEntry(i[1],i[0], LocalVariableKind.LOCAL, i[2]))

        AST.clear_local_var_cache()

        

    def __str__(self):
        
        return_str = f'METHOD: {self.id}, {self.name}, {self.containing_class}, {self.visibility}, {self.applicability}, {self.return_type}\n' +  f'Method parameters: {(", ".join(map(str, self.params))) }\n' + f'Variable Table:\n' + str(self.variable_table)+ f'Method Body:\n{self.body}'

        return return_str
        
        
class Class_Record:


    def to_dict(self):
        res = {}
        res['superclass'] = self.super_class_name
        res['fields'] = [x.to_dict() for x in self.fields]
        res['constructors'] = [x.to_dict() for x in self.constructors]
        res['methods'] = [x.to_dict() for x in self.methods]
        return res

    def get_field_id_from_name(self, field_name : str) -> Optional[int]:
        for field in self.fields:
            if field.name == field_name:
                return field.id
        return None
        
    def get_field_from_name(self, field_name : str):
        for field in self.fields:
            if field.name == field_name:
                return field
            
        return None


    def get_name(self):
        return self.class_name
    
    def get_method_from_name(self, method_name : str):
        
        for record in self.methods:
            if record.name == method_name:
                return record
                
        return None
    
    def get_constructor(self):
        if len(self.constructors) == 0:
            return None
        
        return self.constructors[0]
    
    def get_constructor_record(self, id : int) -> Optional[Constructor_Record]:
        for constructor in self.constructors:
            if constructor.id == id:
                return constructor
        return None
    
    #can find constructors and methods - -1 if not found
    def get_id_from_method_name(self, method_name : str) -> Optional[int]:
        
        if method_name == self.class_name and len(self.constructors) > 0:
            return self.constructors[0].id
        
        for method in self.methods:
            if method_name == method.name:
                return method.id
            
        return None

    def __init__(self, class_name):
        pass
    
    def get_method_records(self) -> List[Method_Record]:
        return self.methods
    
    def get_instance_field_count(self) -> int:
        return self.instance_field_count
    
    def get_super_class_name(self) -> Optional[str]:
        return self.super_class_name

    def __init__(self, class_name, super_class_name, class_body_elements):
        self.class_name = class_name
        self.super_class_name = super_class_name
        self.constructors : List[Constructor_Record] = []
        self.fields : List[Field_Record] = []
        self.methods : List[Method_Record] = []
        self.instance_field_count = 0
        self.create_class_data(class_body_elements)
        
    def type_check(self, ast):
        
        for constructor in self.constructors:
            if constructor.type_check(ast, self.class_name) == False:
                return False
        
        for method in self.methods:
            if method.type_check(ast, self.class_name) == False:
                return False
        return True

    def create_class_data(self, class_body_elements):

        for element in class_body_elements:
            
            if isinstance(element, list):
                
                for list_element in element:
                    if isinstance(list_element, Field_Record):
                        list_element.set_containing_class(self.class_name)

                        for i in self.fields:
                        
                            if i.get_name() == list_element.get_name():
                                print(f'ERROR: repeating field name {i.get_name()}')
                                #sys.exit()

                        self.fields.append(list_element)
                        if list_element.applicability == 'instance':
                            self.instance_field_count += 1
                
                
            
            if isinstance(element, Constructor_Record):
                self.constructors.append(element)
                
                
                this_expressions = element.get_this_expressions_to_resolve()
                for this_expr in this_expressions:
                    this_expr.set_type(decaf_typecheck.ClassObjectType(self.class_name))

            if isinstance(element, Field_Record):
                element.set_containing_class(self.class_name)

                for i in self.fields:
                    
                    if i.get_name() == element.get_name():
                        print(f'ERROR: repeating field name {i.get_name()}')
                        #sys.exit()

                self.fields.append(element)
                if element.applicability == 'instance':
                    self.instance_field_count += 1

            if isinstance(element, Method_Record):
                element.set_containing_class(self.class_name)
                self.methods.append(element)
                
                this_expressions = element.get_this_expressions_to_resolve()
                for this_expr in this_expressions:
                    this_expr.set_type(decaf_typecheck.ClassObjectType(self.class_name))



    def __str__(self):
        return_str = f'- Class Name: {self.class_name}\nSuperclass Name: '
        
        if self.super_class_name != None:
            return_str += self.super_class_name

        return_str += '\n'

        

        return_str += 'Fields:\n'

        for i in self.fields:
            return_str += str(i) + '\n'

        return_str += 'Constructors:\n'

        for i in self.constructors:
            return_str += str(i) + '\n'

        return_str += 'Methods:\n'

        for i in self.methods:
            return_str += str(i) + '\n'

        return return_str
        


class Field_Record:

    def to_dict(self):
        res = {}
        res['name'] = self.name
        res['id'] = self.id
        res['visibility'] = self.visibility
        res['applicability'] = self.applicability
        return res

    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.data_type

    def set_containing_class(self, class_name):
        self.containing_class = class_name
        
    def compute_type(self):
        return self.data_type

    def __init__(self, name, id, containing_class, visibility, applicability, data_type):
        self.name = name
        self.id = AST.get_new_field_id()
        self.containing_class = containing_class
        self.visibility = visibility
        self.applicability = applicability
        
        type_name_map = {'int' : decaf_typecheck.BaseType.INT, 'boolean' : decaf_typecheck.BaseType.BOOL, 'float' : decaf_typecheck.BaseType.FLOAT}
        
        
        #if data_type in type_name_map:
        #    self.data_type = type_name_map[data_type]
        #else:
        #    print(f'not: |{data_type}| {data_type == "int" } {type(data_type)}')
        #    self.data_type = decaf_typecheck.ClassObjectType(data_type)
        
        self.data_type = data_type
        

    def __str__(self):
        return f'FIELD {self.id}, {self.name}, {self.containing_class}, {self.visibility}, {self.applicability}, {self.data_type}'

class New_Object_Expression:

    def compute_type(self, ast, cur_class : str):
        
        class_record : Class_Record =  ast.get_class_record(self.class_name)
        constructor = class_record.get_constructor()
        
        if constructor.visibility == 'private':
            if cur_class == self.class_name:
                self.type = decaf_typecheck.ClassObjectType(self.class_name)
            else:
                self.type = decaf_typecheck.BaseType.ERROR
                
        else:
            self.type = decaf_typecheck.ClassObjectType(self.class_name)
            
        return self.type
    
    def get_type(self):
        return self.type


    def get_this_expressions_to_resolve(self) -> List:
        
        res = []
        
        for arg in self.arguments:
            res.extend(arg.get_this_expressions_to_resolve())
        
        return res

    def get_var_names_to_resolve(self):
        
        res = {}
        
        for arg in self.arguments:
            res = combine_resolve_maps(res, arg.get_var_names_to_resolve())
        
        return res

    def __init__(self, class_name, arguments):
        self.class_name = class_name
        self.arguments = arguments  

    def __str__(self):
        args = ", ".join(map(str, self.arguments))
        return f'New-object({self.class_name}, [{args}])'

class Method_Call_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'method_call'
        res['method_name'] = self.method_name
        res['method_id'] = self.method_id
        res['base_expression'] = self.base_expression.to_dict()
        res['arguments'] = [x.to_dict() for x in self.arguments] 
        res['data_type'] = str(self.type)
        return res
    
    def get_type(self):
        return self.type

    def get_this_expressions_to_resolve(self):
        
        combined = []
        
        for i in self.arguments:
            combined.extend(i.get_this_expressions_to_resolve())
            
        combined.extend(self.base_expression.get_this_expressions_to_resolve())
        
        return list(set(combined))

    

    def compute_type(self, ast, cur_class):
        
        
        if isinstance(self.base_expression, Variable_Reference):        
            if self.base_expression.id == None:
                
                rec = ast.get_class_record(self.base_expression.var_name)
                
                if rec == None:
                    self.type = decaf_typecheck.BaseType.ERROR
                    print_error_msg(f"{self.base_expression.var} is not a class name")
                    return self.type
                else:
                    #replace it
                    self.base_expression = Class_Reference_Expression(self.base_expression.var_name)
                
             
        
        if isinstance(self.base_expression, Class_Reference_Expression):
            class_record = ast.get_class_record(self.base_expression.class_name)
        else:
            base_type = self.base_expression.compute_type(ast, cur_class)
        
            if isinstance(base_type, decaf_typecheck.ClassObjectType):
            
                class_record = ast.get_class_record(base_type.get_class_name())
            else:
                raise Exception(f"Not implemented yet: {base_type} type: {type(base_type)} : {self.base_expression}")
        
        
        
        method_record =  class_record.get_method_from_name(self.method_name)
        
        
        
        if method_record == None:
            
            if class_record.super_class_name != None:
                super_class_record = ast.get_class_record(class_record.super_class_name)
                
                method_record = super_class_record.get_method_from_name(self.method_name)
            
                if method_record == None:
            
                    print_error_msg("ERROR method does not exist")
                    self.type = decaf_typecheck.BaseType.ERROR
                    return self.type
            else:
                self.type = decaf_typecheck.BaseType.ERROR
                return self.type
            
        if method_record.get_param_count() != len(self.arguments):
            print("not correct number of args")
            self.type = decaf_typecheck.BaseType.ERROR
            
        self.type = method_record.get_return_type()
        
        
        
        if self.type not in [decaf_typecheck.BaseType.INT, decaf_typecheck.BaseType.BOOL, decaf_typecheck.BaseType.FLOAT]:
            self.type = decaf_typecheck.ClassObjectType(self.type)
            
        
        
        self.method_id = method_record.get_id()
        
        for arg in self.arguments:
            if arg.compute_type(ast, cur_class) == False:
                print("Error with finding types of args to method call")
                self.type == decaf_typecheck.BaseType.ERROR
        
       
        return self.type

    def get_var_names_to_resolve(self):
        
        res = self.base_expression.get_var_names_to_resolve()
        
        for arg in self.arguments:
            res = combine_resolve_maps(res, arg.get_var_names_to_resolve())
        
        
        return res

    def __init__(self, base_expression, method_name, arguments):
        self.base_expression = base_expression
        self.method_name = method_name
        self.arguments = arguments
        

    def __str__(self):
        args = ", ".join(map(str, self.arguments))
        return f'Method-call({self.base_expression}, {self.method_name}, [{args}], {self.method_id})'

class Auto_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'auto'
        res['expression'] = self.operand_expression.to_dict()
        res['op_type'] = self.inc_dec
        res['op_kind'] = self.post_pre
        res['data_type'] = str(self.type)
        
        return res
    
    def compute_type(self, ast, cur_class):
        
        expr_type = self.operand_expression.compute_type(ast, cur_class)
        
        if expr_type not in [decaf_typecheck.BaseType.INT, decaf_typecheck.BaseType.FLOAT]:
            self.type = decaf_typecheck.BaseType.ERROR
            return self.type

        self.type = expr_type
        return  self.type
            
    
    def get_type(self):
        return self.type
        
    
    def get_this_expressions_to_resolve(self) -> List:
        return self.operand_expression.get_this_expressions_to_resolve()

    def get_var_names_to_resolve(self):
        return self.operand_expression.get_var_names_to_resolve()

    def __init__(self, operand_expression, inc_dec, post_pre):
        self.operand_expression = operand_expression
        self.inc_dec = inc_dec
        self.post_pre = post_pre

    def __str__(self):
        return f'Auto({self.operand_expression}, {self.inc_dec}, {self.post_pre})'
    
class Class_Reference_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'class_reference'
        res['data_type'] = str(self.type)
        return res
    
    def compute_type(self, ast, cur_class):
        return self.type
    
    def get_type(self):
        return self.type
    
    def __init__(self, class_name : str):
        self.class_name = class_name
        self.type = decaf_typecheck.ClassLiteralType(class_name)
        
    def __str__(self):
        return f'class-literal({self.class_name})'

class Variable_Reference:
    
    def to_dict(self):
        res = {}
        res['type'] = 'variable_reference'
        res['variable'] = self.var_name
        res['data_type'] = str(self.type)
        res['id'] = self.id
        return res

    def get_this_expressions_to_resolve(self) -> List:
        return []

    def __init__(self, var_name : str):
        self.var_name : str = var_name
        self.id : Optional[int] = None
        self.type : Optional[int] = None
        
    def get_var_name(self):
        return self.var_name
        
    def compute_type(self, ast, cur_class):
        
        return self.type
    
    def get_type(self):
        
        return self.type
    
    def set_id(self, id : int):
        self.id = id

    def set_type(self, data_type : decaf_typecheck.BaseType | decaf_typecheck.ClassObjectType):
        self.type = data_type
       
    def get_var_name(self) -> str:
        return self.var_name
     

    def get_var_names_to_resolve(self):
        res = {}
        t = []
        t.append(self)
        res[self.var_name] = t
        return res
        
    def __str__(self):
        return f'Variable({self.id}, {self.var_name})'


class WriteStatement:
    
    def to_dict(self):
        res = {}
        res['type'] = 'syscall'
        res['call'] = 'write'
        res['data'] = self.data.to_dict()
        return res
    
    def get_var_names_to_resolve(self):
        return self.data.get_var_names_to_resolve()
    
    def get_this_expressions_to_resolve(self):
        return []
    
    def type_check(self, ast, cur_class):
        return True
    
    
    #Currently, data will always be a VariableReference becasuse write statement is only used inside print function
    def __init__(self, data):
        self.data = data
        
    def __str__(self):
        return f'_write({self.data})'


class AST:

    def to_dict(self):
        res = {}
        res['classes'] = {}
        for class_name, class_record in self.class_records.items():
            res['classes'][class_name] = class_record.to_dict()
        return res

    cur_constructor_id = 1
    cur_field_id = 1
    cur_method_id = 1
    cur_variable_id = 1

    cur_local_var_cache = []

    @staticmethod
    def get_new_constructor_id():
        return_val = AST.cur_constructor_id
        AST.cur_constructor_id += 1
        return return_val

    @staticmethod
    def get_new_field_id():
        return_val = AST.cur_field_id
        AST.cur_field_id += 1
        return return_val

    @staticmethod
    def get_new_method_id():
        return_val = AST.cur_method_id
        AST.cur_method_id += 1
        return return_val
    
    @staticmethod
    def get_new_variable_id():
        return_val = AST.cur_variable_id
        AST.cur_variable_id += 1
        return return_val

    @staticmethod
    def add_local_var_cache(name, id, data_type):
        AST.cur_local_var_cache.append((name, id, data_type))

    @staticmethod
    def get_local_var_cache():
        return AST.cur_local_var_cache

    @staticmethod
    def clear_local_var_cache():
        AST.cur_local_var_cache = []
        
    def is_subclass(self, subclass_name : str, class_name : str) -> bool:
        
        if subclass_name == class_name:
            return True
        
        cur_class_record = self.class_records[subclass_name]
        
        while cur_class_record.get_super_class_name() != None:
            
            if cur_class_record.get_super_class_name() == class_name:
                return True
            
            cur_class_record = self.class_records[cur_class_record.get_super_class_name()]
            
        
        return False 
    
    
    def compute_id_from_field(self, field_class_name, field_name) -> Optional[int]:
        
        class_record = self.get_class_record(field_class_name)
        
        if class_record == None:
            return None
        
        field = class_record.get_field_from_name(field_name)
        
        if field == None:
            
            super_class_record = self.get_class_record(class_record.super_class_name)
            
            if super_class_record == None:
                return None
            
            field = super_class_record.get_field_from_name(field_name)
            
            if field == None:
                return None
            
            return field.id
        
        return field.id
           
        
    def compute_type_from_field(self, class_name : str, field_name : str):
        class_record = self.get_class_record(class_name)
        
        if class_record == None:
            print("ERROR: field not found in class")
            return decaf_typecheck.BaseType.ERROR
        
        field = class_record.get_field_from_name(field_name)
        
        if field == None:
            
            super_class_record = self.get_class_record(class_record.super_class_name)
            
            if super_class_record == None:
                return decaf_typecheck.BaseType.ERROR
            
            field = super_class_record.get_field_from_name(field_name)
            
            if field == None:
                return decaf_typecheck.BaseType.ERROR
            
            
            return field.get_type()
            
            
            
        
        return field.get_type()
    
    #do not check for private vs not private yet - return 
    def can_access_field(self, using_class_name : str, field_name : str, field_class_name : str) -> Optional[int]:
        class_record = self.get_class_record(field_class_name)
        
        if class_record == None:
            print("ERROR: field not found in class")
            return None
        
        field_id = class_record.get_field_id_from_name(field_name)
        
        if field_id == None:
            print("ERROR: not found TODO")
            return None
        
        return field_id
        

    def type_check(self):
        #type check each class
        for c, record in self.class_records.items():
            if record.type_check(self) == False:
                return False
        return True
    
    def get_class_record(self, class_name : str) -> Optional[Class_Record]:
        
        return self.class_records.get(class_name)
        
    

    def get_class_records(self) -> List[Class_Record]:
        return list(self.class_records.values())

    def __init__(self):
        self.class_records : Dict[str, Class_Record] = {}
        self.create_standard_objects()
        

    def add_class_record(self, class_record : Class_Record):

        if class_record.class_name in self.class_records:
            print(f'ERROR: Repeated class name "{i.get_name()}"')
            #sys.exit()

        self.class_records[class_record.class_name] = class_record
                

    

    def create_standard_objects(self):
        
        #scan_int_method = Method_Record("scan_int", -1, "In", "public", "static", [], "int", Block_Stmt())
        #scan_float_method = Method_Record("scan_float", -1, "In", "public", "static", [], "float", Block_Stmt())
        
        #in_class = Class_Record("In", None, [scan_int_method, scan_float_method])
        
        #print_f = Method_Record("print", -1, "Out", "public", "static", [["float", "f"]], "void", Block_Stmt())
        print_i = Method_Record("print", -1, "Out", "public", "static", [["int", "i"]], "void", Block_Stmt([WriteStatement(Variable_Reference("i"))]))
        #print_b = Method_Record("print", -1, "Out", "public", "static", [["boolean", "b"]], "void", Block_Stmt())
        #print_s = Method_Record("print", -1, "Out", "public", "static", [["string", "s"]], "void", Block_Stmt())
        
        out_class = Class_Record("Out", None, [print_i])
        
        #self.add_class_record(in_class)
        self.add_class_record(out_class)
        
        pass


    def __str__(self):

        line = "-------------------------------------------"

        return_str = ''

        for i, record in self.class_records.items():
            return_str += line + '\n'
            return_str += str(record) + '\n'

        return_str += line
        return return_str

