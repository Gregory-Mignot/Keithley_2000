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

## TODO - Tâches en attente (session du 16/01/2026)

### Bugs à corriger

1. **Logo OptiMag** - Vérifier le positionnement du logo sur la figure matplotlib (en bas à droite, sous l'axe X)

2. **Modes de mesure non fonctionnels** - Seuls RES_2W (résistance 2 fils) et DCV (tension DC) fonctionnent. Les autres modes (ACV, DCI, ACI, RES_4W) génèrent des erreurs. Vérifier les commandes SCPI pour chaque type.

3. **Erreur -420 en mode Fast** - Le mode Fast (`measure_fast()`) génère une erreur -420 (Query UNTERMINATED). La séquence INIT/*OPC?/FETC? ne fonctionne pas correctement.

4. **Mode Buffer non fonctionnel** - Le mode Buffer génère plusieurs erreurs :
   - Erreur -113 (Undefined header)
   - Erreur -420 (Query UNTERMINATED)
   - Autres erreurs non identifiées
   - Vérifier les commandes TRAC:* et la séquence d'acquisition buffer

5. **Export CSV** - L'enregistrement CSV ne fonctionne pas, problèmes de caractères (encodage ?). Vérifier l'encodage UTF-8 et les caractères spéciaux (°, Ω, etc.)

### Améliorations demandées

6. **Clear pendant la mesure** - Permettre d'effacer le graphique (Clear) même pendant une acquisition en cours

7. **Zoom amélioré** - Ajouter la possibilité de définir manuellement les valeurs min/max des axes du graphique

8. **Curseur/réticule** - Ajouter un curseur ou réticule "snappé" à la courbe pour lire précisément les valeurs (crosshair suivant la souris, affichant les coordonnées X/Y du point le plus proche)
