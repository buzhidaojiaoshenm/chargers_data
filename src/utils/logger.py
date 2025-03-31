"""
日志记录模块

提供统一的日志记录功能，支持不同的日志级别和输出方式。
"""
import os
import logging
from datetime import datetime
from typing import Dict, Optional


# 日志级别映射
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


class Logger:
    """
    日志记录器
    
    提供统一的日志记录功能，支持不同的日志级别和输出方式。
    """
    
    _instances = {}  # 用于存储不同名称的日志记录器实例
    
    @classmethod
    def get_logger(cls, name: str = 'main', log_level: str = 'info',
                  log_to_file: bool = False, log_dir: str = 'logs',
                  log_file_prefix: str = None) -> logging.Logger:
        """
        获取指定名称的日志记录器实例
        
        Args:
            name: 日志记录器名称
            log_level: 日志级别，可选值：debug, info, warning, error, critical
            log_to_file: 是否将日志记录到文件
            log_dir: 日志文件目录
            log_file_prefix: 日志文件名前缀
            
        Returns:
            日志记录器实例
        """
        # 如果已存在同名实例，则直接返回
        if name in cls._instances:
            return cls._instances[name]
        
        # 创建新的日志记录器
        logger = logging.getLogger(name)
        
        # 设置日志级别
        level = LOG_LEVELS.get(log_level.lower(), logging.INFO)
        logger.setLevel(level)
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # 避免重复添加处理器
        if not logger.handlers:
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if log_to_file:
            # 确保日志目录存在
            os.makedirs(log_dir, exist_ok=True)
            
            # 设置日志文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_prefix = log_file_prefix or name
            log_file = os.path.join(log_dir, f"{file_prefix}_{timestamp}.log")
            
            # 创建文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.info(f"日志将同时记录到文件: {log_file}")
        
        # 存储实例
        cls._instances[name] = logger
        return logger


def setup_logger(global_settings: Dict = None) -> logging.Logger:
    """
    根据全局设置创建日志记录器
    
    Args:
        global_settings: 全局设置字典
        
    Returns:
        日志记录器实例
    """
    settings = global_settings or {}
    
    # 从全局设置中获取日志配置
    log_level = settings.get('log_level', 'info')
    log_to_file = settings.get('log_to_file', False)
    log_dir = settings.get('log_dir', 'logs')
    
    # 创建日志记录器
    return Logger.get_logger(
        name='poi_search',
        log_level=log_level,
        log_to_file=log_to_file,
        log_dir=log_dir,
        log_file_prefix='poi_search'
    )


# 测试函数
def test_logger():
    """测试日志记录器"""
    # 创建一个控制台日志记录器
    console_logger = Logger.get_logger('test_console', log_level='debug')
    console_logger.debug("这是一条调试日志")
    console_logger.info("这是一条信息日志")
    console_logger.warning("这是一条警告日志")
    console_logger.error("这是一条错误日志")
    
    # 创建一个同时记录到文件的日志记录器
    file_logger = Logger.get_logger('test_file', log_level='info', log_to_file=True)
    file_logger.info("这是一条记录到文件的信息日志")
    file_logger.error("这是一条记录到文件的错误日志")
    
    # 使用相同的名称获取相同的日志记录器实例
    same_logger = Logger.get_logger('test_console')
    same_logger.info("这是使用相同实例发送的日志")
    
    # 测试根据全局设置创建日志记录器
    global_settings = {
        'log_level': 'info',
        'log_to_file': True,
        'log_dir': 'logs/test'
    }
    settings_logger = setup_logger(global_settings)
    settings_logger.info("这是根据全局设置创建的日志记录器")


if __name__ == "__main__":
    # 如果直接运行该模块，则执行测试
    test_logger() 