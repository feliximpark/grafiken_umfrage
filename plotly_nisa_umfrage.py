import plotly.graph_objects as go
import pandas as pd
from plotly.io import kaleido
import plotly.io as pio

# Schriftarten konfigurieren in der Plotly-Konfiguration
pio.templates.default = "plotly_white"

# Daten einlesen
df = pd.read_csv('ergebnis_nisa.csv')

# Farbeinstellungen
bar_color = 'rgba(66, 133, 244, 1)'  # Blauer Farbton wie im Original

# HTML-Kopf mit Web-Schriftarten definieren
html_header = '''
<head>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .title {
            font-family: 'DIN', sans-serif;
            font-weight: bold;
        }
    </style>
</head>
'''

# Figur erstellen (600x338)
fig = go.Figure()

# Balken hinzufügen
fig.add_trace(go.Bar(
    x=df['Nutzer in %'],
    y=df['Bewertung'],
    orientation='h',
    marker_color=bar_color,
    text=df['Nutzer in %'].apply(lambda x: f"{x}%".replace('.', ',')),
    textposition='outside',
    textfont=dict(family='"Inter", Arial, sans-serif', size=14),
    width=0.7  # Breite der Balken anpassen
))

# Layout konfigurieren
fig.update_layout(
    width=600,
    height=338,
    margin=dict(l=120, r=30, t=150, b=80),
    paper_bgcolor='white',
    plot_bgcolor='white',
    title=dict(
        text="Wir haben gefragt: Welche Note geben Sie der rot-grünen<br>Landesregierung?",
        font=dict(family='"DIN", Arial, sans-serif', size=22, color='rgb(40, 40, 40)', weight='bold'),
        x=0,
        y=0.98
    ),
    yaxis=dict(
        autorange="reversed",  # Um die Reihenfolge wie im Original zu haben
        tickfont=dict(family='"Inter", Arial, sans-serif', size=14),
        linecolor='white',
        showgrid=False
    ),
    xaxis=dict(
        range=[0, max(df['Nutzer in %']) * 1.1],  # Etwas mehr Platz für Text
        ticksuffix='%',
        tickfont=dict(family='"Inter", Arial, sans-serif', size=14),
        linecolor='white',
        showgrid=False,
        zeroline=False
    )
)

# Subtitle hinzufügen
fig.add_annotation(
    text="Insgesamt haben 1002 Menschen an der Umfrage teilgenommen.",
    font=dict(family='"Inter", Arial, sans-serif', size=16, color='rgb(40, 40, 40)'),
    xref="paper", yref="paper",
    x=0, y=0.87,
    showarrow=False,
    align="left"
)

# Fußnote hinzufügen
fig.add_annotation(
    text="Summe kann aufgrund von Rundungen von 100% abweichen.",
    font=dict(family='"Inter", Arial, sans-serif', size=12, color='rgb(100, 100, 100)'),
    xref="paper", yref="paper",
    x=0, y=-0.12,
    showarrow=False,
    align="left"
)

# Quelle hinzufügen
fig.add_annotation(
    text="Grafik: Knoop/RND • Quelle: eigene Umfrage",
    font=dict(family='"Inter", Arial, sans-serif', size=12, color='rgb(100, 100, 100)'),
    xref="paper", yref="paper",
    x=0, y=-0.17,
    showarrow=False,
    align="left"
)

# Speichern als Bild
fig.write_image("plotly_nisa_umfrage2.png")

# HTML-Datei mit eingebundenen Web-Schriftarten erstellen
with open("plotly_nisa_umfrage.html", "w", encoding="utf-8") as f:
    f.write(f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Umfrageergebnis</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        body {{
            font-family: 'Inter', Arial, sans-serif;
        }}
        
        .js-plotly-plot {{
            margin: 0 auto;
        }}
        
        .gtitle {{
            font-family: 'DIN', Arial, sans-serif !important;
            font-weight: bold !important;
        }}
    </style>
</head>
<body>
    {fig.to_html(include_plotlyjs='cdn', full_html=False, config={'displayModeBar': False})}
</body>
</html>
    ''')

print("HTML und PNG erfolgreich erstellt mit korrekten Schriftarten.") 