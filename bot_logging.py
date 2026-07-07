import logging

logging.basicConfig(level=logging.INFO, filename='bot.log', format='%(asctime)s - %(levelname)s - %(message)s')

class Logger:
    @staticmethod
    def info(message: str):
        logging.info(message)
    @staticmethod
    def error(message: str):
        logging.error(message)
    @staticmethod
    def warning(message: str):
        logging.warning(message)