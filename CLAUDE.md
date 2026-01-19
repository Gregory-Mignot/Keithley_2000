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

1. **Logo OptiMag** - ✏️ *À tester in situ* - Correction avec `AnnotationBbox` + coordonnées relatives dans `gui/quick_measure_tab.py:90`

2. **Modes de mesure non fonctionnels** - ✏️ *À tester in situ* - Ajout `NPLC_SUPPORTED` et `RANGE_SUPPORTED` dans `keithley2000.py` pour éviter les commandes SCPI invalides sur ACV/ACI

3. **Erreur -420 en mode Fast** - ✏️ *À tester in situ* - Remplacé par `INIT;:FETC?` (une seule commande) dans `keithley2000.py:219`

4. **Mode Buffer non fonctionnel** - ✏️ *À tester in situ* - Refonte complète des méthodes buffer dans `keithley2000.py:274-356` (séquence SCPI corrigée, SENS1, délais, gestion status)

5. **Export CSV** - ✏️ *À tester in situ* - Correction appliquée : ajout `encoding='utf-8-sig'` et `newline=''` dans `gui/quick_measure_tab.py:792`

### Améliorations demandées

6. **Clear pendant la mesure** - ✏️ *À tester in situ* - Correction appliquée : confirmation + reset `start_time` dans `gui/quick_measure_tab.py:732`

7. **Zoom amélioré** - ✏️ *À tester in situ* - Nouveau mode "Manuel (limites fixes)" avec champs X/Y min/max dans `gui/quick_measure_tab.py`

8. **Curseur/réticule** - ✏️ *À tester in situ* - Checkbox "Curseur" + crosshair snappé avec annotation X/Y dans `gui/quick_measure_tab.py`

9. **Export données visibles** - ✏️ *À tester in situ* - Bouton "Export visible" sous le graphique pour exporter uniquement les points dans la plage de zoom actuelle (`gui/quick_measure_tab.py:973`)
