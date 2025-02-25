import tkinter as tk
from tkinter import messagebox, ttk
# from functions import

class Compiler_GUI:
    def __init__(self,root):
        
        # aqui creo la ventana principal
        self.root = root
        self.root.title("Compiler Interface")
        self.root.configure(padx=0, pady=0)

        self.root.grid_columnconfigure(0, weight=1) #columnas
        self.root.grid_rowconfigure(0, weight=1) #filas
        
        self.create_menu_bar()
        #Widgets/Areas para aplicacion
        #Codigo
        self.code_text_area = tk.Text(root, wrap=tk.WORD, font=("Consolas",12)) #sirve para crear el text area, el tipo de wrap que usara y la fuente y tamano
        self.code_text_area.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10) #determina la ubicacion del area y donde la deseamos
        #Pestanas de retroalimentacion sobre lexico, semantica, y esas cosas
        self.top_tab = ttk.Notebook(root)
        self.top_tab.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        #Pestanas frame lateral derecho
        self.lexicon_tab = ttk.Frame(self.top_tab)
        self.syntactic_tab = ttk.Frame(self.top_tab)
        self.semantic_tab = ttk.Frame(self.top_tab)
        self.hash_tab = ttk.Frame(self.top_tab)
        self.inter_code_tab = ttk.Frame(self.top_tab)

        self.top_tab.add(self.lexicon_tab, text="Lexicon")
        self.top_tab.add(self.syntactic_tab, text="Syntactic")
        self.top_tab.add(self.semantic_tab, text="Semantic")
        self.top_tab.add(self.hash_tab, text="Hash")
        self.top_tab.add(self.inter_code_tab, text="Intermediate Code")
        #Pestamas frame inferior retroalimentacion de errores por tipo
        self.bottom_tab = ttk.Notebook(root)
        self.bottom_tab.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0,10))

        self.error_lexicon_tab = ttk.Frame(self.bottom_tab)
        self.error_syntactic_tab = ttk.Frame(self.bottom_tab)
        self.error_semantic_tab = ttk.Frame(self.bottom_tab)
        self.results_tab = ttk.Frame(self.bottom_tab)

        self.bottom_tab.add(self.error_lexicon_tab, text="Lexicon Error")
        self.bottom_tab.add(self.error_syntactic_tab, text="Syntactic Error")
        self.bottom_tab.add(self.error_semantic_tab, text="Semantic Error")
        self.bottom_tab.add(self.results_tab, text="Results")
        #Configuracion del grid pa que se expandan chido
        self.root.grid_rowconfigure(0, weight=1) #area de texto
        self.root.grid_rowconfigure(2, weight=1) #frame inferior
        self.root.grid_columnconfigure(0, weight=2) #namas una columna
        #Agrega contenido a las pestanas
            #self.add_content_to_tabs()
        def add_content_to_tabs(self):
            #namas es pa tener una idea
            tk.Label(self.lexicon_tab, text="Análisis Léxico").grid(row=0, column=0, pady=20)
            tk.Label(self.syntactic_tab, text="Análisis Sintáctico").grid(row=0, column=0, pady=20)
            tk.Label(self.semantic_tab, text="Análisis Semántico").grid(row=0, column=0, pady=20)
            tk.Label(self.hash_tab, text="Tabla de Símbolos").grid(row=0, column=0, pady=20)
            tk.Label(self.inter_code_tab, text="Código Intermedio").grid(row=0, column=0, pady=20)

            tk.Label(self.error_lexicon_tab, text="Errores Léxicos").grid(row=0, column=0, pady=20)
            tk.Label(self.error_syntactic_tab, text="Errores Sintácticos").grid(row=0, column=0, pady=20)
            tk.Label(self.error_semantic_tab, text="Errores Semánticos").grid(row=0, column=0, pady=20)
            tk.Label(self.results_tab, text="Resultados").grid(row=0, column=0, pady=20)

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)

        #menu archive
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        #file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        #menu edit
        edit_menu = tk.Menu(menubar,tearoff=0)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        menubar.add_cascade(label="Edit",menu=edit_menu)

        #menu ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About of", command=self.show_about)
        menubar.add_cascade(label="Help",menu=help_menu)

        self.root.config(menu=menubar)
            


    # Aqui se mandaran a llamar la funcionalidades de los botones dentro de la interfaz.
    # def compile(self):
    def new_file(self):
        self.text_area.delete(1.0, tk.END)  # Limpiar el área de texto
        print("Nuevo archivo creado")
    def open_file(self):
        print("Abrir archivo")
    def save_file(self):
        print("Guardar archivo")
    def copy_text(self):
        print("Texto copiado")
    def paste_text(self):
        print("Texto pegado")
    def show_about(self):
        print("Acerca de info jeje")
    
    