#!/bin/bash

# Zunächst ergebnisse_berechnen.py ausführen
echo "Führe ergebnisse_berechnen.py aus..."
python ergebnisse_berechnen.py
echo "Berechnungen abgeschlossen."

# Verzeichnis für die Ausgabe erstellen
mkdir -p ./grafiken

# Aktuelles Datum im Format YYYYMMDD mit Python ermitteln (plattformunabhängig)
current_date=$(python -c "import datetime; print(datetime.datetime.now().strftime('%Y%m%d'))")

# Debug-Ausgabe des Datums
echo "Verwende Datum für Dateinamen: $current_date"

for csv in ./data_out/*.csv; do
  filename=$(basename "$csv")
  identifier=${filename%.csv}
  identifier=${identifier#ergebnis_}
  
  # Neuer Dateiname im Format YYYYMMDD_KENNUNG_Umfrage_Newsletter.png
  output_filename="${current_date}_${identifier^^}_Umfrage_Newsletter.png"
  output="./grafiken/$output_filename"
  
  echo "Verarbeite $csv -> $output"
  
  # Überschrift und Daten aus CSV lesen und in HTML einfügen
  python -c "
import pandas as pd
import re
import json

# CSV-Datei einlesen
data = pd.read_csv('$csv')

# Überschrift aus der CSV-Datei extrahieren
title = data['Überschrift'].iloc[0] if 'Überschrift' in data.columns else 'Umfrage'
print(f'Verwende Überschrift: {title}')

# HTML-Vorlage öffnen und Überschrift ersetzen
with open('umfrage.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'<h1>(.*?)</h1>', f'<h1>{title}</h1>', html)

# Alte Balken-Elemente entfernen
chart_container_start = html.find('<div class=\"chart-container\">')
chart_container_end = html.find('<div class=\"footnote\">', chart_container_start)
chart_container_content = html[chart_container_start:chart_container_end]

# Neue Balken erstellen
new_chart_content = '<div class=\"chart-container\">'

# Maximalen Prozentwert finden für die Balkenbreite
max_percentage = data['Nutzer in %'].max()

# Prüfen, ob lange Beschriftungen vorhanden sind (>25 Zeichen)
has_long_labels = any(len(str(label)) > 25 for label in data['Bewertung'] if pd.notna(label))
label_font_size = 16 if has_long_labels else 18  # 2px kleiner, wenn lange Labels vorhanden sind

# Debug-Ausgabe zu langen Labels
if has_long_labels:
    print(f'Verwende kleinere Schrift (16px) für Labels, da lange Beschriftungen vorhanden sind')

# Speziellen Stil für die Label-Container setzen
label_width = 120 if has_long_labels else 110  # Breiterer Container für lange Labels

# Für jede Zeile in der CSV-Datei einen Balken erstellen
row_count = len(data)
print(f'Anzahl der Zeilen im DataFrame: {row_count}')

# Spezielle Positionierung bei nur zwei Zeilen
special_positioning = row_count == 2

for index, row in data.iterrows():
    if pd.notna(row['Bewertung']) and pd.notna(row['Nutzer in %']):
        label = row['Bewertung']
        percentage = float(row['Nutzer in %'])
        width_percent = (percentage / max_percentage) * 100 if max_percentage > 0 else 0
        
        # Prozentangabe mit Komma statt Punkt formatieren
        percentage_display = str(percentage).replace('.', ',')
        
        # Spezielle Stil-Anpassungen für nur zwei Zeilen
        special_style = ''
        if special_positioning:
            if index == 0:  # Erste Zeile 40px nach unten
                special_style = 'margin-top: 40px;'
                print(f'Verschiebe erste Zeile ({label}) 40px nach unten')
            elif index == 1:  # Zweite Zeile 60px nach oben
                special_style = 'margin-top: -60px;'
                print(f'Verschiebe zweite Zeile ({label}) 60px nach oben')
        
        # Prüfen, ob die Prozentangabe innerhalb oder außerhalb des Balkens angezeigt werden soll
        if width_percent > 18:  # Erhöhter Schwellenwert für größere Schrift (vorher 15)
            new_chart_content += f'''
                <div class=\"chart-row\" style=\"{special_style}\">
                    <div class=\"label\" style=\"font-size: {label_font_size}px; width: {label_width}px;\">{label}</div>
                    <div class=\"bar-container\">
                        <div class=\"bar\" style=\"width: {width_percent}%;\">
                            <span class=\"percentage\">{percentage_display}%</span>
                        </div>
                    </div>
                </div>
            '''
        else:  # Wenn Balken zu schmal ist, Text außerhalb anzeigen
            new_chart_content += f'''
                <div class=\"chart-row\" style=\"{special_style}\">
                    <div class=\"label\" style=\"font-size: {label_font_size}px; width: {label_width}px;\">{label}</div>
                    <div class=\"bar-container\">
                        <div class=\"bar\" style=\"width: {width_percent}%;\">
                        </div>
                        <span class=\"percentage-outside\" style=\"left: calc({width_percent}% + 12px); right: auto;\">{percentage_display}%</span>
                    </div>
                </div>
            '''

new_chart_content += '</div>'

# Alte Balken-Container durch neue ersetzen
html = html.replace(chart_container_content, new_chart_content)

# Geänderte HTML speichern
with open('umfrage.html', 'w', encoding='utf-8') as f:
    f.write(html)
"
  
  # Screenshot erstellen
  node screenshotter.js --width 608 --height 342 --deviceScaleFactor 4 --outputPath "$output"
done

echo "Alle Grafiken wurden erstellt!"
