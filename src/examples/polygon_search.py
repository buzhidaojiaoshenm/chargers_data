"""
多边形网格搜索示例

展示如何使用模块化结构进行多边形网格搜索。
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
from src.utils.polygon_grid import generate_polygon_grid, coords_to_polygon_param


def polygon_grid_search_example():
    """多边形网格搜索示例"""
    # 创建日志记录器
    logger = Logger.get_logger('polygon_search_example', log_level='info')
    logger.info("开始执行多边形网格搜索示例")
    
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
    
    # 定义中心点和搜索参数
    center_lng = 116.397428  # 北京天安门
    center_lat = 39.90923
    
    # 生成多边形网格
    region_radius = 3000  # 3公里半径的区域
    edge_length = 1000  # 每个多边形边长1公里
    num_sides = 6  # 六边形
    
    logger.info(f"生成多边形网格: 中心点 ({center_lng}, {center_lat}), 区域半径 {region_radius}米, 多边形边长 {edge_length}米, {num_sides}边形")
    
    try:
        # 生成多边形网格
        polygons = generate_polygon_grid(
            center_lng=center_lng,
            center_lat=center_lat,
            region_radius=region_radius,
            edge_length=edge_length,
            num_sides=num_sides
        )
        
        logger.info(f"生成了 {len(polygons)} 个多边形")
        
        # 收集所有结果
        all_results = []
        unique_poi_ids = set()
        
        # 定义搜索参数
        search_params = {
            "keywords": "充电站",
            "types": "011100|011101|011102|011103",
            "show_fields": "children,business,indoor,navi,photos",
            "children": 1,
            "page_size": 25
        }
        
        # 保存多边形边界信息（用于可视化）
        polygons_data = []
        
        # 搜索每个多边形
        for idx, polygon in enumerate(polygons):
            logger.info(f"搜索多边形 {idx + 1}/{len(polygons)}")
            
            # 格式化多边形参数
            polygon_str = coords_to_polygon_param(polygon)
            
            # 构建多边形数据（用于可视化）
            points = []
            for coord in polygon.split('|'):
                if coord:
                    lng, lat = coord.split(',')
                    points.append([float(lng), float(lat)])
            
            polygons_data.append({
                'index': idx,
                'polygon': polygon,
                'points': points
            })
            
            # 执行搜索
            params = {**search_params, 'polygon': polygon_str}
            try:
                result = api.search_polygon(**params)
                logger.info(f"搜索成功，获取到 {len(result)} 条数据")
                
                # 去重添加
                for poi in result:
                    poi_id = poi.get('id')
                    if poi_id and poi_id not in unique_poi_ids:
                        unique_poi_ids.add(poi_id)
                        all_results.append(poi)
            except Exception as e:
                logger.error(f"搜索多边形 {idx + 1} 失败: {str(e)}")
        
        logger.info(f"所有多边形搜索完成，共获取 {len(all_results)} 个唯一POI")
        
        # 保存搜索结果
        if all_results:
            # 定义保存配置
            global_settings = {
                "output_dir": "data/examples",
                "add_timestamp": True
            }
            
            output_config = {
                "filename_prefix": "beijing_tiananmen_polygon",
                "formats": ["csv", "json"]
            }
            
            # 创建数据保存器
            saver = DataSaver(global_settings)
            saved_files = saver.save_data(all_results, output_config, "北京天安门区域多边形搜索")
            
            # 保存多边形边界信息（用于可视化）
            from src.utils.data_saver import save_to_file
            polygons_file = os.path.join(global_settings["output_dir"], "beijing_tiananmen_polygons.json")
            save_to_file(polygons_data, polygons_file)
            logger.info(f"多边形边界数据已保存到: {polygons_file}")
            
            # 输出保存结果
            logger.info("数据已保存到以下文件:")
            for fmt, filepath in saved_files.items():
                logger.info(f"  {fmt}: {filepath}")
        else:
            logger.warning("未获取到数据")
    
    except Exception as e:
        logger.error(f"生成多边形或搜索数据时出错: {str(e)}")


if __name__ == "__main__":
    # 执行示例
    polygon_grid_search_example() 