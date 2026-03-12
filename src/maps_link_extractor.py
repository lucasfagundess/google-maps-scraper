import os
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuração de Log profissional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ExcelHandler:
    """Responsável por todas as operações de I/O de arquivos Excel."""
    
    @staticmethod
    def read_search_list(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {file_path}")
        return pd.read_excel(file_path).to_dict('records')

    @staticmethod
    def save_results(file_path, data_list):
        df_new = pd.DataFrame(data_list)
        
        if os.path.exists(file_path):
            df_old = pd.read_excel(file_path)
            df_final = pd.concat([df_old, df_new]).drop_duplicates(subset=['link'])
        else:
            df_final = df_new
            
        df_final.to_excel(file_path, index=False)
        logging.info(f"Dados salvos com sucesso em: {file_path}")


class GoogleMapsScraper:
    """Core da automação de busca no Google Maps."""
    
    def __init__(self, headless=False):
        self.url = "https://www.google.com/maps"
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        
        self.driver = None

    def start_driver(self):
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        self.driver.get(self.url)
        
        # Lógica para fechar pop-ups de cookies (comum em novas instâncias)
        try:
            wait = WebDriverWait(self.driver, 5)
            # Procura botões comuns de "Aceitar" ou "Concordo"
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Aceitar')] | //button[contains(., 'Aceitar')]")))
            cookie_button.click()
            logging.info("Pop-up de cookies fechado.")
        except:
            pass # Se não aparecer, segue o jogo

    def search_location(self, tipo, bairro, cidade, estado):
        query = f"{tipo} no bairro {bairro} em {cidade} - {estado}"
        logging.info(f"Iniciando busca: {query}")
        
        wait = WebDriverWait(self.driver, 20)
        
        try:
            # Lista de possíveis seletores que o Google Maps usa para a busca
            selectors = [
                (By.ID, "searchboxinput"),
                (By.NAME, "q"),
                (By.XPATH, "//input[@id='searchboxinput']"),
                (By.CLASS_NAME, "searchboxinput")
            ]
            
            search_box = None
            for selector_type, selector_value in selectors:
                try:
                    search_box = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                raise Exception("Não foi possível encontrar o campo de busca com nenhum seletor conhecido.")

            # Limpeza robusta
            search_box.click()
            time.sleep(1)
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)
            
            # Digitação simulando humano (evita bloqueios)
            for char in query:
                search_box.send_keys(char)
                time.sleep(0.05)
                
            search_box.send_keys(Keys.ENTER)
            
            # Espera carregar os resultados (procura pela div de feed)
            logging.info("Aguardando resultados carregarem...")
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='feed'] | //div[contains(@aria-label, 'Resultados')]")))
            time.sleep(3) 
            
        except Exception as e:
            logging.error(f"Erro ao localizar campo de busca: {e}")
            self.driver.save_screenshot("erro_busca.png")
            raise e

    def scroll_results(self, interactions=10):
        """Realiza scroll na lista de resultados para carregar mais itens."""
        try:
            # Tenta encontrar a div lateral de resultados
            side_panel = self.driver.find_element(By.XPATH, "//div[@role='feed'] | //div[contains(@aria-label, 'Resultados')]")
            for _ in range(interactions):
                side_panel.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)
        except Exception as e:
            logging.warning(f"Erro ao tentar scroll: {e}")

    def extract_links(self, search_info):
        """Extrai os links e retorna uma lista de dicionários formatada."""
        links_data = []
        # Seleciona todos os links que apontam para detalhes de lugares
        elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'maps/place')]")
        
        for el in elements:
            link = el.get_attribute("href")
            if link and link not in [d['link'] for d in links_data]:
                links_data.append({
                    "tipo": search_info['Tipo'],
                    "bairro": search_info['Bairro'],
                    "cidade": search_info['Cidade'],
                    "estado": search_info['Estado'],
                    "link": link,
                    "data_extracao": time.strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return links_data

    def quit(self):
        if self.driver:
            self.driver.quit()


class MapsOrchestrator:
    """Orquestra a leitura, extração e salvamento."""
    
    def __init__(self, input_file, output_file,headless=False):
        self.input_file = input_file
        self.output_file = output_file
        self.scraper = GoogleMapsScraper(headless=headless)

    def run(self):
        try:
            tasks = ExcelHandler.read_search_list(self.input_file)
            self.scraper.start_driver()
            
            all_extracted_data = []

            for task in tasks:
                self.scraper.search_location(
                    task['Tipo'], task['Bairro'], task['Cidade'], task['Estado']
                )
                self.scraper.scroll_results(interactions=15)
                links = self.scraper.extract_links(task)
                all_extracted_data.extend(links)
                logging.info(f"Extraídos {len(links)} links para esta busca.")

            if all_extracted_data:
                ExcelHandler.save_results(self.output_file, all_extracted_data)
            else:
                logging.warning("Nenhum dado foi extraído.")

        except Exception as e:
            logging.error(f"Erro na orquestração: {e}")
        finally:
            self.scraper.quit()

# --- EXECUÇÃO ---
if __name__ == "__main__":
    # Obtém o diretório onde o script maps_link_extractor.py está salvo
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Monta o caminho apontando para a mesma pasta do script
    ARQUIVO_ENTRADA = os.path.join(BASE_DIR, "buscas.xlsx")
    ARQUIVO_SAIDA = os.path.join(BASE_DIR, "links_extraidos.xlsx")
    
    bot = MapsOrchestrator(ARQUIVO_ENTRADA, ARQUIVO_SAIDA)
    bot.run()