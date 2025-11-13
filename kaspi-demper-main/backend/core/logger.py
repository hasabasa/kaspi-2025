import os
import logging
import sys
from core.colors import *

LOG_FILE = "logs/api.log"
DEMPER_LOG_FILE = "logs/demper.log"

def ensure_log_dir_exists():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(DEMPER_LOG_FILE), exist_ok=True)

COLOR_RESET = RESET
LEVEL_COLORS = {
    "DEBUG": CYAN,
    "INFO": BLUE,
    "WARNING": YELLOW,
    "ERROR": RED,
    "CRITICAL": BG_RED,
}
MESSAGE_COLORS = {
    "DEBUG": BRIGHT_CYAN,
    "INFO": BRIGHT_BLUE,
    "WARNING": BRIGHT_YELLOW,
    "ERROR": BRIGHT_RED,
    "CRITICAL": WHITE,
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        level_color = LEVEL_COLORS.get(record.levelname, COLOR_RESET)
        message_color = MESSAGE_COLORS.get(record.levelname, COLOR_RESET)
        record.levelname = f"{level_color}{record.levelname}{COLOR_RESET}"
        try:
            record.msg = f"{message_color}{record.msg}{COLOR_RESET}"
        except UnicodeEncodeError:
            record.msg = f"{message_color}{record.msg.encode('ascii', 'replace').decode('ascii')}{COLOR_RESET}"
        return super().format(record)

def setup_logging():
    ensure_log_dir_exists()

    console_handler = logging.StreamHandler()
    try:
        console_handler.stream.reconfigure(encoding='utf-8')
    except AttributeError:
        if sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

    console_handler.setFormatter(ColorFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    demper_file_handler = logging.FileHandler(DEMPER_LOG_FILE, encoding='utf-8')
    demper_file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler]
    )

    for lib in ("supabase", "httpx", "httpcore", "urllib3", "postgrest", "gotrue", "telethon"):
        logging.getLogger(lib).setLevel(logging.WARNING)

class NoHttpRequestFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.getMessage().startswith("HTTP Request:")

logger = logging.getLogger()
logger.addFilter(NoHttpRequestFilter())

def setup_demper_logger():
    ensure_log_dir_exists()
    demper_logger = logging.getLogger("price_checker")
    demper_logger.setLevel(logging.INFO)
    demper_logger.propagate = False
    demper_file_handler = logging.FileHandler(DEMPER_LOG_FILE, encoding='utf-8')
    demper_file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    demper_logger.addHandler(demper_file_handler)
    demper_logger.addFilter(NoHttpRequestFilter())
    return demper_logger