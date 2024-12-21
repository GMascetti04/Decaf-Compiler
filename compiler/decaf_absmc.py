
from enum import Enum
from typing import Dict, Tuple, List


class Instruction(Enum):
    MOVE_IMMED_I = "move_immed_i"
    MOVE_IMMED_F = "move_immed_f"
    MOVE = "move"
    IADD = "iadd"
    ISUB = "isub"
    IMUL = "imul"
    IDIV = "idiv"
    IMOD = "imod"
    IGT = "igt"
    IGEQ = "igeq"
    ILT = "ilt"
    ILEQ = "ileq"
    FADD = "fadd"
    FSUB = "fsub"
    FMUL = "fmul"
    FDIV = "fdiv"
    FGT = "fgt"
    FGEQ = "fgeq"
    FLT = "flt"
    FLEQ = "fleq"
    FTOI = "ftoi"
    ITOF = "itof"
    BZ = "bz"
    BNZ = "bnz"
    JMP = "jmp"
    HLOAD = "hload"
    HSTORE = "hstore"
    HALLOC = "halloc"
    CALL = "call"
    RET = "ret"
    SAVE = "save"
    RESTORE = "restore"
    
    IWRITE = 'iwrite'
    






#the code genereate will interact with this class
class AbstractProgram:
    
    def __init__(self):
        self.labels_to_sections_map : Dict[str, List[Tuple[Instruction, List[str], str]]] = {}
        self.label_groups : Dict[str, Tuple[str, List[str]]] = {}
        self.comment_offset = 50
    
    def print_instruction(self, file, instruction_name : str, arg_list : List[str], comment : str):
        
        instruction_string_without_comment = f'{instruction_name} {", ".join(arg_list)}'
        spaces = " " * (self.comment_offset - len(instruction_string_without_comment))
        file.write(f'{instruction_string_without_comment}{spaces}#{comment}\n')
        

    def set_size_static_section(self, size : int):
        self.cur_static_data_offset = size
    
    def create_label_group(self, group_name : str, text : str):
        
        if group_name in self.label_groups:
            raise ValueError(f'"{group_name}" has already been used as a group name')
        
        self.label_groups[group_name] = (text, [])
    

    def create_labeled_section(self, label_name, label_group):
        
        self.labels_to_sections_map[label_name] = []
        self.label_groups[label_group][1].append(label_name)
        
        
    def append_instruction_to_labeled_section(self, label_name, intruction : Tuple[Instruction, List[str], str]):
        self.labels_to_sections_map[label_name].append(intruction)
        
    def append_label_to_labeled_section(self, label_name : str, new_label : str, comment  : str):
        self.labels_to_sections_map[label_name].append([f'{new_label}:', [], comment])
        
    
    
    def print_to_file(self, file):
    
        file.write(f'.static_data {self.cur_static_data_offset}\n\n')
    
        for group in self.label_groups.values():
            
            file.write(f'{group[0]}\n')
            for label_name in group[1]:
                
                file.write(label_name +":\n")
                for instruction_tuple in self.labels_to_sections_map[label_name]:
                    self.print_instruction(file, instruction_tuple[0] if isinstance(instruction_tuple[0], str) else instruction_tuple[0].value, instruction_tuple[1], instruction_tuple[2])
                
            

            
        
        
            
                
        
        
        