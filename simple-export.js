// Einfache Export-Lösung ohne native Abhängigkeiten
const fs = require('fs');
const path = require('path');

function simpleExport() {
  try {
    // HTML-Datei lesen
    const htmlPath = path.join(__dirname, 'umfrage.html');
    const htmlContent = fs.readFileSync(htmlPath, 'utf8');
    
    // Speichere als eigenständige HTML-Datei
    const standalonePath = path.join(__dirname, 'umfrage_standalone.html');
    fs.writeFileSync(standalonePath, htmlContent);
    
    // CSS extrahieren und als separates File speichern
    const cssRegex = /<style>([\s\S]*?)<\/style>/;
    const cssMatch = htmlContent.match(cssRegex);
    
    if (cssMatch && cssMatch[1]) {
      const cssContent = cssMatch[1];
      const cssPath = path.join(__dirname, 'umfrage_style.css');
      fs.writeFileSync(cssPath, cssContent);
    }
    
    // Daten extrahieren für andere Tools
    const data = [
      { label: 'Sehr gut', value: 21.9 },
      { label: 'Gut', value: 31.4 },
      { label: 'Befriedigend', value: 16.1 },
      { label: 'Ausreichend', value: 11.5 },
      { label: 'Mangelhaft', value: 12.9 },
      { label: 'Ungenügend', value: 6.3 }
    ];
    
    // Als JSON speichern
    const jsonPath = path.join(__dirname, 'umfrage_data.json');
    fs.writeFileSync(jsonPath, JSON.stringify(data, null, 2));
    
    // Anweisungen für den Benutzer erstellen
    const instructionsContent = `
# Anleitung zum Exportieren der Grafik als PNG

Da die automatische Erstellung des PNGs fehlgeschlagen ist, hier einige manuelle Alternativen:

## Option 1: Browser-Screenshot
1. Öffne die Datei 'umfrage_standalone.html' in deinem Browser
2. Drücke F12, um die Entwicklertools zu öffnen
3. Drücke Strg+Shift+P und suche nach "Screenshot" 
4. Wähle "Vollständigen Screenshot aufnehmen"

## Option 2: Externe Tools
1. Öffne die HTML-Datei in einem Browser
2. Verwende ein Screenshotprogramm wie Greenshot, Lightshot oder die Windows-Snipping-Tool
3. Speichere den Screenshot als PNG

## Option 3: Online-Konverter
1. Besuche eine Seite wie https://www.html2image.app/
2. Lade die HTML-Datei hoch oder kopiere den Inhalt
3. Exportiere als PNG

Die Daten wurden außerdem als JSON in 'umfrage_data.json' gespeichert, 
falls du sie in einem anderen Tool wie Excel oder einem Online-Diagramm-Tool verwenden möchtest.
    `;
    
    const instructionsPath = path.join(__dirname, 'ANLEITUNG.md');
    fs.writeFileSync(instructionsPath, instructionsContent);
    
    console.log('Dateien erfolgreich exportiert:');
    console.log('- umfrage_standalone.html (Vollständige HTML-Datei)');
    console.log('- umfrage_style.css (Extrahierte CSS-Stile)');
    console.log('- umfrage_data.json (Daten im JSON-Format)');
    console.log('- ANLEITUNG.md (Anleitung zum manuellen PNG-Export)');
    
  } catch (error) {
    console.error('Fehler beim Exportieren:', error);
  }
}

simpleExport(); 