import decaf_ast
import decaf_absmc
import decaf_typecheck
import decaf_ir
from typing import Dict, List, Tuple


def convert_boolean_to_int(boolean : str) -> int:
    if boolean == 'true':
        return 1
    return 0

class IRCodeGenerator:

    def __init__(self, ast : decaf_ast.AST):
        
        self.ast : decaf_ast.AST = ast
        self.program : decaf_ir.IRPRogram = decaf_ir.IRPRogram()
        self.instance_field_id_to_offset_map : Dict[int, int] = {}
        self.static_fields_to_offset_map: Dict[Tuple[str, str], int] = {}
        self.cur_num_static_fields : int= 0
        self.cur_if_statement : int = 1
        self.cur_while_statement : int = 1
        self.cur_for_statement : int = 1
        self.cur_temp_var : int = 0
        
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
        
  
    def reset_temp_variable_count(self):
        self.cur_temp_var = 0
    
    def make_new_temp_var(self) -> decaf_ir.TemporaryVariable:
        id = self.cur_temp_var
        self.cur_temp_var += 1
        return decaf_ir.TemporaryVariable(id)


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
                    
       
        
        
        for class_record in class_records:
             
            for constructor in class_record.constructors:
                self.reset_temp_variable_count()
                constructor_label = f'C_{constructor.id}'
        
                self.program.add_label(constructor_label)
    
                self.generate_body_code(constructor.get_constructor_body().get_statements_list())   
                self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.RET))
        
            
            methods = class_record.get_method_records()
            for method_record in methods:
                self.reset_temp_variable_count()
                
                
                method_label = f'M_{method_record.name}_{method_record.id}'
                
                
                if method_record.name == 'main'and method_record.applicability == 'static':
                    self.program.add_label("_start")
                
                self.program.add_label(method_label)
                
                self.generate_body_code(method_record.get_method_body().get_statements_list())
                
                self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.RET), "return from method")
                #self.generate_method_code(method_record, method_label)        

        return self.program
    
    #returns register in which result is
    def generate_expression_code(self, expression_record):
        
        if isinstance(expression_record, decaf_ast.Auto_Expression):
            
            if expression_record.inc_dec == 'inc':
                delta_ins = decaf_ir.ArithmeticBinaryA3Instruction.Operation.ADD
            else:
                delta_ins = decaf_ir.ArithmeticBinaryA3Instruction.Operation.SUB
                
            if expression_record.post_pre == 'pre':
                
                expr = self.generate_expression_code(expression_record.operand_expression)
                self.program.add_instruction(decaf_ir.ArithmeticBinaryA3Instruction(expr, expr, 1, delta_ins, decaf_ir.DataType.INT))
                
                return  expression_record.operand_expression.get_var_name()
            
            else: #post
        
                old_reg = self.make_new_temp_var()        
                expr_reg = self.generate_expression_code(expression_record.operand_expression)
                
                self.program.add_instruction(decaf_ir.AssignA3Instruction(old_reg, expr_reg), "copy for postfix operator")
                
                self.program.add_instruction(decaf_ir.ArithmeticBinaryA3Instruction(expr_reg, expr_reg, 1, delta_ins, decaf_ir.DataType.INT))
                
                return old_reg
                
        if isinstance(expression_record, decaf_ast.Assign_Expression):
            
            if isinstance(expression_record.left_hand_side, decaf_ast.Field_Access_Expression):
                
                expr_reg = self.generate_expression_code(expression_record.right_hand_side)
                
                if isinstance(expression_record.left_hand_side.base_expression, decaf_ast.Class_Reference_Expression):
                    
                    #static field
                    offset = self.static_fields_to_offset_map[(expression_record.left_hand_side.base_expression.class_name, expression_record.left_hand_side.field_name)]
                        
                    self.program.add_instruction(decaf_ir.MemoryA3Instruction(decaf_ir.MemoryA3Instruction.Instruction.STORE, expr_reg, "sap", offset))
                    
                    return expr_reg
                else:    
                    base_expr_reg = self.generate_expression_code(expression_record.left_hand_side.base_expression)
                                    
                    self.program.add_instruction(decaf_ir.MemoryA3Instruction(decaf_ir.MemoryA3Instruction.Instruction.STORE, expr_reg, base_expr_reg, self.instance_field_id_to_offset_map[expression_record.left_hand_side.id_of_field]))

                    return expr_reg
                
            else:
            
                expr_reg = self.generate_expression_code(expression_record.right_hand_side)
    
                self.program.add_instruction(decaf_ir.AssignA3Instruction(expression_record.left_hand_side.get_var_name(), expr_reg))
                
                return expression_record.left_hand_side.get_var_name()
        
        
        if isinstance(expression_record, decaf_ast.Field_Access_Expression):
            
            reg = self.make_new_temp_var()
            if isinstance(expression_record.base_expression, decaf_ast.This_Expression):
                
                offset = self.get_instance_field_id_to_offset_map()[expression_record.id_of_field]
                
                self.program.add_instruction(decaf_ir.MemoryA3Instruction(decaf_ir.MemoryA3Instruction.Instruction.LOAD, reg, "a0", offset))
                
                return reg
            
            elif isinstance(expression_record.base_expression, decaf_ast.Class_Reference_Expression):
                
                offset = self.static_fields_to_offset_map[(expression_record.base_expression.class_name, expression_record.field_name)]
                
            
                self.program.add_instruction(decaf_ir.MemoryA3Instruction(decaf_ir.MemoryA3Instruction.Instruction.LOAD, reg, "sap", offset))
                
                return reg
                
                
            elif isinstance(expression_record.base_expression, decaf_ast.Variable_Reference):
                
                offset = self.instance_field_id_to_offset_map[expression_record.id_of_field]
                
                var_reg = expression_record.base_expression.var_name
                   
                self.program.add_instruction(decaf_ir.MemoryA3Instruction(decaf_ir.MemoryA3Instruction.Instruction.LOAD, reg, var_reg, offset))
     
                return reg
            else:
                raise Exception(f"cannot convert expression type")
                
            
        if isinstance(expression_record, decaf_ast.New_Object_Expression):
            
            class_record = self.ast.get_class_record(expression_record.class_name)
            constructor_id = class_record.get_id_from_method_name(expression_record.class_name)
             
            count = class_record.get_instance_field_count()
            
            heap_reg = self.make_new_temp_var()
        
            
            self.program.add_instruction(decaf_ir.MemoryAllocateA3Instruction(heap_reg, count))

            self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.PARAM, heap_reg))
            
            for param_index in range(0, len(expression_record.arguments)): 
                    a = self.generate_expression_code(expression_record.arguments[param_index])
                    
                    self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.PARAM, a))
            
            self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.CALL, f'C_{constructor_id}'))
                        
            return heap_reg
            
        
        if isinstance(expression_record, decaf_ast.Constant_Expression):
            
            new_type = decaf_ir.DataType.FLOAT if expression_record.type == decaf_typecheck.BaseType.FLOAT else decaf_ir.DataType.INT
            
            return decaf_ir.Constant(expression_record.val, new_type )
            
            
            
        if isinstance(expression_record, decaf_ast.Variable_Reference):
            
            return expression_record.var_name
        
        if isinstance(expression_record, decaf_ast.Unary_Expression):
            new_reg = self.make_new_temp_var()
            
            op_map = {decaf_ast.Operation.NEGATE : decaf_ir.UnaryInstruction.Operation.NEGATE, 
                      decaf_ast.Operation.UMINUS : decaf_ir.UnaryInstruction.Operation.UMINUS}
            
            self.program.add_instruction(decaf_ir.UnaryInstruction(new_reg, self.generate_expression_code(expression_record.expression), op_map[expression_record.operation]))
                
            return new_reg
    
        if isinstance(expression_record, decaf_ast.Binary_Expression):
    
            new_reg = self.make_new_temp_var()
            
            
            arith_ops = {
                decaf_ast.Operation.ADD : decaf_ir.ArithmeticBinaryA3Instruction.Operation.ADD, 
                decaf_ast.Operation.SUBTRACT : decaf_ir.ArithmeticBinaryA3Instruction.Operation.SUB,
                 decaf_ast.Operation.MULTIPLY : decaf_absmc.Instruction.IMUL, 
                 decaf_ast.Operation.DIVIDE : decaf_ir.ArithmeticBinaryA3Instruction.Operation.DIV}
            
            if expression_record.operation in arith_ops:
                
                left_reg = self.generate_expression_code(expression_record.left_expr)
                right_reg = self.generate_expression_code(expression_record.right_expr)
                
                if expression_record.get_type() == decaf_typecheck.BaseType.FLOAT:
                    
                    if expression_record.left_expr.get_type() == decaf_typecheck.BaseType.INT:
                        
                        conv_reg = self.make_new_temp_var()
                        
                        self.program.add_instruction(decaf_ir.CastA3Instruction(conv_reg, left_reg, decaf_ir.CastA3Instruction.CastType.INT_TO_FLOAT))
                                                
                        left_reg = conv_reg
                        
                    if expression_record.right_expr.get_type() == 'int':
                        conv_reg = self.make_new_temp_var()
                        
                        self.program.add_instruction(decaf_ir.CastA3Instruction(conv_reg, right_reg, decaf_ir.CastA3Instruction.CastType.INT_TO_FLOAT))
                        
                        right_reg = conv_reg
                
                self.program.add_instruction(decaf_ir.ArithmeticBinaryA3Instruction(new_reg, left_reg, right_reg, arith_ops[expression_record.operation], decaf_ir.DataType.INT))
                    
            if expression_record.operation == 'and':
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IMUL, [new_reg, self.generate_expression_code(expression_record.left_expr, cur_label, var_id_to_register_map), self.generate_expression_code(expression_record.right_expr, cur_label, var_id_to_register_map)], "logical and"])
                
            if expression_record.operation == 'or':
                
                one_const = self.get_next_tmp_register()
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.MOVE_IMMED_I, [one_const, str(1)], "#set to 1 for comparison"])
                
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IADD, [new_reg, self.generate_expression_code(expression_record.left_expr, cur_label, var_id_to_register_map), self.generate_expression_code(expression_record.right_expr, cur_label, var_id_to_register_map)], ""])
                
                
                
                self.program.append_instruction_to_labeled_section(cur_label, [decaf_absmc.Instruction.IGEQ, [new_reg, new_reg, one_const], ""])
                
                
            arith_comps = {"lt" : decaf_absmc.Instruction.ILT, "leq" : decaf_absmc.Instruction.ILEQ, "gt" : decaf_absmc.Instruction.IGT, "geq" : decaf_absmc.Instruction.IGEQ}
            
            arith_comps = {decaf_ast.Operation.LESSTHAN : decaf_ir.ArithmeticBinaryA3Instruction.Operation.LESS, decaf_ast.Operation.LESSOREQUAL :decaf_ir.ArithmeticBinaryA3Instruction.Operation.LESSEQ, decaf_ast.Operation.GREATERTHAN : decaf_ir.ArithmeticBinaryA3Instruction.Operation.GREATER, decaf_ast.Operation.GREATEROREQUAL : decaf_ir.ArithmeticBinaryA3Instruction.Operation.GREATEREQ}
                
            if expression_record.operation in arith_comps:
                
                self.program.add_instruction(decaf_ir.ArithmeticBinaryA3Instruction(new_reg,self.generate_expression_code(expression_record.left_expr), self.generate_expression_code(expression_record.right_expr) , arith_comps[expression_record.operation], decaf_ir.DataType.INT))
                
                
                
            if expression_record.operation == decaf_ast.Operation.EQUALS:
                
                left = self.generate_expression_code(expression_record.left_expr)
                right = self.generate_expression_code(expression_record.right_expr)
                
                self.program.add_instruction(decaf_ir.ArithmeticBinaryA3Instruction(new_reg, left, right, decaf_ir.ArithmeticBinaryA3Instruction.Operation.EQUALS, decaf_ir.DataType.INT))   
                    
            if expression_record.operation == decaf_ast.Operation.NOTEQUALS:
                left = self.generate_expression_code(expression_record.left_expr)
                right = self.generate_expression_code(expression_record.right_expr)
                
                self.program.add_instruction(decaf_ir.ArithmeticBinaryA3Instruction(new_reg, left, right, decaf_ir.ArithmeticBinaryA3Instruction.Operation.NOTEQUALS, decaf_ir.DataType.INT))   
            return new_reg
            
            
        
        if isinstance(expression_record, decaf_ast.Method_Call_Expression):
                   
            if isinstance(expression_record.base_expression, decaf_ast.Class_Reference_Expression):
                
                func_return_reg = self.make_new_temp_var()

                
                for param_index in range(0, len(expression_record.arguments)):
                    
                    arg_reg = self.generate_expression_code(expression_record.arguments[param_index])
                    
                    self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.PARAM, arg_reg))
                    
                
                call_label = f'M_{expression_record.method_name}_{expression_record.method_id}'
                
                
                self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.CALL, call_label))
                
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

                func_return_reg = self.make_new_temp_var()
                
                
                self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.PARAM, expression_record.base_expression.get_var_name()))
            
                
                for param_index in range(0, len(expression_record.arguments)):
                    a = self.generate_expression_code(expression_record.arguments[param_index])
                    
                    self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.PARAM, a))
                
                call_label = f'M_{expression_record.method_name}_{expression_record.method_id}'
                
                self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.CALL, call_label))

                
                self.program.add_instruction(decaf_ir.AssignA3Instruction(func_return_reg, 'RES'))
                            
                
            return func_return_reg   
    
        if isinstance(expression_record, decaf_ast.This_Expression):
            return "a0"
    
        raise Exception(f"Cannot convert expression: {expression_record}")
        
        
    
    def generate_body_code(self, statements : List):
        
        for index, statement in enumerate(statements):
            
            if isinstance(statement, decaf_ast.WriteStatement):                
                self.program.add_instruction(decaf_ir.SyscallA3Instruction("write", statement.data), "Print to console")
                

            if isinstance(statement, decaf_ast.For_Statement):
                
                (condition_label, body_label, update_label, end_label) = self.get_next_for_control_flow_labels()
                
                if isinstance(statement.initializer_expression, decaf_ast.Skip_Statement):
                    pass
                else:
                    if isinstance(statement.initializer_expression.get_expression(), decaf_ast.Assign_Expression):
                        init_expr_res_reg = self.generate_expression_code(statement.initializer_expression.get_expression())
                        
                    else:
                        raise Exception("Cannot convert expression")
                
                self.program.add_label(condition_label)
                                
                condition_reg = self.generate_expression_code(statement.loop_condition)
                
                if not isinstance(statement.loop_condition, decaf_ast.Skip_Statement):
                    self.program.add_instruction(decaf_ir.UnaryInstruction(condition_reg, condition_reg, decaf_ir.UnaryInstruction.Operation.NEGATE))
                    self.program.add_instruction(decaf_ir.JumpA3Instruction(end_label, condition_reg))
                    
                self.program.add_label(body_label)
                
                self.generate_body_code(statement.loop_body.get_statements_list())
                
                self.program.add_label(update_label)
                
                if isinstance(statement.update_expression, decaf_ast.Skip_Statement):
                    pass
                else:
                    self.generate_expression_code(statement.update_expression.get_expression())
                
                self.program.add_instruction(decaf_ir.JumpA3Instruction(condition_label, None))
                                
                self.program.add_label(end_label)
                
                
            
            if isinstance(statement, decaf_ast.While_Statement):
                
                (condition_label, body_label, end_label) = self.get_next_while_control_flow_labels()
                
                self.program.add_label(condition_label)
                
                condition_reg = self.generate_expression_code(statement.loop_condition)
                
                self.program.add_instruction(decaf_ir.UnaryInstruction(condition_reg, condition_reg, decaf_ir.UnaryInstruction.Operation.NEGATE))
                
                self.program.add_instruction(decaf_ir.JumpA3Instruction(end_label, condition_reg))    
                self.program.add_label(body_label)
                
                self.generate_body_code(statement.loop_body.get_statements_list())
                
                self.program.add_instruction(decaf_ir.JumpA3Instruction(condition_label,None))
                
                self.program.add_label(end_label)
      
                
            if isinstance(statement, decaf_ast.If_Statement):
                
                (then_label, else_label, end_label) = self.get_next_if_control_flow_labels()
                
                condition_reg = self.generate_expression_code(statement.if_expression)
                    
                
                self.program.add_instruction(decaf_ir.UnaryInstruction(condition_reg, condition_reg, decaf_ir.UnaryInstruction.Operation.NEGATE))
                
                self.program.add_instruction(decaf_ir.JumpA3Instruction(else_label, condition_reg))
                
                
                self.program.add_label(then_label)
                
                self.generate_body_code(statement.then_statement.get_statements_list())
                
                self.program.add_instruction(decaf_ir.JumpA3Instruction(end_label, None))
                
                
                self.program.add_label(else_label)
                
                if not isinstance(statement.else_statement, decaf_ast.Skip_Statement):
                    self.generate_body_code(statement.else_statement.get_statements_list())
                
                #self.program.append_label_to_labeled_section(cur_label, end_label, "else")
                self.program.add_label(end_label)
                             
            if isinstance(statement, decaf_ast.Expression_Statement):      
                self.generate_expression_code(statement.get_expression())
           
            
            if isinstance(statement, decaf_ast.Return_Statement):
                
                if not isinstance(statement.expression, decaf_ast.Skip_Statement): 
                    new_reg = self.generate_expression_code(statement.expression)     
    
                    self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.RET, new_reg))
                else:
                    
                
                    self.program.add_instruction(decaf_ir.ControlStackA3Instruction(decaf_ir.ControlStackA3Instruction.Instruction.RET))
 