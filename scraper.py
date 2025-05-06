import os
import time
import shutil
import re
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv()

LOGIN_NAME = os.getenv('LOGIN_NAME')
LOGIN_PW = os.getenv('LOGIN_PW')

def setup_driver():
    """Initialisiert den Chrome-Webdriver mit geeigneten Optionen"""
    chrome_options = Options()
    # Headless-Modus kann für Produktionsbetrieb aktiviert werden
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Verzeichnis für Downloads festlegen
    prefs = {
        "download.default_directory": os.path.join(os.getcwd(), "data_in"),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_campanero(driver):
    """Führt den Login-Prozess auf der campanero-Plattform durch"""
    try:
        # Navigiere zur Login-Seite
        driver.get("https://leser-umfrage.de/backend/login/")
        logger.info("Login-Seite geladen")
        
        # Speichere die Login-Seite für Debugging-Zwecke
        driver.save_screenshot("login_page_before.png")
        with open("login_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        # Warte bis die Seite geladen ist und die Eingabefelder sichtbar sind
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        
        # Login-Daten direkt über JavaScript eingeben und absenden
        # Dies umgeht potenzielle Probleme mit dem Klicken auf Buttons
        js_code = f"""
            // E-Mail setzen
            document.querySelector('input[name="email"]').value = '{LOGIN_NAME}';
            
            // Passwort setzen
            document.querySelector('input[name="password"]').value = '{LOGIN_PW}';
            
            // Den richtigen Anmelde-Button finden und klicken
            var loginButton = document.querySelector('a.form-button:not(.plain)');
            
            if (loginButton) {{
                console.log('Login-Button gefunden:', loginButton);
                loginButton.click();
            }} else {{
                console.log('Kein Login-Button gefunden');
                // Wenn kein Button gefunden wurde, versuche das Formular direkt abzusenden
                var form = document.querySelector('form');
                if (form) {{
                    form.submit();
                }}
            }}
        """
        
        logger.info("Führe JavaScript-Code für das Login aus")
        driver.execute_script(js_code)
        
        # Alternative: Falls JavaScript nicht funktioniert, versuche konventionelle Methode
        try:
            # Warte kurz und überprüfe, ob die Felder tatsächlich gefüllt wurden
            time.sleep(1)
            email_value = driver.execute_script('return document.querySelector("input[type=\'email\']").value')
            
            if not email_value:
                logger.warning("JavaScript hat die Felder nicht gefüllt, versuche konventionelle Methode")
                
                # Login-Daten konventionell eingeben
                email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
                email_input.clear()
                email_input.send_keys(LOGIN_NAME)
                
                password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                password_input.clear()
                password_input.send_keys(LOGIN_PW)
                
                # Versuche das Formular mit Enter zu senden
                logger.info("Versuche Login über Enter-Taste")
                password_input.send_keys(Keys.RETURN)
        except Exception as e:
            logger.warning(f"Fallback-Methode fehlgeschlagen: {str(e)}")
        
        # Warte auf erfolgreichen Login (warte auf Änderung der URL)
        logger.info("Warte auf URL-Änderung nach dem Login-Versuch")
        try:
            WebDriverWait(driver, 10).until(
                EC.url_changes("https://leser-umfrage.de/backend/login/")
            )
            logger.info(f"URL hat sich geändert: {driver.current_url}")
            
            # Speichere die Seite nach dem Login
            driver.save_screenshot("after_login_success.png")
            return True
        except TimeoutException:
            logger.warning("URL hat sich nicht geändert, versuche dennoch zu überprüfen, ob wir eingeloggt sind")
            
            # Manchmal ändert sich die URL nicht, aber wir sind dennoch eingeloggt
            # Versuche zu erkennen, ob wir auf einer Dashboard- oder Übersichtsseite sind
            driver.save_screenshot("login_check.png")
            
            # Prüfe, ob typische Elemente einer eingeloggten Sitzung vorhanden sind
            try:
                # Suche nach typischen Dashboard-Elementen
                dashboard_elements = driver.find_elements(By.CSS_SELECTOR, ".dashboard, .overview, .logout, .user-info")
                if dashboard_elements:
                    logger.info("Login scheint erfolgreich zu sein (Dashboard-Elemente gefunden)")
                    return True
            except:
                pass
                
            logger.error("Login fehlgeschlagen - konnte nicht zur Dashboard-Seite navigieren")
            return False
        
    except Exception as e:
        logger.error(f"Fehler beim Login: {str(e)}")
        # Screenshots der Seite für Debugging-Zwecke erstellen
        driver.save_screenshot("login_error.png")
        logger.info("Screenshot bei Fehler gespeichert als 'login_error.png'")
        return False

def navigate_to_campaigns(driver):
    """Navigiert zur Kampagnen-Seite nach erfolgreichem Login"""
    try:
        # Methode 1: Direkte Navigation per URL
        logger.info("Navigiere direkt zur Kampagnen-Seite per URL")
        driver.get("https://leser-umfrage.de/backend/campaigns")
        
        # Warte kurz, um sicherzustellen, dass die Seite geladen ist
        time.sleep(2)
        
        # Überprüfe, ob wir auf der richtigen Seite sind
        current_url = driver.current_url
        logger.info(f"Aktuelle URL: {current_url}")
        
        # Speichere einen Screenshot der Kampagnen-Seite
        driver.save_screenshot("campaigns_page.png")
        
        # Wenn die direkte Navigation nicht funktioniert hat, versuche Methode 2
        if "campaigns" not in current_url:
            logger.warning("Direkte Navigation zur Kampagnen-Seite fehlgeschlagen, versuche Button-Klick")
            
            # Methode 2: Klicke auf den Kampagnen-Button
            try:
                # Suche nach dem Kampagnen-Button mit dem gegebenen CSS-Selektor
                campaigns_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.menu-app-item-clickable[href*="campaigns"]'))
                )
                
                logger.info("Kampagnen-Button gefunden, klicke darauf")
                campaigns_button.click()
                
                # Warte, bis die Seite geladen ist
                time.sleep(2)
                
                # Speichere einen Screenshot nach dem Klick
                driver.save_screenshot("campaigns_page_after_click.png")
                
                current_url = driver.current_url
                logger.info(f"Aktuelle URL nach Klick: {current_url}")
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"Konnte den Kampagnen-Button nicht finden: {str(e)}")
                return False
        
        # Speichere den HTML-Code der Kampagnen-Seite für die Analyse
        with open("campaigns_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        logger.info("Navigation zur Kampagnen-Seite erfolgreich")
        return True
        
    except Exception as e:
        logger.error(f"Fehler bei der Navigation zur Kampagnen-Seite: {str(e)}")
        driver.save_screenshot("campaigns_navigation_error.png")
        return False

def search_for_campaign(driver, search_term="Politik"):
    """Sucht nach Kampagnen mit dem angegebenen Suchbegriff"""
    try:
        logger.info(f"Suche nach Kampagnen mit dem Begriff: {search_term}")
        
        # Warte auf das Erscheinen des Suchfeldes
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-input.table-filter[placeholder*="Suche in Name"]'))
        )
        
        # Suchfeld leeren und Suchbegriff eingeben
        search_input.clear()
        search_input.send_keys(search_term)
        
        # Kurze Pause, um die Suche wirken zu lassen
        logger.info("Suchbegriff eingegeben, warte auf Filterergebnisse")
        time.sleep(2)
        
        # Screenshot nach der Suche erstellen
        driver.save_screenshot("campaign_search_results.png")
        
        # HTML der Suchergebnisse speichern
        with open("campaign_search_results.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        return True
        
    except Exception as e:
        logger.error(f"Fehler bei der Suche nach Kampagnen: {str(e)}")
        driver.save_screenshot("campaign_search_error.png")
        return False

def filter_by_status_active(driver):
    """Sucht nach dem Status-Filter, öffnet ihn und wählt 'aktiv' aus"""
    try:
        logger.info("Suche nach dem Status-Filter")
        
        # Finde alle filter-box Elemente
        filter_boxes = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.filter-box'))
        )
        
        # Suche nach der filter-box, die ein span mit dem Text "Status" enthält
        status_filter = None
        for box in filter_boxes:
            try:
                # Suche nach einem span mit dem Text "Status" innerhalb der Box
                span_element = box.find_element(By.XPATH, './/span[contains(text(), "Status")]')
                if span_element:
                    logger.info("Status-Filter gefunden")
                    status_filter = box
                    break
            except NoSuchElementException:
                continue
                
        if not status_filter:
            logger.error("Status-Filter nicht gefunden")
            return False
            
        # Speichere Screenshot vor dem Klick
        driver.save_screenshot("before_status_filter_click.png")
        
        # Finde den Pfeil-Button innerhalb der gefundenen filter-box
        arrow_element = status_filter.find_element(By.CSS_SELECTOR, '.filter-box-arrow.fal.fa-chevron-down')
        logger.info("Pfeil-Element im Status-Filter gefunden, klicke darauf")
        
        # Klicke auf den Pfeil, um das Dropdown-Menü zu öffnen
        arrow_element.click()
        
        # Warte kurz, bis das Dropdown-Menü geöffnet ist
        time.sleep(1)
        
        # Speichere Screenshot nach dem Klick auf den Pfeil
        driver.save_screenshot("status_dropdown_open.png")
        
        # Genau auf das angegebene Label-Element klicken
        try:
            # Suche nach dem label mit der Klasse "filter-box-option", das ein span mit "aktiv" enthält
            # Suche innerhalb des Status-Filters bzw. im geöffneten Dropdown
            logger.info("Suche nach dem 'aktiv'-Element im geöffneten Dropdown")
            
            # Methode 1: Direkt auf das Label mit dem korrekten span-Text klicken
            active_option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, 
                    '//label[contains(@class, "filter-box-option")][.//span[text()="aktiv"]]'))
            )
            logger.info("'aktiv'-Element gefunden (Label), klicke darauf")
            active_option.click()
        except Exception as e:
            logger.warning(f"Konnte nicht direkt auf das Label klicken: {str(e)}")
            
            try:
                # Methode 2: Auf das span-Element mit dem Text "aktiv" innerhalb des Labels klicken
                active_span = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                        '//label[contains(@class, "filter-box-option")]/span[text()="aktiv"]'))
                )
                logger.info("'aktiv'-Element gefunden (span), klicke darauf")
                active_span.click()
            except Exception as e:
                logger.warning(f"Konnte nicht auf das span-Element klicken: {str(e)}")
                
                try:
                    # Methode 3: Klicke auf das Eingabefeld für "aktiv"
                    active_input = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 
                            'input.table-filter[data-type="status"][data-value="active"]'))
                    )
                    logger.info("'aktiv'-Element gefunden (input), klicke darauf")
                    active_input.click()
                except Exception as e:
                    logger.warning(f"Konnte nicht auf das input-Element klicken: {str(e)}")
                    
                    # Methode 4: JavaScript-Ausführung als letzter Ausweg
                    logger.info("Versuche, 'aktiv'-Option per JavaScript zu klicken")
                    driver.execute_script("""
                        var labels = document.querySelectorAll('label.filter-box-option');
                        for (var i = 0; i < labels.length; i++) {
                            if (labels[i].textContent.includes('aktiv')) {
                                labels[i].click();
                                return true;
                            }
                        }
                        
                        // Versuch auf das Input zu klicken
                        var input = document.querySelector('input.table-filter[data-type="status"][data-value="active"]');
                        if (input) {
                            input.click();
                            return true;
                        }
                        
                        return false;
                    """)
        
        # Warte kurz, damit die Filterung wirksam wird
        time.sleep(2)
        
        # Speichere Screenshot nach der Auswahl der Option "aktiv"
        driver.save_screenshot("status_active_selected.png")
        
        logger.info("Filterung nach Status 'aktiv' abgeschlossen")
        return True
        
    except Exception as e:
        logger.error(f"Fehler beim Filtern nach Status 'aktiv': {str(e)}")
        driver.save_screenshot("status_filter_error.png")
        return False

