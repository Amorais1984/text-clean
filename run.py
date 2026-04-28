"""
VoxText Engine — Ponto de entrada principal.

Inicializa logging, configurações e a interface gráfica.
"""

import sys
import logging

from voxtext.app import VoxTextApp
from voxtext.config.settings import Settings
from voxtext.gui.main_window import MainWindow


def setup_logging() -> None:
    """Configura o sistema de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> None:
    """Função principal de inicialização."""
    setup_logging()
    logger = logging.getLogger("VoxText")
    logger.info("Iniciando VoxText Engine v1.0.0")

    # Inicializar configurações
    settings = Settings()

    # Criar aplicação
    app = VoxTextApp(settings=settings)

    # Criar e executar interface
    window = MainWindow(app)
    logger.info("Interface carregada. Aguardando interação do usuário...")
    window.run()

    logger.info("VoxText Engine encerrado.")


if __name__ == "__main__":
    main()
