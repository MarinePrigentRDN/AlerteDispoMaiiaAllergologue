from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests

# Configuration Telegram
TELEGRAM_TOKEN = '7274166974:AAGnCgtxUIqqTFNlsSPSjmqp41NBX89gyNk'
CHAT_ID = '7800997599'

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
    time.sleep(5)

    # Clique sur le bouton pour choisir un motif
    motif_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Motif de consultation")]')
    motif_btn.click()
    time.sleep(1)

    # Choix "Première consultation enfant"
    motif = driver.find_element(By.XPATH, '//span[contains(text(), "Première consultation enfant")]')
    motif.click()
    time.sleep(3)

    if "RDV en ligne indisponible" not in driver.page_source:
        envoyer_alerte("🎉 Un créneau est disponible pour une première consultation chez la Dre Baron Thurotte !")
    else:
        print("Aucun créneau.")

finally:
    driver.quit()