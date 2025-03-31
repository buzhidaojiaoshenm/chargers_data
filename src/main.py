"""
POI数据搜索主模块

使用模块化设计，支持多种API和多种搜索方式。
"""
import sys
import os
import time
import argparse
import json
from typing import Dict, List, Any

from src.utils.config_parser import ConfigParser, create_default_config
from src.utils.task_processor import TaskProcessor
from src.utils.logger import setup_logger


def main(config_file: str = 'config/search_config.json', group_name: str = None, task_count: int = None):
    """
    主函数，处理POI搜索任务
    
    Args:
        config_file: 配置文件路径
        group_name: 要处理的任务组名称，如果为None则处理所有任务组
        task_count: 要处理的任务数量，如果为None则处理所有任务
    """
    # 检查配置文件是否存在，如果不存在则创建默认配置
    if not os.path.exists(config_file):
        print(f"配置文件 {config_file} 不存在，创建默认配置...")
        create_default_config(config_file)
    
    # 解析配置文件
    config_parser = ConfigParser(config_file)
    task_groups, global_settings = config_parser.parse_config()
    
    # 设置日志记录器
    logger = setup_logger(global_settings)
    logger.info(f"加载配置文件: {config_file}")
    
    # 检查是否有任务组
    if not task_groups:
        logger.error("配置文件中没有任务组定义")
        return
    
    # 统计信息
    total_groups = len(task_groups)
    processed_groups = 0
    successful_tasks = 0
    failed_tasks = 0
    
    # 创建任务处理器
    task_processor = TaskProcessor(global_settings)
    
    # 处理指定任务组或所有任务组
    if group_name:
        if group_name not in task_groups:
            logger.error(f"任务组 '{group_name}' 不存在")
            return
        
        # 只处理指定的任务组
        groups_to_process = {group_name: task_groups[group_name]}
    else:
        # 处理所有任务组
        groups_to_process = task_groups
    
    # 记录开始时间
    start_time = time.time()
    
    # 处理每个任务组
    for group_name, group_config in groups_to_process.items():
        logger.info(f"处理任务组 {group_name} ({processed_groups + 1}/{len(groups_to_process)})")
        
        # 如果指定了任务数量，则限制处理的任务数
        if task_count is not None and task_count > 0:
            original_tasks = group_config.get('tasks', [])
            limited_tasks = original_tasks[:task_count]
            logger.info(f"限制处理 {task_count} 个任务（共 {len(original_tasks)} 个）")
            
            # 创建新的配置，只包含限定数量的任务
            limited_config = group_config.copy()
            limited_config['tasks'] = limited_tasks
            
            # 处理任务组
            result = task_processor.process_task_group(group_name, limited_config)
        else:
            # 处理所有任务
            result = task_processor.process_task_group(group_name, group_config)
        
        # 更新统计信息
        processed_groups += 1
        if result.get('successful_tasks'):
            successful_tasks += result['successful_tasks']
        
        if result.get('total_tasks') and result.get('successful_tasks'):
            failed_tasks += result['total_tasks'] - result['successful_tasks']
    
    # 记录结束时间和总运行时间
    end_time = time.time()
    total_time = end_time - start_time
    
    # 打印统计信息
    logger.info("=" * 50)
    logger.info("任务执行完成")
    logger.info(f"总任务组: {total_groups}")
    logger.info(f"处理任务组: {processed_groups}")
    logger.info(f"成功任务: {successful_tasks}")
    logger.info(f"失败任务: {failed_tasks}")
    logger.info(f"总用时: {total_time:.2f} 秒")
    logger.info("=" * 50)


def parse_args():
    """
    解析命令行参数
    
    Returns:
        解析后的参数
    """
    parser = argparse.ArgumentParser(description='POI数据搜索工具')
    parser.add_argument('-c', '--config', default='config/search_config.json',
                      help='配置文件路径')
    parser.add_argument('-g', '--group', default=None,
                      help='要处理的任务组名称，不指定则处理所有任务组')
    parser.add_argument('-t', '--task-count', type=int, default=None,
                      help='要处理的任务数量，不指定则处理所有任务')
    parser.add_argument('--create-config', action='store_true',
                      help='创建默认配置文件并退出')
    
    return parser.parse_args()


if __name__ == "__main__":
    # 解析命令行参数
    args = parse_args()
    
    # 如果指定了创建配置文件
    if args.create_config:
        create_default_config(args.config)
        print(f"默认配置文件已创建: {args.config}")
        sys.exit(0)
    
    # 执行主函数
    main(args.config, args.group, args.task_count) 
