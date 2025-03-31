"""
API测试脚本

用于测试API连接和请求功能，仅执行一次请求。
"""
import os
import sys
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import Logger
from src.utils.api_factory import APIFactory


def test_api_connection():
    """测试API连接"""
    logger = Logger.get_logger('api_test', log_level='info')
    logger.info("开始API连接测试")
    
    # 从api.token文件直接加载API密钥
    try:
        with open('config/api.token', 'r') as f:
            api_key = f.read().strip()
            logger.info(f"从config/api.token加载密钥，长度: {len(api_key)}")
    except Exception as e:
        logger.error(f"加载API密钥文件失败: {str(e)}")
        return
    
    # 创建API实例
    try:
        # 尝试使用两种API实现
        logger.info("尝试创建GaodeAPI实例...")
        api1 = APIFactory.get_api_instance('gaode', api_key)
        logger.info("GaodeAPI实例创建成功")
        
        logger.info("尝试创建GaodeAPI2实例...")
        api2 = APIFactory.get_api_instance('gaode2', api_key)
        logger.info("GaodeAPI2实例创建成功")
        
        # 使用API2进行测试
        logger.info("使用GaodeAPI2执行搜索请求...")
        api = api2
    except Exception as e:
        logger.error(f"创建API实例失败: {str(e)}")
        return
    
    # 定义简单搜索参数
    search_params = {
        "keywords": "天安门",
        "region": "北京",
        "city_limit": True,
        "page_size": 5
    }
    
    # 执行搜索
    try:
        logger.info(f"搜索参数: {search_params}")
        start_time = time.time()
        result = api.search_by_keywords(**search_params)
        end_time = time.time()
        
        # 检查结果
        if isinstance(result, dict) and 'pois' in result:
            pois = result['pois']
            logger.info(f"搜索成功，获取到 {len(pois)} 条数据，用时: {end_time - start_time:.2f}秒")
            
            # 打印第一个POI的基本信息
            if pois:
                first_poi = pois[0]
                logger.info("第一个POI信息:")
                logger.info(f"  名称: {first_poi.get('name')}")
                logger.info(f"  地址: {first_poi.get('address')}")
                logger.info(f"  经纬度: {first_poi.get('location')}")
        else:
            logger.warning(f"搜索结果格式不正确: {type(result)}")
    
    except Exception as e:
        logger.error(f"执行搜索请求失败: {str(e)}")
        
    logger.info("API测试完成")


if __name__ == "__main__":
    test_api_connection() 