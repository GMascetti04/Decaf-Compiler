from typing import Optional, List
from enum import Enum

class MethodType:
    
    def __init__(self, arg_types : List, return_type):
        self.arg_types = arg_types
        self.return_type = return_type
        
    def __str__(self):
        return f'({[str(x) for x in self.arg_types]})->{self.return_type}'
        
        

class Scope:
    
    def __init__(self, class_name : Optional[str] = None, method_name : Optional[str] = None,
                 block_list : List[int] = []):
        self.class_name = class_name
        self.method_name = method_name
        self.block_list = block_list
        
        
    def __str__(self):
        
        return f"{self.class_name}::{self.method_name}::{str(self.block_list)}"
        
        
divider : str = "---------------------------------------------\n"
        
class SymbolType(Enum):
    FIELD = 'field'
    CONSTRUCTOR = 'constructor'
    METHOD = 'method'
    PARAM = 'param'
    VAR = 'var'
    CLASS = 'class'
    
    def __str__(self):
        return self.value
    
class SymbolEntry:
    
    def __init__(self, symbol_name : str, symbol_type : SymbolType, symbol_visibility, symbol_applicability, id : int, data_type ):
        self.symbol_name = symbol_name
        self.symbol_type = symbol_type
        self.symbol_visibility = symbol_visibility
        self.symbol_applicability = symbol_applicability
        self.id = id
        self.data_type = data_type
        
    def __str__(self):
        return f'{self.symbol_name} | {self.symbol_type} | {self.symbol_visibility} | {self.symbol_applicability} | {self.id} | {self.data_type}'

#for constructors and regular methods
class FunctionSymbolTable:
    
    def to_dict(self):
        res = {}
        res['symbols'] = [str(x) for x in self.symbols]
        return res
    
    def __init__(self, function_name : str):
        self.function_name = function_name
        self.symbols : List[SymbolEntry] = []
        self.parent = None
    
    def look_up_local_variable(self, symbol_name : str) -> Optional[SymbolEntry]:
        for entry in self.symbols:
            if entry.symbol_name == symbol_name:
                return entry
            
        #return self.parent.look_up_symbol(symbol_name)
            
        return None
    
    
    def set_parent(self, parent):
        self.parent = parent
        
    def get_parent(self):
        return self.parent

    
    def add_symbol(self, symbol_entry : SymbolEntry):
        self.symbols.append(symbol_entry)
        
    def __str__(self):
        res= ''
        res += f'Function Name: {self.function_name}\n'
        res += 'Symbols:\n'
        for entry in self.symbols:
            res += f'{str(entry)}\n'
        
        return res

class ClassSymbolTable:
    
    def to_dict(self):
        res = {}
        res['class name'] = self.class_name
        res['symbols'] = [str(x) for x in self.symbols]
        res['children'] = [x.to_dict() for x in self.children]
        
        return res
    
    def __init__(self, class_name : str):
        self.class_name = class_name
        self.symbols : List[SymbolEntry] = []
        self.children : List[FunctionSymbolTable] = []
        
    def get_function_symbol(self, func_name : str) -> Optional[SymbolEntry]:
        
        for s in self.symbols:
            if s.symbol_name == func_name:
                return s
        return None
        
    def get_method_table_given_name(self, method_name : str) -> Optional[FunctionSymbolTable]:
        
        for child in self.children:
            if child.function_name == method_name:
                return child
        return None 
        
    def get_method_table(self, method_name : str):
        
        method_table = self.get_method_table_given_name(method_name)
        
        if method_table == None:
            raise Exception("bad")
        
        return method_table
        
    
    def add_child(self, child : FunctionSymbolTable):
        child.set_parent(self)
        self.children.append(child)
    
    def add_symbol(self, symbol_entry : SymbolEntry):
        self.symbols.append(symbol_entry)
    
    def __str__(self):
        
        res = f'Class Name: {self.class_name}\n'
        
        for entry in self.symbols:
            res += f'{str(entry)}\n'
            
        res += f'Children: { [x.__repr__() for x in self.children]}\n'
        for child in self.children:
            res += divider
            res += str(child)
            res += divider
        return res

        

class ProgramSymbolTable:
    
    def __init__(self):
        self.classes = {}
        self.children : List[ClassSymbolTable] = []
        self.symbols : List[SymbolEntry] = []
        self.cur_scope_table = self
        
    def to_dict(self):
        res = {}
        res['symbols'] = [str(x) for x in self.symbols]
        res['children'] = [x.to_dict() for x in self.children]
        return res
        
    def enter_method_scope(self, method_name : str):
        if not isinstance(self.cur_scope_table, ClassSymbolTable):
            raise Exception("currently not in a class scope - cannot enter a method scope")
        
        self.cur_scope_table = self.cur_scope_table.get_method_table(method_name)

        
    def exit_method_scope(self):
        if not isinstance(self.cur_scope_table, FunctionSymbolTable):
            raise Exception("not currently in method scope - cannot leave")
        
        self.cur_scope_table = self.cur_scope_table.get_parent()

    def set_scope_in_class(self, class_name : str):
        
        class_table = self.get_table_for_class(class_name)
        if class_table == None:
            raise Exception("cannot be none")
        
        self.cur_scope_table = class_table
    
    def exit_class_scope(self):
        
        if not isinstance(self.cur_scope_table, ClassSymbolTable):
            raise Exception("not in class scope currently")
        
        self.cur_scope_table = self

    def get_class_function(self, class_name : str, func_name : str) -> Optional[SymbolEntry]:
        for class_table in self.children:
            if class_table.class_name == class_name:
                return class_table.get_function_symbol(func_name)

    def is_class_name_present(self, class_name : str) -> bool:
        
        for entry in self.symbols:
            if entry.symbol_name == class_name:
                return True
        
        return False
    
    def get_table_for_class(self, class_name : str) -> Optional[ClassSymbolTable]:
        for entry in self.children:
            if entry.class_name == class_name:
                return entry
        return None

    def add_class(self, class_name : str):
        
        for entry in self.symbols:
            if entry.symbol_name == class_name:
                raise ValueError(f"class name {class_name} already exists")
            
        self.symbols.append(SymbolEntry(class_name, SymbolType.CLASS, "global", None, None, None))
        
    def add_child(self, child):
        self.children.append(child)
        
    def __str__(self):
        res = divider
        res += f"{self.__repr__()}: \n"
        for entry in self.symbols:
            res += f'{entry}\n'
        res += f'Children: { [x.__repr__() for x in self.children]}\n'
        res += divider
        for child in self.children:
            res += divider
            res += str(child)
            res += divider
        return res