import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(
            filename="logs/app.log",
            maxBytes=10485760,  # 10MB
            backupCount=5,      # Keep 5 backup files
        ),
        logging.StreamHandler()  # Also output to console
    ]
)