import logging
import os

NOME_DO_LOGGER = "atendimento"
FORMATO = "%(asctime)s | %(levelname)s | %(message)s"

logging.getLogger(NOME_DO_LOGGER).addHandler(logging.NullHandler())

def obter_logger():
    return logging.getLogger(NOME_DO_LOGGER)

def configurar_logs(caminho):
    encerrar_logs()

    pasta = os.path.dirname(caminho)
    if pasta != "":
        os.makedirs(pasta, exist_ok=True)

    manipulador = logging.FileHandler(caminho, encoding="utf-8")
    manipulador.setFormatter(logging.Formatter(FORMATO))
    logger = obter_logger()
    logger.setLevel(logging.INFO)
    logger.addHandler(manipulador)

def encerrar_logs():
    logger = obter_logger()
    for manipulador in list(logger.handlers):
        if isinstance(manipulador, logging.FileHandler):
            manipulador.close()
            logger.removeHandler(manipulador)