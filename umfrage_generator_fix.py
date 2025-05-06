import os
import pandas as pd
import subprocess
import shutil
import time

# Konfiguration
DATA_OUT_DIR = "./data_out"
TEMP_HTML_PATH = "./temp_umfrage.html"
EXPORT_DIR = "./grafiken"

# Sicherstellen, dass der Export-Ordner existiert
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

# Funktion zur Generierung der Balkendiagramm-Zeilen
def generate_chart_rows(data):
    max_value = data["Nutzer in %"].max()
    rows = []
    
    for index, row in data.iterrows():
        label = row["Bewertung"]
        percentage = row["Nutzer in %"]
        
        # Balkenbreite als Prozent des maximal vorhandenen Werts berechnen
        width_percent = (percentage / max_value) * 100
        
        # Wenn der Prozentwert zu niedrig ist, zeige ihn auﬂerhalb des Balkens an
        if width_percent < 10:
            row_html = f"""                <div class="chart-row">
                    <div class="label">{label}</div>
                    <div class="bar-container">
                        <div class="bar" style="width: {width_percent}%;">
                            <span class="percentage-outside">{percentage}%</span>
                        </div>
                    </div>
                </div>"""
        else:
            row_html = f"""                <div class="chart-row">
                    <div class="label">{label}</div>
                    <div class="bar-container">
                        <div class="bar" style="width: {width_percent}%;">
                            <span class="percentage">{percentage}%</span>
                        </div>
                    </div>
                </div>"""
        
        rows.append(row_html)
    
    return "
".join(rows)

# Funktion zur Generierung einer Umfragegrafik aus CSV-Daten
def generate_chart_from_csv(csv_path):
    print(f"Verarbeite: {csv_path}")
    
    # CSV-Daten laden
    data = pd.read_csv(csv_path)
    
    # ‹berschrift aus der ersten Zeile der CSV-Datei lesen
    title = data["‹berschrift"].iloc[0] if "‹berschrift" in data.columns and len(data) > 0 else "Umfrageergebnisse"
    
    # Chart-Zeilen generieren
    chart_rows = generate_chart_rows(data)
    