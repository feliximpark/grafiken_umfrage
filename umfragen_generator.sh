#!/bin/bash

# Sicherstellen, dass der Grafiken-Ordner existiert
mkdir -p ./grafiken

# Python-Skript ausführen
echo "Starte Umfragegrafiken-Generator..."
python umfrage_generator.py

echo "Fertig! Die Grafiken wurden im Ordner 'grafiken' gespeichert." 