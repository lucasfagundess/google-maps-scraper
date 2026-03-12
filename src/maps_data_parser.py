import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class MapsDataParser:
    def __init__(self, headless=False):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--start-maximized")
        self.driver = None

    def start_driver(self):
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )

    def get_element_text(self, xpath, attribute="innerText"):
        """Método auxiliar para capturar dados com segurança."""
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return element.get_attribute(attribute)
        except:
            return "Não encontrado"

    def parse_business_details(self, url):
        logging.info(f"Acessando: {url}")
        self.driver.get(url)
        
        # Espera curta para garantir o carregamento do h1 (nome)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//h1'))
            )
        except:
            pass

        data = {
            "nome": self.get_element_text('//h1[@class="DUwDvf lfPIob"]'),
            "endereco": self.get_element_text('//button[@data-item-id="address"]/div/div[2]'),
            "telefone": self.get_element_text('//button[starts-with(@data-item-id,"phone")]/div/div[2]'),
            "site": self.get_element_text('//a[starts-with(@data-item-id,"authority")]', "href"),
            "url_origem": url
        }
        return data

    def run(self, input_xlsx, output_xlsx):
        try:
            df_links = pd.read_excel(input_xlsx)
            if "link" not in df_links.columns:
                logging.error("Coluna 'link' não encontrada no Excel.")
                return

            self.start_driver()
            final_results = []

            for index, row in df_links.iterrows():
                details = self.parse_business_details(row['link'])
                final_results.append(details)
                # Pausa leve para evitar block
                time.sleep(1)

            df_final = pd.DataFrame(final_results)
            df_final.to_excel(output_xlsx, index=False)
            logging.info(f"Processamento concluído. Salvo em {output_xlsx}")

        finally:
            if self.driver:
                self.driver.quit()