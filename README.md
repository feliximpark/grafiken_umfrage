# Umfrage-Grafik Export

Dieses Projekt erstellt eine HTML-Umfrage-Grafik und exportiert sie als PNG mit konfigurierbaren Einstellungen für Größe, Auflösung und Format.

## Voraussetzungen

- Node.js (v14 oder höher)
- npm

## Installation

1. Repository klonen oder Dateien herunterladen
2. Abhängigkeiten installieren:

```bash
npm install
```

## Verwendung

### Standardmäßiger Export (PNG)

Der einfachste Weg, die Grafik zu exportieren:

```bash
npm run export
```

### Export-Varianten mit vordefinierten Einstellungen

Wir bieten verschiedene vordefinierte Export-Konfigurationen:

- **HD-Qualität (1000×800, doppelte Auflösung)**
  ```bash
  npm run export-hd
  ```

- **4K-Qualität (2000×1500, dreifache Auflösung)**
  ```bash
  npm run export-4k
  ```

- **JPEG-Format (90% Qualität)**
  ```bash
  npm run export-jpeg
  ```

- **Mobile Ansicht (375×800, doppelte Auflösung)**
  ```bash
  npm run export-mobile
  ```

### Benutzerdefinierte Einstellungen

Du kannst die Parameter auch direkt anpassen:

```bash
node screenshotter.js --width 1200 --height 900 --deviceScaleFactor 2 --format png --fullPage true
```

**Verfügbare Parameter:**
- `--width` - Breite in Pixeln (Standard: 800)
- `--height` - Höhe in Pixeln (Standard: 600)
- `--deviceScaleFactor` - Auflösung / Pixeldichte (1=normal, 2=doppelt, 3=dreifach)
- `--format` - Ausgabeformat ('png' oder 'jpeg')
- `--quality` - Qualität bei JPEG (0-100)
- `--fullPage` - Gesamte Seite ('true' oder 'false')
- `--outputPath` - Ausgabedateiname

### Alternative: Einfacher Export

Falls Puppeteer Probleme bereitet, nutze diese Methode, um Dateien für die manuelle Bearbeitung zu erzeugen:

```bash
npm run export-simple
```

## Fehlerbehebung

Falls die automatische Erstellung Probleme bereitet:

1. Gib Chrome mehr Zeit zum Laden der Schriftarten, indem du die Wartezeit erhöhst:
   - Ändere in `screenshotter.js` die Zeile `await sleep(5000);` zu `await sleep(10000);`

2. Bei Fehlern mit neueren Versionen von Puppeteer:
   - Das Skript wurde bereits angepasst, um mit aktuellen Puppeteer-Versionen zu funktionieren
   - Falls du Fehler mit `page.waitForTimeout` siehst, prüfe, ob die richtige Version von screenshotter.js verwendet wird

3. Stelle sicher, dass Chrome/Chromium auf deinem System installiert ist

4. Bei Windows-Systemen:
   - Führe das Skript in einer Administrator-Eingabeaufforderung aus
   - Falls du die Fehlermeldung `Could not find browser` erhältst, installiere Chrome oder wechsle zum einfachen Export

5. Wenn alles fehlschlägt, nutze den einfachen Export (`npm run export-simple`) und folge den Anweisungen in der ANLEITUNG.md

## Dateien

- `umfrage.html` - HTML-Darstellung der Umfrage-Grafik
- `screenshotter.js` - Node.js-Skript zum Erstellen des PNG-Screenshots mit konfigurierbaren Einstellungen
- `simple-export.js` - Alternative Lösung für den manuellen Export
- `package.json` - Projekt-Konfiguration und vordefinierte Export-Skripte