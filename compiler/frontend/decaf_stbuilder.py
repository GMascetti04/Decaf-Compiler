import frontend.decaf_st as decaf_st
import frontend.decaf_ast as decaf_ast
import frontend.decaf_typecheck as decaf_typecheck

class ASTChecker(decaf_ast.ASTVisitor):
    
    def __init__(self, ast : decaf_ast.AST):
        self.symbol_table : decaf_st.ProgramSymbolTable = decaf_st.ProgramSymbolTable()
        self.ast : decaf_ast.AST = ast
        self.local_var_id : int = 0
        
    def get_local_var_id(self) -> int:
        res = self.local_var_id
        self.local_var_id += 1
        return res
        
    def reset_local_var_id(self):
        self.local_var_id = 0
    
        
    def construct_function_symbol_table(self, function_record : decaf_ast.FunctionRecord) -> decaf_st.FunctionSymbolTable:
        function_table = decaf_st.FunctionSymbolTable(function_record.get_name())
        self.reset_local_var_id()
        
        #parameters and the local varialbes in the outer most scope would be in the same scope
        for param in function_record.get_parameters():
            
            function_table.add_symbol(decaf_st.SymbolEntry(param.get_name(), decaf_st.SymbolType.PARAM, None, None, self.get_local_var_id(), param.get_type()))
            
        for statement in function_record.get_body().get_statements_list():
            if isinstance(statement, decaf_ast.Variable_Declaration):
                function_table.add_symbol(decaf_st.SymbolEntry(statement.get_name(), decaf_st.SymbolType.VAR, None, None, self.get_local_var_id(), statement.get_type()))
        
        
        return function_table
        
        
    def construct_class_symbol_table(self, class_record : decaf_ast.Class_Record) -> decaf_st.ClassSymbolTable:
        class_table = decaf_st.ClassSymbolTable(class_record.get_name())
        
        for field in class_record.get_fields():
            class_table.add_symbol(decaf_st.SymbolEntry(field.get_name(), decaf_st.SymbolType.FIELD, field.get_visibility(), field.get_applicability(), field.get_id(), None))

        for constructor in class_record.get_constructors():
            
            class_table.add_symbol(decaf_st.SymbolEntry(class_record.get_name(), decaf_st.SymbolType.CONSTRUCTOR, constructor.get_visibility(), None, constructor.get_id(), None))
            
        for method in class_record.get_method_records():
            #iterave over constructor parameters
            param_type_list = []
            for param in method.get_parameters():
                if isinstance(param.get_type(), decaf_typecheck.BaseType):
                    param_type_list.append(param.get_type())
                elif isinstance(param.get_type(), decaf_typecheck.ClassObjectType):
                    if self.symbol_table.is_class_name_present(param.get_type().get_class_name()):
                        param_type_list.append(param.get_type())
                    else:
                        raise Exception(f"Class name {param.get_type().get_class_name()} does not exist")
                else:
                    raise Exception("not supported")
                
            if isinstance(method.get_return_type(), decaf_typecheck.BaseType):
                ret_type = method.get_return_type()
            elif isinstance(method.get_return_type(), decaf_typecheck.ClassObjectType):
                if self.symbol_table.is_class_name_present(param.get_type().get_class_name()):
                    ret_type = param.get_type()
                else:
                    raise Exception(f"Class name {param.get_type().get_class_name()} does not exist")
                    
            t = decaf_st.MethodType([x.get_type() for x in method.get_parameters()], method.get_return_type())
            class_table.add_symbol(decaf_st.SymbolEntry(method.get_name(), decaf_st.SymbolType.METHOD, method.get_visibility(), method.get_applicability(), method.get_id(), t))
            
            #self.construct_function_symbol_table(method)
            
            
            
        return class_table
    
    #results in symbol table being constructed 
    def construct_symbol_table(self):
        
        #step 1: put all of the class names     
        class_records = self.ast.get_class_records()
        for class_record in class_records:
            self.symbol_table.add_class(class_record.get_name())
        
        #step 2: do all fields and methods name/types
        for class_record in class_records:
            self.symbol_table.add_child(self.construct_class_symbol_table(class_record))
            
            
        for class_record in class_records:
            class_table = self.symbol_table.get_table_for_class(class_record.get_name())
            for method in class_record.get_method_records():
                class_table.add_child(self.construct_function_symbol_table(method))
            
        #print(self.symbol_table)
            
        
        pass
    
    #def resolve_block_statement(self, block : decaf_ast.BlockStatement):
     #   for statment in block.get_statements_list():
     
    def visit_identifier(self, identifier_ref_expr : decaf_ast.IdentifierReference):
        
        
        lookup_name = identifier_ref_expr.get_name()
        
        e = self.symbol_table.cur_scope_table.look_up_local_variable(lookup_name)
        
        if e == None:
            
            if self.symbol_table.is_class_name_present(lookup_name) == True:
                
                r = decaf_ast.Class_Reference_Expression(lookup_name)
                
                identifier_ref_expr.set_identifier(r)
            else:
            
                raise Exception(f"Could not find symbol with name: {lookup_name} {identifier_ref_expr}")
        else:
            r = decaf_ast.Variable_Reference(lookup_name)
            r.set_id(e.id)
            r.set_type(e.data_type)
        
            identifier_ref_expr.set_identifier(r)
        
        
     
    def visit_variable_reference_expression(self, var_ref_exp : decaf_ast.Variable_Reference):
        var_name = var_ref_exp.get_var_name()
        
        e = self.symbol_table.cur_scope_table.look_up_local_variable(var_name)
 
        if e == None:
            print(self.symbol_table.cur_scope_table)
            print(f'var name: {var_name}')

        var_ref_exp.set_id(e.id)

    def visit_binary_expression(self, bin_expr : decaf_ast.Binary_Expression):
        
        bin_expr.get_left_expression().accept(self)
        bin_expr.get_right_expression().accept(self)
        
        bin_expr.set_type(bin_expr.get_right_expression().get_type())
        
    def visit_constant_expression(self, const_expr : decaf_ast.Constant_Expression):
        pass
    
    def visit_assign_expression(self, assign_expr : decaf_ast.Assign_Expression):
        assign_expr.get_left_expression().accept(self)
        assign_expr.get_right_expression().accept(self)

    def visit_method_call_expr(self, method_call_expr : decaf_ast.Method_Call_Expression):
        args = method_call_expr.get_args()
        for argument in args:
            argument.accept(self)
            
        method_call_expr.get_base_expression().accept(self)
        
        method_name = method_call_expr.get_method_name()
        
        base_type = method_call_expr.get_base_expression().get_type()
        
        if isinstance(base_type, decaf_typecheck.ClassLiteralType):
            
            entry = self.symbol_table.get_class_function(base_type.class_name, method_name)

            method_call_expr.set_id(entry.id)
            
            method_call_expr.set_type(entry.data_type.return_type)
        
        
            
            
        
        

    def visit_auto_expr(self, auto_expr : decaf_ast.Auto_Expression):
        auto_expr.get_expression().accept(self)
     
    def visit_return_statement(self, ret_stmnt : decaf_ast.Return_Statement):
        ret_stmnt.get_expression().accept(self)
     
    def visit_for_statement(self, for_stmnt : decaf_ast.For_Statement):
        for_stmnt.get_initializer_expression().accept(self)
        for_stmnt.get_loop_condition().accept(self)
        for_stmnt.get_update_expression().accept(self)
        for_stmnt.get_loop_body().accept(self)
     
    def visit_expression_statement(self, expr_stmnt : decaf_ast.Expression_Statement):
        expr_stmnt.get_expression().accept(self)
     
    def visit_if_statement(self, if_statement : decaf_ast.If_Statement):
        if_statement.get_if_expression().accept(self)
        if_statement.get_then_statement().accept(self)
            
    def visit_write_statement(self, write_stmnt : decaf_ast.WriteStatement):
        
        expr = write_stmnt.get_data()
        expr.accept(self)
        
        
        
            
    def visit_block_statement(self, block_stmnt : decaf_ast.BlockStatement):
        for statement in block_stmnt.get_statements_list():
            if isinstance(statement, decaf_ast.Variable_Declaration):
                continue
            statement.accept(self)
    
    #will resolve names in functions (local variables)
    def resolve_names(self):
        
        class_records = self.ast.get_class_records()
        
        for class_record in class_records:
            
            self.symbol_table.set_scope_in_class(class_record.get_name())
            
            if not self.symbol_table.is_class_name_present(class_record.get_name()):
                raise Exception("BAD")
            
            
            
            
            methods = class_record.get_method_records()
            for method in methods:
                
                self.symbol_table.enter_method_scope(method.get_name())
                
                method.get_body().accept(self)
                
                self.symbol_table.exit_method_scope()
                #self.resolve_block_statement(method.get_body())
                
            self.symbol_table.exit_class_scope()
        
        
    
    
    pass