import re

# Definición de colores para cada tipo de token
COLORS = {
    'number': '#FFB86C',
    'identifier': '#17FFFF',
    'comment': '#4B4B4B',
    'keyword': '#CB47B5',
    'arithmetic_operator': '#F772FF',
    'logical_relational_operator': '#F772FF',
    'symbol': '#66FF00',
    'assignment': '#FFB300'
}

# Palabras reservadas del lenguaje
KEYWORDS = {
    'if', 'else', 'do', 'while', 'switch', 'case', 'int', 'end', 'float', 'main', 'until',
    'for', 'foreach', 'double', 'char', 'string', 'break', 'continue', 'return', 'then',
    'cin', 'cout', 'true', 'false'
}

DATA_TYPES = {'int', 'float', 'bool', 'string', 'char', 'double'}

# Patrones para los distintos tipos de tokens
PATTERNS = [
    ('multiline_comment', r'/\*[\s\S]*?\*/'),
    ('singleline_comment', r'#.*'),
    ('shift_op', r'<<|>>'),
    ('logical_op', r'\|\||&&'),
    ('relational_op', r'==|!=|<=|>=|<|>'),
    ('inc_dec_op', r'\+\+|--'),
    ('add_op', r'\+|-'),
    ('mul_op', r'\*|/|%'),
    ('pow_op', r'\^'),
    ('real_number', r'(?<![A-Za-z0-9_])[-+]?\d+\.\d+(?![\d])'),
    ('invalid_real_number', r'(?<![A-Za-z0-9_])[-+]?\d+\.(?!\d)'),
    ('integer_number', r'(?<![A-Za-z0-9_])[-+]?\d+(?![\d.])'),
    ('string', r'"[^"\n]*"'),
    ('char', r"'([^'\\]|\\.)'"),
    ('assignment', r'='),
    ('symbol', r'[\(\)\{\},;]'),
    ('identifier', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('whitespace', r'\s+'),
]

COMPILED_PATTERNS = [(token_type, re.compile(pattern)) for token_type, pattern in PATTERNS]

def lexical_analyzer(source_code):
    tokens = []
    line = 1
    column = 1
    position = 0
    while position < len(source_code):
        match = None
        for token_type, regex in COMPILED_PATTERNS:
            match = regex.match(source_code, position)
            if match:
                text = match.group(0)
                if token_type == 'whitespace':
                    newlines = text.count('\n')
                    if newlines > 0:
                        line += newlines
                        column = len(text.rsplit('\n', 1)[-1]) + 1
                    else:
                        column += len(text)
                    position = match.end()
                    break
                real_type = token_type
                if token_type == 'identifier' and text in KEYWORDS:
                    real_type = 'keyword'
                elif token_type.startswith('invalid_real'):
                    real_type = 'invalid'
                if real_type in ['multiline_comment', 'singleline_comment']:
                    newlines = text.count('\n')
                    if newlines > 0:
                        line += newlines
                        column = len(text.rsplit('\n', 1)[-1]) + 1
                    else:
                        column += len(text)
                else:
                    color = COLORS.get(real_type, '#FFFFFF')
                    tokens.append((real_type, text, color, line, column))
                    column += len(text)
                position = match.end()
                break
        if not match:
            text = source_code[position]
            tokens.append(('invalid', text, '#FF0000', line, column))
            if text == '\n':
                line += 1
                column = 1
            else:
                column += 1
            position += 1
    return tokens

class ASTNode:
    def __init__(self, type, value=None, line=None, column=None, children=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.children = children if children is not None else []
    def __str__(self):
        location = f" (L:{self.line},C:{self.column})" if self.line is not None else ""
        if self.value:
            return f"{self.type}: {self.value}{location}"
        return f"{self.type}{location}"

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t[0] not in ('multiline_comment', 'singleline_comment')]
        self.pos = 0
        self.errors = []
    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def match(self, expected_type, expected_value=None):
        token = self.current_token()
        if token and token[0] == expected_type and (expected_value is None or token[1] == expected_value):
            self.pos += 1
            return token
        else:
            if token:
                expected = f"{expected_type} '{expected_value}'" if expected_value else expected_type
                self.errors.append(f"Syntax error: expected {expected}, found '{token[1]}' at line {token[3]}, column {token[4]}")
            else:
                last_token = self.tokens[-1] if self.tokens else (None, None, None, 1, 1)
                self.errors.append(f"Syntax error: unexpected end of input, expected {expected_type} at line {last_token[3]}")
            return None
    def parse(self):
        return self.program()
    def program(self):
        main_token = self.current_token()
        if not (self.match('keyword', 'int') and self.match('keyword', 'main') and self.match('symbol', '(') and self.match('symbol', ')')):
             self.errors.append("Syntax Error: Program must start with 'int main()'.")
             return ASTNode('Error')
        if not self.match('symbol', '{'):
            self.errors.append("Syntax error: expected '{' after 'int main()'")
            return ASTNode('Error')
        stmts = self.statement_list()
        if not self.match('symbol', '}'):
            self.errors.append("Syntax Error: Expected '}' at the end of the program.")
        return ASTNode('Program', children=[stmts], line=main_token[3] if main_token else None, column=main_token[4] if main_token else None)
    def statement_list(self):
        children = []
        initial_token = self.current_token()
        line, column = (initial_token[3], initial_token[4]) if initial_token else (None, None)
        while self.current_token() and self.current_token()[1] not in ('}', 'end', 'else', 'until'):
            stmt = self.statement()
            if stmt and stmt.type != 'Error':
                children.append(stmt)
            elif self.current_token(): 
                self.pos += 1 
            else:
                break
        return ASTNode('StatementList', children=children, line=line, column=column)
    def statement(self):
        token = self.current_token()
        if not token: return None
        if token[0] == 'keyword' and token[1] in DATA_TYPES:
            return self.variable_declaration()
        if self.lookahead_inc_dec():
            return self.inc_dec_statement()
        if token[1] == 'if':
            return self.selection()
        elif token[1] == 'while':
            return self.iteration()
        elif token[1] == 'do':
            return self.repetition()
        elif token[1] == 'cin':
            return self.input_statement()
        elif token[1] == 'cout':
            return self.output_statement()
        elif token[0] == 'identifier':
            return self.assignment()
        else:
            self.errors.append(f"Unknown statement starting with '{token[1]}' at line {token[3]}, column {token[4]}")
            self.pos += 1 
            return ASTNode('Error', line=token[3], column=token[4])
    def variable_declaration(self):
        type_token = self.match('keyword')
        if not type_token: return None
        type_node = ASTNode('Type', value=type_token[1], line=type_token[3], column=type_token[4])
        initializers = self.initializer_list()
        if not self.match('symbol', ';'):
            return ASTNode('Error')
        return ASTNode('VariableDeclaration', children=[type_node] + initializers, line=type_token[3], column=type_token[4])
    def initializer_list(self):
        initializers = [self.initializer()]
        while self.current_token() and self.current_token()[1] == ',':
            self.match('symbol', ',')
            init = self.initializer()
            if init and init.type != 'Error':
                initializers.append(init)
            else:
                self.errors.append("Syntax Error: Expected identifier after ','.")
                return [ASTNode('Error')]
        return initializers
    def initializer(self):
        id_token = self.match('identifier')
        if not id_token: return None
        identifier_node = ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4])
        if self.current_token() and self.current_token()[0] == 'assignment':
            self.match('assignment')
            expr_node = self.logical_expression()
            if not expr_node or expr_node.type == 'Error':
                return ASTNode('Error')
            return ASTNode('Assignment', children=[identifier_node, expr_node], line=id_token[3], column=id_token[4])
        return identifier_node
    def selection(self):
        if_token = self.match('keyword', 'if')
        if not if_token: return ASTNode('Error')
        condition = self.logical_expression()
        if not condition: return ASTNode('Error')
        if not self.match('keyword', 'then'): return ASTNode('Error')
        then_block = self.statement_list()
        else_block = None
        if self.current_token() and self.current_token()[1] == 'else':
            self.match('keyword', 'else')
            else_block = self.statement_list()
        if not self.match('keyword', 'end'): return ASTNode('Error')
        children = [condition, ASTNode('ThenBlock', children=then_block.children, line=then_block.line)]
        if else_block:
            children.append(ASTNode('ElseBlock', children=else_block.children, line=else_block.line))
        return ASTNode('IfStatement', children=children, line=if_token[3], column=if_token[4])
    def iteration(self):
        while_token = self.match('keyword', 'while')
        if not while_token: return ASTNode('Error')
        condition = self.logical_expression()
        if not condition: return ASTNode('Error')
        if not self.match('keyword', 'then'): return ASTNode('Error')
        body = self.statement_list()
        if not self.match('keyword', 'end'): return ASTNode('Error')
        return ASTNode('WhileLoop', children=[condition, body], line=while_token[3], column=while_token[4])
    def repetition(self):
        do_token = self.match('keyword', 'do')
        if not do_token: return ASTNode('Error')
        body = self.statement_list()
        if not self.match('keyword', 'until'): return ASTNode('Error')
        condition = self.logical_expression()
        if not condition: return ASTNode('Error')
        if self.current_token() and self.current_token()[1] == ';':
            self.match('symbol', ';')
        return ASTNode('DoUntilLoop', children=[body, condition], line=do_token[3], column=do_token[4])
    def lookahead_inc_dec(self):
        token = self.current_token()
        next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
        return token and token[0] == 'identifier' and next_token and next_token[0] == 'inc_dec_op'
    def inc_dec_statement(self):
        id_token = self.match('identifier')
        op_token = self.match('inc_dec_op')
        if not (id_token and op_token and self.match('symbol', ';')):
            return ASTNode('Error')
        op_symbol = '+' if op_token[1] == '++' else '-'
        id_node = ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4])
        one_node = ASTNode('Number', value='1', line=op_token[3], column=op_token[4])
        expr = ASTNode('AddExpression', value=op_symbol, children=[id_node, one_node])
        return ASTNode('Assignment', children=[id_node, expr], line=id_token[3], column=id_token[4])
    def assignment(self):
        id_token = self.match('identifier')
        if not (id_token and self.match('assignment')): return ASTNode('Error')
        expr = self.logical_expression()
        if not (expr and self.match('symbol', ';')): return ASTNode('Error')
        return ASTNode('Assignment', children=[ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4]), expr], line=id_token[3], column=id_token[4])
    def input_statement(self):
        cin_token = self.match('keyword', 'cin')
        if not (cin_token and self.match('shift_op', '>>')): return ASTNode('Error')
        id_token = self.match('identifier')
        if not (id_token and self.match('symbol', ';')): return ASTNode('Error')
        return ASTNode('Input', children=[ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4])], line=cin_token[3], column=cin_token[4])
    def output_statement(self):
        cout_token = self.match('keyword', 'cout')
        if not (cout_token and self.match('shift_op', '<<')): return ASTNode('Error')
        children = []
        while True:
            expr_node = self.logical_expression()
            if not expr_node: return ASTNode('Error')
            children.append(expr_node)
            if self.current_token() and self.current_token()[1] == '<<':
                self.match('shift_op', '<<')
            else:
                break
        if not self.match('symbol', ';'): return ASTNode('Error')
        return ASTNode('Output', children=children, line=cout_token[3], column=cout_token[4])
    def logical_expression(self):
        node = self.expression()
        while self.current_token() and self.current_token()[0] == 'logical_op':
            op_token = self.match('logical_op')
            right = self.expression()
            node = ASTNode('LogicalExpression', value=op_token[1], children=[node, right], line=op_token[3], column=op_token[4])
        return node
    def expression(self):
        left = self.simple_expression()
        if self.current_token() and self.current_token()[0] == 'relational_op':
            op_token = self.match('relational_op')
            right = self.simple_expression()
            return ASTNode('RelationalExpression', value=op_token[1], children=[left, right], line=op_token[3], column=op_token[4])
        return left
    def simple_expression(self):
        node = self.term()
        while self.current_token() and self.current_token()[0] == 'add_op':
            op_token = self.match('add_op')
            right = self.term()
            node = ASTNode('AddExpression', value=op_token[1], children=[node, right], line=op_token[3], column=op_token[4])
        return node
    def term(self):
        node = self.factor()
        while self.current_token() and self.current_token()[0] == 'mul_op':
            op_token = self.match('mul_op')
            right = self.factor()
            node = ASTNode('MulExpression', value=op_token[1], children=[node, right], line=op_token[3], column=op_token[4])
        return node
    def factor(self):
        node = self.component()
        while self.current_token() and self.current_token()[0] == 'pow_op':
            op_token = self.match('pow_op')
            right = self.component()
            node = ASTNode('PowExpression', value=op_token[1], children=[node, right], line=op_token[3], column=op_token[4])
        return node
    def component(self):
        token = self.current_token()
        if not token: return ASTNode('Error')
        if token[1] == '(':
            self.match('symbol', '(')
            expr = self.logical_expression()
            self.match('symbol', ')')
            return expr
        elif token[0] in ('integer_number', 'real_number'):
            self.pos += 1
            return ASTNode('Number', value=token[1], line=token[3], column=token[4])
        elif token[0] in ('string', 'char'):
            self.pos += 1
            node_type = 'String' if token[0] == 'string' else 'Char'
            return ASTNode(node_type, value=token[1], line=token[3], column=token[4])
        elif token[0] == 'identifier':
            self.pos += 1
            return ASTNode('Identifier', value=token[1], line=token[3], column=token[4])
        elif token[1] in ('true', 'false'):
            self.pos += 1
            return ASTNode('Boolean', value=token[1], line=token[3], column=token[4])
        else:
            self.errors.append(f"Invalid expression component '{token[1]}' at line {token[3]}, column {token[4]}")
            self.pos += 1
            return ASTNode('Error')

