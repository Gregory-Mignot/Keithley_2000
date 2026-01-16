# 📦 Installation Offline - Keithley 2000 Controller

Guide complet pour installer le programme **sans connexion Internet**.

---

## 🎯 Vue d'ensemble

Le programme peut fonctionner **complètement hors ligne** en préparant un package contenant :
- ✅ Python portable (optionnel)
- ✅ Toutes les dépendances Python (.whl)
- ✅ Le programme complet

## 📁 Structure du package offline

```
Keithley2000_Controller/
│
├── main.py, keithley2000.py, etc.     ← Programme
├── gui/                                ← Interface
├── launch.bat                          ← Lanceur intelligent
├── requirements.txt                    ← Liste dépendances
│
└── Requirements/                       ← PACKAGE OFFLINE
    ├── README.txt                      ← Instructions
    ├── wheels/                         ← Packages Python (.whl)
    │   ├── pyvisa-1.13.0-py3-none-any.whl
    │   ├── matplotlib-3.7.0-cp311-cp311-win_amd64.whl
    │   ├── numpy-1.24.0-cp311-cp311-win_amd64.whl
    │   └── ... (tous les .whl)
    │
    └── python/                         ← Python portable (optionnel)
        ├── python.exe
        ├── python311.dll
        └── ... (Python embeddable)
```

---

## 🚀 MÉTHODE 1 : Préparation automatique

### Sur une machine **AVEC Internet** :

1. **Téléchargez** tous les fichiers du projet

2. **Exécutez** le script de préparation :
   ```bash
   prepare_offline_install.bat
   ```

3. **Ce script va automatiquement :**
   - ✅ Créer la structure `Requirements/`
   - ✅ Télécharger tous les packages Python dans `Requirements/wheels/`
   - ✅ Créer un README avec instructions

4. **(Optionnel) Ajoutez Python portable :**
   - Téléchargez Python embeddable : https://www.python.org/downloads/windows/
   - Cherchez "**Windows embeddable package (64-bit)**"
   - Téléchargez `python-3.11.x-embed-amd64.zip`
   - Extrayez dans `Requirements/python/`

5. **Copiez tout le dossier** sur une clé USB ou réseau

### Sur la machine **SANS Internet** (cible) :

1. **Copiez** le dossier complet
2. **Clic droit** sur `launch.bat` → **Exécuter en tant qu'administrateur**
3. **Le script détectera automatiquement** les ressources locales
4. **Installation sans Internet !** ✨

---

## 🔧 MÉTHODE 2 : Préparation manuelle

### Étape 1 : Télécharger les wheels Python

```bash
# Créer le dossier
mkdir Requirements\wheels

# Télécharger tous les packages
pip download -r requirements.txt -d Requirements\wheels
```

**Résultat :** Tous les `.whl` dans `Requirements/wheels/`

### Étape 2 : Python portable (optionnel)

#### Option A : Python embeddable (recommandé - ~15 MB)

1. Allez sur : https://www.python.org/downloads/windows/
2. Cherchez la version souhaitée (ex: Python 3.11.8)
3. Téléchargez : **Windows embeddable package (64-bit)**
   - Fichier : `python-3.11.8-embed-amd64.zip`
4. Extrayez dans `Requirements/python/`

**Structure finale :**
```
Requirements/
└── python/
    ├── python.exe
    ├── python311.dll
    ├── python311.zip
    └── ...
```

#### Option B : Python installé complet (~100 MB)

1. Téléchargez l'installeur Python
2. Installez dans un dossier temporaire
3. Copiez tout le dossier dans `Requirements/python/`

### Étape 3 : Vérification

Votre structure doit ressembler à :
```
Requirements/
├── wheels/
│   ├── pyvisa-1.13.0-py3-none-any.whl
│   ├── matplotlib-3.7.0-...whl
│   └── ... (~15-20 fichiers .whl)
│
└── python/          (optionnel)
    └── python.exe
```

### Étape 4 : Tester localement

```bash
# Installation depuis les wheels locales
pip install --no-index --find-links=Requirements/wheels -r requirements.txt

# Vérifier
python check_installation.py
```

### Étape 5 : Créer le package

1. **Copiez** tout le dossier `Keithley2000_Controller/`
2. **Incluez** le dossier `Requirements/` complet
3. **Compressez** (ZIP) si nécessaire pour transfert

**Taille typique :**
- Sans Python : ~50 MB
- Avec Python : ~65 MB

---

## 🎮 Utilisation sur machine cible

### Scénario 1 : Python système déjà installé

```
launch.bat détectera Python système
→ Installera depuis Requirements/wheels/
→ Lancera le programme
```

### Scénario 2 : Python portable fourni

```
launch.bat détectera Python dans Requirements/python/
→ Utilisera cette version
→ Installera depuis Requirements/wheels/
→ Lancera le programme
```

### Scénario 3 : Aucun Python

```
launch.bat proposera:
1. Installer depuis Requirements/python/ (si présent)
2. Télécharger Python (nécessite Internet)
3. Annuler
```

