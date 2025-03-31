"""
关键字搜索示例

展示如何使用模块化结构进行关键字搜索。
"""
import os
import sys
import json
from typing import Dict, List

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.api_factory import APIFactory
from src.utils.config_parser import load_api_key
from src.utils.data_saver import DataSaver
from src.utils.logger import Logger


def keywords_search_example():
    """关键字搜索示例"""
    # 创建日志记录器
    logger = Logger.get_logger('keywords_search_example', log_level='info')
    logger.info("开始执行关键字搜索示例")
    
    # 加载API密钥
    try:
        api_key = load_api_key('api')
    except FileNotFoundError:
        logger.error("无法加载API密钥，请确保config/api.token文件存在")
        return
    
    # 创建API实例
    try:
        api = APIFactory.get_api_instance('gaode2', api_key)
    except Exception as e:
        logger.error(f"创建API实例失败: {str(e)}")
        return
    
    # 定义搜索参数
    search_params = {
        "keywords": "充电站",
        "types": "011100|011101|011102|011103",
        "region": "北京",
        "city_limit": True,
        "show_fields": "children,business,indoor,navi,photos",
        "children": 1,
        "page_size": 25
    }
    
    # 执行搜索
    logger.info(f"搜索参数: {json.dumps(search_params, ensure_ascii=False)}")
    
    try:
        result = api.search_by_keywords(**search_params)
        logger.info(f"搜索成功，获取到 {len(result)} 条数据")
        
        # 保存结果
        if result:
            # 定义保存配置
            global_settings = {
                "output_dir": "data/examples",
                "add_timestamp": True
            }
            
            output_config = {
                "filename_prefix": "beijing_charging_stations",
                "formats": ["csv", "json"]
            }
            
            # 创建数据保存器
            saver = DataSaver(global_settings)
            saved_files = saver.save_data(result, output_config, "北京充电站搜索")
            
            # 输出保存结果
            logger.info("数据已保存到以下文件:")
            for fmt, filepath in saved_files.items():
                logger.info(f"  {fmt}: {filepath}")
        else:
            logger.warning("未获取到数据")
    
    except Exception as e:
        logger.error(f"搜索或保存数据时出错: {str(e)}")


if __name__ == "__main__":
    # 执行示例
    keywords_search_example() 