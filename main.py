import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Récupération sécurisée des variables
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def envoyer_alerte(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, data={'chat_id': CHAT_ID, 'text': message})

# Configuration Selenium Headless
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

try:
    url = "https://www.maiia.com/allergologue/44150-ancenis/baron-thurotte-aurelie/rdv"
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    # ✅ Accepter les cookies
    try:
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "OK, accept all")]'))
        )
        cookie_btn.click()
        print("✅ Cookies acceptés")
    except:
        print("⚠️ Pas de bannière cookies visible")

    # ✅ Cliquer sur "Motif de consultation"
    motif_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//button[contains(text(), "Motif de consultation")]'
    )))
    motif_btn.click()
    time.sleep(1)

    # ✅ Sélectionner "Première consultation enfant"
    motif = driver.find_element(By.XPATH, '//span[contains(text(), "Première consultation enfant")]')
    motif.click()
    time.sleep(10)

    if "RDV en ligne indisponible" not in driver.page_source:
        envoyer_alerte("🎉 Un créneau est disponible pour une première consultation chez la Dre Baron Thurotte !")
    else:
        print("Aucun créneau.")

except Exception as e:
    # 🧪 Dump de la page pour debug
    with open("page_dump.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    raise e

finally:
    driver.quit()
