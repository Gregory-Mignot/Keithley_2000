"""
Classe de contrôle du Keithley 2000
Gère toutes les communications VISA et commandes SCPI
"""
import pyvisa
from pyvisa.errors import VisaIOError
import time

class Keithley2000:
    """Classe pour contrôler le multimètre Keithley 2000 via VISA"""
    
    # Types de mesures supportés
    MEASURE_TYPES = {
        'DCV': 'VOLT:DC',
        'ACV': 'VOLT:AC',
        'DCI': 'CURR:DC',
        'ACI': 'CURR:AC',
        'RES_2W': 'RES',
        'RES_4W': 'FRES',
        'FREQ': 'FREQ',
        'PERIOD': 'PER',
        'TEMP': 'TEMP',
        'DIODE': 'DIOD',
        'CONT': 'CONT'
    }

    # Types de mesure supportant NPLC (les AC et autres n'ont pas NPLC)
    NPLC_SUPPORTED = {'DCV', 'DCI', 'RES_2W', 'RES_4W', 'TEMP'}

    # Types de mesure supportant le réglage de range
    RANGE_SUPPORTED = {'DCV', 'ACV', 'DCI', 'ACI', 'RES_2W', 'RES_4W'}
    
    def __init__(self, gpib_address=None, timeout=5000):
        """
        Initialise la connexion au Keithley 2000
        Args:
            gpib_address (str): Adresse GPIB (ex: 'GPIB0::16::INSTR')
            timeout (int): Timeout en millisecondes
        """
        self.meter = None
        self.connected = False
        self.timeout = timeout
        
        if gpib_address:
            self.connect(gpib_address)
    
    def connect(self, gpib_address):
        """
        Établit la connexion avec l'instrument
        Args:
            gpib_address (str): Adresse GPIB
        Returns:
            bool: True si connexion réussie
        """
        try:
            rm = pyvisa.ResourceManager()
            self.meter = rm.open_resource(gpib_address)
            self.meter.timeout = self.timeout
            self.connected = True
            return True
        except VisaIOError as e:
            self.connected = False
            raise Exception(f"Erreur de connexion GPIB: {e}")
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.meter:
            try:
                self.write('SYST:LOC')  # Retour en mode local
                self.meter.close()
            except:
                pass
        self.connected = False
    
    def write(self, command):
        """
        Envoie une commande SCPI
        Args:
            command (str): Commande SCPI
        """
        if not self.connected:
            raise Exception("Instrument non connecté")
        try:
            self.meter.write(command)
        except VisaIOError as e:
            raise Exception(f"Erreur d'écriture: {e}")
    
    def query(self, command):
        """
        Envoie une commande et lit la réponse
        Args:
            command (str): Commande SCPI
        Returns:
            str: Réponse de l'instrument
        """
        if not self.connected:
            raise Exception("Instrument non connecté")
        try:
            return self.meter.query(command).strip()
        except VisaIOError as e:
            raise Exception(f"Erreur de lecture: {e}")
    
    def read(self):
        """
        Lit une réponse de l'instrument
        Returns:
            str: Réponse
        """
        if not self.connected:
            raise Exception("Instrument non connecté")
        try:
            return self.meter.read().strip()
        except VisaIOError as e:
            raise Exception(f"Erreur de lecture: {e}")
    
    def get_id(self):
        """
        Récupère l'identification de l'instrument
        Returns:
            str: Chaîne d'identification
        """
        return self.query('*IDN?')
    
    def reset(self):
        """Reset de l'instrument"""
        self.write('*RST')
        time.sleep(0.5)
    
    def configure_measurement(self, meas_type, range_val='AUTO', resolution=None):
        """
        Configure le type de mesure
        Args:
            meas_type (str): Type de mesure (clé de MEASURE_TYPES)
            range_val (str/float): 'AUTO' ou valeur numérique
            resolution (float): Résolution (0.0001 à 1)
        """
        if meas_type not in self.MEASURE_TYPES:
            raise ValueError(f"Type de mesure invalide: {meas_type}")

        func = self.MEASURE_TYPES[meas_type]

        # Configuration de base
        self.write(f'CONF:{func}')

        # Configuration de la plage (seulement pour les types qui le supportent)
        if meas_type in self.RANGE_SUPPORTED:
            if range_val == 'AUTO':
                self.write(f'{func}:RANG:AUTO ON')
            else:
                self.write(f'{func}:RANG:AUTO OFF')
                self.write(f'{func}:RANG {range_val}')

        # Configuration de la résolution (seulement si NPLC supporté)
        if resolution and meas_type in self.NPLC_SUPPORTED:
            self.write(f'{func}:NPLC {resolution}')
    
    def set_nplc(self, nplc, meas_type=None):
        """
        Configure le NPLC (Number of Power Line Cycles)
        Args:
            nplc (float): 0.01 à 10 (vitesse vs précision)
            meas_type (str): Type de mesure (si None, utilise la fonction courante)
        Note: NPLC n'est supporté que pour DCV, DCI, RES_2W, RES_4W, TEMP
        """
        # Vérifier si le type de mesure supporte NPLC
        if meas_type and meas_type not in self.NPLC_SUPPORTED:
            return  # Ignorer silencieusement pour les types non supportés

        if meas_type:
            func = self.MEASURE_TYPES.get(meas_type)
        else:
            # Récupérer la fonction courante
            func = self.query('FUNC?').strip('"')

        if func:
            self.write(f'{func}:NPLC {nplc}')
    
    def set_filter(self, state, count=10, filter_type='MOV'):
        """
        Configure le filtrage numérique
        Args:
            state (bool): Active/désactive le filtre
            count (int): Nombre de mesures pour le filtre
            filter_type (str): 'MOV' (moving average) ou 'REP' (repeat)
        """
        if state:
            self.write(f'AVER:TCON {filter_type}')
            self.write(f'AVER:COUN {count}')
            self.write('AVER:STAT ON')
        else:
            self.write('AVER:STAT OFF')
    
    def set_trigger_source(self, source='IMM'):
        """
        Configure la source de déclenchement
        Args:
            source (str): 'IMM', 'BUS', 'EXT', 'TIM'
        """
        self.write(f'TRIG:SOUR {source}')
    
    def measure_single(self):
        """
        Effectue une mesure unique
        Returns:
            float: Valeur mesurée
        """
        response = self.query('READ?')
        return float(response)
    
    def measure_fast(self):
        """
        Mesure rapide: combine INIT et FETCH en une seule transaction GPIB
        Returns:
            float: Valeur mesurée
        Note: Plus rapide que measure_single() car évite la reconfiguration
              L'instrument doit être pré-configuré (trigger source = IMM)
        """
        # Méthode 1: Combiner INIT et FETCH (évite l'erreur -420)
        response = self.query('INIT;:FETC?')
        return float(response)
    
    def initiate_measurement(self):
        """Déclenche une mesure"""
        self.write('INIT')
    
    def fetch_measurement(self):
        """
        Récupère la dernière mesure
        Returns:
            float: Valeur mesurée
        """
        response = self.query('FETC?')
        return float(response)
    
    def get_error(self):
        """
        Vérifie les erreurs
        Returns:
            str: Message d'erreur
        """
        return self.query('SYST:ERR?')
    
    def clear_errors(self):
        """Efface les erreurs"""
        self.write('*CLS')
    
    def set_display(self, state):
        """
        Active/désactive l'affichage
        Args:
            state (bool): True pour activer
        """
        self.write(f'DISP:ENAB {1 if state else 0}')
    
    def beep(self, frequency=1000, duration=0.1):
        """
        Émet un bip
        Args:
            frequency (int): Fréquence en Hz
            duration (float): Durée en secondes
        """
        self.write(f'SYST:BEEP {frequency}, {duration}')
    
    def set_autozero(self, state):
        """
        Active/désactive l'autozero (gain de vitesse si désactivé)
        Args:
            state (bool): True pour activer
        """
        self.write(f'SYST:AZER:STAT {1 if state else 0}')

    # ===== MÉTHODES BUFFER =====

    def buffer_clear(self):
        """Vide le buffer de mesures"""
        self.write('TRAC:CLE')
        time.sleep(0.1)

    def buffer_configure(self, points=1024):
        """
        Configure le buffer pour l'acquisition rapide
        Args:
            points (int): Nombre de points (max 1024 sur Keithley 2000)
        """
        points = min(points, 1024)  # Limite hardware
        self._buffer_target = points  # Sauvegarder pour buffer_is_complete

        # Séquence de configuration robuste
        self.write('TRAC:FEED:CONT NEV')  # Arrêter le feed d'abord
        time.sleep(0.05)
        self.write('TRAC:CLE')            # Vider le buffer
        time.sleep(0.05)
        self.write(f'TRAC:POIN {points}') # Configurer la taille
        self.write('TRAC:FEED SENS1')     # Source = mesures (SENS1 pas SENS)
        self.write('TRAC:FEED:CONT NEXT') # Remplir une fois puis arrêter

    def buffer_start(self, count=1024):
        """
        Lance l'acquisition buffer (mesures au plus vite)
        Args:
            count (int): Nombre de mesures à effectuer
        """
        count = min(count, 1024)
        self.write('STAT:MEAS:ENAB 512')  # Activer bit "Buffer Full" dans status
        self.write(f'TRIG:COUN {count}')
        self.write('TRIG:SOUR IMM')       # Trigger immédiat = au plus vite
        self.write('INIT')

    def buffer_is_complete(self):
        """
        Vérifie si l'acquisition buffer est terminée
        Returns:
            bool: True si terminé
        """
        try:
            # Méthode 1: Vérifier le status byte (bit 4 = MAV)
            stb = int(self.query('*STB?'))
            # Bit 0 du measurement status = Buffer Full
            if stb & 1:
                return True

            # Méthode 2: Comparer les points
            actual = self.buffer_get_count()
            target = getattr(self, '_buffer_target', 1024)
            return actual >= target
        except:
            return False

    def buffer_get_count(self):
        """
        Retourne le nombre de points actuellement dans le buffer
        Returns:
            int: Nombre de points
        """
        try:
            response = self.query('TRAC:POIN:ACT?')
            return int(float(response))  # Parfois retourne un float
        except:
            return 0

    def buffer_read(self):
        """
        Lit toutes les données du buffer
        Returns:
            list: Liste des valeurs mesurées
        """
        # Arrêter l'acquisition si en cours
        self.write('ABOR')
        time.sleep(0.1)

        response = self.query('TRAC:DATA?')
        # Réponse format: "val1,val2,val3,..."
        if not response or response.strip() == '':
            return []
        values = [float(v) for v in response.split(',') if v.strip()]
        return values

    def get_unit(self):
        """
        Récupère l'unité de mesure actuelle
        Returns:
            str: Unité
        """
        func = self.query('FUNC?').strip('"')
        units = {
            'VOLT:DC': 'V',
            'VOLT:AC': 'V',
            'CURR:DC': 'A',
            'CURR:AC': 'A',
            'RES': 'Ω',
            'FRES': 'Ω',
            'FREQ': 'Hz',
            'PER': 's',
            'TEMP': '°C',
            'DIOD': 'V',
            'CONT': 'Ω'
        }
        return units.get(func, '')
    
    @staticmethod
    def list_resources(verify=True, timeout=1000, filter_keithley=True):
        """
        Liste les ressources VISA disponibles
        Args:
            verify (bool): Si True, vérifie que l'instrument répond (*IDN?)
            timeout (int): Timeout en ms pour la vérification
            filter_keithley (bool): Si True, ne garde que les Keithley série 2000
        Returns:
            list: Liste des chaînes "adresse - modèle" pour les instruments compatibles
        """
        try:
            rm = pyvisa.ResourceManager()
            all_resources = list(rm.list_resources())

            if not verify:
                return all_resources

            # Trier pour avoir les adresses simples (sans secondary) en premier
            # Ex: GPIB0::16::INSTR avant GPIB0::16::0::INSTR
            def address_priority(addr):
                # Compter le nombre de :: pour déterminer la complexité
                return addr.count('::')

            sorted_resources = sorted(all_resources, key=address_priority)

            # Vérifier chaque ressource et éliminer les doublons
            # (même instrument accessible via plusieurs adresses secondaires)
            verified_resources = []
            seen_idn = set()

            for resource in sorted_resources:
                try:
                    instr = rm.open_resource(resource)
                    instr.timeout = timeout
                    idn = instr.query('*IDN?').strip()
                    instr.close()

                    # Ne garder que si c'est un nouvel instrument
                    if idn not in seen_idn:
                        seen_idn.add(idn)

                        # Extraire le modèle du IDN (format: MANUFACTURER,MODEL,SERIAL,VERSION)
                        idn_parts = idn.split(',')
                        manufacturer = idn_parts[0] if len(idn_parts) > 0 else ''
                        model = idn_parts[1] if len(idn_parts) > 1 else ''

                        # Filtrer pour Keithley série 2000
                        if filter_keithley:
                            if 'KEITHLEY' in manufacturer.upper() and '2000' in model.upper():
                                display_name = f"{resource} - {model.strip()}"
                                verified_resources.append(display_name)
                        else:
                            display_name = f"{resource} - {manufacturer.strip()} {model.strip()}"
                            verified_resources.append(display_name)
                except:
                    # L'instrument ne répond pas, on l'ignore
                    pass

            return verified_resources
        except:
            return []
