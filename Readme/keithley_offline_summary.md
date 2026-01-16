# 🎉 Installation Offline Automatique - Mode d'emploi Simple

## 🚀 En bref

Le programme peut maintenant **s'installer complètement sans Internet** grâce au système `Requirements/`.

---

## 📦 Nouveaux fichiers créés

| Fichier | Description |
|---------|-------------|
| `launch.bat` (amélioré) | Détecte et installe tout automatiquement |
| `prepare_offline_install.bat` | Prépare le package offline |
| `download_python_portable.bat` | Télécharge Python embeddable |
| `OFFLINE_INSTALL.md` | Guide complet |

---

## 🎯 Méthode ultra-simple

### Sur machine **AVEC Internet** (1 fois) :

```bash
1. Double-cliquez sur: prepare_offline_install.bat
2. (Optionnel) Double-cliquez sur: download_python_portable.bat
3. Copiez tout le dossier sur clé USB
```

### Sur machine **SANS Internet** (autant de fois que nécessaire) :

```bash
1. Copiez le dossier
2. Clic droit sur launch.bat → Exécuter en admin
3. Le programme s'installe et démarre automatiquement !
```

**C'est tout ! ✨**

---

## 🗂️ Structure du dossier Requirements/

```
Requirements/
│
├── wheels/                          ← Packages Python (.whl)
│   ├── pyvisa-1.13.0-py3-none-any.whl
│   ├── matplotlib-3.7.0-...whl
│   ├── numpy-1.24.0-...whl
│   └── ... (~15-20 fichiers)
│
└── python/                          ← Python portable (optionnel)
    ├── python.exe
    ├── python311.dll
    └── ...
```

---

## 💡 Comment ça marche ?

### `launch.bat` détecte automatiquement :

1. **Python système** installé ?
   - ✅ Oui → Utilise celui-ci
   - ❌ Non → Cherche Python portable

2. **Python portable** dans `Requirements/python/` ?
   - ✅ Oui → Utilise celui-ci
   - ❌ Non → Propose de télécharger

3. **Dépendances** installées ?
   - ✅ Oui → Lance le programme
   - ❌ Non → Installe depuis `Requirements/wheels/`

4. **Drivers GPIB** installés ?
   - ✅ Oui → Tout est prêt !
   - ❌ Non → Avertit l'utilisateur

**Tout est automatique, intelligent, et sans effort !**

---

## 📋 3 scénarios d'utilisation

### Scénario 1 : Laboratoire avec Internet (normal)

```
1. Clic droit launch.bat → Exécuter en admin
2. Le script installe depuis Internet
3. Programme démarre
```

**Pas de préparation nécessaire** - Comme avant !

---

### Scénario 2 : Laboratoire isolé (sans Internet)

**Préparation** (1 fois sur machine avec Internet) :
```bash
prepare_offline_install.bat        # Télécharge tout
download_python_portable.bat       # Télécharge Python (optionnel)
→ Copier sur clé USB
```

**Sur chaque poste isolé** :
```bash
Copier dossier → launch.bat (admin) → Installation automatique !
```

---

### Scénario 3 : Déploiement multi-postes

**Préparation** :
```bash
prepare_offline_install.bat
download_python_portable.bat
→ Partager sur réseau/serveur
```

**Installation** :
```
Chaque utilisateur copie et lance launch.bat
Installations identiques et reproductibles !
```

---

## 🎮 Commandes pratiques

### Télécharger tout pour installation offline :
```bash
prepare_offline_install.bat
```

### Télécharger Python portable :
```bash
download_python_portable.bat
```

### Installer depuis packages locaux (manuel) :
```bash
pip install --no-index --find-links=Requirements/wheels -r requirements.txt
```

### Vérifier l'installation :
```bash
python check_installation.py
```

---

## 📊 Avantages

| Avant | Maintenant |
|-------|------------|
| Installation Internet obligatoire | ✅ Installation offline possible |
| Python système requis | ✅ Python portable inclus (optionnel) |
| Dépendances téléchargées à chaque fois | ✅ Dépendances pré-téléchargées |
| Installation lente (~5 min) | ✅ Installation rapide (~30 sec) |
| Versions variables | ✅ Versions fixes et reproductibles |
| - | ✅ Archivage long terme |

---

## ⚠️ Ce qui doit TOUJOURS être installé séparément

### Drivers GPIB Keysight/Agilent

**Pourquoi séparément ?**
- Taille énorme (~500 MB)
- Nécessite privilèges système
- Drivers matériels spécifiques

**Installation :**
1. Téléchargez sur : https://www.keysight.com/
2. Cherchez : "IO Libraries Suite"
3. Installez en administrateur
4. Redémarrez

---

## 🔍 Vérification du package offline

```bash
# Doit contenir environ 15-20 fichiers .whl
dir Requirements\wheels\*.whl

# Vérifier Python portable (optionnel)
Requirements\python\python.exe --version
```

---

## 💾 Tailles

| Élément | Taille |
|---------|--------|
| Programme seul | 500 KB |
| Wheels (dépendances) | ~45 MB |
| Python embeddable | ~15 MB |
| **TOTAL** | **~60 MB** |

**Clé USB 128 MB suffit largement !**

---

## 🎓 Cas d'usage réels

### 1. Installation en salle blanche

```
Pas d'Internet en salle blanche
→ Prépare package sur poste externe
→ Clé USB → Salle blanche
→ Installation en 30 secondes !
```

### 2. Archivage projet

```
Projet 2025 avec versions exactes
→ Archive complète
→ Réinstallation identique en 2030 !
```

### 3. Formation étudiants

```
1 préparation → 30 installations identiques
Chaque étudiant : copie + launch.bat
Tout le monde a la même version !
```

---

## 🐛 Dépannage express

| Problème | Solution |
|----------|----------|
| "Module not found" | Wheels manquants dans Requirements/wheels/ |
| "Python not found" | Ajoutez Python portable ou installez système |
| "pip failed" | Vérifiez connexion Internet OU wheels locales |
| GPIB non détecté | Installez drivers Keysight séparément |

---

## ✅ Checklist rapide

**Avant de transférer sur machine isolée :**

- [ ] `Requirements/wheels/` contient ~15-20 fichiers .whl
- [ ] (Optionnel) `Requirements/python/python.exe` existe
- [ ] Drivers GPIB téléchargés séparément (si nécessaire)
- [ ] `launch.bat` testé en local

**Sur machine isolée :**

- [ ] Dossier complet copié
- [ ] Drivers GPIB installés (si carte PCI)
- [ ] `launch.bat` lancé en admin
- [ ] Programme fonctionne !

---

## 🎉 Résumé en 3 lignes

1. **Avec Internet** : `launch.bat` → Installation automatique
2. **Sans Internet** : `prepare_offline_install.bat` → Clé USB → `launch.bat`
3. **Drivers GPIB** : Toujours installer séparément

**Simple, rapide, reproductible ! ✨**

---

## 📞 Questions fréquentes

**Q : Dois-je télécharger Python embeddable ?**  
R : Non, c'est optionnel. Utile si la machine cible n'a pas Python.

**Q : Puis-je utiliser mon Python système ?**  
R : Oui ! `launch.bat` le détectera automatiquement.

**Q : Les wheels fonctionnent sur toutes les machines ?**  
R : Oui, tant que c'est Windows 64-bit avec même version Python.

**Q : Combien de temps prend l'installation offline ?**  
R : ~30 secondes (vs ~5 minutes avec Internet).

**Q : Puis-je archiver pour plus tard ?**  
R : Oui ! Package complet stable dans le temps.

---

**🚀 Profitez de votre installation autonome et portable !**
