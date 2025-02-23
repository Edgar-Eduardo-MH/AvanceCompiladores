from tkinter import Tk
from gui import Compiler_GUI

if __name__ == "__main__":
    root = Tk()
    #Obtengo los valores de la pantalla, ancho y alto
    SCREEN_WIDTH = root.winfo_screenwidth()
    SCREEN_HEIGHT = root.winfo_screenheight()

    # Que ocupe casi toda la pantalla
    root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}+0+0")
    root.attributes('-fullscreen',False)
    root.resizable(True,True)
    #Instancia
    app = Compiler_GUI(root)

    root.mainloop()