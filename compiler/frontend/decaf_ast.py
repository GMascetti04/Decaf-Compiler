import sys
import frontend.decaf_typecheck as decaf_typecheck
from typing import List, Tuple, Optional, Dict
from enum import Enum
from abc import ABC, abstractmethod




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

def print_error_msg(msg):
    red_text = '\033[91m'
    white_text = '\033[0m'

    print(f"{red_text}Error: {msg}{white_text}", file=sys.stderr)


        

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
        res['kind'] = str(self.kind)
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

    def to_dict(self):
        res = {}
        res['type'] = str(self.type)
        res['name'] = self.name
        return res


    def __init__(self, data_type_name : str, name : str):


        type_name_map = {'int' : decaf_typecheck.BaseType.INT, 'boolean' : decaf_typecheck.BaseType.BOOL, 'float' : decaf_typecheck.BaseType.FLOAT}

       
        self.name = name
        
        if data_type_name not in type_name_map:
            self.type = decaf_typecheck.ClassObjectType(data_type_name)
        else:
            self.type = type_name_map[data_type_name]

    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.type
    
    def __str__(self):
        return f'Var-Dec({self.name}, {self.type})'
    
class ASTVisitor(ABC):
    @abstractmethod
    def visit_block_statement(self, block_stmnt):
        pass
    
    @abstractmethod
    def visit_write_statement(self, write_stmnt):
        pass
    
    @abstractmethod
    def visit_if_statement(self, if_stmnt):
        pass
    
    @abstractmethod
    def visit_expression_statement(self, expr_stmnt):
        pass
    
    @abstractmethod
    def visit_for_statement(self, for_stmnt):
        pass
    
    @abstractmethod
    def visit_return_statement(self, ret_stmnt):
        pass 
    
    @abstractmethod
    def visit_variable_reference_expression(self, var_ref_exp):
        pass 
    
    @abstractmethod
    def visit_binary_expression(self, bin_expr):
        pass
    
    @abstractmethod
    def visit_constant_expression(self, const_expr):
        pass
    
    @abstractmethod
    def visit_assign_expression(self, assign_expr):
        pass
    
    @abstractmethod
    def visit_method_call_expr(self, method_call_expr):
        pass
    
    @abstractmethod
    def visit_auto_expr(self, auto_expr):
        pass
    
    @abstractmethod
    def visit_identifier(self, identifier_ref_expr):
        pass
    
class Statement(ABC):
    
    @abstractmethod
    def accept(self, visitor : ASTVisitor):
        pass
    
class Expression(ABC):
    
    @abstractmethod
    def accept(self, visitor : ASTVisitor):
        pass
    
    @abstractmethod
    def get_type(self) -> Optional[decaf_typecheck.BaseType | decaf_typecheck.ClassObjectType | decaf_typecheck.ClassLiteralType]:
        pass

#can have nested blocks
class BlockStatement(Statement):
    
    def to_dict(self):
        res = []
        for statement in self.statements:
            res.append(statement.to_dict())
        return res
    
    def accept(self, visitor : ASTVisitor):
        return visitor.visit_block_statement(self)

    

    def __init__(self, statements = []):

        self.statements = []
        self.var_declarations = []
        
        for statement in statements:
              
            if isinstance(statement, list):
                
                for s in statement:
                    self.statements.append(s)
                                          
            else:    
                self.statements.append(statement)
    
    def get_statements_list(self) -> List[Statement]:
        return self.statements

    def __str__(self):

        return_str = "Block(["

        for i in range(0, len(self.statements) - 1):
            return_str += str(self.statements[i]) + ',\n'
        
        if len(self.statements) > 0:
            return_str += str(self.statements[-1]) 
            
        return_str += "])"

        return return_str

