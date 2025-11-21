# ISTAT SDMX REST API - Client Python

Client Python completo per interfacciarsi con le API REST SDMX dell'ISTAT (Istituto Nazionale di Statistica).

## 📋 Caratteristiche

- ✅ **Rate limiting automatico**: Rispetta il limite di 5 query/minuto
- ✅ **Gestione completa metadati**: Dataflows, datastructures, codelists
- ✅ **Multiple formati**: CSV, JSON, XML
- ✅ **Type hints e documentazione**: Codice ben documentato
- ✅ **Logging configurabile**: Debug e monitoraggio semplificato
- ✅ **Esempi pratici**: Da casi base ad analisi avanzate ML

## 🚀 Installazione

### Requisiti
```bash
Python >= 3.7
```

### Dipendenze
```bash
pip install requests pandas matplotlib seaborn numpy
```

### Installazione rapida
```bash
# Scarica i file
# istat_sdmx_client.py - Client principale
# istat_advanced_analysis.py - Esempi avanzati

# Importa nel tuo progetto
from istat_sdmx_client import IstatSDMXClient
```

## 📚 Utilizzo Base

### 1. Inizializzazione

```python
from istat_sdmx_client import IstatSDMXClient

# Crea client
client = IstatSDMXClient(log_level="INFO")
```

### 2. Lista dataflows disponibili

```python
# Ottieni tutti i dataset disponibili
dataflows = client.get_dataflows()
print(f"Trovati {len(dataflows)} dataflow")

# Filtra per nome
incidenti = dataflows[dataflows['name_it'].str.contains('incidenti', case=False)]
print(incidenti)
```

### 3. Esplora metadati

```python
# Ottieni codelist (valori possibili per una dimensione)
freq = client.get_codelist("CL_FREQ")
print(freq)

# Ottieni struttura dati di un dataflow
structure = client.get_datastructure("115_333")

# Ottieni valori effettivamente disponibili (SELECT DISTINCT)
constraints = client.get_available_constraints("41_983")
```

### 4. Scarica dati

```python
# Esempio base: tutti i dati
df = client.get_data(
    dataflow_id="115_333",
    format="csv"
)

# Con filtri su dimensioni
# Struttura key: "dim1.dim2.dim3.dim4.dim5"
# Valori multipli: "dim1+dim1b.dim2.dim3"
# Nessun filtro: "."

df = client.get_data(
    dataflow_id="41_983",
    key=".F.082053..",  # Solo feriti (F) a Palermo (082053)
    start_period="2015",
    end_period="2020",
    format="csv"
)

print(df.head())
```

## 🔍 Esempi Avanzati

### Analisi serie temporale

```python
from istat_advanced_analysis import IstatDataAnalyzer

analyzer = IstatDataAnalyzer()

# Scarica e prepara serie temporale
df = analyzer.download_timeseries(
    dataflow_id="41_983",
    key=".F.082053..",
    start_year=2001,
    end_year=2020
)

# Calcola crescita year-over-year
df = analyzer.calculate_growth_rate(df)

# Identifica outliers
df = analyzer.detect_outliers(df, method='iqr')
```

### Confronto regioni

```python
# Confronta dati tra Palermo e Bari
df_compare = analyzer.compare_regions(
    dataflow_id="41_983",
    region_codes=["082053", "072006"],
    start_year=2010
)
```

### Preparazione per Machine Learning

```python
# Crea features per ML
df_ml = analyzer.download_timeseries("41_983", key=".F.082053..")

# Feature engineering
df_ml['year'] = df_ml['TIME_PERIOD'].dt.year
df_ml['rolling_mean_3y'] = df_ml['OBS_VALUE'].rolling(3).mean()
df_ml['lag_1'] = df_ml['OBS_VALUE'].shift(1)
df_ml['diff_pct'] = df_ml['OBS_VALUE'].pct_change()

# Pronto per sklearn
from sklearn.model_selection import train_test_split
# ... il tuo modello ML
```

## 📊 Dataset Popolari

| ID | Nome | Descrizione |
|----|------|-------------|
| 41_983 | Incidenti stradali | Incidenti, morti e feriti per comune |
| 115_333 | Produzione industriale | Indice produzione industriale |
| 47_850 | Prezzi al consumo | Indici prezzi al consumo NIC |
| 144_125 | Occupazione | Occupati e disoccupati |

### Come trovare altri dataset

```python
# Cerca per keyword
dataflows = client.get_dataflows()
pil = dataflows[dataflows['name_it'].str.contains('pil', case=False, na=False)]
print(pil[['id', 'name_it']])
```

## ⚙️ Struttura delle Query

### Anatomia di una chiave di filtro

