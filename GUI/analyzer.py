import re

# Definición de colores para cada tipo de token
COLORS = {
    'number': '#FFB86C',
    'identifier': '#F8F8F2',
    'comment': '#6272A4',
    'keyword': '#FF79C6',
    'arithmetic_operator': '#8BE9FD',
    'logical_relational_operator': '#BD93F9',
    'symbol': '#50FA7B',
    'assignment': '#FF5555'
}

# Palabras reservadas del lenguaje
KEYWORDS = {
    'if', 'else', 'do', 'while', 'switch', 'case', 'int', 'float', 'main',
    'for', 'foreach', 'double', 'char', 'string', 'break', 'continue', 'return'
}

# Patrones para los distintos tipos de tokens
PATTERNS = [
    ('multiline_comment', r'/\*[\s\S]*?\*/'),       # Comentario multilínea estilo C
    ('singleline_comment', r'#.*'),                 # Comentario de una línea estilo Python
    ('real_number', r'[+-]?\d+\.\d+'),              # Número real (positivo o negativo)
    ('integer_number', r'[+-]?\d+'),                # Número entero
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

    while position < len(source_code):
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
                    else:
                        real_type = token_type
                    color = COLORS.get(real_type, '#FFFFFF')  # Color por defecto
                    tokens.append((real_type, text, color, line, column))
                    column += len(text)
                position = match.end()
                break
        if not match:
            # Token no válido — resaltarlo en rojo pero seguir
            text = source_code[position]
            tokens.append(('invalid', text, '#FF0000', line, column))
            if text == '\n':
                line += 1
                column = 1
            else:
                column += 1
            position += 1
    return tokens