class If_Statement(Statement):
    
    def to_dict(self):
        res = {}
        res['type'] = 'if'
        res['condition'] = self.if_expression.to_dict()
        res['then_statement'] = self.then_statement.to_dict()
        res['else_statement'] = self.else_statement.to_dict()
        return res
  
    def get_if_expression(self) -> Expression:
        return self.if_expression
    
    def get_then_statement(self) -> Statement:
        return self.then_statement

    def __init__(self, if_expression : Expression, then_statement : Statement, else_statement : Statement):
       self.if_expression : Expression = if_expression
       self.then_statement : Statement = then_statement
       self.else_statement : Statement = else_statement

    def accept(self, visitor : ASTVisitor):
        return visitor.visit_if_statement(self)


    def get_statements_list(self):
        return [self]

    
    def __str__(self):
       return f'If({self.if_expression},{self.then_statement},{self.else_statement})'

class While_Statement:

    def to_dict(self):
        res = {}
        res['type'] = 'while'
        res['condition'] = self.loop_condition.to_dict()
        res['body'] = self.loop_body.to_dict()
        return res
  
    def __init__(self, loop_condition, loop_body):
        self.loop_condition = loop_condition
        self.loop_body = loop_body
  
    def __str__(self):
        return f'While({self.loop_condition},{self.loop_body})'

class For_Statement(Statement):
    
    def to_dict(self):
        res = {}
        res['type'] = 'for'
        res['initialize_expression'] = self.initializer_expression.to_dict()
        res['loop_condition'] = self.loop_condition.to_dict()
        res['update_expression'] = self.update_expression.to_dict()
        res['body'] = self.loop_body.to_dict()
        return res
    
    def get_initializer_expression(self) -> Expression:
        return self.initializer_expression
    
    def get_loop_condition(self) -> Expression:
        return self.loop_condition
    
    def get_update_expression(self) -> Expression:
        return self.update_expression
    
    def get_loop_body(self) -> Statement:
        return self.loop_body

    def __init__(self, initializer_expression, loop_condition, update_expression, loop_body):
        self.initializer_expression : Expression = (initializer_expression)
        self.loop_condition : Expression = (loop_condition)
        self.update_expression : Expression = (update_expression)
        self.loop_body : Statement = (loop_body)
        
    def accept(self, visitor : ASTVisitor):
        return visitor.visit_for_statement(self)

    def __str__(self):
        return f'For({self.initializer_expression},{self.loop_condition},{self.update_expression},{self.loop_body})'


class Expression_Statement(Statement):
    
    def to_dict(self):
        res = {}
        res['expression'] = self.expression.to_dict()
        return res
    
    def get_expression(self) -> Expression:
        return self.expression

    def accept(self, visitor : ASTVisitor):
        visitor.visit_expression_statement(self)
        
    
    def __init__(self, expression : Expression):
       
       self.expression : Expression = expression


    def __str__(self):
       return f'Expr-stmt({self.expression})'

class Break_Statement:
    
    def to_dict(self):
        res = {}
        res['type'] = 'break'
        return res
  
 
  
    def __init__(self):
        pass


    def __str__(self):
       return f'Break'

class Continue_Statement:
    
    def to_dict(self):
        res = {}
        res['type'] = 'continue'
        return res
    
    

    def __init__(self):
       pass


    def __str__(self):
       return f'Continue'

class Skip_Statement:
    
    
    def to_dict(self):
        res = {}
        res['type'] = 'skip'
        return res
    
  
    def __init__(self):
        pass
  
 
  
    def __str__(self):
        return f'Skip'    

class Assign_Expression(Expression):
    
    def to_dict(self):
        res = {}
        res['type'] = 'assign'
        res['lhs'] = self.left_hand_side.to_dict()
        res['rhs'] = self.right_hand_side.to_dict()
        res['data_type'] = str(self.type)
        return res
        

    def get_type(self):
        return self.type
    
    def get_left_expression(self) -> Expression:
        return self.left_hand_side
    
    def get_right_expression(self)-> Expression:
        return self.right_hand_side


    def accept(self, visitor : ASTVisitor):
        visitor.visit_assign_expression(self)

    def __init__(self, left_hand_side : Expression, right_hand_side : Expression):
        self.left_hand_side : Expression= left_hand_side
        self.right_hand_side : Expression= right_hand_side
        self.type = None

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
        

    def get_base_expression(self):
        return self.base_expression

    def get_field_name(self):
        return self.field_name

    def __init__(self, base_expression, field_name):
        self.base_expression = base_expression
        self.field_name = field_name
        self.type = None 
        self.id_of_field = None
        


    #Field-access(This, x)
    def __str__(self):
        return f'Field-access({self.base_expression}, {self.field_name}, {self.id_of_field})'





