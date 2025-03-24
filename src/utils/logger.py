import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """日志管理器"""
    
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        """
        初始化日志管理器
        
        Args:
            log_dir: 日志文件保存目录
            log_level: 日志级别
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.logger = None
        self.setup_logger()
    
    def setup_logger(self):
        """配置日志记录器"""
        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 生成日志文件名（包含时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(self.log_dir, f'poi_search_{timestamp}.log')
        
        # 创建日志记录器
        self.logger = logging.getLogger('POISearchLogger')
        self.logger.setLevel(self.log_level)
        
        # 清除可能存在的处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 设置处理器格式
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.info(f"日志文件已创建: {log_file}")
    
    def info(self, message: str):
        """记录信息级别的日志"""
        self.logger.info(message)
    
    def error(self, message: str):
        """记录错误级别的日志"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """记录警告级别的日志"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """记录调试级别的日志"""
        self.logger.debug(message)
    
    def critical(self, message: str):
        """记录严重错误级别的日志"""
        self.logger.critical(message) 