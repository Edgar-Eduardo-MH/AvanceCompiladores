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

# Patrones para los distintos tipos de tokens
PATTERNS = [
    ('multiline_comment', r'/\*[\s\S]*?\*/'),       # Comentario multilínea estilo C
    ('singleline_comment', r'#.*'),                 # Comentario de una línea estilo Python
    
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
    ('assignment', r'='),
    ('symbol', r'[\(\)\{\},;]'),

    ('identifier', r'[A-Za-z_][A-Za-z0-9_]*'),      # Identificador válido

    ('whitespace', r'\s+'),                         # Espacios en blanco que se ignoran
]

# Analizador léxico que devuelve lista de tokens con tipo, lexema, línea y columna
COMPILED_PATTERNS = [(token_type, re.compile(pattern)) for token_type, pattern in PATTERNS]

def lexical_analyzer(source_code):
    tokens = []
    line = 1
    column = 1
    position = 0

    while position < len(source_code):
        match = None
        # Probamos cada patrón en la posición actual
        for token_type, regex in COMPILED_PATTERNS:
            match = regex.match(source_code, position)
            if match:
                text = match.group(0)
                
                # Caso especial para los saltos de línea y espacios
                if token_type == 'whitespace':
                    newlines = text.count('\n')
                    if newlines > 0:
                        line += newlines
                        # La nueva columna es la longitud después del último \n
                        column = len(text.rsplit('\n', 1)[-1]) + 1
                    else:
                        column += len(text)
                    # No agregamos 'whitespace' a los tokens, solo actualizamos pos
                    position = match.end()
                    break # Salimos del for y vamos a la siguiente iteración del while

                # Para todos los demás tokens
                real_type = token_type
                if token_type == 'identifier' and text in KEYWORDS:
                    real_type = 'keyword'
                elif token_type.startswith('invalid_real'):
                    real_type = 'invalid'
                
                # No agregamos comentarios a la lista de tokens para el parser,
                # pero sí los procesamos para contar líneas correctamente.
                if real_type in ['multiline_comment', 'singleline_comment', 'comment']:
                    newlines = text.count('\n')
                    if newlines > 0:
                        line += newlines
                        column = len(text.rsplit('\n', 1)[-1]) + 1
                    else:
                        column += len(text)
                else:
                    # Agregamos el token válido a la lista
                    color = COLORS.get(real_type, '#FFFFFF')
                    tokens.append((real_type, text, color, line, column))
                    # Actualizamos la columna después de añadir el token
                    column += len(text)

                position = match.end()
                break # Salimos del for, patrón encontrado

        # Si ningún patrón coincidió, es un carácter inválido
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

