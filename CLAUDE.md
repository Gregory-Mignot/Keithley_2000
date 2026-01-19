# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python desktop application for controlling and monitoring a Keithley 2000 Digital Multimeter via GPIB/VISA interface. Built with Tkinter GUI and PyVISA for instrument communication.

## Commands

### Installation

```bash
# Online installation
pip install -r requirements.txt

# Offline installation (from pre-downloaded wheels)
pip install --no-index --find-links=Requirements/wheels -r requirements.txt

# Verify installation
python check_installation.py
```

### Running the Application

```bash
python main.py
```

Or use `launch.bat` which auto-detects Python and dependencies.

## Architecture

```
main.py                    # Entry point - creates Tk root window
├── keithley2000.py        # Core instrument control class (GPIB/VISA communication)
└── gui/
    ├── main_window.py     # Main window with tab container and status bar
    ├── settings_tab.py    # GPIB connection discovery and setup
    ├── quick_measure_tab.py  # Real-time measurement acquisition with graphing
    └── advanced_tab.py    # SCPI console and advanced configuration
```

### Key Components

**keithley2000.py** - Low-level instrument controller:
- `Keithley2000` class handles all VISA communication
- Supports 11 measurement types: DCV, ACV, DCI, ACI, RES_2W, RES_4W, FREQ, PERIOD, TEMP, DIODE, CONT
- Key methods: `connect()`, `configure_measurement()`, `measure_single()`, `measure_fast()`, `query()`, `write()`

**gui/quick_measure_tab.py** - Real-time acquisition:
- Measurement runs in background thread to avoid UI blocking
- Uses `deque(maxlen=10000)` circular buffer for memory management
- Matplotlib embedded graph with auto-scaling
- CSV export includes full metadata header

**gui/advanced_tab.py** - Direct SCPI control:
- Command console with history (↑/↓ navigation)
- Trigger configuration (IMM, BUS, EXT, TIM)
- NULL/offset measurement support
- Instrument buffer management

### Data Flow

```
Settings Tab → Connect to instrument via GPIB
    ↓
Quick Measure Tab → Configure measurement parameters
    ↓
Keithley2000.configure_measurement() → SCPI commands
    ↓
Background thread: measure_single()/measure_fast() → Update graph via callback
```

## Key Dependencies

- **pyvisa** / **pyvisa-py**: GPIB/VISA communication
- **matplotlib**: Real-time graphing
- **numpy** / **pandas**: Data handling
- **tkinter**: GUI (stdlib)

**External requirement**: Keysight IO Libraries Suite must be installed separately for GPIB driver support.

## Documentation

- `Readme/keithley_summary.md` - Complete feature overview
- `Readme/install_guide.md` - Step-by-step installation
- `keithley_2000_scpi_reference.html` - SCPI command reference (accessible from Advanced tab)

## TODO - Session du 19/01/2026

### À tester sur l'instrument (toutes les corrections de cette session)

#### Bugs corrigés

1. **Logo OptiMag** - ✏️ *À tester* - Correction avec `AnnotationBbox` + coordonnées relatives (reste en place au redimensionnement)

2. **Modes de mesure ACV/ACI** - ✏️ *À tester* - Ajout `NPLC_SUPPORTED` et `RANGE_SUPPORTED` dans `keithley2000.py` pour éviter les commandes SCPI invalides

3. **Erreur -420 en mode Fast** - ✏️ *À tester* - Remplacé par `INIT;:FETC?` (une seule commande SCPI)

4. **Mode Buffer** - ✏️ *À tester* - Refonte complète : séquence SCPI corrigée (SENS1, délais, TRAC:FEED:CONT NEV d'abord)

5. **Export CSV encodage** - ✏️ *À tester* - `encoding='utf-8-sig'` + `newline=''` pour caractères spéciaux (Ω, °C)

#### Améliorations implémentées

6. **Clear pendant la mesure** - ✏️ *À tester* - Possible avec confirmation, reset du temps de départ

7. **Zoom amélioré** - ✏️ *À tester* - Modes ajoutés :
   - "Manuel (limites fixes)" avec champs X/Y sur une ligne
   - "Fixe X, Auto Y" : X fixe, Y autoscale sur données visibles
   - "Auto X, Fixe Y" : X défile, Y fixe
   - Boutons séparés [X] [Y] [X+Y] pour appliquer les limites indépendamment

8. **Curseur/réticule** - ✏️ *À tester* - Checkbox "Curseur" + crosshair rouge snappé à la courbe avec annotation X/Y

9. **Export données visibles** - ✏️ *À tester* - Bouton "Export visible" pour exporter uniquement les points dans la plage de zoom actuelle

10. **Interface améliorée** - ✏️ *À tester* :
    - Fenêtre maximisée au démarrage (`main.py`)
    - Boutons Start/Pause/Stop/Clear/Export fixes en haut (ne scrollent pas)

### Fichiers modifiés (session 19/01/2026)

- `main.py` : fenêtre maximisée au démarrage
- `keithley2000.py` : NPLC_SUPPORTED, RANGE_SUPPORTED, measure_fast(), méthodes buffer
- `gui/quick_measure_tab.py` : logo, curseur, zoom hybride, export visible, boutons fixes
