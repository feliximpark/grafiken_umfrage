"""
Behebung des fig.write_image() Aufhängens unter Windows
========================================================

Problem:
--------
Unter Windows hängt sich die Funktion fig.write_image() bei 
neueren Versionen von Kaleido (0.2.1) auf, ohne eine Fehlermeldung auszugeben.

Lösung:
-------
Die Installation einer älteren Version von Kaleido behebt das Problem:
    pip install kaleido==0.1.0.post1

Ursache:
--------
Dies ist ein bekannter Fehler in Kaleido. Mehr Informationen unter:
    https://github.com/plotly/Kaleido/issues/134
"""

import plotly.graph_objects as go
import plotly.io as pio

# Erstelle ein einfaches Plotly-Diagramm
fig = go.Figure(go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2]))
fig.update_layout(title="Test Diagram")

# Exportiere das Diagramm als PNG
print("Exportiere das Diagramm als PNG...")
try:
    # Mit kaleido==0.1.0.post1 sollte dieser Aufruf nicht hängen bleiben
    fig.write_image("plotly_test_output.png")
    print("Export erfolgreich! Die Datei wurde als plotly_test_output.png gespeichert.")
except Exception as e:
    print(f"Fehler beim Export: {e}")
    print("Tipp: Installiere eine ältere Version von Kaleido mit: pip install kaleido==0.1.0.post1")

# Informationen zur installierten Kaleido-Version anzeigen
import subprocess
print("\nInstallierte Kaleido-Version:")
try:
    result = subprocess.run(["pip", "show", "kaleido"], capture_output=True, text=True)
    print(result.stdout)
except Exception:
    print("Konnte keine Versionsinformationen abrufen.") 