class Binary_Expression(Expression):
    
    def to_dict(self):
        res = {}
        res['type'] = 'binary'
        res['lhs'] = self.left_expr.to_dict()
        res['rhs'] = self.right_expr.to_dict()
        res['data_type'] = str(self.type)
        return res
    
    def set_type(self, type):
        self.type = type
 
    def get_type(self):
        return self.type

    def accept(self, visitor : ASTVisitor):
        return visitor.visit_binary_expression(self)
    
    def get_left_expression(self) -> Expression:
        return self.left_expr
    
    def get_right_expression(self) -> Expression:
        return self.right_expr
 

    def __init__(self, operation : Operation, left_expr : Expression, right_expr : Expression):
        self.operation : Operation = operation
        self.left_expr : Expression = left_expr
        self.right_expr : Expression= right_expr
        self.type = None

    def __str__(self):
        return f'Binary({self.operation}, {self.left_expr}, {self.right_expr})'

class Unary_Expression:

    def get_type(self):
        return self.type


    def __init__(self, operation, expression):
        self.operation = operation
        self.expression = expression

    def __str__(self):
        return f'Urnary({self.operation}, {self.expression})'
 


class Constant_Expression(Expression):
    
    def to_dict(self):
        res = {}
        res['type'] = 'constant'
        res['val'] = self.val
        res['data_type'] = str(self.type)
        return res
    
    def accept(self, visitor : ASTVisitor):
        visitor.visit_constant_expression(self)
    
    def get_type(self):
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



class Return_Statement(Statement):
    
    def to_dict(self):
        res = {}
        res['type'] = 'return'
        res['expression'] = self.expression.to_dict()
        return res
    
    
    def get_statements_list(self):
        return [ self ]
    
    def accept(self, visitor : ASTVisitor):
        visitor.visit_return_statement(self)

    def get_expression(self) -> Expression:
        return self.expression

    def __init__(self, expression : Expression):
        self.expression : Expression = expression

    def __str__(self):
        return f'Return({self.expression})'
    
class FunctionRecord(ABC):
    
    def __init__(self, name : str, id : int, visibility, parameters : List[Variable_Declaration] , body : BlockStatement):
        self.name = name
        self.id = id
        self.visibility = visibility
        self.parameters = parameters
        self.body = body
        
    def get_body(self) -> BlockStatement:
        return self.body
    
    def get_parameters(self) -> List[Variable_Declaration] :
        return self.parameters
    
    def get_name(self) -> str:
        return self.name
    
    def get_visibility(self):
        return self.visibility
    
    def get_id(self) -> int:
        return self.id
    
    
    
    
class Constructor_Record(FunctionRecord):
    
    def to_dict(self):
        res = {}
        res['id'] = self.id
        res['visibility'] = self.visibility
        res['parameters'] = self.params
        res['variables'] = self.variable_table.to_dict()
        res['body'] = self.body.to_dict()
        return res
 

    def get_variable_table(self) -> Variable_Table:
        return self.variable_table


    #body is a block -assume for now that is contains no other block
    def __init__(self, class_name : str, visibility, parameters, body):
        super().__init__(class_name, AST.get_new_constructor_id(), visibility, parameters, body)
       
        self.variable_table = Variable_Table()


    def __str__(self):
        return_str = f'CONSTRUCTOR: {self.id}, {self.visibility}\n' + f'Constructor parameters: {(", ".join(map(str, self.parameters))) }\n' + f'Variable Table:\n' + str(self.variable_table) + f'Constructor Body:\n{self.body}'

        return return_str

    

