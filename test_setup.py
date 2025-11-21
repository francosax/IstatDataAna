"""
Test rapido per verificare funzionamento client ISTAT SDMX
Esegui questo script per validare l'installazione e la connettività
"""

import sys
from datetime import datetime


def test_imports():
    """Test 1: Verifica imports dipendenze"""
    print("\n[TEST 1] Verifica imports...")
    
    try:
        import requests
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✓ Tutte le dipendenze sono installate correttamente")
        return True
    except ImportError as e:
        print(f"❌ Errore import: {e}")
        print("Esegui: pip install -r requirements.txt")
        return False


def test_client_init():
    """Test 2: Inizializzazione client"""
    print("\n[TEST 2] Inizializzazione client...")
    
    try:
        from istat_sdmx_client import IstatSDMXClient
        client = IstatSDMXClient(log_level="WARNING")
        print("✓ Client inizializzato correttamente")
        return True, client
    except Exception as e:
        print(f"❌ Errore inizializzazione: {e}")
        return False, None


def test_connectivity(client):
    """Test 3: Connettività API"""
    print("\n[TEST 3] Test connettività API ISTAT...")
    
    try:
        # Prova una query semplice
        dataflows = client.get_dataflows()
        
        if len(dataflows) > 0:
            print(f"✓ Connessione OK - Trovati {len(dataflows)} dataflow")
            print(f"  Primi 3 dataflow:")
            for i, row in dataflows.head(3).iterrows():
                print(f"  - {row['id']}: {row['name_it']}")
            return True
        else:
            print("⚠ Connessione OK ma nessun dataflow trovato")
            return False
            
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return False


def test_data_download(client):
    """Test 4: Download dati di esempio"""
    print("\n[TEST 4] Test download dati...")
    
    try:
        # Prova a scaricare un piccolo dataset
        # Incidenti a Palermo, solo 2020
        df = client.get_data(
            dataflow_id="41_983",
            key="..082053..",  # Palermo
            start_period="2020",
            end_period="2020",
            format="csv"
        )
        
        if len(df) > 0:
            print(f"✓ Download completato - {len(df)} record")
            print(f"  Colonne: {df.columns.tolist()}")
            print(f"  Primi valori OBS_VALUE: {df['OBS_VALUE'].head(3).tolist()}")
            return True
        else:
            print("⚠ Download OK ma dataset vuoto")
            return False
            
    except Exception as e:
        print(f"❌ Errore download: {e}")
        return False


def test_codelist(client):
    """Test 5: Recupero codelist"""
    print("\n[TEST 5] Test recupero codelist...")
    
    try:
        freq_codes = client.get_codelist("CL_FREQ")
        
        if len(freq_codes) > 0:
            print(f"✓ Codelist recuperata - {len(freq_codes)} codici")
            print(f"  Esempi: {freq_codes['id'].head(3).tolist()}")
            return True
        else:
            print("⚠ Codelist vuota")
            return False
            
    except Exception as e:
        print(f"❌ Errore recupero codelist: {e}")
        return False


def run_all_tests():
    """Esegue tutti i test"""
    print("="*70)
    print("TEST SUITE - ISTAT SDMX CLIENT")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    if not results[-1][1]:
        print("\n❌ Test imports fallito - interrompo test suite")
        return False
    
    # Test 2: Client init
    success, client = test_client_init()
    results.append(("Client Init", success))
    
    if not success:
        print("\n❌ Test client init fallito - interrompo test suite")
        return False
    
    # Test 3: Connectivity
    results.append(("Connectivity", test_connectivity(client)))
    
    # Test 4: Data download
    results.append(("Data Download", test_data_download(client)))
    
    # Test 5: Codelist
    results.append(("Codelist", test_codelist(client)))
    
    # Sommario risultati
    print("\n" + "="*70)
    print("SOMMARIO RISULTATI")
    print("="*70)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<50} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    success_rate = (total_passed / total_tests) * 100
    
    print("\n" + "-"*70)
    print(f"Risultato: {total_passed}/{total_tests} test passati ({success_rate:.0f}%)")
    print("-"*70)
    
    if total_passed == total_tests:
        print("\n🎉 TUTTI I TEST PASSATI! Setup completato con successo.")
        print("\nPuoi ora utilizzare il client per le tue analisi:")
        print("  from istat_sdmx_client import IstatSDMXClient")
        print("  client = IstatSDMXClient()")
        print("  df = client.get_dataflows()")
        return True
    else:
        print("\n⚠ ALCUNI TEST FALLITI")
        print("Controlla gli errori sopra e verifica:")
        print("  - Installazione dipendenze (pip install -r requirements.txt)")
        print("  - Connessione internet")
        print("  - Firewall/proxy settings")
        return False


def quick_validation():
    """Validazione rapida (solo connectivity)"""
    print("="*70)
    print("VALIDAZIONE RAPIDA")
    print("="*70)
    
    try:
        from istat_sdmx_client import IstatSDMXClient
        client = IstatSDMXClient(log_level="WARNING")
        
        print("\nTest connettività API...")
        dataflows = client.get_dataflows()
        
        print(f"✓ Connessione OK")
        print(f"✓ API funzionante")
        print(f"✓ {len(dataflows)} dataflow disponibili")
        
        print("\n🎉 Setup validato con successo!")
        return True
        
    except Exception as e:
        print(f"\n❌ Validazione fallita: {e}")
        return False


if __name__ == "__main__":
    
    # Controlla argomenti
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Validazione rapida
        success = quick_validation()
    else:
        # Test completi
        success = run_all_tests()
    
    # Exit code
    sys.exit(0 if success else 1)
