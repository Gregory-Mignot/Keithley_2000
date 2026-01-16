"""
Onglet Advanced Control - Contrôles avancés et commandes SCPI
"""
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os

class AdvancedTab:
    """Onglet de contrôle avancé"""
    
    def __init__(self, parent, keithley, update_status_callback):
        self.keithley = keithley
        self.update_status = update_status_callback
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        
        # Historique des commandes
        self.command_history = []
        self.history_index = -1
    
    def create_widgets(self):
        """Crée les widgets de l'onglet"""
        
        # Frame principal avec 2 colonnes
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Colonne gauche: Contrôles avancés
        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side='left', fill='both', expand=False, padx=5)
        
        # Colonne droite: Commandes SCPI
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # === CONTRÔLES AVANCÉS ===
        self.create_advanced_controls(left_frame)
        
        # === COMMANDES SCPI ===
        self.create_scpi_section(right_frame)
    
    def create_advanced_controls(self, parent):
        """Crée la section des contrôles avancés"""
        
        # Trigger
        trigger_frame = ttk.LabelFrame(parent, text="Configuration Trigger", padding=10)
        trigger_frame.pack(fill='x', pady=5)
        
        ttk.Label(trigger_frame, text="Source:").pack(anchor='w')
        
        self.trigger_var = tk.StringVar(value='IMM')
        
        triggers = [
            ('Immédiat', 'IMM'),
            ('Bus', 'BUS'),
            ('Externe', 'EXT'),
            ('Timer', 'TIM')
        ]
        
        for text, value in triggers:
            rb = ttk.Radiobutton(trigger_frame, text=text, 
                                variable=self.trigger_var, value=value,
                                command=self.apply_trigger)
            rb.pack(anchor='w', pady=2)
        
        # Affichage
        display_frame = ttk.LabelFrame(parent, text="Affichage", padding=10)
        display_frame.pack(fill='x', pady=5)
        
        self.display_var = tk.BooleanVar(value=True)
        display_cb = ttk.Checkbutton(display_frame, text="Affichage instrument activé",
                                     variable=self.display_var,
                                     command=self.toggle_display)
        display_cb.pack(anchor='w', pady=2)
        
        ttk.Label(display_frame, text="Note: Désactiver l'affichage\npeut accélérer les mesures",
                 font=('Arial', 8, 'italic')).pack(anchor='w', pady=5)
        
        # Math Functions
        math_frame = ttk.LabelFrame(parent, text="Fonctions Mathématiques", padding=10)
        math_frame.pack(fill='x', pady=5)
        
        ttk.Label(math_frame, text="NULL (offset):").pack(anchor='w')
        
        null_control_frame = ttk.Frame(math_frame)
        null_control_frame.pack(fill='x', pady=2)
        
        self.null_var = tk.BooleanVar(value=False)
        null_cb = ttk.Checkbutton(null_control_frame, text="Actif",
                                  variable=self.null_var)
        null_cb.pack(side='left')
        
        ttk.Button(null_control_frame, text="Acquérir NULL",
                  command=self.acquire_null).pack(side='left', padx=5)
        
        # Buffer
        buffer_frame = ttk.LabelFrame(parent, text="Buffer d'acquisition", padding=10)
        buffer_frame.pack(fill='x', pady=5)
        
        ttk.Label(buffer_frame, text="Taille du buffer:").pack(anchor='w')
        
        self.buffer_size_var = tk.IntVar(value=1)
        buffer_spin = ttk.Spinbox(buffer_frame, from_=1, to=2000,
                                  textvariable=self.buffer_size_var, width=15)
        buffer_spin.pack(fill='x', pady=2)
        
        ttk.Button(buffer_frame, text="Configurer Buffer",
                  command=self.configure_buffer).pack(fill='x', pady=5)
        
        # Utilitaires
        util_frame = ttk.LabelFrame(parent, text="Utilitaires", padding=10)
        util_frame.pack(fill='x', pady=5)
        
        ttk.Button(util_frame, text="🔄 Reset Instrument",
                  command=self.reset_instrument).pack(fill='x', pady=2)
        
        ttk.Button(util_frame, text="🔊 Beep",
                  command=self.beep_instrument).pack(fill='x', pady=2)
        
        ttk.Button(util_frame, text="🗑️ Clear Errors",
                  command=self.clear_errors).pack(fill='x', pady=2)
        
        ttk.Button(util_frame, text="🔍 Check Errors",
                  command=self.check_errors).pack(fill='x', pady=2)
    
    def create_scpi_section(self, parent):
        """Crée la section des commandes SCPI"""
        
        # Titre et lien documentation
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=5)
        
        ttk.Label(header_frame, text="Commandes SCPI Directes",
                 font=('Arial', 12, 'bold')).pack(side='left')
        
        ttk.Button(header_frame, text="📖 Documentation SCPI",
                  command=self.open_scpi_doc).pack(side='right', padx=5)
        
        # Zone de saisie de commande
        cmd_frame = ttk.LabelFrame(parent, text="Envoyer une commande", padding=10)
        cmd_frame.pack(fill='x', pady=5)
        
        # Entrée commande
        entry_frame = ttk.Frame(cmd_frame)
        entry_frame.pack(fill='x', pady=5)
        
        ttk.Label(entry_frame, text="Commande:").pack(side='left', padx=5)
        
        self.scpi_entry = ttk.Entry(entry_frame, font=('Courier', 10))
        self.scpi_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.scpi_entry.bind('<Return>', lambda e: self.send_scpi_command())
        self.scpi_entry.bind('<Up>', self.history_up)
        self.scpi_entry.bind('<Down>', self.history_down)
        
        # Boutons
        btn_frame = ttk.Frame(cmd_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="▶ Send (Write)",
                  command=self.send_scpi_command).pack(side='left', padx=2)
        
        ttk.Button(btn_frame, text="❓ Query (Write+Read)",
                  command=self.query_scpi_command).pack(side='left', padx=2)
        
        ttk.Button(btn_frame, text="🗑 Clear",
                  command=self.clear_response).pack(side='left', padx=2)
        
        # Zone de réponse
        response_frame = ttk.LabelFrame(parent, text="Réponse", padding=10)
        response_frame.pack(fill='both', expand=True, pady=5)
        
        # Texte avec scrollbar
        text_frame = ttk.Frame(response_frame)
        text_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.response_text = tk.Text(text_frame, font=('Courier', 10),
                                     yscrollcommand=scrollbar.set)
        self.response_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.response_text.yview)
        
        # Commandes rapides
        quick_frame = ttk.LabelFrame(parent, text="Commandes Rapides", padding=10)
        quick_frame.pack(fill='x', pady=5)
        
        quick_commands = [
            ("*IDN?", "Identification"),
            ("SYST:ERR?", "Vérifier erreurs"),
            ("READ?", "Lecture simple"),
            ("FETC?", "Lecture rapide"),
            ("*RST", "Reset"),
            ("SYST:LOC", "Mode local")
        ]
        
        for i, (cmd, desc) in enumerate(quick_commands):
            btn = ttk.Button(quick_frame, text=f"{desc}\n({cmd})",
                           command=lambda c=cmd: self.quick_command(c))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky='ew')
        
        # Configuration du grid
        for i in range(3):
            quick_frame.columnconfigure(i, weight=1)
        
        # Aide
        help_frame = ttk.LabelFrame(parent, text="Aide", padding=10)
        help_frame.pack(fill='x', pady=5)
        
        help_text = """💡 Astuces:
• Utilisez ↑/↓ pour naviguer dans l'historique
• Write envoie une commande sans attendre de réponse
• Query envoie et attend une réponse
• Les commandes se terminent par ? pour lire une valeur"""
        
        ttk.Label(help_frame, text=help_text, justify='left',
                 font=('Arial', 9)).pack(anchor='w')
    
    def send_scpi_command(self):
        """Envoie une commande SCPI (write)"""
        if not self.keithley.connected:
            messagebox.showerror("Erreur", "Aucun instrument connecté!")
            return
        
        command = self.scpi_entry.get().strip()
        if not command:
            return
        
        try:
            self.keithley.write(command)
            self.add_response(f">>> {command}")
            self.add_response("✓ Commande envoyée\n")
            
            # Ajout à l'historique
            self.add_to_history(command)
            self.scpi_entry.delete(0, 'end')
            
        except Exception as e:
            self.add_response(f"✗ Erreur: {e}\n")
            messagebox.showerror("Erreur", f"Erreur d'envoi:\n{e}")
    
    def query_scpi_command(self):
        """Envoie une commande SCPI et lit la réponse (query)"""
        if not self.keithley.connected:
            messagebox.showerror("Erreur", "Aucun instrument connecté!")
            return
        
        command = self.scpi_entry.get().strip()
        if not command:
            return
        
        try:
            response = self.keithley.query(command)
            self.add_response(f">>> {command}")
            self.add_response(f"<<< {response}\n")
            
            # Ajout à l'historique
            self.add_to_history(command)
            self.scpi_entry.delete(0, 'end')
            
        except Exception as e:
            self.add_response(f"✗ Erreur: {e}\n")
            messagebox.showerror("Erreur", f"Erreur de query:\n{e}")
    
    def quick_command(self, command):
        """Exécute une commande rapide"""
        self.scpi_entry.delete(0, 'end')
        self.scpi_entry.insert(0, command)
        
        if '?' in command:
            self.query_scpi_command()
        else:
            self.send_scpi_command()
    
    def add_response(self, text):
        """Ajoute du texte dans la zone de réponse"""
        self.response_text.insert('end', text + '\n')
        self.response_text.see('end')
    
    def clear_response(self):
        """Efface la zone de réponse"""
        self.response_text.delete('1.0', 'end')
    
    def add_to_history(self, command):
        """Ajoute une commande à l'historique"""
        if command and (not self.command_history or self.command_history[-1] != command):
            self.command_history.append(command)
        self.history_index = len(self.command_history)
    
    def history_up(self, event):
        """Remonte dans l'historique"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.scpi_entry.delete(0, 'end')
            self.scpi_entry.insert(0, self.command_history[self.history_index])
    
    def history_down(self, event):
        """Descend dans l'historique"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.scpi_entry.delete(0, 'end')
            self.scpi_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index >= len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.scpi_entry.delete(0, 'end')
    
    def open_scpi_doc(self):
        """Ouvre la documentation SCPI"""
        # Créer un fichier HTML local avec la doc
        doc_path = self.create_scpi_doc()
        
        try:
            # Ouvrir dans le navigateur
            webbrowser.open(f'file://{os.path.abspath(doc_path)}')
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir la documentation:\n{e}")
    
    def create_scpi_doc(self):
        """Crée un fichier HTML avec la documentation SCPI"""
        doc_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Keithley 2000 - Commandes SCPI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #003366; }
        h2 { color: #0066cc; margin-top: 30px; }
        .command { background: white; padding: 10px; margin: 10px 0; border-left: 4px solid #0066cc; }
        .cmd-name { font-family: 'Courier New', monospace; font-weight: bold; color: #cc0000; }
        .description { margin-top: 5px; }
        .example { background: #f0f0f0; padding: 5px; margin-top: 5px; font-family: 'Courier New', monospace; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; background: white; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #0066cc; color: white; }
    </style>
</head>
<body>
    <h1>📘 Keithley 2000 - Référence des Commandes SCPI</h1>
    
    <h2>🔧 Commandes Système</h2>
    
    <div class="command">
        <div class="cmd-name">*IDN?</div>
        <div class="description">Retourne l'identification de l'instrument</div>
        <div class="example">Exemple: *IDN?<br>Réponse: KEITHLEY INSTRUMENTS INC.,MODEL 2000,...</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">*RST</div>
        <div class="description">Reset de l'instrument aux paramètres par défaut</div>
        <div class="example">Exemple: *RST</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">*CLS</div>
        <div class="description">Efface tous les registres d'erreur et de statut</div>
        <div class="example">Exemple: *CLS</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">SYST:ERR?</div>
        <div class="description">Lit la prochaine erreur dans la file d'attente</div>
        <div class="example">Exemple: SYST:ERR?<br>Réponse: 0,"No error"</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">SYST:LOC</div>
        <div class="description">Place l'instrument en mode local (déverrouille le panneau avant)</div>
        <div class="example">Exemple: SYST:LOC</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">SYST:REM</div>
        <div class="description">Place l'instrument en mode remote (verrouille le panneau avant)</div>
        <div class="example">Exemple: SYST:REM</div>
    </div>
    
    <h2>📊 Configuration de Mesure</h2>
    
    <div class="command">
        <div class="cmd-name">CONF:VOLT:DC [range], [resolution]</div>
        <div class="description">Configure la mesure de tension DC</div>
        <div class="example">Exemple: CONF:VOLT:DC 10, 0.001<br>Configure tension DC, plage 10V, résolution 1mV</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">CONF:VOLT:AC [range], [resolution]</div>
        <div class="description">Configure la mesure de tension AC</div>
        <div class="example">Exemple: CONF:VOLT:AC AUTO</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">CONF:CURR:DC [range], [resolution]</div>
        <div class="description">Configure la mesure de courant DC</div>
        <div class="example">Exemple: CONF:CURR:DC 1, 0.0001</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">CONF:RES [range], [resolution]</div>
        <div class="description">Configure la mesure de résistance 2 fils</div>
        <div class="example">Exemple: CONF:RES AUTO</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">CONF:FRES [range], [resolution]</div>
        <div class="description">Configure la mesure de résistance 4 fils</div>
        <div class="example">Exemple: CONF:FRES 1000</div>
    </div>
    
    <h2>⚙️ Paramètres de Mesure</h2>
    
    <div class="command">
        <div class="cmd-name">[FUNC]:RANG:AUTO ON|OFF</div>
        <div class="description">Active/désactive l'auto-range</div>
        <div class="example">Exemple: VOLT:DC:RANG:AUTO ON</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">[FUNC]:RANG [value]</div>
        <div class="description">Définit la plage de mesure</div>
        <div class="example">Exemple: VOLT:DC:RANG 10<br>Plage fixe de 10V</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">[FUNC]:NPLC [value]</div>
        <div class="description">Définit le temps d'intégration (0.01 à 10 PLC)<br>
        0.01 = rapide mais bruyant, 10 = lent mais précis</div>
        <div class="example">Exemple: VOLT:DC:NPLC 1<br>1 cycle secteur (20ms à 50Hz)</div>
    </div>
    
    <h2>🎯 Déclenchement (Trigger)</h2>
    
    <div class="command">
        <div class="cmd-name">TRIG:SOUR IMM|BUS|EXT|TIM</div>
        <div class="description">Définit la source de déclenchement<br>
        IMM = Immédiat, BUS = Bus GPIB, EXT = Trigger externe, TIM = Timer</div>
        <div class="example">Exemple: TRIG:SOUR IMM</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">INIT</div>
        <div class="description">Déclenche une mesure</div>
        <div class="example">Exemple: INIT</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">*TRG</div>
        <div class="description">Envoie un trigger bus</div>
        <div class="example">Exemple: *TRG</div>
    </div>
    
    <h2>📖 Lecture de Données</h2>
    
    <div class="command">
        <div class="cmd-name">READ?</div>
        <div class="description">Déclenche une mesure et lit le résultat (combinaison INIT + FETCH)</div>
        <div class="example">Exemple: READ?<br>Réponse: +1.234567890E+01</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">FETC?</div>
        <div class="description">Lit la dernière mesure (sans déclencher de nouvelle mesure)</div>
        <div class="example">Exemple: FETC?<br>Plus rapide que READ?</div>
    </div>
    
    <h2>🔢 Filtrage</h2>
    
    <div class="command">
        <div class="cmd-name">AVER:STAT ON|OFF</div>
        <div class="description">Active/désactive le filtre numérique</div>
        <div class="example">Exemple: AVER:STAT ON</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">AVER:COUN [value]</div>
        <div class="description">Définit le nombre de mesures à moyenner (2-100)</div>
        <div class="example">Exemple: AVER:COUN 10</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">AVER:TCON MOV|REP</div>
        <div class="description">Type de filtre: MOV = moyenne mobile, REP = répétitif</div>
        <div class="example">Exemple: AVER:TCON MOV</div>
    </div>
    
    <h2>🖥️ Affichage</h2>
    
    <div class="command">
        <div class="cmd-name">DISP:ENAB ON|OFF</div>
        <div class="description">Active/désactive l'affichage (le désactiver accélère les mesures)</div>
        <div class="example">Exemple: DISP:ENAB OFF</div>
    </div>
    
    <h2>📝 Buffer de Données</h2>
    
    <div class="command">
        <div class="cmd-name">TRAC:CLE</div>
        <div class="description">Efface le buffer de données</div>
        <div class="example">Exemple: TRAC:CLE</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">TRAC:POIN [count]</div>
        <div class="description">Définit la taille du buffer (1-2000)</div>
        <div class="example">Exemple: TRAC:POIN 100</div>
    </div>
    
    <div class="command">
        <div class="cmd-name">TRAC:DATA?</div>
        <div class="description">Lit toutes les données du buffer</div>
        <div class="example">Exemple: TRAC:DATA?</div>
    </div>
    
    <h2>🔔 Utilitaires</h2>
    
    <div class="command">
        <div class="cmd-name">SYST:BEEP [freq], [time]</div>
        <div class="description">Émet un bip (fréquence en Hz, durée en secondes)</div>
        <div class="example">Exemple: SYST:BEEP 1000, 0.5<br>Bip de 1kHz pendant 0.5s</div>
    </div>
    
    <h2>📊 Tableaux de Référence</h2>
    
    <h3>Plages de Mesure</h3>
    <table>
        <tr><th>Fonction</th><th>Plages Disponibles</th></tr>
        <tr><td>Tension DC</td><td>100mV, 1V, 10V, 100V, 1000V</td></tr>
        <tr><td>Tension AC</td><td>100mV, 1V, 10V, 100V, 750V</td></tr>
        <tr><td>Courant DC</td><td>10µA, 100µA, 1mA, 10mA, 100mA, 1A, 3A</td></tr>
        <tr><td>Courant AC</td><td>100µA, 1mA, 10mA, 100mA, 1A, 3A</td></tr>
        <tr><td>Résistance</td><td>100Ω, 1kΩ, 10kΩ, 100kΩ, 1MΩ, 10MΩ, 100MΩ</td></tr>
    </table>
    
    <h3>Valeurs NPLC Recommandées</h3>
    <table>
        <tr><th>NPLC</th><th>Temps (50Hz)</th><th>Usage</th></tr>
        <tr><td>0.01</td><td>0.2ms</td><td>Mesures très rapides, bruyantes</td></tr>
        <tr><td>0.1</td><td>2ms</td><td>Mesures rapides</td></tr>
        <tr><td>1</td><td>20ms</td><td>Standard (bon compromis)</td></tr>
        <tr><td>5</td><td>100ms</td><td>Mesures précises</td></tr>
        <tr><td>10</td><td>200ms</td><td>Mesures très précises</td></tr>
    </table>
    
    <h2>💡 Exemples de Séquences</h2>
    
    <div class="command">
        <div class="cmd-name">Mesure rapide de tension DC</div>
        <div class="example">
*RST<br>
CONF:VOLT:DC 10<br>
VOLT:DC:NPLC 0.1<br>
DISP:ENAB OFF<br>
READ?
        </div>
    </div>
    
    <div class="command">
        <div class="cmd-name">Mesure précise de résistance 4 fils</div>
        <div class="example">
*RST<br>
CONF:FRES AUTO<br>
FRES:NPLC 10<br>
AVER:STAT ON<br>
AVER:COUN 10<br>
READ?
        </div>
    </div>
    
</body>
</html>"""
        
        # Sauvegarder dans un fichier temporaire
        doc_path = "keithley_2000_scpi_reference.html"
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        return doc_path
    
    # === Fonctions des contrôles avancés ===
    
    def apply_trigger(self):
        """Applique la configuration du trigger"""
        if not self.keithley.connected:
            messagebox.showwarning("Attention", "Aucun instrument connecté")
            return
        
        try:
            source = self.trigger_var.get()
            self.keithley.set_trigger_source(source)
            self.update_status(f"Trigger: {source}", "green")
            messagebox.showinfo("Succès", f"Trigger configuré: {source}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de configuration:\n{e}")
    
    def toggle_display(self):
        """Active/désactive l'affichage"""
        if not self.keithley.connected:
            messagebox.showwarning("Attention", "Aucun instrument connecté")
            return
        
        try:
            state = self.display_var.get()
            self.keithley.set_display(state)
            status = "activé" if state else "désactivé"
            self.update_status(f"Affichage {status}", "green")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur:\n{e}")
    
    def acquire_null(self):
        """Acquiert la valeur NULL actuelle"""
        if not self.keithley.connected:
            messagebox.showwarning("Attention", "Aucun instrument connecté")
            return
        
        try:
            # Lecture de la valeur actuelle
            value = self.keithley.measure_single()
            
            # Configuration du NULL
            self.keithley.write(f'CALC:NULL:OFFS {value}')
            self.keithley.write('CALC:NULL:STAT ON')
            
            messagebox.showinfo("Succès", f"NULL acquis: {value:.6g}\nLes mesures suivantes seront relatives à cette valeur")
            self.null_var.set(True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'acquisition NULL:\n{e}")
    
    def configure_buffer(self):
        """Configure le buffer d'acquisition"""
        if not self.keithley.connected:
            messagebox.showwarning("Attention", "Aucun instrument connecté")
            return
        
        try:
            size = self.buffer_size_var.get()
            self.keithley.write('TRAC:CLE')
            self.keithley.write(f'TRAC:POIN {size}')
            messagebox.showinfo("Succès", f"Buffer configuré: {size} points")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de configuration:\n{e}")
    
    def reset_instrument(self):
        """Reset l'instrument"""
        if not self.keithley.connected:
            messagebox.showwarning("Attention", "Aucun instrument connecté")
            return
        
        response = messagebox.askyesno("Confirmation", 
                                       "Réinitialiser l'instrument aux paramètres par défaut ?")
        if response:
            try:
                self.keithley.reset()
                messagebox.showinfo("Succès", "Instrument réinitialisé")
                self.update_status("Instrument réinitialisé", "green")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de reset:\n{e}")
    
    def beep_instrument(self):
        """Émet un bip"""
        if not self.keithley.connected:
            messagebox.showwarning("Attention", "Aucun instrument connecté")
            return
        
        try:
            self.keithley.beep()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur:\n{e}")
    
    def clear_errors(self):
        """Efface les erreurs"""
        if not self.keithley.connected:
            messagebox.showwarning("Attention", "Aucun instrument connecté")
            return
        
        try:
            self.keithley.clear_errors()
            messagebox.showinfo("Succès", "Erreurs effacées")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur:\n{e}")
    
    def check_errors(self):
        """Vérifie les erreurs"""
        if not self.keithley.connected:
            messagebox.showwarning("Attention", "Aucun instrument connecté")
            return
        
        try:
            errors = []
            # Lire toutes les erreurs
            for _ in range(20):  # Max 20 erreurs
                error = self.keithley.get_error()
                if "No error" in error or error.startswith("0,"):
                    break
                errors.append(error)
            
            if errors:
                error_msg = "\n".join(errors)
                messagebox.showwarning("Erreurs détectées", f"Erreurs:\n{error_msg}")
            else:
                messagebox.showinfo("Succès", "Aucune erreur détectée")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de vérification:\n{e}")