class Method_Record(FunctionRecord):
    
    def to_dict(self):
        res = {}
        res['id'] = self.id
        res['visibility'] = self.visibility
        res['parameters'] = [x.to_dict() for x in self.parameters]
        res['variables'] = self.variable_table.to_dict()
        res['body'] = self.body.to_dict()
        return res
    
 
    
    def get_applicability(self):
        return self.applicability

    def set_containing_class(self, class_name):
        self.containing_class = class_name
    
    def __init__(self, name : str, containing_class : str, visibility, applicability, parameters, return_type, body : BlockStatement):
        super().__init__(name, AST.get_new_method_id(), visibility, parameters, body)
        
        self.containing_class = containing_class
        
        self.applicability = applicability
        
        type_name_map = {'int' : decaf_typecheck.BaseType.INT, 'boolean' : decaf_typecheck.BaseType.BOOL, 'float' : decaf_typecheck.BaseType.FLOAT, 'void' : decaf_typecheck.BaseType.VOID}
        
        if return_type in type_name_map:
            self.return_type = type_name_map[return_type]
        else:
            self.return_type = decaf_typecheck.ClassObjectType(return_type)
        
        self.variable_table = Variable_Table()

        
    def get_return_type(self):
        return self.return_type    
  
        
    def get_variable_table(self) -> Variable_Table:
        return self.variable_table
          

    def __str__(self):
        
        return_str = f'METHOD: {self.id}, {self.name}, {self.containing_class}, {self.visibility}, {self.applicability}, {self.return_type}\n' +  f'Method parameters: {(", ".join(map(str, self.parameters))) }\n' + f'Variable Table:\n' + str(self.variable_table)+ f'Method Body:\n{self.body}'

        return return_str
        
class Field_Record:

    def to_dict(self):
        res = {}
        res['name'] = self.name
        res['id'] = self.id
        res['visibility'] = self.visibility
        res['applicability'] = self.applicability
        return res

    def get_name(self) -> str:
        return self.name
    
    def get_type(self):
        return self.data_type

    def set_containing_class(self, class_name):
        self.containing_class = class_name
        
    def compute_type(self):
        return self.data_type
    
    def get_visibility(self):
        return self.visibility
    
    def get_applicability(self):
        return self.applicability
    
    def get_id(self) -> int:
        return self.id

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

        
        
class Class_Record:


    def to_dict(self):
        res = {}
        res['superclass'] = self.super_class_name
        res['fields'] = [x.to_dict() for x in self.fields]
        res['constructors'] = [x.to_dict() for x in self.constructors]
        res['methods'] = [x.to_dict() for x in self.methods]
        return res

    def get_fields(self) -> List[Field_Record]:
        return self.fields

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


    def get_name(self) -> str:
        return self.class_name
    
    def get_method_from_name(self, method_name : str):
        
        for record in self.methods:
            if record.name == method_name:
                return record
                
        return None
    
    def get_constructors(self) -> List[Constructor_Record]:
        return self.constructors
    
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
                
                #this_expressions = element.get_this_expressions_to_resolve()
                #for this_expr in this_expressions:
                #    this_expr.set_type(decaf_typecheck.ClassObjectType(self.class_name))



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
        



class New_Object_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'new_object'
        res['class'] = self.class_name
        res['data_type'] = str(self.type)
        res['args'] = [x.to_dict() for x in self.arguments]
        return res

    
    def get_type(self):
        return self.type



    def __init__(self, class_name, arguments):
        self.class_name = class_name
        self.arguments = arguments  
        self.type = None

    def __str__(self):
        args = ", ".join(map(str, self.arguments))
        return f'New-object({self.class_name}, [{args}])'

