import frontend.decaf_ast as decaf_ast
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