def find_recent_campaigns(driver, table_rows, headers):
    """Findet Kampagnen, die heute oder gestern gestartet wurden und bereits Teilnehmer haben"""
    try:
        # Aktuelles Datum und Datum von gestern ermitteln
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        logger.info(f"Suche nach Kampagnen mit Start-Datum von heute ({today.strftime('%d.%m.%Y')}) oder gestern ({yesterday.strftime('%d.%m.%Y')}) und mit Teilnehmern")
        print(f"\nSuche nach Kampagnen mit Start-Datum von heute ({today.strftime('%d.%m.%Y')}) oder gestern ({yesterday.strftime('%d.%m.%Y')}) und mit Teilnehmern")
        
        # Verschiedene mögliche Datumsformate
        today_formats = [
            today.strftime('%d.%m.%Y'),  # 06.05.2025
            today.strftime('%d.%m.%y'),  # 06.05.25
            today.strftime('%d.%m.'),    # 06.05.
            today.strftime('%d.%m'),     # 06.05
            today.strftime('%Y-%m-%d'),  # 2025-05-06
            today.strftime('%d/%m/%Y'),  # 06/05/2025
            today.strftime('heute')      # Textuell "heute"
        ]
        
        yesterday_formats = [
            yesterday.strftime('%d.%m.%Y'),  # 05.05.2025
            yesterday.strftime('%d.%m.%y'),  # 05.05.25
            yesterday.strftime('%d.%m.'),    # 05.05.
            yesterday.strftime('%d.%m'),     # 05.05
            yesterday.strftime('%Y-%m-%d'),  # 2025-05-05
            yesterday.strftime('%d/%m/%Y'),  # 05/05/2025
            yesterday.strftime('gestern')    # Textuell "gestern"
        ]
        
        # Finde den Index der "Start"-Spalte
        start_column_index = -1
        for i, header in enumerate(headers):
            if "start" in header.lower():
                start_column_index = i
                break
        
        # Finde den Index der "Teilnehmer"-Spalte
        participants_column_index = -1
        for i, header in enumerate(headers):
            # Verschiedene mögliche Bezeichnungen für die Teilnehmer-Spalte
            if any(term in header.lower() for term in ["teilnehmer", "responses", "antworten", "anzahl"]):
                participants_column_index = i
                break
        
        if start_column_index == -1:
            logger.warning("Konnte keine 'Start'-Spalte in der Tabelle finden")
            print("Konnte keine 'Start'-Spalte in der Tabelle finden")
            return []
            
        if participants_column_index == -1:
            logger.warning("Konnte keine 'Teilnehmer'-Spalte in der Tabelle finden")
            print("Konnte keine 'Teilnehmer'-Spalte in der Tabelle finden")
            return []
        
        logger.info(f"Spalten gefunden - Start: {headers[start_column_index]}, Teilnehmer: {headers[participants_column_index]}")
        print(f"Spalten gefunden - Start: {headers[start_column_index]}, Teilnehmer: {headers[participants_column_index]}")
        
        recent_campaigns = []
        filtered_campaigns = []
        skipped_date = 0
        skipped_participants = 0
        
        # Durchsuche alle Zeilen nach Einträgen mit heutigem oder gestrigem Startdatum
        for i, row in enumerate(table_rows):
            cells = row.find_elements(By.CSS_SELECTOR, 'td')
            
            # Überprüfe, ob es genügend Zellen gibt
            if len(cells) <= max(start_column_index, participants_column_index):
                continue
                
            # Hole den Text aus der Start-Spalte
            start_date_text = cells[start_column_index].text.strip()
            
            # Hole den Text aus der Teilnehmer-Spalte
            participants_text = cells[participants_column_index].text.strip()
            
            # Überprüfe, ob das Datum mit einem der heutigen oder gestrigen Formate übereinstimmt
            is_today = any(date_format in start_date_text for date_format in today_formats)
            is_yesterday = any(date_format in start_date_text for date_format in yesterday_formats)
            
            # Prüfe auf Teilnehmer
            has_participants = False
            try:
                # Versuche, den Text in eine Zahl umzuwandeln
                # Entferne zuerst eventuelle Nicht-Ziffern-Zeichen (z.B. Punkte oder Kommas als Tausendertrennzeichen)
                cleaned_participant_text = participants_text
                for char in ['.', ',', ' ']:
                    cleaned_participant_text = cleaned_participant_text.replace(char, '')
                
                # Konvertiere in int, wenn möglich
                if cleaned_participant_text and cleaned_participant_text != '-' and cleaned_participant_text != '0':
                    participants_count = int(cleaned_participant_text)
                    has_participants = participants_count > 0
            except ValueError:
                # Wenn die Konvertierung fehlschlägt, hat die Kampagne keine Teilnehmer
                has_participants = False
            
            # Kampagne entspricht dem Datum-Kriterium
            if is_today or is_yesterday:
                # Sammle alle Informationen zu dieser Kampagne
                campaign_data = {}
                for j, cell in enumerate(cells):
                    if j < len(headers):
                        column_name = headers[j]
                        campaign_data[column_name] = cell.text.strip()
                
                # Füge zusätzliche Metadaten hinzu
                campaign_data['row_index'] = i
                campaign_data['start_date_match'] = 'today' if is_today else 'yesterday'
                campaign_data['has_participants'] = has_participants
                
                # Suche nach Links in der Zeile (für spätere Navigation)
                links = row.find_elements(By.CSS_SELECTOR, 'a')
                if links:
                    campaign_data['links'] = [{'text': link.text.strip(), 'href': link.get_attribute('href')} for link in links]
                
                # Füge zur Liste aller kürzlich gestarteten Kampagnen hinzu
                recent_campaigns.append(campaign_data)
                
                # Wenn sie auch Teilnehmer hat, füge sie zur gefilterten Liste hinzu
                if has_participants:
                    filtered_campaigns.append(campaign_data)
                else:
                    skipped_participants += 1
            else:
                skipped_date += 1
        
        # Ausgabe der gefundenen Kampagnen nach beiden Kriterien
        print(f"\n=== Filterungsergebnisse ===")
        print(f"Kampagnen insgesamt: {len(table_rows)}")
        print(f"Übersprungen (falsches Datum): {skipped_date}")
        print(f"Kürzlich gestartet (heute/gestern): {len(recent_campaigns)}")
        print(f"Übersprungen (keine Teilnehmer): {skipped_participants}")
        print(f"Entsprechen allen Kriterien: {len(filtered_campaigns)}")
        
        if filtered_campaigns:
            logger.info(f"Gefunden: {len(filtered_campaigns)} Kampagnen, die heute oder gestern gestartet wurden UND Teilnehmer haben:")
            print(f"\n=== Kampagnen, die heute/gestern gestartet wurden UND Teilnehmer haben ===")
            
            for i, campaign in enumerate(filtered_campaigns):
                start_date = campaign.get(headers[start_column_index], "Unbekannt")
                participants = campaign.get(headers[participants_column_index], "Unbekannt")
                
                # Verwende die erste Spalte als Titel/Name, wenn verfügbar
                campaign_name = campaign.get(headers[0], "Unbekannt") if headers else "Unbekannt"
                
                logger.info(f"Kampagne {i+1}: {campaign_name} (Start: {start_date}, Teilnehmer: {participants})")
                print(f"\nKampagne {i+1}: {campaign_name}")
                print(f"  Start: {start_date}")
                print(f"  Teilnehmer: {participants}")
                
                # Gib alle relevanten Details aus (für Debugging)
                title_columns = ["titel", "name", "beschreibung", "description"]
                
                # Finde Spalten, die potenziell Titelüberschriften enthalten könnten
                for key, value in campaign.items():
                    if key not in ['row_index', 'links', 'start_date_match', 'has_participants']:
                        key_lower = key.lower()
                        if any(title_term in key_lower for title_term in title_columns):
                            print(f"  {key}: {value}")
                
                # Gib Links aus, falls vorhanden
                if 'links' in campaign:
                    logger.info("  Links gefunden")
                    first_link = campaign['links'][0] if campaign['links'] else None
                    if first_link:
                        print(f"  Link: {first_link['href']}")
        else:
            logger.info("Keine Kampagnen gefunden, die alle Filterkriterien erfüllen")
            print("\nKeine Kampagnen gefunden, die alle Filterkriterien erfüllen")
        
        return filtered_campaigns
        
    except Exception as e:
        logger.error(f"Fehler beim Suchen nach gefilterten Kampagnen: {str(e)}")
        print(f"Fehler beim Suchen nach gefilterten Kampagnen: {str(e)}")
        return []

