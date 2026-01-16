# 🚀 Guide d'Installation Rapide

## Étape 1️⃣ : Installer les drivers GPIB Agilent

### Téléchargement
1. Allez sur : https://www.keysight.com/
2. Cherchez "IO Libraries Suite"
3. Téléchargez la dernière version pour Windows
4. Exécutez l'installeur **en administrateur**

### Vérification
Après installation, lancez **Keysight Connection Expert** :
- Menu Démarrer → Keysight → Connection Expert
- Vous devriez voir votre carte GPIB PCI
- Si l'instrument est connecté et allumé, il devrait être détecté

⚠️ **Redémarrez l'ordinateur** après installation des drivers

---

## Étape 2️⃣ : Installer Python

### Téléchargement
1. Allez sur : https://www.python.org/downloads/
2. Téléchargez Python 3.11 ou 3.12 (recommandé)
3. Lancez l'installeur

### Installation
✅ **IMPORTANT** : Cochez **"Add Python to PATH"**

![Python Install](https://i.imgur.com/XJqPW0M.png)

Puis cliquez sur "Install Now"

### Vérification
Ouvrez un terminal (cmd) et tapez :
```bash
python --version
```

Vous devriez voir : `Python 3.11.x` (ou similaire)

---

## Étape 3️⃣ : Télécharger le programme

Téléchargez tous les fichiers du programme dans un dossier, par exemple :
```
C:\Users\VotreNom\Documents\Keithley2000\
```

Structure du dossier :
```
Keithley2000/
├── main.py
├── keithley2000.py
├── requirements.txt
├── launch.bat
├── check_installation.py
├── README.md
├── INSTALL.md
└── gui/
    ├── __init__.py
    ├── main_window.py
    ├── settings_tab.py
    ├── quick_measure_tab.py
    └── advanced_tab.py
```

---

## Étape 4️⃣ : Installer les dépendances Python

### Méthode automatique (recommandée)

1. Ouvrez le dossier du programme
2. **Clic droit** sur `launch.bat`
3. **Exécuter en tant qu'administrateur**

Le script installera automatiquement toutes les dépendances.

### Méthode manuelle

Ouvrez un terminal **en administrateur** :
- Windows 10/11 : Clic droit sur l'icône Windows → Terminal (admin)
- Windows 7/8 : Chercher "cmd" → Clic droit → Exécuter en tant qu'administrateur

Naviguez vers le dossier :
```bash
cd C:\Users\VotreNom\Documents\Keithley2000
```

Installez les dépendances :
```bash
pip install -r requirements.txt
```

Attendez la fin de l'installation (peut prendre 2-5 minutes).

---

## Étape 5️⃣ : Vérifier l'installation

Dans le dossier du programme, **double-cliquez** sur :
```
check_installation.py
```

Ou en ligne de commande :
```bash
python check_installation.py
```

Ce script vérifie :
- ✅ Version de Python
- ✅ Modules installés
- ✅ PyVISA et backend
- ✅ Détection des instruments GPIB
- ✅ Interface graphique
- ✅ Privilèges administrateur

**Exemple de résultat attendu :**
```
✓ Python 3.11.5
✓ tkinter         - Interface graphique
✓ pyvisa          - Communication VISA
✓ matplotlib      - Graphiques
✓ numpy           - Calculs numériques
✓ pandas          - Gestion de données
✓ Backend VISA: Keysight VISA
✓ 2 ressource(s) VISA détectée(s):
  • GPIB0::16::INSTR
  • ASRL1::INSTR
```

---

## Étape 6️⃣ : Lancer le programme

### Méthode 1 : Fichier batch (recommandé)

**Clic droit** sur `launch.bat` → **Exécuter en tant qu'administrateur**

### Méthode 2 : Ligne de commande

Terminal **en administrateur** :
```bash
cd C:\Users\VotreNom\Documents\Keithley2000
python main.py
```

### Méthode 3 : Créer un raccourci

1. Clic droit sur `launch.bat` → Créer un raccourci
2. Clic droit sur le raccourci → Propriétés
3. Onglet "Raccourci" → Avancé
4. ✅ Cocher "Exécuter en tant qu'administrateur"
5. OK → OK
6. Placez le raccourci sur le Bureau

---

## Premier démarrage ✨

### 1. Onglet Settings

![Settings Tab](https://via.placeholder.com/800x400?text=Settings+Tab)

1. Cliquez sur **"🔍 Scan"**
2. Sélectionnez votre Keithley 2000 (ex: `GPIB0::16::INSTR`)
3. Cliquez sur **"🔌 Connect"**
4. Message de succès : "Connexion établie avec: KEITHLEY..."

### 2. Onglet Quick Measure

![Quick Measure Tab](https://via.placeholder.com/800x400?text=Quick+Measure+Tab)

1. Choisissez **Type de Mesure** (ex: DCV)
2. Configurez les paramètres (plage AUTO, NPLC 1)
3. Réglez l'**Intervalle** (ex: 0.1s)
4. Cliquez sur **"▶ Start"**
5. Observez le graphique en temps réel !

### 3. Arrêt de la mesure

- **⏸ Pause** : Met en pause
- **⏹ Stop** : Arrête définitivement
- **💾 Export CSV** : Sauvegarde les données

---

## 🔧 Dépannage

### ❌ "Aucune ressource VISA détectée"

**Causes possibles :**
1. Drivers Keysight non installés → Installer depuis keysight.com
2. Carte GPIB non détectée → Vérifier le Gestionnaire de périphériques
3. Instrument éteint → Allumer le Keithley 2000
4. Câble GPIB défectueux → Vérifier les connexions

**Solution :**
1. Ouvrir **Keysight Connection Expert**
2. Vérifier que la carte GPIB apparaît
3. Scanner les instruments
4. Noter l'adresse GPIB trouvée

### ❌ "Module 'pyvisa' not found"

**Cause :** Dépendances non installées

**Solution :**
```bash
pip install -r requirements.txt
```

### ❌ "Permission denied" ou "Access denied"

**Cause :** Pas lancé en administrateur

**Solution :**
- Clic droit sur `launch.bat`
- **Exécuter en tant qu'administrateur**

### ❌ Mesures très lentes

**Optimisations :**
1. ✅ Cocher **"Mode Fast"**
2. Réduire **NPLC** → 0.1 ou 0.01
3. Désactiver **Filtre numérique**
4. Onglet Advanced : Désactiver l'affichage instrument

### ❌ Graphique qui lag

**Cause :** Trop de points affichés

**Solution :**
1. Augmenter l'**Intervalle** (ex: 0.5s au lieu de 0.1s)
2. Utiliser **"🗑 Clear"** régulièrement
3. Désactiver **Autoscale** si zoom manuel suffisant

---

## 📞 Support

### Vérifications avant de demander de l'aide

1. ✅ Lancé **en administrateur** ?
2. ✅ Script `check_installation.py` OK ?
3. ✅ **Keysight Connection Expert** détecte l'instrument ?
4. ✅ Instrument allumé et câble connecté ?

### Ressources utiles

- **Manuel Keithley 2000** : https://www.tek.com/en/support
- **PyVISA Docs** : https://pyvisa.readthedocs.io/
- **Keysight Support** : https://www.keysight.com/us/en/support.html

---

## ✅ Checklist complète

- [ ] Drivers Keysight installés
- [ ] Python 3.8+ installé (PATH configuré)
- [ ] Dépendances pip installées
- [ ] check_installation.py OK
- [ ] Keysight Connection Expert détecte l'instrument
- [ ] Programme lancé en administrateur
- [ ] Connexion établie dans Settings
- [ ] Première mesure réussie !

---

🎉 **Félicitations ! Vous êtes prêt à utiliser le Keithley 2000 Controller !**
