"""
Keithley 2000 Controller - Point d'entrée principal
Contrôle complet du multimètre Keithley 2000 via GPIB
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Ajout du chemin pour les imports locaux
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    """Point d'entrée principal de l'application"""
    root = tk.Tk()
    root.title("Keithley 2000")
    root.geometry("1200x800")

    # Ouvrir en plein écran (maximisé) au démarrage
    root.state('zoomed')

    # Icône de la fenêtre (optionnel)
    try:
        root.iconbitmap('icone.ico')
    except:
        pass
    
    # Création de la fenêtre principale
    app = MainWindow(root)
    
    # Gestion de la fermeture
    def on_closing():
        if app.confirm_exit():
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Lancement de l'application
    root.mainloop()

if __name__ == "__main__":
    main()
