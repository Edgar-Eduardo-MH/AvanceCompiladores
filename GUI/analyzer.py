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
                # Provide a more accurate line/column for unexpected EOF if possible
                last_token = self.tokens[-1] if self.tokens else (None, None, None, 1, 1) # Fallback to 1,1
                line = last_token[3] if last_token and len(last_token) > 3 else '?'
                column = last_token[4] if last_token and len(last_token) > 4 else '?'
                self.errors.append(f"Syntax error: expected {expected_type} '{expected_value}', but reached end of input at line {line}, column {column}")
            return None

    def parse(self):
        return self.program()

    def program(self):
        # Capture line/column from the 'main' token
        main_token = self.match('keyword', 'main')
        if main_token:
            self.match('symbol', '{')
            decls = self.declaration_list()
            
            # The Program node itself should get its line/column from the 'main' token
            program_node = ASTNode('Program', line=main_token[3], column=main_token[4])
            if decls:
                program_node.children.append(decls)

            if not self.current_token():
                self.errors.append("Expected '}' at end of program")
            elif self.current_token()[1] == '}':
                self.match('symbol', '}')
            else:
                # Use current token's line/column for error if available
                token = self.current_token()
                line = token[3] if token and len(token) > 3 else '?'
                column = token[4] if token and len(token) > 4 else '?'
                self.errors.append(f"Unexpected token '{token[1]}' before program end at line {line}, column {column}")
            return program_node
        else:
            # If 'main' is not found, fallback to default line/column or first token
            first_token = self.current_token()
            line = first_token[3] if first_token and len(first_token) > 3 else '?'
            column = first_token[4] if first_token and len(first_token) > 4 else '?'
            self.errors.append(f"Syntax error: program must start with 'main' at line {line}, column {column}")
            return ASTNode('Error', line=line, column=column)

    def declaration_list(self):
        children = []
        # Get line/column from the first declaration if available
        initial_token = self.current_token()
        line, column = (initial_token[3], initial_token[4]) if initial_token and len(initial_token) > 3 else (None, None)

        while self.current_token() and self.current_token()[1] != '}':
            decl = self.declaration()
            if decl:
                children.append(decl)
            else:
                # If declaration fails, break to avoid infinite loop on bad input
                if self.current_token():
                    # Advance to next token to try and recover
                    self.pos += 1
                else:
                    break # Reached end of input
        return ASTNode('DeclarationList', children=children, line=line, column=column)


    def declaration(self):
        token = self.current_token()
        if token and token[0] == 'keyword' and token[1] in ('int', 'float', 'bool'):
            return self.variable_declaration()
        else:
            stmt = self.statement()
            if stmt:
                # The 'Declaration' node takes the line/column of its statement child
                return ASTNode('Declaration', children=[stmt], line=stmt.line, column=stmt.column)
            # If neither a variable declaration nor a statement, it's an error
            line = token[3] if token and len(token) > 3 else '?'
            column = token[4] if token and len(token) > 4 else '?'
            self.errors.append(f"Expected a declaration or statement, found '{token[1]}' at line {line}, column {column}")
            return ASTNode('Error', line=line, column=column)

    def variable_declaration(self):
        # Get line/column from the type token
        type_token = self.match('keyword')
        if not type_token:
            return ASTNode('Error') # Already added error in match
        
        # Create Type node with its own line/column
        type_node = ASTNode('Type', value=type_token[1], line=type_token[3], column=type_token[4])
        
        id_list_node = self.identifier_list()
        if not id_list_node:
            # Error already added by identifier_list
            return ASTNode('Error')
        
        if not self.match('symbol', ';'):
            # Error already added by match
            return ASTNode('Error')
        
        # VariableDeclaration node uses the line/column of its type token
        return ASTNode('VariableDeclaration', children=[type_node, id_list_node], 
                       line=type_token[3], column=type_token[4])

    def identifier_list(self):
        children = []
        id_token = self.match('identifier')
        if not id_token:
            return ASTNode('Error') # Error added by match
        children.append(ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4]))

        while self.current_token() and self.current_token()[1] == ',':
            self.match('symbol', ',') # Consume the comma
            id_token = self.match('identifier')
            if id_token:
                children.append(ASTNode('Identifier', value=id_token[1], line=id_token[3], column=id_token[4]))
            else:
                self.errors.append(f"Expected identifier after ',' at line {self.current_token()[3] if self.current_token() else '?'}, column {self.current_token()[4] if self.current_token() else '?'}")
                return ASTNode('Error')
        # IdentifierList node can take the line/column of its first identifier
        first_id_token = children[0] if children else None
        return ASTNode('IdentifierList', children=children, 
                       line=first_id_token.line if first_id_token else None, 
                       column=first_id_token.column if first_id_token else None)

    def statement_list(self):
        children = []
        initial_token = self.current_token()
        line, column = (initial_token[3], initial_token[4]) if initial_token and len(initial_token) > 3 else (None, None)

        while self.current_token() and self.current_token()[1] not in ('}', 'end', 'else', 'until'):
            stmt = self.statement()
            if stmt:
                children.append(stmt)
            elif self.current_token(): # If statement didn't parse but there's a token, advance
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
            # Check for assignment
            if len(self.tokens) > self.pos + 1 and self.tokens[self.pos + 1][1] == '=':
                return self.assignment()
            else:
                self.errors.append(f"Unexpected identifier '{token[1]}' at line {statement_line}, column {statement_column}. Expected assignment or inc/dec.")
                self.pos += 1 # Advance to avoid infinite loop
                return ASTNode('Error', line=statement_line, column=statement_column)
        else:
            self.errors.append(f"Unknown statement starting with '{token[1]}' at line {statement_line}, column {statement_column}")
            self.pos += 1 # Advance to avoid infinite loop
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

        # Capture the line/column from the identifier token
        inc_dec_line = id_token[3]
        inc_dec_column = id_token[4]

        # Create the expression node: x + 1 or x - 1
        expression_node = ASTNode('AddExpression' if op_symbol == '+' else 'SubExpression', value=op_symbol, children=[
            ASTNode('Identifier', value=id_token[1], line=inc_dec_line, column=inc_dec_column),
            ASTNode('Number', value='1', line=inc_dec_line, column=inc_dec_column) # '1' is a constant, so use token's location
        ], line=inc_dec_line, column=inc_dec_column) # Line/column for the expression

        # Complete assignment: x = x + 1
        return ASTNode('Assignment', children=[
            ASTNode('Identifier', value=id_token[1], line=inc_dec_line, column=inc_dec_column),
            expression_node
        ], line=inc_dec_line, column=inc_dec_column) # Line/column for the assignment

    def assignment(self):
        id_token = self.match('identifier')
        if not id_token:
            return ASTNode('Error') # Error handled by match

        assignment_op_token = self.match('assignment')
        if not assignment_op_token:
            return ASTNode('Error') # Error handled by match

        expr = self.logical_expression()
        if not expr: # expr could be None if there's a syntax error in the expression
            return ASTNode('Error')
            
        if not self.match('symbol', ';'):
            return ASTNode('Error') # Error handled by match

        # Assignment node uses the line/column of its identifier token
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
            else: # If statement parsing failed, advance to avoid infinite loop
                if self.current_token(): self.pos += 1
                else: break
        
        else_branch = None
        if self.current_token() and self.current_token()[1] == 'else':
            else_token = self.match('keyword', 'else')
            else_branch = ASTNode('ElseBlock', line=else_token[3], column=else_token[4])
            while self.current_token() and self.current_token()[1] != 'end':
                stmt = self.statement()
                if stmt: else_branch.children.append(stmt)
                else: # If statement parsing failed, advance to avoid infinite loop
                    if self.current_token(): self.pos += 1
                    else: break

        end_token = self.match('keyword', 'end')
        if not end_token: return ASTNode('Error') # Error handled by match

        children = [condition, then_branch]
        if else_branch: children.append(else_branch)
        return ASTNode('IfStatement', children=children, line=if_token[3], column=if_token[4])

    def iteration(self):
        while_token = self.match('keyword', 'while')
        if not while_token: return ASTNode('Error')

        condition = self.logical_expression()
        if not condition: return ASTNode('Error')

        body = self.statement_list()
        # if not body: return ASTNode('Error') # statement_list can return empty body

        end_token = self.match('keyword', 'end')
        if not end_token: return ASTNode('Error')

        return ASTNode('WhileLoop', children=[condition, body], line=while_token[3], column=while_token[4])

    def repetition(self):
        do_token = self.match('keyword', 'do')
        if not do_token: return ASTNode('Error')

        body = ASTNode('DoBlock', line=do_token[3], column=do_token[4])
        while self.current_token() and self.current_token()[1] != 'until':
            stmt = self.statement()
            if stmt: body.children.append(stmt)
            else: # If statement parsing failed, advance to avoid infinite loop
                if self.current_token(): self.pos += 1
                else: break

        until_token = self.match('keyword', 'until')
        if not until_token: return ASTNode('Error')

        condition = self.logical_expression()
        if not condition: return ASTNode('Error')

        if self.current_token() and self.current_token()[1] == ';':
            self.match('symbol', ';')
        
        return ASTNode('DoUntilLoop', children=[body, condition], line=do_token[3], column=do_token[4])

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
            if not op_token: return ASTNode('Error') # Should not happen if current_token matched

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

    def component(self):
        token = self.current_token()
        if not token:
            self.errors.append("Unexpected end of input when parsing component")
            return ASTNode('Error')

        # Capture line/column from the component's starting token
        component_line = token[3] if len(token) > 3 else None
        component_column = token[4] if len(token) > 4 else None

        if token[1] == '(':
            self.match('symbol', '(')
            expr = self.logical_expression()
            self.match('symbol', ')')
            # The line/column for the parenthesized expression will be taken from the expr itself
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