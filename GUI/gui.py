import tkinter as tk
from tkinter import messagebox, ttk, filedialog

class Compiler_GUI:
    def __init__(self, root):
        self.BG_COLOR = "#1B1D23"
        self.TAB_BG = "#23272A" 
        self.TEXT_BG = "#1E2124" 
        self.BORDER_COLOR = "#40444B"
        self.TEXT_COLOR = "#FFFFFF"
        self.FRAME_BG = "#474E68"
        self.LINE_NUM_BG = "#343A50"
        self.LINE_NUM_FG = "#E0E0E0"
        self.STATUS_BAR_BG = "#6B728E"
        self.BUTTON_BG = "#5865F2"
        self.BUTTON_FG = "#FFFFFF"
        self.ENTRY_BG = "#1E1E1E"
        self.BORDER_TAB = "#2E2E2E"
        self.SELECTED_TAB = "#303540"
        self.ARROW_SCROLL = "#50575D"
        self.DARK_GRAY_SCROLL = "#1E1E1E"
        self.DARKER_GRAY_SCROLL = "#121212"
        self.BORDER_SCROLL = "#1E1E1E"
    
        
        # aqui creo la ventana principal
        self.root = root
        self.root.title("Compiler Interface")
        self.root.configure(padx=0, pady=0, bg=self.BG_COLOR)

        #configuracion de estilo del ttk(notebooks y tabs)
        self.configure_styles()

        self.root.grid_columnconfigure(0, weight=1)  # columnas
        self.root.grid_rowconfigure(0, weight=1)  # filas

        self.current_file = None  # Ruta del archivo actual
        self.create_menu_bar()

        # Widgets/Areas para aplicacion
        # Frame para el área de texto y los números de línea
        text_frame = tk.Frame(root, bg=self.FRAME_BG)
        text_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Números de línea
        self.line_numbers = tk.Text(text_frame, width=4, wrap=tk.NONE, font=("Consolas", 12), bg=self.LINE_NUM_BG, fg=self.LINE_NUM_FG, bd=0)
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        self.line_numbers.insert(tk.END, "1\n")
        self.line_numbers.config(state=tk.DISABLED)  # Hacerlo de solo lectura

        # Codigo o area de texto
        self.code_text_area = tk.Text(text_frame, wrap=tk.NONE, font=("Consolas", 12), bd=0, bg=self.LINE_NUM_BG, fg=self.LINE_NUM_FG, insertbackground=self.TEXT_COLOR)  # sirve para crear el text area, el tipo de wrap que usara y la fuente y tamano
        self.code_text_area.grid(row=0, column=1, sticky="nsew")  # determina la ubicacion del area y donde la deseamos

        # Scrollbar vertical
        #scrollbar = tk.Scrollbar(text_frame, command=self.sync_scroll, bg=self.BORDER_TAB, troughcolor=self.ENTRY_BG, highlightbackground=self.ENTRY_BG, activebackground=self.ARROW_SCROLL)
        scrollbar = ttk.Scrollbar(text_frame, command=self.sync_scroll, style="Vertical.TScrollbar")

        scrollbar.grid(row=0, column=2, sticky="ns")
        self.code_text_area.config(yscrollcommand=scrollbar.set)
        self.line_numbers.config(yscrollcommand=scrollbar.set)

        # Scrollbar horizontal
        #h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.code_text_area.xview, bg=self.BORDER_TAB, troughcolor=self.ENTRY_BG, highlightbackground=self.ENTRY_BG, activebackground=self.ARROW_SCROLL)
        h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal", command=self.code_text_area.xview, style="Horizontal.TScrollbar")

        h_scrollbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.code_text_area.config(xscrollcommand=h_scrollbar.set)

        # Sincronizar el área de texto con los números de línea
        self.code_text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.code_text_area.bind("<MouseWheel>", self.on_scroll)
        self.code_text_area.bind("<Button-4>", self.on_scroll)  # Para Linux
        self.code_text_area.bind("<Button-5>", self.on_scroll)  # Para Linux

         # Configuración del grid para el frame de texto
        text_frame.grid_columnconfigure(1, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        # Mostrar número de línea y columna
        self.line_column_label = tk.Label(text_frame, text="Línea: 1, Columna: 1", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg=self.STATUS_BAR_BG, fg=self.TEXT_COLOR)
        self.line_column_label.grid(row=2, column=1, sticky="we", columnspan=1)
        self.code_text_area.bind("<KeyRelease>", self.update_line_column)  # Mover esta línea aquí

        # Pestañas de retroalimentacion sobre lexico, semantica, y esas cosas
        self.top_tab = ttk.Notebook(root)
        self.top_tab.configure(style="TNotebook")
        self.top_tab.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Pestañas frame lateral derecho
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

        # Configuración del grid para la ventana principal
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Pestañas frame inferior retroalimentacion de errores por tipo
        self.bottom_tab = ttk.Notebook(root)
        self.bottom_tab.configure(style="TNotebook")
        self.bottom_tab.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))

        self.error_lexicon_tab = ttk.Frame(self.bottom_tab)
        self.error_syntactic_tab = ttk.Frame(self.bottom_tab)
        self.error_semantic_tab = ttk.Frame(self.bottom_tab)
        self.results_tab = ttk.Frame(self.bottom_tab)

        self.bottom_tab.add(self.error_lexicon_tab, text="Lexicon Error")
        self.bottom_tab.add(self.error_syntactic_tab, text="Syntactic Error")
        self.bottom_tab.add(self.error_semantic_tab, text="Semantic Error")
        self.bottom_tab.add(self.results_tab, text="Results")

        # Configuracion del grid pa que se expandan chido
        self.root.grid_rowconfigure(0, weight=1)  # area de texto
        self.root.grid_rowconfigure(2, weight=1)  # frame inferior
        self.root.grid_columnconfigure(0, weight=2)  # namas una columna

        
    def configure_styles(self):
        style = ttk.Style(self.root)

        style.theme_use("clam")
        #scrolls
        style.configure("Vertical.TScrollbar", background=self.DARK_GRAY_SCROLL, troughcolor=self.DARKER_GRAY_SCROLL, bordercolor=self.BORDER_SCROLL, arrowcolor=self.ARROW_SCROLL)
        style.configure("Horizontal.TScrollbar", background=self.DARK_GRAY_SCROLL, troughcolor=self.DARKER_GRAY_SCROLL, bordercolor=self.BORDER_SCROLL, arrowcolor=self.ARROW_SCROLL)
        #fondo de los notebooks
        style.configure("TNotebook",background=self.FRAME_BG, borderwidth=0, relief="flat")    
        style.configure("TNotebook.Tab", background=self.LINE_NUM_BG, foreground=self.TEXT_COLOR, padding=(10,8), font=("Arial", 12, "bold"), borderwidth=1, relief="solid",
                        highlighthickness=0, highlightbackground=self.BORDER_TAB, highlightcolor=self.BORDER_TAB)
        style.map("TNotebook.Tab", background=[("selected", self.SELECTED_TAB)], foreground=[("selected", self.TEXT_COLOR)], bordercolor=[("selected","#50575D"),("!selected","#2E2E2E")], 
                  highlightcolor=[("selected","#2E2E2E"), ("!selected","#2E2E2E")])
        #fondo de los frames de las notebooks
        style.configure("TFrame", background=self.FRAME_BG)
        #fondo de labels y lo demas
        style.configure("TLabel", background=self.FRAME_BG, foreground=self.TEXT_COLOR)
        style.configure("TButton", background=self.BUTTON_BG, foreground=self.BUTTON_FG, font=("Arial", 10, "bold"), padding=(5,5), borderwidth=1, relief="flat")
        style.map("TButton", background=[("active","#4850D4")])
        style.configure("TEntry", background=self.ENTRY_BG, foreground=self.TEXT_COLOR, insertcolor=self.TEXT_COLOR, padding=(5,5), borderwidth=1) 


    def create_menu_bar(self):
        menubar = tk.Menu(self.root, bg=self.BORDER_COLOR, fg=self.TEXT_COLOR)

        # menu archive
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.TAB_BG, fg=self.TEXT_COLOR)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Menú Compilar
        compile_menu = tk.Menu(menubar, tearoff=0)
        compile_menu.add_command(label="Lexical Analysis", command=self.lexical_analysis)
        compile_menu.add_command(label="Syntactic Analysis", command=self.syntactic_analysis)
        compile_menu.add_command(label="Semantic Analysis", command=self.semantic_analysis)
        compile_menu.add_command(label="Generate Intermediate Code", command=self.generate_intermediate_code)
        compile_menu.add_command(label="Execute", command=self.execute)
        menubar.add_cascade(label="Compile", menu=compile_menu)

        # menu edit
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # menu ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About of", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def lexical_analysis(self):
        # Llamar al analizador léxico
        print("Análisis léxico ejecutado")

    def syntactic_analysis(self):
        # Llamar al analizador sintáctico
        print("Análisis sintáctico ejecutado")

    def semantic_analysis(self):
        # Llamar al analizador semántico
        print("Análisis semántico ejecutado")

    def generate_intermediate_code(self):
        # Generar código intermedio
        print("Código intermedio generado")

    def execute(self):
        # Ejecutar el código
        print("Ejecución completada")

    def new_file(self):
        self.code_text_area.delete(1.0, tk.END)  # Limpiar el área de texto
        self.current_file = None
        self.root.title("Compiler Interface - New File")
        self.update_line_numbers()
        print("Nuevo archivo creado")

    def open_file(self):
        self.update_line_numbers()
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.code_text_area.delete(1.0, tk.END)
                self.code_text_area.insert(tk.END, file.read())
            self.current_file = file_path
            self.root.title(f"Compiler Interface - {file_path}")
        self.update_line_numbers()
        print("Abrir archivo")

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.code_text_area.get(1.0, tk.END))
        else:
            self.save_file_as()
        print("Guardar archivo")

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.code_text_area.get(1.0, tk.END))
            self.current_file = file_path
            self.root.title(f"Compiler Interface - {file_path}")
        print("Guardar archivo como")

    def copy_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.code_text_area.selection_get())
        print("Texto copiado")

    def paste_text(self):
        self.code_text_area.insert(tk.INSERT, self.root.clipboard_get())
        print("Texto pegado")

    def show_about(self):
        messagebox.showinfo("About", "Compiler Interface v1.0\nDesarrollado por Scroto Company")
        print("Acerca de info jeje")

    def update_line_column(self, event=None):
        """Actualiza la posición actual del cursor."""
        line, column = self.code_text_area.index(tk.INSERT).split('.')
        self.line_column_label.config(text=f"Línea: {line}, Columna: {int(column)+1}")

    def update_line_numbers(self, event=None):
        """Actualiza los números de línea."""
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete(1.0, tk.END)
        
        # Obtener el número total de líneas, eliminando el salto de línea adicional de Tkinter
        lines = int(self.code_text_area.index(tk.END).split('.')[0]) - 1

        # Insertar los números de línea correctamente
        line_numbers_string = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.insert(tk.END, line_numbers_string)

        self.line_numbers.config(state=tk.DISABLED)

    def on_scroll(self, event):
        """Sincroniza el scroll del área de texto con los números de línea."""
        if event.state & 0x1:
            return # Evita el desplazamiento horizontal con Shift + rueda del mouse
        
        if event.delta:  # Windows y MacOS (rueda del mouse)
            move = -1 if event.delta > 0 else 1
        elif event.num == 4:  # Linux scroll up
            move = -1
        elif event.num == 5:  # Linux scroll down
            move = 1
        else:
            return

        self.code_text_area.yview_scroll(move, "units")
        self.line_numbers.yview_scroll(move, "units")
        return "break"  # Evita el desplazamiento duplicado

    def sync_scroll(self, *args):
        """Sincroniza el desplazamiento con la barra de scroll."""
        self.code_text_area.yview(*args)
        self.line_numbers.yview(*args)
        self.update_line_numbers()