Per il dataflow `41_983` (incidenti):
- Dimensioni: `FREQ.ESITO.ITTER107.TIPO_DATO.TIME_PERIOD`

```python
# Esempio: ".F.082053+072006.."
# Pos 1 (FREQ): . = tutti i valori
# Pos 2 (ESITO): F = solo feriti
# Pos 3 (ITTER107): 082053+072006 = Palermo O Bari
# Pos 4 (TIPO_DATO): . = tutti
# Pos 5 (TIME_PERIOD): gestito da start/end_period
```

### Come trovare i codici

```python
# 1. Ottieni la struttura
structure = client.get_datastructure("41_983")

# 2. Per ogni dimensione, ottieni la codelist
codelist_esito = client.get_codelist("CL_ESITO")
print(codelist_esito)
# Output: F=feriti, M=morti, I=incidenti

# 3. Oppure usa availableconstraint per vedere solo valori presenti
constraints = client.get_available_constraints("41_983")
```

## ⚠️ Limitazioni e Best Practices

### Rate Limiting
- **Limite**: 5 richieste al minuto per IP
- **Penalità**: Blocco 1-2 giorni se superato
- **Soluzione**: Il client implementa rate limiting automatico

### Gestione file grandi
```python
# ❌ NON fare: scarica tutto senza filtri
df = client.get_data("41_983")  # 53 MB!

# ✅ Meglio: applica filtri
df = client.get_data("41_983", key="..082053..", start_period="2015")
```

### Caching
```python
# Per query ripetute, salva i risultati
dataflows = client.get_dataflows()
dataflows.to_pickle("dataflows_cache.pkl")

# Ricarica da cache
dataflows = pd.read_pickle("dataflows_cache.pkl")
```

## 🔗 Risorse Utili

### Documentazione ufficiale
- [ISTAT Web Services](https://www.istat.it/it/metodi-e-strumenti/web-service-sdmx)
- [SDMX Standard](https://sdmx.org/)
- [Guida API REST ISTAT](https://ondata.github.io/guida-api-istat/)

### Endpoint
- **Nuovo (consigliato)**: `https://esploradati.istat.it/SDMXWS/rest/`
- **Vecchio**: `http://sdmx.istat.it/SDMXWS/rest/`

### Altre banche dati ISTAT
- I.Stat: database principale
- Health for All Italia: dati sanitari
- Demo.Istat: dati demografici

## 🛠️ Testing e QA

```python
# Test connessione
def test_connection():
    client = IstatSDMXClient()
    try:
        df = client.get_dataflows()
        assert len(df) > 0
        print("✅ Connessione OK")
    except Exception as e:
        print(f"❌ Errore: {e}")

test_connection()
```

## 📝 Note per Testing e Validazione

### Test automatici
```python
import pytest

def test_rate_limiting():
    """Verifica che il rate limiting funzioni"""
    client = IstatSDMXClient()
    import time
    start = time.time()
    
    for i in range(3):
        client.get_dataflows()
    
    elapsed = time.time() - start
    # Dovrebbe richiedere almeno 24 secondi (3 req * 12 sec/req)
    assert elapsed >= 24

def test_data_quality():
    """Verifica qualità dati scaricati"""
    client = IstatSDMXClient()
    df = client.get_data("41_983", key="..082053..", start_period="2015")
    
    # Verifica struttura
    assert 'OBS_VALUE' in df.columns
    assert 'TIME_PERIOD' in df.columns
    
    # Verifica valori
    assert df['OBS_VALUE'].notna().all()
    assert (df['OBS_VALUE'] >= 0).all()
```

## 🤝 Contribuire

Feedback e contributi sono benvenuti! Essendo esperto in:
- Testing e QA
- Python e data science
- Automazione

Potresti contribuire con:
- Test automatici più completi
- Validazione dati
- Ottimizzazioni performance
- Gestione errori avanzata

## 📄 Licenza

Questo codice è fornito "as is" per uso educativo e professionale.
I dati ISTAT sono soggetti alle loro condizioni d'uso.

## 🔧 Troubleshooting

### Errore 503 (Service Unavailable)
```python
# Riprova con backoff esponenziale
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

### Errore 414 (URI Too Long)
```python
# URL troppo lungo - riduci il numero di filtri
# Invece di: ".F.082053+072006+075068+..."
# Fai multiple query e unisci i risultati
```

### Timeout
```python
# Aumenta il timeout per dataset grandi
client.session.timeout = 60  # secondi
```

## 📞 Supporto

Per problemi con le API ISTAT:
- Email: dcmt-servizi@istat.it
- Web: [Contatti ISTAT](https://www.istat.it/it/contatti)

---

**Versione**: 1.0  
**Autore**: Creato per Franco  
**Data**: Novembre 2025
