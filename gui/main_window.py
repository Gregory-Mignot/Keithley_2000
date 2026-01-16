"""
Fenêtre principale avec système d'onglets
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Import des onglets
#sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .settings_tab import SettingsTab
from .quick_measure_tab import QuickMeasureTab
from .advanced_tab import AdvancedTab
from keithley2000 import Keithley2000

class MainWindow:
    """Fenêtre principale de l'application"""
    
    def __init__(self, root):
        self.root = root
        self.keithley = Keithley2000()
        
        # Style
        self.setup_style()
        
        # Barre de statut
        self.create_status_bar()
        
        # Création des onglets
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Onglet 1: Settings
        self.settings_tab = SettingsTab(self.notebook, self.keithley, self.update_status)
        self.notebook.add(self.settings_tab.frame, text='⚙️ Réglages')
        
        # Onglet 2: Quick Measure
        self.quick_measure_tab = QuickMeasureTab(self.notebook, self.keithley, self.update_status)
        self.notebook.add(self.quick_measure_tab.frame, text='📊 Mesures Rapides')
        
        # Onglet 3: Advanced Control
        self.advanced_tab = AdvancedTab(self.notebook, self.keithley, self.update_status)
        self.notebook.add(self.advanced_tab.frame, text='🔧 Réglages Avancés')
        
        # Mise à jour initiale du statut
        self.update_status("Prêt - Aucun instrument connecté", "red")
    
    def setup_style(self):
        """Configure le style de l'application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs personnalisées
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('Status.TLabel', background='#e0e0e0', relief='sunken', padding=5)
    
    def create_status_bar(self):
        """Crée la barre de statut en bas de la fenêtre"""
        status_frame = ttk.Frame(self.root, style='Status.TLabel')
        status_frame.pack(side='bottom', fill='x')
        
        # Indicateur LED
        self.status_led = tk.Canvas(status_frame, width=20, height=20, 
                                     bg='#e0e0e0', highlightthickness=0)
        self.status_led.pack(side='left', padx=5)
        self.led_indicator = self.status_led.create_oval(5, 5, 15, 15, fill='red')
        
        # Message de statut
        self.status_label = ttk.Label(status_frame, text="", style='Status.TLabel')
        self.status_label.pack(side='left', fill='x', expand=True)
        
		# Crédits
        self.credits_label = ttk.Label(status_frame, text="Programme créé par Grégory Mignot pour le laboratoire OptiMag (2026).  https://github.com/Gregory-Mignot/Keithley_2000", style='Status.TLabel')
        self.credits_label.pack(side='right', padx=5)
		
        # Heure
        #self.time_label = ttk.Label(status_frame, text="", style='Status.TLabel')
        #self.time_label.pack(side='right', padx=5)
        #self.update_time()
    
    def update_status(self, message, color='black'):
        """
        Met à jour la barre de statut
        Args:
            message (str): Message à afficher
            color (str): Couleur de l'indicateur LED
        """
        self.status_label.config(text=message)
        
        # Couleur LED selon statut
        led_colors = {
            'green': '#00ff00',
            'red': '#ff0000',
            'orange': '#ff8800',
            'yellow': '#ffff00'
        }
        self.status_led.itemconfig(self.led_indicator, fill=led_colors.get(color, color))
    
    def update_time(self):
        """Met à jour l'heure dans la barre de statut"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def confirm_exit(self):
        """
        Demande confirmation avant de quitter
        Returns:
            bool: True si l'utilisateur confirme
        """
        # Vérifier si une mesure est en cours
        if hasattr(self.quick_measure_tab, 'measuring') and self.quick_measure_tab.measuring:
            response = messagebox.askyesno(
                "Mesure en cours",
                "Une mesure est en cours. Voulez-vous vraiment quitter ?"
            )
            if not response:
                return False
            
            # Arrêter la mesure
            self.quick_measure_tab.stop_measurement()
        
        # Déconnecter l'instrument
        if self.keithley.connected:
            try:
                self.keithley.disconnect()
            except:
                pass
        
        return True
