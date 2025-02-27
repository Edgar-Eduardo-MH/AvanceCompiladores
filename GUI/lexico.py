def lexical_analysis(code):
    # análisis léxico aquí
    tokens = []
    
    return tokens

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as file:
            code = file.read()
        tokens = lexical_analysis(code)
        print("Tokens:", tokens)
    else:
        print("Usage: lexer.py <file>")