---

## 📋 Checklist de préparation

### Sur machine avec Internet :

- [ ] Projet complet téléchargé
- [ ] `prepare_offline_install.bat` exécuté
- [ ] Dossier `Requirements/wheels/` contient ~15-20 fichiers .whl
- [ ] (Optionnel) Python embeddable dans `Requirements/python/`
- [ ] Tout le dossier copié sur support de transfert

### Sur machine sans Internet :

- [ ] Dossier complet copié
- [ ] Drivers Keysight IO Libraries installés (installer séparément)
- [ ] `launch.bat` lancé en administrateur
- [ ] Programme fonctionne !

---

## 🔍 Vérification des packages téléchargés

Pour vérifier que tous les packages sont présents :

```bash
# Lister les wheels
dir Requirements\wheels\*.whl

# Devrait montrer environ:
# - pyvisa-*.whl
# - pyvisa_py-*.whl
# - matplotlib-*.whl
# - numpy-*.whl
# - pandas-*.whl
# - pillow-*.whl (dépendance matplotlib)
# - contourpy-*.whl (dépendance matplotlib)
# - cycler-*.whl (dépendance matplotlib)
# - fonttools-*.whl (dépendance matplotlib)
# - kiwisolver-*.whl (dépendance matplotlib)
# - packaging-*.whl (dépendance matplotlib)
# - pyparsing-*.whl (dépendance matplotlib)
# - python_dateutil-*.whl (dépendance matplotlib)
# - pytz-*.whl (dépendance pandas)
# - six-*.whl (dépendances diverses)
# + quelques autres dépendances
```

---

## ⚠️ Important : Drivers GPIB

Les **drivers Keysight/Agilent** ne peuvent **PAS** être inclus dans le package et doivent être **installés séparément** sur chaque machine :

### Installation des drivers :

1. **Téléchargez** Keysight IO Libraries Suite (sur une machine avec Internet)
   - https://www.keysight.com/
   - Cherchez "IO Libraries Suite"
   - Téléchargez l'installeur (~500 MB)

2. **Copiez** l'installeur sur la machine cible

3. **Installez** en administrateur

4. **Redémarrez** la machine

5. **Vérifiez** avec Keysight Connection Expert

---

## 💾 Tailles des fichiers

| Composant | Taille approximative |
|-----------|---------------------|
| Programme Python | ~500 KB |
| Wheels (dépendances) | ~45 MB |
| Python embeddable | ~15 MB |
| **TOTAL OFFLINE** | **~60 MB** |
| Drivers GPIB (séparés) | ~500 MB |

---

## 🐛 Dépannage

### "Module not found" même avec wheels

**Cause :** Installation incomplète

**Solution :**
```bash
# Forcer réinstallation
pip install --no-index --find-links=Requirements/wheels --force-reinstall -r requirements.txt
```

### Python portable ne démarre pas

**Cause :** Fichiers manquants dans Python embeddable

**Solution :**
1. Vérifiez que `python.exe` existe
2. Vérifiez que `python3xx.dll` existe
3. Retéléchargez le package embeddable complet

### "pip not found" avec Python embeddable

**Cause :** pip n'est pas inclus par défaut

**Solution :**
```bash
# Télécharger get-pip.py (sur machine avec Internet)
# Puis exécuter:
Requirements\python\python.exe get-pip.py
```

### Installation échoue sur packages C/C++

**Cause :** Certains packages (numpy, pandas) nécessitent compilation

**Solution :** Téléchargez les **wheels précompilés** pour Windows :
- https://www.lfd.uci.edu/~gohlke/pythonlibs/
- Cherchez la version correspondant à votre Python (cp311 = Python 3.11)
- Architecture : win_amd64 (64-bit)

---

## 🎓 Cas d'usage typiques

### 1. Installation en laboratoire isolé

```
Machine prep (Internet) → USB → Machine labo (isolée)
   prepare_offline         copie    launch.bat (admin)
                                        ↓
                                    Installation OK
```

### 2. Déploiement multi-postes

```
1 préparation → Plusieurs installations identiques
prepare_offline   copie × N    launch.bat × N
```

### 3. Archivage long terme

```
Package complet 2025 → Archive → Réinstallation 2030
Tout fonctionne sans modification !
```

---

## ✅ Avantages de cette approche

✅ **Autonomie totale** - Aucune connexion Internet requise  
✅ **Portable** - Clé USB, réseau local, archive  
✅ **Reproductible** - Versions exactes des dépendances  
✅ **Rapide** - Installation en quelques secondes  
✅ **Sûr** - Pas de téléchargements non vérifiés  
✅ **Archivable** - Package complet pour le futur  

---

## 📞 Support

En cas de problème :

1. Vérifiez `Requirements/README.txt`
2. Exécutez `python check_installation.py`
3. Consultez les logs dans la console
4. Vérifiez la structure des dossiers

---

**🎉 Avec cette méthode, votre installation est 100% autonome et reproductible !**