def count_table_entries(driver):
    """Zählt die Anzahl der Einträge in der Kampagnen-Tabelle und liest alle Spalteninhalte aus"""
    try:
        logger.info("Zähle Einträge in der Kampagnen-Tabelle und lese Spalteninhalte")
        
        # Warte, bis die Tabelle geladen ist
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.content-table[data-id="campaigns"]'))
        )
        
        # Lies die Spaltenüberschriften aus
        header_cells = driver.find_elements(By.CSS_SELECTOR, 'table.content-table[data-id="campaigns"] thead th')
        headers = [header.text.strip() for header in header_cells]
        
        # Gib die Spaltenüberschriften aus (nur für Log, nicht mehr in Konsole)
        logger.info("Spaltenüberschriften der Tabelle:")
        for i, header in enumerate(headers):
            logger.info(f"  Spalte {i+1}: {header}")
        
        # Finde alle Zeilen in der Tabelle (tbody tr)
        # Wir suchen nach tr-Elementen innerhalb der tbody der Tabelle
        table_rows = driver.find_elements(By.CSS_SELECTOR, 'table.content-table[data-id="campaigns"] tbody tr')
        
        # Alternative Methode, falls keine tbody verwendet wird oder die Struktur anders ist
        if not table_rows:
            # Versuche alle tr-Elemente zu finden, außer denen im thead
            table_rows = driver.find_elements(By.CSS_SELECTOR, 'table.content-table[data-id="campaigns"] tr:not(thead tr)')
        
        # Anzahl der Zeilen
        row_count = len(table_rows)
        
        # Ausgabe für Debugging (nur in Log, nicht mehr in Konsole)
        logger.info(f"Anzahl der Einträge in der Kampagnen-Tabelle: {row_count}")
        
        # Lese alle Zeilen für die spätere Analyse, aber gib sie nicht mehr in der Konsole aus
        for i, row in enumerate(table_rows):
            # Für Log-Zwecke speichern wir die Daten der ersten Zelle jeder Zeile
            cells = row.find_elements(By.CSS_SELECTOR, 'td')
            if cells:
                first_cell_text = cells[0].text.strip()
                logger.info(f"Eintrag {i+1}: {first_cell_text}")
        
        # Speichere einen Screenshot der Tabelle
        driver.save_screenshot("campaign_table.png")
        
        # Suche nach kürzlich gestarteten Kampagnen - diese werden in der Konsole ausgegeben
        print(f"\n=== Gefundene Kampagnen insgesamt: {row_count} ===")
        recent_campaigns = find_recent_campaigns(driver, table_rows, headers)
        
        return row_count, recent_campaigns
        
    except Exception as e:
        logger.error(f"Fehler beim Auslesen der Tabelle: {str(e)}")
        driver.save_screenshot("table_read_error.png")
        return 0, []

