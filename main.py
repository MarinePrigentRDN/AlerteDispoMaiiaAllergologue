import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Récupération sécurisée des variables d'environnement
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def envoyer_alerte(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, data={'chat_id': CHAT_ID, 'text': message})

# Configuration Selenium Headless
options = Options()
options.add_argument('--headless=new')  # plus fiable
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    url = "https://www.maiia.com/allergologue/44150-ancenis/baron-thurotte-aurelie/rdv"
    driver.get(url)

    # Sauvegarde du HTML pour diagnostic si besoin
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    # Attente et clic sur le bouton "Motif de consultation" (insensible à la casse)
    motif_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        '//button[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "motif de consultation")]'
    )))
    motif_btn.click()

    # Sélection du motif "Première consultation enfant"
    motif = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        '//span[contains(text(), "Première consultation enfant")]'
    )))
    motif.click()

    # Attente que la page se charge après le clic
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    if "RDV en ligne indisponible" not in driver.page_source:
        envoyer_alerte("🎉 Un créneau est disponible pour une première consultation chez la Dre Baron Thurotte !")
    else:
        print("Aucun créneau.")

finally:
    driver.quit()
