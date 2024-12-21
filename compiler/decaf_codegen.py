import decaf_ast
import decaf_absmc
import decaf_typecheck
from typing import Dict, List, Tuple


def convert_boolean_to_int(boolean : str) -> int:
    if boolean == 'true':
        return 1
    return 0

class AbstractCodeGenerator:

    def __init__(self, ast : decaf_ast.AST):
        self.cur_arg_register = 1 
        self.cur_tmp_register = 0
        self.ast = ast
        self.register_save_stack : List[str] = []
        self.program = decaf_absmc.AbstractProgram()
        self.instance_field_id_to_offset_map : Dict[int, int] = {}
        self.static_fields_to_offset_map: Dict[Tuple[str, str], int] = {}
        self.cur_num_static_fields = 0
        self.cur_if_statement = 1
        self.cur_while_statement = 1
        self.cur_for_statement = 1
        
    def get_next_for_control_flow_labels(self) -> Tuple[str, str, str, str]:
        res = (f'for_{self.cur_for_statement}_cond', f'for_{self.cur_for_statement}_body', f'for_{self.cur_for_statement}_update', f'for_{self.cur_for_statement}_end')
        self.cur_for_statement += 1
        return res
        
        
    def get_next_while_control_flow_labels(self) -> Tuple[str, str, str]:
        res = (f'while_{self.cur_while_statement}_cond', f'while_{self.cur_while_statement}_body', f'while_{self.cur_while_statement}_end')
        self.cur_while_statement += 1
        return res    
        
    def get_next_if_control_flow_labels(self) -> Tuple[str, str, str]:
        res = (f'if_{self.cur_if_statement}_then', f'if_{self.cur_if_statement}_else', f'if_{self.cur_if_statement}_end') 
        self.cur_if_statement += 1
        return res
        

    
    def add_static_field(self, field: Tuple[str, str]):
        self.static_fields_to_offset_map[field] = self.cur_num_static_fields
        self.cur_num_static_fields += 1
            
    
    def get_instance_field_id_to_offset_map(self) -> Dict[int, int]:
        return self.instance_field_id_to_offset_map
    
    def set_instance_field_id_to_offset_map(self, map : Dict[int, int]):
        self.instance_field_id_to_offset_map = map
        
    def save_all_regs_cur_used(self, cur_label):
        
        for i in range(0, self.cur_arg_register):
            self.register_save_stack.append(f'a{i}')
            self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.SAVE, [f'a{i}'], ""])
            
        for i in range(0, self.cur_tmp_register):
            self.register_save_stack.append(f't{i}')
            self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.SAVE, [f't{i}'], ""])
            
        
    
    def restore_all_saved_regs(self, cur_label):
        
        while len(self.register_save_stack) > 0:
            self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.RESTORE, [self.register_save_stack.pop()], ""])
        

    def reset_tmp_register(self):
        self.cur_tmp_register = 0
        
    def get_next_tmp_register(self):
        res = self.cur_tmp_register
        self.cur_tmp_register += 1
        return "t" + str(res)

    def reset_arg_register(self, num : int): 
        
        self.cur_arg_register = num
    
    def get_next_arg_register(self):
        res = self.cur_arg_register
        self.cur_arg_register += 1
        return "a" + str(res)


    def generate_code(self):
        
        class_records = self.ast.get_class_records()
        
        
        #determine static fields
        for class_record in class_records:
            class_instance_field_offset = 0
            for field in class_record.fields:
                if field.applicability == 'static':
                    self.add_static_field((class_record.class_name, field.name))
                else:
                    self.instance_field_id_to_offset_map[field.id] = class_instance_field_offset
                    class_instance_field_offset += 1
                    
        self.program.set_size_static_section(self.cur_num_static_fields)
        
        
        for class_record in class_records:
             
            self.program.create_label_group(class_record.class_name, f"#====== Code for class {class_record.class_name}")
            
            for constructor in class_record.constructors:
                self.reset_tmp_register()
                self.reset_arg_register(1)
                
                constructor_label = f'C_{constructor.id}'
                self.program.create_labeled_section(constructor_label, class_record.class_name)
                
                self.generate_constructor_code(constructor, constructor_label)
            
            methods = class_record.get_method_records()
            for method_record in methods:
                self.reset_tmp_register()
                self.reset_arg_register(0 if method_record.applicability == 'static' else 1)
                
                method_label = f'M_{method_record.name}_{method_record.id}'
                
                
                if method_record.name == 'main'and method_record.applicability == 'static':
                    #self.program.append_label_to_labeled_section(meh)
                    self.program.create_labeled_section("_start", class_record.class_name)
                
                self.program.create_labeled_section(method_label, class_record.class_name)
                self.generate_method_code(method_record, method_label)        

        return self.program
    
    #returns register in which result is
    def generate_expression_code(self, expression_record, cur_label, var_id_to_register_map):
        
        if isinstance(expression_record, decaf_ast.Auto_Expression):
            
            if expression_record.inc_dec == 'inc':
                delta_ins = decaf_absmc.Instruction.IADD
            else:
                delta_ins = decaf_absmc.Instruction.ISUB
                
            
            if expression_record.post_pre == 'pre':
                
                delta_reg = self.get_next_tmp_register()
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [delta_reg, str(1)], "auto"])
                
                self.program.append_instruction_to_labeled_section(cur_label, [delta_ins, [var_id_to_register_map[expression_record.operand_expression.get_var()], var_id_to_register_map[expression_record.operand_expression.get_var()], delta_reg], "prefix operator"])
                
                return  var_id_to_register_map[expression_record.operand_expression.get_var()]
            
            else: #post
                
                old_reg = self.get_next_tmp_register()
                
                
                expr_reg = self.generate_expression_code(expression_record.operand_expression, cur_label, var_id_to_register_map)
                
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, [old_reg, expr_reg], "copy for postfix operator"])
                
                delta_reg = self.get_next_tmp_register()
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [delta_reg, str(1)], "auto"])
                
                self.program.append_instruction_to_labeled_section(cur_label, [delta_ins, [expr_reg, expr_reg, delta_reg], "postfix operator"])
                
                return old_reg
                
        if isinstance(expression_record, decaf_ast.Assign_Expression):
            
                if isinstance(expression_record.left_hand_side, decaf_ast.Field_Access_Expression):
                    
                    expr_reg = self.generate_expression_code(expression_record.right_hand_side, cur_label, var_id_to_register_map)
                    
                    if isinstance(expression_record.left_hand_side.base_expression, decaf_ast.Class_Reference_Expression):
                        
                        #static field
                        
                        offset = self.static_fields_to_offset_map[(expression_record.left_hand_side.base_expression.class_name, expression_record.left_hand_side.field_name)]
                        
                        temp_reg = self.get_next_tmp_register()
                        
                        self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [temp_reg, str(offset)], "store offset to static field"])
                        
                        self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.HSTORE, ["sap", temp_reg, expr_reg], ""])
                        
                        return expr_reg
                       
                    base_expr_reg = self.generate_expression_code(expression_record.left_hand_side.base_expression, cur_label, var_id_to_register_map)
                        
                    off_reg = self.get_next_tmp_register()
                           
                    self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [off_reg, str(self.instance_field_id_to_offset_map[expression_record.left_hand_side.id_of_field])], "store offset for field access"])
                    
                    self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.HSTORE, [base_expr_reg, off_reg, expr_reg], ""])
                    
                    return expr_reg
                    
                else:
                    
                    #returns register that contains the pointer
                    expr_reg = self.generate_expression_code(expression_record.right_hand_side, cur_label, var_id_to_register_map)
                    self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, [var_id_to_register_map[expression_record.left_hand_side.get_var()], expr_reg], f"Set {expression_record.left_hand_side} to RHS"])
                    
                    return var_id_to_register_map[expression_record.left_hand_side.get_var()]
        
        
        if isinstance(expression_record, decaf_ast.Field_Access_Expression):
            
            if isinstance(expression_record.base_expression, decaf_ast.This_Expression):
                
                reg = self.get_next_tmp_register()
                
                offset_reg = self.get_next_tmp_register()
                
                offset = self.get_instance_field_id_to_offset_map()[expression_record.id_of_field]
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [offset_reg, str(offset)], " "])                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.HLOAD, [reg, "a0", offset_reg], ""])
                
                return reg
            
            elif isinstance(expression_record.base_expression, decaf_ast.Class_Reference_Expression):
                reg = self.get_next_tmp_register()
                
                offset = self.static_fields_to_offset_map[(expression_record.base_expression.class_name, expression_record.field_name)]
                
                offset_reg = self.get_next_tmp_register()
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [offset_reg, str(offset)], " "])                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.HLOAD, [reg, "sap", offset_reg], ""])
                
                return reg
                
                
            elif isinstance(expression_record.base_expression, decaf_ast.Variable_Reference):
                
                reg = self.get_next_tmp_register()
                
                offset = self.instance_field_id_to_offset_map[expression_record.id_of_field]
                
                offset_reg = self.get_next_tmp_register()
                
                var_reg = var_id_to_register_map[expression_record.base_expression.var]
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [offset_reg, str(offset)], " "])                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.HLOAD, [reg, var_reg, offset_reg], ""])
                
                #field access
                
                return reg
            else:
                raise Exception(f"cannot convert expression type")
                
            
        if isinstance(expression_record, decaf_ast.New_Object_Expression):
            
            class_record = self.ast.get_class_record(expression_record.class_name)
            constructor_id = class_record.get_id_from_method_name(expression_record.class_name)
             
            count = class_record.get_instance_field_count()
            
            count_reg = self.get_next_tmp_register()
            heap_reg = self.get_next_tmp_register()
            
            self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [count_reg , str(count)], "t1 := number of fields"])
            
            self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.HALLOC, [heap_reg, count_reg] , "allocate heap memory for fields"])
            
            self.save_all_regs_cur_used(cur_label)
            
            self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, ["a0", heap_reg], "pointer to object must be in first arg register"])
            
            
            
            
            for param_index in range(0, len(expression_record.arguments)): 
                    a = self.generate_expression_code(expression_record.arguments[param_index], cur_label, var_id_to_register_map)
                    self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, [f'a{param_index + 1}', a], "pass arg into funciton"])
            
            
            
            self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.CALL, [f'C_{constructor_id}'], "call constructor"])
            
            self.restore_all_saved_regs(cur_label)
            
            return heap_reg
            
        
        if isinstance(expression_record, decaf_ast.Constant_Expression):
            
            reg = self.get_next_tmp_register()
            
            if expression_record.type == decaf_typecheck.BaseType.BOOL:
                value = convert_boolean_to_int(expression_record.val)
                ins = decaf_absmc.Instruction.MOVE_IMMED_I
            elif expression_record.type == decaf_typecheck.BaseType.INT:
                value = expression_record.val
                ins = decaf_absmc.Instruction.MOVE_IMMED_I
            elif expression_record.type == decaf_typecheck.BaseType.NULL: 
                value = str(0)
                ins = decaf_absmc.Instruction.MOVE_IMMED_I
            else: #float
                value = expression_record.val
                ins = decaf_absmc.Instruction.MOVE_IMMED_F
            
            
            self.program.append_instruction_to_labeled_section(cur_label, [ins, [reg,  str(value)], f'{expression_record}'])
            
            return reg
        if isinstance(expression_record, decaf_ast.Variable_Reference):
            
            return var_id_to_register_map[expression_record.var]
        
        if isinstance(expression_record, decaf_ast.Unary_Expression):
            new_reg = self.get_next_tmp_register()
            
            if expression_record.operation == 'neg':
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [new_reg, str(1)], "#set to 1 for compare"])
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.ISUB, [new_reg, new_reg, self.generate_expression_code(expression_record.expression, cur_label, var_id_to_register_map)], ""])
                
            elif expression_record.operation == "uminus":
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [new_reg, str(-1)], "Store -1 constant for negation"])
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IMUL, [new_reg, new_reg, self.generate_expression_code(expression_record.expression, cur_label, var_id_to_register_map)], "Multiply by -1 to negatve"])
                
            return new_reg
    
        if isinstance(expression_record, decaf_ast.Binary_Expression):
            new_reg = self.get_next_tmp_register()
            
            
            arith_ops = {decaf_typecheck.BaseType.INT : {decaf_ast.Operation.ADD : decaf_absmc.Instruction.IADD, "sub" : decaf_absmc.Instruction.ISUB,
                            "mult" : decaf_absmc.Instruction.IMUL, "div" : decaf_absmc.Instruction.IDIV}, 
                   "float" : {"add" : decaf_absmc.Instruction.FADD, "sub" : decaf_absmc.Instruction.FSUB,
                            "mult" : decaf_absmc.Instruction.FMUL, "div" : decaf_absmc.Instruction.FDIV}}
            
            if expression_record.operation in arith_ops[decaf_typecheck.BaseType.INT]:
                
                left_reg = self.generate_expression_code(expression_record.left_expr, cur_label, var_id_to_register_map)
                right_reg = self.generate_expression_code(expression_record.right_expr, cur_label, var_id_to_register_map)
                
            
               
                if expression_record.get_type() == 'float':
                    
                    if expression_record.left_expr.get_type() == 'int':
                        
                        conv_reg = self.get_next_tmp_register()
                        
                        self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.ITOF, [conv_reg, left_reg], ""])
                        
                        left_reg = conv_reg
                        
                    if expression_record.right_expr.get_type() == 'int':
                        conv_reg = self.get_next_tmp_register()
                        
                        self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.ITOF, [conv_reg, right_reg], ""])
                        
                        right_reg = conv_reg
                
                self.program.append_instruction_to_labeled_section(cur_label, [arith_ops[expression_record.get_type()][expression_record.operation], [new_reg, left_reg, right_reg], "Add op"])
                    
            if expression_record.operation == 'and':
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IMUL, [new_reg, self.generate_expression_code(expression_record.left_expr, cur_label, var_id_to_register_map), self.generate_expression_code(expression_record.right_expr, cur_label, var_id_to_register_map)], "logical and"])
                
            if expression_record.operation == 'or':
                
                one_const = self.get_next_tmp_register()
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [one_const, str(1)], "#set to 1 for comparison"])
                
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IADD, [new_reg, self.generate_expression_code(expression_record.left_expr, cur_label, var_id_to_register_map), self.generate_expression_code(expression_record.right_expr, cur_label, var_id_to_register_map)], ""])
                
                
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IGEQ, [new_reg, new_reg, one_const], ""])
                
                
            arith_comps = {"lt" : decaf_absmc.Instruction.ILT, "leq" : decaf_absmc.Instruction.ILEQ, "gt" : decaf_absmc.Instruction.IGT, "geq" : decaf_absmc.Instruction.IGEQ}
                
            if expression_record.operation in arith_comps:
                self.program.append_instruction_to_labeled_section(cur_label, [arith_comps[expression_record.operation], [new_reg, self.generate_expression_code(expression_record.left_expr, cur_label, var_id_to_register_map), self.generate_expression_code(expression_record.right_expr, cur_label, var_id_to_register_map)], ""])
                
            if expression_record.operation == 'eq':
                
                left = self.generate_expression_code(expression_record.left_expr, cur_label, var_id_to_register_map)
                right = self.generate_expression_code(expression_record.right_expr, cur_label, var_id_to_register_map)
                
                comp_reg = self.get_next_tmp_register()
            
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IGEQ, [new_reg, left, right], ""])   
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.ILEQ, [comp_reg, left, right], ""]) 
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IMUL, [new_reg, new_reg, comp_reg], ""])   
                    
            if expression_record.operation == 'neq':
                left = self.generate_expression_code(expression_record.left_expr, cur_label, var_id_to_register_map)
                right = self.generate_expression_code(expression_record.right_expr, cur_label, var_id_to_register_map)
                
                comp_reg = self.get_next_tmp_register()
            
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IGT, [new_reg, left, right], ""])   
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.ILT, [comp_reg, left, right], ""]) 
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IADD, [new_reg, new_reg, comp_reg], ""])
            return new_reg
            
            
        
        if isinstance(expression_record, decaf_ast.Method_Call_Expression):
                   
            if isinstance(expression_record.base_expression, decaf_ast.Class_Reference_Expression):
                
                self.save_all_regs_cur_used(cur_label)
                
                func_return_reg = self.get_next_tmp_register()
                
                for param_index in range(0, len(expression_record.arguments)):
                    
                    arg_reg = self.generate_expression_code(expression_record.arguments[param_index], cur_label, var_id_to_register_map)
                    
                    self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, [f'a{param_index}', arg_reg], "pass arg into funciton"])
                
                call_label = f'M_{expression_record.method_name}_{expression_record.method_id}'
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.CALL, [call_label], "call function"])
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, [func_return_reg, "a0"], "save func result"])
                
                self.restore_all_saved_regs(cur_label)
                #static method
                pass
            elif isinstance(expression_record.base_expression, decaf_ast.Field_Access_Expression):
                
                obj_reg = self.generate_expression_code(expression_record.base_expression, cur_label, var_id_to_register_map)
                   
                self.save_all_regs_cur_used(cur_label)
                
                func_return_reg = self.get_next_tmp_register()
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, ["a0", obj_reg], "move pointer to object to a0"])
                
                for param_index in range(0, len(expression_record.arguments)):
                    
                    self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, [f'a{param_index + 1}', var_id_to_register_map[expression_record.arguments[param_index].var]], "pass arg into funciton"])
                
                call_label = f'M_{expression_record.method_name}_{expression_record.method_id}'
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.CALL, [call_label], "call function"])
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, [func_return_reg, "a0"], "save func result"])
                
                self.restore_all_saved_regs(cur_label)
                         
            else:
                
                self.save_all_regs_cur_used(cur_label)
                
                func_return_reg = self.get_next_tmp_register()
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, ["a0", var_id_to_register_map[expression_record.base_expression.var]], "move pointer to object to a0"])
                
                for param_index in range(0, len(expression_record.arguments)):
                    a = self.generate_expression_code(expression_record.arguments[param_index], cur_label, var_id_to_register_map)

                    self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, [f'a{param_index + 1}', a], "pass arg into funciton"])
                
                call_label = f'M_{expression_record.method_name}_{expression_record.method_id}'
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.CALL, [call_label], "call function"])
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, [func_return_reg, "a0"], "save func result"])
                
                self.restore_all_saved_regs(cur_label)                
                
            return func_return_reg   
    
        if isinstance(expression_record, decaf_ast.This_Expression):
            return "a0"
    
        raise Exception(f"Cannot convert expression: {expression_record}")
        
        
    
    def generate_body_code(self, cur_label, statements : List, var_id_to_register_map : Dict[int, str]):
        
        for index, statement in enumerate(statements):
            
            
            if isinstance(statement, decaf_ast.WriteStatement):
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IWRITE, [var_id_to_register_map[statement.data.var]], "print to console"])
                
                
            
            if isinstance(statement, decaf_ast.For_Statement):
                
                (condition_label, body_label, update_label, end_label) = self.get_next_for_control_flow_labels()
                
                if isinstance(statement.initializer_expression, decaf_ast.Skip_Statement):
                    pass
                else:
                    if isinstance(statement.initializer_expression.get_expression(), decaf_ast.Assign_Expression):
                        init_expr_res_reg = self.generate_expression_code(statement.initializer_expression.get_expression(), cur_label, var_id_to_register_map)
                        
                    else:
                        raise Exception("Cannot convert expression")
                
                self.program.append_label_to_labeled_section(cur_label, condition_label, "for loop")
                
                condition_reg = self.generate_expression_code(statement.loop_condition, cur_label, var_id_to_register_map)
                
                if not isinstance(statement.loop_condition, decaf_ast.Skip_Statement):
                    self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.BZ, [condition_reg, end_label], ""])
                
                self.program.append_label_to_labeled_section(cur_label, body_label, "")
                
                self.generate_body_code(cur_label, statement.loop_body.get_statements_list(), var_id_to_register_map)
                
                self.program.append_label_to_labeled_section(cur_label, update_label, "")
                
                if isinstance(statement.update_expression, decaf_ast.Skip_Statement):
                    pass
                else:
                    self.generate_expression_code(statement.update_expression.get_expression(), cur_label, var_id_to_register_map)
                    
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.JMP, [condition_label], ""])
                
                self.program.append_label_to_labeled_section(cur_label, end_label, "exit loop")
                
                
            
            if isinstance(statement, decaf_ast.While_Statement):
                
                (condition_label, body_label, end_label) = self.get_next_while_control_flow_labels()
                
                self.program.append_label_to_labeled_section(cur_label, condition_label, "")
                
                condition_reg = self.generate_expression_code(statement.loop_condition, cur_label, var_id_to_register_map)
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.BZ, [condition_reg, end_label], ''])
                
                self.program.append_label_to_labeled_section(cur_label, body_label, "body of while loop")
                
                self.generate_body_code(cur_label, statement.loop_body.get_statements_list(), var_id_to_register_map)
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.JMP, [condition_label], ''])
                
                self.program.append_label_to_labeled_section(cur_label, end_label, '')
      
                
            if isinstance(statement, decaf_ast.If_Statement):
                
                (then_label, else_label, end_label) = self.get_next_if_control_flow_labels()
                
                condition_reg = self.generate_expression_code(statement.if_expression, cur_label, var_id_to_register_map)
                    
                    
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.BZ, [condition_reg, else_label], "if statement not satisfied"])
                
                self.program.append_label_to_labeled_section(cur_label, then_label, "then part of if statement")
                
                self.generate_body_code(cur_label, statement.then_statement.get_statements_list(), var_id_to_register_map)
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.JMP, [end_label], "just to end of if statement"])
                
                self.program.append_label_to_labeled_section(cur_label, else_label, "else")
                
                if not isinstance(statement.else_statement, decaf_ast.Skip_Statement):
                    self.generate_body_code(cur_label, statement.else_statement.get_statements_list(), var_id_to_register_map)
                
                self.program.append_label_to_labeled_section(cur_label, end_label, "else")
                             
            if isinstance(statement, decaf_ast.Expression_Statement):      
                self.generate_expression_code(statement.get_expression(), cur_label, var_id_to_register_map)
           
            
            if isinstance(statement, decaf_ast.Return_Statement):
                
                if not isinstance(statement.expression, decaf_ast.Skip_Statement): 
                    new_reg = self.generate_expression_code(statement.expression, cur_label, var_id_to_register_map)     
                    self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE, ["a0", new_reg], "move for return"])
                
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.RET, [],  "return from method"])
    
        
    
    def generate_constructor_code(self, constructor_record : decaf_ast.Constructor_Record, constructor_label):
        
        
        var_id_to_register_map : Dict[int, str] = {}
        
        variable_table =  constructor_record.get_variable_table()
        
        vars = variable_table.get_variables()
        
        for variable in vars:
            if variable[2] == 'formal':
                #utilize a_1, a_2, ... registers
                var_id_to_register_map[variable[0]] = self.get_next_arg_register()
            elif variable[2] == 'local':
                var_id_to_register_map[variable[0]] = self.get_next_tmp_register()
                
        
        method_block = constructor_record.get_constructor_body()
        
        constructor_statements = method_block.get_statements_list()
        
        self.generate_body_code(constructor_label, constructor_statements, var_id_to_register_map)    
        
        self.program.append_instruction_to_labeled_section(constructor_label, [decaf_absmc.Instruction.RET, [],  "return"])        
    
    
    
        
    def generate_method_code(self, method_record : decaf_ast.Method_Record, method_label):
        
        var_id_to_register_map : Dict[int, str] = {}
        
        variable_table =  method_record.get_variable_table()
        
        vars = variable_table.get_variables()
        
        for variable in vars:
            if variable[2] == 'formal':
                #utilize a_1, a_2, ... registers
                var_id_to_register_map[variable[0]] = self.get_next_arg_register()
            elif variable[2] == 'local':
                var_id_to_register_map[variable[0]] = self.get_next_tmp_register()
                
        
        method_block = method_record.get_method_body()
        
        method_statements = method_block.get_statements_list()
        
        
        self.generate_body_code(method_label, method_statements, var_id_to_register_map)
                
        self.program.append_instruction_to_labeled_section(method_label, [decaf_absmc.Instruction.RET, [], "return from method"])
 


    