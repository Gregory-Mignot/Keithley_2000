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
import numpy as np

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
        
        # Colonne gauche: Configuration
        left_frame = ttk.Frame(main_frame, width=350)
        left_frame.pack(side='left', fill='y', padx=5)
        left_frame.pack_propagate(False)
        
        # Colonne droite: Graphique
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # === CONFIGURATION ===
        self.create_config_section(left_frame)
        
        # === GRAPHIQUE ===
        self.create_graph_section(right_frame)
    
    def create_config_section(self, parent):
        """Crée la section de configuration"""
        
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
            rb = ttk.Radiobutton(meas_frame, text=text, variable=self.meas_type_var, value=value)
            rb.pack(anchor='w', pady=2)
        
        # Configuration mesure
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding=10)
        config_frame.pack(fill='x', pady=5)
        
        # Plage
        range_frame = ttk.Frame(config_frame)
        range_frame.pack(fill='x', pady=2)
        
        ttk.Label(range_frame, text="Plage:").pack(side='left')
        self.range_var = tk.StringVar(value='AUTO')
        range_combo = ttk.Combobox(range_frame, textvariable=self.range_var, width=15, state='readonly')
        range_combo['values'] = ['AUTO', '0.1', '1', '10', '100', '1000']
        range_combo.pack(side='left', padx=5)
        
        # NPLC (résolution)
        nplc_frame = ttk.Frame(config_frame)
        nplc_frame.pack(fill='x', pady=2)
        
        ttk.Label(nplc_frame, text="NPLC:").pack(side='left')
        self.nplc_var = tk.DoubleVar(value=1.0)
        nplc_combo = ttk.Combobox(nplc_frame, textvariable=self.nplc_var, width=15, state='readonly')
        nplc_combo['values'] = [0.01, 0.1, 1.0, 5.0, 10.0]
        nplc_combo.pack(side='left', padx=5)
        
        ttk.Label(nplc_frame, text="(vitesse vs précision)").pack(side='left')
        
        # Options vitesse
        speed_frame = ttk.LabelFrame(parent, text="Options Vitesse", padding=10)
        speed_frame.pack(fill='x', pady=5)
        
        self.fast_mode_var = tk.BooleanVar(value=False)
        fast_cb = ttk.Checkbutton(speed_frame, text="Mode Fast (désactive vérifications)", 
                                  variable=self.fast_mode_var)
        fast_cb.pack(anchor='w', pady=2)
        
        self.filter_var = tk.BooleanVar(value=False)
        filter_cb = ttk.Checkbutton(speed_frame, text="Filtre numérique", 
                                    variable=self.filter_var, 
                                    command=self.toggle_filter)
        filter_cb.pack(anchor='w', pady=2)
        
        # Nombre de points pour le filtre
        self.filter_frame = ttk.Frame(speed_frame)
        ttk.Label(self.filter_frame, text="  Points filtre:").pack(side='left')
        self.filter_count_var = tk.IntVar(value=10)
        filter_spin = ttk.Spinbox(self.filter_frame, from_=2, to=100, 
                                  textvariable=self.filter_count_var, width=8)
        filter_spin.pack(side='left', padx=5)
        
        # Acquisition
        acq_frame = ttk.LabelFrame(parent, text="Acquisition", padding=10)
        acq_frame.pack(fill='x', pady=5)
        
        # Intervalle entre mesures
        interval_frame = ttk.Frame(acq_frame)
        interval_frame.pack(fill='x', pady=2)
        
        ttk.Label(interval_frame, text="Intervalle (s):").pack(side='left')
        self.interval_var = tk.DoubleVar(value=0.1)
        interval_spin = ttk.Spinbox(interval_frame, from_=0.001, to=3600, increment=0.1,
                                    textvariable=self.interval_var, width=10, format='%.3f')
        interval_spin.pack(side='left', padx=5)
        
        # Durée maximale
        duration_frame = ttk.Frame(acq_frame)
        duration_frame.pack(fill='x', pady=2)
        
        self.duration_mode_var = tk.StringVar(value='infinite')
        
        inf_rb = ttk.Radiobutton(duration_frame, text="Durée infinie", 
                                 variable=self.duration_mode_var, value='infinite')
        inf_rb.pack(anchor='w')
        
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
        graph_options_frame = ttk.Frame(parent)
        graph_options_frame.pack(fill='x', pady=5)
        
        self.autoscale_var = tk.BooleanVar(value=True)
        autoscale_cb = ttk.Checkbutton(graph_options_frame, text="Autoscale", 
                                       variable=self.autoscale_var)
        autoscale_cb.pack(side='left', padx=5)
        
        self.scroll_var = tk.BooleanVar(value=True)
        scroll_cb = ttk.Checkbutton(graph_options_frame, text="Défilement continu", 
                                    variable=self.scroll_var)
        scroll_cb.pack(side='left', padx=5)
        
        ttk.Button(graph_options_frame, text="Zoom Reset", 
                  command=self.reset_zoom).pack(side='left', padx=5)
        
        # Graphique matplotlib
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Temps (s)')
        self.ax.set_ylabel('Valeur')
        self.ax.set_title('Mesure en temps réel')
        self.ax.grid(True, alpha=0.3)
        
        self.line, = self.ax.plot([], [], 'b-', linewidth=1.5)
        
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Barre d'outils matplotlib
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()
    
    def toggle_filter(self):
        """Active/désactive le frame du filtre"""
        if self.filter_var.get():
            self.filter_frame.pack(fill='x', pady=2)
        else:
            self.filter_frame.pack_forget()
    
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
            range_val = self.range_var.get()
            nplc = self.nplc_var.get()
            
            self.keithley.configure_measurement(meas_type, range_val)
            self.keithley.set_nplc(nplc)
            
            # Filtre
            if self.filter_var.get():
                self.keithley.set_filter(True, self.filter_count_var.get())
            else:
                self.keithley.set_filter(False)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de configuration:\n{e}")
            return
        
        # Démarrage
        self.measuring = True
        self.paused = False
        self.start_time = time.time()
        
        # Clear des données si nouvelles mesures
        if len(self.data_time) > 0 and messagebox.askyesno("Nouveau démarrage", 
                                                             "Effacer les données précédentes ?"):
            self.clear_data()
        
        # Mise à jour de l'interface
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.stop_btn.config(state='normal')
        self.update_status("Mesure en cours...", "green")
        
        # Démarrage du thread de mesure
        self.measure_thread = threading.Thread(target=self.measurement_loop, daemon=True)
        self.measure_thread.start()
        
        # Démarrage de l'animation
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
        
        # Autoscale ou scroll
        if self.autoscale_var.get():
            self.ax.relim()
            self.ax.autoscale_view()
        elif self.scroll_var.get():
            # Défilement: garder les 100 derniers points visibles
            if len(x_data) > 100:
                x_min = x_data[-100]
                x_max = x_data[-1]
                self.ax.set_xlim(x_min, x_max)
        
        # Rafraîchissement
        self.canvas.draw_idle()
    
    def update_stats(self):
        """Met à jour les statistiques"""
        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', 'end')
        
        if len(self.data_values) > 0:
            values = np.array(self.data_values)
            
            stats = f"""Points: {len(values)}
Min:    {np.min(values):.6g}
Max:    {np.max(values):.6g}
Moyenne:{np.mean(values):.6g}
Std Dev:{np.std(values):.6g}
Dernier:{values[-1]:.6g}"""
            
            self.stats_text.insert('1.0', stats)
        else:
            self.stats_text.insert('1.0', "Aucune donnée")
        
        self.stats_text.config(state='disabled')
    
    def clear_data(self):
        """Efface les données"""
        if self.measuring:
            messagebox.showwarning("Attention", "Arrêtez la mesure avant d'effacer les données")
            return
        
        self.data_time.clear()
        self.data_values.clear()
        self.line.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        self.update_stats()
    
    def reset_zoom(self):
        """Réinitialise le zoom du graphique"""
        if len(self.data_time) > 0:
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
    
    def save_current_config(self):
        """Sauvegarde la configuration actuelle"""
        self.current_config = {
            'timestamp': datetime.now().isoformat(),
            'measurement_type': self.meas_type_var.get(),
            'range': self.range_var.get(),
            'nplc': self.nplc_var.get(),
            'fast_mode': self.fast_mode_var.get(),
            'filter': self.filter_var.get(),
            'filter_count': self.filter_count_var.get() if self.filter_var.get() else 0,
            'interval': self.interval_var.get(),
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
            with open(filename, 'w') as f:
                # En-tête avec métadonnées
                f.write("# Keithley 2000 Measurement Data\n")
                f.write(f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Measurement Type: {self.current_config.get('measurement_type', 'N/A')}\n")
                f.write(f"# Range: {self.current_config.get('range', 'N/A')}\n")
                f.write(f"# NPLC: {self.current_config.get('nplc', 'N/A')}\n")
                f.write(f"# Fast Mode: {self.current_config.get('fast_mode', 'N/A')}\n")
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
