"""
Onglet Quick Measure - Mesures rapides avec graphique temps réel
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import numpy as np
import os

class QuickMeasureTab:
    """Onglet de mesure rapide avec graphique"""
    
    def __init__(self, parent, keithley, update_status_callback):
        self.keithley = keithley
        self.update_status = update_status_callback
        
        self.frame = ttk.Frame(parent)
        
        # Variables de mesure
        self.measuring = False
        self.paused = False
        self.data_time = deque(maxlen=10000)
        self.data_values = deque(maxlen=10000)
        self.start_time = None
        self.measure_thread = None
        
        # Configuration actuelle
        self.current_config = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crée les widgets de l'onglet"""

        # Frame principal avec 2 colonnes
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Colonne gauche: Configuration avec scrollbar
        left_container = ttk.Frame(main_frame, width=370)
        left_container.pack(side='left', fill='y', padx=5)
        left_container.pack_propagate(False)

        # Canvas pour le scroll
        self.config_canvas = tk.Canvas(left_container, highlightthickness=0, width=350)
        scrollbar = ttk.Scrollbar(left_container, orient='vertical', command=self.config_canvas.yview)

        # Frame scrollable à l'intérieur du canvas
        self.scrollable_frame = ttk.Frame(self.config_canvas)

        # Configurer le scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.config_canvas.configure(scrollregion=self.config_canvas.bbox("all"))
        )

        self.config_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.config_canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas et scrollbar
        self.config_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Scroll avec la molette de la souris (seulement sur le panneau config)
        self.config_canvas.bind("<Enter>", lambda e: self.config_canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.config_canvas.bind("<Leave>", lambda e: self.config_canvas.unbind_all("<MouseWheel>"))

        # Colonne droite: Graphique
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)

        # === CONFIGURATION ===
        self.create_config_section(self.scrollable_frame)

        # === GRAPHIQUE ===
        self.create_graph_section(right_frame)

    def _on_mousewheel(self, event):
        """Gère le scroll avec la molette de la souris"""
        self.config_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _add_logo(self):
        """Ajoute le logo OptiMag dans la figure, en bas à droite (sous l'axe X)"""
        try:
            from PIL import Image

            # Chemin du logo (même dossier que le script principal)
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(script_dir, 'logo_optimag.png')

            if os.path.exists(logo_path):
                # Charger et redimensionner avec PIL
                pil_image = Image.open(logo_path)

                # Redimensionner pour une hauteur de ~30 pixels
                target_height = 30
                aspect = pil_image.width / pil_image.height
                new_width = int(target_height * aspect)
                pil_image = pil_image.resize((new_width, target_height), Image.LANCZOS)

                # Convertir en array numpy pour matplotlib
                logo = np.array(pil_image)

                # Ajuster la figure pour laisser de la place en bas
                self.fig.subplots_adjust(bottom=0.12)

                # Utiliser AnnotationBbox pour un positionnement relatif
                # Coordonnées en fraction de figure (0-1): bas-droite = (0.98, 0.01)
                imagebox = OffsetImage(logo, zoom=1.0, alpha=0.8)
                ab = AnnotationBbox(imagebox, (0.98, 0.01),
                                   xycoords='figure fraction',
                                   boxcoords='figure fraction',
                                   box_alignment=(1.0, 0.0),  # Ancrage bas-droite
                                   frameon=False)
                self.fig.add_artist(ab)

        except Exception as e:
            # Si le logo ne peut pas être chargé, on continue sans
            print(f"Logo non chargé: {e}")

    def create_config_section(self, parent):
        """Crée la section de configuration"""

        # Calibres par type de mesure (Keithley 2000)
        self.ranges_by_type = {
            'DCV': ['AUTO', '0.1 V', '1 V', '10 V', '100 V', '1000 V'],
            'ACV': ['AUTO', '0.1 V', '1 V', '10 V', '100 V', '750 V'],
            'DCI': ['AUTO', '10 mA', '100 mA', '1 A', '3 A'],
            'ACI': ['AUTO', '1 A', '3 A'],
            'RES_2W': ['AUTO', '100 Ω', '1 kΩ', '10 kΩ', '100 kΩ', '1 MΩ', '10 MΩ', '100 MΩ'],
            'RES_4W': ['AUTO', '100 Ω', '1 kΩ', '10 kΩ', '100 kΩ', '1 MΩ', '10 MΩ', '100 MΩ'],
        }

        # Type de mesure
        meas_frame = ttk.LabelFrame(parent, text="Type de Mesure", padding=10)
        meas_frame.pack(fill='x', pady=5)

        self.meas_type_var = tk.StringVar(value='DCV')

        measures = [
            ('DCV - Tension DC', 'DCV'),
            ('ACV - Tension AC', 'ACV'),
            ('DCI - Courant DC', 'DCI'),
            ('ACI - Courant AC', 'ACI'),
            ('RES_2W - Résistance 2 fils', 'RES_2W'),
            ('RES_4W - Résistance 4 fils', 'RES_4W'),
        ]

        for text, value in measures:
            rb = ttk.Radiobutton(meas_frame, text=text, variable=self.meas_type_var, value=value,
                                 command=self.on_measure_type_changed)
            rb.pack(anchor='w', pady=2)

        # Configuration mesure
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding=10)
        config_frame.pack(fill='x', pady=5)

        # Calibre
        range_frame = ttk.Frame(config_frame)
        range_frame.pack(fill='x', pady=2)

        ttk.Label(range_frame, text="Calibre:").pack(side='left')
        self.range_var = tk.StringVar(value='AUTO')
        self.range_combo = ttk.Combobox(range_frame, textvariable=self.range_var, width=15, state='readonly')
        self.range_combo['values'] = self.ranges_by_type['DCV']
        self.range_combo.pack(side='left', padx=5)
        
        # NPLC (temps d'intégration)
        nplc_frame = ttk.LabelFrame(config_frame, text="NPLC (temps d'intégration)", padding=5)
        nplc_frame.pack(fill='x', pady=5)

        nplc_select_frame = ttk.Frame(nplc_frame)
        nplc_select_frame.pack(fill='x')

        self.nplc_var = tk.DoubleVar(value=1.0)
        nplc_combo = ttk.Combobox(nplc_select_frame, textvariable=self.nplc_var, width=10, state='readonly')
        nplc_combo['values'] = [0.01, 0.1, 1.0, 5.0, 10.0]
        nplc_combo.pack(side='left', padx=5)

        nplc_help = ttk.Label(nplc_frame, text="Nombre de cycles secteur pour la mesure.\n"
                              "0.01 = rapide (~0.2ms), moins précis, plus de bruit\n"
                              "10 = lent (~200ms), très précis, peu de bruit",
                              font=('Arial', 8), foreground='gray')
        nplc_help.pack(anchor='w', padx=5)

        # Options vitesse
        speed_frame = ttk.LabelFrame(parent, text="Options Vitesse", padding=10)
        speed_frame.pack(fill='x', pady=5)

        # Mode Buffer (le plus rapide)
        self.buffer_mode_var = tk.BooleanVar(value=False)
        buffer_cb = ttk.Checkbutton(speed_frame, text="Mode Buffer (acquisition rapide)",
                                    variable=self.buffer_mode_var,
                                    command=self.toggle_buffer_mode)
        buffer_cb.pack(anchor='w', pady=2)
        self.buffer_help = ttk.Label(speed_frame, text="   1024 points max, ~2000 mes/s avec NPLC=0.01",
                                     font=('Arial', 8), foreground='gray')
        self.buffer_help.pack(anchor='w')

        # Nombre de points buffer (créé mais pas affiché initialement)
        self.buffer_points_frame = ttk.Frame(speed_frame)
        ttk.Label(self.buffer_points_frame, text="   Nb points:").pack(side='left')
        self.buffer_points_var = tk.IntVar(value=1024)
        buffer_points_spin = ttk.Spinbox(self.buffer_points_frame, from_=10, to=1024,
                                         textvariable=self.buffer_points_var, width=8)
        buffer_points_spin.pack(side='left', padx=5)

        self.buffer_separator = ttk.Separator(speed_frame, orient='horizontal')
        self.buffer_separator.pack(fill='x', pady=5)

        self.fast_mode_var = tk.BooleanVar(value=False)
        self.fast_cb = ttk.Checkbutton(speed_frame, text="Mode Fast",
                                       variable=self.fast_mode_var)
        self.fast_cb.pack(anchor='w', pady=2)
        self.fast_help = ttk.Label(speed_frame, text="   Réduit la communication GPIB (gain ~10-20%)",
                                   font=('Arial', 8), foreground='gray')
        self.fast_help.pack(anchor='w')

        self.display_off_var = tk.BooleanVar(value=False)
        display_cb = ttk.Checkbutton(speed_frame, text="Désactiver affichage instrument",
                                     variable=self.display_off_var)
        display_cb.pack(anchor='w', pady=2)
        display_help = ttk.Label(speed_frame, text="   L'écran du Keithley s'éteint, gain ~10-15%",
                                 font=('Arial', 8), foreground='gray')
        display_help.pack(anchor='w')

        self.filter_var = tk.BooleanVar(value=False)
        filter_cb = ttk.Checkbutton(speed_frame, text="Filtre numérique (moyenne glissante)",
                                    variable=self.filter_var,
                                    command=self.toggle_filter)
        filter_cb.pack(anchor='w', pady=2)

        # Nombre de points pour le filtre
        self.filter_frame = ttk.Frame(speed_frame)
        ttk.Label(self.filter_frame, text="   Nb points:").pack(side='left')
        self.filter_count_var = tk.IntVar(value=10)
        filter_spin = ttk.Spinbox(self.filter_frame, from_=2, to=100,
                                  textvariable=self.filter_count_var, width=8)
        filter_spin.pack(side='left', padx=5)

        # Acquisition
        self.acq_frame = ttk.LabelFrame(parent, text="Acquisition", padding=10)
        self.acq_frame.pack(fill='x', pady=5)

        # Intervalle entre mesures (masqué en mode buffer)
        self.interval_frame = ttk.Frame(self.acq_frame)
        self.interval_frame.pack(fill='x', pady=2)

        ttk.Label(self.interval_frame, text="Intervalle (s):").pack(side='left')
        self.interval_var = tk.DoubleVar(value=0.1)
        self.interval_spin = ttk.Spinbox(self.interval_frame, from_=0.05, to=3600, increment=0.05,
                                         textvariable=self.interval_var, width=10, format='%.2f')
        self.interval_spin.pack(side='left', padx=5)

        self.interval_help = ttk.Label(self.acq_frame, text="Min 0.05s (~20 mes/s max avec NPLC=0.01)",
                                       font=('Arial', 8), foreground='gray')
        self.interval_help.pack(anchor='w', padx=5)

        # Message mode buffer (affiché uniquement en mode buffer)
        self.buffer_info_label = ttk.Label(self.acq_frame,
                                           text="Mode Buffer: acquisition au plus vite (pas d'intervalle)",
                                           font=('Arial', 9, 'italic'), foreground='blue')

        # Durée maximale
        duration_frame = ttk.Frame(self.acq_frame)
        duration_frame.pack(fill='x', pady=2)

        self.duration_mode_var = tk.StringVar(value='infinite')

        self.inf_rb = ttk.Radiobutton(duration_frame, text="Durée infinie",
                                      variable=self.duration_mode_var, value='infinite')
        self.inf_rb.pack(anchor='w')
        
        dur_rb = ttk.Radiobutton(duration_frame, text="Durée limitée:", 
                                 variable=self.duration_mode_var, value='limited')
        dur_rb.pack(anchor='w')
        
        dur_sub_frame = ttk.Frame(duration_frame)
        dur_sub_frame.pack(fill='x', padx=20)
        
        self.duration_var = tk.DoubleVar(value=60.0)
        dur_spin = ttk.Spinbox(dur_sub_frame, from_=1, to=86400, increment=10,
                               textvariable=self.duration_var, width=10)
        dur_spin.pack(side='left', padx=5)
        ttk.Label(dur_sub_frame, text="secondes").pack(side='left')
        
        # Contrôles
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="▶ Start", 
                                    command=self.start_measurement, width=10)
        self.start_btn.pack(side='left', padx=2)
        
        self.pause_btn = ttk.Button(control_frame, text="⏸ Pause", 
                                    command=self.pause_measurement, width=10, state='disabled')
        self.pause_btn.pack(side='left', padx=2)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ Stop", 
                                   command=self.stop_measurement, width=10, state='disabled')
        self.stop_btn.pack(side='left', padx=2)
        
        self.clear_btn = ttk.Button(control_frame, text="🗑 Clear", 
                                    command=self.clear_data, width=10)
        self.clear_btn.pack(side='left', padx=2)
        
        # Export
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill='x', pady=5)
        
        self.export_btn = ttk.Button(export_frame, text="💾 Export CSV", 
                                     command=self.export_data, width=20)
        self.export_btn.pack(fill='x')
        
        # Statistiques
        stats_frame = ttk.LabelFrame(parent, text="Statistiques", padding=10)
        stats_frame.pack(fill='x', pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=6, width=30, font=('Courier', 9))
        self.stats_text.pack(fill='x')
        self.stats_text.config(state='disabled')
        
        self.update_stats()
    
    def create_graph_section(self, parent):
        """Crée la section graphique"""
        
        # Options graphique
        self.graph_options_frame = ttk.Frame(parent)
        self.graph_options_frame.pack(fill='x', pady=5)

        ttk.Label(self.graph_options_frame, text="Affichage:").pack(side='left', padx=5)

        self.display_mode_var = tk.StringVar(value='Autoscale')
        display_mode_combo = ttk.Combobox(self.graph_options_frame, textvariable=self.display_mode_var,
                                          width=20, state='readonly')
        display_mode_combo['values'] = [
            'Autoscale',
            '100 derniers points',
            '500 derniers points',
            '1000 derniers points',
            'Manuel (zoom libre)',
            'Manuel (limites fixes)',
            'Fixe X, Auto Y',
            'Auto X, Fixe Y'
        ]
        display_mode_combo.pack(side='left', padx=5)
        display_mode_combo.bind('<<ComboboxSelected>>', self.on_display_mode_changed)

        ttk.Button(self.graph_options_frame, text="Zoom Reset",
                  command=self.reset_zoom).pack(side='left', padx=5)

        # Checkbox curseur
        self.cursor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.graph_options_frame, text="Curseur",
                       variable=self.cursor_var,
                       command=self.toggle_cursor).pack(side='left', padx=10)

        # Bouton export données visibles
        ttk.Button(self.graph_options_frame, text="Export visible",
                  command=self.export_visible_data).pack(side='left', padx=5)

        # Frame pour les limites manuelles (masquée par défaut) - tout sur une ligne
        self.manual_limits_frame = ttk.Frame(parent)

        # X min/max
        ttk.Label(self.manual_limits_frame, text="X:").pack(side='left', padx=(5, 2))
        self.x_min_var = tk.StringVar(value='0')
        ttk.Entry(self.manual_limits_frame, textvariable=self.x_min_var, width=8).pack(side='left', padx=2)
        ttk.Label(self.manual_limits_frame, text="à").pack(side='left')
        self.x_max_var = tk.StringVar(value='100')
        ttk.Entry(self.manual_limits_frame, textvariable=self.x_max_var, width=8).pack(side='left', padx=2)
        ttk.Button(self.manual_limits_frame, text="X", width=2,
                  command=lambda: self.apply_manual_limits('x')).pack(side='left', padx=2)

        # Séparateur
        ttk.Label(self.manual_limits_frame, text=" | ").pack(side='left')

        # Y min/max
        ttk.Label(self.manual_limits_frame, text="Y:").pack(side='left', padx=(2, 2))
        self.y_min_var = tk.StringVar(value='0')
        ttk.Entry(self.manual_limits_frame, textvariable=self.y_min_var, width=8).pack(side='left', padx=2)
        ttk.Label(self.manual_limits_frame, text="à").pack(side='left')
        self.y_max_var = tk.StringVar(value='10')
        ttk.Entry(self.manual_limits_frame, textvariable=self.y_max_var, width=8).pack(side='left', padx=2)
        ttk.Button(self.manual_limits_frame, text="Y", width=2,
                  command=lambda: self.apply_manual_limits('y')).pack(side='left', padx=2)

        # Séparateur + bouton X+Y
        ttk.Label(self.manual_limits_frame, text=" | ").pack(side='left')
        ttk.Button(self.manual_limits_frame, text="X+Y",
                  command=lambda: self.apply_manual_limits('xy')).pack(side='left', padx=2)
        
        # Graphique matplotlib
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Temps (s)')
        self.ax.set_ylabel('Valeur')
        self.ax.set_title('Mesure en temps réel')
        self.ax.grid(True, alpha=0.3)

        self.line, = self.ax.plot([], [], 'b-', linewidth=1.5)

        # Crosshair (curseur) - lignes invisibles par défaut
        self.hline = self.ax.axhline(y=0, color='red', linestyle='--', linewidth=0.8, visible=False)
        self.vline = self.ax.axvline(x=0, color='red', linestyle='--', linewidth=0.8, visible=False)
        self.cursor_point, = self.ax.plot([], [], 'ro', markersize=6, visible=False)

        # Annotation pour les coordonnées
        self.cursor_annotation = self.ax.annotate('', xy=(0, 0), xytext=(10, 10),
                                                   textcoords='offset points',
                                                   bbox=dict(boxstyle='round,pad=0.3',
                                                            facecolor='yellow', alpha=0.8),
                                                   fontsize=9, visible=False)

        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Connecter l'événement mouvement souris
        self.cursor_cid = None

        # Barre d'outils matplotlib
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()

        # Logo OptiMag en bas à droite (dans la figure)
        self._add_logo()
    
    def on_measure_type_changed(self):
        """Met à jour les calibres disponibles selon le type de mesure"""
        meas_type = self.meas_type_var.get()
        if meas_type in self.ranges_by_type:
            self.range_combo['values'] = self.ranges_by_type[meas_type]
            self.range_var.set('AUTO')

    def convert_range_to_value(self, range_str):
        """Convertit le calibre affiché en valeur numérique pour le Keithley"""
        if range_str == 'AUTO':
            return 'AUTO'

        # Extraire le nombre et l'unité
        parts = range_str.split()
        if len(parts) != 2:
            return range_str

        value = float(parts[0])
        unit = parts[1]

        # Conversion selon l'unité
        multipliers = {
            'V': 1,
            'mA': 0.001,
            'A': 1,
            'Ω': 1,
            'kΩ': 1000,
            'MΩ': 1000000,
        }

        multiplier = multipliers.get(unit, 1)
        return value * multiplier

    def toggle_filter(self):
        """Active/désactive le frame du filtre"""
        if self.filter_var.get():
            self.filter_frame.pack(fill='x', pady=2)
        else:
            self.filter_frame.pack_forget()

    def toggle_buffer_mode(self):
        """Active/désactive le mode buffer et ajuste l'interface"""
        if self.buffer_mode_var.get():
            # Mode buffer activé - afficher nb points après le label d'aide
            self.buffer_points_frame.pack(after=self.buffer_help, fill='x', pady=2)
            self.interval_frame.pack_forget()
            self.interval_help.pack_forget()
            self.buffer_info_label.pack(anchor='w', padx=5, pady=2)
            # Désactiver mode Fast (inutile en buffer)
            self.fast_mode_var.set(False)
            self.fast_cb.config(state='disabled')
            # Désactiver durée infinie (buffer = nombre de points fixe)
            self.duration_mode_var.set('limited')
            self.inf_rb.config(state='disabled')
        else:
            # Mode buffer désactivé
            self.buffer_points_frame.pack_forget()
            self.buffer_info_label.pack_forget()
            self.interval_frame.pack(fill='x', pady=2)
            self.interval_help.pack(anchor='w', padx=5)
            self.fast_cb.config(state='normal')
            self.inf_rb.config(state='normal')

    def start_measurement(self):
        """Démarre l'acquisition"""
        if not self.keithley.connected:
            messagebox.showerror("Erreur", "Aucun instrument connecté!")
            return

        # Sauvegarde de la configuration
        self.save_current_config()

        # Configuration de l'instrument
        try:
            meas_type = self.meas_type_var.get()
            range_display = self.range_var.get()
            range_val = self.convert_range_to_value(range_display)
            nplc = self.nplc_var.get()

            self.keithley.configure_measurement(meas_type, range_val)
            self.keithley.set_nplc(nplc, meas_type)

            # Filtre
            if self.filter_var.get():
                self.keithley.set_filter(True, self.filter_count_var.get())
            else:
                self.keithley.set_filter(False)

            # Affichage instrument
            if self.display_off_var.get():
                self.keithley.set_display(False)

            # Mode buffer: désactiver autozero pour plus de vitesse
            if self.buffer_mode_var.get():
                self.keithley.set_autozero(False)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de configuration:\n{e}")
            return

        # Clear des données si nouvelles mesures
        if len(self.data_time) > 0 and messagebox.askyesno("Nouveau démarrage",
                                                           "Effacer les données précédentes ?"):
            self.clear_data()

        # Démarrage
        self.measuring = True
        self.paused = False
        self.start_time = time.time()

        # Mise à jour de l'interface
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        if self.buffer_mode_var.get():
            # Mode Buffer
            self.pause_btn.config(state='disabled')  # Pas de pause en mode buffer
            self.update_status("Acquisition buffer en cours...", "green")
            self.measure_thread = threading.Thread(target=self.buffer_measurement_loop, daemon=True)
        else:
            # Mode Normal
            self.pause_btn.config(state='normal')
            self.update_status("Mesure en cours...", "green")
            self.measure_thread = threading.Thread(target=self.measurement_loop, daemon=True)

        self.measure_thread.start()

        # Démarrage de l'animation (seulement en mode normal)
        if not self.buffer_mode_var.get():
            self.animate_graph()
    
    def pause_measurement(self):
        """Met en pause l'acquisition"""
        self.paused = not self.paused
        
        if self.paused:
            self.pause_btn.config(text="▶ Resume")
            self.update_status("Mesure en pause", "orange")
        else:
            self.pause_btn.config(text="⏸ Pause")
            self.update_status("Mesure en cours...", "green")
    
    def stop_measurement(self):
        """Arrête l'acquisition"""
        self.measuring = False
        self.paused = False

        # Attendre la fin du thread
        if self.measure_thread and self.measure_thread.is_alive():
            self.measure_thread.join(timeout=2.0)

        # Restaurer les paramètres de l'instrument
        if self.keithley.connected:
            try:
                if self.display_off_var.get():
                    self.keithley.set_display(True)
                if self.buffer_mode_var.get():
                    self.keithley.set_autozero(True)  # Restaurer autozero
            except:
                pass

        # Mise à jour de l'interface
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text="⏸ Pause")
        self.stop_btn.config(state='disabled')
        self.update_status("Mesure arrêtée", "orange")

        # Mise à jour finale du graphique et des stats
        self.update_graph()
        self.update_stats()
    
    def measurement_loop(self):
        """Boucle d'acquisition (thread séparé)"""
        interval = self.interval_var.get()
        duration_mode = self.duration_mode_var.get()
        max_duration = self.duration_var.get() if duration_mode == 'limited' else float('inf')
        
        fast_mode = self.fast_mode_var.get()
        
        while self.measuring:
            if not self.paused:
                try:
                    # Temps écoulé
                    elapsed = time.time() - self.start_time
                    
                    # Vérifier durée maximale
                    if elapsed > max_duration:
                        self.frame.after(0, self.stop_measurement)
                        break
                    
                    # Mesure
                    if fast_mode:
                        value = self.keithley.measure_fast()
                    else:
                        value = self.keithley.measure_single()
                    
                    # Ajout des données
                    self.data_time.append(elapsed)
                    self.data_values.append(value)
                    
                except Exception as e:
                    self.frame.after(0, lambda: self.update_status(f"Erreur: {e}", "red"))
                    self.frame.after(0, self.stop_measurement)
                    break
            
            # Attente avant prochaine mesure
            time.sleep(interval)

    def buffer_measurement_loop(self):
        """Boucle d'acquisition en mode buffer (thread séparé)"""
        try:
            n_points = self.buffer_points_var.get()

            # Configurer et démarrer le buffer
            self.frame.after(0, lambda: self.update_status(
                f"Configuration buffer ({n_points} points)...", "orange"))

            self.keithley.buffer_configure(n_points)
            self.keithley.buffer_start(n_points)

            self.frame.after(0, lambda: self.update_status(
                f"Acquisition buffer en cours (0/{n_points})...", "green"))

            # Attendre la fin de l'acquisition avec mise à jour du statut
            while self.measuring:
                current = self.keithley.buffer_get_count()
                self.frame.after(0, lambda c=current: self.update_status(
                    f"Acquisition buffer en cours ({c}/{n_points})...", "green"))

                if self.keithley.buffer_is_complete():
                    break

                time.sleep(0.1)  # Polling toutes les 100ms

            if not self.measuring:
                # Arrêt demandé par l'utilisateur
                return

            # Lire les données du buffer
            self.frame.after(0, lambda: self.update_status("Lecture du buffer...", "orange"))

            values = self.keithley.buffer_read()
            end_time = time.time()
            total_duration = end_time - self.start_time

            # Calculer les timestamps (répartis uniformément)
            if len(values) > 1:
                time_step = total_duration / (len(values) - 1)
                for i, val in enumerate(values):
                    self.data_time.append(i * time_step)
                    self.data_values.append(val)
            elif len(values) == 1:
                self.data_time.append(0)
                self.data_values.append(values[0])

            # Mise à jour finale
            self.frame.after(0, self.update_graph)
            self.frame.after(0, self.update_stats)
            self.frame.after(0, lambda: self.update_status(
                f"Buffer terminé: {len(values)} points en {total_duration:.2f}s", "green"))
            self.frame.after(0, self.stop_measurement)

        except Exception as e:
            self.frame.after(0, lambda: self.update_status(f"Erreur buffer: {e}", "red"))
            self.frame.after(0, self.stop_measurement)

    def animate_graph(self):
        """Animation du graphique (appelé périodiquement)"""
        if self.measuring:
            self.update_graph()
            self.update_stats()
            self.frame.after(100, self.animate_graph)  # Mise à jour toutes les 100ms
    
    def update_graph(self):
        """Met à jour le graphique"""
        if len(self.data_time) == 0:
            return

        # Conversion en arrays numpy
        x_data = np.array(self.data_time)
        y_data = np.array(self.data_values)

        # Mise à jour de la ligne
        self.line.set_data(x_data, y_data)

        # Mode d'affichage
        mode = self.display_mode_var.get()

        if mode == 'Autoscale':
            # Afficher toutes les données
            self.ax.set_autoscale_on(True)
            self.ax.relim()
            self.ax.autoscale_view(True, True, True)

        elif mode == 'Manuel (zoom libre)' or mode == 'Manuel (limites fixes)':
            # Ne rien faire, l'utilisateur contrôle le zoom
            pass

        elif mode == 'Fixe X, Auto Y':
            # X fixe (défini par l'utilisateur), Y autoscale
            # Trouver les Y min/max pour les points visibles en X
            x_min, x_max = self.ax.get_xlim()
            mask = (x_data >= x_min) & (x_data <= x_max)
            if np.any(mask):
                visible_y = y_data[mask]
                y_min, y_max = np.min(visible_y), np.max(visible_y)
                margin = (y_max - y_min) * 0.1 if y_max != y_min else abs(y_min) * 0.1 or 0.1
                self.ax.set_ylim(y_min - margin, y_max + margin)

        elif mode == 'Auto X, Fixe Y':
            # X autoscale, Y fixe (défini par l'utilisateur)
            self.ax.set_xlim(np.min(x_data), np.max(x_data))

        elif 'derniers points' in mode:
            # Mode défilement: extraire le nombre de points
            if '100' in mode:
                n_points = 100
            elif '500' in mode:
                n_points = 500
            elif '1000' in mode:
                n_points = 1000
            else:
                n_points = 100

            if len(x_data) > n_points:
                x_min = x_data[-n_points]
                x_max = x_data[-1]
                # Trouver les Y min/max pour les points visibles
                visible_y = y_data[-n_points:]
                y_min, y_max = np.min(visible_y), np.max(visible_y)
                margin = (y_max - y_min) * 0.1 if y_max != y_min else abs(y_min) * 0.1 or 0.1
                self.ax.set_xlim(x_min, x_max)
                self.ax.set_ylim(y_min - margin, y_max + margin)
            else:
                # Pas assez de points: afficher tout
                self.ax.relim()
                self.ax.autoscale_view()

        # Rafraîchissement
        self.canvas.draw_idle()
    
    def update_stats(self):
        """Met à jour les statistiques"""
        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', 'end')

        if len(self.data_values) > 0:
            values = np.array(self.data_values)
            times = np.array(self.data_time)

            stats = f"""Points:  {len(values)}
Min:     {np.min(values):.6g}
Max:     {np.max(values):.6g}
Moyenne: {np.mean(values):.6g}
Std Dev: {np.std(values):.6g}
Dernier: {values[-1]:.6g}"""

            # Calcul du temps moyen entre mesures
            if len(times) > 1:
                intervals = np.diff(times)
                avg_interval = np.mean(intervals)
                rate = 1.0 / avg_interval if avg_interval > 0 else 0
                stats += f"\n--- Vitesse ---\nIntervalle: {avg_interval*1000:.1f} ms\nCadence:  {rate:.1f} mes/s"

            self.stats_text.insert('1.0', stats)
        else:
            self.stats_text.insert('1.0', "Aucune donnée")

        self.stats_text.config(state='disabled')
    
    def clear_data(self):
        """Efface les données (possible même pendant une mesure)"""
        if self.measuring:
            if not messagebox.askyesno("Confirmation",
                    "Effacer les données pendant la mesure en cours ?"):
                return

        self.data_time.clear()
        self.data_values.clear()
        self.line.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        self.update_stats()

        # Réinitialiser le temps de départ si mesure en cours
        if self.measuring:
            self.start_time = time.time()
    
    def reset_zoom(self):
        """Réinitialise le zoom du graphique"""
        if len(self.data_time) > 0:
            # Réactiver l'autoscale
            self.ax.set_autoscale_on(True)
            self.ax.relim()
            self.ax.autoscale_view(True, True, True)
            self.canvas.draw()
            # Remettre le mode sur "Autoscale"
            self.display_mode_var.set('Autoscale')
            # Masquer les limites manuelles
            self.manual_limits_frame.pack_forget()

    def on_display_mode_changed(self, event=None):
        """Affiche/masque les champs de limites selon le mode"""
        mode = self.display_mode_var.get()
        if mode in ('Manuel (limites fixes)', 'Fixe X, Auto Y', 'Auto X, Fixe Y'):
            # Afficher la frame des limites (après self.graph_options_frame)
            self.manual_limits_frame.pack(fill='x', pady=5, after=self.graph_options_frame)
        else:
            self.manual_limits_frame.pack_forget()

    def apply_manual_limits(self, axis='xy'):
        """Applique les limites manuelles au graphique
        Args:
            axis: 'x', 'y' ou 'xy' pour choisir quel(s) axe(s) modifier
        """
        try:
            # Validation et application X
            if axis in ('x', 'xy'):
                x_min = float(self.x_min_var.get())
                x_max = float(self.x_max_var.get())
                if x_min >= x_max:
                    messagebox.showwarning("Erreur", "X min doit être inférieur à X max")
                    return
                self.ax.set_xlim(x_min, x_max)

            # Validation et application Y
            if axis in ('y', 'xy'):
                y_min = float(self.y_min_var.get())
                y_max = float(self.y_max_var.get())
                if y_min >= y_max:
                    messagebox.showwarning("Erreur", "Y min doit être inférieur à Y max")
                    return
                self.ax.set_ylim(y_min, y_max)

            self.canvas.draw()

        except ValueError:
            messagebox.showwarning("Erreur", "Veuillez entrer des valeurs numériques valides")

    def toggle_cursor(self):
        """Active/désactive le curseur crosshair"""
        if self.cursor_var.get():
            # Activer le curseur
            self.cursor_cid = self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        else:
            # Désactiver le curseur
            if self.cursor_cid:
                self.canvas.mpl_disconnect(self.cursor_cid)
                self.cursor_cid = None
            # Masquer les éléments du curseur
            self.hline.set_visible(False)
            self.vline.set_visible(False)
            self.cursor_point.set_visible(False)
            self.cursor_annotation.set_visible(False)
            self.canvas.draw_idle()

    def on_mouse_move(self, event):
        """Gère le mouvement de la souris pour le curseur"""
        # Vérifier que la souris est dans les axes et qu'il y a des données
        if event.inaxes != self.ax or len(self.data_time) == 0:
            self.hline.set_visible(False)
            self.vline.set_visible(False)
            self.cursor_point.set_visible(False)
            self.cursor_annotation.set_visible(False)
            self.canvas.draw_idle()
            return

        # Trouver le point le plus proche sur la courbe
        x_mouse = event.xdata
        x_data = np.array(self.data_time)
        y_data = np.array(self.data_values)

        # Trouver l'index du point le plus proche en X
        idx = np.abs(x_data - x_mouse).argmin()
        x_snap = x_data[idx]
        y_snap = y_data[idx]

        # Mettre à jour le crosshair
        self.hline.set_ydata([y_snap, y_snap])
        self.vline.set_xdata([x_snap, x_snap])
        self.cursor_point.set_data([x_snap], [y_snap])

        # Mettre à jour l'annotation
        self.cursor_annotation.xy = (x_snap, y_snap)
        self.cursor_annotation.set_text(f'X: {x_snap:.3f} s\nY: {y_snap:.6g}')

        # Afficher les éléments
        self.hline.set_visible(True)
        self.vline.set_visible(True)
        self.cursor_point.set_visible(True)
        self.cursor_annotation.set_visible(True)

        self.canvas.draw_idle()

    def save_current_config(self):
        """Sauvegarde la configuration actuelle"""
        self.current_config = {
            'timestamp': datetime.now().isoformat(),
            'measurement_type': self.meas_type_var.get(),
            'range': self.range_var.get(),
            'nplc': self.nplc_var.get(),
            'buffer_mode': self.buffer_mode_var.get(),
            'buffer_points': self.buffer_points_var.get() if self.buffer_mode_var.get() else 0,
            'fast_mode': self.fast_mode_var.get(),
            'display_off': self.display_off_var.get(),
            'filter': self.filter_var.get(),
            'filter_count': self.filter_count_var.get() if self.filter_var.get() else 0,
            'interval': self.interval_var.get() if not self.buffer_mode_var.get() else 'N/A (buffer)',
            'duration_mode': self.duration_mode_var.get(),
            'max_duration': self.duration_var.get()
        }
    
    def export_data(self):
        """Exporte les données en CSV avec métadonnées"""
        if len(self.data_time) == 0:
            messagebox.showwarning("Attention", "Aucune donnée à exporter")
            return
        
        # Dialogue de sauvegarde
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"keithley_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                # En-tête avec métadonnées
                # Note: utf-8-sig ajoute un BOM pour compatibilité Excel
                f.write("# Keithley 2000 Measurement Data\n")
                f.write(f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Measurement Type: {self.current_config.get('measurement_type', 'N/A')}\n")
                f.write(f"# Range: {self.current_config.get('range', 'N/A')}\n")
                f.write(f"# NPLC: {self.current_config.get('nplc', 'N/A')}\n")
                f.write(f"# Buffer Mode: {self.current_config.get('buffer_mode', 'N/A')}\n")
                f.write(f"# Buffer Points: {self.current_config.get('buffer_points', 'N/A')}\n")
                f.write(f"# Fast Mode: {self.current_config.get('fast_mode', 'N/A')}\n")
                f.write(f"# Display Off: {self.current_config.get('display_off', 'N/A')}\n")
                f.write(f"# Filter: {self.current_config.get('filter', 'N/A')}\n")
                f.write(f"# Filter Count: {self.current_config.get('filter_count', 'N/A')}\n")
                f.write(f"# Sample Interval: {self.current_config.get('interval', 'N/A')} s\n")
                f.write(f"# GPIB Address: {self.keithley.meter.resource_name if self.keithley.connected else 'N/A'}\n")
                
                # Statistiques
                values = np.array(self.data_values)
                f.write(f"# Statistics - Min: {np.min(values):.6g}, Max: {np.max(values):.6g}, Mean: {np.mean(values):.6g}, Std: {np.std(values):.6g}\n")
                f.write("#\n")
                
                # En-tête des colonnes
                unit = self.keithley.get_unit() if self.keithley.connected else ''
                f.write(f"Time(s),Value,Unit\n")
                
                # Données
                for t, v in zip(self.data_time, self.data_values):
                    f.write(f"{t:.6f},{v:.10g},{unit}\n")
            
            messagebox.showinfo("Succès", f"Données exportées:\n{filename}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'export:\n{e}")

    def export_visible_data(self):
        """Exporte uniquement les données visibles dans la vue actuelle du graphique"""
        if len(self.data_time) == 0:
            messagebox.showwarning("Attention", "Aucune donnée à exporter")
            return

        # Obtenir les limites actuelles des axes
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        # Filtrer les données dans la plage X visible
        x_data = np.array(self.data_time)
        y_data = np.array(self.data_values)

        mask = (x_data >= x_min) & (x_data <= x_max)
        visible_x = x_data[mask]
        visible_y = y_data[mask]

        if len(visible_x) == 0:
            messagebox.showwarning("Attention", "Aucune donnée visible dans la plage actuelle")
            return

        # Dialogue de sauvegarde
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"keithley_visible_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                # En-tête avec métadonnées
                f.write("# Keithley 2000 Measurement Data (VISIBLE RANGE ONLY)\n")
                f.write(f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Visible X Range: {x_min:.6f} to {x_max:.6f} s\n")
                f.write(f"# Visible Y Range: {y_min:.6g} to {y_max:.6g}\n")
                f.write(f"# Points in range: {len(visible_x)} / {len(self.data_time)} total\n")
                f.write(f"# Measurement Type: {self.current_config.get('measurement_type', 'N/A')}\n")
                f.write(f"# Range: {self.current_config.get('range', 'N/A')}\n")
                f.write(f"# NPLC: {self.current_config.get('nplc', 'N/A')}\n")
                f.write(f"# GPIB Address: {self.keithley.meter.resource_name if self.keithley.connected else 'N/A'}\n")

                # Statistiques des données visibles
                f.write(f"# Statistics (visible) - Min: {np.min(visible_y):.6g}, Max: {np.max(visible_y):.6g}, Mean: {np.mean(visible_y):.6g}, Std: {np.std(visible_y):.6g}\n")
                f.write("#\n")

                # En-tête des colonnes
                unit = self.keithley.get_unit() if self.keithley.connected else ''
                f.write(f"Time(s),Value,Unit\n")

                # Données visibles uniquement
                for t, v in zip(visible_x, visible_y):
                    f.write(f"{t:.6f},{v:.10g},{unit}\n")

            messagebox.showinfo("Succès", f"Données visibles exportées ({len(visible_x)} points):\n{filename}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'export:\n{e}")
