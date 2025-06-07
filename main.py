import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

import os
import time
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def envoyer_alerte(message):
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        response = requests.post(url, data={'chat_id': CHAT_ID, 'text': message})
        response.raise_for_status()
    except Exception as e:
        print("❌ Impossible d'envoyer une alerte Telegram :", e)

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)

try:
    url = "https://www.maiia.com/allergologue/44150-ancenis/baron-thurotte-aurelie/rdv"
    driver.get(url)
    wait = WebDriverWait(driver, 20)

    # Supprimer tarteaucitron
    driver.execute_script("""
        var el = document.getElementById('tarteaucitronRoot');
        if (el && el.parentNode) el.parentNode.removeChild(el);
        var alert = document.getElementById('tarteaucitronDisclaimerAlert');
        if (alert && alert.parentNode) alert.parentNode.removeChild(alert);
    """)
    print("✅ Bandeau 'tarteaucitron' supprimé du DOM")

    # Accepter cookies
    try:
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Tout accepter")]'))
        )
        cookie_btn.click()
        print("✅ Cookies acceptés")
    except:
        print("⚠️ Pas de bannière cookies visible")

    wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Motif de consultation")]')))
    print("✅ Texte 'Motif de consultation' détecté")

    # Étape critique : clic forcé sur le bouton role=combobox
    try:
        bouton = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[role="combobox"]')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bouton)
        time.sleep(1)

        try:
            bouton.click()
            print("✅ Bouton cliqué avec click()")
        except Exception as click_error:
            print("⚠️ click() échoué, tentative JS")
            driver.execute_script("""
                try {
                    arguments[0].scrollIntoView({block: 'center'});
                    var event = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    arguments[0].dispatchEvent(event);
                } catch (e) {
                    console.error("❌ JS click échoué", e);
                    throw e;
                }
            """, bouton)
            print("✅ JS click déclenché")
    except Exception as e:
        raise Exception("❌ Impossible de cliquer le bouton du menu déroulant (forcé)") from e

    # Attente apparition menu
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//ul[@role="listbox"]')))
        print("✅ Menu déroulant affiché")
    except:
        raise Exception("❌ Menu déroulant non affiché après clic")

    # Sélection motif
    try:
        motif = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Première consultation enfant")]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", motif)
        motif.click()
        print("✅ Motif sélectionné")
    except Exception as motif_error:
        print("❌ Impossible de cliquer le motif :", motif_error)
        driver.save_screenshot("motif_debug.png")
        raise

    time.sleep(10)
    if "RDV en ligne indisponible" not in driver.page_source:
        envoyer_alerte("🎉 Un créneau est disponible chez la Dre Baron Thurotte !")
        print("✅ Créneau détecté et alerte envoyée")
    else:
        print("❌ Aucun créneau.")

except Exception as e:
    print("⚠️ Erreur :", e)
    driver.save_screenshot("page_debug.png")
    with open("page_dump.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    envoyer_alerte(f"❌ Erreur script Maiia : {e}")

finally:
    driver.quit()
