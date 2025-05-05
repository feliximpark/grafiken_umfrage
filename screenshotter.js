const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Konfigurierbare Parameter
const config = {
  width: 608,           // Breite in Pixeln
  height: 342,          // Höhe in Pixeln (wird automatisch angepasst)
  deviceScaleFactor: 4, // Auflösung (2 = doppelte Auflösung/Retina)
  format: 'png',        // Exportformat
  quality: 100,         // Qualität (nur für JPEG relevant, 0-100)
  fullPage: true,       // True = vollständige Seite, False = nur sichtbarer Bereich
  outputPath: 'umfrage_export.png'
};

// Konfiguration aus Befehlszeilenargumenten laden
function parseArgs() {
  const args = process.argv.slice(2);
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    const value = args[i + 1];
    
    if (key === 'width' || key === 'height' || key === 'deviceScaleFactor' || key === 'quality') {
      config[key] = Number(value);
    } else if (key === 'fullPage') {
      config[key] = value.toLowerCase() === 'true';
    } else if (key === 'format' || key === 'outputPath') {
      config[key] = value;
    }
  }
  
  // Korrigieren des Ausgabepfads, wenn das Format geändert wurde
  if (config.outputPath === 'umfrage_export.png' && config.format !== 'png') {
    config.outputPath = `umfrage_export.${config.format}`;
  }
}

// Eine asynchrone setTimeout-Funktion um die fehlende waitForTimeout zu ersetzen
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function screenshot() {
  parseArgs();
  console.log('Verwende folgende Konfiguration:');
  console.log(config);
  
  let browser;
  try {
    // Browser mit expliziten Optionen starten
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Seiteneinstellungen konfigurieren
    await page.setViewport({
      width: config.width,
      height: config.height,
      deviceScaleFactor: config.deviceScaleFactor
    });
    
    // HTML-Seite öffnen (lokaler Pfad)
    const htmlPath = path.join(__dirname, 'umfrage.html');
    await page.goto(`file://${htmlPath}`);
    
    // Warten, bis die Schriftarten geladen sind (5 Sekunden)
    console.log('Warte 5 Sekunden, bis die Schriftarten geladen sind...');
    await sleep(5000);
    
    // Screenshot erstellen
    console.log('Erstelle Screenshot...');
    await page.screenshot({
      path: config.outputPath,
      fullPage: config.fullPage,
      type: config.format,
      quality: config.format === 'jpeg' ? config.quality : undefined
    });
    
    console.log(`Screenshot wurde gespeichert als: ${config.outputPath}`);
    console.log(`Größe: ${config.width}x${config.height}, Auflösung: ${config.deviceScaleFactor}x`);
    
    // Dateigröße ausgeben
    const stats = fs.statSync(config.outputPath);
    console.log(`Dateigröße: ${(stats.size / 1024).toFixed(2)} KB`);
    
  } catch (error) {
    console.error('Fehler beim Erstellen des Screenshots:', error);
  } finally {
    // Browser immer schließen, auch bei Fehlern
    if (browser) {
      await browser.close();
    }
  }
}

screenshot(); 