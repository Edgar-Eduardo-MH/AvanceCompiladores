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
    'if', 'else', 'do', 'while', 'switch', 'case', 'int', 'float', 'main',
    'for', 'foreach', 'double', 'char', 'string', 'break', 'continue', 'return', 'then'
}

# Patrones para los distintos tipos de tokens
PATTERNS = [
    ('multiline_comment', r'/\*[\s\S]*?\*/'),       # Comentario multilínea estilo C
    ('singleline_comment', r'#.*'),                 # Comentario de una línea estilo Python
    
    ('real_number', r'(?<![A-Za-z0-9_])[-+]?\d+\.\d+(?![\d])'),        # Número real (positivo o negativo)
    
    ('invalid_real_number', r'(?<![A-Za-z0-9_])[-+]?\d+\.(?!\d)'),

    ('integer_number', r'(?<![A-Za-z0-9_])[-+]?\d+(?![\d.])'),                # Número entero
    
    ('logical_relational_operator', r'(\|\||&&|==|!=|<=|>=|<|>)'),  # Operadores relacionales/lógicos
    ('arithmetic_operator', r'(\+\+|--|\+|-|\*|/|%|\^)'),            # Operadores aritméticos
    ('assignment', r'='),                           # Asignación
    ('symbol', r'[\(\)\{\},;]'),                    # Símbolos especiales

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