class SymbolTable:
    def __init__(self):
        self.scope_stack = [{'__name__': 'global'}] 
        self.memory_address_counter = 0
        self.persistent_symbols = {}
    def enter_scope(self, name='block'):
        self.scope_stack.append({'__name__': name})
    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
    def get_current_scope_name(self):
        return self.scope_stack[-1]['__name__']
    def define(self, name, symbol_type, line, column):
        current_scope = self.scope_stack[-1]
        if name in current_scope:
            return False
        address = self.memory_address_counter
        self.memory_address_counter += 4
        symbol_data = {
            'name': name,
            'type': symbol_type, 
            'value': None, 
            'scope': self.get_current_scope_name(), 
            'line': line, 
            'column': column, 
            'memory_address': address
        }
        current_scope[name] = symbol_data
        self.persistent_symbols[address] = symbol_data
        return True
    
    # --- CAMBIO CLAVE: Se actualiza el valor en ambos registros ---
    def update_value(self, name, value):
        """Actualiza el valor de un símbolo en el ámbito activo Y en el registro persistente."""
        for scope in reversed(self.scope_stack):
            if name in scope:
                # Actualiza el valor en el ámbito activo (scope_stack)
                scope[name]['value'] = value
                
                # Actualiza también el registro persistente usando la dirección de memoria
                if 'memory_address' in scope[name]:
                    address = scope[name]['memory_address']
                    if address in self.persistent_symbols:
                        self.persistent_symbols[address]['value'] = value
                
                return True
        return False

    def lookup(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    def get_historical_symbols(self):
        return dict(sorted(self.persistent_symbols.items()))

class SemanticAnalyzer:
    def __init__(self, ast_root):
        self.ast = ast_root
        self.symbol_table = SymbolTable()
        self.errors = []
        self.log = []
    def analyze(self):
        if self.ast and self.ast.type != 'Error':
            self.visit(self.ast)
        return self.errors
    def visit(self, node):
        if not node or node.type == 'Error':
            return 'error_type', None
        method_name = f'visit_{node.type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)
    def add_error(self, message, line, column):
        self.errors.append(f"Semantic Error: {message} (Line: {line}, Column: {column})")
    def visit_Program(self, node):
        self.generic_visit(node)
    def visit_StatementList(self, node):
        self.generic_visit(node)
    def visit_ThenBlock(self, node):
        self.generic_visit(node)
    def visit_ElseBlock(self, node):
        self.generic_visit(node)
    def visit_IfStatement(self, node):
        condition_node, then_block = node.children[0], node.children[1]
        self.log.append("\nRegla: Analizando sentencia IF.")
        condition_type, _ = self.visit(condition_node)
        self.log.append(f" -> Condición evaluada a tipo: '{condition_type}'.")
        if condition_type != 'bool' and condition_type != 'error_type':
            self.add_error(f"If statement condition must be boolean, but got '{condition_type}'.", condition_node.line, condition_node.column)
        self.log.append("Acción: Entrando en ámbito 'if'.")
        self.symbol_table.enter_scope('if')
        self.visit(then_block)
        self.symbol_table.exit_scope()
        self.log.append("Acción: Saliendo de ámbito 'if'.")
        if len(node.children) > 2:
            else_block = node.children[2]
            self.log.append("Acción: Entrando en ámbito 'else'.")
            self.symbol_table.enter_scope('else')
            self.visit(else_block)
            self.symbol_table.exit_scope()
            self.log.append("Acción: Saliendo de ámbito 'else'.")
    def visit_WhileLoop(self, node):
        condition_node, body_block = node.children[0], node.children[1]
        self.log.append("\nRegla: Analizando bucle WHILE.")
        condition_type, _ = self.visit(condition_node)
        self.log.append(f" -> Condición evaluada a tipo: '{condition_type}'.")
        if condition_type != 'bool' and condition_type != 'error_type':
            self.add_error(f"While loop condition must be boolean, but got '{condition_type}'.", condition_node.line, condition_node.column)
        self.log.append("Acción: Entrando en ámbito 'while'.")
        self.symbol_table.enter_scope('while')
        self.visit(body_block)
        self.symbol_table.exit_scope()
        self.log.append("Acción: Saliendo de ámbito 'while'.")
    def visit_DoUntilLoop(self, node):
        body_block, condition_node = node.children[0], node.children[1]
        self.log.append("\nRegla: Analizando bucle DO-UNTIL.")
        self.log.append("Acción: Entrando en ámbito 'do-until'.")
        self.symbol_table.enter_scope('do-until')
        self.visit(body_block)
        self.symbol_table.exit_scope()
        self.log.append("Acción: Saliendo de ámbito 'do-until'.")
        condition_type, _ = self.visit(condition_node)
        self.log.append(f" -> Condición evaluada a tipo: '{condition_type}'.")
        if condition_type != 'bool' and condition_type != 'error_type':
            self.add_error(f"Do-until loop condition must be boolean, but got '{condition_type}'.", condition_node.line, condition_node.column)
    def visit_VariableDeclaration(self, node):
        var_type = node.children[0].value
        for initializer_node in node.children[1:]:
            if initializer_node.type == 'Assignment':
                var_name = initializer_node.children[0].value
                self.log.append(f"\nRegla: Declaración de '{var_name}' con inicialización.")
                if not self.symbol_table.define(var_name, var_type, initializer_node.line, initializer_node.column):
                    self.add_error(f"Variable '{var_name}' already declared in this scope.", initializer_node.line, initializer_node.column)
                else:
                    self.log.append(f"Acción: Símbolo '{var_name}' añadido a la tabla en ámbito '{self.symbol_table.get_current_scope_name()}'.")
                expr_type, expr_value = self.visit(initializer_node.children[1])
                self.log.append(f" -> Verificando asignación: Esperado '{var_type}', Obtenido '{expr_type}'.")
                is_compatible = (expr_type == var_type or (var_type == 'float' and expr_type == 'int') or (var_type == 'string' and expr_type == 'char'))
                if not is_compatible and expr_type != 'error_type':
                    self.add_error(f"Type mismatch: Cannot assign '{expr_type}' to '{var_name}' of type '{var_type}'.", initializer_node.line, initializer_node.column)
                elif expr_type != 'error_type':
                    self.symbol_table.update_value(var_name, expr_value)
                    self.log.append(f" -> Resultado: Tipos compatibles. Valor actualizado.")
            elif initializer_node.type == 'Identifier':
                var_name = initializer_node.value
                self.log.append(f"\nRegla: Declaración de variable '{var_name}'.")
                if not self.symbol_table.define(var_name, var_type, initializer_node.line, initializer_node.column):
                    self.add_error(f"Variable '{var_name}' already declared in this scope.", initializer_node.line, initializer_node.column)
                else:
                    self.log.append(f"Acción: Símbolo '{var_name}' añadido a la tabla en ámbito '{self.symbol_table.get_current_scope_name()}'.")
    def visit_Assignment(self, node):
        var_name = node.children[0].value
        self.log.append(f"\nRegla: Analizando asignación para '{var_name}'.")
        symbol = self.symbol_table.lookup(var_name)
        if not symbol:
            self.add_error(f"Variable '{var_name}' is not declared.", node.children[0].line, node.children[0].column)
            return ('error_type', None)
        expr_type, expr_value = self.visit(node.children[1])
        if expr_type == 'error_type': return ('error_type', None)
        expected_type = symbol['type']
        self.log.append(f" -> Verificando tipos: Esperado '{expected_type}', Obtenido '{expr_type}'.")
        is_compatible = (expr_type == expected_type or (expected_type == 'float' and expr_type == 'int') or (expected_type == 'string' and expr_type == 'char'))
        if not is_compatible:
            self.add_error(f"Type mismatch. Cannot assign type '{expr_type}' to '{var_name}' of type '{expected_type}'.", node.line, node.column)
        else:
            self.symbol_table.update_value(var_name, expr_value)
            self.log.append(f" -> Resultado: Tipos compatibles. Valor actualizado.")
        return expected_type, expr_value
    def visit_Input(self, node):
        var_name = node.children[0].value
        if not self.symbol_table.lookup(var_name):
            self.add_error(f"Variable '{var_name}' for input is not declared.", node.children[0].line, node.children[0].column)
        else:
            self.symbol_table.update_value(var_name, '<input>')
    def visit_Output(self, node):
        self.generic_visit(node)
    def visit_LogicalExpression(self, node):
        left_type, _ = self.visit(node.children[0])
        right_type, _ = self.visit(node.children[1])
        if left_type == 'bool' and right_type == 'bool':
            return 'bool', None
        if left_type != 'error_type' and right_type != 'error_type':
            self.add_error(f"Unsupported operand types for '{node.value}': '{left_type}' and '{right_type}'. Both must be boolean.", node.line, node.column)
        return 'error_type', None
    def visit_RelationalExpression(self, node):
        left_type, _ = self.visit(node.children[0])
        right_type, _ = self.visit(node.children[1])
        if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
             if left_type != 'error_type' and right_type != 'error_type':
                self.add_error(f"Unsupported operand types for '{node.value}': '{left_type}' and '{right_type}'. Both must be numeric.", node.line, node.column)
             return 'error_type', None
        return 'bool', None
    def visit_AddExpression(self, node):
        left_type, left_val = self.visit(node.children[0])
        right_type, right_val = self.visit(node.children[1])
        if left_type in ('int', 'float') and right_type in ('int', 'float'):
            new_val = None
            if left_val is not None and right_val is not None:
                new_val = left_val + right_val if node.value == '+' else left_val - right_val
            return 'float' if 'float' in (left_type, right_type) else 'int', new_val
        if node.value == '+' and (left_type == 'string' or right_type == 'string'):
            new_val = None
            if left_val is not None and right_val is not None:
                new_val = str(left_val) + str(right_val)
            return 'string', new_val
        if 'error_type' not in (left_type, right_type):
            self.add_error(f"Unsupported operand types for '{node.value}': '{left_type}' and '{right_type}'.", node.line, node.column)
        return 'error_type', None
    def visit_MulExpression(self, node):
        left_type, left_val = self.visit(node.children[0])
        right_type, right_val = self.visit(node.children[1])
        op = node.value
        if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
            self.add_error(f"Unsupported operand types for '{op}': '{left_type}' and '{right_type}'.", node.line, node.column)
            return 'error_type', None
        new_val = None
        if left_val is not None and right_val is not None:
            if op == '*': new_val = left_val * right_val
            elif op == '/': new_val = left_val / right_val if right_val != 0 else float('inf')
            elif op == '%': 
                if left_type == 'int' and right_type == 'int':
                    new_val = left_val % right_val
                else:
                    self.add_error(f"Operator '%' requires integer operands.", node.line, node.column)
                    return 'error_type', None
        if op == '/': return 'float', new_val
        return 'float' if 'float' in (left_type, right_type) else 'int', new_val
    def visit_PowExpression(self, node):
        left_type, left_val = self.visit(node.children[0])
        right_type, right_val = self.visit(node.children[1])
        if left_type in ('int', 'float') and right_type in ('int', 'float'):
            new_val = None
            if left_val is not None and right_val is not None:
                new_val = left_val ** right_val
            return 'float' if 'float' in (left_type, right_type) else 'int', new_val
        if left_type != 'error_type' and right_type != 'error_type':
            self.add_error(f"Unsupported operand types for '^': '{left_type}' and '{right_type}'.", node.line, node.column)
        return 'error_type', None
    def visit_Identifier(self, node):
        symbol = self.symbol_table.lookup(node.value)
        if not symbol:
            self.add_error(f"Variable '{node.value}' used before declaration.", node.line, node.column)
            return 'error_type', None
        return symbol['type'], symbol['value']
    def visit_Number(self, node):
        val = eval(node.value)
        return 'float' if isinstance(val, float) else 'int', val
    def visit_Boolean(self, node):
        return 'bool', node.value == 'true'
    def visit_String(self, node):
        return 'string', node.value[1:-1]
    def visit_Char(self, node):
        return 'char', node.value[1:-1]

