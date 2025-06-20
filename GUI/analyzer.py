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
def lexical_analyzer(source_code):
    tokens = []
    line = 1
    column = 1
    position = 0
    in_multiline_comment = False
    multiline_comment_start = (1, 1)  # posicion inicial del comentario

    while position < len(source_code):
        if in_multiline_comment:
            end_pos = source_code.find('*/', position)
            if end_pos != -1:
                comment_text = source_code[position:end_pos + 2]
                tokens.append(('comment', comment_text, COLORS['comment'], multiline_comment_start[0], multiline_comment_start[1]))
                newlines = comment_text.count('\n')
                if newlines > 0:
                    line += newlines
                    column = len(comment_text.rsplit('\n', 1)[-1]) + 1
                else:
                    column += len(comment_text)
                position = end_pos + 2
                in_multiline_comment = False
            else:
                # Si no se encuentra el cierre, consideramos todo el resto como comentario
                comment_text = source_code[position:]
                tokens.append(('comment', comment_text, COLORS['comment'], multiline_comment_start[0], multiline_comment_start[1]))
                return tokens  # ya no hay más texto
        else:
            if source_code[position:position+2] == '/*':
                in_multiline_comment = True
                multiline_comment_start = (line, column)
                position += 2
                column += 2
                continue

            match = None
            for token_type, pattern in PATTERNS:
                regex = re.compile(pattern)
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
                    else:
                        if token_type == 'identifier' and text in KEYWORDS:
                            real_type = 'keyword'
                        elif token_type.startswith('invalid_real'):
                            real_type = 'invalid'
                        elif token_type in ['singleline_comment', 'multiline_comment']:
                            real_type = 'comment'
                        else:
                            real_type = token_type
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