# ANALIZADOR SINTACTICO
class ASTNode:
    def __init__(self, type, value=None, line=None, column=None, children=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.children = children if children is not None else []

    def __str__(self):
        # Enhance default string representation to include line/column
        location = f" (Line: {self.line}, Column: {self.column})" if self.line is not None and self.column is not None else ""
        if self.value:
            return f"{self.type}: {self.value}{location}"
        return f"{self.type}{location}"

    def __repr__(self, level=0):
        indent = "    " * level
        location = f" (Line: {self.line}, Column: {self.column})" if self.line is not None and self.column is not None else ""
        repr_str = f"{indent}{self.type}: {self.value if self.value else ''}{location}\n"
        for child in self.children:
            repr_str += child.__repr__(level + 1)
        return repr_str

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
                self.errors.append(f"Syntax error: expected {expected_type} '{expected_value}', found '{token[1]}' at line {token[3]}, column {token[4]}")
            else:
                # Provide a more accurate line/column for unexpected EOF if possible
                last_token = self.tokens[-1] if self.tokens else (None, None, None, 1, 1) # Fallback to 1,1
                line = last_token[3] if last_token and len(last_token) > 3 else '?'
                column = last_token[4] if last_token and len(last_token) > 4 else '?'
                self.errors.append(f"Syntax error: expected {expected_type} '{expected_value}', but reached end of input at line {line}, column {column}")
            return None

    def parse(self):
        ast = self.program()
        return ast

    def program(self):
        # Primero, verificamos la secuencia 'int', 'main', '(', ')'
        # Guardamos la posición actual por si necesitamos retroceder para el error
        initial_pos = self.pos
        
        int_token = self.match('keyword', 'int')
        main_token = self.match('keyword', 'main')
        lparen_token = self.match('symbol', '(')
        rparen_token = self.match('symbol', ')')
        
        # Si la secuencia 'int main()' es correcta, procedemos
        if int_token and main_token and lparen_token and rparen_token:
            # Ahora buscamos la llave de apertura '{'
            if not self.match('symbol', '{'):
                # Si no hay '{', es un error.
                self.errors.append(f"Syntax error: expected '{{' after '()' at line {rparen_token[3]}, column {rparen_token[4]+1}")
                return ASTNode('Error', line=rparen_token[3], column=rparen_token[4]+1)
            
            declarations = self.declaration_list()
            statements = self.statement_list()
            
            # El nodo del programa usa la ubicación del token 'main'
            program_node = ASTNode('Program', children=[declarations, statements], line=main_token[3], column=main_token[4])

            # Verificación de la llave de cierre '}'
            if not self.match('symbol', '}'):
                self.errors.append("Syntax Error: Expected '}' at the end of the program.")
            
            return program_node
        
        else:
            self.pos = initial_pos
            first_token = self.current_token()
            line = first_token[3] if first_token and len(first_token) > 3 else '1'
            column = first_token[4] if first_token and len(first_token) > 4 else '1'
            self.errors.append(f"Syntax Error: Program must start with 'int main()' at line {line}, column {column}.")
            return ASTNode('Error', line=line, column=column)

    def declaration_list(self):
        declarations = []
        initial_token = self.current_token()

        while self.current_token() and self.current_token()[0] == 'keyword' and self.current_token()[1] in ('int', 'float', 'bool', 'string', 'char'):
            decl = self.variable_declaration()
            if decl and decl.type != 'Error':
                declarations.append(decl)
            else:
                break

        line = initial_token[3] if initial_token and len(initial_token) > 3 else None
        column = initial_token[4] if initial_token and len(initial_token) > 4 else None
        
        return ASTNode('DeclarationList', children=declarations, line=line, column=column)


    def variable_declaration(self):
        type_token = self.match('keyword')
        if not type_token:
            return None

        type_node = ASTNode('Type', value=type_token[1], line=type_token[3], column=type_token[4])
        
        initializers = self.initializer_list()

        if not self.match('symbol', ';'):
            return ASTNode('Error')

        return ASTNode('VariableDeclaration', children=[type_node] + initializers, line=type_token[3], column=type_token[4])

    def initializer_list(self):
        initializers = []
        
        init = self.initializer()
        if init:
            initializers.append(init)

        while self.current_token() and self.current_token()[1] == ',':
            self.match('symbol', ',')
            init = self.initializer()
            if init:
                initializers.append(init)
            else:
                self.errors.append("Syntax Error: Expected identifier after ','.")
                return [ASTNode('Error')]

        return initializers
    
    def initializer(self):
        id_token = self.match('identifier')
        if not id_token:
            return None

        identifier_node = ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4])
        
        if self.current_token() and self.current_token()[0] == 'assignment':
            self.match('assignment')
            expr_node = self.logical_expression()
            if not expr_node or expr_node.type == 'Error':
                self.errors.append(f"Syntax Error: Invalid expression for variable '{id_token[1]}' initialization.")
                return ASTNode('Error')
            return ASTNode('Assignment', children=[identifier_node, expr_node], line=id_token[3], column=id_token[4])
        
        return identifier_node

    def statement_list(self):
        children = []
        initial_token = self.current_token()
        line, column = (initial_token[3], initial_token[4]) if initial_token and len(initial_token) > 3 else (None, None)

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
        if not token:
            return None

        # Capture line/column from the starting token of the statement
        statement_line = token[3] if len(token) > 3 else None
        statement_column = token[4] if len(token) > 4 else None

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
            if len(self.tokens) > self.pos + 1 and self.tokens[self.pos + 1][1] == '=':
                return self.assignment()
            else:
                self.errors.append(f"Unexpected identifier '{token[1]}' at line {statement_line}, column {statement_column}. Expected assignment or inc/dec.")
                self.pos += 1 #
                return ASTNode('Error', line=statement_line, column=statement_column)
        else:
            self.errors.append(f"Unknown statement starting with '{token[1]}' at line {statement_line}, column {statement_column}")
            self.pos += 1 
            return ASTNode('Error', line=statement_line, column=statement_column)
        
    def lookahead_inc_dec(self):
        token = self.current_token()
        next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
        return token and token[0] == 'identifier' and next_token and next_token[0] == 'inc_dec_op'

    def inc_dec_statement(self):
        id_token = self.match('identifier')
        if not id_token:
            return ASTNode('Error')

        op_token = self.match('inc_dec_op')
        if not op_token:
            return ASTNode('Error')

        if not self.match('symbol', ';'):
            return ASTNode('Error')

        op_symbol = '+' if op_token[1] == '++' else '-'

        inc_dec_line = id_token[3]
        inc_dec_column = id_token[4]

        expression_node = ASTNode('AddExpression' if op_symbol == '+' else 'SubExpression', value=op_symbol, children=[
            ASTNode('Identifier', value=id_token[1], line=inc_dec_line, column=inc_dec_column),
            ASTNode('Number', value='1', line=inc_dec_line, column=inc_dec_column) 
        ], line=inc_dec_line, column=inc_dec_column)

        return ASTNode('Assignment', children=[
            ASTNode('Identifier', value=id_token[1], line=inc_dec_line, column=inc_dec_column),
            expression_node
        ], line=inc_dec_line, column=inc_dec_column) 

    def assignment(self):
        id_token = self.match('identifier')
        if not id_token:
            return ASTNode('Error')

        assignment_op_token = self.match('assignment')
        if not assignment_op_token:
            return ASTNode('Error')

        expr = self.logical_expression()
        if not expr: 
            return ASTNode('Error')
            
        if not self.match('symbol', ';'):
            return ASTNode('Error') 

        return ASTNode('Assignment', children=[
            ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4]),
            expr
        ], line=id_token[3], column=id_token[4])

    def selection(self):
        if_token = self.match('keyword', 'if')
        if not if_token: return ASTNode('Error')

        condition = self.logical_expression()
        if not condition: return ASTNode('Error')

        if not self.match('keyword', 'then'): return ASTNode('Error')

        then_branch = ASTNode('ThenBlock', line=if_token[3], column=if_token[4])
        while self.current_token() and self.current_token()[1] not in ('else', 'end'):
            stmt = self.statement()
            if stmt: then_branch.children.append(stmt)
            else: 
                if self.current_token(): self.pos += 1
                else: break
        
        else_branch = None
        if self.current_token() and self.current_token()[1] == 'else':
            else_token = self.match('keyword', 'else')
            else_branch = ASTNode('ElseBlock', line=else_token[3], column=else_token[4])
            while self.current_token() and self.current_token()[1] != 'end':
                stmt = self.statement()
                if stmt: else_branch.children.append(stmt)
                else: 
                    if self.current_token(): self.pos += 1
                    else: break

        end_token = self.match('keyword', 'end')
        if not end_token: return ASTNode('Error') 

        children = [condition, then_branch]
        if else_branch: children.append(else_branch)
        return ASTNode('IfStatement', children=children, line=if_token[3], column=if_token[4])

    def iteration(self):
        while_token = self.match('keyword', 'while')
        if not while_token: return ASTNode('Error')

        condition = self.logical_expression()
        if not condition: return ASTNode('Error')
        
        if not self.match('keyword', 'then'): return ASTNode('Error')
        body = self.statement_list()

        end_token = self.match('keyword', 'end')
        if not end_token: return ASTNode('Error')

        return ASTNode('WhileLoop', children=[condition, body], line=while_token[3], column=while_token[4])

    # Modificar el método repetition:
    def repetition(self):
        do_token = self.match('keyword', 'do')
        if not do_token: return ASTNode('Error')

        body = ASTNode('DoBlock', line=do_token[3], column=do_token[4])
        while self.current_token() and self.current_token()[1] != 'until':
            stmt = self.statement()
            if stmt: body.children.append(stmt)
            else: 
                if self.current_token(): self.pos += 1
                else: break

        until_token = self.match('keyword', 'until')
        if not until_token: return ASTNode('Error')

        condition = self.logical_expression()
        if not condition: return ASTNode('Error')

        if self.current_token() and self.current_token()[1] == ';':
            self.match('symbol', ';')
        
        return ASTNode('DoUntilLoop', children=[body, condition], line=do_token[3], column=do_token[4])

    # Modificar input_statement y output_statement:
    def input_statement(self):
        cin_token = self.match('keyword', 'cin')
        if not cin_token: return ASTNode('Error')

        if not self.match('shift_op', '>>'): return ASTNode('Error')

        id_token = self.match('identifier')
        if not id_token: return ASTNode('Error')
        
        if not self.match('symbol', ';'): return ASTNode('Error')

        return ASTNode('Input', children=[
            ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4])
        ], line=cin_token[3], column=cin_token[4])

    def output_statement(self):
        cout_token = self.match('keyword', 'cout')
        if not cout_token: return ASTNode('Error')

        if not self.match('shift_op', '<<'): return ASTNode('Error')
        
        children = []
        while True:
            token = self.current_token()
            if not token or token[1] in (';', '}'):
                break
                
            if token[0] == 'string':
                str_token = self.match('string')
                if not str_token: return ASTNode('Error')
                children.append(ASTNode('String', value=str_token[1], line=str_token[3], column=str_token[4]))
            else:
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
        if not node: return ASTNode('Error')

        while self.current_token() and self.current_token()[0] == 'logical_op':
            op_token = self.match('logical_op')
            if not op_token: return ASTNode('Error') 

            right = self.expression()
            if not right: return ASTNode('Error')
            
            node = ASTNode('LogicalExpression', value=op_token[1], children=[node, right], line=op_token[3], column=op_token[4])
        return node

    def expression(self):
        left = self.simple_expression()
        if not left: return ASTNode('Error')

        if self.current_token() and self.current_token()[0] == 'relational_op':
            op_token = self.match('relational_op')
            if not op_token: return ASTNode('Error')

            right = self.simple_expression()
            if not right: return ASTNode('Error')
            
            return ASTNode('RelationalExpression', value=op_token[1], children=[left, right], line=op_token[3], column=op_token[4])
        return left

    def simple_expression(self):
        node = self.term()
        if not node: return ASTNode('Error')

        while self.current_token() and self.current_token()[0] == 'add_op':
            op_token = self.match('add_op')
            if not op_token: return ASTNode('Error')

            right = self.term()
            if not right: return ASTNode('Error')
            
            node = ASTNode('AddExpression', value=op_token[1], children=[node, right], line=op_token[3], column=op_token[4])
        return node

    def term(self):
        node = self.factor()
        if not node: return ASTNode('Error')

        while self.current_token() and self.current_token()[0] == 'mul_op':
            op_token = self.match('mul_op')
            if not op_token: return ASTNode('Error')

            right = self.factor()
            if not right: return ASTNode('Error')
            
            node = ASTNode('MulExpression', value=op_token[1], children=[node, right], line=op_token[3], column=op_token[4])
        return node

    def factor(self):
        node = self.component()
        if not node: return ASTNode('Error')

        while self.current_token() and self.current_token()[0] == 'pow_op':
            op_token = self.match('pow_op')
            if not op_token: return ASTNode('Error')

            right = self.component()
            if not right: return ASTNode('Error')
            
            node = ASTNode('PowExpression', value=op_token[1], children=[node, right], line=op_token[3], column=op_token[4])
        return node

    # Modificar el método component:
    def component(self):
        token = self.current_token()
        if not token:
            self.errors.append("Unexpected end of input when parsing component")
            return ASTNode('Error')

        component_line = token[3] if len(token) > 3 else None
        component_column = token[4] if len(token) > 4 else None

        if token[1] == '(':
            self.match('symbol', '(')
            expr = self.logical_expression()
            self.match('symbol', ')')
            return expr 
        elif token[0] in ('integer_number', 'real_number'):
            self.pos += 1
            return ASTNode('Number', value=token[1], line=component_line, column=component_column)
        elif token[0] == 'identifier':
            self.pos += 1
            return ASTNode('Identifier', value=token[1], line=component_line, column=component_column)
        elif token[0] == 'string':
            self.pos += 1
            return ASTNode('String', value=token[1], line=component_line, column=component_column)
        elif token[0] == 'keyword' and token[1] in ('true', 'false'):
            self.pos += 1
            return ASTNode('Boolean', value=token[1], line=component_line, column=component_column)
        else:
            self.errors.append(f"Invalid component starting with '{token[1]}' at line {component_line}, column {component_column}")
            self.pos += 1
            return ASTNode('Error', line=component_line, column=component_column)
        
