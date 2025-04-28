import re

# Definicion de variables
COLORES = {
    'numero': 'Color 1',
    'identificador': 'Color 2',
    'comentario': 'Color 3',
    'reservada': 'Color 4',
    'operador_aritmetico': 'Color 5',
    'operador_relacional_logico': 'Color 6',
    'simbolo': 'Color 7',
    'asignacion': 'Color 4'
}

PALABRAS_RESERVADAS = {
    'if', 'else', 'do', 'while', 'switch', 'case', 'int', 'float', 'main', 'for', 'foreach', 'double', 'char', 'string', 'break', 'continue', 'return',
}

PATRONES = [
    ('comentario_multilinea', r'/\*[\s\S]*?\*/'),  # Multilínea estilo C
    ('comentario_linea', r'#.*'),  # Comentario una línea estilo python
    ('numero_real', r'[+-]?\d+\.\d+'),  # Número real ya sea positivo o negativo
    ('numero_entero', r'[+-]?\d+'),  # Número entero
    ('operador_relacional_logico', r'(\|\||&&|==|!=|<=|>=|<|>)'),  # Relacionales y lógicos
    ('operador_aritmetico', r'(\+\+|--|\+|-|\*|/|%|\^)'),  # Aritméticos
    ('asignacion', r'='),  # Asignación
    ('simbolo', r'[\(\)\{\},;]'),  # Símbolos especiales
    ('identificador', r'[A-Za-z_][A-Za-z0-9_]*'),  # Identificador válido
    ('espacio', r'\s+'),  # Espacios que se van a irgnorar
]

# analizador lexico - tokenizador
def analizador_lexico(codigo_fuente):
    tokens = []
    posicion = 0
    while posicion < len(codigo_fuente):
        match = None
        for tipo, patron in PATRONES:
            regex = re.compile(patron)
            match = regex.match(codigo_fuente, posicion)
            if match:
                texto = match.group(0)
                if tipo == 'espacio':
                    # Ignorar espacios
                    pass
                elif tipo == 'identificador' and texto in PALABRAS_RESERVADAS:
                    tokens.append(('reservada', texto, COLORES['reservada']))
                else:
                    tokens.append((tipo, texto, COLORES.get(tipo, 'Color Default')))
                posicion = match.end()
                break
        if not match:
            # No se reconoció un token válido
            raise SyntaxError(f"Token inválido en posición {posicion}: '{codigo_fuente[posicion]}'")
    return tokens