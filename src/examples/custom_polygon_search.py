"""
自定义多边形搜索示例

演示如何直接使用多边形坐标进行搜索，无需额外的格式转换。
"""
import os
import sys
import json
from typing import Dict, List

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.api_factory import APIFactory
from src.utils.config_parser import load_api_key
from src.utils.data_saver import DataSaver, save_to_file
from src.utils.logger import Logger


def custom_polygon_search_example():
    """自定义多边形区域搜索示例"""
    # 创建日志记录器
    logger = Logger.get_logger('custom_polygon_example', log_level='info')
    logger.info("开始执行自定义多边形区域搜索示例")
    
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
    
    # 定义自定义多边形
    # 北京天安门周边区域（确保首尾坐标相同，形成闭合多边形）
    custom_polygon = "116.389254,39.913173|116.400626,39.913087|116.400798,39.905145|116.389254,39.905145|116.389254,39.913173"
    
    logger.info(f"使用自定义多边形搜索: {custom_polygon}")
    
    try:
        # 定义搜索参数
        search_params = {
            "keywords": "充电站|充电桩|充电设施",
            "types": "011100|011101|011102|011103",
            "polygon": custom_polygon,
            "show_fields": "children,business,indoor,navi,photos",
            "children": 1,
            "page_size": 25
        }
        
        # 执行搜索
        logger.info("开始搜索...")
        result = api.search_polygon(**search_params)
        
        # 提取POI列表
        poi_list = result.get('pois', [])
        logger.info(f"搜索成功，找到 {len(poi_list)} 个POI")
        
        # 保存结果
        if poi_list:
            # 定义保存配置
            global_settings = {
                "output_dir": "data/examples",
                "add_timestamp": True
            }
            
            output_config = {
                "filename_prefix": "tiananmen_custom_polygon",
                "formats": ["csv", "json"]
            }
            
            # 创建数据保存器
            saver = DataSaver(global_settings)
            saved_files = saver.save_data(poi_list, output_config, "北京天安门自定义多边形搜索")
            
            # 保存多边形边界信息（用于可视化）
            polygon_file = os.path.join(global_settings["output_dir"], "tiananmen_custom_polygon_boundary.json")
            save_to_file([{
                'polygon': custom_polygon,
                'points': [[float(x.split(',')[0]), float(x.split(',')[1])] for x in custom_polygon.split('|')]
            }], polygon_file, 'json')
            logger.info(f"多边形边界数据已保存到: {polygon_file}")
            
            # 输出保存结果
            logger.info("数据已保存到以下文件:")
            for fmt, filepath in saved_files.items():
                logger.info(f"  {fmt}: {filepath}")
        else:
            logger.warning("未获取到数据")
            
    except Exception as e:
        logger.error(f"搜索或保存数据时出错: {str(e)}")


def main():
    """主函数"""
    custom_polygon_search_example()


if __name__ == "__main__":
    main() 