class SymbolTable:
    """
    Una tabla de símbolos simple para un único ámbito (scope).
    En un compilador más complejo, esto sería una pila de diccionarios para manejar ámbitos anidados.
    """
    def __init__(self):
        self.symbols = {}
        self.memory_address_counter = 0

    def define(self, name, symbol_type, line, column, scope='global'):
        """Define un nuevo símbolo. Devuelve False si ya existe."""
        if name in self.symbols:
            return False
        address = self.memory_address_counter
        self.memory_address_counter += 4
        self.symbols[name] = {'type': symbol_type, 'value': None, 'scope': scope, 'line': line, 'column': column, 'memory_address': address}
        return True
    
    def update_value(self, name, value):
        """Actualiza el valor de un símbolo ya existente."""
        if name in self.symbols:
            self.symbols[name]['value'] = value
            return True
        return False

    def lookup(self, name):
        """Busca un símbolo. Devuelve su información o None si no se encuentra."""
        return self.symbols.get(name)

class SemanticAnalyzer:
    """
    Recorre el AST para realizar el análisis semántico.
    Utiliza un patrón 'Visitor' para procesar cada tipo de nodo.
    """
    def __init__(self, ast_root):
        self.ast = ast_root
        self.symbol_table = SymbolTable()
        self.errors = []
        self.log = []

    def analyze(self):
        """Inicia el análisis desde la raíz del AST."""
        if self.ast and self.ast.type != 'Error':
            self.visit(self.ast)
        return self.errors

    def visit(self, node):
        """Método 'visit' genérico que delega al método específico del tipo de nodo."""
        if not node or node.type == 'Error':
            return 'error_type', None
        method_name = f'visit_{node.type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Visita todos los hijos de un nodo si no hay un método específico."""
        for child in node.children:
            self.visit(child)

    def add_error(self, message, line, column):
        """Añade un error semántico a la lista."""
        self.errors.append(f"Semantic Error: {message} (Line: {line}, Column: {column})")

    #  Métodos Visitor para Nodos Específicos 

    def visit_VariableDeclaration(self, node):
        var_type_node = node.children[0]
        var_type = var_type_node.value
        
        for initializer_node in node.children[1:]:
            if initializer_node.type == 'Assignment':
                identifier_node = initializer_node.children[0]
                expression_node = initializer_node.children[1]
                var_name = identifier_node.value

                self.log.append(f"Regla: Declaración de variable '{var_name}' de tipo '{var_type}'.")

                if not self.symbol_table.define(var_name, var_type, identifier_node.line, identifier_node.column):
                    self.add_error(f"Variable '{var_name}' is already declared.", identifier_node.line, identifier_node.column)
                else:
                    self.log.append(f"Acción: Símbolo '{var_name}' añadido a la tabla.")

                expr_type, expr_value = self.visit(expression_node)

                self.log.append(f"Regla: Verificando asignación en declaración para '{var_name}'.")
                self.log.append(f"  -> Tipo esperado: '{var_type}', Tipo obtenido: '{expr_type}'.")
                
                if expr_type == 'error_type':
                    continue

                if expr_type != var_type and not (var_type == 'float' and expr_type == 'int'):
                    self.add_error(f"Type mismatch. Cannot assign '{expr_type}' to variable '{var_name}' of type '{var_type}'.",
                                   identifier_node.line, identifier_node.column)
                else:
                    self.log.append(f"  -> Resultado: Tipos compatibles. Valor actualizado a {expr_value}.")
                    self.symbol_table.update_value(var_name, expr_value)

            elif initializer_node.type == 'Identifier':
                var_name = initializer_node.value
                self.log.append(f"Regla: Declaración de variable '{var_name}' de tipo '{var_type}'.")
                if not self.symbol_table.define(var_name, var_type, initializer_node.line, initializer_node.column):
                    self.add_error(f"Variable '{var_name}' is already declared.", initializer_node.line, initializer_node.column)
                    self.log.append(f"Acción: Símbolo '{var_name}' añadido a la tabla.")

    def visit_Assignment(self, node):
        identifier_node = node.children[0]
        expression_node = node.children[1]
        var_name = identifier_node.value

        self.log.append(f"\nRegla: Analizando asignación para la variable '{var_name}'.")

        # Acción Semántica: Verificar que la variable a la izquierda exista
        symbol = self.symbol_table.lookup(var_name)
        if not symbol:
            self.log.append(f"  -> ¡ERROR! La variable '{var_name}' no ha sido declarada.")
            self.add_error(f"Variable '{var_name}' is not declared.", identifier_node.line, identifier_node.column)
            self.visit(expression_node)  
            return

        # Acción Semántica: Calcular tipo de la expresión y comparar
        self.log.append(f"  -> Símbolo '{var_name}' encontrado en la tabla.")
        expression_type, expression_value = self.visit(expression_node)

        if expression_type == 'error_type':
            return

        expected_type = symbol['type']
        self.log.append(f"Regla: Verificando tipos para asignación.")
        self.log.append(f"  -> Tipo esperado ('{var_name}'): '{expected_type}', Tipo obtenido (expresión): '{expression_type}'.")
        if expression_type != expected_type and not (expected_type == 'float' and expression_type == 'int'):
            self.log.append(f"  -> ¡ERROR DE TIPOS! No se puede asignar '{expression_type}' a '{expected_type}'.")
            self.add_error(f"Type mismatch. Cannot assign type '{expression_type}' to variable '{var_name}' of type '{expected_type}'.",
                           identifier_node.line, identifier_node.column)
        else:
            self.log.append(f"  -> Resultado: Tipos compatibles. Valor de '{var_name}' actualizado a {expression_value}.")
            self.symbol_table.update_value(var_name, expression_value)

    def visit_IfStatement(self, node):
        condition_node = node.children[0]
        condition_type, _ = self.visit(condition_node)
        
        if condition_type != 'bool' and condition_type != 'error_type':
            self.add_error(f"If statement condition must be boolean, but got '{condition_type}'.", 
                        condition_node.line, condition_node.column)

        self.visit(node.children[1]) 
        if len(node.children) > 2:
            self.visit(node.children[2]) 

    def visit_WhileLoop(self, node):
        condition_node = node.children[0]

        # Extraemos solo el tipo de la tupla
        condition_type, _ = self.visit(condition_node)

        if condition_type != 'bool' and condition_type != 'error_type':
            self.add_error(f"While loop condition must be boolean, but got '{condition_type}'.", 
                        condition_node.line, condition_node.column)

        self.visit(node.children[1]) # StatementList (cuerpo del bucle)

    def visit_DoUntilLoop(self, node):
        # Visita el cuerpo del bucle primero
        self.visit(node.children[0]) # DoBlock

        condition_node = node.children[1]
        # Acción Semántica: La condición de un 'do-until' debe ser de tipo booleano.
        condition_type = self.visit(condition_node)
        if condition_type != 'bool' and condition_type != 'error_type':
            self.add_error(f"Do-until loop condition must be boolean, but got '{condition_type}'.", 
                           condition_node.line, condition_node.column)

    def visit_Input(self, node):
        identifier_node = node.children[0]
        var_name = identifier_node.value

        # Acción Semántica: Verificar que la variable donde se guarda la entrada exista.
        if not self.symbol_table.lookup(var_name):
            self.add_error(f"Variable '{var_name}' for input is not declared.", 
                           identifier_node.line, identifier_node.column)
        else:
            self.symbol_table.update_value(var_name, '<input>')

    def visit_Output(self, node):
        # Simplemente visita cada expresión en la sentencia cout para verificarla.
        self.generic_visit(node)


    # --- Métodos Visitor para Expresiones ---

    def visit_LogicalExpression(self, node):
    # Obtenemos las tuplas completas de ambos lados
        left_type, left_val = self.visit(node.children[0])
        right_type, right_val = self.visit(node.children[1])

        # Comparamos solo los tipos
        if left_type == 'bool' and right_type == 'bool':
            # Calculamos el nuevo valor si es posible
            new_val = None
            if left_val is not None and right_val is not None:
                if node.value == '&&':
                    new_val = left_val and right_val
                elif node.value == '||':
                    new_val = left_val or right_val
            return 'bool', new_val # Devolvemos la tupla correcta
        
        if left_type != 'error_type' and right_type != 'error_type':
            self.add_error(f"Unsupported operand types for '{node.value}': '{left_type}' and '{right_type}'. Both must be boolean.", 
                        node.line, node.column)
        
        return 'error_type', None # Devolvemos la tupla de error

    def visit_RelationalExpression(self, node):
        left_type, left_val = self.visit(node.children[0])
        right_type, right_val = self.visit(node.children[1])

        if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
            self.add_error(f"Unsupported operand types for '{node.value}': '{left_type}' and '{right_type}'. Both must be numeric.", 
                           node.line, node.column)
            return 'error_type', None
        
        new_val = None
        if left_val is not None and right_val is not None:
            op_map = {'>': lambda a,b: a > b, '<': lambda a,b: a < b, '==': lambda a,b: a == b,
                      '!=': lambda a,b: a != b, '>=': lambda a,b: a >= b, '<=': lambda a,b: a <= b}
            new_val = op_map[node.value](left_val, right_val)

        return 'bool', new_val

    def visit_MulExpression(self, node):
        left_type, left_val = self.visit(node.children[0])
        right_type, right_val = self.visit(node.children[1])
        op = node.value

        if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
            # ... (manejo de error igual que antes)
            return 'error_type', None

        # Calcular el nuevo valor
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

        # Calcular el nuevo tipo
        if op == '/': new_type = 'float'
        elif op == '%': new_type = 'int'
        else: new_type = 'float' if 'float' in (left_type, right_type) else 'int'

        return new_type, new_val

    def visit_PowExpression(self, node): # Para Potencia (^)
        left_type = self.visit(node.children[0])
        right_type = self.visit(node.children[1])

        # Regla de tipos para la potencia:
        if left_type in ('int', 'float') and right_type in ('int', 'float'):
            return 'float' if 'float' in (left_type, right_type) else 'int'
            
        if left_type != 'error_type' and right_type != 'error_type':
            self.add_error(f"Unsupported operand types for '^': '{left_type}' and '{right_type}'.", 
                           node.line, node.column)
        return 'error_type'

    def visit_AddExpression(self, node): # Sirve para + y -
        self.log.append(f"Regla: Analizando expresión de suma/resta ('{node.value}').")
        left_type, left_val = self.visit(node.children[0])
        right_type, right_val = self.visit(node.children[1])
        self.log.append(f"  -> Operando izquierdo tipo: '{left_type}', Operando derecho tipo: '{right_type}'.")

        if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
            self.log.append(f"  -> ¡ERROR DE TIPOS! Los operandos para '{node.value}' deben ser numéricos.")
            if 'error_type' not in (left_type, right_type):
                self.add_error(f"Unsupported operand types for '{node.value}': '{left_type}' and '{right_type}'.", node.line, node.column)
            return 'error_type', None

        # Si alguno de los valores es desconocido, el resultado también lo es
        if left_val is None or right_val is None:
            new_val = None
        else:
            new_val = left_val + right_val if node.value == '+' else left_val - right_val
        
        new_type = 'float' if 'float' in (left_type, right_type) else 'int'
        self.log.append(f"  -> Resultado: Operación válida. Tipo resultante: '{new_type}'.")
        return new_type, new_val

    def visit_Identifier(self, node):
        var_name = node.value
        # Acción Semántica: Verificar que la variable usada en una expresión exista
        symbol = self.symbol_table.lookup(var_name)
        if not symbol:
            self.add_error(f"Variable '{var_name}' used before declaration.", node.line, node.column)
            return 'error_type' # Devolver un tipo de error para detener la cascada
        return symbol['type'], symbol['value']

    # Métodos para Nodos Terminales que devuelven su tipo

    def visit_Number(self, node):
        if '.' in node.value:
            return 'float', float(node.value)
        else:
            return 'int', int(node.value)

    def visit_Boolean(self, node):
        return 'bool', True if node.value == 'true' else False
    
    def visit_String(self, node):
        return 'string', node.value