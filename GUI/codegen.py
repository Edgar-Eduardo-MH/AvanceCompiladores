# codegen.py
import llvmlite.ir as ir
import llvmlite.binding as llvm

class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def define(self, name, value):
        self.symbols[name] = value

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

class CodeGenerator:
    def __init__(self):

        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        
        self.module = ir.Module(name="my_compiler")
        self.builder = None
        self.scope = Scope()

        # Tipos de LLVM que usaremos
        self.types = {
            'int': ir.IntType(32),
            'float': ir.FloatType(),
            'bool': ir.IntType(1),
            'string': ir.PointerType(ir.IntType(8)),
        }
        
        self.external_funcs = {}
        self.string_cache = {}
        
    def new_scope(self):
        self.scope = Scope(parent=self.scope)
        
    def exit_scope(self):
        self.scope = self.scope.parent

    def generate(self, node):
        """Punto de entrada principal para generar el código."""
        self.visit(node)
        return str(self.module)

    def visit(self, node):
        if node is None:
            return
        
        method_name = f'visit_{node.type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in getattr(node, 'children', []):
            self.visit(child)
    
    # Lectura y Escritura

    def _declare_printf(self):
        if "printf" not in self.external_funcs:
            printf_type = ir.FunctionType(self.types['int'], [self.types['string']], var_arg=True)
            self.external_funcs["printf"] = ir.Function(self.module, printf_type, name="printf")
        return self.external_funcs["printf"]
    
    def _declare_fflush(self):
        if "fflush" not in self.external_funcs:
            file_ptr_type = ir.PointerType(ir.IntType(8)) 
            fflush_type = ir.FunctionType(self.types['int'], [file_ptr_type])
            self.external_funcs["fflush"] = ir.Function(self.module, fflush_type, name="fflush")
        return self.external_funcs["fflush"]

    def _declare_scanf(self):
        if "scanf" not in self.external_funcs:
            scanf_type = ir.FunctionType(self.types['int'], [self.types['string']], var_arg=True)
            self.external_funcs["scanf"] = ir.Function(self.module, scanf_type, name="scanf")
        return self.external_funcs["scanf"]

    def _get_string_constant(self, value):
        if value in self.string_cache:
            return self.string_cache[value]
        
        value_with_null = value + '\0'
            
        c_str = ir.Constant(ir.ArrayType(ir.IntType(8), len(value_with_null)),
                            bytearray(value_with_null.encode("utf8")))
        
        global_name = f".str{abs(hash(value))}"
        global_str = ir.GlobalVariable(self.module, c_str.type, name=global_name)
        global_str.initializer = c_str
        global_str.global_constant = True
        
        ptr = global_str.bitcast(self.types['string'])
        self.string_cache[value] = ptr
        return ptr
    
    def visit_Program(self, node):
        func_type = ir.FunctionType(self.types['int'], [], False)
        self.main_func = ir.Function(self.module, func_type, name='main')
        
        entry_block = self.main_func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(entry_block)

        self.visit(node.children[0])

        self.builder.ret(ir.Constant(self.types['int'], 0))

    def visit_StatementList(self, node):
        self.generic_visit(node) 


    def visit_VariableDeclaration(self, node):
        var_type_name = node.children[0].value
        var_type = self.types.get(var_type_name, self.types['int'])

        for initializer in node.children[1:]:
            var_name = initializer.value if initializer.type == 'Identifier' else initializer.children[0].value
            
            # alloca reserva espacio en la pila (stack) para la variable
            # Devuelve un puntero a esa memoria.
            ptr = self.builder.alloca(var_type, name=var_name)
            
            # Guardar el *puntero* en nuestra tabla de símbolos
            self.scope.define(var_name, ptr)

            if initializer.type == 'Assignment':
                self.visit(initializer)

    def visit_Assignment(self, node):
        var_name = node.children[0].value
        expr_node = node.children[1]

        value = self.visit(expr_node)
        
        ptr = self.scope.lookup(var_name)
        
        if ptr:
            self.builder.store(value, ptr)
        else:
            print(f"Error de CodeGen: Puntero no encontrado para '{var_name}'")

    def visit_IfStatement(self, node):
        condition_node, then_block = node.children[0], node.children[1]
        else_block = node.children[2] if len(node.children) > 2 else None
        
        cond_val = self.visit(condition_node)

        then_bb = self.main_func.append_basic_block('then')
        else_bb = self.main_func.append_basic_block('else')
        merge_bb = self.main_func.append_basic_block('merge')
        
        self.builder.cbranch(cond_val, then_bb, else_bb)
        
        self.builder.position_at_start(then_bb)
        self.new_scope()
        self.visit(then_block)
        self.exit_scope()
        self.builder.branch(merge_bb) 
        
        self.builder.position_at_start(else_bb)
        if else_block:
            self.new_scope()
            self.visit(else_block)
            self.exit_scope()
        self.builder.branch(merge_bb)
        
        self.builder.position_at_start(merge_bb)

    def visit_WhileLoop(self, node):
        condition_node, body_block = node.children[0], node.children[1]

        header_bb = self.main_func.append_basic_block('loop_header')
        body_bb = self.main_func.append_basic_block('loop_body')
        after_bb = self.main_func.append_basic_block('after_loop')

        self.builder.branch(header_bb)
        self.builder.position_at_start(header_bb)
        
        cond_val = self.visit(condition_node)
        self.builder.cbranch(cond_val, body_bb, after_bb) # Saltar al body o salir

        self.builder.position_at_start(body_bb)
        self.new_scope()
        self.visit(body_block)
        self.exit_scope()
        self.builder.branch(header_bb) # Volver al header para re-evaluar

        self.builder.position_at_start(after_bb)

    def visit_DoUntilLoop(self, node):
        body_block, condition_node = node.children[0], node.children[1]

        body_bb = self.main_func.append_basic_block('do_body')
        header_bb = self.main_func.append_basic_block('do_header')
        after_bb = self.main_func.append_basic_block('after_do')
        
        self.builder.branch(body_bb)
        
        self.builder.position_at_start(body_bb)
        self.new_scope()
        self.visit(body_block)
        self.exit_scope()
        self.builder.branch(header_bb) # Ir a la condición
        
        self.builder.position_at_start(header_bb)
        cond_val = self.visit(condition_node)
        
        # cbranch(condición, si_true, si_false)
        self.builder.cbranch(cond_val, after_bb, body_bb)

        self.builder.position_at_start(after_bb)

    def visit_ForLoop(self, node):
        init_node, condition_node, increment_node, body_block = node.children

        header_bb = self.main_func.append_basic_block('for_header')
        body_bb = self.main_func.append_basic_block('for_body')
        inc_bb = self.main_func.append_basic_block('for_inc')
        after_bb = self.main_func.append_basic_block('after_for')

        self.new_scope() 
        self.visit(init_node)
        self.builder.branch(header_bb) # Saltar al header

        self.builder.position_at_start(header_bb)
        cond_val = self.visit(condition_node)
        self.builder.cbranch(cond_val, body_bb, after_bb)

        self.builder.position_at_start(body_bb)
        self.new_scope() # Ámbito separado para el cuerpo
        self.visit(body_block)
        self.exit_scope()
        self.builder.branch(inc_bb)

        self.builder.position_at_start(inc_bb)
        self.visit(increment_node)
        self.builder.branch(header_bb)

        self.builder.position_at_start(after_bb)
        self.exit_scope() 

    def visit_SwitchStatement(self, node):
        expr_node = node.children[0]
        case_clauses = node.children[1:]
        
        switch_val = self.visit(expr_node)
        
        end_bb = self.main_func.append_basic_block('switch_end')
        
        switch_inst = self.builder.switch(switch_val, end_bb, len(case_clauses))
        
        for case_node in case_clauses:
            case_val_node = case_node.children[0]
            case_body_node = case_node.children[1]
            
            case_bb = self.main_func.append_basic_block('case_')
            
            case_val = self.visit(case_val_node) 
            
            switch_inst.add_case(case_val, case_bb)
            
            self.builder.position_at_start(case_bb)
            self.new_scope()
            self.visit(case_body_node)
            self.exit_scope()
            self.builder.branch(end_bb) # 'break' implícito
        
        self.builder.position_at_start(end_bb)

    def visit_Output(self, node):
        printf = self._declare_printf()
        fflush = self._declare_fflush()
        null_ptr = ir.Constant(ir.PointerType(ir.IntType(8)), None)
        
        for child in node.children:
            value = self.visit(child)
            
            if isinstance(value.type, ir.FloatType):
                format_str = "%f\n"
            elif isinstance(value.type, ir.IntType) and value.type.width == 32:
                format_str = "%d\n"
            else: 
                format_str = "%s\n"
                
            format_str_ptr = self._get_string_constant(format_str)
            self.builder.call(printf, [format_str_ptr, value])

            self.builder.call(fflush, [null_ptr])

    def visit_Input(self, node):
        scanf = self._declare_scanf()
        var_name = node.children[0].value
        ptr = self.scope.lookup(var_name)
        
        if not ptr:
             print(f"Error de CodeGen: Puntero no encontrado para 'scanf >> {var_name}'")
             return
             
        if ptr.type.pointee == self.types['int']:
            format_str = "%d"
        elif ptr.type.pointee == self.types['float']:
            format_str = "%f"
        else:
            format_str = "%s"
            
        format_str_ptr = self._get_string_constant(format_str)
        self.builder.call(scanf, [format_str_ptr, ptr])



    def visit_Identifier(self, node):
        ptr = self.scope.lookup(node.value)
        return self.builder.load(ptr, name=node.value)

    def visit_Number(self, node):
        if '.' in node.value:
            return ir.Constant(self.types['float'], float(node.value))
        return ir.Constant(self.types['int'], int(node.value))

    def visit_Boolean(self, node):
        val = True if node.value == 'true' else False
        return ir.Constant(self.types['bool'], val)
        
    def visit_String(self, node):
        val = node.value[1:-1]
        return self._get_string_constant(val)

    def _handle_arithmetic(self, node, int_op, float_op):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])
        
        # Promoción de tipo: si uno es float, ambos deben ser float
        if left.type == self.types['float'] or right.type == self.types['float']:
            if left.type == self.types['int']:
                left = self.builder.sitofp(left, self.types['float'], 'fptmp')
            if right.type == self.types['int']:
                right = self.builder.sitofp(right, self.types['float'], 'fptmp')
            return getattr(self.builder, float_op)(left, right, 'foptmp')
        else:
            return getattr(self.builder, int_op)(left, right, 'ioptmp')

    def visit_AddExpression(self, node):
        op = 'add' if node.value == '+' else 'sub'
        f_op = 'fadd' if node.value == '+' else 'fsub'
        return self._handle_arithmetic(node, op, f_op)
    
    def _declare_pow(self):
        if "pow" not in self.external_funcs:
            # Tipo: float pow(float, float)
            pow_type = ir.FunctionType(self.types['float'], [self.types['float'], self.types['float']])
            self.external_funcs["pow"] = ir.Function(self.module, pow_type, name="pow")
        return self.external_funcs["pow"]

    def visit_MulExpression(self, node):
        
        if node.value == '*':
            return self._handle_arithmetic(node, 'mul', 'fmul')
        elif node.value == '/':
            return self._handle_arithmetic(node, 'sdiv', 'fdiv') # sdiv = signed division
        elif node.value == '%':
            # srem = signed remainder, frem = float remainder
            return self.handle_arithmetic(node, 'srem', 'frem')
            
        elif node.value == '^':
            # La potencia siempre la manejaremos con floats
            pow_func = self._declare_pow()
            
            left = self.visit(node.children[0])
            right = self.visit(node.children[1])
            
            # Convertir ambos a float si no lo son
            if left.type == self.types['int']:
                left = self.builder.sitofp(left, self.types['float'], 'fptmp')
            if right.type == self.types['int']:
                right = self.builder.sitofp(right, self.types['float'], 'fptmp')
                
            return self.builder.call(pow_func, [left, right], 'powtmp')
        
    def visit_RelationalExpression(self, node):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])
        
        is_float_op = False
        if left.type == self.types['float'] and right.type == self.types['int']:
            right = self.builder.sitofp(right, self.types['float'], 'fptmp') # sitofp = Signed Int to Floating Point
            is_float_op = True
        elif left.type == self.types['int'] and right.type == self.types['float']:
            left = self.builder.sitofp(left, self.types['float'], 'fptmp')
            is_float_op = True
        elif left.type == self.types['float'] and right.type == self.types['float']:
            is_float_op = True
            
        if is_float_op:
            # fcmp = floating point comparison
            return self.builder.fcmp_ordered(node.value, left, right, 'fcmptmp')
        else:
            # icmp = integer comparison
            return self.builder.icmp_signed(node.value, left, right, 'icmptmp')