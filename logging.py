python
import logging
import sys
import os


def setup_logging():
    """
    Настройка логирования одновременно в консоль и файл.
    """

    # Создание папки logs, если её нет
    os.makedirs("logs", exist_ok=True)

    # Формат записи лога
    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Настройка корневого логгера
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                "logs/file_txt.log",
                encoding="utf-8"
            )
        ]
    )

    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")