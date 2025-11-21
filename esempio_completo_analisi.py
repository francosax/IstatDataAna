"""
CASO D'USO COMPLETO: Analisi Incidenti Stradali in Emilia-Romagna
===================================================================

Esempio end-to-end di utilizzo delle API ISTAT per:
1. Esplorare i dati disponibili
2. Scaricare dati storici
3. Pulire e validare i dati
4. Analisi esplorativa
5. Visualizzazioni avanzate
6. Export per reporting

Target: Head of Testing con background data science
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from istat_sdmx_client import IstatSDMXClient

# Configurazione plot
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


# ============================================================================
# STEP 1: ESPLORAZIONE DATAFLOW
# ============================================================================

def step1_explore_dataflows():
    """
    Trova dataflow rilevanti per analisi incidenti stradali
    """
    print("="*80)
    print("STEP 1: ESPLORAZIONE DATAFLOW DISPONIBILI")
    print("="*80)
    
    client = IstatSDMXClient(log_level="WARNING")
    
    # Scarica tutti i dataflow
    print("\n[1.1] Recupero lista completa dataflow...")
    all_dataflows = client.get_dataflows()
    print(f"✓ Trovati {len(all_dataflows)} dataflow totali")
    
    # Filtra per keyword rilevanti
    keywords = ['inciden', 'strada', 'traffic']
    
    print("\n[1.2] Filtraggio per keywords rilevanti...")
    relevant_flows = pd.DataFrame()
    
    for keyword in keywords:
        mask = (
            all_dataflows['name_it'].str.contains(keyword, case=False, na=False) |
            all_dataflows['name_en'].str.contains(keyword, case=False, na=False)
        )
        relevant_flows = pd.concat([relevant_flows, all_dataflows[mask]]).drop_duplicates()
    
    print(f"✓ Trovati {len(relevant_flows)} dataflow rilevanti")
    print("\nDataflow identificati:")
    print(relevant_flows[['id', 'name_it', 'name_en']].to_string())
    
    # Salva per riferimento
    relevant_flows.to_csv('dataflows_incidenti.csv', index=False)
    print("\n✓ Salvato: dataflows_incidenti.csv")
    
    return relevant_flows


# ============================================================================
# STEP 2: ANALISI STRUTTURA DATI
# ============================================================================

def step2_analyze_structure():
    """
    Analizza la struttura del dataflow 41_983 (incidenti per comune)
    """
    print("\n" + "="*80)
    print("STEP 2: ANALISI STRUTTURA DATI")
    print("="*80)
    
    client = IstatSDMXClient(log_level="WARNING")
    
    dataflow_id = "41_983"  # Incidenti, morti e feriti - comuni
    
    print(f"\n[2.1] Analisi dataflow: {dataflow_id}")
    
    # Ottieni dimensioni disponibili
    print("\n[2.2] Recupero vincoli (valori disponibili)...")
    try:
        constraints = client.get_available_constraints(dataflow_id)
        print("✓ Vincoli ottenuti")
    except Exception as e:
        print(f"⚠ Vincoli non disponibili: {e}")
    
    # Ottieni codelists rilevanti
    print("\n[2.3] Analisi codelists principali...")
    
    codelists_info = {}
    
    # FREQ - Frequenza
    try:
        cl_freq = client.get_codelist("CL_FREQ")
        codelists_info['FREQ'] = cl_freq
        print("\n✓ Codelist FREQ (Frequenza):")
        print(cl_freq.to_string())
    except Exception as e:
        print(f"⚠ FREQ: {e}")
    
    # ESITO - Tipo esito incidente
    try:
        cl_esito = client.get_codelist("CL_ESITO")
        codelists_info['ESITO'] = cl_esito
        print("\n✓ Codelist ESITO (Tipo esito):")
        print(cl_esito.to_string())
    except Exception as e:
        print(f"⚠ ESITO: {e}")
    
    return codelists_info


# ============================================================================
# STEP 3: DOWNLOAD DATI EMILIA-ROMAGNA
# ============================================================================

def step3_download_data():
    """
    Scarica dati storici incidenti per comuni principali Emilia-Romagna
    """
    print("\n" + "="*80)
    print("STEP 3: DOWNLOAD DATI EMILIA-ROMAGNA")
    print("="*80)
    
    client = IstatSDMXClient(log_level="WARNING")
    
    # Codici ISTAT comuni principali Emilia-Romagna
    comuni_er = {
        '037006': 'Bologna',
        '099014': 'Modena',
        '035036': 'Reggio Emilia',
        '033039': 'Parma',
        '038013': 'Ferrara',
        '040030': 'Ravenna',
        '040010': 'Forlì',
        '040024': 'Rimini',
        '034032': 'Piacenza'
    }
    
    print(f"\n[3.1] Download dati per {len(comuni_er)} comuni...")
    print(f"Comuni: {', '.join(comuni_er.values())}")
    
    # Costruisci key per multiple comuni
    codici_comuni = '+'.join(comuni_er.keys())
    
    # Download dati: tutti gli esiti, tutti i comuni
    # Key: FREQ.ESITO.ITTER107.TIPO_DATO
    # ..: tutti i valori per FREQ e ESITO
    # codici_comuni: filtro sui comuni
    # .: tutti i valori TIPO_DATO
    
    print("\n[3.2] Esecuzione query API...")
    key = f"..{codici_comuni}.."
    
    df = client.get_data(
        dataflow_id="41_983",
        key=key,
        start_period="2001",
        end_period="2023",
        format="csv"
    )
    
    print(f"✓ Scaricati {len(df)} record")
    print(f"Periodo: {df['TIME_PERIOD'].min()} - {df['TIME_PERIOD'].max()}")
    
    # Aggiungi nomi comuni
    df['COMUNE'] = df['ITTER107'].map(comuni_er)
    
    # Salva raw data
    df.to_csv('incidenti_emilia_romagna_raw.csv', index=False)
    print("\n✓ Salvato: incidenti_emilia_romagna_raw.csv")
    
    # Info dataset
    print("\n[3.3] Info dataset:")
    print(f"Shape: {df.shape}")
    print(f"\nColonne: {df.columns.tolist()}")
    print(f"\nEsiti unici: {df['ESITO'].unique()}")
    print(f"\nPeriodo copertura: {df['TIME_PERIOD'].nunique()} anni")
    
    return df


# ============================================================================
# STEP 4: DATA CLEANING E VALIDAZIONE
# ============================================================================

def step4_clean_and_validate(df):
    """
    Pulizia dati e controlli di qualità
    """
    print("\n" + "="*80)
    print("STEP 4: DATA CLEANING E VALIDAZIONE")
    print("="*80)
    
    df_clean = df.copy()
    
    print("\n[4.1] Controllo valori mancanti...")
    missing = df_clean.isnull().sum()
    print(missing[missing > 0])
    
    if missing.sum() == 0:
        print("✓ Nessun valore mancante")
    
    print("\n[4.2] Conversione tipi dati...")
    # Converti TIME_PERIOD in datetime
    df_clean['TIME_PERIOD'] = pd.to_datetime(df_clean['TIME_PERIOD'])
    df_clean['ANNO'] = df_clean['TIME_PERIOD'].dt.year
    
    # Converti OBS_VALUE in numerico
    df_clean['OBS_VALUE'] = pd.to_numeric(df_clean['OBS_VALUE'], errors='coerce')
    
    print("✓ Conversioni completate")
    
    print("\n[4.3] Validazione range valori...")
    # I valori non dovrebbero essere negativi
    negative_values = df_clean[df_clean['OBS_VALUE'] < 0]
    if len(negative_values) > 0:
        print(f"⚠ Trovati {len(negative_values)} valori negativi (anomali)")
    else:
        print("✓ Nessun valore negativo")
    
    # Outliers detection
    print("\n[4.4] Rilevamento outliers (metodo IQR)...")
    Q1 = df_clean['OBS_VALUE'].quantile(0.25)
    Q3 = df_clean['OBS_VALUE'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df_clean[
        (df_clean['OBS_VALUE'] < lower_bound) | 
        (df_clean['OBS_VALUE'] > upper_bound)
    ]
    
    print(f"Identificati {len(outliers)} outliers potenziali")
    print(f"Range normale: [{lower_bound:.0f}, {upper_bound:.0f}]")
    
    if len(outliers) > 0:
        print("\nOutliers principali:")
        print(outliers.nlargest(5, 'OBS_VALUE')[
            ['ANNO', 'COMUNE', 'ESITO', 'OBS_VALUE']
        ].to_string())
    
    print("\n[4.5] Statistiche descrittive:")
    print(df_clean.groupby('ESITO')['OBS_VALUE'].describe())
    
    # Salva dataset pulito
    df_clean.to_csv('incidenti_emilia_romagna_clean.csv', index=False)
    print("\n✓ Salvato: incidenti_emilia_romagna_clean.csv")
    
    return df_clean


# ============================================================================
# STEP 5: ANALISI ESPLORATIVA
# ============================================================================

def step5_exploratory_analysis(df):
    """
    Analisi esplorativa dei dati
    """
    print("\n" + "="*80)
    print("STEP 5: ANALISI ESPLORATIVA")
    print("="*80)
    
    # Aggrega per anno e comune
    print("\n[5.1] Trend temporale per comune...")
    trend_comune = df.groupby(['ANNO', 'COMUNE', 'ESITO'])['OBS_VALUE'].sum().reset_index()
    
    # Trend totale Emilia-Romagna
    print("\n[5.2] Trend totale regionale...")
    trend_regionale = df.groupby(['ANNO', 'ESITO'])['OBS_VALUE'].sum().reset_index()
    
    # Statistiche per esito
    print("\n[5.3] Analisi per tipo esito:")
    stats_esito = df.groupby('ESITO')['OBS_VALUE'].agg([
        ('totale', 'sum'),
        ('media_annua', 'mean'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max')
    ]).round(2)
    print(stats_esito)
    
    # Ranking comuni
    print("\n[5.4] Ranking comuni per numero incidenti totali:")
    ranking = df.groupby('COMUNE')['OBS_VALUE'].sum().sort_values(ascending=False)
    print(ranking)
    
    # Variazione temporale
    print("\n[5.5] Variazione percentuale 2001-2020:")
    anni_confronto = df[df['ANNO'].isin([2001, 2020])]
    
    if len(anni_confronto) > 0:
        pivot_variazione = anni_confronto.pivot_table(
            values='OBS_VALUE',
            index=['COMUNE', 'ESITO'],
            columns='ANNO',
            aggfunc='sum'
        )
        
        if 2001 in pivot_variazione.columns and 2020 in pivot_variazione.columns:
            pivot_variazione['variazione_%'] = (
                (pivot_variazione[2020] - pivot_variazione[2001]) / 
                pivot_variazione[2001] * 100
            ).round(2)
            
            print(pivot_variazione.sort_values('variazione_%'))
    
    return trend_comune, trend_regionale, stats_esito


# ============================================================================
# STEP 6: VISUALIZZAZIONI
# ============================================================================

def step6_visualizations(df, trend_regionale):
    """
    Crea visualizzazioni comprehensive
    """
    print("\n" + "="*80)
    print("STEP 6: GENERAZIONE VISUALIZZAZIONI")
    print("="*80)
    
    # === GRAFICO 1: Trend temporale regionale ===
    print("\n[6.1] Creazione grafico trend regionale...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Trend per esito
    ax1 = axes[0, 0]
    for esito in trend_regionale['ESITO'].unique():
        data = trend_regionale[trend_regionale['ESITO'] == esito]
        ax1.plot(data['ANNO'], data['OBS_VALUE'], marker='o', label=esito, linewidth=2)
    
    ax1.set_title('Trend Incidenti Emilia-Romagna per Esito', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Anno')
    ax1.set_ylabel('Numero Eventi')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Distribuzione per comune (ultimi 5 anni)
    ax2 = axes[0, 1]
    df_recent = df[df['ANNO'] >= 2016]
    comune_totals = df_recent.groupby('COMUNE')['OBS_VALUE'].sum().sort_values()
    comune_totals.plot(kind='barh', ax=ax2, color='steelblue')
    ax2.set_title('Totale Incidenti per Comune (2016-2020)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Numero Eventi')
    
    # Plot 3: Heatmap anno x comune
    ax3 = axes[1, 0]
    pivot_heatmap = df.pivot_table(
        values='OBS_VALUE',
        index='COMUNE',
        columns='ANNO',
        aggfunc='sum'
    )
    sns.heatmap(pivot_heatmap, cmap='YlOrRd', ax=ax3, cbar_kws={'label': 'N. Eventi'})
    ax3.set_title('Heatmap Temporale Comuni', fontsize=14, fontweight='bold')
    
    # Plot 4: Box plot distribuzione per esito
    ax4 = axes[1, 1]
    df.boxplot(column='OBS_VALUE', by='ESITO', ax=ax4)
    ax4.set_title('Distribuzione Valori per Esito', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Tipo Esito')
    ax4.set_ylabel('Numero Eventi')
    plt.suptitle('')  # Rimuove titolo automatico boxplot
    
    plt.tight_layout()
    plt.savefig('analisi_incidenti_er_comprehensive.png', dpi=300, bbox_inches='tight')
    print("✓ Salvato: analisi_incidenti_er_comprehensive.png")
    
    # === GRAFICO 2: Focus Bologna ===
    print("\n[6.2] Creazione grafico focus Bologna...")
    
    df_bologna = df[df['COMUNE'] == 'Bologna']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Trend Bologna
    ax1 = axes[0]
    bologna_trend = df_bologna.groupby(['ANNO', 'ESITO'])['OBS_VALUE'].sum().reset_index()
    for esito in bologna_trend['ESITO'].unique():
        data = bologna_trend[bologna_trend['ESITO'] == esito]
        ax1.plot(data['ANNO'], data['OBS_VALUE'], marker='s', label=esito, linewidth=2)
    
    ax1.set_title('Trend Incidenti Stradali - Bologna', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Anno')
    ax1.set_ylabel('Numero Eventi')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Distribuzione per esito
    ax2 = axes[1]
    esito_totals = df_bologna.groupby('ESITO')['OBS_VALUE'].sum()
    colors = sns.color_palette('Set2', len(esito_totals))
    esito_totals.plot(kind='pie', ax=ax2, autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title('Distribuzione per Tipo Esito - Bologna', fontsize=14, fontweight='bold')
    ax2.set_ylabel('')
    
    plt.tight_layout()
    plt.savefig('analisi_incidenti_bologna.png', dpi=300, bbox_inches='tight')
    print("✓ Salvato: analisi_incidenti_bologna.png")
    
    plt.close('all')


# ============================================================================
# STEP 7: REPORT FINALE
# ============================================================================

def step7_generate_report(df, stats_esito):
    """
    Genera report testuale di sintesi
    """
    print("\n" + "="*80)
    print("STEP 7: GENERAZIONE REPORT FINALE")
    print("="*80)
    
    report = []
    report.append("="*80)
    report.append("REPORT ANALISI INCIDENTI STRADALI - EMILIA-ROMAGNA")
    report.append("="*80)
    report.append(f"\nData generazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\nPeriodo analisi: {df['ANNO'].min()} - {df['ANNO'].max()}")
    report.append(f"Comuni analizzati: {df['COMUNE'].nunique()}")
    report.append(f"Record totali: {len(df):,}")
    
    report.append("\n" + "-"*80)
    report.append("STATISTICHE PRINCIPALI")
    report.append("-"*80)
    
    report.append(f"\nTotale eventi periodo: {df['OBS_VALUE'].sum():,.0f}")
    report.append(f"Media annua: {df.groupby('ANNO')['OBS_VALUE'].sum().mean():,.0f}")
    report.append(f"Picco massimo annuale: {df.groupby('ANNO')['OBS_VALUE'].sum().max():,.0f}")
    report.append(f"Minimo annuale: {df.groupby('ANNO')['OBS_VALUE'].sum().min():,.0f}")
    
    report.append("\n" + "-"*80)
    report.append("STATISTICHE PER TIPO ESITO")
    report.append("-"*80)
    report.append("\n" + stats_esito.to_string())
    
    report.append("\n" + "-"*80)
    report.append("RANKING COMUNI (Top 5)")
    report.append("-"*80)
    top_comuni = df.groupby('COMUNE')['OBS_VALUE'].sum().nlargest(5)
    for i, (comune, valore) in enumerate(top_comuni.items(), 1):
        report.append(f"{i}. {comune}: {valore:,.0f} eventi")
    
    report.append("\n" + "-"*80)
    report.append("TREND TEMPORALE")
    report.append("-"*80)
    
    trend_annuale = df.groupby('ANNO')['OBS_VALUE'].sum()
    variazione_totale = ((trend_annuale.iloc[-1] - trend_annuale.iloc[0]) / 
                        trend_annuale.iloc[0] * 100)
    
    report.append(f"\nVariazione totale periodo: {variazione_totale:+.1f}%")
    report.append(f"Anno con più eventi: {trend_annuale.idxmax()} ({trend_annuale.max():,.0f})")
    report.append(f"Anno con meno eventi: {trend_annuale.idxmin()} ({trend_annuale.min():,.0f})")
    
    report.append("\n" + "="*80)
    report.append("CONCLUSIONI")
    report.append("="*80)
    report.append("\n- Dati scaricati da ISTAT via API SDMX REST")
    report.append("- Analisi copre " + str(df['ANNO'].nunique()) + " anni di storico")
    report.append("- Dataset validato e pulito con successo")
    report.append("- Visualizzazioni generate per insight immediati")
    
    report.append("\n" + "="*80)
    report.append("FILE GENERATI")
    report.append("="*80)
    report.append("\n- incidenti_emilia_romagna_raw.csv")
    report.append("- incidenti_emilia_romagna_clean.csv")
    report.append("- analisi_incidenti_er_comprehensive.png")
    report.append("- analisi_incidenti_bologna.png")
    report.append("- report_analisi_incidenti.txt")
    
    report_text = '\n'.join(report)
    
    # Salva report
    with open('report_analisi_incidenti.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print("\n✓ Salvato: report_analisi_incidenti.txt")
    
    # Stampa a video
    print("\n" + report_text)
    
    return report_text


# ============================================================================
# MAIN - ESECUZIONE PIPELINE COMPLETA
# ============================================================================

def main():
    """
    Esegue pipeline completa di analisi
    """
    print("\n" + "█"*80)
    print("PIPELINE ANALISI INCIDENTI STRADALI EMILIA-ROMAGNA")
    print("Utilizzo API SDMX ISTAT")
    print("█"*80)
    
    try:
        # Step 1: Esplora dataflows
        dataflows = step1_explore_dataflows()
        
        # Step 2: Analizza struttura
        codelists = step2_analyze_structure()
        
        # Step 3: Download dati
        df_raw = step3_download_data()
        
        # Step 4: Pulizia e validazione
        df_clean = step4_clean_and_validate(df_raw)
        
        # Step 5: Analisi esplorativa
        trend_comune, trend_regionale, stats_esito = step5_exploratory_analysis(df_clean)
        
        # Step 6: Visualizzazioni
        step6_visualizations(df_clean, trend_regionale)
        
        # Step 7: Report finale
        report = step7_generate_report(df_clean, stats_esito)
        
        print("\n" + "█"*80)
        print("PIPELINE COMPLETATA CON SUCCESSO!")
        print("█"*80)
        
        return df_clean, report
        
    except Exception as e:
        print(f"\n❌ ERRORE DURANTE L'ESECUZIONE: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    df_risultati, report_finale = main()
