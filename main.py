import os
from interface.menu import executar_menu
from interface.sistema import Sistema
from servicos.registro import configurar_logs, encerrar_logs

PASTA_DADOS = "dados"
ARQUIVO_LOG = os.path.join("logs", "sistema.log")

def main():
    configurar_logs(ARQUIVO_LOG)
    try:
        sistema = Sistema(PASTA_DADOS)
        for aviso in sistema.avisos:
            print("Aviso:", aviso)
        executar_menu(sistema)
    finally:
        encerrar_logs()

if __name__ == "__main__":
    main()