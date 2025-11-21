#!/usr/bin/env python3
"""
QUICK START - ISTAT SDMX API
=============================

Script di esempio rapido per iniziare subito con le API ISTAT.
Esegui semplicemente questo file per vedere il client in azione!

Uso:
    python quickstart.py
"""

from istat_sdmx_client import IstatSDMXClient
import pandas as pd


def esempio_veloce():
    """
    Esempio rapido: scarica dati incidenti stradali Bologna 2015-2020
    """
    print("\n" + "="*70)
    print("QUICK START - Esempio pratico")
    print("="*70)
    
    # 1. Crea il client
    print("\n[1] Inizializzazione client...")
    client = IstatSDMXClient(log_level="INFO")
    print("✓ Client pronto\n")
    
    # 2. Scarica i dati
    print("[2] Download dati incidenti stradali Bologna 2015-2020...")
    
    df = client.get_data(
        dataflow_id="41_983",          # ID dataset incidenti
        key="..037006..",               # 037006 = codice ISTAT Bologna
        start_period="2015",            # Dal 2015
        end_period="2020",              # Al 2020
        format="csv"                    # Formato CSV
    )
    
    print(f"✓ Scaricati {len(df)} record\n")
    
    # 3. Mostra i dati
    print("[3] Prime righe dataset:")
    print(df.head(10))
    
    # 4. Statistiche rapide
    print("\n[4] Statistiche descrittive:")
    print(df['OBS_VALUE'].describe())
    
    # 5. Salva risultati
    output_file = "incidenti_bologna_quick.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✓ Dati salvati in: {output_file}")
    
    print("\n" + "="*70)
    print("COMPLETATO!")
    print("="*70)
    print("\nProssimi passi:")
    print("1. Leggi README.md per la documentazione completa")
    print("2. Esplora istat_advanced_analysis.py per esempi avanzati")
    print("3. Guarda esempio_completo_analisi.py per un caso d'uso reale")
    
    return df


def esplora_dataset_disponibili():
    """
    Esplora i dataset disponibili
    """
    print("\n" + "="*70)
    print("ESPLORAZIONE DATASET DISPONIBILI")
    print("="*70)
    
    client = IstatSDMXClient(log_level="WARNING")
    
    print("\n[1] Recupero lista dataflow...")
    dataflows = client.get_dataflows()
    print(f"✓ Trovati {len(dataflows)} dataset disponibili")
    
    print("\n[2] Cerca dataset per keyword...")
    keyword = input("Inserisci una parola chiave (es: 'produzione', 'occupazione', 'prezzi'): ")
    
    if keyword:
        risultati = dataflows[
            dataflows['name_it'].str.contains(keyword, case=False, na=False)
        ]
        
        if len(risultati) > 0:
            print(f"\n✓ Trovati {len(risultati)} dataset corrispondenti:\n")
            for i, row in risultati.head(10).iterrows():
                print(f"ID: {row['id']}")
                print(f"Nome: {row['name_it']}")
                print("-" * 60)
        else:
            print(f"\nNessun risultato per '{keyword}'")
    
    return dataflows


def menu_interattivo():
    """
    Menu interattivo per esplorare le API
    """
    while True:
        print("\n" + "="*70)
        print("MENU QUICK START")
        print("="*70)
        print("\n1. Esegui esempio veloce (incidenti Bologna)")
        print("2. Esplora dataset disponibili")
        print("3. Esci")
        
        scelta = input("\nScegli un'opzione (1-3): ").strip()
        
        if scelta == "1":
            esempio_veloce()
        elif scelta == "2":
            esplora_dataset_disponibili()
        elif scelta == "3":
            print("\nArrivederci!")
            break
        else:
            print("\n⚠ Opzione non valida")


def main():
    """
    Entry point principale
    """
    print("\n" + "█"*70)
    print(" "*20 + "ISTAT SDMX API - QUICK START")
    print("█"*70)
    
    # Verifica che il modulo sia importabile
    try:
        from istat_sdmx_client import IstatSDMXClient
    except ImportError:
        print("\n❌ ERRORE: modulo istat_sdmx_client non trovato!")
        print("\nAssicurati che il file istat_sdmx_client.py sia nella stessa cartella.")
        print("Altrimenti copia i file nella directory corrente.")
        return
    
    # Verifica dipendenze
    try:
        import requests
        import pandas
    except ImportError as e:
        print(f"\n❌ ERRORE: dipendenza mancante - {e}")
        print("\nEsegui: pip install -r requirements.txt")
        return
    
    print("\n✓ Tutto pronto!")
    
    # Chiedi all'utente cosa vuole fare
    print("\nCosa vuoi fare?")
    print("1. Esegui subito l'esempio veloce")
    print("2. Apri menu interattivo")
    
    scelta = input("\nScegli (1 o 2): ").strip()
    
    if scelta == "1":
        esempio_veloce()
    elif scelta == "2":
        menu_interattivo()
    else:
        print("\nEseguo esempio di default...")
        esempio_veloce()


if __name__ == "__main__":
    main()
