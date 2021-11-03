from time import sleep

import webdriver_manager.firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC


def scrap_url(url: str):
    s = Service(webdriver_manager.firefox.GeckoDriverManager().install())
    driver = webdriver.Firefox(service=s)
    driver.get(url)
    iframe = driver.find_element(By.XPATH, '//*[@id="tokentxnsiframe"]')
    sleep(10)
    wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(iframe))

    transactions_tr = driver.find_elements(By.XPATH, '/html/body/div[2]/div[2]/table/tbody/tr')
    for transaction in transactions_tr:
        print(transaction.text)


if __name__ == '__main__':
    scrap_url('https://etherscan.io/token/0x761d38e5ddf6ccf6cf7c55759d5210750b5d60f3')