"""
Esempi avanzati di analisi dati ISTAT con pandas e visualizzazione
Per utenti con esperienza in data science
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from istat_sdmx_client import IstatSDMXClient
from typing import List, Dict
import numpy as np


class IstatDataAnalyzer:
    """
    Classe per analisi avanzate sui dati ISTAT
    """
    
    def __init__(self):
        self.client = IstatSDMXClient(log_level="INFO")
        
    def search_dataflows(self, keyword: str, lang: str = "it") -> pd.DataFrame:
        """
        Cerca dataflow per parola chiave nel nome
        
        Args:
            keyword: Parola da cercare
            lang: Lingua (it o en)
            
        Returns:
            DataFrame filtrato
        """
        df = self.client.get_dataflows()
        name_col = f"name_{lang}"
        return df[df[name_col].str.contains(keyword, case=False, na=False)]
    
    def download_timeseries(
        self,
        dataflow_id: str,
        key: str = "",
        start_year: int = None,
        end_year: int = None
    ) -> pd.DataFrame:
        """
        Scarica una serie temporale e la prepara per analisi
        
        Args:
            dataflow_id: ID del dataflow
            key: Filtri sulle dimensioni
            start_year: Anno inizio
            end_year: Anno fine
            
        Returns:
            DataFrame con TIME_PERIOD come indice datetime
        """
        df = self.client.get_data(
            dataflow_id=dataflow_id,
            key=key,
            start_period=str(start_year) if start_year else None,
            end_period=str(end_year) if end_year else None,
            format="csv"
        )
        
        # Converte TIME_PERIOD in datetime se presente
        if 'TIME_PERIOD' in df.columns:
            # Gestisce diversi formati SDMX
            df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'], errors='coerce')
            df = df.sort_values('TIME_PERIOD')
            
        # Converte OBS_VALUE in numerico
        if 'OBS_VALUE' in df.columns:
            df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
            
        return df
    
    def compare_regions(
        self,
        dataflow_id: str,
        region_codes: List[str],
        start_year: int = None,
        end_year: int = None
    ) -> pd.DataFrame:
        """
        Confronta dati tra diverse regioni/comuni
        
        Args:
            dataflow_id: ID del dataflow
            region_codes: Lista di codici territoriali
            start_year: Anno inizio
            end_year: Anno fine
            
        Returns:
            DataFrame pivot con confronto temporale
        """
        # Costruisci chiave con OR tra regioni (codici separati da +)
        key = f"..{'+'.join(region_codes)}.."
        
        df = self.download_timeseries(
            dataflow_id=dataflow_id,
            key=key,
            start_year=start_year,
            end_year=end_year
        )
        
        return df
    
    def calculate_growth_rate(self, df: pd.DataFrame, value_col: str = 'OBS_VALUE') -> pd.DataFrame:
        """
        Calcola tassi di crescita year-over-year
        
        Args:
            df: DataFrame con serie temporale
            value_col: Nome colonna valori
            
        Returns:
            DataFrame con colonna growth_rate aggiunta
        """
        df = df.copy()
        df['growth_rate'] = df[value_col].pct_change() * 100
        return df
    
    def aggregate_by_period(
        self,
        df: pd.DataFrame,
        freq: str = 'Y',
        value_col: str = 'OBS_VALUE',
        agg_func: str = 'mean'
    ) -> pd.DataFrame:
        """
        Aggrega dati per periodo (mensile -> annuale, etc.)
        
        Args:
            df: DataFrame con TIME_PERIOD come indice/colonna
            freq: Frequenza ('Y'=anno, 'Q'=trimestre, 'M'=mese)
            value_col: Colonna da aggregare
            agg_func: Funzione aggregazione (mean, sum, etc.)
            
        Returns:
            DataFrame aggregato
        """
        if 'TIME_PERIOD' not in df.index.names:
            df = df.set_index('TIME_PERIOD')
        
        return df.resample(freq)[value_col].agg(agg_func).reset_index()
    
    def detect_outliers(
        self,
        df: pd.DataFrame,
        value_col: str = 'OBS_VALUE',
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Identifica outliers nei dati
        
        Args:
            df: DataFrame
            value_col: Colonna valori
            method: Metodo ('iqr' o 'zscore')
            threshold: Soglia (1.5 per IQR, 3 per zscore)
            
        Returns:
            DataFrame con colonna 'is_outlier'
        """
        df = df.copy()
        
        if method == 'iqr':
            Q1 = df[value_col].quantile(0.25)
            Q3 = df[value_col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - threshold * IQR
            upper = Q3 + threshold * IQR
            df['is_outlier'] = (df[value_col] < lower) | (df[value_col] > upper)
            
        elif method == 'zscore':
            z_scores = np.abs((df[value_col] - df[value_col].mean()) / df[value_col].std())
            df['is_outlier'] = z_scores > threshold
            
        return df


# ============================================================================
# ESEMPI PRATICI DI ANALISI
# ============================================================================

def esempio_analisi_incidenti():
    """
    Analisi completa degli incidenti stradali in Italia
    """
    analyzer = IstatDataAnalyzer()
    
    print("\n=== ANALISI INCIDENTI STRADALI ===")
    
    # Scarica dati incidenti con feriti a Palermo e Bari
    df = analyzer.download_timeseries(
        dataflow_id="41_983",
        key=".F.082053+072006..",  # F=feriti, Palermo+Bari
        start_year=2001,
        end_year=2020
    )
    
    print(f"\nRecuperati {len(df)} record")
    print(df.head())
    
    # Calcola statistiche descrittive
    print("\n--- Statistiche descrittive ---")
    print(df['OBS_VALUE'].describe())
    
    # Calcola tassi di crescita
    df = analyzer.calculate_growth_rate(df)
    
    # Identifica outliers
    df = analyzer.detect_outliers(df, method='iqr')
    outliers = df[df['is_outlier']]
    print(f"\nIdentificati {len(outliers)} outliers")
    
    # Visualizzazione
    plt.figure(figsize=(14, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(df['TIME_PERIOD'], df['OBS_VALUE'], marker='o')
    if len(outliers) > 0:
        plt.scatter(outliers['TIME_PERIOD'], outliers['OBS_VALUE'], 
                   color='red', s=100, label='Outliers', zorder=5)
    plt.title('Incidenti con feriti - Trend temporale')
    plt.xlabel('Anno')
    plt.ylabel('Numero incidenti')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(df['TIME_PERIOD'], df['growth_rate'], marker='s', color='orange')
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    plt.title('Tasso di crescita year-over-year')
    plt.xlabel('Anno')
    plt.ylabel('Crescita (%)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('analisi_incidenti.png', dpi=300, bbox_inches='tight')
    print("\nGrafico salvato: analisi_incidenti.png")
    
    return df


def esempio_confronto_regioni():
    """
    Confronta indicatori economici tra diverse regioni
    """
    analyzer = IstatDataAnalyzer()
    
    print("\n=== CONFRONTO REGIONI ===")
    
    # Prima cerca dataflow su PIL/economia
    economic_flows = analyzer.search_dataflows("produzione industriale")
    print("\nDataflow trovati:")
    print(economic_flows)
    
    # Esempio: scarica e confronta dati
    # (qui serve conoscere i codici specifici delle regioni)
    
    return economic_flows


def esempio_pipeline_ml():
    """
    Prepara dati ISTAT per modelli di machine learning
    """
    analyzer = IstatDataAnalyzer()
    
    print("\n=== PREPARAZIONE DATI PER ML ===")
    
    # Scarica dati
    df = analyzer.download_timeseries(
        dataflow_id="41_983",
        key=".F.082053..",
        start_year=2001
    )
    
    # Feature engineering
    df['year'] = df['TIME_PERIOD'].dt.year
    df['month'] = df['TIME_PERIOD'].dt.month
    df['quarter'] = df['TIME_PERIOD'].dt.quarter
    
    # Calcola statistiche rolling
    df['rolling_mean_3y'] = df['OBS_VALUE'].rolling(window=3, min_periods=1).mean()
    df['rolling_std_3y'] = df['OBS_VALUE'].rolling(window=3, min_periods=1).std()
    
    # Lag features
    df['lag_1'] = df['OBS_VALUE'].shift(1)
    df['lag_2'] = df['OBS_VALUE'].shift(2)
    
    # Differenze
    df['diff_1'] = df['OBS_VALUE'].diff()
    df['diff_pct'] = df['OBS_VALUE'].pct_change() * 100
    
    # Rimuovi NaN
    df_ml = df.dropna()
    
    print("\nFeatures create per ML:")
    print(df_ml.columns.tolist())
    print(f"\nDataset finale: {df_ml.shape}")
    print(df_ml.head(10))
    
    # Salva dataset per ML
    df_ml.to_csv('dataset_ml_ready.csv', index=False)
    print("\nDataset salvato: dataset_ml_ready.csv")
    
    # Matrice di correlazione
    numeric_cols = df_ml.select_dtypes(include=[np.number]).columns
    correlation_matrix = df_ml[numeric_cols].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0)
    plt.title('Matrice di correlazione - Features')
    plt.tight_layout()
    plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
    print("Matrice correlazione salvata: correlation_matrix.png")
    
    return df_ml


def esempio_batch_download():
    """
    Download batch di multiple serie temporali
    """
    analyzer = IstatDataAnalyzer()
    
    print("\n=== BATCH DOWNLOAD ===")
    
    # Lista di dataflow da scaricare
    dataflows_of_interest = [
        ("41_983", "incidenti_stradali"),
        ("115_333", "produzione_industriale"),
        # Aggiungi altri...
    ]
    
    datasets = {}
    
    for flow_id, name in dataflows_of_interest:
        try:
            print(f"\nScarico: {name} ({flow_id})...")
            df = analyzer.client.get_data(
                dataflow_id=flow_id,
                format="csv"
            )
            datasets[name] = df
            
            # Salva su file
            filename = f"data_{name}.csv"
            df.to_csv(filename, index=False)
            print(f"Salvato: {filename}")
            
        except Exception as e:
            print(f"Errore con {name}: {e}")
    
    print(f"\nScaricati {len(datasets)} dataset")
    return datasets


# ============================================================================
# ESECUZIONE ESEMPI
# ============================================================================

if __name__ == "__main__":
    
    # Esegui analisi completa
    try:
        df_incidenti = esempio_analisi_incidenti()
    except Exception as e:
        print(f"Errore analisi incidenti: {e}")
    
    try:
        flows = esempio_confronto_regioni()
    except Exception as e:
        print(f"Errore confronto regioni: {e}")
    
    try:
        df_ml = esempio_pipeline_ml()
    except Exception as e:
        print(f"Errore pipeline ML: {e}")
    
    print("\n=== ANALISI COMPLETATE ===")