class Method_Call_Expression(Expression):
    
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
    
    def get_base_expression(self) ->Expression:
        return self.base_expression

    def accept(self, visitor : ASTVisitor):
        return visitor.visit_method_call_expr(self)
    
    def get_args(self) -> List[Expression]:
        return self.arguments
    
    def get_method_name(self) -> str:
        return self.method_name
    
    def set_id(self, id : int):
        self.method_id = id
    
    def __init__(self, base_expression, method_name, arguments):
        self.base_expression : Expression = base_expression
        self.method_name = method_name
        self.arguments = arguments
        self.method_id = None
        self.type = None
    
    def set_type(self, data_type):
        self.type = data_type

    def __str__(self):
        args = ", ".join(map(str, self.arguments))
        return f'Method-call({self.base_expression}, {self.method_name}, [{args}], {self.method_id})'

class Auto_Expression(Expression):
    
    def to_dict(self):
        res = {}
        res['type'] = 'auto'
        res['expression'] = self.operand_expression.to_dict()
        res['op_type'] = self.inc_dec
        res['op_kind'] = self.post_pre
        res['data_type'] = str(self.type)
        
        return res
    
    def get_expression(self) -> Expression:
        return self.operand_expression
    
    def accept(self, visitor : ASTVisitor):
        visitor.visit_auto_expr(self)
    
    def get_type(self):
        return self.type
        
    def __init__(self, operand_expression, inc_dec, post_pre):
        self.operand_expression = operand_expression
        self.inc_dec = inc_dec
        self.post_pre = post_pre
        self.type = None

    def __str__(self):
        return f'Auto({self.operand_expression}, {self.inc_dec}, {self.post_pre})'
    
class Class_Reference_Expression:
    
    def to_dict(self):
        res = {}
        res['type'] = 'class_reference'
        res['data_type'] = str(self.type)
        return res
  
    
    def get_type(self):
        return self.type
    
    def __init__(self, class_name : str):
        self.class_name = class_name
        self.type = decaf_typecheck.ClassLiteralType(class_name)
        
    def __str__(self):
        return f'class-literal({self.class_name})'


        
class Variable_Reference(Expression):
    
    def to_dict(self):
        res = {}
        res['type'] = 'variable_reference'
        res['variable'] = self.var_name
        res['data_type'] = str(self.type)
        res['id'] = self.id
        return res
    
    def accept(self, visitor : ASTVisitor):
        visitor.visit_variable_reference_expression(self)


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
     


        
    def __str__(self):
        return f'Variable({self.id}, {self.var_name})'

#can be fore a local variable, or class name
class IdentifierReference(Expression):
    
    def to_dict(self):
        return self.identifier.to_dict()
    
    def __init__(self, name : str):
        self.name = name
        self.identifier = None
        
    def get_name(self) -> str:
        return self.name
        
    def set_identifier(self, identifier : Class_Reference_Expression | Variable_Reference):
        self.identifier = identifier
        
    def get_identifier(self) -> Optional[Class_Reference_Expression | Variable_Reference]:
        return self.identifier
    
    def accept(self, visitor : ASTVisitor):
       visitor.visit_identifier(self)
       
    def get_type(self):
        if self.identifier == None:
            return None
        return self.identifier.get_type()
    
    def __str__(self):
        
        if self.identifier == None:
            return f'UNRESOLVED({self.name})'
        
        return str(self.identifier)
        



class WriteStatement(Statement):
    
    def to_dict(self):
        res = {}
        res['type'] = 'syscall'
        res['call'] = 'write'
        res['data'] = self.data.to_dict()
        return res
    
    def get_data(self):
        return self.data
    
    def accept(self, visitor):
        return visitor.visit_write_statement(self)
    
    #Currently, data will always be a VariableReference becasuse write statement is only used inside print function
    def __init__(self, data : Expression):
        self.data : Expression = data
        
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
        print_i = Method_Record("print", "Out", "public", "static", [Variable_Declaration("int", "i")], "void", BlockStatement([WriteStatement(Variable_Reference("i"))]))
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

