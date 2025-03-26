import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Any

from src.api.gaode2 import GaodeAPI2
from src.utils.logger import Logger

# 创建全局日志记录器
logger = Logger()


def load_api_key() -> str:
    """从配置文件加载API密钥"""
    try:
        with open('config/api.token', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise Exception("请在config/api.token文件中配置高德地图API密钥")


def load_config() -> Dict:
    """加载搜索配置"""
    try:
        with open('config/search_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception("请确保config/search_config.json文件存在")
    except json.JSONDecodeError:
        raise Exception("search_config.json格式错误")


def save_to_csv(data: List[Dict], filename: str, fields: List[str]) -> None:
    """保存数据到CSV文件"""
    if not data:
        logger.warning(f"没有数据要保存到 {filename}")
        return

    try:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            
            for item in data:
                row = {}
                for field in fields:
                    if '.' in field:  # 处理嵌套字段
                        parts = field.split('.')
                        value = item
                        for part in parts:
                            if isinstance(value, dict):
                                value = value.get(part, '')
                            else:
                                value = ''
                                break
                    else:
                        value = item.get(field, '')
                    
                    # 处理特殊字段
                    if field == 'photos':
                        if isinstance(value, list):
                            value = ';'.join(photo.get('url', '') for photo in value)
                    elif field == 'children':
                        if isinstance(value, list):
                            value = len(value)  # 只记录子POI数量
                            
                    row[field] = value
                writer.writerow(row)
        logger.info(f"数据已保存到: {filename}")
    except Exception as e:
        logger.error(f"保存CSV文件时出错: {str(e)}")


def save_to_json(data: List[Dict], filename: str) -> None:
    """保存数据到JSON文件"""
    if not data:
        logger.warning(f"没有数据要保存到 {filename}")
        return

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存到: {filename}")
    except Exception as e:
        logger.error(f"保存JSON文件时出错: {str(e)}")


def save_results(data: List[Dict], output_config: Dict, global_settings: Dict) -> None:
    """保存搜索结果"""
    if not data:
        logger.warning("没有数据要保存")
        return

    # 准备输出目录
    base_output_dir = global_settings.get('output_dir', 'data')
    
    # 创建带有时间戳的子目录
    current_time = datetime.now()
    time_subfolder = current_time.strftime('%Y%m%d_%H%M')
    output_dir = os.path.join(base_output_dir, time_subfolder)
    
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"输出目录: {output_dir}")

    # 添加时间戳到文件名（如果配置中指定）
    timestamp = ''
    if global_settings.get('add_timestamp', False):
        timestamp = f"_{current_time.strftime('%Y%m%d_%H%M%S')}"

    # 定义要保存的字段
    fields = [
        'id', 'name', 'type', 'typecode', 'address', 'pname', 'cityname', 'adname',
        'location', 'tel', 'website', 'email', 'postcode', 'business_area',
        'business.open_time', 'business.rating', 'business.cost',
        'indoor.indoor_map', 'indoor.cpid', 'indoor.floor', 'indoor.truefloor',
        'navi.entr_location', 'navi.exit_location',
        'photos', 'children'
    ]

    # 保存不同格式的文件
    filename_prefix = output_config.get('filename_prefix', 'poi_data')
    formats = output_config.get('formats', ['csv'])

    for fmt in formats:
        filename = os.path.join(output_dir, f"{filename_prefix}{timestamp}.{fmt}")
        if fmt.lower() == 'csv':
            save_to_csv(data, filename, fields)
        elif fmt.lower() == 'json':
            save_to_json(data, filename)
        else:
            logger.warning(f"不支持的文件格式: {fmt}")


def execute_search_task(api: GaodeAPI2, task: Dict) -> None:
    """执行单个搜索任务"""
    try:
        search_type = task.get('search_type', 'keywords')
        params = task.get('params', {})
        
        logger.info(f"\n开始执行任务: {task.get('name', '未命名任务')}")
        logger.info(f"搜索类型: {search_type}")
        logger.info("搜索参数:")
        for key, value in params.items():
            logger.info(f"  {key}: {value}")

        # 获取所有数据
        result = api.get_poi_total_list(search_type, **params)
        
        if result:
            logger.info(f"\n成功获取 {len(result)} 条数据")
            # 保存结果
            save_results(result, task.get('output', {}), config.get('global_settings', {}))
        else:
            logger.warning("未获取到数据")

    except Exception as e:
        logger.error(f"执行任务时出错: {str(e)}")


def main():
    """主函数"""
    try:
        # 加载API密钥和配置
        api_key = load_api_key()
        global config
        config = load_config()

        # 初始化API客户端
        api = GaodeAPI2(api_key)

        # 获取任务列表
        tasks = config.get('tasks', [])
        if not tasks:
            logger.warning("配置文件中没有定义搜索任务")
            return

        logger.info(f"共加载 {len(tasks)} 个任务")

        # 执行每个任务
        for task in tasks:
            execute_search_task(api, task)

        logger.info("\n所有任务执行完成")

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")


if __name__ == '__main__':
    main() 
