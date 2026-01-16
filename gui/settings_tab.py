"""
Onglet Settings - Configuration de la connexion GPIB
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class SettingsTab:
    """Onglet de configuration de la connexion"""
    
    def __init__(self, parent, keithley, update_status_callback):
        self.keithley = keithley
        self.update_status = update_status_callback
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        
        # Scan automatique au démarrage
        self.root = parent
        self.frame.after(500, self.scan_resources)
    
    def create_widgets(self):
        """Crée les widgets de l'onglet"""
        
        # Titre
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = ttk.Label(title_frame, text="Configuration GPIB", 
                                font=('Arial', 16, 'bold'))
        title_label.pack(anchor='w')
        
        # Zone de connexion
        conn_frame = ttk.LabelFrame(self.frame, text="Connexion Instrument", padding=10)
        conn_frame.pack(fill='x', padx=20, pady=10)
        
        # Ligne 1: Sélection ressource
        res_frame = ttk.Frame(conn_frame)
        res_frame.pack(fill='x', pady=5)
        
        ttk.Label(res_frame, text="Ressource VISA:").pack(side='left', padx=5)
        
        self.resource_var = tk.StringVar()
        self.resource_combo = ttk.Combobox(res_frame, textvariable=self.resource_var, 
                                           width=40, state='readonly')
        self.resource_combo.pack(side='left', padx=5)
        
        self.scan_btn = ttk.Button(res_frame, text="🔍 Scan", command=self.scan_resources)
        self.scan_btn.pack(side='left', padx=5)
        
        # Ligne 2: Timeout
        timeout_frame = ttk.Frame(conn_frame)
        timeout_frame.pack(fill='x', pady=5)
        
        ttk.Label(timeout_frame, text="Timeout (ms):").pack(side='left', padx=5)
        
        self.timeout_var = tk.IntVar(value=5000)
        timeout_spin = ttk.Spinbox(timeout_frame, from_=1000, to=30000, 
                                   increment=1000, textvariable=self.timeout_var, width=10)
        timeout_spin.pack(side='left', padx=5)
        
        # Ligne 3: Boutons connexion
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.pack(fill='x', pady=10)
        
        self.connect_btn = ttk.Button(btn_frame, text="🔌 Connecter", 
                                      command=self.connect_instrument, width=15)
        self.connect_btn.pack(side='left', padx=5)
        
        self.disconnect_btn = ttk.Button(btn_frame, text="❌ Déconnecter", 
                                         command=self.disconnect_instrument, 
                                         width=15, state='disabled')
        self.disconnect_btn.pack(side='left', padx=5)
        
        self.test_btn = ttk.Button(btn_frame, text="🧪 Test", 
                                   command=self.test_connection, 
                                   width=15, state='disabled')
        self.test_btn.pack(side='left', padx=5)
        
        # Zone d'information instrument
        info_frame = ttk.LabelFrame(self.frame, text="Information Instrument", padding=10)
        info_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.info_text = tk.Text(info_frame, height=10, width=60, 
                                 font=('Courier', 10), state='disabled')
        self.info_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(info_frame, command=self.info_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.info_text.config(yscrollcommand=scrollbar.set)
        
        # Zone aide
        help_frame = ttk.LabelFrame(self.frame, text="Aide", padding=10)
        help_frame.pack(fill='x', padx=20, pady=10)
        
        help_text = """
📌 Connexion GPIB:
1. Cliquez sur 'Scan' pour détecter les instruments
2. Sélectionnez votre Keithley 2000 dans la liste
3. Cliquez sur 'Connect' pour établir la connexion
4. Utilisez 'Test' pour vérifier la communication

⚠️ Note: Assurez-vous que les drivers Agilent/Keysight sont installés.
        """
        
        help_label = ttk.Label(help_frame, text=help_text, justify='left')
        help_label.pack(anchor='w')
    
    def scan_resources(self):
        """Scan des ressources VISA disponibles"""
        self.update_status("Scan des ressources VISA...", "orange")
        self.scan_btn.config(state='disabled')
        
        def scan_thread():
            try:
                resources = self.keithley.list_resources()
                
                # Mise à jour de l'interface dans le thread principal
                self.frame.after(0, lambda: self.update_resource_list(resources))
                
            except Exception as e:
                self.frame.after(0, lambda: self.show_scan_error(str(e)))
            finally:
                self.frame.after(0, lambda: self.scan_btn.config(state='normal'))
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def update_resource_list(self, resources):
        """Met à jour la liste des ressources"""
        if resources:
            self.resource_combo['values'] = resources
            
            # Sélectionner le premier GPIB trouvé
            gpib_resources = [r for r in resources if 'GPIB' in r.upper()]
            if gpib_resources:
                self.resource_combo.set(gpib_resources[0])
            elif resources:
                self.resource_combo.set(resources[0])
            
            self.update_status(f"{len(resources)} ressource(s) trouvée(s)", "green")
            self.add_info(f"✓ {len(resources)} ressource(s) VISA détectée(s)")
            for res in resources:
                self.add_info(f"  - {res}")
        else:
            self.update_status("Aucune ressource trouvée", "red")
            self.add_info("✗ Aucune ressource VISA détectée")
            self.add_info("  Vérifiez que:")
            self.add_info("  - La carte GPIB est installée")
            self.add_info("  - Les drivers sont installés")
            self.add_info("  - L'instrument est allumé")
    
    def show_scan_error(self, error_msg):
        """Affiche une erreur de scan"""
        self.update_status("Erreur lors du scan", "red")
        self.add_info(f"✗ Erreur: {error_msg}")
        messagebox.showerror("Erreur", f"Impossible de scanner les ressources:\n{error_msg}")
    
    def connect_instrument(self):
        """Établit la connexion avec l'instrument"""
        resource = self.resource_var.get()
        
        if not resource:
            messagebox.showwarning("Attention", "Veuillez sélectionner une ressource VISA")
            return
        
        self.update_status("Connexion en cours...", "orange")
        self.connect_btn.config(state='disabled')
        
        def connect_thread():
            try:
                # Configuration du timeout
                self.keithley.timeout = self.timeout_var.get()
                
                # Connexion
                self.keithley.connect(resource)
                
                # Lecture de l'identification
                idn = self.keithley.get_id()
                
                # Mise à jour de l'interface
                self.frame.after(0, lambda: self.connection_success(idn))
                
            except Exception as e:
                self.frame.after(0, lambda: self.connection_failed(str(e)))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def connection_success(self, idn):
        """Gestion de la connexion réussie"""
        self.update_status(f"Connecté: {self.resource_var.get()}", "green")
        self.add_info(f"\n✓ Connexion établie!")
        self.add_info(f"Identification: {idn}")
        
        # Mise à jour des boutons
        self.connect_btn.config(state='disabled')
        self.disconnect_btn.config(state='normal')
        self.test_btn.config(state='normal')
        self.resource_combo.config(state='disabled')
        
        messagebox.showinfo("Succès", f"Connexion établie avec:\n{idn}")
    
    def connection_failed(self, error_msg):
        """Gestion de l'échec de connexion"""
        self.update_status("Échec de connexion", "red")
        self.add_info(f"\n✗ Échec de connexion: {error_msg}")
        self.connect_btn.config(state='normal')
        messagebox.showerror("Erreur", f"Impossible de se connecter:\n{error_msg}")
    
    def disconnect_instrument(self):
        """Déconnecte l'instrument"""
        try:
            self.keithley.disconnect()
            self.update_status("Déconnecté", "red")
            self.add_info("\n✓ Instrument déconnecté")
            
            # Mise à jour des boutons
            self.connect_btn.config(state='normal')
            self.disconnect_btn.config(state='disabled')
            self.test_btn.config(state='disabled')
            self.resource_combo.config(state='readonly')
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la déconnexion:\n{e}")
    
    def test_connection(self):
        """Test la connexion avec l'instrument"""
        if not self.keithley.connected:
            messagebox.showwarning("Attention", "Aucun instrument connecté")
            return
        
        try:
            # Test simple
            idn = self.keithley.get_id()
            error = self.keithley.get_error()
            
            self.add_info(f"\n✓ Test de connexion réussi")
            self.add_info(f"IDN: {idn}")
            self.add_info(f"Erreurs: {error}")
            
            messagebox.showinfo("Test", f"Connexion OK!\n\n{idn}\n\nErreurs: {error}")
            
        except Exception as e:
            self.add_info(f"\n✗ Échec du test: {e}")
            messagebox.showerror("Erreur", f"Test échoué:\n{e}")
    
    def add_info(self, text):
        """Ajoute du texte dans la zone d'information"""
        self.info_text.config(state='normal')
        self.info_text.insert('end', text + '\n')
        self.info_text.see('end')
        self.info_text.config(state='disabled')
