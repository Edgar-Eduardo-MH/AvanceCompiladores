import tkinter as tk, os, sys
from tkinter import messagebox, ttk, filedialog
from analyzer import lexical_analyzer, Parser

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

        self.last_tokens = None

        self.fullscreen = True  # Estado inicial
        self.root.attributes('-fullscreen', True)

        # Asignar eventos de teclado
        self.root.bind("<F11>", self.toggle_fullscreen)  # Alternar con F11
        self.root.bind("<Escape>", self.exit_fullscreen)  # Salir con Escape

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
        scrollbar = ttk.Scrollbar(text_frame, command=self.sync_scroll, style="Vertical.TScrollbar")
        scrollbar.grid(row=0, column=2, sticky="ns")
        self.code_text_area.config(yscrollcommand=scrollbar.set)
        self.line_numbers.config(yscrollcommand=scrollbar.set)

        # Scrollbar horizontal
        h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal", command=self.code_text_area.xview, style="Horizontal.TScrollbar")
        h_scrollbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.code_text_area.config(xscrollcommand=h_scrollbar.set)

        # Sincronizar el área de texto con los números de línea
        self.code_text_area.bind("<MouseWheel>", self.on_scroll)
        self.code_text_area.bind("<Button-4>", self.on_scroll)  # Para Linux
        self.code_text_area.bind("<Button-5>", self.on_scroll)  # Para Linux

        # Configuración del grid para el frame de texto
        text_frame.grid_columnconfigure(1, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        # Mostrar número de línea y columna
        self.line_column_label = tk.Label(text_frame, text="Línea: 1, Columna: 1", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg=self.STATUS_BAR_BG, fg=self.TEXT_COLOR)
        self.line_column_label.grid(row=2, column=1, sticky="we", columnspan=1)

        self.code_text_area.bind("<KeyRelease>", self.handle_key_release)
        self.code_text_area.bind("<Return>", self.update_line_numbers)
        self.code_text_area.bind("<BackSpace>", self.update_line_numbers)
        self.code_text_area.bind("<ButtonRelease-1>", self.update_line_column)

        # Pestañas de retroalimentacion sobre lexico, semantica, y esas cosas
        self.top_tab = ttk.Notebook(root)
        self.top_tab.configure(style="TNotebook")
        self.top_tab.grid(row=0, column=1, sticky="nsew", padx=10, pady=10,)

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

        self.bottom_tab.config(height=100)
        self.bottom_tab.grid_propagate(False)
        self.top_tab.config(width=200)
        self.top_tab.grid_propagate(False)

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
        
        # Estilo para Treeview
        style.configure("Treeview",
                        background=self.TEXT_BG,
                        foreground=self.TEXT_COLOR,
                        fieldbackground=self.TEXT_BG,
                        bordercolor=self.BORDER_COLOR,
                        rowheight=25)
        style.map("Treeview",
                  background=[('selected', self.SELECTED_TAB)],
                  foreground=[('selected', self.TEXT_COLOR)])
        style.configure("Treeview.Heading",
                        background=self.STATUS_BAR_BG,
                        foreground=self.TEXT_COLOR,
                        font=("Consolas", 10, "bold"))


    def create_menu_bar(self):
        menubar = tk.Menu(self.root, bg=self.BORDER_COLOR, fg=self.TEXT_COLOR)

        def resource_path(relative_path):
            """ Obtiene la ruta correcta dentro del ejecutable o normal en visual """
            if getattr(sys, 'frozen', False):  # Si el script está compilado con PyInstaller
                base_path = sys._MEIPASS  # Carpeta temporal donde PyInstaller guarda archivos
            else:
                base_path = os.path.abspath(".")  # Carpeta normal en modo desarrollo
            return os.path.join(base_path, relative_path)

        # menu archive
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.TAB_BG, fg=self.TEXT_COLOR)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.close_file)
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

        # Crear una segunda barra (frame) para los botones con íconos
        icon_bar = tk.Frame(self.root, bg=self.BORDER_COLOR)
        icon_bar.grid(row=1, column=0, sticky="ew", padx=10)
        # Cargar imágenes para los botones
        self.new_icon = tk.PhotoImage(file=resource_path("icons/new.png")).subsample(15, 15)
        self.open_icon = tk.PhotoImage(file=resource_path("icons/open.png")).subsample(17, 17)
        self.save_icon = tk.PhotoImage(file=resource_path("icons/save.png")).subsample(23, 23)
        self.saveas_icon = tk.PhotoImage(file=resource_path("icons/save_as.png")).subsample(20, 20)
        self.exit_icon = tk.PhotoImage(file=resource_path("icons/exit.png")).subsample(20, 20)

        # Crear botones con imágenes para la barra de íconos
        btn_new = tk.Button(icon_bar, image=self.new_icon, command=self.new_file, borderwidth=1, width=25, height=25)
        btn_open = tk.Button(icon_bar, image=self.open_icon, command=self.open_file, borderwidth=1, width=25, height=25)
        btn_save = tk.Button(icon_bar, image=self.save_icon, command=self.save_file, borderwidth=1, width=25, height=25)
        btn_saveas = tk.Button(icon_bar, image=self.saveas_icon, command=self.save_file_as, borderwidth=1, width=25, height=25)
        btn_exit = tk.Button(icon_bar, image=self.exit_icon, command=self.close_file, borderwidth=1, width=25, height=25)

        # Posicionar botones en la barra de íconos
        btn_new.grid(row=0, column=0, padx=2, pady=2)
        btn_open.grid(row=0, column=1, padx=2, pady=2)
        btn_save.grid(row=0, column=2, padx=2, pady=2)
        btn_saveas.grid(row=0, column=3, padx=2, pady=2)
        btn_exit.grid(row=0, column=4, padx=2, pady=2)

    def create_output_area(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
        output = tk.Text(frame, wrap="word", bg=self.TEXT_BG, fg=self.TEXT_COLOR, font=("Consolas", 12), height=4)
        output.pack(expand=True, fill="both")
        return output

    def lexical_analysis(self):
        text_widget = self.code_text_area
        text = text_widget.get(1.0, tk.END)

        tokens = lexical_analyzer(text)

        for tag in text_widget.tag_names():
            text_widget.tag_delete(tag)

        if not tokens:
            return

        output_valid = self.create_output_area(self.lexicon_tab)
        output_error = self.create_output_area(self.error_lexicon_tab)

        token_lines = []
        error_lines = []

        for idx, token in enumerate(tokens):
            if len(token) >= 5:
                token_type, lexeme, color, line, column = token
                start_index = f"{line}.{column - 1}"
                end_index = f"{line}.{column - 1 + len(lexeme)}"
                tag_name = f"token_{idx}"

                if token_type == 'comment':
                    continue

                text_widget.tag_add(tag_name, start_index, end_index)
                text_widget.tag_config(tag_name, foreground=color)

                if token_type != 'invalid':
                    output_tag = f"output_token_{idx}"
                    token_str = f"{lexeme} ({token_type}) (Line: {line}, Column: {column})\n"
                    output_valid.insert(tk.END, token_str, output_tag)
                    output_valid.tag_config(output_tag, foreground=color)
                    token_lines.append(token_str)
                else:
                    tag_error = f"error_token_{idx}"
                    text_widget.tag_add(tag_error, start_index, end_index)
                    text_widget.tag_config(tag_error, foreground="#FF0000")

                    if lexeme.endswith('.'):
                        error_str = f"Numerical error: '{lexeme}' it is not a valid real number (Line: {line}, Column: {column})\n"
                    else:
                        error_str = f"Error: '{lexeme}' not recognized (Line: {line}, Column: {column})\n"

                    output_error.insert(tk.END, error_str, "error")
                    output_error.tag_config("error", foreground="#FF0000")
                    error_lines.append(error_str)

        output_valid.config(state=tk.DISABLED)
        output_error.config(state=tk.DISABLED)

        with open("tokens.txt", "w", encoding="utf-8") as token_file:
            token_file.writelines(token_lines)

        with open("errors.txt", "w", encoding="utf-8") as error_file:
            error_file.writelines(error_lines)

        self.last_tokens = tokens
        self.syntactic_analysis()

    def build_treeview_ast(self, treeview, parent_item, node):
        """Recursivamente construye el Treeview a partir del AST."""
        if node is None:
            return

        node_text = str(node) # Asume que tu clase AST_Node tiene un método __str__ descriptivo
        item_id = treeview.insert(parent_item, "end", text=node_text, open=True)

        # Aquí, necesitas acceder a los hijos de tu nodo AST.
        # Esto dependerá de cómo está estructurada tu clase de nodos AST.
        # Por ejemplo, si tienes una lista de hijos en cada nodo:
        if hasattr(node, 'children') and isinstance(node.children, list):
            for child in node.children:
                self.build_treeview_ast(treeview, item_id, child)
        # O si tienes atributos específicos para los hijos (e.g., 'left', 'right'):
        elif hasattr(node, 'left') and node.left is not None:
            self.build_treeview_ast(treeview, item_id, node.left)
        elif hasattr(node, 'right') and node.right is not None:
            self.build_treeview_ast(treeview, item_id, node.right)
        # Agrega más casos según la estructura de tu AST

    def syntactic_analysis(self):
        text_widget = self.code_text_area
        source_code = text_widget.get(1.0, tk.END)

        tokens = self.last_tokens if self.last_tokens else lexical_analyzer(source_code)

        # Limpiar el contenido anterior de la pestaña sintáctica
        for widget in self.syntactic_tab.winfo_children():
            widget.destroy()

        parser = Parser(tokens)
        ast = parser.parse()

        # Crear el Treeview para mostrar el AST
        tree_frame = ttk.Frame(self.syntactic_tab, style="TFrame")
        tree_frame.pack(expand=True, fill="both")

        # Configurar el Treeview para que se expanda en el frame
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Usar grid para el Treeview dentro de tree_frame
        tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse", style="Treeview")
        tree.grid(row=0, column=0, sticky="nsew")

        # Configurar la columna principal del Treeview
        # Esto es crucial para controlar el ancho.
        # Puedes ajustar este valor si el texto sigue encimándose.
        tree.column("#0", width=400, minwidth=200, anchor="w")
        # El anchor="w" asegura que el texto se alinee a la izquierda.

        # Scrollbar para el Treeview (ahora usando grid)
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
        tree_scrollbar_y.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=tree_scrollbar_y.set)

        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview, style="Horizontal.TScrollbar")
        tree_scrollbar_x.grid(row=1, column=0, sticky="ew")
        tree.configure(xscrollcommand=tree_scrollbar_x.set)


        if ast is None:
            tree.insert("", "end", text="⚠️ No AST generated or syntax errors present.")
        else:
            self.build_treeview_ast(tree, "", ast) # Inicia la construcción desde la raíz

        # Asegúrate de que el frame de errores también se limpie y actualice
        output_error_syntax = self.create_output_area(self.error_syntactic_tab)
        output_error_syntax.delete(1.0, tk.END) # Limpiar errores anteriores
        output_error_syntax.insert(tk.END, "Syntactic errors:\n", "error")
        output_error_syntax.tag_config("error", foreground="red")

        if parser.errors:
            for err in parser.errors:
                output_error_syntax.insert(tk.END, f"{err}\n", "errors")
        else:
            output_error_syntax.insert(tk.END, "No syntactic errors found.\n", "success")
            output_error_syntax.tag_config("success", foreground="green")

        output_error_syntax.config(state=tk.DISABLED)

    def build_treeview_ast(self, treeview, parent_item, node):
        """Recursively constructs the Treeview from the AST."""
        if node is None:
            return

        node_text = str(node)

        if node.type == 'Program':
            node_text = f"Program (Line: {getattr(node, 'line', '?')}, Column: {getattr(node, 'column', '?')})"


        item_id = treeview.insert(parent_item, "end", text=node_text, open=True)

        if hasattr(node, 'children') and isinstance(node.children, list):
            for child in node.children:
                self.build_treeview_ast(treeview, item_id, child)
        elif hasattr(node, 'declarations') and isinstance(node.declarations, list):
            for decl in node.declarations:
                self.build_treeview_ast(treeview, item_id, decl)
        elif hasattr(node, 'statements') and isinstance(node.statements, list):
            for stmt in node.statements:
                self.build_treeview_ast(treeview, item_id, stmt)


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
        self.lexical_analysis()
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

    def close_file(self):
        """ Cierra el archivo actual sin cerrar la aplicación """
        self.code_text_area.delete(1.0, tk.END)  # Limpia el área de texto
        self.current_file = None
        self.root.title("Compiler Interface - Sin archivo abierto")
        self.update_line_numbers()
        print("Archivo cerrado")

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

    def handle_key_release(self, event=None):
        """Maneja la actualización de números de línea y posición del cursor."""
        self.update_line_numbers()
        self.update_line_column()
        self.lexical_analysis()

    def update_line_column(self, event=None):
        """Actualiza la posición actual del cursor."""
        line, column = self.code_text_area.index(tk.INSERT).split('.')
        self.line_column_label.config(text=f"Línea: {line}, Columna: {int(column)+1}")

    def update_line_numbers(self, event=None):
        """Actualiza los números de línea."""
        self.line_numbers.config(state=tk.NORMAL)

        scroll_position = self.code_text_area.yview()

        self.line_numbers.delete(1.0, tk.END)

        lines = int(self.code_text_area.index('end-1c').split('.')[0])

        line_numbers_string = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.insert(tk.END, line_numbers_string)

        self.line_numbers.config(state=tk.DISABLED)
        self.line_numbers.yview_moveto(scroll_position[0])

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

    #Configuracion pantalla completa
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes('-fullscreen', False)

    def save_to_file(filename, lines):
        """Escribe en el archivo y lo sobreescribe si ya existe"""
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(lines)

