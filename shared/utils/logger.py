import logging
import sys
from pathlib import Path

def setup_logger(name: str = "app", log_level: int = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    if not logger.handlers:
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File Handler (Optional, ensure logs dir exists if used)
        # log_dir = Path("logs")
        # log_dir.mkdir(exist_ok=True)
        # file_handler = logging.FileHandler(log_dir / "app.log")
        # file_handler.setFormatter(formatter)
        # logger.addHandler(file_handler)
        
    return logger

logger = setup_logger()
