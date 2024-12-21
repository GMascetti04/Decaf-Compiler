import decaf_ast
from enum import Enum



class ClassLiteralType:
    
    def __init__(self, class_name : str):
        self.class_name = class_name
        
    def get_class_name(self):
        return self.class_name
    
    def __eq__(self, other):
        if isinstance(other, ClassLiteralType):
            return other.class_name == self.class_name
        
        return False
        
    def __str__(self):
        return f'class-literal({self.class_name})'
    
    
class ClassObjectType:
    
    def __init__(self, class_name):
        self.class_name = class_name
        
    def get_class_name(self):
        return self.class_name
    
    def __eq__(self, other):
        if isinstance(other, ClassObjectType):
            return other.class_name == self.class_name
        
        return False
        
    def __str__(self):
        return f'user({self.class_name})'

class BaseType(Enum):
    INT = 'int'
    BOOL = 'boolean'
    FLOAT = 'float'
    VOID = 'void'
    NULL = 'null'
    ERROR = 'error'
    
    def __str__(self):
        return self.value



#returns true iff a is a subtype of b
def is_subtype(a : str, b : str, ast):

    if a == b:
        return True
    
    if a == BaseType.INT and b == BaseType.FLOAT:
        return True

    
    if a == BaseType.NULL and isinstance(b, ClassObjectType):
        return True
    
    if isinstance(a, ClassObjectType) and isinstance(b, ClassObjectType):
        return ast.is_subclass(a.get_class_name(), b.get_class_name) 

    if isinstance(a, ClassLiteralType) and isinstance(b, ClassLiteralType):
        return ast.is_subclass(a.get_class_name(), b.get_class_name())

    return False
 