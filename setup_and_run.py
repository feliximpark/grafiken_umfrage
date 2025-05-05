import subprocess
import sys
import os

def install_dependencies():
    """Installiere alle benötigten Abhängigkeiten"""
    print("Installiere benötigte Pakete...")
    
    # Liste der benötigten Pakete
    packages = [
        "plotly",
        "pandas",
        "kaleido",  # Für die Bild-Export-Funktionalität
    ]
    
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("Alle Pakete erfolgreich installiert.")

def run_plotly_script():
    """Führe das Plotly-Skript aus"""
    print("Generiere die Grafik...")
    
    try:
        exec(open("plotly_nisa_umfrage.py").read())
        print("Grafik erfolgreich erstellt!")
        
        # Überprüfe, ob die Ausgabedateien erstellt wurden
        if os.path.exists("plotly_nisa_umfrage.png"):
            print("PNG-Datei wurde erstellt: plotly_nisa_umfrage.png")
        
        if os.path.exists("plotly_nisa_umfrage.html"):
            print("HTML-Datei wurde erstellt: plotly_nisa_umfrage.html")
    
    except Exception as e:
        print(f"Fehler beim Erstellen der Grafik: {e}")

if __name__ == "__main__":
    install_dependencies()
    run_plotly_script() 