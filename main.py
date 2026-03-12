import os
import logging
import shutil
from datetime import datetime

# O setup_logging DEVE ser definido antes dos imports de src
def setup_logging(base_dir):
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"execucao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ],
        force=True 
    )

# Imports dos seus módulos agora que o log está pronto
from src.maps_link_extractor import MapsOrchestrator
from src.maps_data_parser import MapsDataParser

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    setup_logging(BASE_DIR)
    
    # Marca de tempo única para esta rodada
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    logging.info("Iniciando Pipeline Profissional Google Maps")

    # --- CONFIGURAÇÕES ---
    HEADLESS_EXTRACTOR = True
    HEADLESS_PARSER = True
    
    INPUT_PATH = os.path.join(BASE_DIR, "inputs", "buscas.xlsx")
    LINKS_PATH = os.path.join(BASE_DIR, "outputs", "retorno_links.xlsx")
    
    # Arquivo com timestamp e arquivo fixo (Latest)
    FINAL_PATH_TS = os.path.join(BASE_DIR, "outputs", f"dados_extraidos_{ts}.xlsx")
    LATEST_PATH = os.path.join(BASE_DIR, "outputs", "dados_mais_recentes.xlsx")

    try:
        # FASE 1
        logging.info("--- FASE 1: Extraindo Links ---")
        extractor = MapsOrchestrator(INPUT_PATH, LINKS_PATH, headless=HEADLESS_EXTRACTOR)
        extractor.run()

        # FASE 2
        if os.path.exists(LINKS_PATH):
            logging.info(f"--- FASE 2: Extraindo Detalhes para {FINAL_PATH_TS} ---")
            parser = MapsDataParser(headless=HEADLESS_PARSER)
            parser.run(LINKS_PATH, FINAL_PATH_TS)
            
            # Criar a cópia de fácil acesso
            shutil.copy(FINAL_PATH_TS, LATEST_PATH)
            logging.info("Cópia 'dados_mais_recentes.xlsx' atualizada.")
        else:
            logging.warning("Fase 1 não gerou links para processar.")

    except Exception as e:
        logging.error(f"Erro inesperado no fluxo principal: {e}", exc_info=True)
    
    logging.info("Pipeline finalizado.")
    logging.shutdown()

if __name__ == "__main__":
    main()