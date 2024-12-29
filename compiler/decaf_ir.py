from abc import ABC, abstractmethod
from typing import Optional, Tuple, TextIO, List
from enum import Enum


class A3Instruction(ABC):
    
    def __init__(self, operation, result, arg1, arg2):
        self.operation = operation
        self.result = result
        self.arg1 = arg1
        self.arg2 = arg2
    
    @abstractmethod
    def __str__(self):
        pass
    
class DataType(Enum):
    INT = 'int'
    FLOAT = 'float'
    
class ArithmeticBinaryA3Instruction(A3Instruction):
    
    
        
    class Operation(Enum):
        ADD = '+'
        SUB = '-'
        MULT = '*'
        DIV = '/'
        LESS = '<'
        LESSEQ = '<='
        GREATER = '>'
        GREATEREQ = '>='
        EQUALS = '=='
        NOTEQUALS = '!='
    
    def __init__(self, result, arg1, arg2, operation : Operation, data_type : DataType):
        self.result = result
        self.arg1 = arg1
        self.arg2 = arg2
        self.operation = operation
        self.data_type = data_type
        
    
    def __str__(self):
        return f'{self.result} := {self.arg1} {self.operation.value} {self.arg2}'

class SyscallA3Instruction(A3Instruction):
    
    def __init__(self, instruction, arg1):
        self.instruction = instruction
        self.arg1 = arg1
    
    def __str__(self):
        return f'{self.instruction} {self.arg1}'    

class UnaryInstruction(A3Instruction):
    
    class Operation(Enum):
        NEGATE = 'not'
        UMINUS = 'uminus'
    
    def __init__(self, res, arg1, type : Operation):
        self.res = res
        self.arg1 = arg1
        self.type = type
        
    def __str__(self):
        return f'{self.res} := {self.type.value} {self.arg1}'
        

class MemoryA3Instruction(A3Instruction):
    
    class Instruction(Enum):
        LOAD = 'load'
        STORE = 'store'
        
    def __init__(self, operation, result, base, offset):
        super().__init__(operation, result, base, offset)
        
    def __str__(self):
        if self.operation == MemoryA3Instruction.Instruction.LOAD:
            return f'{self.result} := LOAD {self.arg1} {self.arg2}'
        else:
            return f'{self.result} -> STORE {self.arg1} {self.arg2}'
        
class MemoryAllocateA3Instruction(A3Instruction):
    
    def __init__(self, result, num : int):
        self.num = num
        self.result = result
        
    def __str__(self):
        return f'{self.result} := ALLOC {self.num}'
      
class ControlStackA3Instruction(A3Instruction):
    
    class Instruction(Enum):
        CALL = 'call'
        RET = 'return'
        PARAM = 'param'
    
    def __init__(self, operation : Instruction, arg1 = None):
        self.operation = operation
        self.arg1 = arg1
    
    def __str__(self):
        if self.arg1 == None:
            return f'{self.operation.value}'
        return f'{self.operation.value} {self.arg1}'
       
class StackA3Instruction(A3Instruction):
    pass
    #def __init__(self, operation)
       
class AssignA3Instruction(A3Instruction):
    
    def __init__(self, target, value):
        self.target = target
        self.value = value
        
    def __str__(self):
        return f'{self.target} := {self.value}'   
        
class CastA3Instruction(A3Instruction):
    
    class CastType(Enum):
        INT_TO_FLOAT = 1
        FLOAT_TO_INT = 2
    
    def __init__(self, target, value, cast_type : CastType):
        self.target = target
        self.value = value
        self.type = cast_type
        
    def __str__(self):
        if self.type == self.CastType.INT_TO_FLOAT:
            return f'{self.target} := FLOAT({self.value})'
        else:
            return f'{self.target} := INT({self.value})'

            
        
class JumpA3Instruction(A3Instruction):
    
    
    
    def __init__(self, target, condition = None):
        
        self.target = target
        self.condition = condition
        
    def __str__(self):
        if self.condition:
            return f"if {self.condition} GOTO {self.target}"
        else:
            return f"GOTO {self.target}"



class TemporaryVariable(A3Instruction):
    
    def __init__(self, id : int):
        self.id = id
        
    def __str__(self):
        return f't{self.id}'
    
class Constant:
    
    def __init__(self, value : int | float, data_type : DataType):
        self.value = value
        self.data_type = data_type
        
    def __str__(self):
        return f'{self.value}'
    
class MethodLabel(A3Instruction):
    def __init__(self, method_name : str, method_id : int):
        self.method_name = method_name
        self.method_id = method_id
        
    def __str__(self):
        return f'M_{self.method_name}_{self.method_id}'
        
class ConstructorLabel(A3Instruction):
    def __init__(self, method_name : str, method_id : int):
        self.constructor_name = method_name
        self.constructor_id = method_id
        
    def __str__(self):
        return f'M_{self.constructor_name}_{self.constructor_id}'

class ControlFlowLabel(A3Instruction):
    def __init__(self, label_name : str):
        self.label_name = label_name
    
    def __str__(self):
        return f'{self.label_name}'
    
    


class IRPRogram:
    
    def __init__(self):
        self.program = []
        self.labels = {}

    def add_comment(self, comment : str):
        self.program.append(comment)
        
    def add_label(self, label : str):
        self.labels[label] = len(self.program)
    
    def add_instruction(self, instruction : A3Instruction, comment : Optional[str] = None):
        self.program.append((instruction, comment))
    
    def print_to_file(self, file : TextIO):
        file.write(self.__str__())
        
    def create_basic_blocks(self):
        
        self.leaders = [False] * len(self.program)
        self.leaders[0] = True
        
        for index, instruction in enumerate(self.program):
            if isinstance(instruction, Tuple):
                
                if isinstance(instruction[0], JumpA3Instruction):
                    self.leaders[self.labels[instruction[0].target]] = True
                    if index + 1 < len(self.program):
                        self.leaders[index + 1] = True
                        
                if isinstance(instruction[0], ControlStackA3Instruction):
                    
                    if instruction[0].operation == ControlStackA3Instruction.Instruction.RET:
                        if index + 1 < len(self.program):
                            self.leaders[index + 1] = True
                            
                    if instruction[0].operation == ControlStackA3Instruction.Instruction.CALL:
                        self.leaders[self.labels[instruction[0].arg1]] = True
                        if index + 1 < len(self.program):
                            self.leaders[index + 1] = True
    
    def __str__(self):
        res = ""
        index_to_labels = {}
        for label, idx in self.labels.items():
            if idx not in index_to_labels:
                index_to_labels[idx] = []
            index_to_labels[idx].append(label)

        # Print labels and instructions in order
        for i, instruction in enumerate(self.program):
            
            if self.leaders[i]:
                res += "------------------------\n"
        # Check if the current instruction has any labels
            if i in index_to_labels:
                for label in index_to_labels[i]:
                    res+= f"{label}:\n"  # Print the label
                    
            if isinstance(instruction, str):
                res += f'#{instruction}\n'
            elif isinstance(instruction, Tuple):
                if instruction[1] == None:
                    res += f'{instruction[0]}\n'
                else:
                    res += f'{instruction[0]} #{instruction[1]}\n'
        
       
            
        return res
    
    
    