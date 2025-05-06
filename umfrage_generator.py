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

# HTML-Template für die Umfrage
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Umfrage</title>
    <style>
        @font-face {
            font-family: 'DINNextLTPro-Bold';
            src: url('https://assets.rndtech.de/one/fonts/DINNextLTPro/DINNextLTPro-Bold.ttf') format('truetype');
            font-weight: 700;
        }
        
        @font-face {
            font-family: 'Inter-Regular';
            src: url('https://assets.rndtech.de/one/fonts/Inter/Inter-Regular.ttf') format('truetype');
            font-weight: 400;
        }
        
        body {
            margin: 0;
            padding: 0;
            background-color: transparent;
        }
        
        .container {
            width: 608px;
            height: 342px;
            padding: 10px 20px 10px 15px;
            box-sizing: border-box;
            background-color: white;
            position: relative;
        }
        
        .content {
            width: 100%;
            height: 100%;
            padding-left: 20px;
        }
        
        h1 {
            font-family: 'DINNextLTPro-Bold', sans-serif;
            font-weight: 700;
            font-size: 22px;
            color: #2c3e50;
            margin-top: 0;
            margin-bottom: 20px;
            line-height: 1.3;
            padding-left: 0;
        }
        
        .chart-container {
            margin-top: 10px;
            padding-right: 40px;
            padding-left: 0;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: calc(100% - 100px);
        }
        
        .chart-row {
            display: flex;
            align-items: center;
            font-family: 'Inter-Regular', sans-serif;
            height: 45px;
        }
        
        .label {
            width: 200px;
            font-size: 16px;
            text-align: left;
            padding-right: 15px;
            color: #333;
            flex-shrink: 0;
            line-height: 1.4;
        }
        
        .bar-container {
            flex-grow: 1;
            height: 45px;
            position: relative;
            margin-right: 10px;
        }
        
        .bar {
            height: 100%;
            background-color: #4e7ae8;
            position: absolute;
            left: 0;
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }
        
        .percentage {
            color: white;
            padding-right: 10px;
            font-size: 16px;
            font-weight: 500;
        }
        
        .percentage-outside {
            position: absolute;
            left: auto;
            right: -45px;
            top: 0;
            height: 100%;
            display: flex;
            align-items: center;
            color: #444;
            font-size: 16px;
            font-weight: 500;
        }
        
        .footnote {
            font-family: 'Inter-Regular', sans-serif;
            font-size: 12px;
            color: #666;
            text-align: left;
            margin-top: 25px;
            padding-left: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <h1>{title}</h1>
            
            <div class="chart-container">
{chart_rows}
            </div>
            
            <div class="footnote">Summe kann aufgrund von Rundungen von 100% abweichen.</div>
        </div>
    </div>
</body>
</html>"""

# Funktion zur Generierung der Balkendiagramm-Zeilen
def generate_chart_rows(data):
    max_value = data['Nutzer in %'].max()
    rows = []
    
    for index, row in data.iterrows():
        label = row['Bewertung']
        percentage = row['Nutzer in %']
        
        # Balkenbreite als Prozent des maximal vorhandenen Werts berechnen
        width_percent = (percentage / max_value) * 100
        
        # Wenn der Prozentwert zu niedrig ist, zeige ihn außerhalb des Balkens an
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
    
    return "\n".join(rows)

# Funktion zur Generierung einer Umfragegrafik aus CSV-Daten
def generate_chart_from_csv(csv_path, title):
    print(f"Verarbeite: {csv_path}")
    
    # CSV-Daten laden
    data = pd.read_csv(csv_path)
    
    # Chart-Zeilen generieren
    chart_rows = generate_chart_rows(data)
    
    # HTML generieren
    html_content = HTML_TEMPLATE.format(title=title, chart_rows=chart_rows)
    
    # Temporäre HTML-Datei erstellen
    with open(TEMP_HTML_PATH, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)
    
    # Dateiname für die Ausgabe erstellen
    base_name = os.path.basename(csv_path)
    output_name = os.path.splitext(base_name)[0].replace("ergebnis_", "") + ".png"
    output_path = os.path.join(EXPORT_DIR, output_name)
    
    # Screenshot mit NodeJS erstellen
    cmd = f"node screenshotter.js --width 608 --height 342 --deviceScaleFactor 4 --outputPath {output_path}"
    
    # Kopiere die HTML-Datei nach umfrage.html (für den Screenshotter)
    shutil.copy(TEMP_HTML_PATH, "umfrage.html")
    
    # Führe den Screenshot-Befehl aus
    print(f"Erstelle Screenshot: {output_path}")
    subprocess.run(cmd, shell=True)
    
    # Kurz warten, um sicherzustellen, dass der Screenshot erstellt wurde
    time.sleep(1)
    
    return output_path

# Hauptfunktion
def main():
    print(f"Durchsuche Verzeichnis: {DATA_OUT_DIR}")
    csv_files = [f for f in os.listdir(DATA_OUT_DIR) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"Keine CSV-Dateien im Verzeichnis {DATA_OUT_DIR} gefunden.")
        return
    
    print(f"{len(csv_files)} CSV-Dateien gefunden.")
    
    # Titel für die verschiedenen Umfragen
    titles = {
        "nisa": "Wie beurteilen Sie den Transfer von Jamal Musiala zu Manchester City?",
        "bb": "Hätten Sie dem Koalitionsvertrag zwischen CDU und SPD auch zugestimmt?",
        "sn": "Sollte Sachsen eine Minderheitsregierung bilden?",
        "sh": "Befürworten Sie den Umbau des Kieler Hafens zum Marinestützpunkt?",
        "mv": "Sollte die Landesregierung zurücktreten?"
    }
    
    # Verarbeite jede CSV-Datei
    for csv_file in csv_files:
        csv_path = os.path.join(DATA_OUT_DIR, csv_file)
        
        # Extrahiere den Kennzeichner aus dem Dateinamen (z.B. "nisa" aus "ergebnis_nisa.csv")
        identifier = os.path.splitext(csv_file)[0].replace("ergebnis_", "")
        
        # Wähle den passenden Titel oder verwende einen generischen
        title = titles.get(identifier, f"Umfrageergebnisse {identifier.upper()}")
        
        # Generiere die Grafik
        output_path = generate_chart_from_csv(csv_path, title)
        print(f"Grafik erstellt: {output_path}")
    
    # Lösche temporäre Dateien
    if os.path.exists(TEMP_HTML_PATH):
        os.remove(TEMP_HTML_PATH)
    
    print("Alle Grafiken wurden erstellt.")

if __name__ == "__main__":
    main() 