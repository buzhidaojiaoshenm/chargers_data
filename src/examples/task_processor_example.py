"""
任务处理器使用示例

展示如何使用TaskProcessor直接处理任务配置。
"""
import os
import sys
import json
from typing import Dict, List

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.task_processor import TaskProcessor, process_single_task
from src.utils.logger import Logger


def task_processor_example():
    """任务处理器使用示例"""
    # 创建日志记录器
    logger = Logger.get_logger('task_processor_example', log_level='info')
    logger.info("开始执行任务处理器示例")
    
    # 定义全局设置
    global_settings = {
        "output_dir": "data/examples/task_processor",
        "add_timestamp": True,
        "log_level": "info",
        "max_retries": 3,
        "retry_delay": 1.0
    }
    
    # 定义任务组
    task_group = {
        "api": "gaode2",
        "search_method": "keywords",
        "tasks": [
            {
                "name": "北京大学周边充电站搜索",
                "params": {
                    "keywords": "充电站|充电桩|充电设施",
                    "types": "011100|011101|011102|011103",
                    "region": "北京市海淀区",
                    "city_limit": True,
                    "show_fields": "children,business,indoor,navi,photos",
                    "children": 1,
                    "page_size": 25
                },
                "output": {
                    "filename_prefix": "pku_charging_stations",
                    "formats": ["csv", "json"]
                }
            },
            {
                "name": "清华大学周边充电站搜索",
                "params": {
                    "keywords": "充电站|充电桩|充电设施",
                    "types": "011100|011101|011102|011103",
                    "region": "北京市海淀区",
                    "city_limit": True,
                    "show_fields": "children,business,indoor,navi,photos",
                    "children": 1,
                    "page_size": 25
                },
                "output": {
                    "filename_prefix": "tsinghua_charging_stations",
                    "formats": ["csv", "json"]
                }
            }
        ]
    }
    
    # 方法1：处理整个任务组
    logger.info("方法1：处理整个任务组")
    
    # 创建任务处理器
    processor = TaskProcessor(global_settings)
    
    # 处理任务组
    try:
        result = processor.process_task_group("beijing_universities", task_group)
        logger.info(f"任务组处理结果: {json.dumps(result, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"处理任务组时出错: {str(e)}")
    
    # 方法2：处理单个任务
    logger.info("\n方法2：处理单个任务")
    
    # 定义单个任务
    single_task = {
        "name": "中关村充电站搜索",
        "api": "gaode2",
        "search_method": "keywords",
        "params": {
            "keywords": "充电站|充电桩|充电设施",
            "types": "011100|011101|011102|011103",
            "region": "中关村",
            "city_limit": True,
            "show_fields": "children,business,indoor,navi,photos",
            "children": 1,
            "page_size": 25
        },
        "output": {
            "filename_prefix": "zhongguancun_charging_stations",
            "formats": ["csv", "json"]
        }
    }
    
    # 处理单个任务
    try:
        result = process_single_task(single_task, global_settings)
        logger.info(f"单个任务处理结果: {json.dumps(result, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"处理单个任务时出错: {str(e)}")


if __name__ == "__main__":
    # 执行示例
    task_processor_example() 