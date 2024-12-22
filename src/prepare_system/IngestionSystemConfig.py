import json

# Percorso del file di configurazione JSON
CONFIG_PATH = "../../data/prepare_system/configs/config.json"

class IngConfiguration:
    """
    Classe per gestire la configurazione del sistema di ingestion.
    Carica i parametri dal file JSON specificato nel percorso CONFIG_PATH.

    Attributi:
        threshold (float): Soglia per la configurazione.
        evaluation_phase (str): Fase di valutazione specificata nel file di configurazione.
        development_phase (str): Fase di sviluppo specificata nel file di configurazione.
    """

    def __init__(self):
        """
        Inizializza l'oggetto IngConfiguration caricando i parametri dal file di configurazione.
        Gestisce eventuali errori di lettura o di decodifica del file JSON.
        """
        try:
            # Apertura del file di configurazione
            with open(CONFIG_PATH) as f:
                config = json.load(f)  # Carica il contenuto del file JSON

                # Assegna i parametri ai rispettivi attributi
                self.threshold = config["threshold"]
                self.evaluation_phase = config["ev_phase"]
                self.development_phase = config["dev_phase"]

                self.indirizzo_test = config["indirizzo_test"]
                self.indirizzo_ev =  config["indirizzo_ev"]
                self.indirizzo_segr = config["indirizzo_segr"]
                self.indirizzo_prod = config["indirizzo_prod"]
                self.testing = config["testing"]



        except FileNotFoundError:
            # Gestisce il caso in cui il file di configurazione non venga trovato
            print("ERROR> Configuration file not found")
        except json.JSONDecodeError:
            # Gestisce il caso in cui il file di configurazione contenga un JSON non valido
            print("ERROR> Error decoding JSON file")