def main():
    # Stelle sicher, dass das Download-Verzeichnis existiert
    os.makedirs("data_in", exist_ok=True)
    
    logger.info("Scraper gestartet")
    driver = setup_driver()
    
    try:
        if login_to_campanero(driver):
            logger.info("Erfolgreich eingeloggt bei campanero")
            
            # Nach erfolgreichem Login zur Kampagnen-Seite navigieren
            if navigate_to_campaigns(driver):
                logger.info("Erfolgreich zur Kampagnen-Seite navigiert")
                
                # Nach Kampagnen mit dem Begriff "Politik" suchen
                if search_for_campaign(driver, "Politik"):
                    logger.info("Suche nach 'Politik' erfolgreich durchgeführt")
                    
                    # Nach Status 'aktiv' filtern
                    if filter_by_status_active(driver):
                        logger.info("Filterung nach Status 'aktiv' erfolgreich")
                        
                        # Zähle die Einträge in der Tabelle und identifiziere aktuelle Kampagnen
                        entry_count, recent_campaigns = count_table_entries(driver)
                        logger.info(f"Gefundene Kampagnen nach Filterung: {entry_count}")
                        logger.info(f"Davon heute oder gestern gestartet: {len(recent_campaigns)}")
                        
                    else:
                        logger.error("Filterung nach Status fehlgeschlagen!")
                else:
                    logger.error("Suche nach Kampagnen fehlgeschlagen!")
            else:
                logger.error("Navigation zur Kampagnen-Seite fehlgeschlagen!")
        else:
            logger.error("Login fehlgeschlagen!")
            
    except Exception as e:
        logger.error(f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}")
    finally:
        # Kurze Pause vor dem Schließen, damit man sehen kann, was passiert ist
        time.sleep(20)
        driver.quit()
        logger.info("Scraper beendet")

if __name__ == "__main__":
    main() 