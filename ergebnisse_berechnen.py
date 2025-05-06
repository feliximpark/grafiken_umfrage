import pandas as pd
import os
# Zukünftiges Verhalten für replace-Funktion aktivieren
pd.set_option('future.no_silent_downcasting', True)
# Excel-Datei einlesen

xlsx_liste = ["./data_in/nisa.xlsx", "./data_in/bb.xlsx", "./data_in/sn.xlsx", "./data_in/sh.xlsx", "./data_in/mv.xlsx"]
dict_teilnehmer = {}
for xlsx in xlsx_liste:
    df = pd.read_excel(xlsx)
    überschrift = df["Unnamed: 6"][0]
    if überschrift.startswith("1. "):
        überschrift = überschrift[3:]  # Entferne "1. " am Anfang

    print(f"Identifizierte Überschrift: {überschrift}")
    # Neue Spaltennamen generieren
    new_columns = []
    for i, col in enumerate(df.columns):
        if i <= 5:
            new_columns.append(df.iloc[0, i])
        else:
            new_columns.append(df.iloc[2, i])

    # Spaltennamen setzen
    df.columns = new_columns

    # Die Hilfszeilen entfernen (Zeile 0, 1 und 2)
    df = df.iloc[3:].reset_index(drop=True)

    # Ersetze den Haken durch 1
    df = df.replace('✓', 1, inplace=False)
    df = df.astype(df.dtypes)  # Explizite Typumwandlung

    # Ersetze alle NaN-Werte durch 0
    df = df.fillna(0)

    # Liste der Bewertungs-Spalten
    herkunft_index = df.columns.get_loc("Herkunft")

    # Dann lesen wir die drei Spaltennamen nach "Herkunft" aus
    spalten_nach_herkunft = df.columns[herkunft_index+1:herkunft_index+4]
    bewertungsspalten = spalten_nach_herkunft
   
    
    # Anzahl der Nutzer (Zeilen im DataFrame)
    anzahl_nutzer = len(df)

    # Prozentuale Verteilung berechnen
    prozent_nutzer = {}
    for spalte in bewertungsspalten:
        anzahl = df[spalte].sum()
        prozent = (anzahl / anzahl_nutzer) * 100
        prozent_nutzer[spalte] = prozent

    # Neue Tabelle erstellen
    ergebnis_df = pd.DataFrame({
        "Nutzer in %": [prozent_nutzer[spalte] for spalte in bewertungsspalten]
    }, index=bewertungsspalten)

    # Ausgabe
    from decimal import Decimal, ROUND_HALF_UP
    def kaufmaennisch_runden(x):
        return float(Decimal(x).quantize(Decimal('1.0'), rounding=ROUND_HALF_UP))
    ergebnis_df["Nutzer in %"] = ergebnis_df["Nutzer in %"].apply(kaufmaennisch_runden)
    # Index zur Spalte machen
    ergebnis_df = ergebnis_df.reset_index()
    ergebnis_df = ergebnis_df.rename(columns={'index': 'Bewertung'})
    # Extrahiere den Dateinamen aus dem Pfad
    ergebnis_df["Überschrift"] = überschrift
    xlsx_pfad = xlsx  # Annahme: file_path enthält den vollständigen Pfad zur xlsx-Datei
    if "./data_in/" in xlsx_pfad:
        xlsx_name = xlsx_pfad.split("./data_in/")[1]
        xlsx_url = os.path.splitext(xlsx_name)[0]
    else:
        # Falls der Pfad nicht dem erwarteten Format entspricht
        xlsx_url = os.path.splitext(os.path.basename(xlsx_pfad))[0]
    
    dict_teilnehmer[xlsx_url] = anzahl_nutzer
    ergebnis_df.to_csv(f"./data_out/ergebnis_{xlsx_url}.csv", index=False)
    
print(dict_teilnehmer)
print("Teilnehmerzahlen:")
for key, value in dict_teilnehmer.items():
    land_dict = {"bb":"Brandenburg", "mv":"Mecklenburg-Vorpommern", "nisa":"Niedersachsen", "sn":"Sachsen", "sh":"Schleswig-Holstein"}
    print(f"{land_dict[key]}: {value}")