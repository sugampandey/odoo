import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class CustomLogger:
    def __init__(self, name="odoo_custom", log_level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Clear any existing handlers
        self.logger.handlers = []
        
        # Create logs directory if it doesn't exist
        if os.getenv('ODOO_ENV') == 'prod':
            self.log_dir = "/opt/odoo/logs"
        else:
            self.log_dir = os.path.join('logs')
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Setup handlers
        self._setup_file_handler()
        self._setup_console_handler()
        
    def _setup_file_handler(self):
        log_file = os.path.join(self.log_dir, 'odoo.log')
        # Timed rotating file handler (daily rotation, keep 30 days of logs)
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='midnight',          # Rotate every day at midnight
            interval=1,              # Rotate every 1 day
            backupCount=30,          # Keep 30 days of backup
            encoding='utf-8'
        )
        
        # Set format for file logs
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        file_handler.setLevel(logging.DEBUG)
        # customize the rotation filename
        file_handler.namer = lambda name: name.replace(".log", "") + ".log"
        
        self.logger.addHandler(file_handler)
        
    def _setup_console_handler(self):
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Set format for console logs
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        console_handler.setLevel(logging.DEBUG)
        
        self.logger.addHandler(console_handler)
    
    def set_level(self, level):
        """Set logging level for all handlers"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)
            
    def set_file_level(self, level):
        """Set logging level for file handler only"""
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.setLevel(level)
                
    def set_console_level(self, level):
        """Set logging level for console handler only"""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and \
               not isinstance(handler, RotatingFileHandler):
                handler.setLevel(level)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

logger = CustomLogger()