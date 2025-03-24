import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any

from src.api.gaode import GaodeAPI
from src.utils.logger import Logger

# 创建全局日志记录器
logger = Logger()


def load_api_key() -> str:
    """加载API密钥"""
    with open('config/api.token', 'r') as f:
        return f.read().strip()


def load_search_config() -> Dict[str, Any]:
    """加载搜索配置"""
    with open('config/search_config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def save_to_csv(pois: list, filename: str):
    """
    将POI数据保存为CSV文件
    
    Args:
        pois: POI数据列表
        filename: 输出文件名
    """
    if not pois:
        return
    
    # 定义要提取的字段
    fields = [
        'id', 'name', 'type', 'typecode', 'address', 'pname', 'cityname',
        'adname', 'location', 'tel', 'business_area', 'biz_ext.open_time',
        'biz_ext.rating', 'biz_ext.cost'
    ]
    
    # 创建目录
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # 写入表头
        writer.writerow(fields)
        
        # 写入数据
        for poi in pois:
            row = []
            for field in fields:
                if '.' in field:
                    # 处理嵌套字段
                    parent, child = field.split('.')
                    value = poi.get(parent, {}).get(child, '')
                else:
                    value = poi.get(field, '')
                row.append(value)
            writer.writerow(row)


def save_results(pois: List[Dict], task: Dict, global_settings: Dict):
    """
    根据配置保存搜索结果
    
    Args:
        pois: POI数据列表
        task: 任务配置
        global_settings: 全局设置
    """
    if not pois:
        return
        
    # 准备文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') if global_settings.get('add_timestamp') else ''
    base_name = f"{task['output']['filename_prefix']}_{timestamp}" if timestamp else task['output']['filename_prefix']
    output_dir = global_settings.get('output_dir', 'data')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存指定格式
    for format_type in task['output']['formats']:
        if format_type.lower() == 'csv':
            filename = os.path.join(output_dir, f"{base_name}.csv")
            save_to_csv(pois, filename)
            logger.info(f"CSV数据已保存到: {filename}")
            
        elif format_type.lower() == 'json':
            filename = os.path.join(output_dir, f"{base_name}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(pois, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON数据已保存到: {filename}")


def execute_search_task(api: GaodeAPI, task: Dict) -> List[Dict]:
    """
    执行单个搜索任务
    
    Args:
        api: GaodeAPI实例
        task: 任务配置
        
    Returns:
        搜索结果列表
    """
    logger.info(f"\n开始执行任务: {task['name']}")
    
    search_type = task['search_type']
    params = task['params']
    
    try:
        return api.get_poi_total_list(search_type=search_type, **params)
    except Exception as e:
        logger.error(f"任务 '{task['name']}' 执行失败: {str(e)}")
        return []


def main():
    try:
        logger.info("开始POI数据搜索程序")
        
        # 加载配置
        api_key = load_api_key()
        config = load_search_config()
        logger.info("配置文件加载完成")
        
        # 初始化API客户端
        api = GaodeAPI(key=api_key)
        
        # 获取全局设置
        global_settings = config.get('global_settings', {})
        
        # 执行每个搜索任务
        total_tasks = len(config['tasks'])
        logger.info(f"共有 {total_tasks} 个搜索任务待执行")
        
        for i, task in enumerate(config['tasks'], 1):
            logger.info(f"正在执行第 {i}/{total_tasks} 个任务")
            
            # 执行搜索
            pois = execute_search_task(api, task)
            
            if pois:
                logger.info(f"任务 '{task['name']}' 找到 {len(pois)} 个POI")
                # 保存结果
                save_results(pois, task, global_settings)
            else:
                logger.warning(f"任务 '{task['name']}' 未找到任何POI")
        
        logger.info("所有任务执行完成")
        return 0
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main()) 
