import plotly.graph_objects as go
import plotly.io as pio

# Einfaches Diagramm erstellen
fig = go.Figure(go.Bar(y=[2, 1, 3]))

# Als PNG speichern
print("Exportiere als PNG...")
fig.write_image("test.png")
print("Export erfolgreich!") 