# ANALIZADOR SINTACTICO CORREGIDO Y OPTIMIZADO
class ASTNode:
    def __init__(self, type_, value=None, children=None, line=None, column=None):
        self.type = type_
        self.value = value
        self.children = children if children is not None else []
        self.line = line
        self.column = column

    def __repr__(self, level=0):
        indent = "  " * level
        location = f" (Line: {self.line}, Column: {self.column})" if self.line is not None and self.column is not None else ""
        repr_str = f"{indent}{self.type}: {self.value if self.value else ''}{location}\n"
        for child in self.children:
            repr_str += child.__repr__(level + 1)
        return repr_str

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
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
                self.errors.append(f"Syntax error: expected {expected_type} '{expected_value}', but reached end of input")
            return None

    def parse(self):
        return self.program()

    def program(self):
        children = []
        token = self.match('keyword', 'main')
        if token:
            self.match('symbol', '{')
            decls = self.declaration_list()
            children.append(decls)

            if not self.current_token():
                self.errors.append("Expected '}' at end of program")
            elif self.current_token()[1] == '}':
                self.match('symbol', '}')
            else:
                self.errors.append(f"Unexpected token '{self.current_token()[1]}' before program end")
            return ASTNode('Program', children=children, line=token[3], column=token[4])
        else:
            self.errors.append("Syntax error: program must start with 'main'")
            return ASTNode('Error')

    def declaration_list(self):
        children = []
        while self.current_token() and self.current_token()[1] != '}':
            decl = self.declaration()
            if decl:
                children.append(decl)
        return ASTNode('DeclarationList', children=children)

    def declaration(self):
        token = self.current_token()
        if token and token[0] == 'keyword' and token[1] in ('int', 'float', 'bool'):
            return self.variable_declaration()
        else:
            stmt = self.statement()
            if stmt:
                return ASTNode('Declaration', children=[stmt])
            return ASTNode('Error')

    def variable_declaration(self):
        children = []
        type_token = self.match('keyword')
        if not type_token:
            return ASTNode('Error')
        children.append(ASTNode('Type', value=type_token[1]))

        id_list_node = self.identifier_list()
        if id_list_node:
            children.append(id_list_node)

        if not self.match('symbol', ';'):
            return ASTNode('Error')
        return ASTNode('VariableDeclaration', children=children)

    def identifier_list(self):
        children = []
        id_token = self.match('identifier')
        if not id_token:
            return ASTNode('Error')
        children.append(ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4]))

        while self.current_token() and self.current_token()[1] == ',':
            self.match('symbol', ',')
            id_token = self.match('identifier')
            if id_token:
                children.append(ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4]))
            else:
                self.errors.append("Expected identifier after ','")
                return ASTNode('Error')
        return ASTNode('IdentifierList', children=children)

    def statement_list(self):
        children = []
        while self.current_token() and self.current_token()[1] not in ('}', 'end', 'else', 'until'):
            stmt = self.statement()
            if stmt:
                children.append(stmt)
            elif self.current_token() and self.current_token()[1] in ('}', 'end', 'else', 'until'):
                break
            else:
                self.pos +- 1
        return ASTNode('StatementList', children=children)

    def statement(self):
        token = self.current_token()
        if not token:
            return None

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
                self.error.append(f"Unexpected ifentifier '{token[1]}' at line {token[3]}, column {token[4]}")
                self.pos += 1
                return ASTNode('Error')
        else:
            self.errors.append(f"Unknown statement starting with '{token[1]}' at line {token[3]}, column {token[4]}")
            self.pos += 1
            return ASTNode('Error')
        
    def lookahead_inc_dec(self):
        token = self.current_token()
        next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
        return token and token[0] == 'identifier' and next_token and next_token[0] == 'inc_dec_op'

    def inc_dec_statement(self):
        id_token = self.match('identifier')
        op_token = self.match('inc_dec_op')
        self.match('symbol', ';')
        return ASTNode('IncDec', value=op_token[1], children=[
            ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4])
        ])


    def assignment(self):
        id_token = self.match('identifier')
        if not id_token:
            return ASTNode('Error')
        if not self.match('assignment'):
            return ASTNode('Error')
        expr = self.logical_expression()
        self.match('symbol', ';')
        return ASTNode('Assignment', children=[
            ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4]),
            expr
        ], line=id_token[3], column=id_token[4])

    def selection(self):
        self.match('keyword', 'if')
        condition = self.logical_expression()
        self.match('keyword', 'then')

        then_branch = ASTNode('ThenBlock')
        while self.current_token() and self.current_token()[1] not in ('else', 'end'):
            stmt = self.statement()
            if stmt:
                then_branch.children.append(stmt)
        
        else_branch = None
        if self.current_token() and self.current_token()[1] == 'else':
            self.match('keyword', 'else')
            else_branch = ASTNode('ElseBlock')
            while self.current_token() and self.current_token()[1] != 'end':
                stmt = self.statement()
                if stmt:
                    else_branch.children.append(stmt)

        self.match('keyword', 'end')
        children = [condition, then_branch]
        if else_branch:
            children.append(else_branch)
        return ASTNode('IfStatement', children=children)

    def iteration(self):
        self.match('keyword', 'while')
        condition = self.logical_expression()
        body = self.statement_list()
        self.match('keyword', 'end')
        return ASTNode('WhileLoop', children=[condition, body])

    def repetition(self):
        self.match('keyword', 'do')
        body = ASTNode('DoBlock')
        while self.current_token() and self.current_token()[1] != 'until':
            stmt = self.statement()
            if stmt:
                body.children.append(stmt)

        self.match('keyword', 'until')
        condition = self.logical_expression()

        if self.current_token() and self.current_token()[1] == ';':
            self.match('symbol', ';')
        return ASTNode('DoUntilLoop', children=[body, condition])


    def input_statement(self):
        self.match('keyword', 'cin')
        self.match('shift_op', '>>')
        id_token = self.match('identifier')
        if not id_token:
            return ASTNode('Error')
        self.match('symbol', ';')
        return ASTNode('Input', children=[
            ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4])
        ])

    def output_statement(self):
        self.match('keyword', 'cout')
        self.match('shift_op', '<<')
        children = []
        while True:
            token = self.current_token()
            if not token or token[1] in (';', '}'):
                break
            if token[0] == 'string':
                str_token = self.match('string')
                children.append(ASTNode('String', value=str_token[1], line=str_token[3], column=str_token[4]))
            else:
                children.append(self.logical_expression())
            if self.current_token() and self.current_token()[1] == '<<':
                self.match('shift_op', '<<')
            else:
                break
        self.match('symbol', ';')
        return ASTNode('Output', children=children)

    def logical_expression(self):
        node = self.expression()
        while self.current_token() and self.current_token()[0] == 'logical_op':
            op_token = self.match('logical_op')
            right = self.expression()
            node = ASTNode('LogicalExpression', value=op_token[1], children=[node, right])
        return node

    def expression(self):
        left = self.simple_expression()
        if self.current_token() and self.current_token()[0] == 'relational_op':
            op_token = self.match('relational_op')
            right = self.simple_expression()
            return ASTNode('RelationalExpression', value=op_token[1], children=[left, right])
        return left

    def simple_expression(self):
        node = self.term()
        while self.current_token() and self.current_token()[0] == 'add_op':
            op_token = self.match('add_op')
            right = self.term()
            node = ASTNode('AddExpression', value=op_token[1], children=[node, right])
        return node

    def term(self):
        node = self.factor()
        while self.current_token() and self.current_token()[0] == 'mul_op':
            op_token = self.match('mul_op')
            right = self.factor()
            node = ASTNode('MulExpression', value=op_token[1], children=[node, right])
        return node

    def factor(self):
        node = self.component()
        while self.current_token() and self.current_token()[0] == 'pow_op':
            op_token = self.match('pow_op')
            right = self.component()
            node = ASTNode('PowExpression', value=op_token[1], children=[node, right])
        return node

    def component(self):
        token = self.current_token()
        if not token:
            self.errors.append("Unexpected end of input")
            return ASTNode('Error')

        if token[1] == '(':
            self.match('symbol', '(')
            expr = self.logical_expression()
            self.match('symbol', ')')
            return expr
        elif token[0] in ('integer_number', 'real_number'):
            self.pos += 1
            return ASTNode('Number', value=token[1], line=token[3], column=token[4])
        elif token[0] == 'identifier':
            self.pos += 1
            return ASTNode('Identifier', value=token[1], line=token[3], column=token[4])
        elif token[0] == 'string':
            self.pos += 1
            return ASTNode('String', value=token[1], line=token[3], column=token[4])
        elif token[0] == 'keyword' and token[1] in ('true', 'false'):
            self.pos += 1
            return ASTNode('Boolean', value=token[1], line=token[3], column=token[4])
        else:
            self.errors.append(f"Invalid component starting with '{token[1]}' at line {token[3]}, column {token[4]}")
            self.pos += 1
            return ASTNode('Error')
