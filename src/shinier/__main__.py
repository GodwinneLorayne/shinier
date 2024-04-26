from logging import getLogger
import shinier.logging

def main():
    shinier.logging.configure()

    logger = getLogger(__name__)

    logger.info("Hello, world!")
