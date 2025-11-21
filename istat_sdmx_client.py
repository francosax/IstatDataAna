"""
ISTAT SDMX API Client
Classe Python per interfacciarsi con le API REST SDMX dell'ISTAT
"""

import requests
import pandas as pd
import time
from typing import Optional, Dict, List
import logging
from datetime import datetime


class IstatSDMXClient:
    """
    Client per accedere ai dati statistici ISTAT via API SDMX REST
    """
    
    # Endpoint principale
    BASE_URL = "https://esploradati.istat.it/SDMXWS/rest"
    
    # Rate limiting: max 5 query al minuto
    MAX_REQUESTS_PER_MINUTE = 5
    REQUEST_INTERVAL = 60 / MAX_REQUESTS_PER_MINUTE  # secondi tra richieste
    
    def __init__(self, log_level: str = "INFO"):
        """
        Inizializza il client ISTAT SDMX
        
        Args:
            log_level: Livello di logging (DEBUG, INFO, WARNING, ERROR)
        """
        self.session = requests.Session()
        self.last_request_time = 0
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _rate_limit(self):
        """
        Implementa il rate limiting per evitare di superare 5 richieste al minuto
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < self.REQUEST_INTERVAL:
            sleep_time = self.REQUEST_INTERVAL - elapsed
            self.logger.debug(f"Rate limiting: attendo {sleep_time:.2f} secondi")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, headers: Optional[Dict] = None) -> requests.Response:
        """
        Esegue una richiesta HTTP con rate limiting
        
        Args:
            endpoint: Endpoint API relativo
            headers: Headers HTTP opzionali
            
        Returns:
            Response object
        """
        self._rate_limit()
        url = f"{self.BASE_URL}/{endpoint}"
        
        self.logger.info(f"Richiesta: {url}")
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Errore nella richiesta: {e}")
            raise
    
    def get_dataflows(self, agency_id: str = "IT1", format: str = "json") -> pd.DataFrame:
        """
        Recupera l'elenco completo dei dataflow (dataset) disponibili
        
        Args:
            agency_id: ID dell'agenzia (default: IT1 per ISTAT)
            format: Formato output (json o xml)
            
        Returns:
            DataFrame con l'elenco dei dataflow
        """
        endpoint = f"dataflow/{agency_id}"
        
        headers = {}
        if format.lower() == "json":
            headers["Accept"] = "application/vnd.sdmx.structure+json;version=1.0.0"
        
        response = self._make_request(endpoint, headers)
        
        if format.lower() == "json":
            data = response.json()
            # Parsing della struttura JSON SDMX
            dataflows = []
            for df in data.get('data', {}).get('dataflows', []):
                dataflows.append({
                    'id': df.get('id'),
                    'name_it': df.get('name', {}).get('it'),
                    'name_en': df.get('name', {}).get('en'),
                    'agency': df.get('agencyID'),
                    'version': df.get('version')
                })
            return pd.DataFrame(dataflows)
        else:
            # Per XML restituisce il testo grezzo
            return response.text
    
    def get_datastructure(self, dataflow_id: str, agency_id: str = "IT1") -> Dict:
        """
        Recupera la struttura dati (dimensioni e attributi) di un dataflow
        
        Args:
            dataflow_id: ID del dataflow
            agency_id: ID dell'agenzia
            
        Returns:
            Dizionario con la struttura dati
        """
        # Prima ottieni il dataflow per trovare l'ID della datastructure
        endpoint = f"dataflow/{agency_id}/{dataflow_id}"
        headers = {"Accept": "application/vnd.sdmx.structure+json;version=1.0.0"}
        
        response = self._make_request(endpoint, headers)
        data = response.json()
        
        # Estrai l'ID della datastructure
        dataflows = data.get('data', {}).get('dataflows', [])
        if not dataflows:
            raise ValueError(f"Dataflow {dataflow_id} non trovato")
        
        structure_ref = dataflows[0].get('structure', {})
        structure_id = structure_ref.get('id')
        
        # Ottieni la datastructure
        endpoint = f"datastructure/{agency_id}/{structure_id}"
        response = self._make_request(endpoint, headers)
        
        return response.json()
    
    def get_codelist(self, codelist_id: str, agency_id: str = "IT1") -> pd.DataFrame:
        """
        Recupera una codelist (elenco dei valori possibili per una dimensione)
        
        Args:
            codelist_id: ID della codelist (es: CL_FREQ)
            agency_id: ID dell'agenzia
            
        Returns:
            DataFrame con i codici e le descrizioni
        """
        endpoint = f"codelist/{agency_id}/{codelist_id}"
        headers = {"Accept": "application/vnd.sdmx.structure+json;version=1.0.0"}
        
        response = self._make_request(endpoint, headers)
        data = response.json()
        
        codelists = data.get('data', {}).get('codelists', [])
        if not codelists:
            raise ValueError(f"Codelist {codelist_id} non trovata")
        
        codes = []
        for code in codelists[0].get('codes', []):
            codes.append({
                'id': code.get('id'),
                'name_it': code.get('name', {}).get('it'),
                'name_en': code.get('name', {}).get('en')
            })
        
        return pd.DataFrame(codes)
    
    def get_available_constraints(self, dataflow_id: str) -> Dict:
        """
        Recupera i vincoli (valori effettivamente disponibili) per un dataflow
        Equivalente a un SELECT DISTINCT sulle dimensioni
        
        Args:
            dataflow_id: ID del dataflow
            
        Returns:
            Dizionario con i valori disponibili per dimensione
        """
        endpoint = f"availableconstraint/{dataflow_id}"
        headers = {"Accept": "application/vnd.sdmx.structure+json;version=1.0.0"}
        
        response = self._make_request(endpoint, headers)
        return response.json()
    
    def get_data(
        self,
        dataflow_id: str,
        key: str = "",
        provider_id: str = "IT1",
        start_period: Optional[str] = None,
        end_period: Optional[str] = None,
        format: str = "csv",
        **kwargs
    ) -> pd.DataFrame:
        """
        Recupera i dati da un dataflow
        
        Args:
            dataflow_id: ID del dataflow (es: "115_333")
            key: Chiave di filtro (es: ".F.082053.." per filtrare dimensioni)
                 Separare valori multipli con +, lasciare vuoto per nessun filtro
            provider_id: ID del provider (default: IT1)
            start_period: Periodo inizio (ISO8601: 2014-01 o SDMX: 2014-Q3)
            end_period: Periodo fine
            format: Formato output (csv, json, xml)
            **kwargs: Altri parametri query string (detail, includeHistory, etc.)
            
        Returns:
            DataFrame con i dati (se formato CSV o JSON)
            
        Esempi:
            # Tutti i dati
            client.get_data("115_333")
            
            # Solo incidenti con feriti (F) a Palermo (082053)
            client.get_data("41_983", key=".F.082053..")
            
            # Multiple città
            client.get_data("41_983", key=".F.082053+072006..")
            
            # Con filtro temporale
            client.get_data("41_983", start_period="2015", end_period="2020")
        """
        # Costruisci l'endpoint
        if key:
            endpoint = f"data/{dataflow_id}/{key}/{provider_id}"
        else:
            endpoint = f"data/{dataflow_id}"
        
        # Costruisci query string parameters
        params = []
        if start_period:
            params.append(f"startPeriod={start_period}")
        if end_period:
            params.append(f"endPeriod={end_period}")
        for k, v in kwargs.items():
            params.append(f"{k}={v}")
        
        if params:
            endpoint += "?" + "&".join(params)
        
        # Imposta headers per formato
        headers = {}
        if format.lower() == "csv":
            headers["Accept"] = "application/vnd.sdmx.data+csv;version=1.0.0"
        elif format.lower() == "json":
            headers["Accept"] = "application/vnd.sdmx.data+json;version=1.0.0"
        
        response = self._make_request(endpoint, headers)
        
        # Parsing risposta
        if format.lower() == "csv":
            # Pandas può leggere direttamente dal testo CSV
            from io import StringIO
            return pd.read_csv(StringIO(response.text))
        elif format.lower() == "json":
            # Per JSON SDMX serve parsing personalizzato
            # Qui restituiamo il JSON grezzo, da parsare in base alle esigenze
            return response.json()
        else:
            return response.text


# ============================================================================
# ESEMPI DI UTILIZZO
# ============================================================================

def esempi_utilizzo():
    """
    Esempi pratici di utilizzo del client ISTAT SDMX
    """
    
    # Inizializza il client
    client = IstatSDMXClient(log_level="INFO")
    
    # ----- ESEMPIO 1: Lista tutti i dataflow disponibili -----
    print("\n=== ESEMPIO 1: Elenco dataflow ===")
    try:
        dataflows = client.get_dataflows()
        print(f"Trovati {len(dataflows)} dataflow")
        print(dataflows.head())
        # Salva su file
        dataflows.to_csv("istat_dataflows.csv", index=False)
        print("Salvato in: istat_dataflows.csv")
    except Exception as e:
        print(f"Errore: {e}")
    
    # ----- ESEMPIO 2: Ottieni una codelist -----
    print("\n=== ESEMPIO 2: Codelist frequenze ===")
    try:
        freq_codes = client.get_codelist("CL_FREQ")
        print(freq_codes)
    except Exception as e:
        print(f"Errore: {e}")
    
    # ----- ESEMPIO 3: Scarica dati con filtri -----
    print("\n=== ESEMPIO 3: Dati incidenti stradali ===")
    try:
        # Dataflow: Incidenti, morti e feriti - comuni (ID: 41_983)
        # Filtro: Solo feriti (F) nelle città di Palermo (082053) e Bari (072006)
        # Dal 2015 in poi
        
        df = client.get_data(
            dataflow_id="41_983",
            key=".F.082053+072006..",
            start_period="2015",
            format="csv"
        )
        
        print(f"Recuperati {len(df)} record")
        print(df.head())
        
        # Salva risultati
        df.to_csv("incidenti_palermo_bari.csv", index=False)
        print("Dati salvati in: incidenti_palermo_bari.csv")
        
    except Exception as e:
        print(f"Errore: {e}")
    
    # ----- ESEMPIO 4: Esplora la struttura di un dataflow -----
    print("\n=== ESEMPIO 4: Struttura dati ===")
    try:
        structure = client.get_datastructure("115_333")  # Produzione industriale
        print("Struttura ottenuta con successo")
        # Analizza le dimensioni disponibili
        # (il parsing dettagliato dipende dalla struttura JSON SDMX)
    except Exception as e:
        print(f"Errore: {e}")
    
    # ----- ESEMPIO 5: Vincoli disponibili -----
    print("\n=== ESEMPIO 5: Valori disponibili ===")
    try:
        constraints = client.get_available_constraints("41_983")
        print("Vincoli ottenuti con successo")
        # Mostra quali combinazioni di valori sono effettivamente presenti
    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    # Esegui gli esempi
    esempi_utilizzo()
